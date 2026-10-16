"""
node_002_adapter_kitsu — thin task context (fake by default, gazu when env set)

Env (live):
  KITSU_HOST      e.g. https://your-kitsu-host/api
  KITSU_EMAIL
  KITSU_PASSWORD

Mental model:
  Kitsu = tracking SoT for task + status
  WorkContext tokens stay the path contract; kitsu_* ids are sync handles
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ANATOMY_DIR = HERE.parent / "stage_0020_anatomy"
sys.path.insert(0, str(ANATOMY_DIR))

from node_002_contracts import WorkContext, snippet_dummy_context  # noqa: E402

# ---------------------------------------------------------------------------
# MIND MAP
# ---------------------------------------------------------------------------
#
# snippet_kitsu_env_ready()
# snippet_connect()                 → fake session or gazu login
# snippet_ensure_shot_task(ctx)     → project/seq/shot/task dicts + ids
# snippet_set_task_status(task, s)
# snippet_context_from_task(...)    → WorkContext (tokens unchanged)
#


@dataclass
class KitsuSession:
    """Thin handle. live=False means in-memory fake studio."""

    live: bool
    host: str | None = None
    store: dict[str, Any] | None = None  # fake entities keyed by logical path


def snippet_kitsu_env_ready() -> bool:
    return bool(
        os.environ.get("KITSU_HOST")
        and os.environ.get("KITSU_EMAIL")
        and os.environ.get("KITSU_PASSWORD")
    )


def snippet_connect() -> KitsuSession:
    if not snippet_kitsu_env_ready():
        return KitsuSession(live=False, store={})

    import gazu

    host = os.environ["KITSU_HOST"]
    gazu.set_host(host)
    gazu.log_in(os.environ["KITSU_EMAIL"], os.environ["KITSU_PASSWORD"])
    return KitsuSession(live=True, host=host)


def _fake_id(kind: str, *parts: str) -> str:
    return f"fake-{kind}-" + "-".join(parts)


def snippet_ensure_shot_task(
    session: KitsuSession | None = None,
    ctx: WorkContext | None = None,
) -> dict[str, Any]:
    """
    Ensure project/sequence/shot/task exist. Returns a bundle:
      project, sequence, shot, task, context, mode
    """
    session = session or snippet_connect()
    ctx = ctx or snippet_dummy_context()

    if not session.live:
        assert session.store is not None
        key = f"{ctx.project_code}/{ctx.sequence}/{ctx.shot}/{ctx.task}"
        if key not in session.store:
            project = {
                "id": _fake_id("project", ctx.project_code),
                "name": ctx.project_name,
                "code": ctx.project_code,
            }
            sequence = {
                "id": _fake_id("sequence", ctx.project_code, ctx.sequence),
                "name": ctx.sequence,
                "project_id": project["id"],
            }
            shot = {
                "id": _fake_id("shot", ctx.project_code, ctx.shot),
                "name": ctx.shot,
                "sequence_id": sequence["id"],
                "project_id": project["id"],
            }
            task = {
                "id": _fake_id("task", ctx.project_code, ctx.shot, ctx.task),
                "name": ctx.task,
                "task_type_name": ctx.task,
                "task_status_name": "todo",
                "entity_id": shot["id"],
                "project_id": project["id"],
            }
            session.store[key] = {
                "project": project,
                "sequence": sequence,
                "shot": shot,
                "task": task,
            }
        bundle = dict(session.store[key])
        bundle["context"] = ctx
        bundle["mode"] = "fake"
        return bundle

    # --- live gazu ---
    import gazu

    project = gazu.project.get_project_by_name(ctx.project_name)
    if project is None:
        project = gazu.project.new_project(ctx.project_name)

    sequence = gazu.shot.get_sequence_by_name(project, ctx.sequence)
    if sequence is None:
        sequence = gazu.shot.new_sequence(project, ctx.sequence)

    shot = gazu.shot.get_shot_by_name(sequence, ctx.shot)
    if shot is None:
        shot = gazu.shot.new_shot(
            project,
            sequence,
            ctx.shot,
            frame_in=1001,
            frame_out=1100,
        )

    task_type = gazu.task.get_task_type_by_name(ctx.task.title())
    if task_type is None:
        # fall back: search case-insensitive among types
        task_type = next(
            (
                t
                for t in gazu.task.all_task_types()
                if t["name"].lower() == ctx.task.lower()
            ),
            None,
        )
    if task_type is None:
        raise RuntimeError(
            f"Kitsu task type not found for '{ctx.task}'. "
            "Create it in Kitsu or map the name in the adapter."
        )

    tasks = gazu.task.all_tasks_for_shot(shot)
    task = next(
        (t for t in tasks if t.get("task_type_id") == task_type["id"]),
        None,
    )
    if task is None:
        task = gazu.task.new_task(shot, task_type)

    return {
        "project": project,
        "sequence": sequence,
        "shot": shot,
        "task": task,
        "context": ctx,
        "mode": "live",
    }


def snippet_set_task_status(
    session: KitsuSession,
    task: dict[str, Any],
    status_name: str,
) -> dict[str, Any]:
    """Bump status. Fake mutates dict; live calls gazu."""
    if not session.live:
        task = dict(task)
        task["task_status_name"] = status_name
        # keep store in sync if we can find the key
        if session.store:
            for bundle in session.store.values():
                if bundle["task"]["id"] == task["id"]:
                    bundle["task"] = task
        return task

    import gazu

    status = gazu.task.get_task_status_by_name(status_name)
    if status is None:
        raise RuntimeError(f"Kitsu status not found: {status_name}")
    return gazu.task.update_task_status(task, status)


def snippet_status_name(task: dict[str, Any]) -> str:
    return (
        task.get("task_status_name")
        or task.get("task_status", {}).get("name")
        or "unknown"
    )


def snippet_with_version(ctx: WorkContext, version: int) -> WorkContext:
    return replace(ctx, version=version)


if __name__ == "__main__":
    try:
        session = snippet_connect()
        print("mode:", "live" if session.live else "fake")
        bundle = snippet_ensure_shot_task(session)
        task = bundle["task"]
        print("task id:", task["id"], "status:", snippet_status_name(task))
        task = snippet_set_task_status(session, task, "wip")
        print("after wip:", snippet_status_name(task))
    except Exception as exc:  # noqa: BLE001 — learning cheat
        print(f"skip kitsu: {exc}")
