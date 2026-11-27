import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.orders.models import DeliveryZone, OrderStatus

# BD mobile: 01XXXXXXXXX with optional +88 / 88 prefix
BD_PHONE = r"^(\+?88)?01[3-9]\d{8}$"


class OrderItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(ge=1)
    # agreed price after bargaining; None means the product's selling price
    unit_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)


class OrderCreate(BaseModel):
    # set by the AI flow to find the messenger customer; manual orders leave it empty
    customer_psid: str | None = Field(default=None, max_length=100)
    customer_name: str = Field(min_length=1, max_length=200)
    customer_phone: str = Field(pattern=BD_PHONE)
    customer_address: str = Field(min_length=1)
    delivery_zone: DeliveryZone
    note: str | None = None
    items: list[OrderItemCreate] = Field(min_length=1)


# items are not editable: changing them would need stock re-adjustment
class OrderUpdate(BaseModel):
    status: OrderStatus | None = None
    customer_name: str | None = Field(default=None, min_length=1, max_length=200)
    customer_phone: str | None = Field(default=None, pattern=BD_PHONE)
    customer_address: str | None = Field(default=None, min_length=1)
    note: str | None = None
    courier_name: str | None = Field(default=None, max_length=100)
    tracking_id: str | None = Field(default=None, max_length=100)


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID | None
    product_name: str
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: uuid.UUID
    page_id: uuid.UUID
    status: OrderStatus
    customer_id: uuid.UUID
    customer_name: str
    customer_phone: str
    customer_address: str
    note: str | None
    delivery_zone: DeliveryZone
    delivery_charge: Decimal
    total_amount: Decimal
    courier_name: str | None
    tracking_id: str | None
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
