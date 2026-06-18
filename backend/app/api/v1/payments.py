"""Payments API — multi-rail payment processing."""

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import require_auth

router = APIRouter()


class CreateInvoiceRequest(BaseModel):
    product_id: str
    currency: str = "XTR"  # XTR = Stars, TON, USD
    amount: float | None = None  # Override price (for custom amounts)


class InvoiceResponse(BaseModel):
    invoice_url: str
    payment_id: str
    amount: float
    currency: str


@router.post("/create-invoice", response_model=InvoiceResponse)
async def create_invoice(
    request: CreateInvoiceRequest,
    user=Depends(require_auth),
):
    """Create a payment invoice for Telegram Stars.

    Returns an invoice URL that the Mini App can use to
    trigger the Telegram payment flow.
    """
    payment_id = str(uuid.uuid4())

    # TODO: Create invoice via Telegram Bot API
    # bot.send_invoice(...)

    return InvoiceResponse(
        invoice_url=f"tg://invoice/{payment_id}",
        payment_id=payment_id,
        amount=request.amount or 0.0,
        currency=request.currency,
    )


@router.get("/history")
async def get_payment_history(user=Depends(require_auth)):
    """Get user's payment history."""
    return {"payments": []}
