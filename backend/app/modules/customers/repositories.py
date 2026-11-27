import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customers.models import Customer


class CustomerRepository:
    def __init__(self, session: AsyncSession):
        self.db_session = session

    async def create_customer(self, data: dict) -> Customer:
        customer = Customer(**data)
        self.db_session.add(customer)
        await self.db_session.flush()
        return customer

    async def get_customer_by_psid(self, page_id: uuid.UUID, psid: str) -> Customer | None:
        stmt = select(Customer).where(Customer.page_id == page_id, Customer.psid == psid)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    # phone isn't unique (a messenger and a manual customer can share one), so take the oldest
    async def get_customer_by_phone(self, page_id: uuid.UUID, phone: str) -> Customer | None:
        stmt = (
            select(Customer)
            .where(Customer.page_id == page_id, Customer.phone == phone)
            .order_by(Customer.created_at)
            .limit(1)
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_customer(self, customer: Customer, data: dict) -> Customer:
        for field, value in data.items():
            setattr(customer, field, value)
        await self.db_session.flush()
        # updated_at is set by the db on update; reload it so callers can read it
        await self.db_session.refresh(customer)
        return customer
