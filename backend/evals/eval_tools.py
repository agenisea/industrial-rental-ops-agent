"""Pydantic Evals — tool-level evaluation suite.

Tests that each agent tool returns correct, complete data for
known queries. Runs against seeded SQLite (deterministic, no LLM).

Run:  uv run --extra dev python -m evals.eval_tools
"""

from dataclasses import dataclass, field
from pathlib import Path

from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import (
    Evaluator,
    EvaluatorContext,
)
from sqlalchemy.orm import Session

from ops_agent.agent.deps import AgentDeps
from ops_agent.agent.tools import (
    OrderNotFoundError,
    _get_order_info,
    _get_product_info,
)
from ops_agent.logger import AgentLogger
from ops_agent.models.base import get_engine, get_session_factory
from ops_agent.repositories.message_repo import (
    SqlMessageRepository,
)
from ops_agent.repositories.order_repo import SqlOrderRepository
from ops_agent.repositories.product_repo import (
    SqlProductRepository,
)
from ops_agent.services.data_service import seed_database

DATA_DIR = Path(__file__).parent.parent / "data"


# ── Types ────────────────────────────────────────────────────


@dataclass
class ToolInput:
    tool: str
    args: dict[str, str]


# ── Evaluators ───────────────────────────────────────────────


@dataclass
class ContainsAll(Evaluator[ToolInput, str]):
    """Check that output contains ALL expected substrings."""

    substrings: list[str] = field(default_factory=list)

    def evaluate(
        self, ctx: EvaluatorContext[ToolInput, str]
    ) -> bool:
        output = str(ctx.output)
        return all(
            s.lower() in output.lower() for s in self.substrings
        )


@dataclass
class SentimentCounts(Evaluator[ToolInput, str]):
    """Verify sentiment breakdown has correct counts."""

    positive: int = 0
    neutral: int = 0
    negative: int = 0
    total: int = 0

    def evaluate(
        self, ctx: EvaluatorContext[ToolInput, str]
    ) -> bool:
        output = str(ctx.output)
        return (
            f"positive={self.positive}" in output
            and f"neutral={self.neutral}" in output
            and f"negative={self.negative}" in output
            and f"{self.total} messages" in output
        )


@dataclass
class HasProduct(Evaluator[ToolInput, str]):
    """Verify the output includes product name and tonnage."""

    product_name: str = ""
    tonnage: float | None = None

    def evaluate(
        self, ctx: EvaluatorContext[ToolInput, str]
    ) -> bool:
        output = str(ctx.output)
        if self.product_name not in output:
            return False
        return not (
            self.tonnage is not None
            and str(self.tonnage) not in output
        )


# ── DB + Deps setup ──────────────────────────────────────────


def _setup() -> tuple[Session, AgentDeps]:
    engine = get_engine("sqlite://")
    seed_database(engine, DATA_DIR)
    session = get_session_factory(engine)()
    deps = AgentDeps(
        order_repo=SqlOrderRepository(session),
        message_repo=SqlMessageRepository(session),
        product_repo=SqlProductRepository(session),
        logger=AgentLogger(Path("/tmp/eval-logs")),
        request_id="eval-run",
    )
    return session, deps


# ── Task function ────────────────────────────────────────────

_session, _deps = _setup()


