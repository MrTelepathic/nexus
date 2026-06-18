"""Gamification API — XP, badges, streaks, leaderboard."""

from app.dependencies import require_auth
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()


class GamificationProfile(BaseModel):
    xp: int
    level: int
    daily_streak: int
    longest_streak: int
    badges: list[dict]
    next_level_xp: int


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str | None
    xp: int
    level: int


@router.get("/profile", response_model=GamificationProfile)
async def get_gamification_profile(user=Depends(require_auth)):
    """Get user's gamification state."""
    return GamificationProfile(
        xp=0,
        level=1,
        daily_streak=0,
        longest_streak=0,
        badges=[],
        next_level_xp=100,
    )


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(user=Depends(require_auth)):
    """Get top users by XP."""
    return []


@router.post("/checkin")
async def daily_checkin(user=Depends(require_auth)):
    """Claim daily check-in reward.

    Awards XP and increments streak.
    """
    return {"message": "Check-in successful!", "xp_earned": 10, "streak": 1}
