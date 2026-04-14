from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.review import ReviewListResponse
from app.services.review_service import list_reviews

router = APIRouter()


@router.get(
    "",
    response_model=ReviewListResponse,
    summary="List product reviews",
    description="List reviews for a product with cursor-based pagination, ordered by newest first.",
    responses={
        404: {
            "description": "Product not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Product with this slug does not exist", "code": "PRODUCT_NOT_FOUND"}
                }
            },
        },
        400: {
            "description": "Invalid cursor",
            "content": {
                "application/json": {
                    "example": {"detail": "Malformed pagination cursor", "code": "INVALID_CURSOR"}
                }
            },
        },
    },
)
async def get_product_reviews(
    slug: str,
    after: str | None = Query(None, description="Cursor token for pagination"),
    page_size: int = Query(10, ge=1, le=50, description="Number of reviews per page"),
    db: AsyncSession = Depends(get_db),
) -> ReviewListResponse:
    """List reviews for a product identified by slug.

    Returns paginated reviews with reviewer names, star ratings, review text,
    and timestamps. Results are ordered by newest first.
    """
    return await list_reviews(
        db,
        slug=slug,
        after=after,
        page_size=page_size,
    )
