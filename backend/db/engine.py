"""Async SQLAlchemy engine and session factory.

Provides:
- Async engine with connection pooling
- Session factory with automatic tenant context setting
- Dependency injection for FastAPI and aiogram handlers

SECURITY: Every session sets the tenant_id for Row-Level Security.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text

from bot.config import get_settings


def create_engine():
    """Create async SQLAlchemy engine with production-ready pool settings."""
    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,          # Verify connections before use
        pool_recycle=3600,           # Recycle connections after 1 hour
        echo=settings.app_debug,     # Log SQL in debug mode
    )


engine = create_engine()

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session(tenant_id: str | None = None) -> AsyncGenerator[AsyncSession, None]:
    """Get a database session with optional tenant context.

    Usage:
        async with get_session(tenant_id="...") as session:
            result = await session.execute(select(User).where(...))

    If tenant_id is provided, sets the PostgreSQL session variable
    for Row-Level Security enforcement.
    """
    async with async_session_factory() as session:
        if tenant_id:
            await session.execute(
                text("SELECT set_config('app.current_tenant', :tenant, true)"),
                {"tenant": tenant_id},
            )
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_session_dependency(tenant_id: str | None = None) -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions.

    Usage in routes:
        @router.get("/items")
        async def list_items(session: AsyncSession = Depends(get_db)):
            ...
    """
    async with get_session(tenant_id=tenant_id) as session:
        yield session


async def init_db() -> None:
    """Initialize database: verify connection and run any pending migrations.

    Called once at application startup.
    """
    settings = get_settings()
    async with engine.begin() as conn:
        # Verify connection
        await conn.execute(text("SELECT 1"))

        # Ensure pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        # Ensure UUID extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))

    from structlog import get_logger
    log = get_logger()
    log.info("database_connected", url=settings.database_url.split("@")[-1])


async def close_db() -> None:
    """Dispose of the engine connection pool.

    Called once at application shutdown.
    """
    await engine.dispose()
