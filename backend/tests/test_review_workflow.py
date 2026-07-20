import pytest
from pydantic import ValidationError

from app.models import ShipmentStatusUpdate, SuggestionApplicationRequest
from app.services.shipment_workflow import ShipmentStatus, can_transition, transition_error


def test_review_workflow_requires_processing_before_readiness():
    assert can_transition(ShipmentStatus.DRAFT.value, ShipmentStatus.PROCESSING.value)
    assert not can_transition(ShipmentStatus.DRAFT.value, ShipmentStatus.REVIEW_READY.value)
    assert can_transition(ShipmentStatus.PROCESSING.value, ShipmentStatus.NEEDS_REVIEW.value)
    assert can_transition(ShipmentStatus.PROCESSING.value, ShipmentStatus.REVIEW_READY.value)
    assert not can_transition(ShipmentStatus.ARCHIVED.value, ShipmentStatus.DRAFT.value)


def test_transition_error_is_safe_for_unknown_legacy_status():
    assert transition_error("unknown", ShipmentStatus.PROCESSING.value)


def test_status_update_exposes_only_review_workflow_actions():
    assert ShipmentStatusUpdate(status="archived").status == "archived"
    with pytest.raises(ValidationError):
        ShipmentStatusUpdate(status="dossier_generated")


def test_suggestion_request_is_limited_to_shipment_facts():
    assert SuggestionApplicationRequest(fields=["currency", "declared_value"]).fields == ["currency", "declared_value"]
    with pytest.raises(ValidationError):
        SuggestionApplicationRequest(fields=["invoice_number"])
