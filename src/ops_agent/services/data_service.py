"""Smart CSV → SQLite seed loader.

First run: bulk-inserts all CSV rows.
Subsequent runs: diffs CSV IDs vs DB IDs and inserts only new rows.
"""

import csv
import logging
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from ops_agent.models.base import Base, Engine
from ops_agent.models.message import Message
from ops_agent.models.order import Order
from ops_agent.models.product import Product
from ops_agent.models.user import User

logger = logging.getLogger(__name__)

CSV_MODEL_MAP: list[tuple[str, type[Base]]] = [
    ("users.csv", User),
    ("products.csv", Product),
    ("orders.csv", Order),
    ("messages.csv", Message),
]

TRUTHY_STRINGS = {"true", "1", "yes"}


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in TRUTHY_STRINGS


def _row_to_model(model_cls: type[Base], row: dict[str, str]) -> Base:
    """Convert a CSV row dict into an ORM instance, coercing types."""
    kwargs: dict[str, object] = {}
    for col in model_cls.__table__.columns:
        raw = row.get(col.name)
        if raw is None or raw == "":
            kwargs[col.name] = None
            continue
        col_type = str(col.type)
        if col_type == "BOOLEAN":
            kwargs[col.name] = _parse_bool(raw)
        elif col_type == "FLOAT":
            kwargs[col.name] = float(raw)
        else:
            kwargs[col.name] = raw
    return model_cls(**kwargs)


def seed_database(engine: Engine, data_dir: Path) -> None:
    """Load CSV data into SQLite. Only inserts rows not already in DB."""
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        for csv_name, model_cls in CSV_MODEL_MAP:
            csv_path = data_dir / csv_name
            if not csv_path.exists():
                logger.warning("CSV not found: %s", csv_path)
                continue

            existing_ids = set(
                session.scalars(
                    select(text("id")).select_from(model_cls.__table__)
                ).all()
            )

            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                new_rows = []
                for row in reader:
                    if row["id"] not in existing_ids:
                        new_rows.append(_row_to_model(model_cls, row))

            if new_rows:
                session.add_all(new_rows)
                session.commit()
                logger.info(
                    "Seeded %d new rows into %s", len(new_rows), model_cls.__tablename__
                )
            else:
                logger.info("Table %s already up to date", model_cls.__tablename__)
