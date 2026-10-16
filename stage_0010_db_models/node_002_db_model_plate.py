from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel

from node_004_db_model_project import Server  # noqa: E402 — Server lives on project module


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Plate(SQLModel, table=True):
    """One set clip/take. Queryable camera/lens/color fields; paths not files."""

    __tablename__ = "plates"

    id_plate: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)
    server: Server = Field(nullable=False)
    id_project: int = Field(foreign_key="projects.id_project", nullable=False)

    # identity / disk
    clip_name: str = Field(index=True, nullable=False)
    folder_path: str = Field(nullable=False)
    media_path: str = Field(nullable=False)  # file or frame pattern, e.g. .../clip.%04d.exr

    # set report
    frame_width: int = Field(nullable=False)       # e.g. 1920
    frame_height: int = Field(nullable=False)      # e.g. 1080
    file_size: int = Field(nullable=False)   # file size in MB
    frame_rate: float = Field(nullable=False)      # e.g. 23.976

    # logger / DIT
    camera: Optional[str] = None
    lens: Optional[str] = None
    shutter: Optional[str] = None  # shutter speed
    colorspace: Optional[str] = None
    encoding: Optional[str] = None  # log/gamma family, e.g. LogC3
    notes: Optional[str] = None

    set_comment: Optional[str] = None  # Comment or notes from set
    # set supervisor
    set_supervisor: Optional[str] = None  # Set supervisor for this plate/clip

