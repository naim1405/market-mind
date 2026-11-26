import uuid
from typing import TYPE_CHECKING

from sqlalchemy import true
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Boolean, String

from app.db.base import Base, TimeStampMixin

if TYPE_CHECKING:
    from app.modules.pages.models import Pages

class User(Base, TimeStampMixin):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    facebook_id: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )
    pages: Mapped[list["Pages"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
