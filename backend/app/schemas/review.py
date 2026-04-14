import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import CursorParams


class ReviewItem(BaseModel):
    """A single review in a review list."""

    id: uuid.UUID
    rating: int = Field(ge=1, le=5, description="Star rating (1-5)")
    text: str
    reviewer_name: str = Field(description="Display name of the reviewer")
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewListResponse(BaseModel):
    """Paginated list of reviews for a product."""

    items: list[ReviewItem]
    next_cursor: str | None = None
    has_next_page: bool = False


class ReviewListParams(CursorParams):
    """Query parameters for review listing."""

    page_size: int = Field(10, ge=1, le=50, description="Number of reviews per page")
