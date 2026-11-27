from typing import Annotated

from fastapi import Depends

from app.db.session import SessionDep
from app.modules.products.repositories import ProductRepository
from app.modules.products.services import ProductService


def get_product_repository(session: SessionDep) -> ProductRepository:
    return ProductRepository(session=session)


ProductRepositoryDep = Annotated[ProductRepository, Depends(get_product_repository)]


def get_product_service(product_repo: ProductRepositoryDep) -> ProductService:
    return ProductService(product_repo=product_repo)


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
