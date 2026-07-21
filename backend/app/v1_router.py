"""Versioned deterministic record/review APIs. AI data is inert until a human acts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select

from app.db_models import AiSuggestion, AuditEvent, IntakeDocument, PlatformResource, ReviewDecision, ReviewTask, Shipment, ShipmentRevision, TradeFact
from app.models import AiSuggestionCreateRequest, FactWriteRequest, LandedCostRequest, PlatformResourceRequest, ReviewDecisionRequest, ReviewTaskCreateRequest
from app.routers import _not_found, _request_id, get_repository
from app.repositories import FreightRepository

router = APIRouter(prefix="/api/v1", tags=["canonical-record"])


def _event_digest(previous: str | None, event_type: str, resource_id: str, metadata: dict) -> str:
    material = json.dumps({"previous": previous, "event_type": event_type, "resource_id": resource_id, "metadata": metadata}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(material.encode()).hexdigest()


async def _audit(repo: FreightRepository, event_type: str, resource_type: str, resource_id: str, request: Request, metadata: dict) -> None:
    previous = (await repo.session.execute(select(AuditEvent.event_hash).where(AuditEvent.owner_id == repo.owner_id).order_by(AuditEvent.created_at.desc()).limit(1))).scalar_one_or_none()
    digest = _event_digest(previous, event_type, resource_id, metadata)
    repo.session.add(AuditEvent(owner_id=repo.owner_id, event_type=event_type, resource_type=resource_type, resource_id=resource_id, request_id=_request_id(request), metadata_json=metadata, previous_event_hash=previous, event_hash=digest))


async def _shipment(repo: FreightRepository, shipment_id: str):
    value = await repo.get_shipment(shipment_id)
    if not value:
        raise _not_found("Shipment")
    return value


@router.get("/shipments/{shipment_id}/record")
async def record(shipment_id: str, repo: Annotated[FreightRepository, Depends(get_repository)]):
    shipment = await _shipment(repo, shipment_id)
    facts = list((await repo.session.execute(select(TradeFact).where(TradeFact.shipment_id == shipment.id).order_by(TradeFact.created_at.desc()))).scalars())
    revisions = list((await repo.session.execute(select(ShipmentRevision).where(ShipmentRevision.shipment_id == shipment.id).order_by(ShipmentRevision.revision_number.desc()))).scalars())
    tasks = list((await repo.session.execute(select(ReviewTask).where(ReviewTask.shipment_id == shipment.id).order_by(ReviewTask.created_at.desc()))).scalars())
    suggestions = list((await repo.session.execute(select(AiSuggestion).where(AiSuggestion.shipment_id == shipment.id, AiSuggestion.status == "proposed").order_by(AiSuggestion.created_at.desc()))).scalars())
    documents = list((await repo.session.execute(select(IntakeDocument).where(IntakeDocument.shipment_id == shipment.id).order_by(IntakeDocument.created_at.desc()))).scalars())
    quality_result = await _quality_findings(shipment)
    return {
        "shipment_id": shipment.id,
        "revision_number": shipment.revision_number,
        "facts": [{"id": f.id, "field": f.field, "value": f.value.get("value"), "confidence": f.confidence, "provenance": f.provenance, "status": f.status, "revision_number": f.revision_number} for f in facts],
        "revisions": [{"id": r.id, "revision_number": r.revision_number, "reason": r.reason, "actor": r.actor_id, "created_at": r.created_at} for r in revisions],
        "review_tasks": [{"id": t.id, "kind": t.kind, "reason": t.reason, "status": t.status, "assigned_to": t.assignee_id, "created_at": t.created_at} for t in tasks],
        "document_workflows": [{"id": d.id, "document_name": d.filename, "status": d.status, "duplicate_of": None, "dependency": "Review extracted facts before dossier generation."} for d in documents],
        "suggestions": [{"id": s.id, "field": s.payload.get("field"), "title": s.payload.get("title"), "rationale": s.rationale, "provider": s.provider, "confidence": s.confidence, "status": s.status} for s in suggestions],
        "quality_findings": quality_result["findings"],
    }


@router.post("/shipments/{shipment_id}/facts", status_code=status.HTTP_201_CREATED)
async def write_fact(shipment_id: str, body: FactWriteRequest, request: Request, repo: Annotated[FreightRepository, Depends(get_repository)]):
    shipment = await _shipment(repo, shipment_id)
    if shipment.revision_number != body.expected_revision:
        raise HTTPException(409, detail={"code": "STALE_REVISION", "message": "Refresh the shipment record before saving."})
    next_revision = shipment.revision_number + 1
    shipment.payload = {**shipment.payload, body.field: body.value}
    shipment.revision_number = next_revision
    revision = ShipmentRevision(shipment_id=shipment.id, revision_number=next_revision, payload=shipment.payload, actor_id=repo.owner_id, reason=body.reason)
    fact = TradeFact(shipment_id=shipment.id, field=body.field, value={"value": body.value}, confidence=body.confidence, provenance=body.provenance, status="accepted", revision_number=next_revision)
    repo.session.add_all([revision, fact])
    await repo.session.flush()
    shipment.canonical_revision_id = revision.id
    await _audit(repo, "fact.accepted", "trade_fact", fact.id, request, {"shipment_id": shipment.id, "field": body.field, "revision": next_revision})
    await repo.session.commit()
    return {"id": fact.id, "revision_number": next_revision, "status": "accepted"}


@router.get("/shipments/{shipment_id}/revisions")
async def revisions(shipment_id: str, repo: Annotated[FreightRepository, Depends(get_repository)]):
    shipment = await _shipment(repo, shipment_id)
    rows = list((await repo.session.execute(select(ShipmentRevision).where(ShipmentRevision.shipment_id == shipment.id).order_by(ShipmentRevision.revision_number.desc()))).scalars())
    return {"items": [{"id": r.id, "revision_number": r.revision_number, "reason": r.reason, "created_at": r.created_at} for r in rows]}


@router.post("/shipments/{shipment_id}/review-tasks", status_code=201)
async def create_task(shipment_id: str, body: ReviewTaskCreateRequest, request: Request, repo: Annotated[FreightRepository, Depends(get_repository)]):
    shipment = await _shipment(repo, shipment_id)
    task = ReviewTask(shipment_id=shipment.id, kind=body.kind, reason=body.reason, maker_id=repo.owner_id, assignee_id=body.assignee_id)
    repo.session.add(task); await repo.session.flush()
    await _audit(repo, "review_task.created", "review_task", task.id, request, {"shipment_id": shipment.id, "kind": body.kind})
    await repo.session.commit()
    return {"id": task.id, "status": task.status}


@router.post("/review-tasks/{task_id}/decision")
async def decide_task(task_id: str, body: ReviewDecisionRequest, request: Request, repo: Annotated[FreightRepository, Depends(get_repository)]):
    task = (await repo.session.execute(select(ReviewTask).join(Shipment, ReviewTask.shipment_id == Shipment.id).where(ReviewTask.id == task_id, Shipment.owner_id == repo.owner_id))).scalar_one_or_none()
    if not task: raise _not_found("Review task")
    if task.status != "open": raise HTTPException(409, detail={"code": "TASK_ALREADY_DECIDED", "message": "This task already has a decision."})
    if task.maker_id == repo.owner_id and task.assignee_id and task.assignee_id != repo.owner_id:
        raise HTTPException(403, detail={"code": "MAKER_CHECKER_REQUIRED", "message": "The assigned reviewer must record this decision."})
    task.status = body.decision; task.resolved_at = datetime.now(timezone.utc)
    decision = ReviewDecision(task_id=task.id, actor_id=repo.owner_id, decision=body.decision, reason=body.reason)
    repo.session.add(decision); await _audit(repo, "review_task.decided", "review_task", task.id, request, {"decision": body.decision})
    await repo.session.commit(); return {"id": decision.id, "status": task.status}


@router.get("/shipments/{shipment_id}/quality")
async def quality(shipment_id: str, repo: Annotated[FreightRepository, Depends(get_repository)]):
    shipment = await _shipment(repo, shipment_id)
    return await _quality_findings(shipment)


async def _quality_findings(shipment: Shipment) -> dict:
    required = ("product_name", "product_description", "origin_country", "destination_country", "quantity", "declared_value", "currency")
    findings = [{"code": "MISSING_REQUIRED_FACT", "severity": "critical", "field": f, "message": "Required canonical fact is missing."} for f in required if shipment.payload.get(f) in (None, "")]
    if shipment.payload.get("origin_country") == shipment.payload.get("destination_country"):
        findings.append({"code":"SAME_CORRIDOR", "severity":"warning", "field":"destination_country", "message":"Origin and destination are the same."})
    return {"shipment_id": shipment.id, "mode": "deterministic", "findings": findings, "waiver_path": "Create a review task and record a waived decision with a reason."}


@router.post("/shipments/{shipment_id}/ai-suggestions", status_code=201)
async def store_suggestion(shipment_id: str, body: AiSuggestionCreateRequest, request: Request, repo: Annotated[FreightRepository, Depends(get_repository)]):
    shipment = await _shipment(repo, shipment_id)
    item = AiSuggestion(shipment_id=shipment.id, payload=body.payload, provider=body.provider, model=body.model, prompt_version=body.prompt_version, input_references=body.input_references, confidence=body.confidence, rationale=body.rationale)
    repo.session.add(item); await repo.session.flush()
    await _audit(repo, "ai_suggestion.recorded", "ai_suggestion", item.id, request, {"shipment_id": shipment.id, "status": "proposed"})
    await repo.session.commit(); return {"id": item.id, "status": item.status, "requires_human_acceptance": True}


@router.post("/suggestions/{suggestion_id}/accept")
@router.post("/suggestions/{suggestion_id}/reject")
async def decide_suggestion(suggestion_id: str, request: Request, repo: Annotated[FreightRepository, Depends(get_repository)]):
    suggestion = (await repo.session.execute(select(AiSuggestion).join(Shipment, AiSuggestion.shipment_id == Shipment.id).where(AiSuggestion.id == suggestion_id, Shipment.owner_id == repo.owner_id))).scalar_one_or_none()
    if not suggestion:
        raise _not_found("Suggestion")
    if suggestion.status != "proposed":
        raise HTTPException(409, detail={"code": "SUGGESTION_ALREADY_DECIDED", "message": "This suggestion has already been decided."})
    decision = "accepted" if request.url.path.endswith("/accept") else "rejected"
    suggestion.status = decision
    await _audit(repo, f"ai_suggestion.{decision}", "ai_suggestion", suggestion.id, request, {"shipment_id": suggestion.shipment_id, "decision": decision})
    await repo.session.commit()
    return {"id": suggestion.id, "status": decision, "fact_changed": False}


@router.get("/shipments/{shipment_id}/audit")
async def audit(shipment_id: str, repo: Annotated[FreightRepository, Depends(get_repository)]):
    await _shipment(repo, shipment_id)
    rows = list((await repo.session.execute(select(AuditEvent).where(AuditEvent.owner_id == repo.owner_id, AuditEvent.metadata_json.contains({"shipment_id": shipment_id})).order_by(AuditEvent.created_at.asc()))).scalars())
    return {"items": [{"id": e.id, "event_type": e.event_type, "resource_id": e.resource_id, "event_hash": e.event_hash, "previous_event_hash": e.previous_event_hash, "created_at": e.created_at} for e in rows]}


# Governed local knowledge -------------------------------------------------------

def _country_rules() -> dict:
    path = Path(__file__).parent / "data" / "country_rules.json"
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/rules")
async def rules(repo: Annotated[FreightRepository, Depends(get_repository)]):
    """Read-only local rule import; it is not an official legal source."""
    return {"version": "local-country-rules-v1", "status": "published_local_reference", "rules": _country_rules(), "advisory": True}


@router.get("/playbooks")
async def playbooks(repo: Annotated[FreightRepository, Depends(get_repository)]):
    data = _country_rules()
    return {"items": [{"corridor": key, "version": "local-country-rules-v1", "status": "published_local_reference", "checklist": value} for key, value in data.items() if key != "metadata"], "advisory": True}


_HS_LIBRARY = [
    {"code": "847130", "description": "Portable automatic data processing machines", "source": "local curated reference", "advisory": True},
    {"code": "851713", "description": "Smartphones and similar telephones", "source": "local curated reference", "advisory": True},
    {"code": "620342", "description": "Men's or boys' cotton trousers", "source": "local curated reference", "advisory": True},
]

@router.post("/shipments/{shipment_id}/classifications/candidates")
async def classification_candidates(shipment_id: str, body: PlatformResourceRequest, repo: Annotated[FreightRepository, Depends(get_repository)]):
    await _shipment(repo, shipment_id)
    terms = set((body.name + " " + str(body.payload.get("description", ""))).lower().split())
    matches = [row for row in _HS_LIBRARY if terms.intersection(row["description"].lower().split())]
    return {"shipment_id": shipment_id, "candidates": matches or _HS_LIBRARY, "selection_required": True, "advisory": True}

@router.post("/shipments/{shipment_id}/classifications/decisions", status_code=201)
async def classification_decision(shipment_id: str, body: PlatformResourceRequest, request: Request, repo: Annotated[FreightRepository, Depends(get_repository)]):
    await _shipment(repo, shipment_id)
    code = str(body.payload.get("hs_code", ""))
    if not code.isdigit() or not 6 <= len(code) <= 10:
        raise HTTPException(422, detail={"code": "INVALID_HS_CODE", "message": "Provide a 6–10 digit advisory HS code."})
    item = PlatformResource(owner_id=repo.owner_id, shipment_id=shipment_id, kind="classification_decision", status="human_selected", payload={"name": body.name, **body.payload, "advisory": True})
    repo.session.add(item); await repo.session.flush(); await _audit(repo, "classification.selected", "classification_decision", item.id, request, {"shipment_id": shipment_id, "advisory": True}); await repo.session.commit()
    return {"id": item.id, "status": item.status, "advisory": True}

@router.get("/rulings/search")
async def rulings_search(q: str, repo: Annotated[FreightRepository, Depends(get_repository)]):
    if not q.strip(): raise HTTPException(422, detail={"code": "QUERY_REQUIRED", "message": "A local reference query is required."})
    terms = set(q.lower().split())
    return {"items": [r for r in _HS_LIBRARY if terms.intersection(r["description"].lower().split())], "source_status": "local_curated_not_official"}

@router.post("/scenarios/landed-cost", status_code=201)
async def landed_cost(body: LandedCostRequest, request: Request, repo: Annotated[FreightRepository, Depends(get_repository)]):
    customs_value = body.goods_value + body.freight + body.insurance
    unknowns = [name for name, value in (("duty_rate", body.duty_rate), ("tax_rate", body.tax_rate)) if value is None]
    duty = customs_value * body.duty_rate if body.duty_rate is not None else None
    tax_base = customs_value + (duty or 0)
    tax = tax_base * body.tax_rate if body.tax_rate is not None else None
    total = None if unknowns else tax_base + (tax or 0) + body.fees
    payload = {"inputs": body.model_dump(), "customs_value": customs_value, "duty": duty, "tax": tax, "total": total, "unknowns": unknowns, "formula": "customs=goods+freight+insurance; duty=customs*duty_rate; tax=(customs+duty)*tax_rate; total=customs+duty+tax+fees"}
    run = PlatformResource(owner_id=repo.owner_id, kind="landed_cost_scenario", status="unknown_inputs" if unknowns else "calculated", payload=payload)
    repo.session.add(run); await repo.session.flush(); await _audit(repo, "scenario.calculated", "scenario", run.id, request, {"unknown_count": len(unknowns)}); await repo.session.commit()
    return {"id": run.id, "status": run.status, **payload, "advisory": True}


# Operations and deliberately disconnected adapters --------------------------------

@router.get("/operations/health")
async def operations_health(repo: Annotated[FreightRepository, Depends(get_repository)]):
    return {"status": "ok", "mode": "synchronous_database_backed", "queue_service": "not_configured", "external_adapters": "disabled", "ai_required": False}

@router.get("/operations/metrics")
async def operations_metrics(repo: Annotated[FreightRepository, Depends(get_repository)]):
    shipments = (await repo.session.execute(select(func.count(Shipment.id)).where(Shipment.owner_id == repo.owner_id))).scalar_one()
    open_tasks = (await repo.session.execute(select(func.count(ReviewTask.id)).join(Shipment, ReviewTask.shipment_id == Shipment.id).where(Shipment.owner_id == repo.owner_id, ReviewTask.status == "open"))).scalar_one()
    runs = (await repo.session.execute(select(func.count(PlatformResource.id)).where(PlatformResource.owner_id == repo.owner_id))).scalar_one()
    return {"shipments": shipments, "open_review_tasks": open_tasks, "local_runs": runs, "privacy": "aggregate_metadata_only"}

@router.get("/shipments/{shipment_id}/runs")
async def shipment_runs(shipment_id: str, repo: Annotated[FreightRepository, Depends(get_repository)]):
    await _shipment(repo, shipment_id)
    rows = list((await repo.session.execute(select(PlatformResource).where(PlatformResource.owner_id == repo.owner_id, PlatformResource.shipment_id == shipment_id).order_by(PlatformResource.created_at.desc()))).scalars())
    return {"items": [{"id": r.id, "kind": r.kind, "status": r.status, "created_at": r.created_at} for r in rows]}

_DISCONNECTED = {
    "connectors": {"status": "not_configured", "activation": "requires approved vendor, credentials, security review, and certification where applicable"},
    "screening": {"status": "not_screened", "activation": "requires authoritative licensed/official source and compliance owner"},
    "clearance": {"status": "not_connected_not_filed", "activation": "requires broker/customs authorization and production credentials"},
    "governance": {"status": "local_metadata_only", "activation": "SSO/SCIM requires enterprise approval; no provisioning is available"},
}

async def _create_resource(kind: str, body: PlatformResourceRequest, request: Request, repo: FreightRepository, *, status_value: str) -> dict:
    if body.shipment_id: await _shipment(repo, body.shipment_id)
    resource = PlatformResource(owner_id=repo.owner_id, shipment_id=body.shipment_id, kind=kind, status=status_value, payload={"name": body.name, **body.payload})
    repo.session.add(resource); await repo.session.flush(); await _audit(repo, f"{kind}.created", kind, resource.id, request, {"shipment_id": body.shipment_id, "status": status_value}); await repo.session.commit()
    return {"id": resource.id, "kind": kind, "status": status_value, "payload": resource.payload}

@router.get("/connectors")
async def connectors(repo: Annotated[FreightRepository, Depends(get_repository)]):
    return {"items": [{"id": "manual-csv", "capabilities": ["manual_import", "csv_export", "mock_validation"], **_DISCONNECTED["connectors"]}], "live_connectors": False}

@router.post("/connectors/mock-runs", status_code=201)
async def connector_mock(body: PlatformResourceRequest, request: Request, repo: Annotated[FreightRepository, Depends(get_repository)]):
    return await _create_resource("connector_run", body, request, repo, status_value="mock_completed_no_external_transmission")

@router.post("/partner-grants", status_code=201)
async def partner_grant(body: PlatformResourceRequest, request: Request, repo: Annotated[FreightRepository, Depends(get_repository)]):
    return await _create_resource("partner_grant", body, request, repo, status_value="draft_not_shared")

@router.post("/screening/cases", status_code=201)
async def screening_case(body: PlatformResourceRequest, request: Request, repo: Annotated[FreightRepository, Depends(get_repository)]):
    result = await _create_resource("screening_case", body, request, repo, status_value="not_screened_manual_review_required")
    result["authority_status"] = _DISCONNECTED["screening"]
    return result

@router.post("/clearance/cases", status_code=201)
async def clearance_case(body: PlatformResourceRequest, request: Request, repo: Annotated[FreightRepository, Depends(get_repository)]):
    result = await _create_resource("clearance_case", body, request, repo, status_value="not_connected_not_filed")
    result["authority_status"] = _DISCONNECTED["clearance"]
    return result

@router.post("/governance/policies", status_code=201)
async def governance_policy(body: PlatformResourceRequest, request: Request, repo: Annotated[FreightRepository, Depends(get_repository)]):
    return await _create_resource("governance_policy", body, request, repo, status_value="local_metadata_only")

@router.post("/implementation/projects", status_code=201)
async def implementation_project(body: PlatformResourceRequest, request: Request, repo: Annotated[FreightRepository, Depends(get_repository)]):
    payload = {"checklist": ["confirm owner scope", "review authority prerequisites", "configure manual workflow"], **body.payload}
    return await _create_resource("implementation_project", body.model_copy(update={"payload": payload}), request, repo, status_value="planned")

async def _resources_for(kind: str, repo: FreightRepository) -> dict:
    rows = list((await repo.session.execute(select(PlatformResource).where(PlatformResource.owner_id == repo.owner_id, PlatformResource.kind == kind).order_by(PlatformResource.created_at.desc()))).scalars())
    return {"items": [{"id": r.id, "status": r.status, "name": r.payload.get("name"), "payload": r.payload, "created_at": r.created_at} for r in rows]}

@router.get("/partners")
async def partners(repo: Annotated[FreightRepository, Depends(get_repository)]):
    return await _resources_for("partner_grant", repo)

@router.get("/governance/roles")
async def governance_roles(repo: Annotated[FreightRepository, Depends(get_repository)]):
    result = await _resources_for("governance_policy", repo)
    result["mode"] = "local_metadata_only"
    result["sso_scim"] = "not_configured_requires_enterprise_approval"
    return result

@router.get("/implementation/projects")
async def implementation_projects(repo: Annotated[FreightRepository, Depends(get_repository)]):
    return await _resources_for("implementation_project", repo)

@router.get("/platform-resources/{kind}")
async def platform_resources(kind: str, repo: Annotated[FreightRepository, Depends(get_repository)]):
    if not kind.replace("_", "").isalnum() or len(kind) > 64: raise HTTPException(422, detail={"code": "INVALID_RESOURCE_KIND", "message": "Invalid resource kind."})
    return await _resources_for(kind, repo)
