"""
node_004_run_ensure_tree — create DUMY shot tree twice (prove idempotent)

Run:
  uv run python stage_0020_anatomy/node_004_run_ensure_tree.py

Optional:
  set STUDIO_ROOT=C:\\path\\to\\shows
"""

from __future__ import annotations

from node_002_contracts import snippet_dummy_context
from node_003_anatomy import (
    snippet_describe_paths,
    snippet_ensure_shot_tree,
    snippet_studio_root,
)


def main() -> None:
    ctx = snippet_dummy_context()
    root = snippet_studio_root()

    print("=== stage_0020 ensure_shot_tree ===")
    print(f"studio_root: {root}")
    print(
        f"context: {ctx.project_code} / {ctx.sequence} / {ctx.shot} "
        f"/ {ctx.task} / {ctx.version_token()}"
    )

    first = snippet_ensure_shot_tree(ctx, root)
    print(f"[1] ensured: {first}")

    second = snippet_ensure_shot_tree(ctx, root)
    print(f"[2] ensured again (idempotent): {second}")
    if first != second:
        raise RuntimeError("shot root changed between runs — paths must be stable")

    print("--- resolved paths ---")
    for key, value in snippet_describe_paths(ctx, root).items():
        print(f"  {key}: {value}")

    # Prove dirs exist after ensure
    missing = [
        rel
        for rel in (
            first / "work" / "blender",
            first / "export" / "abc",
            first / "export" / "fbx",
            first / "import" / "ref",
            first / "publish",
        )
        if not rel.is_dir()
    ]
    if missing:
        raise FileNotFoundError(f"missing after ensure: {missing}")

    print("ok — tree present; re-run anytime.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — learning cheat
        print(f"skip ensure: {exc}")
        raise SystemExit(1) from exc
