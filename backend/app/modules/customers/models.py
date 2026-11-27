import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStampMixin

if TYPE_CHECKING:
    from app.modules.orders.models import Order
    from app.modules.pages.models import Pages


# a page's buyer: reached via messenger (psid) or added manually by the owner (phone only)
class Customer(Base, TimeStampMixin):
    __tablename__ = "customers"
    __table_args__ = (
        # psid is page-scoped: the same person has a different psid on each page
        UniqueConstraint("page_id", "psid"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    page_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pages.id", ondelete="CASCADE"), index=True, nullable=False
    )
    page: Mapped["Pages"] = relationship(back_populates="customers")
    psid: Mapped[str | None] = mapped_column(String(100))
    name: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(20), index=True)
    address: Mapped[str | None] = mapped_column(Text)

    orders: Mapped[list["Order"]] = relationship(back_populates="customer")
