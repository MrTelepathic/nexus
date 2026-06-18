"""Nexus database models.

Import all models here so Alembic can discover them for autogeneration.
"""

from db.models.automation import AutomationStep, AutomationWorkflow
from db.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin
from db.models.business import BusinessConnection
from db.models.conversation import Conversation, Message
from db.models.gamification import Badge, UserBadge, UserGamification
from db.models.knowledge import KnowledgeBase, LLMCache
from db.models.order import Order
from db.models.payment import Payment
from db.models.product import Product, ProductReview
from db.models.referral import Referral, ReferralCommission
from db.models.tenant import Tenant
from db.models.user import User
from db.models.wallet import Wallet, WalletTransaction

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "TenantMixin",
    "User",
    "Tenant",
    "Conversation",
    "Message",
    "BusinessConnection",
    "Product",
    "ProductReview",
    "Order",
    "Payment",
    "Wallet",
    "WalletTransaction",
    "UserGamification",
    "Badge",
    "UserBadge",
    "Referral",
    "ReferralCommission",
    "AutomationWorkflow",
    "AutomationStep",
    "KnowledgeBase",
    "LLMCache",
]
