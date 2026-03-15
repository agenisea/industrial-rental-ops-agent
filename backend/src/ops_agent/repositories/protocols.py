from typing import Protocol

from ops_agent.models.message import Message
from ops_agent.models.order import Order
from ops_agent.models.product import Product


class OrderRepository(Protocol):
    def get_by_code(self, code: str) -> Order | None: ...
    def find_active_by_company(self, company_name: str) -> list[Order]: ...


class MessageRepository(Protocol):
    def get_by_conversation(self, conversation_id: str) -> list[Message]: ...


class ProductRepository(Protocol):
    def get_by_id(self, product_id: str) -> Product | None: ...
