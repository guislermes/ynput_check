"""
node_005_db_model_kitsu — Kitsu / Zou tracking shapes (local mirror)

Hierarchy (gazu mental model):
  Project
    ├── AssetType → Asset → Task
    └── Episode? → Sequence → Shot → Task
  Task has TaskType + TaskStatus
  Comment attaches to Task
  Assignees = Person via Assignment (node_003_db_model_people.py)

FKs so far: id_project on Episode/Sequence/Shot/Asset/Task/Comment.
Next: id_sequence, id_shot XOR id_asset, id_task, id_person.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# ENUMS (Kitsu lookup-shaped)
# ---------------------------------------------------------------------------


class AssetType(str, Enum):
    """Kitsu AssetType names — project-specific types sync later."""

    CHARACTER = "character"
    PROP = "prop"
    ENVIRONMENT = "environment"
    FX = "fx"
    OTHER = "other"


class EntityStatus(str, Enum):
    """Soft status on Shot/Asset (roll-up; real workflow lives on Task)."""

    TODO = "todo"
    WIP = "wip"
    RETAKE = "retake"
    DONE = "done"
    ON_HOLD = "on_hold"


class TaskType(str, Enum):
    """Kitsu TaskType — studio will alias to gazu task type names."""

    CONCEPT = "concept"
    MODELING = "modeling"
    RIGGING = "rigging"
    SHADER = "shader"
    ANIMATION = "animation"
    LAYOUT = "layout"
    LIGHTING = "lighting"
    FX = "fx"
    COMP = "comp"
    PAINT = "paint"
    EDIT = "edit"
    RENDERING = "rendering"
    OTHER = "other"


class TaskStatus(str, Enum):
    """Kitsu TaskStatus — common pipeline set."""

    TODO = "todo"
    READY_TO_START = "ready_to_start"
    WIP = "wip"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    RETAKE = "retake"
    DONE = "done"
    ON_HOLD = "on_hold"


# ---------------------------------------------------------------------------
# ENTITIES
# ---------------------------------------------------------------------------


class Episode(SQLModel, table=True):
    """Optional series bucket (Kitsu Episode). Skip rows for feature films."""

    __tablename__ = "episodes"

    id_episode: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)
    id_project: int = Field(foreign_key="projects.id_project", nullable=False)

    name: str = Field(index=True, nullable=False)  # e.g. EP01


class Sequence(SQLModel, table=True):
    """Shot group (Kitsu Sequence). Under Episode when series."""

    __tablename__ = "sequences"

    id_sequence: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)
    id_project: int = Field(foreign_key="projects.id_project", nullable=False)
    description: Optional[str] = Field(default=None)
    name: str = Field(index=True, nullable=False)  # e.g. SEQ010


class Shot(SQLModel, table=True):
    """Timeline unit (Kitsu Shot). Work happens on Tasks, not here."""

    __tablename__ = "shots"

    id_shot: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)
    id_project: int = Field(foreign_key="projects.id_project", nullable=False)

    name: str = Field(index=True, nullable=False)  # e.g. SH010
    entity_status: EntityStatus = Field(default=EntityStatus.TODO)
    frame_in: int = Field(default=1001, nullable=False)
    frame_out: int = Field(default=1100, nullable=False)


class Asset(SQLModel, table=True):
    """Reusable show entity (Kitsu Asset). Typed via AssetType."""

    __tablename__ = "assets"

    id_asset: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)
    id_project: int = Field(foreign_key="projects.id_project", nullable=False)

    name: str = Field(index=True, nullable=False)
    asset_type: AssetType = Field(default=AssetType.OTHER, nullable=False)
    entity_status: EntityStatus = Field(default=EntityStatus.TODO)


class Task(SQLModel, table=True):
    """
    Unit of work on exactly one entity (Shot XOR Asset) — Kitsu Task.

    Assignees = Assignment in node_003. Status/type drive the board.
    """

    __tablename__ = "tasks"

    id_task: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)
    id_project: int = Field(foreign_key="projects.id_project", nullable=False)

    name: str = Field(index=True, nullable=False)  # often mirrors task_type label
    task_type: TaskType = Field(nullable=False)
    task_status: TaskStatus = Field(default=TaskStatus.TODO)


class Comment(SQLModel, table=True):
    """Note / feedback (Kitsu Comment). id_task later; id_project for now."""

    __tablename__ = "comments"

    id_comment: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)
    id_project: int = Field(foreign_key="projects.id_project", nullable=False)

    text: str = Field(nullable=False)
    # audience for studio use; Kitsu is usually task-threaded
    is_client: bool = False
