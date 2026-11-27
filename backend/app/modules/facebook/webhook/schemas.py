from pydantic import BaseModel


class WebhookUserSchema(BaseModel):
    id: str


class WebhookMessageSchema(BaseModel):
    mid: str
    text: str | None = None
    is_echo: bool = False


class WebhookMessagingEventSchema(BaseModel):
    sender: WebhookUserSchema
    recipient: WebhookUserSchema
    timestamp: int | None = None
    message: WebhookMessageSchema | None = None


class WebhookEntrySchema(BaseModel):
    id: str
    time: int
    messaging: list[WebhookMessagingEventSchema] = []


class WebhookPayloadSchema(BaseModel):
    object: str
    entry: list[WebhookEntrySchema]
