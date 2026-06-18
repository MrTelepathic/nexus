"""Orders API — order management with idempotency."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import require_auth

router = APIRouter()


class OrderCreate(BaseModel):
    items: list[dict]
    idempotency_key: str | None = None  # Client-generated for idempotency


class OrderResponse(BaseModel):
    id: str
    status: str
    total_amount: float
    currency: str
    items: list[dict]
    created_at: str


@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    order: OrderCreate,
    user=Depends(require_auth),
):
    """Create an order with idempotency protection.

    SECURITY: If idempotency_key is provided and already exists,
    return the existing order instead of creating a duplicate.
    """
    idempotency_key = order.idempotency_key or str(uuid.uuid4())

    # TODO: INSERT INTO orders ... ON CONFLICT (idempotency_key) DO NOTHING
    # Returning existing order if conflict

    return OrderResponse(
        id=str(uuid.uuid4()),
        status="pending",
        total_amount=0.0,
        currency="XTR",
        items=order.items,
        created_at="2024-01-15T10:30:00Z",
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, user=Depends(require_auth)):
    """Get order details."""
    raise HTTPException(status_code=404, detail="Order not found")
