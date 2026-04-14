import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import apply_cursor_pagination, build_cursor_page
from app.models.product import Product, ProductImage, ProductVariant
from app.schemas.product import (
    CategoryRef,
    ProductImageRef,
    ProductListItem,
    ProductListResponse,
)


async def list_products(
    db: AsyncSession,
    *,
    category_id: uuid.UUID | None = None,
    after: str | None = None,
    page_size: int = 20,
) -> ProductListResponse:
    """List products with optional category filter and cursor-based pagination.

    Returns products sorted by newest first (created_at desc).
    Only active, non-deleted products are returned.
    """
    # Build the base query selecting specific columns (no SELECT *)
    # We need: product fields + primary image + aggregated review/stock info
    query = select(Product).where(
        Product.is_active.is_(True),
        Product.deleted_at.is_(None),
    )

    # Apply category filter
    if category_id is not None:
        query = query.where(Product.category_id == category_id)

    # Apply cursor-based pagination, sorted by newest first
    query = apply_cursor_pagination(
        query=query,
        sort_column=Product.created_at,
        id_column=Product.id,
        page_size=page_size,
        after=after,
        sort_direction="desc",
    )

    result = await db.execute(query)
    products = list(result.scalars().all())

    # Build the cursor page
    cursor_page = build_cursor_page(
        rows=products,
        page_size=page_size,
        sort_column_name="created_at",
    )

    # Convert to response items
    items: list[ProductListItem] = []
    for product in cursor_page.items:
        # Get primary image (position=0 or first available)
        primary_image: ProductImageRef | None = None
        if product.images:
            sorted_images = sorted(product.images, key=lambda img: img.position)
            first_img = sorted_images[0]
            primary_image = ProductImageRef(
                url=first_img.url,
                alt_text=first_img.alt_text,
            )

        # Compute has_stock from variants
        has_stock = any(v.stock_quantity > 0 for v in product.variants)

        # Build category reference
        category_ref = CategoryRef(
            id=product.category.id,
            name=product.category.name,
            slug=product.category.slug,
        )

        # For now, average_rating and review_count are 0 (Review model not yet implemented)
        items.append(
            ProductListItem(
                id=product.id,
                name=product.name,
                slug=product.slug,
                description=product.description[:200] if len(product.description) > 200 else product.description,
                base_price=product.base_price,
                category=category_ref,
                primary_image=primary_image,
                average_rating=0.0,
                review_count=0,
                has_stock=has_stock,
            )
        )

    return ProductListResponse(
        items=items,
        next_cursor=cursor_page.next_cursor,
        has_next_page=cursor_page.has_next_page,
    )
