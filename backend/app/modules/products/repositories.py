import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.models import Product


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.db_session = session

    async def create_product(self, data: dict) -> Product:
        product = Product(**data)
        self.db_session.add(product)
        await self.db_session.flush()
        return product

    async def get_product_by_id(self, product_id: uuid.UUID) -> Product | None:
        return await self.db_session.get(Product, product_id)

    async def list_products(
        self,
        page_id: uuid.UUID,
        keyword: str | None = None,
        category: str | None = None,
        in_stock: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Product]:
        stmt = select(Product).where(Product.page_id == page_id)
        if keyword:
            stmt = stmt.where(Product.name.ilike(f"%{keyword}%"))
        if category:
            stmt = stmt.where(Product.category == category)
        if in_stock is not None:
            stmt = stmt.where(
                Product.stock_qty > 0 if in_stock else Product.stock_qty == 0
            )

        stmt = stmt.order_by(Product.created_at.desc()).limit(limit).offset(offset)
        result = await self.db_session.execute(stmt)
        return list(result.scalars().all())

    async def update_product(self, product: Product, data: dict) -> Product:
        for field, value in data.items():
            setattr(product, field, value)
        await self.db_session.flush()
        await self.db_session.refresh(product)
        return product

    async def delete_product(self, product: Product) -> None:
        await self.db_session.delete(product)
        await self.db_session.flush()

    async def get_products_by_ids(
        self, page_id: uuid.UUID, product_ids: list[uuid.UUID]
    ) -> list[Product]:
        stmt = select(Product).where(
            Product.page_id == page_id, Product.id.in_(product_ids)
        )
        result = await self.db_session.execute(stmt)
        return list(result.scalars().all())

    # atomic: two orders racing for the last unit can't both succeed
    async def deduct_stock(self, product_id: uuid.UUID, quantity: int) -> bool:
        stmt = (
            update(Product)
            .where(Product.id == product_id, Product.stock_qty >= quantity)
            .values(stock_qty=Product.stock_qty - quantity)
            .returning(Product.id)
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def restore_stock(self, product_id: uuid.UUID, quantity: int) -> None:
        stmt = (
            update(Product)
            .where(Product.id == product_id)
            .values(stock_qty=Product.stock_qty + quantity)
        )
        await self.db_session.execute(stmt)
