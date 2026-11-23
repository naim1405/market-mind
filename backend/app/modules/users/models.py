import uuid

from sqlalchemy import true
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Boolean, String

from db.base import Base, TimeStampMixin


class User(Base, TimeStampMixin):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
