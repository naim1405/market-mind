from typing import Annotated

from fastapi import Depends

from app.db.session import SessionDep
from app.modules.orders.repositories import OrderRepository
from app.modules.orders.services import OrderService
from app.modules.products.dependencies import ProductRepositoryDep


def get_order_repository(session: SessionDep) -> OrderRepository:
    return OrderRepository(session=session)


OrderRepositoryDep = Annotated[OrderRepository, Depends(get_order_repository)]


def get_order_service(
    order_repo: OrderRepositoryDep,
    product_repo: ProductRepositoryDep,
) -> OrderService:
    return OrderService(order_repo=order_repo, product_repo=product_repo)


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
