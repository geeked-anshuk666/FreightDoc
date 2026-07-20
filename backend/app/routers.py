"""HTTP routes for public reference data and owner-scoped FreightDoc workspaces."""

from __future__ import annotations

import asyncio
import base64
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import Response
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import CurrentUser, require_current_user
from app.database import get_db
from app.db_models import AuditEvent, Shipment, TradeParty
from app.models import (
    DocumentType,
    DossierDetail,
    DossierSummary,
    GenerateRequest,
    IntakeDocumentList,
    IntakeDocumentResponse,
    ShipmentDetail,
    ShipmentDraftRequest,
    ShipmentPage,
    ShipmentRequest,
    ShipmentSummary,
    TradePartyRequest,
    TradePartyResponse,
    ValidateRequest,
)
from app.rate_limit import rate_limit
from app.repositories import FreightRepository
from app.services.doc_engine import DocumentEngine
from app.services.document_intake import ExtractedDocument, sanitize_and_extract
from app.services.groq_client import GroqClient
from app.services.pdf_generator import render_complete_dossier
from app.services.pipeline import PipelineService
from app.services.upload_policy import MAX_FILE_BYTES, MAX_REQUEST_BYTES, DocumentSafetyError

router = APIRouter(prefix="/api")


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def ai_error(exc: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail={
            "code": "AI_SERVICE_ERROR",
            "message": "The structured AI service could not complete this step safely.",
            "request_id": getattr(exc, "request_id", None),
        },
    )


def _not_found(resource: str) -> HTTPException:
    # Same response for a foreign resource and a missing resource avoids ID probing.
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": f"{resource} was not found."})


def _safety_error(exc: DocumentSafetyError) -> HTTPException:
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE if exc.code in {"FILE_TOO_LARGE", "CONTENT_LIMIT_EXCEEDED"} else status.HTTP_422_UNPROCESSABLE_ENTITY
    return HTTPException(status_code=status_code, detail={"code": exc.code, "message": exc.message})


