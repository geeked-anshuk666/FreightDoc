import pytest
from pydantic import ValidationError

from app.models import Category, DocumentRequirements, ShipmentRequest
from app.services.doc_engine import DocumentEngine
from app.services.shipment_workflow import ShipmentStatus, can_transition, transition_error


def _shipment(**overrides):
    payload = {
        "product_name": "Bluetooth earbuds",
        "product_description": "500 wireless Bluetooth earbuds in retail packaging.",
        "origin_country": "us",
        "destination_country": "de",
        "quantity": 500,
        "declared_value": 25000,
    }
    payload.update(overrides)
    return ShipmentRequest(**payload)


@pytest.mark.unit
def test_shipment_normalizes_codes_and_rejects_bounds_and_extra_fields():
    assert _shipment().origin_country == "US"
    with pytest.raises(ValidationError):
        _shipment(quantity=0)
    with pytest.raises(ValidationError):
        _shipment(product_description="short")
    with pytest.raises(ValidationError):
        _shipment(unexpected="blocked")


@pytest.mark.unit
def test_corridor_rules_cover_bilateral_and_china_eu_matrix():
    engine = DocumentEngine()
    assert set(engine.supported_corridors()) >= {"CN-EU", "US-DE", "US-IN"}
    us_de = engine.requirements_for("US", "DE", Category.electronics)
    assert isinstance(us_de, DocumentRequirements)
    assert "ce_declaration" in us_de.required_docs
    cn_fr = engine.requirements_for("CN", "FR", Category.other)
    assert cn_fr.corridor == "CN-EU"
    with pytest.raises(ValueError):
        _shipment(origin_country="CN", destination_country="BR")


@pytest.mark.unit
def test_status_transition_matrix_is_explicit_and_idempotent():
    assert can_transition("draft", "processing")
    assert can_transition("processing", "review_ready")
    assert not can_transition("archived", "draft")
    assert not can_transition("bogus", "draft")
    assert transition_error("draft", "draft") is None
    assert transition_error("draft", "archived") is None
    assert "cannot move" in transition_error("archived", "draft")
