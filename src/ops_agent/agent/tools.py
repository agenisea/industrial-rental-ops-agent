import functools
from typing import Any

from pydantic_ai import Agent, RunContext

from ops_agent.agent.deps import AgentDeps
from ops_agent.agent.schemas import AgentResponse
from ops_agent.models.order import Order
from ops_agent.repositories.protocols import (
    OrderRepository,
    ProductRepository,
)


class OrderNotFoundError(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(f"No order found with code {code}")


def _get_order_info(
    order_repo: OrderRepository, order_code: str
) -> Order:
    """Retrieve an order by code, raising OrderNotFoundError if missing."""
    order = order_repo.get_by_code(order_code)
    if not order:
        raise OrderNotFoundError(order_code)
    return order


def _get_product_info(
    product_repo: ProductRepository,
    waste_type_id: str | None,
) -> tuple[str, float | None]:
    """Resolve product name and tonnage from waste_type_id.

    Returns ("Unknown", None) when the product cannot be found.
    """
    if waste_type_id:
        product = product_repo.get_by_id(waste_type_id)
        if product:
            return product.name, product.included_tonnage_quantity
    return "Unknown", None


def handle_tool_errors(func: Any) -> Any:
    """Cross-cutting error handler for all agent tools."""

    @functools.wraps(func)
    async def wrapper(
        ctx: RunContext[AgentDeps], *args: Any, **kwargs: Any
    ) -> Any:
        try:
            return await func(ctx, *args, **kwargs)
        except OrderNotFoundError as e:
            return str(e)
        except Exception as e:
            ctx.deps.logger.log_error(
                request_id=ctx.deps.request_id,
                tool_name=func.__name__,
                error=str(e),
            )
            return f"Sorry, I encountered an error: {type(e).__name__}"

    return wrapper


def register_tools(
    agent: Agent[AgentDeps, AgentResponse],
) -> None:
    @agent.tool
    @handle_tool_errors
    async def lookup_order(
        ctx: RunContext[AgentDeps],
        order_code: str,
    ) -> str:
        """Look up an order by short code (e.g., ORD-1234). \
Returns status, access details, product info, and customer."""
        order = _get_order_info(
            ctx.deps.order_repo, order_code
        )
        product_name, tonnage = _get_product_info(
            ctx.deps.product_repo, order.waste_type_id
        )
        return (
            f"Order {order.code}: status={order.status}, "
            f"customer={order.user.username.replace('_', ' ')}, "
            f"product={product_name}, "
            f"included_tonnage={tonnage}, "
            f"access_details={order.access_details or 'None'}, "
            f"start_date={order.start_date}, "
            f"end_date={order.end_date}"
        )

    @agent.tool
    @handle_tool_errors
    async def find_active_orders(
        ctx: RunContext[AgentDeps],
        company_name: str,
    ) -> str:
        """Find all active orders for a company \
(e.g., 'Chase Construction')."""
        orders = ctx.deps.order_repo.find_active_by_company(
            company_name
        )
        if not orders:
            return f"No active orders found for '{company_name}'"
        lines: list[str] = []
        for order in orders:
            product_name, _ = _get_product_info(
                ctx.deps.product_repo, order.waste_type_id
            )
            lines.append(
                f"Order {order.code}: status={order.status}, "
                f"customer={order.user.username.replace('_', ' ')}, "
                f"product={product_name}, "
                f"access_details="
                f"{order.access_details or 'None'}"
            )
        return "\n".join(lines)

    @agent.tool
    @handle_tool_errors
    async def get_order_sentiment(
        ctx: RunContext[AgentDeps],
        order_code: str,
    ) -> str:
        """Analyze customer sentiment for messages on an order. \
Returns sentiment breakdown and flagged negative messages."""
        order = _get_order_info(
            ctx.deps.order_repo, order_code
        )
        messages = ctx.deps.message_repo.get_by_conversation(
            order.conversation_id
        )
        if not messages:
            return "No messages found for this order"
        counts: dict[str, int] = {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
        }
        flagged: list[str] = []
        for message in messages:
            sentiment = (
                message.sentiment_label
                if message.sentiment_label in counts
                else "neutral"
            )
            counts[sentiment] += 1
            if sentiment == "negative":
                flagged.append(message.message)
        overall = max(counts, key=lambda k: counts[k])
        return (
            f"Order {order_code}: {len(messages)} messages, "
            f"overall={overall}, "
            f"positive={counts['positive']}, "
            f"neutral={counts['neutral']}, "
            f"negative={counts['negative']}, "
            f"flagged_negative_messages={flagged}"
        )
