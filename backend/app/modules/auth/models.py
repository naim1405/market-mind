import uuid

from sqlalchemy import ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimeStampMixin


class Auth(Base, TimeStampMixin):
    __tablename__ = "auth"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    access_token = mapped_column(String, nullable=False)
    refresh_token = mapped_column(String, nullable=True)
    expires_in = mapped_column(Integer, nullable=True)
