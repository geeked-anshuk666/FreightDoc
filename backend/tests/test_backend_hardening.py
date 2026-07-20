"""Focused regression tests for zero-cost production hardening."""

import asyncio
from types import SimpleNamespace

import pytest

from app.main import _request_id
from app.rate_limit import InMemoryRateLimiter
from app import routers
from app.services.hts_api import DEFAULT_FALLBACK_TARIFF, fallback_tariff
from app.services.groq_client import AIServiceError, GroqClient
from app.models import ClassificationResult


def test_request_id_rejects_header_injection_and_overlong_values() -> None:
    assert _request_id("trace-123") == "trace-123"
    assert _request_id("trace\r\nX-Injected: yes") != "trace\r\nX-Injected: yes"
    assert len(_request_id("x" * 81)) == 36  # fresh UUID


def test_unknown_valid_corridor_uses_bounded_tariff_fallback() -> None:
    assert fallback_tariff("CN-EU") == 6.0
    assert fallback_tariff("CN-FR") == DEFAULT_FALLBACK_TARIFF


def test_ai_rate_limit_error_includes_retry_hint() -> None:
    error = routers.ai_error(RuntimeError(), request_id="req", stage="generation")
    # Unknown exceptions intentionally remain generic rather than being
    # classified as provider rate limits.
    assert error.headers is None

    provider_error = RuntimeError()
    provider_error.code = "AI_RATE_LIMITED"
    provider_error.stage = "generation"
    provider_error.request_id = "req"
    rate_limited = routers.ai_error(provider_error, request_id="req", stage="generation")
    assert rate_limited.headers == {"Retry-After": "5"}


@pytest.mark.asyncio
async def test_rate_limiter_caps_client_bucket_memory(monkeypatch) -> None:
    limiter = InMemoryRateLimiter()
    limiter._MAX_KEYS = 2
    monkeypatch.setattr("app.rate_limit.get_settings", lambda: SimpleNamespace(rate_limit_window_seconds=60))
    await limiter.check("bucket:a", 1)
    await limiter.check("bucket:b", 1)
    await limiter.check("bucket:c", 1)
    assert len(limiter._events) <= 2


@pytest.mark.asyncio
async def test_groq_provider_call_obeys_application_timeout(monkeypatch) -> None:
    class SlowCompletions:
        async def create(self, **_kwargs):
            await asyncio.sleep(1.1)

    # Keep this test independent of the real environment and provider key.
    monkeypatch.setattr(
        "app.services.groq_client.get_settings",
        lambda: SimpleNamespace(ai_model="test", request_timeout_seconds=1),
    )
    client = object.__new__(GroqClient)
    client.client = SimpleNamespace(chat=SimpleNamespace(completions=SlowCompletions()))
    with pytest.raises(AIServiceError) as caught:
        await client._request("system", {}, ClassificationResult, "req-timeout", stage="classification")
    assert caught.value.code == "AI_SERVICE_ERROR"
    assert caught.value.stage == "classification"
