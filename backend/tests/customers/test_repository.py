import uuid
from datetime import UTC, datetime

import pytest

from app.modules.customers.repositories import CustomerRepository

pytestmark = pytest.mark.anyio


async def test_get_by_psid_is_scoped_to_page(db_session, page):
    repo = CustomerRepository(db_session)
    created = await repo.create_customer({"page_id": page.id, "psid": "psid-1"})

    assert (await repo.get_customer_by_psid(page.id, "psid-1")).id == created.id
    assert await repo.get_customer_by_psid(page.id, "psid-2") is None
    assert await repo.get_customer_by_psid(uuid.uuid4(), "psid-1") is None


async def test_get_by_phone_returns_oldest(db_session, page):
    repo = CustomerRepository(db_session)
    # now() is fixed per transaction, so give the first row an explicitly older timestamp
    first = await repo.create_customer(
        {"page_id": page.id, "phone": "01712345678", "created_at": datetime(2020, 1, 1, tzinfo=UTC)}
    )
    await repo.create_customer(
        {"page_id": page.id, "phone": "01712345678", "psid": "psid-1"}
    )

    assert (await repo.get_customer_by_phone(page.id, "01712345678")).id == first.id


async def test_update_customer(db_session, page):
    repo = CustomerRepository(db_session)
    customer = await repo.create_customer({"page_id": page.id, "psid": "psid-1"})

    updated = await repo.update_customer(customer, {"name": "Rahim", "phone": "01712345678"})

    assert updated.name == "Rahim"
    assert updated.updated_at is not None
