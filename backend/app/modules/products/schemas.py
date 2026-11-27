import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Price = Field(ge=0, max_digits=12, decimal_places=2)


class ProductBase(BaseModel):
    sku: str = Field(max_length=100)
    name: str = Field(max_length=200)
    category: str = Field(max_length=120)
    description: str | None = None
    selling_price: Decimal = Price
    stock_qty: int = Field(default=0, ge=0)
    image_urls: list[str] = Field(min_length=1)


class ProductCreate(ProductBase):
    page_id: uuid.UUID
    min_floor_price: Decimal = Price
    max_discount_pct: Decimal = Field(default=Decimal(0), ge=0, le=100)

    @model_validator(mode="after")
    def floor_not_above_selling_price(self):
        if self.min_floor_price > self.selling_price:
            raise ValueError("min_floor_price cannot exceed selling_price")
        return self


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, max_length=100)
    name: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=120)
    description: str | None = None
    selling_price: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    min_floor_price: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    max_discount_pct: Decimal | None = Field(default=None, ge=0, le=100)
    stock_qty: int | None = Field(default=None, ge=0)
    image_urls: list[str] | None = Field(default=None, min_length=1)


# returned to customers: never includes the margin guardrails
class ProductPublicResponse(ProductBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


# returned to admins only
class ProductAdminResponse(ProductPublicResponse):
    page_id: uuid.UUID
    min_floor_price: Decimal
    max_discount_pct: Decimal
    created_at: datetime
    updated_at: datetime
