import uuid
from decimal import Decimal

import pytest

from app.modules.orders.models import DeliveryZone, OrderStatus
from app.modules.orders.repositories import OrderRepository
from app.modules.products.repositories import ProductRepository

pytestmark = pytest.mark.anyio


def order_data(page, customer, **override):
    return {
        "page_id": page.id,
        "customer_id": customer.id,
        "customer_name": "Rahim",
        "customer_phone": "01712345678",
        "customer_address": "Mirpur 10, Dhaka",
        "delivery_zone": DeliveryZone.INSIDE_DHAKA,
        "delivery_charge": Decimal("60"),
        "total_amount": Decimal("2860"),
        **override,
    }


def item_data(product, **override):
    return {
        "product_id": product.id,
        "product_name": product.name,
        "quantity": 2,
        "unit_price": Decimal("1400"),
        **override,
    }


async def test_create_order_with_items(db_session, page, customer, product):
    repo = OrderRepository(db_session)
    order = await repo.create_order(order_data(page, customer), [item_data(product)])

    fetched = await repo.get_order_by_id(order.id)
    assert fetched.status == OrderStatus.CONFIRMED
    assert len(fetched.items) == 1
    assert fetched.items[0].unit_price == Decimal("1400")
    assert fetched.created_at is not None


async def test_get_by_tracking_id_is_scoped_to_page(db_session, page, customer, product):
    repo = OrderRepository(db_session)
    await repo.create_order(
        order_data(page, customer, tracking_id="TRK-1"), [item_data(product)]
    )

    assert (await repo.get_order_by_tracking_id(page.id, "TRK-1")) is not None
    assert await repo.get_order_by_tracking_id(uuid.uuid4(), "TRK-1") is None


async def test_list_orders_filters(db_session, page, customer, product):
    repo = OrderRepository(db_session)
    confirmed = await repo.create_order(order_data(page, customer), [item_data(product)])
    await repo.create_order(
        order_data(page, customer, status=OrderStatus.DELIVERED), [item_data(product)]
    )

    assert len(await repo.list_orders(page.id)) == 2
    by_status = await repo.list_orders(page.id, status=OrderStatus.CONFIRMED)
    assert [o.id for o in by_status] == [confirmed.id]
    assert await repo.list_orders(page.id, customer_id=uuid.uuid4()) == []
    assert await repo.list_orders(uuid.uuid4()) == []


async def test_update_order_keeps_items_loaded(db_session, page, customer, product):
    repo = OrderRepository(db_session)
    order = await repo.create_order(order_data(page, customer), [item_data(product)])

    updated = await repo.update_order(
        order, {"status": OrderStatus.BOOKED, "tracking_id": "TRK-9"}
    )

    assert updated.status == OrderStatus.BOOKED
    assert updated.updated_at is not None
    assert len(updated.items) == 1


async def test_deduct_stock_refuses_oversell(db_session, product):
    repo = ProductRepository(db_session)

    assert await repo.deduct_stock(product.id, 3) is True
    assert product.stock_qty == 2  # already-loaded product sees the new value
    assert await repo.deduct_stock(product.id, 3) is False
    assert product.stock_qty == 2


async def test_restore_stock(db_session, product):
    repo = ProductRepository(db_session)
    await repo.restore_stock(product.id, 4)
    assert product.stock_qty == 9


async def test_get_products_by_ids_is_scoped_to_page(db_session, page, product):
    repo = ProductRepository(db_session)
    assert [p.id for p in await repo.get_products_by_ids(page.id, [product.id])] == [product.id]
    assert await repo.get_products_by_ids(uuid.uuid4(), [product.id]) == []
