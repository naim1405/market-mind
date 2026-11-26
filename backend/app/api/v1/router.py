from app.modules.facebook.webhook.controllers import router as webhook_router
from fastapi.routing import APIRouter

from app.modules.auth.controllers import router as auth_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(webhook_router)
