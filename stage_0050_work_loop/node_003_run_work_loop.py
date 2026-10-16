"""
node_003_run_work_loop — chain Kitsu → anatomy → Blender I/O → SQL → status

Thin glue only. Run:
  uv run python stage_0050_work_loop/node_003_run_work_loop.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ANATOMY_DIR = ROOT / "stage_0020_anatomy"
BLENDER_DIR = ROOT / "stage_0030_blender_io"
KITSU_DIR = ROOT / "stage_0040_kitsu_context"

for path in (ANATOMY_DIR, BLENDER_DIR, KITSU_DIR, HERE):
    sys.path.insert(0, str(path))

from node_002_adapter_blender import (  # noqa: E402
    snippet_export,
    snippet_has_bpy,
    snippet_import_file,
    snippet_load_workfile,
    snippet_save_workfile,
)
from node_002_adapter_kitsu import (  # noqa: E402
    snippet_connect,
    snippet_ensure_shot_task,
    snippet_set_task_status,
    snippet_status_name,
)
from node_002_adapter_sql import snippet_upsert_work_mirror  # noqa: E402
from node_003_anatomy import (  # noqa: E402
    snippet_describe_paths,
    snippet_ensure_shot_tree,
    snippet_studio_root,
)


def _log(msg: str) -> None:
    print(msg)


def main() -> None:
    _log("=== stage_0050 work_loop ===")

    # 1) Kitsu context
    session = snippet_connect()
    _log(f"[kitsu] mode={'live' if session.live else 'fake'}")
    bundle = snippet_ensure_shot_task(session)
    ctx = bundle["context"]
    task = bundle["task"]
    _log(
        f"[kitsu] project={bundle['project']['id']} "
        f"shot={bundle['shot']['id']} task={task['id']} "
        f"status={snippet_status_name(task)}"
    )

    task = snippet_set_task_status(session, task, "wip")
    _log(f"[kitsu] status → {snippet_status_name(task)}")

    # 2) Anatomy
    root = snippet_studio_root()
    shot_root = snippet_ensure_shot_tree(ctx, root)
    _log(f"[anatomy] shot_root={shot_root}")

    # 3) Blender I/O
    _log(f"[blender] bpy={'yes' if snippet_has_bpy() else 'stub'}")
    work_target = snippet_load_workfile(ctx, root)
    _log(f"[blender] load_target={work_target}")
    saved = snippet_save_workfile(ctx, root)
    _log(f"[blender] saved={saved} exists={saved.is_file()}")
    abc = snippet_export(ctx, "abc", root)
    fbx = snippet_export(ctx, "fbx", root)
    _log(f"[blender] export abc={abc}")
    _log(f"[blender] export fbx={fbx}")
    imported = snippet_import_file(ctx, abc, "abc", root)
    _log(f"[blender] imported={imported}")

    if not saved.is_file() or not abc.is_file():
        raise FileNotFoundError("workfile or export missing after I/O — fail loud")

    # 4) SQL cache
    mirror = snippet_upsert_work_mirror(
        ctx,
        saved,
        task_status=snippet_status_name(task),
        kitsu_task_id=str(task["id"]),
    )
    _log("[sql] mirror:")
    for key, value in mirror.items():
        _log(f"  {key}: {value}")

    # 5) Kitsu status bump after deliverable exists
    task = snippet_set_task_status(session, task, "waiting_for_approval")
    _log(f"[kitsu] status → {snippet_status_name(task)}")
    snippet_upsert_work_mirror(
        ctx,
        saved,
        task_status=snippet_status_name(task),
        kitsu_task_id=str(task["id"]),
    )

    _log("--- path dump ---")
    for key, value in snippet_describe_paths(ctx, root).items():
        _log(f"  {key}: {value}")

    _log("ok — work loop finished.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — learning cheat
        print(f"skip work loop: {exc}")
        raise SystemExit(1) from exc
