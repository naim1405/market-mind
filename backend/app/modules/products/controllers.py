import uuid

from fastapi import APIRouter, Query, status

from app.modules.pages.dependencies import PageIdDep
from app.modules.products.dependencies import ProductServiceDep
from app.modules.products.schemas import (
    ProductAdminResponse,
    ProductCreate,
    ProductUpdate,
)

router = APIRouter(prefix="/pages/{page_id}/products", tags=["products"])


@router.post(
    "/", response_model=ProductAdminResponse, status_code=status.HTTP_201_CREATED
)
async def create_product(
    page_id: PageIdDep, data: ProductCreate, service: ProductServiceDep
):
    return await service.create_product(page_id, data)


@router.get("/", response_model=list[ProductAdminResponse])
async def list_products(
    page_id: PageIdDep,
    service: ProductServiceDep,
    keyword: str | None = None,
    category: str | None = None,
    in_stock: bool | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await service.list_products(
        page_id,
        keyword=keyword,
        category=category,
        in_stock=in_stock,
        limit=limit,
        offset=offset,
    )


@router.get("/{product_id}", response_model=ProductAdminResponse)
async def get_product(
    page_id: PageIdDep, product_id: uuid.UUID, service: ProductServiceDep
):
    return await service.get_product(page_id, product_id)


@router.patch("/{product_id}", response_model=ProductAdminResponse)
async def update_product(
    page_id: PageIdDep,
    product_id: uuid.UUID,
    data: ProductUpdate,
    service: ProductServiceDep,
):
    return await service.update_product(page_id, product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    page_id: PageIdDep, product_id: uuid.UUID, service: ProductServiceDep
):
    await service.delete_product(page_id, product_id)
