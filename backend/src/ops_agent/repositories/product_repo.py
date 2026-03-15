from sqlalchemy.orm import Session

from ops_agent.models.product import Product


class SqlProductRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, product_id: str) -> Product | None:
        return self._session.get(Product, product_id)
