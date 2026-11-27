import uuid

from sqlalchemy import select
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
