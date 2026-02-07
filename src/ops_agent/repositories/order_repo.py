from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ops_agent.models.order import Order
from ops_agent.models.user import User


class SqlOrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_code(self, code: str) -> Order | None:
        stmt = (
            select(Order)
            .options(joinedload(Order.user))
            .where(Order.code == code)
        )
        return self._session.scalars(stmt).first()

    def find_active_by_company(self, company_name: str) -> list[Order]:
        # Convert "Chase Construction" → "%Chase_Construction%" for LIKE
        like_pattern = f"%{company_name.replace(' ', '_')}%"
        stmt = (
            select(Order)
            .join(User)
            .options(joinedload(Order.user))
            .where(
                User.username.ilike(like_pattern),
                Order.status == "Active",
            )
        )
        return list(self._session.scalars(stmt).unique().all())
