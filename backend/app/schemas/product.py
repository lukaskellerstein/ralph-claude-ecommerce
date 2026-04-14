import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import CursorParams


class CategoryRef(BaseModel):
    """Lightweight category reference for product listings."""

    id: uuid.UUID
    name: str
    slug: str

    model_config = {"from_attributes": True}


class CategoryWithParent(CategoryRef):
    """Category reference with optional parent breadcrumb."""

    parent: CategoryRef | None = None


class ProductImageRef(BaseModel):
    """Product image reference for listings."""

    url: str
    alt_text: str

    model_config = {"from_attributes": True}


class ProductImageDetail(BaseModel):
    """Full product image for detail page."""

    id: uuid.UUID
    url: str
    alt_text: str
    position: int

    model_config = {"from_attributes": True}


class ProductVariantDetail(BaseModel):
    """Product variant with resolved price for detail page."""

    id: uuid.UUID
    variant_type: str
    variant_value: str
    sku: str
    price: int = Field(description="Resolved price in cents (price_override or base_price)")
    stock_quantity: int
    in_stock: bool

    model_config = {"from_attributes": True}


class ProductListItem(BaseModel):
    """A product item in catalog listings."""

    id: uuid.UUID
    name: str
    slug: str
    description: str = Field(description="Truncated to 200 chars")
    base_price: int = Field(description="Price in cents")
    category: CategoryRef
    primary_image: ProductImageRef | None = None
    average_rating: float
    review_count: int
    has_stock: bool

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Paginated product list response."""

    items: list[ProductListItem]
    next_cursor: str | None = None
    has_next_page: bool = False


class ProductDetail(BaseModel):
    """Full product detail response."""

    id: uuid.UUID
    name: str
    slug: str
    description: str = Field(description="Full markdown/rich text description")
    base_price: int = Field(description="Base price in cents")
    category: CategoryWithParent
    images: list[ProductImageDetail] = Field(description="Images ordered by position")
    variants: list[ProductVariantDetail]
    average_rating: float
    review_count: int
    rating_distribution: dict[str, int] = Field(
        description="Star rating distribution (keys '1'-'5', values are counts)"
    )
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductListParams(CursorParams):
    """Query parameters for product listing with category filter."""

    category_id: uuid.UUID | None = Field(None, description="Filter by category")
