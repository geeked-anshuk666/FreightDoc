import base64
import pytest
from app.models import Category, ClassificationResult, DocumentPackage, ShipmentRequest, TariffData, ValidationResult
from app.services.doc_engine import DocumentEngine
from app.services.pdf_generator import render_documents
from app.services.pipeline import PipelineService


def shipment(destination="DE"):
    return ShipmentRequest(product_name="Bluetooth earbuds", product_description="500 wireless Bluetooth earbuds in retail packaging.", origin_country="US", destination_country=destination, quantity=500, declared_value=25000)


def test_country_rules_add_ce_for_electronics():
    rules = DocumentEngine().requirements_for("US", "DE", Category.electronics)
    assert "ce_declaration" in rules.required_docs


def test_china_requires_eu_member_destination():
    with pytest.raises(ValueError):
        ShipmentRequest(product_name="Cable", product_description="Electrical cable assembly for industrial machinery.", origin_country="CN", destination_country="EU", quantity=1, declared_value=10)


def test_pdf_renderer_returns_pdf_bytes():
    pdf = render_documents({"commercial_invoice": {"quantity": 1}})[0]
    assert base64.b64decode(pdf.content_base64).startswith(b"%PDF")


@pytest.mark.asyncio
async def test_pipeline_adds_missing_document_error():
    class AI:
        async def classify_product(self, *_): return ClassificationResult(hs_code="851830", hs_description="Headphones", confidence=0.9, category="electronics", notes="test")
        async def generate_documents(self, *_): return DocumentPackage(commercial_invoice={"quantity": 500, "declared_value": 25000}, packing_list={"quantity": 500, "declared_value": 25000}, certificate_of_origin={}, customs_declaration={})
        async def validate_documents(self, *_): return ValidationResult(errors=[], compliance_score=100, ready_to_ship=True)
    async def tariff(*_): return TariffData(duty_rate=4.0, source="test", retrieved_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc))
    response = await PipelineService(ai=AI(), usitc_lookup=tariff, comtrade_lookup=tariff).run(shipment(), "test")
    assert any(error.document == "ce_declaration" for error in response.validation.errors)
