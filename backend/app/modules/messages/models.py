import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStampMixin

if TYPE_CHECKING:
    from app.modules.customers.models import Customer


# named like gemini's content roles, so history maps 1:1 to the api
class MessageRole(StrEnum):
    USER = "user"  # the customer
    MODEL = "model"  # the ai reply


class Message(Base, TimeStampMixin):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    customer: Mapped["Customer"] = relationship(back_populates="messages")
    role: Mapped[MessageRole] = mapped_column(
        Enum(
            MessageRole,
            native_enum=False,
            length=20,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # messenger message id; unique so a webhook retry can't be processed twice
    mid: Mapped[str | None] = mapped_column(String(255), unique=True)
    # clock_timestamp, not now(): now() is fixed per transaction, and a customer message
    # and its reply are saved in one transaction, so history order would be random
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.clock_timestamp(), index=True
    )
