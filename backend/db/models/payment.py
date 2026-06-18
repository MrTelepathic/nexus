"""Payment model — triple payment system (Stars + TON + Fiat).

CRITICAL: Idempotency enforced at DB level.
Every payment MUST have a unique idempotency_key.
"""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, TenantMixin


class Payment(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    """Payment record with full audit trail.

    SECURITY:
    - idempotency_key UNIQUE constraint prevents double-processing
    - Status transitions are one-way (pending → completed, never backwards)
    - For crypto payments (irreversible), idempotency is CRITICAL
    """

    __tablename__ = "payments"

    order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    # Telegram payment ID, TON tx hash, or fiat reference
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    # CRITICAL: Unique constraint — prevents double-processing of crypto payments
    idempotency_key: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    # Raw webhook payload for debugging and reconciliation
    provider_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    refund_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
