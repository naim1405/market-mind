from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.products.schemas import (
    ProductCreate,
    ProductPublicResponse,
    ProductUpdate,
)

VALID = {
    "sku": "PJ-01",
    "name": "Cotton Panjabi",
    "category": "Panjabi",
    "selling_price": "1500",
    "min_floor_price": "1200",
    "image_urls": ["https://res.cloudinary.com/demo/a.jpg"],
}


def test_create_defaults():
    product = ProductCreate(**VALID)
    assert product.max_discount_pct == 0
    assert product.stock_qty == 0


def test_floor_equal_to_selling_price_is_allowed():
    ProductCreate(**{**VALID, "min_floor_price": "1500"})


@pytest.mark.parametrize(
    "override",
    [
        {"min_floor_price": "1600"},  # floor above selling price
        {"selling_price": "-1"},
        {"stock_qty": -1},
        {"max_discount_pct": "101"},
        {"image_urls": []},
        {"sku": "x" * 101},
    ],
)
def test_create_rejects_invalid(override):
    with pytest.raises(ValidationError):
        ProductCreate(**{**VALID, **override})


def test_create_requires_images():
    data = {k: v for k, v in VALID.items() if k != "image_urls"}
    with pytest.raises(ValidationError):
        ProductCreate(**data)


def test_update_allows_partial_and_rejects_empty_images():
    assert ProductUpdate(stock_qty=3).model_dump(exclude_unset=True) == {"stock_qty": 3}
    with pytest.raises(ValidationError):
        ProductUpdate(image_urls=[])


def test_public_response_hides_margin_fields():
    assert "min_floor_price" not in ProductPublicResponse.model_fields
    assert "max_discount_pct" not in ProductPublicResponse.model_fields
    assert ProductCreate(**VALID).selling_price == Decimal("1500")
