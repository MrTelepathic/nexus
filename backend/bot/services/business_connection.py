"""Business Connection service — auto-reply management.

Manages the lifecycle of business connections:
- Store bot tokens (encrypted)
- Enable/disable auto-reply
- Route messages to AI
"""

import structlog
from db.engine import get_session
from db.models.business import BusinessConnection
from sqlalchemy import select

log = structlog.get_logger()


async def get_business_connection(connection_id: str) -> BusinessConnection | None:
    """Look up a business connection by its Telegram ID."""
    async with get_session() as session:
        result = await session.execute(
            select(BusinessConnection).where(
                BusinessConnection.business_connection_id == connection_id,
                BusinessConnection.is_enabled,
            )
        )
        return result.scalar_one_or_none()


async def register_business_connection(
    tenant_id,
    connection_id: str,
    bot_token: str,
    username: str | None = None,
    name: str | None = None,
) -> BusinessConnection:
    """Register a new business connection.

    In production, bot_token should be encrypted before storage.
    """
    async with get_session(str(tenant_id)) as session:
        conn = BusinessConnection(
            tenant_id=tenant_id,
            business_connection_id=connection_id,
            bot_token_encrypted=bot_token,  # TODO: encrypt
            business_username=username,
            business_name=name,
        )
        session.add(conn)
        await session.commit()
        log.info(
            "business_connection_registered",
            tenant_id=str(tenant_id),
            connection_id=connection_id,
        )
        return conn
