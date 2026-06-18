"""Order model — idempotent order processing."""

import uuid

from sqlalchemy import BigInteger, Float, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, TenantMixin


class Order(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    """Customer order with idempotency protection.

    SECURITY: idempotency_key has a UNIQUE constraint.
    Use ON CONFLICT DO NOTHING to prevent duplicate orders.
    """

    __tablename__ = "orders"

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    payment_method: Mapped[str | None] = mapped_column(String(20), nullable=True)
    payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # CRITICAL: Unique constraint prevents duplicate payments
    idempotency_key: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    items: Mapped[dict] = mapped_column(JSONB, default=list)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
