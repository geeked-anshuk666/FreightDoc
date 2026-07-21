from types import SimpleNamespace

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from starlette.requests import Request

from app import auth
from app.auth import require_current_user
from app import routers
from app.database import Base
from app.db_models import Shipment
from app.repositories import FreightRepository


@pytest.mark.asyncio
@pytest.mark.integration
async def test_repository_enforces_owner_scope_for_reads_and_writes():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions() as session:
        owner_a = FreightRepository(session, "owner-a")
        owner_b = FreightRepository(session, "owner-b")
        first = await owner_a.create_shipment({"product_name": "A"}, "A", "req-a")
        second = await owner_b.create_shipment({"product_name": "B"}, "B", "req-b")
        assert await owner_a.get_shipment(first.id)
        assert await owner_a.get_shipment(second.id) is None
        assert [row.id for row in await owner_a.list_shipments(10)] == [first.id]
        assert [row.id for row in await owner_b.list_shipments(10)] == [second.id]
        rows = (await session.execute(select(Shipment))).scalars().all()
        assert {row.owner_id for row in rows} == {"owner-a", "owner-b"}
        exported = await routers.export_account_data(auth.CurrentUser("owner-a"), session)
        assert [item["id"] for item in exported["shipments"]] == [first.id]
        assert exported["original_uploads_included"] is False
    await engine.dispose()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_clerk_missing_and_malformed_credentials_are_safe(monkeypatch):
    request = Request({"type": "http", "method": "GET", "path": "/api/shipments", "headers": []})
    monkeypatch.setattr(auth, "get_settings", lambda: SimpleNamespace(clerk_auth_configured=False))
    with pytest.raises(Exception) as caught:
        await require_current_user(request, None)
    assert caught.value.status_code == 503
    assert caught.value.detail["code"] == "AUTH_NOT_CONFIGURED"

    configured = SimpleNamespace(
        clerk_auth_configured=True,
        clerk_jwt_algorithms=("RS256",),
        clerk_issuer="https://issuer.example",
        clerk_audience=None,
    )
    monkeypatch.setattr(auth, "get_settings", lambda: configured)
    with pytest.raises(Exception) as caught:
        await require_current_user(request, None)
    assert caught.value.status_code == 401
    with pytest.raises(Exception) as caught:
        await require_current_user(request, SimpleNamespace(scheme="Bearer", credentials="not-a-jwt"))
    assert caught.value.status_code == 401
    assert caught.value.detail["code"] == "AUTH_INVALID"
