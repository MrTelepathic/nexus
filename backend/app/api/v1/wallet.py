"""Wallet API — internal balance and transactions."""

from app.dependencies import require_auth
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()


class WalletResponse(BaseModel):
    balance: float
    currency: str
    pending_cashback: float


class TransactionResponse(BaseModel):
    id: str
    amount: float
    balance_after: float
    type: str
    description: str | None
    created_at: str


@router.get("/balance", response_model=WalletResponse)
async def get_balance(user=Depends(require_auth)):
    """Get wallet balance."""
    return WalletResponse(
        balance=0.0,
        currency="XTR",
        pending_cashback=0.0,
    )


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(user=Depends(require_auth)):
    """Get transaction history."""
    return []
