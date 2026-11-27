import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.orders.models import Order, OrderItem, OrderStatus


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.db_session = session

    async def create_order(self, data: dict, items: list[dict]) -> Order:
        order = Order(**data, items=[OrderItem(**item) for item in items])
        self.db_session.add(order)
        await self.db_session.flush()
        return order

    async def get_order_by_id(self, order_id: uuid.UUID) -> Order | None:
        return await self.db_session.get(Order, order_id)

    async def get_order_by_tracking_id(
        self, page_id: uuid.UUID, tracking_id: str
    ) -> Order | None:
        stmt = select(Order).where(
            Order.page_id == page_id, Order.tracking_id == tracking_id
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_orders(
        self,
        page_id: uuid.UUID,
        status: OrderStatus | None = None,
        customer_id: uuid.UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Order]:
        stmt = select(Order).where(Order.page_id == page_id)
        if status:
            stmt = stmt.where(Order.status == status)
        if customer_id:
            stmt = stmt.where(Order.customer_id == customer_id)

        stmt = stmt.order_by(Order.created_at.desc()).limit(limit).offset(offset)
        result = await self.db_session.execute(stmt)
        return list(result.scalars().all())

    async def update_order(self, order: Order, data: dict) -> Order:
        for field, value in data.items():
            setattr(order, field, value)
        await self.db_session.flush()
        # updated_at is set by the db on update; reload it so the response can read it
        await self.db_session.refresh(order)
        return order
