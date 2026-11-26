import uuid

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None


class UserCreate(UserBase):
    facebook_id: str | None = None
    is_active: bool | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    facebook_id: str | None = None

    model_config = ConfigDict(from_attributes=True)
