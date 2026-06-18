"""CRM service — customer profiles, tagging, LTV tracking."""

import structlog
from db.models.user import User
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

log = structlog.get_logger()


async def get_customer_profile(session: AsyncSession, tenant_id, user_id: int) -> User | None:
    """Get full customer profile."""
    result = await session.execute(
        select(User).where(
            User.tenant_id == tenant_id,
            User.id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def update_customer_tags(session: AsyncSession, tenant_id, user_id: int, tags: list[str]):
    """Add tags to a customer (idempotent)."""
    await session.execute(
        update(User)
        .where(User.tenant_id == tenant_id, User.id == user_id)
        .values(tags=User.tags + tags)
    )
    await session.commit()


async def get_top_customers(session: AsyncSession, tenant_id, limit: int = 10):
    """Get top customers by lifetime value."""
    result = await session.execute(
        select(User).where(User.tenant_id == tenant_id).order_by(User.ltv.desc()).limit(limit)
    )
    return result.scalars().all()


async def get_customer_count(session: AsyncSession, tenant_id) -> int:
    """Count total customers for a tenant."""
    result = await session.execute(select(func.count(User.id)).where(User.tenant_id == tenant_id))
    return result.scalar_one() or 0


async def tag_paying_customer(session: AsyncSession, tenant_id, user_id: int):
    """Tag a customer who made a payment."""
    await update_customer_tags(session, tenant_id, user_id, ["paying_customer"])
    log.info("customer_tagged_paying", tenant_id=str(tenant_id), user_id=user_id)
