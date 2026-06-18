"""Nexus database models.

Import all models here so Alembic can discover them for autogeneration.
"""

from db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, TenantMixin
from db.models.user import User
from db.models.tenant import Tenant
from db.models.conversation import Conversation, Message
from db.models.business import BusinessConnection
from db.models.product import Product, ProductReview
from db.models.order import Order
from db.models.payment import Payment
from db.models.wallet import Wallet, WalletTransaction
from db.models.gamification import UserGamification, Badge, UserBadge
from db.models.referral import Referral, ReferralCommission
from db.models.automation import AutomationWorkflow, AutomationStep
from db.models.knowledge import KnowledgeBase, LLMCache

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
