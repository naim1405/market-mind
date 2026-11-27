import uuid

import pytest

pytestmark = pytest.mark.anyio

PRODUCT = {
    "sku": "PJ-01",
    "name": "Cotton Panjabi",
    "category": "Panjabi",
    "description": "Eid collection",
    "selling_price": "1500.00",
    "min_floor_price": "1200.00",
    "max_discount_pct": "10.00",
    "stock_qty": 5,
    "image_urls": ["https://res.cloudinary.com/demo/a.jpg"],
}


def url(page_id, product_id=None):
    base = f"/api/v1/pages/{page_id}/products/"
    return f"{base}{product_id}" if product_id else base


async def create(client, page, **override):
    res = await client.post(url(page.id), json={**PRODUCT, **override})
    assert res.status_code == 201, res.text
    return res.json()


async def test_create_product(client, page):
    body = await create(client, page)
    assert body["page_id"] == str(page.id)
    assert body["sku"] == "PJ-01"
    assert body["min_floor_price"] == "1200.00"
    assert body["image_urls"] == PRODUCT["image_urls"]


async def test_create_rejects_invalid_body(client, page):
    res = await client.post(url(page.id), json={**PRODUCT, "min_floor_price": "2000"})
    assert res.status_code == 422


async def test_duplicate_sku_on_same_page_conflicts(client, page):
    await create(client, page)
    res = await client.post(url(page.id), json=PRODUCT)
    assert res.status_code == 409


async def test_get_product(client, page):
    created = await create(client, page)
    res = await client.get(url(page.id, created["id"]))
    assert res.status_code == 200
    assert res.json()["id"] == created["id"]


async def test_get_missing_product_404(client, page):
    res = await client.get(url(page.id, uuid.uuid4()))
    assert res.status_code == 404


async def test_product_not_visible_through_another_page(client, page):
    created = await create(client, page)
    res = await client.get(url(uuid.uuid4(), created["id"]))
    assert res.status_code == 404


async def test_list_filters(client, page):
    await create(client, page, sku="PJ-01", name="Cotton Panjabi", category="Panjabi")
    await create(
        client, page, sku="SK-01", name="Face Serum", category="Skincare", stock_qty=0
    )

    async def names(**params):
        res = await client.get(url(page.id), params=params)
        assert res.status_code == 200
        return {p["name"] for p in res.json()}

    assert await names() == {"Cotton Panjabi", "Face Serum"}
    assert await names(keyword="panjabi") == {"Cotton Panjabi"}
    assert await names(category="Skincare") == {"Face Serum"}
    assert await names(in_stock="true") == {"Cotton Panjabi"}
    assert await names(in_stock="false") == {"Face Serum"}
    assert len(await names(limit=1)) == 1


async def test_update_product(client, page):
    created = await create(client, page)
    res = await client.patch(url(page.id, created["id"]), json={"stock_qty": 9})
    assert res.status_code == 200
    assert res.json()["stock_qty"] == 9
    assert res.json()["name"] == PRODUCT["name"]


async def test_update_floor_above_stored_selling_price_400(client, page):
    created = await create(client, page)
    res = await client.patch(
        url(page.id, created["id"]), json={"min_floor_price": "1600"}
    )
    assert res.status_code == 400


async def test_update_to_existing_sku_conflicts(client, page):
    await create(client, page, sku="PJ-01")
    other = await create(client, page, sku="PJ-02")
    res = await client.patch(url(page.id, other["id"]), json={"sku": "PJ-01"})
    assert res.status_code == 409


async def test_delete_product(client, page):
    created = await create(client, page)
    res = await client.delete(url(page.id, created["id"]))
    assert res.status_code == 204
    res = await client.get(url(page.id, created["id"]))
    assert res.status_code == 404
