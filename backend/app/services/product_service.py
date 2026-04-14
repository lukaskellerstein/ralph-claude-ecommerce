import base64
import json
import uuid
from enum import StrEnum

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.core.pagination import apply_cursor_pagination, build_cursor_page, decode_cursor
from app.models.product import Product, ProductImage, ProductVariant
from app.schemas.product import (
    CategoryRef,
    CategoryWithParent,
    ProductDetail,
    ProductImageDetail,
    ProductImageRef,
    ProductListItem,
    ProductListResponse,
    ProductVariantDetail,
)


class SortOption(StrEnum):
    """Allowed sort options for product listing."""

    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    NEWEST = "newest"
    POPULAR = "popular"


def _build_product_list_item(product: Product) -> ProductListItem:
    """Convert a Product ORM instance to a ProductListItem response schema."""
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
    return ProductListItem(
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


async def list_products(
    db: AsyncSession,
    *,
    category_id: uuid.UUID | None = None,
    q: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    min_rating: int | None = None,
    in_stock: bool | None = None,
    sort: SortOption = SortOption.NEWEST,
    after: str | None = None,
    page_size: int = 20,
) -> ProductListResponse:
    """List products with optional category filter, full-text search, filtering, sorting, and cursor-based pagination.

    Filters:
      - min_price / max_price: filter by base_price in cents
      - min_rating: filter by minimum average rating (placeholder, currently no-op)
      - in_stock: if True, only products with at least one variant with stock > 0

    Sort options:
      - newest: created_at desc (default)
      - price_asc: base_price asc
      - price_desc: base_price desc
      - popular: placeholder, falls back to newest

    When a search query `q` is provided, results are ranked by relevance using
    PostgreSQL ts_rank against the search_vector column (sort is ignored for search).
    Only active, non-deleted products are returned.
    """
    is_search = q is not None and q.strip() != ""

    if is_search:
        return await _list_products_search(
            db,
            q=q,  # type: ignore[arg-type]
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            in_stock=in_stock,
            after=after,
            page_size=page_size,
        )

    return await _list_products_browse(
        db,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        in_stock=in_stock,
        sort=sort,
        after=after,
        page_size=page_size,
    )


def _apply_filters(
    query: select,  # type: ignore[type-arg]
    *,
    category_id: uuid.UUID | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    min_rating: int | None = None,
    in_stock: bool | None = None,
) -> select:  # type: ignore[type-arg]
    """Apply shared filter clauses to a product query."""
    if category_id is not None:
        query = query.where(Product.category_id == category_id)
    if min_price is not None:
        query = query.where(Product.base_price >= min_price)
    if max_price is not None:
        query = query.where(Product.base_price <= max_price)
    # min_rating: placeholder — Review model not yet implemented, no-op for now
    if in_stock is True:
        # Subquery: product must have at least one variant with stock > 0
        in_stock_subquery = (
            select(ProductVariant.product_id)
            .where(ProductVariant.stock_quantity > 0)
            .correlate(Product)
            .exists()
        )
        query = query.where(
            Product.id.in_(
                select(ProductVariant.product_id).where(ProductVariant.stock_quantity > 0)
            )
        )
    return query


async def _list_products_search(
    db: AsyncSession,
    *,
    q: str,
    category_id: uuid.UUID | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    min_rating: int | None = None,
    in_stock: bool | None = None,
    after: str | None = None,
    page_size: int = 20,
) -> ProductListResponse:
    """List products matching a full-text search query, ranked by relevance.

    Uses PostgreSQL plainto_tsquery and ts_rank for relevance-ranked results.
    Pagination for search uses offset-based cursors since relevance ranking
    doesn't map well to keyset pagination.
    """
    search_query = func.plainto_tsquery("english", q)
    rank = func.ts_rank(Product.search_vector, search_query).label("search_rank")

    query = (
        select(Product, rank)
        .where(
            Product.is_active.is_(True),
            Product.deleted_at.is_(None),
            Product.search_vector.op("@@")(search_query),
        )
        .order_by(text("search_rank DESC"), Product.id.desc())
    )

    # Apply shared filters
    query = _apply_filters(
        query,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        in_stock=in_stock,
    )

    # Decode offset from cursor for search pagination
    offset = 0
    if after:
        try:
            payload = json.loads(base64.urlsafe_b64decode(after.encode()).decode())
            offset = int(payload.get("offset", 0))
        except (json.JSONDecodeError, KeyError, ValueError, UnicodeDecodeError):
            offset = 0
        query = query.offset(offset)

    query = query.limit(page_size + 1)

    result = await db.execute(query)
    rows = list(result.all())

    has_next_page = len(rows) > page_size
    result_rows = rows[:page_size]

    # Build next cursor for search results using offset
    next_cursor: str | None = None
    if has_next_page:
        next_offset = offset + page_size
        cursor_payload = json.dumps({"s": "search", "id": str(uuid.uuid4()), "offset": next_offset})
        next_cursor = base64.urlsafe_b64encode(cursor_payload.encode()).decode()

    # Extract Product objects from result rows (each row is (Product, rank))
    items = [_build_product_list_item(row[0]) for row in result_rows]

    return ProductListResponse(
        items=items,
        next_cursor=next_cursor,
        has_next_page=has_next_page,
    )


async def _list_products_browse(
    db: AsyncSession,
    *,
    category_id: uuid.UUID | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    min_rating: int | None = None,
    in_stock: bool | None = None,
    sort: SortOption = SortOption.NEWEST,
    after: str | None = None,
    page_size: int = 20,
) -> ProductListResponse:
    """List products for browsing (no search), with filtering and sorting via cursor pagination."""
    query = select(Product).where(
        Product.is_active.is_(True),
        Product.deleted_at.is_(None),
    )

    # Apply shared filters
    query = _apply_filters(
        query,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        in_stock=in_stock,
    )

    # Determine sort column and direction from sort option
    sort_column, sort_direction, sort_column_name = _resolve_sort(sort)

    # Apply cursor-based pagination with chosen sort
    query = apply_cursor_pagination(
        query=query,
        sort_column=sort_column,
        id_column=Product.id,
        page_size=page_size,
        after=after,
        sort_direction=sort_direction,
    )

    result = await db.execute(query)
    products = list(result.scalars().all())

    # Build the cursor page
    cursor_page = build_cursor_page(
        rows=products,
        page_size=page_size,
        sort_column_name=sort_column_name,
    )

    items = [_build_product_list_item(product) for product in cursor_page.items]

    return ProductListResponse(
        items=items,
        next_cursor=cursor_page.next_cursor,
        has_next_page=cursor_page.has_next_page,
    )


def _resolve_sort(sort: SortOption) -> tuple:
    """Resolve a SortOption into (sort_column, sort_direction, sort_column_name)."""
    if sort == SortOption.PRICE_ASC:
        return Product.base_price, "asc", "base_price"
    elif sort == SortOption.PRICE_DESC:
        return Product.base_price, "desc", "base_price"
    elif sort == SortOption.POPULAR:
        # Placeholder: popular sorts by newest until review/order data is available
        return Product.created_at, "desc", "created_at"
    else:
        # Default: newest
        return Product.created_at, "desc", "created_at"


async def get_product_by_slug(
    db: AsyncSession,
    *,
    slug: str,
) -> ProductDetail:
    """Get full product detail by slug.

    Returns full product with images (ordered by position), variants with resolved
    prices, category breadcrumb (with parent), average rating, review count, and
    rating distribution.

    Raises NotFoundError if product not found or soft-deleted.
    """
    query = select(Product).where(
        Product.slug == slug,
        Product.is_active.is_(True),
        Product.deleted_at.is_(None),
    )

    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if product is None:
        raise NotFoundError(
            detail="Product with this slug does not exist",
            code="PRODUCT_NOT_FOUND",
        )

    # Build category with parent breadcrumb
    category = product.category
    parent_ref: CategoryRef | None = None
    if category.parent is not None:
        parent_ref = CategoryRef(
            id=category.parent.id,
            name=category.parent.name,
            slug=category.parent.slug,
        )

    category_with_parent = CategoryWithParent(
        id=category.id,
        name=category.name,
        slug=category.slug,
        parent=parent_ref,
    )

    # Build images ordered by position
    sorted_images = sorted(product.images, key=lambda img: img.position)
    images = [
        ProductImageDetail(
            id=img.id,
            url=img.url,
            alt_text=img.alt_text,
            position=img.position,
        )
        for img in sorted_images
    ]

    # Build variants with resolved price
    variants = [
        ProductVariantDetail(
            id=v.id,
            variant_type=v.variant_type,
            variant_value=v.variant_value,
            sku=v.sku,
            price=v.price_override if v.price_override is not None else product.base_price,
            stock_quantity=v.stock_quantity,
            in_stock=v.stock_quantity > 0,
        )
        for v in product.variants
    ]

    # Rating distribution — placeholder until Review model is implemented
    # Returns empty distribution with 0 counts for each star rating
    rating_distribution: dict[str, int] = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
    }

    return ProductDetail(
        id=product.id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        base_price=product.base_price,
        category=category_with_parent,
        images=images,
        variants=variants,
        average_rating=0.0,
        review_count=0,
        rating_distribution=rating_distribution,
        created_at=product.created_at,
    )
