import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app import routers
from app.models import ClassificationResult
from app.services import groq_client
from app.services.groq_client import AIServiceError, GroqClient
from app.services.pipeline import PipelineService, PipelineStageError


PAYLOAD = {
    "product_name": "Bluetooth earbuds",
    "product_description": "500 wireless Bluetooth earbuds in retail packaging.",
    "origin_country": "US",
    "destination_country": "DE",
    "quantity": 500,
    "declared_value": 25000,
}


class _BadJsonCompletions:
    def __init__(self) -> None:
        self.calls = 0

    async def create(self, **_kwargs):
        self.calls += 1
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="not-json"))])


class _RateLimitedCompletions:
    def __init__(self) -> None:
        self.calls = 0

    async def create(self, **_kwargs):
        self.calls += 1
        error = RuntimeError("provider response must not be exposed")
        error.status_code = 429
        raise error


def _client_with(completions) -> GroqClient:
    client = object.__new__(GroqClient)
    client.client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    return client


def test_missing_groq_config_has_safe_non_retryable_error(monkeypatch):
    monkeypatch.setattr(groq_client, "get_settings", lambda: SimpleNamespace(ai_model="test-model"))
    client = object.__new__(GroqClient)
    client.client = None

    async def invoke():
        with pytest.raises(AIServiceError) as caught:
            await client._request("system", {}, ClassificationResult, "req-config", stage="classification")
        return caught.value

    error = asyncio.run(invoke())

    assert error.code == "AI_CONFIGURATION_ERROR"
    assert error.stage == "classification"
    assert error.request_id == "req-config"
    assert error.retryable is False


def test_malformed_groq_output_retries_once_and_is_safe(monkeypatch):
    monkeypatch.setattr(groq_client, "get_settings", lambda: SimpleNamespace(ai_model="test-model"))
    completions = _BadJsonCompletions()

    async def invoke():
        with pytest.raises(AIServiceError) as caught:
            await _client_with(completions)._request("system", {}, ClassificationResult, "req-json", stage="classification")
        return caught.value

    error = asyncio.run(invoke())

    assert completions.calls == 2
    assert error.code == "AI_MALFORMED_RESPONSE"
    assert error.status_code == 502
    assert error.retryable is True


def test_groq_rate_limit_maps_to_retryable_429(monkeypatch):
    monkeypatch.setattr(groq_client, "get_settings", lambda: SimpleNamespace(ai_model="test-model"))
    completions = _RateLimitedCompletions()

    async def invoke():
        with pytest.raises(AIServiceError) as caught:
            await _client_with(completions)._request("system", {}, ClassificationResult, "req-rate", stage="generation")
        return caught.value

    error = asyncio.run(invoke())

    assert completions.calls == 2
    assert error.code == "AI_RATE_LIMITED"
    assert error.status_code == 429
    assert error.stage == "generation"


def test_pipeline_tags_non_ai_invalid_input_stage():
    class AI:
        async def classify_product(self, *_):
            return ClassificationResult(
                hs_code="851830",
                hs_description="Headphones",
                confidence=0.9,
                category="electronics",
                notes="test",
            )

    class Rules:
        def requirements_for(self, *_):
            raise ValueError("unsafe internal detail")

    from app.models import ShipmentRequest

    shipment = ShipmentRequest(**PAYLOAD)
    async def invoke():
        with pytest.raises(PipelineStageError) as caught:
            await PipelineService(ai=AI(), rules=Rules()).run(shipment, "req-rules")
        return caught.value

    error = asyncio.run(invoke())

    assert error.code == "PIPELINE_INPUT_INVALID"
    assert error.stage == "requirements"
    assert error.status_code == 422
    assert error.retryable is False


def test_full_pipeline_returns_safe_stage_aware_envelope(monkeypatch):
    class FailingPipeline:
        async def run(self, _shipment, request_id):
            raise AIServiceError(
                code="AI_RATE_LIMITED",
                stage="generation",
                request_id=request_id,
                retryable=True,
                status_code=429,
            )

    monkeypatch.setattr(routers, "PipelineService", lambda: FailingPipeline())
    request = Request({"type": "http", "method": "POST", "path": "/api/full-pipeline", "headers": []})
    request.state.request_id = "req-http"
    from app.models import ShipmentRequest

    async def invoke():
        with pytest.raises(HTTPException) as caught:
            await routers.full_pipeline(ShipmentRequest(**PAYLOAD), request)
        return caught.value

    error = asyncio.run(invoke())

    assert error.status_code == 429
    assert error.detail == {
        "code": "AI_RATE_LIMITED",
        "message": "The AI document service is temporarily rate-limited during the generation step. Please retry shortly.",
        "stage": "generation",
        "request_id": "req-http",
        "retryable": True,
    }


def test_error_envelope_never_uses_raw_provider_text():
    error = routers.ai_error(
        RuntimeError("provider response with a secret must never reach the browser"),
        request_id="req-safe",
        stage="validation",
    )

    assert error.status_code == 502
    assert error.detail["code"] == "AI_SERVICE_ERROR"
    assert error.detail["stage"] == "validation"
    assert error.detail["request_id"] == "req-safe"
    assert error.detail["retryable"] is True
    assert "secret" not in str(error.detail)
