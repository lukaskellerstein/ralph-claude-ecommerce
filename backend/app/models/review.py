import uuid

from sqlalchemy import ForeignKey, Index, SmallInteger, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Review(Base):
    """A product review submitted by a user."""

    __tablename__ = "reviews"

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False,
    )
    rating: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Relationships
    product: Mapped["Product"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Product",
        back_populates="reviews",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_reviews_product_id", "product_id"),
        Index("ix_reviews_user_id", "user_id"),
        Index("ix_reviews_created_at", "created_at"),
        UniqueConstraint(
            "user_id",
            "product_id",
            name="uq_review_user_product",
        ),
    )