async def run_tool(inputs: ToolInput) -> str:
    """Execute a single tool call and return its string output."""
    if inputs.tool == "lookup_order":
        try:
            order = _get_order_info(
                _deps.order_repo, inputs.args["order_code"]
            )
        except OrderNotFoundError as e:
            return str(e)
        product_name, tonnage = _get_product_info(
            _deps.product_repo, order.waste_type_id
        )
        return (
            f"Order {order.code}: status={order.status}, "
            f"customer="
            f"{order.user.username.replace('_', ' ')}, "
            f"product={product_name}, "
            f"included_tonnage={tonnage}, "
            f"access_details={order.access_details or 'None'}, "
            f"start_date={order.start_date}, "
            f"end_date={order.end_date}"
        )

    if inputs.tool == "find_active_orders":
        orders = _deps.order_repo.find_active_by_company(
            inputs.args["company_name"]
        )
        if not orders:
            return (
                f"No active orders found for "
                f"'{inputs.args['company_name']}'"
            )
        lines = []
        for order in orders:
            product_name, _ = _get_product_info(
                _deps.product_repo, order.waste_type_id
            )
            lines.append(
                f"Order {order.code}: status={order.status}, "
                f"product={product_name}, "
                f"access_details="
                f"{order.access_details or 'None'}"
            )
        return "\n".join(lines)

    if inputs.tool == "get_order_sentiment":
        try:
            order = _get_order_info(
                _deps.order_repo, inputs.args["order_code"]
            )
        except OrderNotFoundError as e:
            return str(e)
        messages = _deps.message_repo.get_by_conversation(
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
        for msg in messages:
            sentiment = (
                msg.sentiment_label
                if msg.sentiment_label in counts
                else "neutral"
            )
            counts[sentiment] += 1
            if sentiment == "negative":
                flagged.append(msg.message)
        overall = max(counts, key=lambda k: counts[k])
        return (
            f"Order {inputs.args['order_code']}: "
            f"{len(messages)} messages, "
            f"overall={overall}, "
            f"positive={counts['positive']}, "
            f"neutral={counts['neutral']}, "
            f"negative={counts['negative']}, "
            f"flagged_negative_messages={flagged}"
        )

    return f"Unknown tool: {inputs.tool}"


# ── Dataset ──────────────────────────────────────────────────

dataset: Dataset[ToolInput, str] = Dataset(
    cases=[
        # ── Order Lookup ─────────────────────────────────
        Case(
            name="lookup_ord_5353",
            inputs=ToolInput(
                tool="lookup_order",
                args={"order_code": "ORD-5353"},
            ),
            evaluators=[
                ContainsAll(
                    substrings=[
                        "ORD-5353",
                        "Completed",
                        "Omaha Builders",
                        "Front driveway",
                    ]
                ),
                HasProduct(
                    product_name="30 Yard Dumpster",
                    tonnage=4.0,
                ),
            ],
            metadata={"capability": "order_context"},
        ),
        Case(
            name="lookup_ord_1592",
            inputs=ToolInput(
                tool="lookup_order",
                args={"order_code": "ORD-1592"},
            ),
            evaluators=[
                ContainsAll(
                    substrings=[
                        "ORD-1592",
                        "Active",
                        "Back alley access",
                    ]
                ),
                HasProduct(
                    product_name="20 Yard Dumpster",
                    tonnage=3.0,
                ),
            ],
            metadata={"capability": "order_context"},
        ),
        Case(
            name="lookup_toilet_order",
            inputs=ToolInput(
                tool="lookup_order",
                args={"order_code": "ORD-3657"},
            ),
            evaluators=[
                HasProduct(
                    product_name="Portable Toilet",
                    tonnage=0.0,
                ),
            ],
            metadata={"capability": "order_context"},
        ),
        Case(
            name="lookup_nonexistent",
            inputs=ToolInput(
                tool="lookup_order",
                args={"order_code": "ORD-0000"},
            ),
            expected_output="No order found with code ORD-0000",
            metadata={"capability": "error_handling"},
        ),
        # ── Company Search ───────────────────────────────
        Case(
            name="active_chase_construction",
            inputs=ToolInput(
                tool="find_active_orders",
                args={"company_name": "Chase Construction"},
            ),
            evaluators=[
                ContainsAll(
                    substrings=["ORD-1592", "Active"],
                ),
            ],
            metadata={"capability": "data_linking"},
        ),
        Case(
            name="active_no_results",
            inputs=ToolInput(
                tool="find_active_orders",
                args={"company_name": "Nonexistent Corp"},
            ),
            evaluators=[
                ContainsAll(
                    substrings=["No active orders found"],
                ),
            ],
            metadata={"capability": "data_linking"},
        ),
        # ── Boundary / Off-topic ─────────────────────────
        Case(
            name="unknown_tool",
            inputs=ToolInput(
                tool="weather_forecast",
                args={"city": "Denver"},
            ),
            evaluators=[
                ContainsAll(substrings=["Unknown tool"]),
            ],
            metadata={"capability": "boundary"},
        ),
        # ── Sentiment ────────────────────────────────────
        Case(
            name="sentiment_ord_9910",
            inputs=ToolInput(
                tool="get_order_sentiment",
                args={"order_code": "ORD-9910"},
            ),
            evaluators=[
                SentimentCounts(
                    positive=2,
                    neutral=3,
                    negative=3,
                    total=8,
                ),
            ],
            metadata={"capability": "sentiment"},
        ),
    ],
)


# ── Run ──────────────────────────────────────────────────────

if __name__ == "__main__":
    report = dataset.evaluate_sync(run_tool)
    report.print(
        include_input=True,
        include_output=True,
    )
