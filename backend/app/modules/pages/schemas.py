import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PageBase(BaseModel):
    facebook_id: str
    name: str
    access_token: str


class PageCreate(PageBase):
    pass


class PageUpdate(BaseModel):
    facebook_id: str | None = None
    name: str | None = None
    access_token: str | None = None


class PageResponse(BaseModel):
    id: uuid.UUID
    facebook_id: str
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
