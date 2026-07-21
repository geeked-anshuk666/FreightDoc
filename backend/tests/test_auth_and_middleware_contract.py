import httpx
import pytest

from app.main import app


@pytest.mark.asyncio
@pytest.mark.contract
async def test_health_middleware_emits_correlation_and_security_headers():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health", headers={"X-Request-ID": "safe-trace"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "safe-trace"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


@pytest.mark.asyncio
@pytest.mark.contract
async def test_json_body_limit_returns_stable_413_without_calling_route():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/classify",
            content=b"x" * (1024 * 1024 + 1),
            headers={"Content-Length": str(1024 * 1024 + 1), "X-Request-ID": "limit-test"},
        )
    assert response.status_code == 413
    assert response.json()["detail"]["code"] == "REQUEST_TOO_LARGE"
    assert response.json()["detail"]["request_id"] == "limit-test"
