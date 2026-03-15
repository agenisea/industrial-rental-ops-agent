"""Pydantic Evals — agent-level evaluation suite.

Tests the full pipeline: prompt → LLM → tool selection → response.
Requires ANTHROPIC_API_KEY. Makes real API calls.

Run:  uv run --extra dev python -m evals.eval_agent
"""

from dataclasses import dataclass, field
from pathlib import Path

from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import (
    Evaluator,
    EvaluatorContext,
)

from ops_agent.agent.agent import create_agent
from ops_agent.agent.deps import AgentDeps
from ops_agent.agent.schemas import AgentResponse
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


# ── Evaluators ───────────────────────────────────────────────


@dataclass
class MessageContains(Evaluator[str, AgentResponse]):
    """Check that the message field contains expected substrings."""

    substrings: list[str] = field(default_factory=list)

    def evaluate(
        self, ctx: EvaluatorContext[str, AgentResponse]
    ) -> bool:
        msg = ctx.output.message.lower()
        return all(s.lower() in msg for s in self.substrings)


@dataclass
class HasOrderData(Evaluator[str, AgentResponse]):
    """Check that structured order data is populated."""

    order_code: str = ""

    def evaluate(
        self, ctx: EvaluatorContext[str, AgentResponse]
    ) -> bool:
        if not ctx.output.orders:
            return False
        return any(
            o.code == self.order_code for o in ctx.output.orders
        )


@dataclass
class HasSentimentData(Evaluator[str, AgentResponse]):
    """Check that sentiment data is populated correctly."""

    order_code: str = ""
    expected_count: int = 0

    def evaluate(
        self, ctx: EvaluatorContext[str, AgentResponse]
    ) -> bool:
        if not ctx.output.sentiment:
            return False
        s = ctx.output.sentiment
        return (
            s.order_code == self.order_code
            and s.message_count == self.expected_count
        )


@dataclass
class HasOrderSummaries(Evaluator[str, AgentResponse]):
    """Check that order summaries are populated."""

    expected_code: str = ""

    def evaluate(
        self, ctx: EvaluatorContext[str, AgentResponse]
    ) -> bool:
        if not ctx.output.order_summaries:
            return False
        return any(
            o.code == self.expected_code
            for o in ctx.output.order_summaries
        )


@dataclass
class NoToolData(Evaluator[str, AgentResponse]):
    """Check that the agent declined gracefully (no structured data)."""

    def evaluate(
        self, ctx: EvaluatorContext[str, AgentResponse]
    ) -> bool:
        return (
            ctx.output.orders is None
            and ctx.output.order_summaries is None
            and ctx.output.sentiment is None
            and len(ctx.output.message) > 0
        )


# ── Setup ────────────────────────────────────────────────────

_engine = get_engine("sqlite://")
seed_database(_engine, DATA_DIR)
_session = get_session_factory(_engine)()
_deps = AgentDeps(
    order_repo=SqlOrderRepository(_session),
    message_repo=SqlMessageRepository(_session),
    product_repo=SqlProductRepository(_session),
    logger=AgentLogger(Path("/tmp/eval-logs")),
    request_id="eval-agent",
)
_agent = create_agent()


# ── Task function ────────────────────────────────────────────


async def run_agent(query: str) -> AgentResponse:
    """Run the full agent pipeline with a real LLM."""
    result = await _agent.run(query, deps=_deps)
    return result.output


# ── Dataset ──────────────────────────────────────────────────

dataset: Dataset[str, AgentResponse] = Dataset(
    cases=[
        # ── Order Lookup ─────────────────────────────────
        Case(
            name="order_lookup_5353",
            inputs="What's the status of ORD-5353?",
            evaluators=[
                MessageContains(
                    substrings=[
                        "ORD-5353",
                        "Completed",
                        "30 Yard Dumpster",
                        "4.0",
                    ]
                ),
                HasOrderData(order_code="ORD-5353"),
            ],
            metadata={"capability": "order_context"},
        ),
        # ── Product awareness (tonnage) ──────────────────
        Case(
            name="tonnage_awareness",
            inputs="Look up ORD-1592, what product is it?",
            evaluators=[
                MessageContains(
                    substrings=["20 Yard Dumpster"],
                ),
                HasOrderData(order_code="ORD-1592"),
            ],
            metadata={"capability": "schema_awareness"},
        ),
        # ── Sentiment ────────────────────────────────────
        Case(
            name="sentiment_check",
            inputs="How's the customer feeling about ORD-9910?",
            evaluators=[
                HasSentimentData(
                    order_code="ORD-9910",
                    expected_count=8,
                ),
                MessageContains(
                    substrings=["neutral"],
                ),
            ],
            metadata={"capability": "sentiment"},
        ),
        # ── Company search ───────────────────────────────
        Case(
            name="company_search",
            inputs="Show me active orders for Chase Construction",
            evaluators=[
                HasOrderSummaries(expected_code="ORD-1592"),
            ],
            metadata={"capability": "data_linking"},
        ),
        # ── Off-topic rejection ──────────────────────────
        Case(
            name="off_topic_weather",
            inputs="What's the weather in Denver?",
            evaluators=[
                NoToolData(),
            ],
            metadata={"capability": "boundary"},
        ),
    ],
)


# ── Run ──────────────────────────────────────────────────────

if __name__ == "__main__":
    report = dataset.evaluate_sync(run_agent)
    report.print(include_input=True, include_output=True)
