import uuid

from sqlalchemy.exc import IntegrityError

from app.core.exceptions.errors import BadRequestError, ConflictError, NotFoundError
from app.modules.products.models import Product
from app.modules.products.repositories import ProductRepository
from app.modules.products.schemas import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    async def create_product(self, page_id: uuid.UUID, data: ProductCreate) -> Product:
        try:
            return await self.product_repo.create_product(
                {**data.model_dump(), "page_id": page_id}
            )
        except IntegrityError:
            raise ConflictError("Product with this SKU")

    async def get_product(self, page_id: uuid.UUID, product_id: uuid.UUID) -> Product:
        product = await self.product_repo.get_product_by_id(product_id)
        if not product or product.page_id != page_id:
            raise NotFoundError("Product")
        return product

    async def list_products(self, page_id: uuid.UUID, **filters) -> list[Product]:
        return await self.product_repo.list_products(page_id, **filters)

    async def update_product(
        self, page_id: uuid.UUID, product_id: uuid.UUID, data: ProductUpdate
    ) -> Product:
        product = await self.get_product(page_id, product_id)
        changes = data.model_dump(exclude_unset=True)

        # ProductUpdate can't see stored values, so check the floor against the merged result
        selling_price = changes.get("selling_price", product.selling_price)
        min_floor_price = changes.get("min_floor_price", product.min_floor_price)
        if min_floor_price > selling_price:
            raise BadRequestError("min_floor_price cannot exceed selling_price")

        try:
            return await self.product_repo.update_product(product, changes)
        except IntegrityError:
            raise ConflictError("Product with this SKU")

    async def delete_product(self, page_id: uuid.UUID, product_id: uuid.UUID) -> None:
        product = await self.get_product(page_id, product_id)
        await self.product_repo.delete_product(product)
