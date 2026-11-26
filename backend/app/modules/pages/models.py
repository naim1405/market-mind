import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStampMixin

if TYPE_CHECKING:
    from app.modules.users.models import User

class Pages(Base, TimeStampMixin):
    __tablename__ = "pages"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    facebook_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    user: Mapped["User"] = relationship(back_populates="pages")
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
