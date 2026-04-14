import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.product import ProductListResponse
from app.services.product_service import list_products

router = APIRouter()


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List products",
    description="List products with optional category filter and cursor-based pagination.",
)
async def get_products(
    category_id: uuid.UUID | None = Query(None, description="Filter by category"),
    after: str | None = Query(None, description="Cursor token for pagination"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> ProductListResponse:
    """List products with optional category filter and cursor-based pagination.

    Products are sorted by newest first. Only active, non-deleted products are returned.
    """
    return await list_products(
        db,
        category_id=category_id,
        after=after,
        page_size=page_size,
    )
