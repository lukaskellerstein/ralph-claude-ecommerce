import base64
import json
import uuid
from enum import StrEnum

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.core.pagination import apply_cursor_pagination, build_cursor_page, decode_cursor
from app.models.product import Product, ProductImage, ProductVariant
from app.models.review import Review
from app.services.review_service import get_product_rating_stats
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


def _build_product_list_item(
    product: Product,
    average_rating: float = 0.0,
    review_count: int = 0,
) -> ProductListItem:
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

    return ProductListItem(
        id=product.id,
        name=product.name,
        slug=product.slug,
        description=product.description[:200] if len(product.description) > 200 else product.description,
        base_price=product.base_price,
        category=category_ref,
        primary_image=primary_image,
        average_rating=average_rating,
        review_count=review_count,
        has_stock=has_stock,
    )


async def _get_product_ratings_batch(
    db: AsyncSession,
    product_ids: list[uuid.UUID],
) -> dict[uuid.UUID, tuple[float, int]]:
    """Fetch average rating and review count for a batch of products.

    Returns a dict mapping product_id to (average_rating, review_count).
    """
    if not product_ids:
        return {}

    query = (
        select(
            Review.product_id,
            func.count(Review.id).label("review_count"),
            func.coalesce(func.avg(Review.rating), 0).label("average_rating"),
        )
        .where(Review.product_id.in_(product_ids))
        .group_by(Review.product_id)
    )

    result = await db.execute(query)
    rows = result.all()

    ratings: dict[uuid.UUID, tuple[float, int]] = {}
    for row in rows:
        ratings[row.product_id] = (float(row.average_rating), int(row.review_count))

    return ratings


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
    # min_rating: filter products whose average rating >= min_rating
    if min_rating is not None:
        avg_rating_subquery = (
            select(Review.product_id)
            .group_by(Review.product_id)
            .having(func.avg(Review.rating) >= min_rating)
        )
        query = query.where(Product.id.in_(avg_rating_subquery))
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
    products_list = [row[0] for row in result_rows]

    # Fetch ratings for all products in the page
    product_ids = [p.id for p in products_list]
    ratings_map = await _get_product_ratings_batch(db, product_ids)

    items = [
        _build_product_list_item(
            p,
            average_rating=ratings_map.get(p.id, (0.0, 0))[0],
            review_count=ratings_map.get(p.id, (0.0, 0))[1],
        )
        for p in products_list
    ]

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

    # Fetch ratings for all products in the page
    product_ids = [p.id for p in cursor_page.items]
    ratings_map = await _get_product_ratings_batch(db, product_ids)

    items = [
        _build_product_list_item(
            product,
            average_rating=ratings_map.get(product.id, (0.0, 0))[0],
            review_count=ratings_map.get(product.id, (0.0, 0))[1],
        )
        for product in cursor_page.items
    ]

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

    # Fetch real rating statistics from reviews
    average_rating, review_count, rating_distribution = await get_product_rating_stats(
        db, product_id=product.id
    )

    return ProductDetail(
        id=product.id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        base_price=product.base_price,
        category=category_with_parent,
        images=images,
        variants=variants,
        average_rating=round(average_rating, 1),
        review_count=review_count,
        rating_distribution=rating_distribution,
        created_at=product.created_at,
    )
