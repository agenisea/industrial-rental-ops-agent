from dataclasses import dataclass

from ops_agent.logger import AgentLogger
from ops_agent.repositories.protocols import (
    MessageRepository,
    OrderRepository,
    ProductRepository,
)


@dataclass
class AgentDeps:
    order_repo: OrderRepository
    message_repo: MessageRepository
    product_repo: ProductRepository
    logger: AgentLogger
    request_id: str
