import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStampMixin

if TYPE_CHECKING:
    from app.modules.pages.models import Pages


class Product(Base, TimeStampMixin):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("page_id", "sku"),
        # last line of defence against overselling when orders deduct stock concurrently
        CheckConstraint("stock_qty >= 0", name="ck_products_stock_qty_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    page_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pages.id", ondelete="CASCADE"), index=True, nullable=False
    )
    page: Mapped["Pages"] = relationship(back_populates="products")
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    # hidden from customers: bargaining guardrails
    min_floor_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    max_discount_pct: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, server_default="0"
    )
    stock_qty: Mapped[int] = mapped_column(nullable=False, server_default="0")
    # cloudinary urls, first one is the main image
    image_urls: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default="{}"
    )
