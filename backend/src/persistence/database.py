"""
Database engine with automatic PostgreSQL → SQLite fallback.

When PostgreSQL is configured but unreachable (e.g. Docker not running during
local dev), the module probes the socket before committing to an engine, and
silently downgrades to a local SQLite file so the rest of the app can still
start.  Set FORCE_POSTGRES=1 in the environment to disable the fallback and
fail fast (recommended in staging / production).
"""

import asyncio
import logging
import os
import socket

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

SQLITE_FALLBACK_URL = "sqlite+aiosqlite:///./studio_guardian.db"


def _postgres_reachable(db_url: str, timeout: float = 2.0) -> bool:
    """Synchronous TCP probe – quick check before creating the async engine."""
    try:
        # Parse host/port from the URL (handles asyncpg and psycopg2 dialects)
        # e.g. postgresql+asyncpg://user:pass@host:5432/db
        after_at = db_url.split("@")[-1]          # host:port/db
        host_port = after_at.split("/")[0]         # host:port
        if ":" in host_port:
            host, port_str = host_port.rsplit(":", 1)
            port = int(port_str)
        else:
            host, port = host_port, 5432
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception as exc:
        logger.warning("PostgreSQL not reachable at %s (%s). Will use SQLite fallback.", db_url, exc)
        return False


def _choose_db_url() -> str:
    configured = settings.DATABASE_URL
    force_postgres = os.getenv("FORCE_POSTGRES", "")

    if "postgresql" in configured:
        if force_postgres:
            logger.info("FORCE_POSTGRES set – using PostgreSQL at %s", configured)
            return configured
        if _postgres_reachable(configured):
            logger.info("PostgreSQL reachable – connecting to %s", configured)
            return configured
        logger.warning(
            "Falling back to SQLite (%s). "
            "Start PostgreSQL (docker compose up -d db) or set FORCE_POSTGRES=1 to suppress fallback.",
            SQLITE_FALLBACK_URL,
        )
        return SQLITE_FALLBACK_URL

    return configured


_effective_url = _choose_db_url()

_engine_kwargs: dict = dict(echo=False, future=True, pool_pre_ping=True)
if "sqlite" in _effective_url:
    # SQLite doesn't support connection pools the same way
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(_effective_url, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    import src.persistence.models  # Ensure all model classes are imported & registered
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialised (engine: %s)", _effective_url.split("@")[-1] if "@" in _effective_url else _effective_url)