async def get_repository(
    user: Annotated[CurrentUser, Depends(require_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FreightRepository:
    return FreightRepository(db, user.owner_id)


def _shipment_summary(shipment: Shipment) -> ShipmentSummary:
    return ShipmentSummary(
        id=shipment.id,
        status=shipment.status,
        title=shipment.title,
        created_at=shipment.created_at,
        updated_at=shipment.updated_at,
    )


def _shipment_detail(shipment: Shipment) -> ShipmentDetail:
    return ShipmentDetail(
        **_shipment_summary(shipment).model_dump(),
        payload=shipment.payload,
        review_submitted_at=shipment.review_submitted_at,
    )


def _document_response(document) -> IntakeDocumentResponse:
    return IntakeDocumentResponse(
        id=document.id,
        shipment_id=document.shipment_id,
        document_type=document.document_type,
        filename=document.filename,
        mime_type=document.mime_type,
        size_bytes=document.size_bytes,
        status=document.status,
        extracted_text=document.extracted_text,
        normalized_fields=document.normalized_fields,
        findings=document.findings,
        confidence=document.confidence,
        extraction_error_code=document.extraction_error_code,
        retained_original=False,
        created_at=document.created_at,
    )


async def _owner_shipment(repository: FreightRepository, shipment_id: str) -> Shipment:
    shipment = await repository.get_shipment(shipment_id)
    if not shipment:
        raise _not_found("Shipment")
    return shipment


def _complete_shipment(shipment: Shipment) -> ShipmentRequest:
    try:
        return ShipmentRequest.model_validate(shipment.payload)
    except PydanticValidationError as exc:
        missing = sorted({str(error["loc"][-1]) for error in exc.errors() if error.get("type") == "missing"})
        message = "Complete the required shipment fields before review." if not missing else f"Complete: {', '.join(missing)}."
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "SHIPMENT_INCOMPLETE", "message": message}) from exc


async def _extract_safely(file: UploadFile) -> ExtractedDocument:
    size_hint = file.size
    if size_hint is not None and size_hint > MAX_FILE_BYTES:
        raise _safety_error(DocumentSafetyError("FILE_TOO_LARGE", "Each document must be 15 MiB or smaller."))
    data = await file.read(MAX_FILE_BYTES + 1)
    try:
        if len(data) > MAX_FILE_BYTES:
            raise DocumentSafetyError("FILE_TOO_LARGE", "Each document must be 15 MiB or smaller.")
        # Native parsers execute in a worker thread with a bounded request wait.
        # All supported parsers also have explicit size/page/archive limits.
        from app.config import get_settings

        return await asyncio.wait_for(
            asyncio.to_thread(sanitize_and_extract, file.filename, file.content_type, data),
            timeout=get_settings().document_parser_timeout_seconds,
        )
    except asyncio.TimeoutError as exc:
        raise DocumentSafetyError("EXTRACTION_TIMEOUT", "Document extraction exceeded the safe time limit.") from exc
    finally:
        # Do not retain input bytes beyond the request/extraction lifetime.
        data = b""
        await file.close()


# Public, informational endpoints -------------------------------------------------


@router.get("/country-pairs")
async def country_pairs():
    return {
        "supported_corridors": DocumentEngine().supported_corridors(),
        "china_eu_requirement": "China shipments must specify an EU member-state destination.",
        "legal_disclaimer": "Informational preparation only; confirm filing obligations with a licensed customs broker.",
    }


@router.post("/full-pipeline", dependencies=[Depends(rate_limit("pipeline", 6))])
async def full_pipeline(shipment: ShipmentRequest, request: Request):
    """Stateless demo endpoint retained for the existing browser workflow.

    Saved shipment dossier runs use the authenticated route below. This endpoint
    persists nothing and must not be used for private uploads.
    """
    try:
        return await PipelineService().run(shipment, _request_id(request) or "standalone")
    except RuntimeError as exc:
        raise ai_error(exc) from exc


@router.post("/classify", dependencies=[Depends(rate_limit("classify", 12))])
async def classify(shipment: ShipmentRequest, request: Request):
    try:
        return await GroqClient().classify_product(shipment, _request_id(request) or "standalone")
    except RuntimeError as exc:
        raise ai_error(exc) from exc


@router.post("/generate", dependencies=[Depends(rate_limit("generate", 10))])
async def generate(payload: GenerateRequest, request: Request):
    try:
        from app.models import TariffData
        from datetime import timezone

        return await GroqClient().generate_documents(
            payload.shipment,
            payload.classification,
            TariffData(duty_rate=None, source="standalone", retrieved_at=datetime.now(timezone.utc)),
            payload.requirements.required_docs,
            _request_id(request) or "standalone",
        )
    except RuntimeError as exc:
        raise ai_error(exc) from exc


@router.post("/validate", dependencies=[Depends(rate_limit("validate", 10))])
async def validate(payload: ValidateRequest, request: Request):
    try:
        return await GroqClient().validate_documents(
            payload.documents, payload.shipment, payload.requirements.required_docs, _request_id(request) or "standalone"
        )
    except RuntimeError as exc:
        raise ai_error(exc) from exc


# Authenticated shipment workspace -------------------------------------------------


@router.post("/shipments", response_model=ShipmentDetail, status_code=status.HTTP_201_CREATED)
async def create_shipment(
    payload: ShipmentDraftRequest,
    request: Request,
    repository: Annotated[FreightRepository, Depends(get_repository)],
):
    values = payload.model_dump(exclude_none=True)
    title = values.pop("title", None)
    shipment = await repository.create_shipment(values, title, _request_id(request))
    return _shipment_detail(shipment)


@router.get("/shipments", response_model=ShipmentPage)
async def list_shipments(
    repository: Annotated[FreightRepository, Depends(get_repository)],
    limit: int = Query(default=20, ge=1, le=50),
    cursor: str | None = Query(default=None),
):
    parsed_cursor: datetime | None = None
    if cursor:
        try:
            parsed_cursor = datetime.fromisoformat(cursor.replace("Z", "+00:00"))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail={"code": "INVALID_CURSOR", "message": "The page cursor is invalid."}) from exc
    rows = await repository.list_shipments(limit + 1, parsed_cursor)
    page_rows, extra = rows[:limit], rows[limit:]
    next_cursor = page_rows[-1].created_at.isoformat() if extra and page_rows[-1].created_at else None
    return ShipmentPage(items=[_shipment_summary(row) for row in page_rows], next_cursor=next_cursor)


