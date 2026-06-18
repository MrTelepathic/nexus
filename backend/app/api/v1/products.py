"""Products API — CRUD for marketplace listings."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.dependencies import require_auth

router = APIRouter()


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    price: float
    currency: str = "XTR"
    stock: int = 0
    images: list[str] = []
    tags: list[str] = []


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str | None
    category: str | None
    price: float
    currency: str
    stock: int
    images: list[str]
    tags: list[str]
    rating: float | None
    review_count: int
    is_active: bool


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    user=Depends(require_auth),
    category: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """List products with optional filtering and search.

    Search uses full-text search (tsvector) for text queries.
    Category filtering uses an index.
    """
    # TODO: Query from DB with proper filtering
    return []


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, user=Depends(require_auth)):
    """Get a single product by ID."""
    # TODO: Query from DB
    raise HTTPException(status_code=404, detail="Product not found")


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    user=Depends(require_auth),
):
    """Create a new product listing.

    Only business owners and staff can create products.
    """
    # TODO: Insert into DB
    return ProductResponse(
        id="new-product-id",
        **product.model_dump(),
        rating=None,
        review_count=0,
        is_active=True,
    )
