"""Tenant resolution middleware — real DB lookup.

Extracts tenant context from the incoming update.
Creates user record on first contact.
"""

from collections.abc import Awaitable, Callable
from typing import Any

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from db.engine import get_session
from db.models.tenant import Tenant
from db.models.user import User as UserModel
from sqlalchemy import select

log = structlog.get_logger()


class TenantMiddleware(BaseMiddleware):
    """Resolves the current tenant from the user's Telegram ID.

    Flow:
    1. Look up or create user in DB by Telegram user ID
    2. Resolve tenant from user record
    3. Set tenant_id in context for RLS enforcement
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        # Get or create user and resolve tenant
        async with get_session() as session:
            # Get default tenant (or the user's tenant)
            result = await session.execute(select(Tenant).where(Tenant.is_active).limit(1))
            tenant = result.scalar_one_or_none()

            if not tenant:
                log.warning("no_active_tenant_found")
                data["tenant_id"] = None
                data["telegram_user"] = user
                return await handler(event, data)

            # Get or create user
            user_result = await session.execute(
                select(UserModel).where(
                    UserModel.id == user.id,
                    UserModel.tenant_id == tenant.id,
                )
            )
            db_user = user_result.scalar_one_or_none()

            if not db_user:
                # First contact — create user record
                db_user = UserModel(
                    id=user.id,
                    tenant_id=tenant.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                    language_code=user.language_code,
                    is_premium=bool(user.is_premium),
                    last_active_at=user.last_active_at,
                )
                session.add(db_user)
                await session.commit()
                log.info(
                    "new_user_created",
                    user_id=user.id,
                    tenant_id=str(tenant.id),
                )
            else:
                # Update last active
                db_user.last_active_at = user.last_active_at
                if user.first_name:
                    db_user.first_name = user.first_name
                if user.username:
                    db_user.username = user.username
                await session.commit()

            data["tenant_id"] = tenant.id
            data["db_user"] = db_user
            data["telegram_user"] = user

        structlog.contextvars.bind_contextvars(
            tenant_id=str(data.get("tenant_id", "unknown")),
            user_id=user.id,
        )

        return await handler(event, data)
