import contextlib
import json
import time
import uuid
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, Request
from pydantic_ai import CallToolsNode, ToolCallPart
from pydantic_graph.nodes import End
from sse_starlette.sse import EventSourceResponse

from ops_agent.agent.deps import AgentDeps
from ops_agent.agent.schemas import AgentResponse
from ops_agent.api.schemas import ChatRequest, ChatResponseEnvelope
from ops_agent.logger import AgentLogger
from ops_agent.repositories.message_repo import SqlMessageRepository
from ops_agent.repositories.order_repo import SqlOrderRepository
from ops_agent.repositories.product_repo import SqlProductRepository

router = APIRouter(prefix="/api")

TOOL_STATUS_TEMPLATES: dict[str, str] = {
    "lookup_order": "Looking up order {order_code}...",
    "find_active_orders": (
        "Searching active orders for {company_name}..."
    ),
    "get_order_sentiment": (
        "Analyzing sentiment for {order_code}..."
    ),
}


def _tool_status_message(
    tool_name: str, args: str | dict[str, Any] | None
) -> str:
    template = TOOL_STATUS_TEMPLATES.get(tool_name)
    if not template:
        return f"Running {tool_name}..."
    fmt_args: dict[str, Any] = {}
    if isinstance(args, dict):
        fmt_args = args
    elif isinstance(args, str):
        with contextlib.suppress(json.JSONDecodeError, TypeError):
            fmt_args = json.loads(args)
    try:
        return template.format(**fmt_args)
    except KeyError:
        return f"Running {tool_name}..."


def _sse_event(
    phase: str,
    message: str | None = None,
    error: str | None = None,
) -> dict[str, str]:
    payload: dict[str, Any] = {}
    if message is not None:
        payload["message"] = message
    if error is not None:
        payload["error"] = error
    return {"event": phase, "data": json.dumps(payload)}


@router.post("/chat")
async def chat(body: ChatRequest, request: Request) -> EventSourceResponse:
    request_id = str(uuid.uuid4())
    start_time = time.monotonic()

    session_factory = request.app.state.session_factory
    agent = request.app.state.agent
    agent_logger: AgentLogger = request.app.state.agent_logger

    async def event_stream() -> AsyncIterator[dict[str, str]]:
        session = session_factory()
        try:
            deps = AgentDeps(
                order_repo=SqlOrderRepository(session),
                message_repo=SqlMessageRepository(session),
                product_repo=SqlProductRepository(session),
                logger=agent_logger,
                request_id=request_id,
            )

            yield _sse_event("thinking", "Processing your request...")

            model_name = "unknown"
            tools_called: list[str] = []

            async with agent.iter(
                body.message, deps=deps
            ) as agent_run:
                async for node in agent_run:
                    if isinstance(node, CallToolsNode):
                        if node.model_response.model_name:
                            model_name = node.model_response.model_name
                        for part in node.model_response.parts:
                            if isinstance(part, ToolCallPart):
                                tools_called.append(
                                    part.tool_name
                                )
                                msg = _tool_status_message(
                                    part.tool_name, part.args
                                )
                                yield _sse_event(
                                    "tool_call", msg
                                )
                    elif isinstance(node, End):
                        pass

            agent_result = agent_run.result
            output: AgentResponse = agent_result.output

            usage = agent_result.usage()
            duration_ms = int(
                (time.monotonic() - start_time) * 1000
            )

            agent_logger.log_request(
                request_id=request_id,
                query=body.message,
                model=model_name,
                input_tokens=usage.request_tokens or 0,
                output_tokens=usage.response_tokens or 0,
                tools_called=tools_called,
                duration_ms=duration_ms,
            )

            envelope = ChatResponseEnvelope(
                data=output,
                request_id=request_id,
                model=model_name,
            )

            yield {
                "event": "complete",
                "data": envelope.model_dump_json(),
            }

        except Exception as e:
            agent_logger.log_error(
                request_id=request_id,
                tool_name="chat",
                error=str(e),
            )
            yield _sse_event(
                "error",
                error=str(e),
            )
        finally:
            session.close()

    return EventSourceResponse(event_stream(), sep="\n")
