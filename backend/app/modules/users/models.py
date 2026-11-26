import uuid

from sqlalchemy import true
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Boolean, String

from app.db.base import Base, TimeStampMixin


class User(Base, TimeStampMixin):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    facebook_id: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )
