import uuid

from pydantic import BaseModel


class CategoryTree(BaseModel):
    """A category with nested children and product count."""

    id: uuid.UUID
    name: str
    slug: str
    product_count: int
    children: list["CategoryTree"]

    model_config = {"from_attributes": True}


class CategoryListResponse(BaseModel):
    """Response for the category tree endpoint."""

    items: list[CategoryTree]