@router.get("/shipments/{shipment_id}", response_model=ShipmentDetail)
async def get_shipment(shipment_id: str, repository: Annotated[FreightRepository, Depends(get_repository)]):
    return _shipment_detail(await _owner_shipment(repository, shipment_id))


@router.patch("/shipments/{shipment_id}", response_model=ShipmentDetail)
async def update_shipment(
    shipment_id: str,
    payload: ShipmentDraftRequest,
    request: Request,
    repository: Annotated[FreightRepository, Depends(get_repository)],
):
    shipment = await _owner_shipment(repository, shipment_id)
    updates = payload.model_dump(exclude_none=True)
    title = updates.pop("title", shipment.title)
    merged = {**shipment.payload, **updates}
    shipment = await repository.update_shipment(shipment, merged, title, _request_id(request))
    return _shipment_detail(shipment)


@router.post("/shipments/{shipment_id}/review", response_model=ShipmentDetail)
async def submit_review(
    shipment_id: str,
    request: Request,
    repository: Annotated[FreightRepository, Depends(get_repository)],
):
    shipment = await _owner_shipment(repository, shipment_id)
    _complete_shipment(shipment)
    return _shipment_detail(await repository.submit_for_review(shipment, _request_id(request)))


@router.delete("/shipments/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment(
    shipment_id: str,
    request: Request,
    repository: Annotated[FreightRepository, Depends(get_repository)],
):
    shipment = await _owner_shipment(repository, shipment_id)
    await repository.delete_shipment(shipment, _request_id(request))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Parties -------------------------------------------------------------------------


@router.post("/parties", response_model=TradePartyResponse, status_code=status.HTTP_201_CREATED)
async def create_party(
    payload: TradePartyRequest,
    request: Request,
    repository: Annotated[FreightRepository, Depends(get_repository)],
):
    party = await repository.create_party(payload.kind, payload.name, payload.details, _request_id(request))
    return TradePartyResponse(id=party.id, kind=party.kind, name=party.name, details=party.details, created_at=party.created_at)


@router.get("/parties", response_model=list[TradePartyResponse])
async def search_parties(
    repository: Annotated[FreightRepository, Depends(get_repository)],
    kind: str | None = Query(default=None, pattern="^(exporter|importer)$"),
    q: str | None = Query(default=None, min_length=1, max_length=80),
):
    rows = await repository.search_parties(kind, q)
    return [TradePartyResponse(id=row.id, kind=row.kind, name=row.name, details=row.details, created_at=row.created_at) for row in rows]


# Document intake -----------------------------------------------------------------


@router.post(
    "/shipments/{shipment_id}/documents",
    response_model=IntakeDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("document-upload", 10))],
)
async def intake_document(
    shipment_id: str,
    request: Request,
    document_type: Annotated[DocumentType, Form(...)],
    file: Annotated[UploadFile, File(...)],
    repository: Annotated[FreightRepository, Depends(get_repository)],
):
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > MAX_REQUEST_BYTES:
        raise HTTPException(status_code=413, detail={"code": "REQUEST_TOO_LARGE", "message": "A document upload request must be 40 MiB or smaller."})
    shipment = await _owner_shipment(repository, shipment_id)
    try:
        extracted = await _extract_safely(file)
    except DocumentSafetyError as exc:
        raise _safety_error(exc) from exc
    document = await repository.create_document(
        shipment,
        {
            "document_type": document_type.value,
            "filename": extracted.filename,
            "mime_type": extracted.mime_type,
            "size_bytes": extracted.size_bytes,
            "status": extracted.status,
            "extracted_text": extracted.text,
            "normalized_fields": extracted.normalized_fields,
            "findings": extracted.findings,
            "confidence": extracted.confidence,
            "extraction_error_code": extracted.error_code,
            "extraction_error_message": extracted.error_message,
            "original_deleted": True,
            "parser_provenance": extracted.parser_provenance,
        },
        _request_id(request),
    )
    return _document_response(document)


