"""Internal wallet and transaction models."""

import uuid

from db.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import BigInteger, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class Wallet(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    """Per-user wallet for internal currency (cashback, referral earnings).

    Balance is CHECK-constrained to >= 0 to prevent overdraft.
    """

    __tablename__ = "wallets"

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(3), default="XTR")


class WalletTransaction(Base, UUIDPrimaryKeyMixin, TenantMixin):
    """Immutable ledger of wallet balance changes.

    Every credit/debit is recorded with the balance_after for audit.
    """

    __tablename__ = "wallet_transactions"

    wallet_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    balance_after: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
