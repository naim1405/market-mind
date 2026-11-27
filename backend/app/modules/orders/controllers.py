from fastapi import APIRouter

router = APIRouter(prefix="/pages/{page_id}/orders", tags=["orders"])
