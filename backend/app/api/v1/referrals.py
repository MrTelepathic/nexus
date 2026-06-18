"""Referrals API — referral tree and commissions."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import require_auth

router = APIRouter()


class ReferralStats(BaseModel):
    referral_code: str
    total_referrals: int
    active_referrals: int
    total_earned: float
    pending_commissions: float


class ReferralEntry(BaseModel):
    user_id: int
    username: str | None
    joined_at: str
    total_purchases: float
    commission_earned: float


@router.get("/stats", response_model=ReferralStats)
async def get_referral_stats(user=Depends(require_auth)):
    """Get referral statistics."""
    return ReferralStats(
        referral_code="",
        total_referrals=0,
        active_referrals=0,
        total_earned=0.0,
        pending_commissions=0.0,
    )


@router.get("/tree", response_model=list[ReferralEntry])
async def get_referral_tree(user=Depends(require_auth)):
    """Get referral tree (direct referrals)."""
    return []
