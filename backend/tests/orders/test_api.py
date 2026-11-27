import uuid

import pytest

pytestmark = pytest.mark.anyio


def url(page_id, order_id=None):
    base = f"/api/v1/pages/{page_id}/orders/"
    return f"{base}{order_id}" if order_id else base


def order_body(product, **override):
    return {
        "customer_psid": "psid-9",
        "customer_name": "Karim",
        "customer_phone": "+8801712345678",
        "customer_address": "Agrabad, Chattogram",
        "delivery_zone": "outside_dhaka",
        "items": [{"product_id": str(product.id), "quantity": 2, "unit_price": "1300"}],
        **override,
    }


async def create(client, page, product, **override):
    res = await client.post(url(page.id), json=order_body(product, **override))
    assert res.status_code == 201, res.text
    return res.json()


async def test_create_order_prices_deducts_stock_and_creates_customer(
    client, db_session, page, product
):
    body = await create(client, page, product)

    assert body["status"] == "confirmed"
    assert body["customer_phone"] == "01712345678"  # normalized
    assert body["delivery_charge"] == "120.00"
    assert body["total_amount"] == "2720.00"  # 2 x 1300 + 120
    assert body["items"][0]["product_name"] == "Cotton Panjabi"

    await db_session.refresh(product)
    assert product.stock_qty == 3

    from app.modules.customers.repositories import CustomerRepository

    customer = await CustomerRepository(db_session).get_customer_by_psid(page.id, "psid-9")
    assert str(customer.id) == body["customer_id"]
    assert customer.phone == "01712345678"


async def test_missing_unit_price_uses_selling_price(client, page, product):
    body = await create(
        client, page, product, items=[{"product_id": str(product.id), "quantity": 1}]
    )
    assert body["items"][0]["unit_price"] == "1500.00"


async def test_repeat_customer_is_reused_and_details_updated(client, page, product):
    first = await create(client, page, product)
    second = await create(client, page, product, customer_address="New address")
    assert first["customer_id"] == second["customer_id"]


async def test_manual_order_matches_customer_by_phone(client, page, product):
    first = await create(client, page, product, customer_psid=None)
    second = await create(
        client, page, product, customer_psid=None, customer_phone="01712345678"
    )
    assert first["customer_id"] == second["customer_id"]


async def test_price_below_floor_rejected_without_revealing_it(client, page, product):
    items = [{"product_id": str(product.id), "quantity": 1, "unit_price": "1100"}]
    res = await client.post(url(page.id), json=order_body(product, items=items))
    assert res.status_code == 400
    assert "1200" not in res.text


async def test_not_enough_stock_rejected_and_nothing_deducted(
    client, db_session, page, product
):
    items = [{"product_id": str(product.id), "quantity": 6}]
    res = await client.post(url(page.id), json=order_body(product, items=items))
    assert res.status_code == 400
    await db_session.refresh(product)
    assert product.stock_qty == 5


async def test_unknown_or_duplicate_product_rejected(client, page, product):
    unknown = [{"product_id": str(uuid.uuid4()), "quantity": 1}]
    res = await client.post(url(page.id), json=order_body(product, items=unknown))
    assert res.status_code == 404

    dup = [{"product_id": str(product.id), "quantity": 1}] * 2
    res = await client.post(url(page.id), json=order_body(product, items=dup))
    assert res.status_code == 400


async def test_get_and_list_orders(client, page, product):
    created = await create(client, page, product)

    res = await client.get(url(page.id, created["id"]))
    assert res.status_code == 200 and res.json()["id"] == created["id"]

    assert len((await client.get(url(page.id))).json()) == 1
    assert (await client.get(url(page.id), params={"status": "delivered"})).json() == []
    assert (await client.get(url(uuid.uuid4(), created["id"]))).status_code == 404


async def test_status_flow_to_delivered(client, page, product):
    order = await create(client, page, product)
    oid = order["id"]

    res = await client.patch(url(page.id, oid), json={"status": "booked"})
    assert res.status_code == 400  # tracking id required

    res = await client.patch(
        url(page.id, oid),
        json={"status": "booked", "tracking_id": "TRK-1", "courier_name": "Pathao"},
    )
    assert res.status_code == 200 and res.json()["tracking_id"] == "TRK-1"

    for step in ["in_transit", "delivered"]:
        res = await client.patch(url(page.id, oid), json={"status": step})
        assert res.status_code == 200 and res.json()["status"] == step

    res = await client.patch(url(page.id, oid), json={"status": "cancelled"})
    assert res.status_code == 400  # delivered is final


async def test_invalid_transition_rejected(client, page, product):
    order = await create(client, page, product)
    res = await client.patch(url(page.id, order["id"]), json={"status": "delivered"})
    assert res.status_code == 400


async def test_cancel_restores_stock(client, db_session, page, product):
    order = await create(client, page, product)
    res = await client.patch(url(page.id, order["id"]), json={"status": "cancelled"})
    assert res.status_code == 200
    await db_session.refresh(product)
    assert product.stock_qty == 5


async def test_duplicate_tracking_id_conflicts(client, page, product):
    a = await create(client, page, product, items=[{"product_id": str(product.id), "quantity": 1}])
    b = await create(client, page, product, items=[{"product_id": str(product.id), "quantity": 1}])
    await client.patch(url(page.id, a["id"]), json={"status": "booked", "tracking_id": "T-1"})
    res = await client.patch(
        url(page.id, b["id"]), json={"status": "booked", "tracking_id": "T-1"}
    )
    assert res.status_code == 409
