"""Referral system models — multi-level referral tree."""

import uuid

from sqlalchemy import BigInteger, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, TenantMixin


class Referral(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    """Referral relationship: referrer → referred."""

    __tablename__ = "referrals"

    referrer_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    referred_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    commission_rate: Mapped[float] = mapped_column(Float, default=0.10)
    total_earned: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(default=True)


class ReferralCommission(Base, UUIDPrimaryKeyMixin, TenantMixin):
    """Commission earned from a referred user's purchase."""

    __tablename__ = "referral_commissions"

    referral_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    source_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default="pending")
