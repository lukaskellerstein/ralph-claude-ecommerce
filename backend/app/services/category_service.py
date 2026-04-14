import uuid

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.product import Product
from app.schemas.category import CategoryTree


async def get_category_tree(db: AsyncSession) -> list[CategoryTree]:
    """Get the full category tree with product counts.

    Uses a recursive CTE to build the hierarchy, computing product_count
    for active, non-deleted products in each category.
    """
    # Step 1: Compute product counts per category for active, non-deleted products
    product_count_subquery = (
        select(
            Product.category_id,
            func.count(Product.id).label("product_count"),
        )
        .where(Product.is_active.is_(True))
        .where(Product.deleted_at.is_(None))
        .group_by(Product.category_id)
    ).subquery("product_counts")

    # Step 2: Fetch all categories with their product counts
    stmt = (
        select(
            Category.id,
            Category.name,
            Category.slug,
            Category.parent_id,
            Category.position,
            func.coalesce(product_count_subquery.c.product_count, 0).label(
                "product_count"
            ),
        )
        .outerjoin(
            product_count_subquery,
            Category.id == product_count_subquery.c.category_id,
        )
        .order_by(Category.position, Category.name)
    )

    result = await db.execute(stmt)
    rows = result.all()

    # Step 3: Build the tree in memory
    # Index categories by their ID
    categories_by_id: dict[uuid.UUID, dict] = {}
    for row in rows:
        categories_by_id[row.id] = {
            "id": row.id,
            "name": row.name,
            "slug": row.slug,
            "parent_id": row.parent_id,
            "product_count": row.product_count,
            "children": [],
        }

    # Build parent-child relationships
    root_categories: list[dict] = []
    for cat in categories_by_id.values():
        if cat["parent_id"] is None:
            root_categories.append(cat)
        else:
            parent = categories_by_id.get(cat["parent_id"])
            if parent:
                parent["children"].append(cat)

    # Step 4: Convert to Pydantic models
    def to_category_tree(cat: dict) -> CategoryTree:
        return CategoryTree(
            id=cat["id"],
            name=cat["name"],
            slug=cat["slug"],
            product_count=cat["product_count"],
            children=[to_category_tree(child) for child in cat["children"]],
        )

    return [to_category_tree(cat) for cat in root_categories]
