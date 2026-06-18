"""User model — Telegram users within a tenant."""

from datetime import datetime

from db.models.base import Base, TenantMixin, TimestampMixin
from sqlalchemy import BigInteger, Boolean, DateTime, Float, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column


class User(Base, TenantMixin, TimestampMixin):
    """Telegram user record scoped to a tenant.

    The primary key is the Telegram user ID (BIGINT).
    Combined with tenant_id, this uniquely identifies a user
    within a specific business context.
    """

    __tablename__ = "users"

    # Telegram user ID is the primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    language_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String(50), default="customer")
    ltv: Mapped[float] = mapped_column(Float, default=0.0)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Composite unique: one user record per (tenant, telegram_id)
    __table_args__ = ({"schema": None},)

    # Relationships — tenant resolved via tenant_id FK
