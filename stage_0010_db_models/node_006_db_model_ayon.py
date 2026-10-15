"""
node_006_db_model_ayon — AYON publish shapes (local mirror)

Hierarchy (ayon_api mental model):
  Project
    └── Folder (sync twin of Shot/Asset/Sequence — ids later, no table yet)
          ├── Task          (sync twin of Kitsu Task)
          ├── Workfile
          └── Product       (name + productType / family)
                └── Version
                      └── Representation  (files on disk)

3D + AI + published plates = Product rows with different product_type.
FKs so far: id_project on Product / Workfile.
Next: id_product on Version, id_version on Representation, id_task on Workfile.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProductType(str, Enum):
    """AYON productType / family — extend as anatomy grows."""

    PLATE = "plate"
    MODEL = "model"
    RIG = "rig"
    LOOK = "look"
    CACHE = "cache"
    RENDER = "render"
    IMAGE = "image"
    AI_IMAGE = "ai_image"
    AI_VIDEO = "ai_video"
    AI_MESH = "ai_mesh"
    WORKFILE = "workfile"
    OTHER = "other"


class Product(SQLModel, table=True):
    """Publishable family under a folder (AYON Product)."""

    __tablename__ = "products"

    id_product: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)
    id_project: int = Field(foreign_key="projects.id_project", nullable=False)

    name: str = Field(index=True, nullable=False)  # e.g. plateMain, model, renderBeauty
    product_type: ProductType = Field(nullable=False)


class Version(SQLModel, table=True):
    """Immutable publish bump (AYON Version). Never overwrite — new row."""

    __tablename__ = "versions"

    id_version: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)

    number: int = Field(default=1, nullable=False)  # v001 → 1
    comment: Optional[str] = None
    # AI extras (optional; unused for normal 3D publishes)
    tool: Optional[str] = None
    model_name: Optional[str] = None
    seed: Optional[str] = None
    prompt_ref: Optional[str] = None  # path or hash — not full prompt blob


class Representation(SQLModel, table=True):
    """Files for a Version (AYON Representation). path = uri/pattern, not blob."""

    __tablename__ = "representations"

    id_representation: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)

    name: str = Field(index=True, nullable=False)  # e.g. exr, usd, abc, mp4, png
    path: str = Field(nullable=False)


class Workfile(SQLModel, table=True):
    """DCC scene on a Task (AYON Workfile)."""

    __tablename__ = "workfiles"

    id_workfile: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)
    id_project: int = Field(foreign_key="projects.id_project", nullable=False)

    path: str = Field(nullable=False)
    name: Optional[str] = Field(default=None, index=True)
