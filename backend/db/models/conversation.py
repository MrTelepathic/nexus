"""Conversation and Message models — distributed state machine.

Handles thousands of concurrent conversations across multiple
business accounts. State transitions are DB-backed for durability.
"""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, TenantMixin


class Conversation(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    """Per-user conversation state for a business connection.

    State machine: idle → active → awaiting_input → escalated → closed
    """

    __tablename__ = "conversations"

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    business_conn_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    state: Mapped[str] = mapped_column(String(30), default="idle")
    assigned_agent: Mapped[str | None] = mapped_column(String(30), nullable=True)
    context_window: Mapped[dict] = mapped_column(JSONB, default=list)
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    last_message_at: Mapped[datetime | None] = mapped_column(
        nullable=True, index=True
    )


class Message(Base, UUIDPrimaryKeyMixin, TenantMixin):
    """Individual message within a conversation.

    SECURITY: tenant_id is denormalized here for RLS enforcement.
    """

    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    agent_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
