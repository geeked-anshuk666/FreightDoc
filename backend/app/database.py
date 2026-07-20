"""Async SQLAlchemy setup for Neon/Postgres.

Schema creation is intentionally delegated to Alembic.  The service does not
silently call ``create_all`` at startup because that masks missing migrations in
deployment.
"""

from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncGenerator

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


# psycopg's asynchronous connection implementation is incompatible with the
# Windows Proactor event loop. Set the compatible policy before Alembic or
# Uvicorn constructs the application's event loop/engine. Linux deployments
# (Render) retain their normal event-loop policy.
if sys.platform == "win32":  # pragma: no cover - platform-specific bootstrap
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def _database_configuration(database_url: str | None) -> tuple[str | None, dict]:
    if not database_url:
        return None, {}

    normalized = database_url
    if normalized.startswith("postgresql://"):
        # psycopg supports Neon's standard libpq connection options, including
        # sslmode and channel_binding. Keeping those options intact avoids the
        # authentication failures some asyncpg/Neon combinations can produce.
        normalized = normalized.replace("postgresql://", "postgresql+psycopg://", 1)
    return normalized, {}


_database_url, _connect_args = _database_configuration(get_settings().database_url)
engine = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None
if _database_url:
    engine_options: dict = {"pool_pre_ping": True, "connect_args": _connect_args}
    if not _database_url.startswith("sqlite"):
        # Conservative free-tier pool: it avoids exhausting Neon/Render limits.
        engine_options.update({"pool_size": 3, "max_overflow": 2, "pool_recycle": 1200})
    engine = create_async_engine(_database_url, **engine_options)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if not SessionLocal:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "DATABASE_NOT_CONFIGURED", "message": "Persistent workspace storage is not configured."},
        )
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
