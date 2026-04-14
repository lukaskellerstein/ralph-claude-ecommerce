import uuid

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Category(Base):
    """Hierarchical product category (max 2 levels: root → child)."""

    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side="Category.id",
        back_populates="children",
        lazy="selectin",
    )
    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent",
        lazy="selectin",
        order_by="Category.position",
    )
    products: Mapped[list["Product"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Product",
        back_populates="category",
        lazy="noload",
    )

    __table_args__ = (
        Index("ix_categories_parent_id", "parent_id"),
        Index("ix_categories_slug", "slug", unique=True),
    )
