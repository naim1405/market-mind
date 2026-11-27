import uuid

from fastapi import APIRouter, Query, status

from app.modules.orders.dependencies import OrderServiceDep
from app.modules.orders.models import OrderStatus
from app.modules.orders.schemas import OrderCreate, OrderResponse, OrderUpdate
from app.modules.pages.dependencies import PageIdDep

router = APIRouter(prefix="/pages/{page_id}/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(page_id: PageIdDep, data: OrderCreate, service: OrderServiceDep):
    return await service.create_order(page_id, data)


@router.get("/", response_model=list[OrderResponse])
async def list_orders(
    page_id: PageIdDep,
    service: OrderServiceDep,
    status: OrderStatus | None = None,
    customer_id: uuid.UUID | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await service.list_orders(
        page_id, status=status, customer_id=customer_id, limit=limit, offset=offset
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(page_id: PageIdDep, order_id: uuid.UUID, service: OrderServiceDep):
    return await service.get_order(page_id, order_id)


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    page_id: PageIdDep,
    order_id: uuid.UUID,
    data: OrderUpdate,
    service: OrderServiceDep,
):
    return await service.update_order(page_id, order_id, data)