@router.get("/shipments/{shipment_id}/documents", response_model=IntakeDocumentList)
async def list_documents(shipment_id: str, repository: Annotated[FreightRepository, Depends(get_repository)]):
    shipment = await _owner_shipment(repository, shipment_id)
    return IntakeDocumentList(items=[_document_response(document) for document in await repository.list_documents(shipment)])


@router.delete("/shipments/{shipment_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    shipment_id: str,
    document_id: str,
    request: Request,
    repository: Annotated[FreightRepository, Depends(get_repository)],
):
    shipment = await _owner_shipment(repository, shipment_id)
    document = await repository.get_document(shipment, document_id)
    if not document:
        raise _not_found("Document")
    await repository.delete_document(shipment, document, _request_id(request))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/shipments/{shipment_id}/documents/{document_id}/retry", response_model=IntakeDocumentResponse)
async def retry_document_extraction(
    shipment_id: str,
    document_id: str,
    request: Request,
    repository: Annotated[FreightRepository, Depends(get_repository)],
    file: UploadFile | None = File(default=None),
):
    """Re-extract a user-supplied replacement; originals are deliberately absent."""
    shipment = await _owner_shipment(repository, shipment_id)
    document = await repository.get_document(shipment, document_id)
    if not document:
        raise _not_found("Document")
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "REUPLOAD_REQUIRED", "message": "Original files are not retained. Re-upload the document to retry extraction."},
        )
    try:
        extracted = await _extract_safely(file)
    except DocumentSafetyError as exc:
        raise _safety_error(exc) from exc
    document.filename = extracted.filename
    document.mime_type = extracted.mime_type
    document.size_bytes = extracted.size_bytes
    document.status = extracted.status
    document.extracted_text = extracted.text
    document.normalized_fields = extracted.normalized_fields
    document.findings = extracted.findings
    document.confidence = extracted.confidence
    document.extraction_error_code = extracted.error_code
    document.extraction_error_message = extracted.error_message
    document.parser_provenance = extracted.parser_provenance
    await repository.audit("document.retried", "document", document.id, _request_id(request), {"status": document.status})
    await repository.session.commit()
    await repository.session.refresh(document)
    return _document_response(document)


# Dossiers ------------------------------------------------------------------------


@router.post(
    "/shipments/{shipment_id}/dossiers",
    response_model=DossierDetail,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("saved-dossier", 6))],
)
async def generate_dossier(
    shipment_id: str,
    request: Request,
    repository: Annotated[FreightRepository, Depends(get_repository)],
):
    shipment = await _owner_shipment(repository, shipment_id)
    complete = _complete_shipment(shipment)
    try:
        result = await PipelineService().run(complete, _request_id(request) or "saved-dossier")
    except RuntimeError as exc:
        raise ai_error(exc) from exc
    requirements = result.requirements
    if requirements is None:  # defensive guard for older pipeline implementations
        raise HTTPException(status_code=500, detail={"code": "PIPELINE_PROVENANCE_MISSING", "message": "The pipeline did not return rules provenance."})
    package = await repository.create_package(
        shipment,
        {
            "request_id": result.request_id,
            "classification": result.classification.model_dump(mode="json"),
            "tariff": result.tariff.model_dump(mode="json"),
            "requirements": requirements.model_dump(mode="json"),
            "documents": result.documents.model_dump(mode="json"),
            "validation": result.validation.model_dump(mode="json"),
            "pdfs": result.pdfs,
            "source_provenance": {
                "tariff_source": result.tariff.source,
                "tariff_retrieved_at": result.tariff.retrieved_at.isoformat(),
                "tariff_fallback_used": result.tariff.fallback_used,
                "rule_version": requirements.rule_version,
                "rule_effective_date": requirements.effective_date,
                "provider": result.provider,
                "model": result.model,
            },
            "legal_disclaimer": result.legal_disclaimer,
        },
        _request_id(request),
    )
    shipment.status = "dossier_generated"
    await repository.session.commit()
    return _dossier_detail(package)


