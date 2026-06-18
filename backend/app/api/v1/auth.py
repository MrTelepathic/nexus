"""Auth endpoints — initData verification."""

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from bot.config import get_settings
from bot.utils.crypto import validate_init_data
from app.dependencies import get_redis

router = APIRouter()


class InitDataRequest(BaseModel):
    init_data: str


class AuthResponse(BaseModel):
    user_id: int
    username: str | None
    first_name: str | None
    is_valid: bool


@router.post("/verify", response_model=AuthResponse)
async def verify_init_data(
    request: InitDataRequest,
    redis=Depends(get_redis),
):
    """Verify Telegram Mini App initData and return user info.

    This is the primary authentication endpoint for the Mini App.
    The frontend calls this on load to establish a session.

    SECURITY: HMAC-SHA-256 signature is validated.
    Replay attacks are prevented via Redis nonce store.
    """
    settings = get_settings()

    result = await validate_init_data(
        bot_token=settings.bot_token_str,
        init_data=request.init_data,
        redis=redis,
    )

    if not result:
        raise HTTPException(status_code=401, detail="Invalid init data")

    user_data = json.loads(result.get("user", "{}"))

    return AuthResponse(
        user_id=user_data.get("id", 0),
        username=user_data.get("username"),
        first_name=user_data.get("first_name"),
        is_valid=True,
    )
