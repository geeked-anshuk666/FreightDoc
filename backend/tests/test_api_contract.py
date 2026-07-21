import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app import routers
from app.main import app, health
from app.models import Category, ClassificationResult, DocumentPackage, GenerateRequest, ShipmentRequest, ValidateRequest


PAYLOAD = {
    "product_name": "Bluetooth earbuds",
    "product_description": "500 wireless Bluetooth earbuds in retail packaging.",
    "origin_country": "US",
    "destination_country": "DE",
    "quantity": 500,
    "declared_value": 25000,
}


def _request(path="/api/classify", request_id="req-test"):
    request = Request({"type": "http", "method": "POST", "path": path, "headers": []})
    request.state.request_id = request_id
    return request


@pytest.mark.contract
def test_openapi_exposes_public_pipeline_routes_and_health_schema():
    paths = app.openapi()["paths"]
    for path in ("/health", "/api/country-pairs", "/api/classify", "/api/generate", "/api/validate", "/api/full-pipeline"):
        assert path in paths
    assert app.version == "0.2.0"


@pytest.mark.contract
def test_openapi_exposes_every_authenticated_workspace_route():
    paths = app.openapi()["paths"]
    expected = {
        "/api/shipments",
        "/api/shipments/{shipment_id}",
        "/api/shipments/{shipment_id}/review",
        "/api/shipments/{shipment_id}/status",
        "/api/shipments/{shipment_id}/documents",
        "/api/shipments/{shipment_id}/documents/{document_id}/apply-suggestions",
        "/api/shipments/{shipment_id}/documents/{document_id}",
        "/api/shipments/{shipment_id}/documents/{document_id}/retry",
        "/api/shipments/{shipment_id}/dossiers/latest",
        "/api/shipments/{shipment_id}/dossiers",
        "/api/shipments/{shipment_id}/dossiers/{package_id}",
        "/api/shipments/{shipment_id}/dossiers/{package_id}/download/complete.pdf",
        "/api/shipments/{shipment_id}/dossiers/{package_id}/download/{document_name}.pdf",
        "/api/parties",
        "/api/account/export",
        "/api/account/data",
    }
    assert expected <= paths.keys()


@pytest.mark.asyncio
@pytest.mark.contract
async def test_health_and_country_pairs_are_provider_free():
    response = await health()
    assert response["status"] == "ok"
    pairs = await routers.country_pairs()
    assert "US-DE" in pairs["supported_corridors"]
    assert "legal_disclaimer" in pairs


@pytest.mark.asyncio
@pytest.mark.contract
async def test_classify_generate_validate_routes_delegate_with_correlation_id(monkeypatch):
    shipment = ShipmentRequest(**PAYLOAD)
    classification = ClassificationResult(hs_code="851830", hs_description="Headphones", confidence=0.9, category="electronics", notes="test")
    calls = []

    class FakeGroq:
        async def classify_product(self, value, request_id): calls.append(("classify", request_id)); return classification
        async def generate_documents(self, *args): calls.append(("generate", args[-1])); return {"ok": True}
        async def validate_documents(self, *args): calls.append(("validate", args[-1])); return {"ok": True}

    monkeypatch.setattr(routers, "GroqClient", FakeGroq)
    request = _request()
    assert await routers.classify(shipment, request) == classification
    requirements = routers.DocumentEngine().requirements_for("US", "DE", Category.electronics)
    generate_payload = GenerateRequest(shipment=shipment, classification=classification, requirements=requirements)
    validate_payload = ValidateRequest(shipment=shipment, classification=classification, requirements=requirements, documents=DocumentPackage(commercial_invoice={}, packing_list={}, certificate_of_origin={}, customs_declaration={}))
    await routers.generate(generate_payload, request)
    await routers.validate(validate_payload, request)
    assert calls == [("classify", "req-test"), ("generate", "req-test"), ("validate", "req-test")]


@pytest.mark.asyncio
@pytest.mark.contract
async def test_pipeline_error_envelope_is_stable_and_sanitized(monkeypatch):
    class Failing:
        async def run(self, shipment, request_id):
            error = RuntimeError("provider secret")
            error.code = "AI_RATE_LIMITED"; error.stage = "generation"; error.request_id = request_id
            raise error
    monkeypatch.setattr(routers, "PipelineService", lambda: Failing())
    with pytest.raises(HTTPException) as caught:
        await routers.full_pipeline(ShipmentRequest(**PAYLOAD), _request("/api/full-pipeline", "req-pipe"))
    assert caught.value.status_code == 429
    assert caught.value.headers == {"Retry-After": "5"}
    assert "provider secret" not in str(caught.value.detail)
    assert caught.value.detail["request_id"] == "req-pipe"
