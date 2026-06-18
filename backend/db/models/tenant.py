"""Tenant model — root entity for multi-tenancy."""

from db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class Tenant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Multi-tenancy root. Every entity belongs to exactly one tenant."""

    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    owner_user_id: Mapped[int | None] = mapped_column(nullable=True)
    subscription: Mapped[str] = mapped_column(String(20), default="free")
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships — users and connections resolved via tenant_id FK
