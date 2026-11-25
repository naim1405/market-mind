from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.types import DateTime


class Base(DeclarativeBase):
    pass


class TimeStampMixin:
    """A mixin that adds created_at and updated_at columns to a model."""

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),)

