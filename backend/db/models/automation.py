"""No-code automation engine models."""

import uuid

from db.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column


class AutomationWorkflow(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    """User-created automation workflow (if-this-then-that)."""

    __tablename__ = "automation_workflows"

    creator_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger_config: Mapped[dict] = mapped_column(JSONB, nullable=False)


class AutomationStep(Base, UUIDPrimaryKeyMixin):
    """Individual step within a workflow."""

    __tablename__ = "automation_steps"

    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    action_config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    condition: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
