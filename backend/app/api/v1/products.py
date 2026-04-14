import uuid
from enum import StrEnum
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.product import ProductDetail, ProductListResponse
from app.services.product_service import SortOption, get_product_by_slug, list_products

router = APIRouter()


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List products",
    description="List products with optional category filter, full-text search, filtering, sorting, and cursor-based pagination.",
)
async def get_products(
    category_id: uuid.UUID | None = Query(None, description="Filter by category"),
    q: str | None = Query(None, description="Full-text search query"),
    min_price: int | None = Query(None, ge=0, description="Minimum price in cents"),
    max_price: int | None = Query(None, ge=0, description="Maximum price in cents"),
    min_rating: int | None = Query(None, ge=1, le=5, description="Minimum average rating (1-5)"),
    in_stock: bool | None = Query(None, description="If true, only show products with stock > 0"),
    sort: SortOption = Query(SortOption.NEWEST, description="Sort order: price_asc, price_desc, newest, popular"),
    after: str | None = Query(None, description="Cursor token for pagination"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> ProductListResponse:
    """List products with optional category filter, full-text search, filtering, sorting, and cursor-based pagination.

    Products are sorted by newest first by default. When a search query `q` is provided,
    results are ranked by relevance (sort parameter is ignored for search).
    Supports price range filtering, minimum rating, and in-stock filtering.
    Only active, non-deleted products are returned.
    """
    return await list_products(
        db,
        category_id=category_id,
        q=q,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        in_stock=in_stock,
        sort=sort,
        after=after,
        page_size=page_size,
    )


@router.get(
    "/{slug}",
    response_model=ProductDetail,
    summary="Get product detail",
    description="Get full product details by slug, including images, variants, and ratings.",
    responses={
        404: {
            "description": "Product not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Product with this slug does not exist", "code": "PRODUCT_NOT_FOUND"}
                }
            },
        }
    },
)
async def get_product_detail(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> ProductDetail:
    """Get full product detail by slug.

    Returns product with images (ordered by position), variants with resolved prices,
    category breadcrumb, ratings, and review summary. Returns 404 if product not found
    or soft-deleted.
    """
    return await get_product_by_slug(db, slug=slug)
