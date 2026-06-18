"""Gamification models — XP, badges, streaks."""

import uuid

from sqlalchemy import BigInteger, Boolean, Integer, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, TenantMixin


class UserGamification(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    """Per-user gamification state: XP, level, streak."""

    __tablename__ = "user_gamification"

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    daily_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_checkin: Mapped[str | None] = mapped_column(String(10), nullable=True)
    total_spent: Mapped[float] = mapped_column(default=0.0)


class Badge(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    """Achievement badge definition."""

    __tablename__ = "badges"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon_emoji: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rarity: Mapped[str] = mapped_column(String(20), default="common")
    xp_reward: Mapped[int] = mapped_column(Integer, default=0)
    conditions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserBadge(Base, TenantMixin):
    """Badge earned by a user."""

    __tablename__ = "user_badges"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    badge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
