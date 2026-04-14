from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.category import CategoryListResponse
from app.services.category_service import get_category_tree

router = APIRouter()


@router.get(
    "",
    response_model=CategoryListResponse,
    summary="Get category tree",
    description="Returns the full category tree (max 2 levels) with product counts.",
)
async def list_categories(
    db: AsyncSession = Depends(get_db),
) -> CategoryListResponse:
    """Get the full category tree with product counts for active products."""
    categories = await get_category_tree(db)
    return CategoryListResponse(items=categories)
