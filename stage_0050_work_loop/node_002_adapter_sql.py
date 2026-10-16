"""
node_002_adapter_sql — local cache for Project / Shot / Task / Workfile

Uses stage_0010_db_models shapes. SQL is audit/cache — not tracking SoT.

Default DB: stage_0050_work_loop/stage_0050_work.db
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from sqlmodel import Session, SQLModel, create_engine, select

HERE = Path(__file__).resolve().parent
SCHEMA_DIR = HERE.parent / "stage_0010_db_models"
ANATOMY_DIR = HERE.parent / "stage_0020_anatomy"
DB_PATH = HERE / "stage_0050_work.db"

sys.path.insert(0, str(SCHEMA_DIR))
sys.path.insert(0, str(ANATOMY_DIR))

from node_002_contracts import WorkContext  # noqa: E402
from node_004_db_model_project import Project, ProjectStatus, Server  # noqa: E402
from node_005_db_model_kitsu import (  # noqa: E402
    EntityStatus,
    Shot,
    Task,
    TaskStatus,
    TaskType,
)
from node_006_db_model_ayon import Workfile  # noqa: E402

# ---------------------------------------------------------------------------
# MIND MAP
# ---------------------------------------------------------------------------
#
# snippet_engine / snippet_create_tables
# snippet_upsert_work_mirror(ctx, workfile_path, task_status, kitsu_ids?)
#   → Project, Shot, Task, Workfile rows
#


_TASK_TYPE_MAP = {
    "modeling": TaskType.MODELING,
    "rigging": TaskType.RIGGING,
    "animation": TaskType.ANIMATION,
    "layout": TaskType.LAYOUT,
    "lighting": TaskType.LIGHTING,
    "comp": TaskType.COMP,
    "fx": TaskType.FX,
}


_TASK_STATUS_MAP = {
    "todo": TaskStatus.TODO,
    "ready_to_start": TaskStatus.READY_TO_START,
    "wip": TaskStatus.WIP,
    "waiting_for_approval": TaskStatus.WAITING_FOR_APPROVAL,
    "retake": TaskStatus.RETAKE,
    "done": TaskStatus.DONE,
    "on_hold": TaskStatus.ON_HOLD,
}


def snippet_engine(db_path: Path = DB_PATH):
    return create_engine(f"sqlite:///{db_path.as_posix()}", echo=False)


def snippet_create_tables(engine) -> None:
    # Import side-effects already registered Project/Shot/Task/Workfile.
    # create_all is safe for the subset we use; other models may also appear
    # if their modules were imported — keep imports narrow above.
    SQLModel.metadata.create_all(engine)


def _map_task_type(name: str) -> TaskType:
    return _TASK_TYPE_MAP.get(name.lower(), TaskType.OTHER)


def _map_task_status(name: str) -> TaskStatus:
    key = name.lower().replace(" ", "_")
    return _TASK_STATUS_MAP.get(key, TaskStatus.TODO)


def snippet_upsert_work_mirror(
    ctx: WorkContext,
    workfile_path: Path | str,
    task_status: str = "wip",
    db_path: Path = DB_PATH,
    kitsu_task_id: str | None = None,
) -> dict[str, Any]:
    """
    Upsert local Project / Shot / Task / Workfile for this context.
    Returns ids + paths for trace logs.
    """
    engine = snippet_engine(db_path)
    snippet_create_tables(engine)
    path_str = str(Path(workfile_path))
    work_name = Path(workfile_path).name

    with Session(engine) as session:
        project = session.exec(
            select(Project).where(Project.code == ctx.project_code)
        ).first()
        if project is None:
            project = Project(
                name=ctx.project_name,
                code=ctx.project_code,
                client="dummy",
                status=ProjectStatus.IN_PROGRESS,
                server=Server.LOCAL,
            )
            session.add(project)
            session.commit()
            session.refresh(project)

        assert project.id_project is not None
        pid = project.id_project

        shot = session.exec(
            select(Shot).where(Shot.id_project == pid, Shot.name == ctx.shot)
        ).first()
        if shot is None:
            shot = Shot(
                id_project=pid,
                name=ctx.shot,
                entity_status=EntityStatus.WIP,
            )
            session.add(shot)
            session.commit()
            session.refresh(shot)

        task = session.exec(
            select(Task).where(
                Task.id_project == pid,
                Task.name == ctx.task,
            )
        ).first()
        mapped_status = _map_task_status(task_status)
        if task is None:
            task = Task(
                id_project=pid,
                name=ctx.task,
                task_type=_map_task_type(ctx.task),
                task_status=mapped_status,
            )
            session.add(task)
        else:
            task.task_status = mapped_status
            session.add(task)
        session.commit()
        session.refresh(task)

        workfile = session.exec(
            select(Workfile).where(Workfile.path == path_str)
        ).first()
        if workfile is None:
            workfile = Workfile(
                id_project=pid,
                path=path_str,
                name=work_name,
            )
            session.add(workfile)
        else:
            workfile.name = work_name
            session.add(workfile)
        session.commit()
        session.refresh(workfile)

        result = {
            "db_path": str(db_path.resolve()),
            "id_project": project.id_project,
            "id_shot": shot.id_shot,
            "id_task": task.id_task,
            "id_workfile": workfile.id_workfile,
            "workfile_path": path_str,
            "task_status": task.task_status.value,
            "kitsu_task_id": kitsu_task_id,
        }

    engine.dispose()
    return result


if __name__ == "__main__":
    try:
        from node_002_contracts import snippet_dummy_context
        from node_003_anatomy import snippet_workfile_path

        ctx = snippet_dummy_context()
        path = snippet_workfile_path(ctx)
        info = snippet_upsert_work_mirror(ctx, path, task_status="wip")
        for key, value in info.items():
            print(f"  {key}: {value}")
    except Exception as exc:  # noqa: BLE001 — learning cheat
        print(f"skip sql: {exc}")
