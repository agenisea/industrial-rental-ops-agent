from sqlalchemy import Boolean, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from ops_agent.models.base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    sentiment_label: Mapped[str] = mapped_column(String, nullable=False)
    created_on: Mapped[str] = mapped_column(String, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (Index("ix_messages_conversation_id", "conversation_id"),)
