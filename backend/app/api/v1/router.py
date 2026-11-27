from app.modules.facebook.webhook.controllers import router as webhook_router
from fastapi.routing import APIRouter

from app.modules.auth.controllers import router as auth_router
from app.modules.orders.controllers import router as orders_router
from app.modules.products.controllers import router as products_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(webhook_router)
api_router.include_router(products_router)
api_router.include_router(orders_router)
