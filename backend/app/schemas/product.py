import uuid

from pydantic import BaseModel, Field

from app.schemas.common import CursorParams


class CategoryRef(BaseModel):
    """Lightweight category reference for product listings."""

    id: uuid.UUID
    name: str
    slug: str

    model_config = {"from_attributes": True}


class ProductImageRef(BaseModel):
    """Product image reference for listings."""

    url: str
    alt_text: str

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


class ProductListParams(CursorParams):
    """Query parameters for product listing with category filter."""

    category_id: uuid.UUID | None = Field(None, description="Filter by category")
