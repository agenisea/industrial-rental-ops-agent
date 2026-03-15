import logging
from pathlib import Path

LOG_FORMAT = "%(asctime)s - [%(name)s] - %(message)s"
LOG_DATEFMT = "%Y-%m-%dT%H:%M:%S"


class AgentLogger:
    """Structured logger for agent interactions."""

    def __init__(self, log_dir: Path = Path("logs")) -> None:
        log_dir.mkdir(exist_ok=True)
        self._logger = logging.getLogger("ops_agent")
        if not self._logger.handlers:
            handler = logging.FileHandler(log_dir / "agent.log")
            handler.setFormatter(
                logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT)
            )
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)

    def log_request(
        self,
        *,
        request_id: str,
        query: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        tools_called: list[str],
        duration_ms: int,
    ) -> None:
        tools = ", ".join(tools_called)
        total = input_tokens + output_tokens
        self._logger.info(
            "request_id=%s query=%r model=%s "
            "tokens=%d tools=[%s] duration=%dms",
            request_id[:8],
            query,
            model,
            total,
            tools,
            duration_ms,
        )

    def log_error(
        self, *, request_id: str, tool_name: str, error: str
    ) -> None:
        self._logger.error(
            "request_id=%s tool=%s error=%s",
            request_id[:8],
            tool_name,
            error,
        )
