from __future__ import annotations

import asyncio
import logging

from app.config import get_settings
from app.models import (DocumentPackage, PipelineResponse, PipelineStatus, ShipmentRequest, ValidationError, ValidationResult)
from app.services.doc_engine import DocumentEngine
from app.services.groq_client import AIServiceError, GroqClient
from app.services.pdf_generator import render_documents
from app.services.hts_api import lookup_usitc
from app.services.tariff_api import lookup_comtrade

DISCLAIMER = "FreightDoc is an informational export-documentation assistant, not legal or customs advice. Verify classifications, tariffs, and documentation with a licensed customs broker before shipping."
logger = logging.getLogger("freightdoc.pipeline")


class PipelineStageError(RuntimeError):
    """A non-AI pipeline failure converted into a public-safe error shape."""

    def __init__(
        self,
        *,
        code: str,
        stage: str,
        request_id: str,
        retryable: bool,
        status_code: int = 502,
    ) -> None:
        super().__init__(code)
        self.code = code
        self.stage = stage
        self.request_id = request_id
        self.retryable = retryable
        self.status_code = status_code


def _stage_failure(stage: str, request_id: str, exc: Exception) -> PipelineStageError:
    """Convert implementation exceptions without exposing their contents."""
    if isinstance(exc, ValueError):
        code = "PIPELINE_INPUT_INVALID"
        retryable = False
        status_code = 422
    else:
        code = "PIPELINE_PROCESSING_ERROR"
        retryable = True
        status_code = 502
    logger.error(
        "request_id=%s stage=%s status=failed error_type=%s code=%s",
        request_id,
        stage,
        type(exc).__name__,
        code,
    )
    return PipelineStageError(
        code=code,
        stage=stage,
        request_id=request_id,
        retryable=retryable,
        status_code=status_code,
    )


def deterministic_checks(shipment: ShipmentRequest, requirements, package: DocumentPackage) -> list[ValidationError]:
    errors: list[ValidationError] = []
    missing = set(requirements.required_docs) - set(package.documents)
    for document in sorted(missing):
        errors.append(ValidationError(severity="critical", document=document, field="document", issue="Required document is missing from the package.", fix=f"Generate and review the required {document.replace('_', ' ')}."))
    invoice = package.documents.get("commercial_invoice", {})
    packing = package.documents.get("packing_list", {})
    for field, expected in (("quantity", shipment.quantity), ("declared_value", shipment.declared_value)):
        values = [str(doc.get(field)) for doc in (invoice, packing) if field in doc]
        if values and any(value != str(expected) for value in values):
            errors.append(ValidationError(severity="critical", document="package", field=field, issue=f"Document value does not match submitted shipment {field}.", fix=f"Set {field} consistently to {expected} in all documents."))
    return errors


class PipelineService:
    def __init__(self, ai: GroqClient | None = None, rules: DocumentEngine | None = None, usitc_lookup=lookup_usitc, comtrade_lookup=lookup_comtrade):
        self.ai = ai or GroqClient()
        self.rules = rules or DocumentEngine()
        self.usitc_lookup = usitc_lookup
        self.comtrade_lookup = comtrade_lookup

    async def run(self, shipment: ShipmentRequest, request_id: str) -> PipelineResponse:
        try:
            classification = await self.ai.classify_product(shipment, request_id)
        except AIServiceError:
            raise
        except Exception as exc:
            raise _stage_failure("classification", request_id, exc) from None

        try:
            requirements = self.rules.requirements_for(shipment.origin_country, shipment.destination_country, classification.category)
        except Exception as exc:
            raise _stage_failure("requirements", request_id, exc) from None

        try:
            usitc, comtrade = await asyncio.gather(
                self.usitc_lookup(classification.hs_code, requirements.corridor, request_id),
                self.comtrade_lookup(classification.hs_code, requirements.corridor, request_id),
            )
            tariff = usitc if usitc.duty_rate is not None else comtrade
        except Exception as exc:
            raise _stage_failure("tariff_lookup", request_id, exc) from None

        try:
            documents = await self.ai.generate_documents(
                shipment,
                classification,
                tariff,
                requirements.required_docs,
                request_id,
            )
        except AIServiceError:
            raise
        except Exception as exc:
            raise _stage_failure("generation", request_id, exc) from None

        try:
            validation = await self.ai.validate_documents(documents, shipment, requirements.required_docs, request_id)
            extra = deterministic_checks(shipment, requirements, documents)
        except AIServiceError:
            raise
        except Exception as exc:
            raise _stage_failure("validation", request_id, exc) from None

        if classification.confidence < get_settings().low_confidence_threshold:
            extra.append(ValidationError(severity="warning", document="classification", field="confidence", issue="HS classification confidence is below the review threshold.", fix="Ask a licensed customs broker to verify the HS classification."))
        combined = validation.errors + extra
        critical = any(error.severity == "critical" for error in combined)
        validation = ValidationResult(errors=combined, compliance_score=min(validation.compliance_score, 70 if critical else validation.compliance_score), ready_to_ship=validation.ready_to_ship and not critical)
        fallback = usitc.fallback_used and comtrade.fallback_used
        statuses = [PipelineStatus(step="classification", status="completed"), PipelineStatus(step="tariff_lookup", status="fallback" if fallback else "completed"), PipelineStatus(step="requirements", status="completed"), PipelineStatus(step="generation", status="completed"), PipelineStatus(step="validation", status="completed"), PipelineStatus(step="pdf_rendering", status="completed")]
        try:
            pdfs = {artifact.filename.removesuffix(".pdf"): artifact.content_base64 for artifact in render_documents(documents.documents)}
        except Exception as exc:
            raise _stage_failure("pdf_rendering", request_id, exc) from None
        settings = get_settings()
        return PipelineResponse(
            request_id=request_id,
            status=statuses,
            classification=classification,
            tariff=tariff,
            required_docs=requirements.required_docs,
            documents=documents,
            validation=validation,
            pdfs=pdfs,
            legal_disclaimer=DISCLAIMER,
            requirements=requirements,
            provider=settings.ai_provider,
            model=settings.ai_model,
        )
