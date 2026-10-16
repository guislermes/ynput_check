"""
node_003_anatomy — path builders + idempotent ensure_shot_tree

Config:
  STUDIO_ROOT  — absolute or relative root for shows (optional)
  default: stage_0020_anatomy/_studio_root

Mental model:
  tokens → Path objects → mkdir parents (exist_ok=True)
  Same input → same paths → safe re-run.
"""

from __future__ import annotations

import os
from pathlib import Path

from node_002_contracts import WorkContext, snippet_dummy_context

# ---------------------------------------------------------------------------
# MIND MAP
# ---------------------------------------------------------------------------
#
# studio_root()
# shot_root(ctx)
# ├── work_blender_dir / workfile_path
# ├── export_dir(fmt) / export_path(fmt)
# ├── import_ref_dir
# └── publish_dir
# ensure_shot_tree(ctx)  → creates all of the above dirs
# assert_under_shot(path, ctx)  → fail loud if path escapes shot root
#

HERE = Path(__file__).resolve().parent
DEFAULT_STUDIO_ROOT = HERE / "_studio_root"

SHOT_SUBDIRS = (
    Path("work") / "blender",
    Path("export") / "abc",
    Path("export") / "fbx",
    Path("import") / "ref",
    Path("publish"),
)


def snippet_studio_root(explicit: Path | str | None = None) -> Path:
    """Resolve STUDIO_ROOT from arg, env, or stage default."""
    if explicit is not None:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get("STUDIO_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return DEFAULT_STUDIO_ROOT.resolve()


def snippet_shot_root(ctx: WorkContext, studio_root: Path | None = None) -> Path:
    root = studio_root or snippet_studio_root()
    return root / ctx.project_code / ctx.sequence / ctx.shot


def snippet_work_blender_dir(ctx: WorkContext, studio_root: Path | None = None) -> Path:
    return snippet_shot_root(ctx, studio_root) / "work" / "blender"


def snippet_workfile_path(
    ctx: WorkContext,
    studio_root: Path | None = None,
    ext: str = "blend",
) -> Path:
    return snippet_work_blender_dir(ctx, studio_root) / ctx.filename(ext)


def snippet_export_dir(
    ctx: WorkContext,
    fmt: str,
    studio_root: Path | None = None,
) -> Path:
    return snippet_shot_root(ctx, studio_root) / "export" / fmt.lower()


def snippet_export_path(
    ctx: WorkContext,
    fmt: str,
    studio_root: Path | None = None,
) -> Path:
    fmt_l = fmt.lower()
    return snippet_export_dir(ctx, fmt_l, studio_root) / ctx.filename(fmt_l)


def snippet_import_ref_dir(ctx: WorkContext, studio_root: Path | None = None) -> Path:
    return snippet_shot_root(ctx, studio_root) / "import" / "ref"


def snippet_publish_dir(ctx: WorkContext, studio_root: Path | None = None) -> Path:
    return snippet_shot_root(ctx, studio_root) / "publish"


def snippet_assert_under_shot(
    path: Path,
    ctx: WorkContext,
    studio_root: Path | None = None,
) -> Path:
    """Fail loud if path is outside the shot tree — pipeline contract guard."""
    shot = snippet_shot_root(ctx, studio_root).resolve()
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(shot)
    except ValueError as exc:
        raise ValueError(
            f"path escapes shot tree: {resolved} not under {shot}"
        ) from exc
    return resolved


def snippet_ensure_shot_tree(
    ctx: WorkContext | None = None,
    studio_root: Path | None = None,
) -> Path:
    """
    Create the canonical shot dirs. Idempotent — safe to call every open/save.
    Returns shot root.
    """
    ctx = ctx or snippet_dummy_context()
    root = studio_root or snippet_studio_root()
    shot = snippet_shot_root(ctx, root)
    for rel in SHOT_SUBDIRS:
        (shot / rel).mkdir(parents=True, exist_ok=True)
    return shot.resolve()


def snippet_describe_paths(
    ctx: WorkContext | None = None,
    studio_root: Path | None = None,
) -> dict[str, str]:
    """Traceable dump for logs — project / shot / task / every key path."""
    ctx = ctx or snippet_dummy_context()
    root = studio_root or snippet_studio_root()
    return {
        "studio_root": str(snippet_studio_root(root)),
        "project": ctx.project_code,
        "sequence": ctx.sequence,
        "shot": ctx.shot,
        "task": ctx.task,
        "version": ctx.version_token(),
        "shot_root": str(snippet_shot_root(ctx, root)),
        "workfile": str(snippet_workfile_path(ctx, root)),
        "export_abc": str(snippet_export_path(ctx, "abc", root)),
        "export_fbx": str(snippet_export_path(ctx, "fbx", root)),
        "import_ref": str(snippet_import_ref_dir(ctx, root)),
        "publish": str(snippet_publish_dir(ctx, root)),
    }


if __name__ == "__main__":
    try:
        ctx = snippet_dummy_context()
        shot = snippet_ensure_shot_tree(ctx)
        print(f"shot_root: {shot}")
        for key, value in snippet_describe_paths(ctx).items():
            print(f"  {key}: {value}")
    except Exception as exc:  # noqa: BLE001 — learning cheat
        print(f"skip anatomy: {exc}")
