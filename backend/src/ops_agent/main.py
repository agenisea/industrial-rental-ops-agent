import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ops_agent.agent.agent import create_agent
from ops_agent.api.routes import router
from ops_agent.config import settings
from ops_agent.logger import AgentLogger
from ops_agent.models.base import get_engine, get_session_factory
from ops_agent.services.data_service import seed_database

logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting ops-agent...")

    engine = get_engine(settings.database_url)
    seed_database(engine, settings.data_dir)

    app.state.session_factory = get_session_factory(engine)
    app.state.agent = create_agent()
    app.state.agent_logger = AgentLogger(settings.log_dir)

    logger.info("ops-agent ready")
    yield

    engine.dispose()
    logger.info("ops-agent shut down")


app = FastAPI(title="Ops Agent", version="0.1.0", lifespan=lifespan)
app.include_router(router)

static_dir = Path(settings.static_dir)
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True))
