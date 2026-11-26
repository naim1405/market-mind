from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse

from app.core.config import get_settings

router = APIRouter(prefix="/facebook/webhook", tags=["webhook"])


# webhook verification endpoint
@router.get("/")
async def verify_callback(req: Request):
    setting = get_settings()
    params = req.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == setting.META_WEBHOOK_TOKEN:
        return PlainTextResponse(challenge, status_code=200)

    raise HTTPException(status_code=403, detail="Verification failed")


# webhook callback endpoint
@router.post("/")
async def webhook_callback(req: Request):
    payload = await req.json()
    print("🚀 payload : ", payload)
    return {"message": "Callback received", "payload": payload}
