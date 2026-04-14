from pydantic import BaseModel, Field


class CursorParams(BaseModel):
    """Query parameters for cursor-based pagination."""

    after: str | None = Field(None, description="Cursor token for pagination")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page")


class PaginatedResponse[T](BaseModel):
    """Generic paginated response with cursor-based pagination."""

    items: list[T]
    next_cursor: str | None = None
    has_next_page: bool = False


class ErrorResponse(BaseModel):
    """Consistent error response format."""

    detail: str
    code: str
