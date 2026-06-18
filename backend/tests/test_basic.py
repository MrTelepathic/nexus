"""Basic sanity tests for Nexus backend."""

import os
import sys

import pytest


def test_config_loads():
    """Verify that settings can be loaded from environment."""
    os.environ.setdefault("BOT_TOKEN", "test:token")
    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

    from bot.config import get_settings

    settings = get_settings()
    assert settings.app_env in ("development", "production", "testing")


def test_database_url_set():
    """Verify DATABASE_URL is configured."""
    os.environ.setdefault("BOT_TOKEN", "test:token")
    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

    from bot.config import get_settings

    settings = get_settings()
    assert "postgresql" in settings.database_url


def test_models_import():
    """Verify all SQLAlchemy models import cleanly."""
    from db.models import (
        Badge,
        KnowledgeBase,
        LLMCache,
        Message,
        Order,
        Payment,
        Product,
        Tenant,
        User,
        UserBadge,
        UserGamification,
        Wallet,
        WalletTransaction,
    )

    assert User is not None
    assert Tenant is not None
    assert Payment is not None