def _dossier_detail(package) -> DossierDetail:
    from app.models import ClassificationResult, DocumentPackage, DocumentRequirements, TariffData, ValidationResult

    validation = ValidationResult.model_validate(package.validation)
    return DossierDetail(
        id=package.id,
        shipment_id=package.shipment_id,
        readiness_score=validation.compliance_score,
        ready_to_ship=validation.ready_to_ship,
        created_at=package.created_at,
        legal_disclaimer=package.legal_disclaimer,
        classification=ClassificationResult.model_validate(package.classification),
        tariff=TariffData.model_validate(package.tariff),
        requirements=DocumentRequirements.model_validate(package.requirements),
        documents=DocumentPackage.model_validate(package.documents),
        validation=validation,
        source_provenance=package.source_provenance,
    )


@router.get("/shipments/{shipment_id}/dossiers/latest", response_model=DossierDetail)
async def latest_dossier(shipment_id: str, repository: Annotated[FreightRepository, Depends(get_repository)]):
    shipment = await _owner_shipment(repository, shipment_id)
    package = await repository.latest_package(shipment)
    if not package:
        raise _not_found("Dossier")
    return _dossier_detail(package)


@router.get("/shipments/{shipment_id}/dossiers/{package_id}", response_model=DossierDetail)
async def get_dossier(
    shipment_id: str, package_id: str, repository: Annotated[FreightRepository, Depends(get_repository)]
):
    shipment = await _owner_shipment(repository, shipment_id)
    package = await repository.get_package(shipment, package_id)
    if not package:
        raise _not_found("Dossier")
    return _dossier_detail(package)


@router.get("/shipments/{shipment_id}/dossiers/{package_id}/download/complete.pdf")
async def download_complete_dossier(
    shipment_id: str, package_id: str, repository: Annotated[FreightRepository, Depends(get_repository)]
):
    shipment = await _owner_shipment(repository, shipment_id)
    package = await repository.get_package(shipment, package_id)
    if not package:
        raise _not_found("Dossier")
    validation = package.validation
    classification = package.classification
    route = f"{shipment.payload.get('origin_country', '?')} → {shipment.payload.get('destination_country', '?')}"
    content = render_complete_dossier(
        package.documents,
        route,
        str(classification.get("hs_code", "")) or None,
        int(validation.get("compliance_score", 0)),
    )
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="freightdoc-dossier-{shipment.id}.pdf"', "Cache-Control": "private, no-store"},
    )


@router.get("/shipments/{shipment_id}/dossiers/{package_id}/download/{document_name}.pdf")
async def download_document_pdf(
    shipment_id: str,
    package_id: str,
    document_name: str,
    repository: Annotated[FreightRepository, Depends(get_repository)],
):
    shipment = await _owner_shipment(repository, shipment_id)
    package = await repository.get_package(shipment, package_id)
    if not package:
        raise _not_found("Dossier")
    payload = package.pdfs.get(document_name)
    if not payload:
        raise _not_found("PDF artifact")
    try:
        content = base64.b64decode(payload, validate=True)
    except (ValueError, TypeError):
        raise HTTPException(status_code=500, detail={"code": "PDF_ARTIFACT_INVALID", "message": "The stored PDF artifact is invalid."})
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{document_name}.pdf"', "Cache-Control": "private, no-store"},
    )


# Data rights ---------------------------------------------------------------------


@router.get("/account/export")
async def export_account_data(
    user: Annotated[CurrentUser, Depends(require_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return the account's saved business data, never a Clerk profile or file bytes."""
    shipments = list((await db.execute(select(Shipment).where(Shipment.owner_id == user.owner_id))).scalars())
    parties = list((await db.execute(select(TradeParty).where(TradeParty.owner_id == user.owner_id))).scalars())
    return {
        "owner_id": user.owner_id,
        "shipments": [{"id": item.id, "status": item.status, "title": item.title, "payload": item.payload} for item in shipments],
        "trade_parties": [{"id": item.id, "kind": item.kind, "name": item.name, "details": item.details} for item in parties],
        "original_uploads_included": False,
    }


@router.delete("/account/data", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account_data(
    request: Request,
    user: Annotated[CurrentUser, Depends(require_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await db.execute(delete(Shipment).where(Shipment.owner_id == user.owner_id))
    await db.execute(delete(TradeParty).where(TradeParty.owner_id == user.owner_id))
    await db.execute(delete(AuditEvent).where(AuditEvent.owner_id == user.owner_id))
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
