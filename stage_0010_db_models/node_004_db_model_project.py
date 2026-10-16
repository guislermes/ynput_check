"""
node_004_db_model_project — show root (Kitsu + AYON: Project)

No FKs yet. Sequence/Shot/Asset/Task/Plate hang off this later.
Client stays a string until Client entity exists.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Server(str, Enum):
    """Where the show lives (local learning / studio site). Thin until ProjectSetting."""

    LOCAL = "local"
    STUDIO = "studio"
    CLOUD = "cloud"


class ProjectStatus(str, Enum):
    PITCH = "pitch"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project(SQLModel, table=True):
    """Show root. Everything production-scoped resolves via project id later."""

    __tablename__ = "projects"

    id_project: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)

    name: str = Field(index=True, unique=True, nullable=False)
    code: str = Field(index=True, unique=True, nullable=False)  # naming token, e.g. SHOW
    client: str = Field(nullable=False)  # string for now — Client table later
    status: ProjectStatus = Field(default=ProjectStatus.PITCH)
    server: Server = Field(nullable=False)

    # thin specs until ProjectSetting key/value
    fps: str = Field(default="24")
    resolution: str = Field(default="1920x1080")
