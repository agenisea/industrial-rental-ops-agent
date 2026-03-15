from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from ops_agent.models.base import get_engine, get_session_factory
from ops_agent.repositories.message_repo import SqlMessageRepository
from ops_agent.repositories.order_repo import SqlOrderRepository
from ops_agent.repositories.product_repo import SqlProductRepository
from ops_agent.services.data_service import seed_database

DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture(scope="session")
def db_engine():
    engine = get_engine("sqlite://")
    seed_database(engine, DATA_DIR)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    factory = get_session_factory(db_engine)
    session = factory()
    yield session
    session.close()


@pytest.fixture()
def order_repo(db_session: Session) -> SqlOrderRepository:
    return SqlOrderRepository(db_session)


@pytest.fixture()
def message_repo(db_session: Session) -> SqlMessageRepository:
    return SqlMessageRepository(db_session)


@pytest.fixture()
def product_repo(db_session: Session) -> SqlProductRepository:
    return SqlProductRepository(db_session)
