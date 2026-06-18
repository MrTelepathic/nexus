"""Business Connection model — stores connected Telegram business accounts."""

import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, TenantMixin


class BusinessConnection(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    """Telegram Business Connection record.

    Stores the business_connection_id and bot_token for each
    connected business account. The bot_token is encrypted at rest
    using pgcrypto (AES-256-GCM).

    SECURITY: bot_token column is encrypted. Access via service layer
    that handles decryption. Never log bot_token.
    """

    __tablename__ = "business_connections"

    business_connection_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    # Encrypted at rest — use pgcrypto or application-level encryption
    bot_token_encrypted: Mapped[str] = mapped_column(String(500), nullable=False)
    business_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    business_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Relationships — tenant resolved via tenant_id FK, no back_populates needed here
