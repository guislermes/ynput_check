"""
node_003_run_task_context — resolve DUMY task + derive anatomy paths

Run:
  uv run python stage_0040_kitsu_context/node_003_run_task_context.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANATOMY_DIR = HERE.parent / "stage_0020_anatomy"
sys.path.insert(0, str(ANATOMY_DIR))
sys.path.insert(0, str(HERE))

from node_002_adapter_kitsu import (  # noqa: E402
    snippet_connect,
    snippet_ensure_shot_task,
    snippet_set_task_status,
    snippet_status_name,
)
from node_003_anatomy import snippet_describe_paths, snippet_studio_root  # noqa: E402


def main() -> None:
    session = snippet_connect()
    print("=== stage_0040 task_context ===")
    print(f"mode: {'live' if session.live else 'fake (set KITSU_* for live)'}")

    bundle = snippet_ensure_shot_task(session)
    ctx = bundle["context"]
    task = bundle["task"]

    print(
        f"kitsu: project={bundle['project']['id']} "
        f"shot={bundle['shot']['id']} task={task['id']}"
    )
    print(f"status: {snippet_status_name(task)}")

    task = snippet_set_task_status(session, task, "wip")
    print(f"status → wip: {snippet_status_name(task)}")
    task = snippet_set_task_status(session, task, "waiting_for_approval")
    print(f"status → waiting_for_approval: {snippet_status_name(task)}")

    root = snippet_studio_root()
    print(f"studio_root: {root}")
    print("--- derived paths (anatomy, not stored in Kitsu) ---")
    for key, value in snippet_describe_paths(ctx, root).items():
        print(f"  {key}: {value}")

    print("ok — task context resolved.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — learning cheat
        print(f"skip task context: {exc}")
        raise SystemExit(1) from exc
