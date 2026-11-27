import uuid
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStampMixin

if TYPE_CHECKING:
    from app.modules.customers.models import Customer
    from app.modules.pages.models import Pages
    from app.modules.products.models import Product


class OrderStatus(StrEnum):
    CONFIRMED = "confirmed"  # order placed, stock deducted, not yet with courier
    BOOKED = "booked"  # parcel booked with courier, has tracking id
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    RETURNED = "returned"
    CANCELLED = "cancelled"


class DeliveryZone(StrEnum):
    INSIDE_DHAKA = "inside_dhaka"
    SUB_DHAKA = "sub_dhaka"
    OUTSIDE_DHAKA = "outside_dhaka"


def _str_enum(enum: type[StrEnum]) -> Enum:
    # varchar + check constraint instead of a native pg enum, so adding values needs no ALTER TYPE
    return Enum(
        enum,
        native_enum=False,
        length=30,
        values_callable=lambda e: [m.value for m in e],
    )


class Order(Base, TimeStampMixin):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    page_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pages.id", ondelete="CASCADE"), index=True, nullable=False
    )
    page: Mapped["Pages"] = relationship(back_populates="orders")
    status: Mapped[OrderStatus] = mapped_column(
        _str_enum(OrderStatus), index=True, nullable=False, default=OrderStatus.CONFIRMED
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id"), index=True, nullable=False
    )
    customer: Mapped["Customer"] = relationship(back_populates="orders")
    # delivery details for this order; may differ from the customer's saved ones
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    customer_address: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)

    delivery_zone: Mapped[DeliveryZone] = mapped_column(
        _str_enum(DeliveryZone), nullable=False
    )
    delivery_charge: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    # items subtotal + delivery charge, stored so later price changes don't alter it
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # parcel: filled in when booked with the courier
    courier_name: Mapped[str | None] = mapped_column(String(100))
    tracking_id: Mapped[str | None] = mapped_column(String(100), unique=True)

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", lazy="selectin"
    )


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True, nullable=False
    )
    order: Mapped["Order"] = relationship(back_populates="items")
    # SET NULL so deleting a product keeps order history; name is kept below
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), index=True
    )
    product: Mapped["Product | None"] = relationship()
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    # agreed price per unit, may be below selling price after bargaining
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
