"""Dashboard API — real-time business analytics."""

from app.dependencies import require_auth
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()


class DashboardStats(BaseModel):
    total_customers: int
    active_conversations: int
    revenue_today: float
    revenue_month: float
    total_orders: int
    avg_rating: float
    conversion_rate: float
    active_products: int


class RecentActivity(BaseModel):
    id: str
    type: str  # "sale", "review", "signup", "message"
    description: str
    timestamp: str
    user_name: str | None


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(user=Depends(require_auth)):
    """Get real-time dashboard statistics.

    In production, this aggregates data from multiple tables
    and is cached in Redis with a 30-second TTL.
    """
    # TODO: Query real data from DB
    return DashboardStats(
        total_customers=1234,
        active_conversations=89,
        revenue_today=2450.0,
        revenue_month=12450.0,
        total_orders=342,
        avg_rating=4.8,
        conversion_rate=3.2,
        active_products=47,
    )


@router.get("/activity", response_model=list[RecentActivity])
async def get_recent_activity(user=Depends(require_auth)):
    """Get recent business activity feed.

    Used by the real-time WebSocket dashboard.
    """
    return [
        RecentActivity(
            id="1",
            type="sale",
            description="New order: Starter Plan — 100 Stars",
            timestamp="2024-01-15T10:30:00Z",
            user_name="alice",
        ),
        RecentActivity(
            id="2",
            type="review",
            description="5-star review on Pro Plan",
            timestamp="2024-01-15T10:25:00Z",
            user_name="bob",
        ),
        RecentActivity(
            id="3",
            type="signup",
            description="New customer registered",
            timestamp="2024-01-15T10:20:00Z",
            user_name="charlie",
        ),
    ]
