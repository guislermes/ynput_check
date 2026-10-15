from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PersonKind(str, Enum):
    STAFF = "staff"
    FREELANCER = "freelancer"


class Department(str, Enum):
    ANIMATION = "animation"
    COMPOSITING = "compositing"
    CG = "cg"
    PRODUCTION = "production"
    PIPELINE = "pipeline"
    IT = "it"
    EDITORIAL = "editorial"
    ART = "art"
    MOTION_GRAPHICS = "motion_graphics"
    AI = "ai"

class Role(str, Enum):
    MODELER = "modeler"
    LIGHTER = "lighter"
    CG_COMPOSITOR = "cg_compositor"
    VFX_COMPOSITOR = "vfx_compositor"
    MOTION_GRAPHICS_COMPOSITOR = "motion_graphics_compositor"
    RIGGER = "rigger"
    ANIMATOR = "animator"
    AI_ARTIST = "ai_artist"
    PRODUCER = "producer"
    COORDINATOR = "coordinator"
    EDITOR = "editor"
    RETOUCHER = "retoucher"
    PAINTER = "painter"
    IT = "it"
    TD = "td"
    AI_ARTIST = "ai_artist"
    SUPERVISOR = "supervisor"


class Level(str, Enum):
    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    SUPERVISOR = "supervisor"
    DIRECTOR = "director"

class Person(SQLModel, table=True):
    """Studio person (Kitsu Person). Assignees resolve via Assignment."""

    __tablename__ = "people"

    id_person: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)

    name: str = Field(index=True, nullable=False)
    email: str = Field(index=True, nullable=False)
    kind: PersonKind = Field(default=PersonKind.STAFF)
    department: Department = Field(nullable=False)
    role: Role = Field(nullable=False)
    level: Level = Field(default=Level.MID)


class Assignment(SQLModel, table=True):
    """Person ↔ Task bridge (Kitsu task assignees). person_id / task_id FKs later."""

    __tablename__ = "assignments"

    id_assignment: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)

    is_lead: bool = False

