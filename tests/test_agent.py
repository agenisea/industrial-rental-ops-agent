"""Agent behavior tests — verify prompt → tool selection → output correctness."""

from pathlib import Path

import pytest
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from ops_agent.agent.agent import create_agent
from ops_agent.agent.deps import AgentDeps
from ops_agent.agent.schemas import AgentResponse
from ops_agent.logger import AgentLogger
from ops_agent.models.base import get_engine, get_session_factory
from ops_agent.repositories.message_repo import SqlMessageRepository
from ops_agent.repositories.order_repo import SqlOrderRepository
from ops_agent.repositories.product_repo import SqlProductRepository
from ops_agent.services.data_service import seed_database

DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture(scope="module")
def test_agent():
    """Create agent with TestModel for deterministic testing."""
    return create_agent(model=TestModel())


@pytest.fixture(scope="module")
def seeded_engine():
    engine = get_engine("sqlite://")
    seed_database(engine, DATA_DIR)
    yield engine
    engine.dispose()


@pytest.fixture()
def deps(seeded_engine):
    session = get_session_factory(seeded_engine)()
    yield AgentDeps(
        order_repo=SqlOrderRepository(session),
        message_repo=SqlMessageRepository(session),
        product_repo=SqlProductRepository(session),
        logger=AgentLogger(Path("/tmp/test-logs")),
        request_id="test-request-123",
    )
    session.close()


@pytest.mark.asyncio
async def test_agent_has_three_tools(test_agent: Agent):
    tool_names = list(test_agent._function_toolset.tools)
    assert "lookup_order" in tool_names
    assert "find_active_orders" in tool_names
    assert "get_order_sentiment" in tool_names


@pytest.mark.asyncio
async def test_agent_calls_tools(test_agent: Agent, deps: AgentDeps):
    """TestModel calls all tools. Verify agent doesn't crash and returns output."""
    result = await test_agent.run(
        "What's the status of ORD-5353?",
        deps=deps,
    )
    # TestModel returns a canned response, but the tools should have run
    assert result.output is not None
    assert isinstance(result.output, AgentResponse)
    assert result.output.message
