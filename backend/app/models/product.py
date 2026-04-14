import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    """A purchasable product in the catalog."""

    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    base_price: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        nullable=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    category: Mapped["Category"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Category",
        back_populates="products",
        lazy="selectin",
    )
    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        lazy="selectin",
        order_by="ProductImage.position",
        cascade="all, delete-orphan",
    )
    variants: Mapped[list["ProductVariant"]] = relationship(
        "ProductVariant",
        back_populates="product",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_products_slug", "slug", unique=True),
        Index("ix_products_category_id", "category_id"),
        Index("ix_products_base_price", "base_price"),
        Index("ix_products_created_at", "created_at"),
        Index("ix_products_is_active", "is_active"),
        Index("ix_products_deleted_at", "deleted_at"),
        Index("ix_products_search_vector", "search_vector", postgresql_using="gin"),
    )


class ProductImage(Base):
    """An image associated with a product."""

    __tablename__ = "product_images"

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="images",
    )

    __table_args__ = (
        Index("ix_product_images_product_id", "product_id"),
        Index("ix_product_images_product_position", "product_id", "position"),
    )


class ProductVariant(Base):
    """A specific purchasable configuration of a product (e.g., size/color)."""

    __tablename__ = "product_variants"

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    variant_type: Mapped[str] = mapped_column(String(50), nullable=False)
    variant_value: Mapped[str] = mapped_column(String(100), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    price_override: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="variants",
    )

    __table_args__ = (
        Index("ix_product_variants_product_id", "product_id"),
        Index("ix_product_variants_sku", "sku", unique=True),
        UniqueConstraint(
            "product_id",
            "variant_type",
            "variant_value",
            name="uq_product_variant_type_value",
        ),
    )
