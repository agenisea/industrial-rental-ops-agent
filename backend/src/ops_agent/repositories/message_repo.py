from sqlalchemy import select
from sqlalchemy.orm import Session

from ops_agent.models.message import Message


class SqlMessageRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_conversation(self, conversation_id: str) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_on)
        )
        return list(self._session.scalars(stmt).all())
