import uuid

from pydantic import Basemodel


class AuthSchema(Basemodel):
    user_id: uuid.UUID
    access_token: str
    refresh_token: str | None
    expires_in: int | None


class Token(Basemodel):
    access_token: str
    token_type: str = "bearer"
