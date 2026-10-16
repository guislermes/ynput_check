"""
node_002_db_engine — create SQLite from all stage_0010_db_models tables

Imports every model module so SQLModel.metadata is complete, then create_all.
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqlmodel import SQLModel, create_engine

HERE = Path(__file__).resolve().parent
SCHEMA_DIR = HERE.parent / "stage_0010_db_models"
DB_PATH = HERE / "stage_0010_production.db"

sys.path.insert(0, str(SCHEMA_DIR))

# Register all tables on SQLModel.metadata (import side-effect)
from node_002_db_model_plate import Plate  # noqa: E402, F401
from node_003_db_model_people import Assignment, Person  # noqa: E402, F401
from node_004_db_model_project import Project, Server  # noqa: E402, F401
from node_005_db_model_kitsu import (  # noqa: E402, F401
    Asset,
    Comment,
    Episode,
    Sequence,
    Shot,
    Task,
)
from node_006_db_model_ayon import (  # noqa: E402, F401
    Product,
    Representation,
    Version,
    Workfile,
)

# Stable order for count / verify helpers
ALL_MODELS = (
    Person,
    Assignment,
    Project,
    Plate,
    Episode,
    Sequence,
    Shot,
    Asset,
    Task,
    Comment,
    Product,
    Version,
    Representation,
    Workfile,
)


def snippet_engine(db_path: Path = DB_PATH):
    return create_engine(f"sqlite:///{db_path.as_posix()}", echo=False)


def db_render(db_path: Path = DB_PATH):
    """create_all then dispose — Windows needs the pool closed before unlink."""
    engine = snippet_engine(db_path)
    SQLModel.metadata.create_all(engine)
    engine.dispose()
    print(f"Database created: {db_path}")
    return engine


if __name__ == "__main__":
    try:
        db_render()
    except Exception as exc:  # noqa: BLE001 — learning cheat
        print(f"skip create: {exc}")
