"""Service layer for product reviews."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.core.pagination import apply_cursor_pagination, build_cursor_page
from app.models.product import Product
from app.models.review import Review
from app.schemas.review import ReviewItem, ReviewListResponse


async def list_reviews(
    db: AsyncSession,
    *,
    slug: str,
    after: str | None = None,
    page_size: int = 10,
) -> ReviewListResponse:
    """List reviews for a product identified by slug.

    Returns paginated reviews ordered by created_at descending (newest first).
    Raises NotFoundError if the product does not exist or is soft-deleted.
    """
    # Verify product exists and is active
    product_query = select(Product.id).where(
        Product.slug == slug,
        Product.is_active.is_(True),
        Product.deleted_at.is_(None),
    )
    result = await db.execute(product_query)
    product_id = result.scalar_one_or_none()

    if product_id is None:
        raise NotFoundError(
            detail="Product with this slug does not exist",
            code="PRODUCT_NOT_FOUND",
        )

    # Build review query
    query = select(Review).where(Review.product_id == product_id)

    # Apply cursor-based pagination ordered by created_at desc
    query = apply_cursor_pagination(
        query=query,
        sort_column=Review.created_at,
        id_column=Review.id,
        page_size=page_size,
        after=after,
        sort_direction="desc",
    )

    result = await db.execute(query)
    reviews = list(result.scalars().all())

    # Build cursor page
    cursor_page = build_cursor_page(
        rows=reviews,
        page_size=page_size,
        sort_column_name="created_at",
    )

    # Convert to response items
    items = [
        ReviewItem(
            id=review.id,
            rating=review.rating,
            text=review.text,
            reviewer_name=_get_reviewer_name(review),
            created_at=review.created_at,
        )
        for review in cursor_page.items
    ]

    return ReviewListResponse(
        items=items,
        next_cursor=cursor_page.next_cursor,
        has_next_page=cursor_page.has_next_page,
    )


def _get_reviewer_name(review: Review) -> str:
    """Get the display name for a reviewer.

    Currently returns a placeholder since the User model is not yet implemented.
    When the User model is available, this should look up the user's name.
    """
    # Placeholder: Use a shortened version of user_id as the display name
    # In production, this would be replaced with an actual user name lookup
    return f"User {str(review.user_id)[:8]}"


async def get_product_rating_stats(
    db: AsyncSession,
    *,
    product_id: "str | __import__('uuid').UUID",
) -> tuple[float, int, dict[str, int]]:
    """Compute aggregate rating statistics for a product.

    Returns:
        A tuple of (average_rating, review_count, rating_distribution).
        rating_distribution keys are "1" through "5", values are counts.
    """
    import uuid as uuid_mod

    if isinstance(product_id, str):
        product_id = uuid_mod.UUID(product_id)

    # Get count and average
    stats_query = select(
        func.count(Review.id).label("review_count"),
        func.coalesce(func.avg(Review.rating), 0).label("average_rating"),
    ).where(Review.product_id == product_id)

    result = await db.execute(stats_query)
    row = result.one()
    review_count = int(row.review_count)
    average_rating = float(row.average_rating)

    # Get distribution
    dist_query = (
        select(
            Review.rating,
            func.count(Review.id).label("count"),
        )
        .where(Review.product_id == product_id)
        .group_by(Review.rating)
    )

    result = await db.execute(dist_query)
    dist_rows = result.all()

    rating_distribution: dict[str, int] = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
    }
    for dist_row in dist_rows:
        rating_distribution[str(dist_row.rating)] = int(dist_row.count)

    return average_rating, review_count, rating_distribution
