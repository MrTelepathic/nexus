"""Basic sanity tests for Nexus backend."""

import pytest


def test_config_loads():
    """Verify that settings can be loaded from environment."""
    import os
    os.chdir("/home/runner/work/nexus/nexus") if os.path.exists("/home/runner/work/nexus/nexus") else None
    from bot.config import get_settings
    settings = get_settings()
    assert settings.app_env in ("development", "production", "testing")


def test_database_url_set():
    """Verify DATABASE_URL is configured."""
    from bot.config import get_settings
    settings = get_settings()
    assert "postgresql" in settings.database_url


def test_models_import():
    """Verify all SQLAlchemy models import cleanly."""
    from db.models import (
        User, Tenant, Conversation, Message,
        Product, Order, Payment,
        Wallet, WalletTransaction,
        UserGamification, Badge, UserBadge,
        KnowledgeBase, LLMCache,
    )
    assert User is not None
    assert Tenant is not None
    assert Payment is not None
