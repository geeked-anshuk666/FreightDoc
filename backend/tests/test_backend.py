import base64
import pytest
from app.models import Category, ClassificationResult, DocumentPackage, PlatformResourceRequest, ShipmentRequest, TariffData, ValidationResult
from app.services.doc_engine import DocumentEngine
from app.services.pdf_generator import render_documents
from app.services.pipeline import PipelineService
from app.services.groq_client import AIServiceError
from pydantic import ValidationError as PydanticValidationError


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


@pytest.mark.asyncio
async def test_pipeline_completes_with_deterministic_fallback_when_ai_is_unavailable():
    class OfflineAI:
        async def classify_product(self, *_):
            raise AIServiceError(code="AI_CONFIGURATION_ERROR", stage="classification", request_id="offline", retryable=False)
        async def generate_documents(self, *_):
            raise AIServiceError(code="AI_CONFIGURATION_ERROR", stage="generation", request_id="offline", retryable=False)
        async def validate_documents(self, *_):
            raise AIServiceError(code="AI_CONFIGURATION_ERROR", stage="validation", request_id="offline", retryable=False)

    async def tariff(*_):
        return TariffData(duty_rate=4.0, source="deterministic fixture", retrieved_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc))

    response = await PipelineService(ai=OfflineAI(), usitc_lookup=tariff, comtrade_lookup=tariff).run(shipment(), "offline")
    assert response.documents.commercial_invoice["prepared_mode"] == "deterministic_template"
    assert {stage.step for stage in response.status if stage.status == "fallback"} >= {"classification", "generation", "validation"}
    assert response.classification.confidence < 0.5
    assert response.pdfs


def test_platform_resource_metadata_rejects_credentials():
    with pytest.raises(PydanticValidationError):
        PlatformResourceRequest(name="Carrier adapter", payload={"api_key": "must-not-store"})
    accepted = PlatformResourceRequest(name="Manual CSV mapping", payload={"columns": ["invoice_number", "quantity"]})
    assert accepted.payload["columns"] == ["invoice_number", "quantity"]
