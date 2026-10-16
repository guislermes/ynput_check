"""
node_003_run_io_roundtrip — ensure tree → save → export → import

Run (OS Python stubs):
  uv run python stage_0030_blender_io/node_003_run_io_roundtrip.py

Inside Blender: open this file in the Text Editor and Run Script.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANATOMY_DIR = HERE.parent / "stage_0020_anatomy"
sys.path.insert(0, str(ANATOMY_DIR))
sys.path.insert(0, str(HERE))

from node_002_contracts import snippet_dummy_context  # noqa: E402
from node_002_adapter_blender import (  # noqa: E402
    snippet_export,
    snippet_has_bpy,
    snippet_import_file,
    snippet_load_workfile,
    snippet_save_workfile,
)
from node_003_anatomy import (  # noqa: E402
    snippet_describe_paths,
    snippet_ensure_shot_tree,
    snippet_studio_root,
)


def main() -> None:
    ctx = snippet_dummy_context()
    root = snippet_studio_root()

    print("=== stage_0030 io_roundtrip ===")
    print(f"bpy: {'available' if snippet_has_bpy() else 'stub mode (outside Blender)'}")
    print(
        f"context: {ctx.project_code} / {ctx.sequence} / {ctx.shot} "
        f"/ {ctx.task} / {ctx.version_token()}"
    )

    shot = snippet_ensure_shot_tree(ctx, root)
    print(f"shot_root: {shot}")

    work_path = snippet_load_workfile(ctx, root)
    print(f"load target: {work_path}")

    saved = snippet_save_workfile(ctx, root)
    print(f"saved: {saved} exists={saved.is_file()}")

    abc = snippet_export(ctx, "abc", root)
    fbx = snippet_export(ctx, "fbx", root)
    print(f"export abc: {abc} exists={abc.is_file()}")
    print(f"export fbx: {fbx} exists={fbx.is_file()}")

    imported = snippet_import_file(ctx, abc, "abc", root)
    print(f"import ok: {imported}")

    print("--- paths ---")
    for key, value in snippet_describe_paths(ctx, root).items():
        print(f"  {key}: {value}")

    print("ok — roundtrip finished.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — learning cheat
        print(f"skip roundtrip: {exc}")
        raise SystemExit(1) from exc
