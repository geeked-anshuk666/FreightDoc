from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from dotenv import load_dotenv
load_dotenv(override=True)

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.database import Base
import app.db_models  # noqa: F401 - registers all metadata models

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _url() -> str:
    # Runtime API traffic can use Neon PgBouncer, but schema migrations need a
    # direct endpoint because Alembic uses session-dependent DDL operations.
    value = os.getenv("MIGRATIONS_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not value:
        raise RuntimeError("MIGRATIONS_DATABASE_URL or DATABASE_URL must be configured before running Alembic migrations")
    if value.startswith("postgresql://"):
        # Keep Neon's TLS and channel-binding options intact; psycopg is the
        # SQLAlchemy async driver used by both the API and migrations.
        value = value.replace("postgresql://", "postgresql+psycopg://", 1)
    return value


def run_migrations_offline() -> None:
    context.configure(url=_url(), target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _url()
    connectable = async_engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
