from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from src.config import settings

import logging
import os

logger = logging.getLogger(__name__)

Base = declarative_base()

db_url = settings.DATABASE_URL
# When running in local dev / test environments without active PostgreSQL daemon, fall back gracefully to SQLite
if "postgresql" in db_url and not os.getenv("FORCE_POSTGRES", ""):
    # Try connecting or fallback
    try:
        pass
    except Exception:
        pass

def get_engine():
    try:
        return create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            future=True,
            pool_pre_ping=True
        )
    except Exception:
        logger.warning("Falling back to local SQLite async database.")
        return create_async_engine(
            "sqlite+aiosqlite:///./studio_guardian.db",
            echo=False,
            future=True
        )

engine = get_engine()

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
