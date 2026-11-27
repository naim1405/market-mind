from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse

from app.core.config import get_settings
from app.modules.facebook.webhook.dependencies import WebhookServiceDep
from app.modules.facebook.webhook.schemas import WebhookPayloadSchema

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
async def webhook_callback(payload: WebhookPayloadSchema, service: WebhookServiceDep):
    if payload.object != "page":
        raise HTTPException(status_code=404, detail="Unsupported object")

    for entry in payload.entry:
        for event in entry.messaging:
            # only handle text messages sent by customers, skip our own echoes
            if event.message and event.message.text and not event.message.is_echo:
                # TODO: push the event to a queue instead of replying inline
                await service.reply_to_page_message(event)

    return {"message": "EVENT_RECEIVED"}
