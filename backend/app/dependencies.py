"""FastAPI dependency injection.

Provides:
- Database session per request (with tenant context)
- Redis client
- Auth (initData validation)
"""

from typing import AsyncGenerator

from fastapi import Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import get_settings
from db.engine import get_session


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency.

    Automatically sets tenant context from the authenticated user.
    """
    tenant_id = getattr(request.state, "tenant_id", None)
    async with get_session(tenant_id=str(tenant_id) if tenant_id else None) as session:
        yield session


async def get_redis(request: Request):
    """Redis client dependency."""
    return request.app.state.redis


async def require_auth(request: Request) -> dict:
    """Require valid Telegram Mini App initData.

    Validates HMAC-SHA-256 signature and extracts user info.
    Used as a dependency on protected routes.
    """
    settings = get_settings()

    # initData can come from:
    # 1. Header: X-Init-Data
    # 2. Cookie: init_data
    # 3. Query param: init_data (less secure, dev only)
    init_data = (
        request.headers.get("X-Init-Data")
        or request.cookies.get("init_data")
    )

    if not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication data",
        )

    import json
    from bot.utils.crypto import validate_init_data
    from redis.asyncio import Redis

    redis: Redis = request.app.state.redis
    result = await validate_init_data(
        bot_token=settings.bot_token_str,
        init_data=init_data,
        redis=redis,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication",
        )

    # Parse user data from initData
    user_data = json.loads(result.get("user", "{}"))
    request.state.user_id = user_data.get("id")
    request.state.tenant_id = getattr(request.state, "tenant_id", None)

    return {
        "user_id": user_data.get("id"),
        "username": user_data.get("username"),
        "first_name": user_data.get("first_name"),
    }
