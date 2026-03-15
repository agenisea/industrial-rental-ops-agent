from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ops_agent.models.base import Base
from ops_agent.models.user import User


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    conversation_id: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[str] = mapped_column(String, nullable=False)
    end_date: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    waste_type_id: Mapped[str] = mapped_column(String, nullable=True)
    access_details: Mapped[str] = mapped_column(String, default="")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship(back_populates="orders")

    __table_args__ = (
        Index("ix_orders_code", "code"),
        Index("ix_orders_user_id", "user_id"),
        Index("ix_orders_status", "status"),
    )
