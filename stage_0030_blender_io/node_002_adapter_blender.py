"""
node_002_adapter_blender — load / save / import / export against stage_0020 paths

Run inside Blender for real bpy ops. Outside Blender, stubs write/read the same paths
so the pipeline contract stays exercisable from OS Python.

Docs: https://docs.blender.org/api/current/
Mental model:
  anatomy resolves Path → this module performs I/O there
  never trusts bpy.context.selected_objects as a pipeline address
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANATOMY_DIR = HERE.parent / "stage_0020_anatomy"
sys.path.insert(0, str(ANATOMY_DIR))

from node_002_contracts import WorkContext, snippet_dummy_context  # noqa: E402
from node_003_anatomy import (  # noqa: E402
    snippet_assert_under_shot,
    snippet_ensure_shot_tree,
    snippet_export_path,
    snippet_import_ref_dir,
    snippet_workfile_path,
)

# ---------------------------------------------------------------------------
# MIND MAP
# ---------------------------------------------------------------------------
#
# snippet_has_bpy()
# snippet_load_workfile(ctx)   → open or prepare path
# snippet_save_workfile(ctx)   → .blend at work/blender/
# snippet_export(ctx, fmt)     → export/{fmt}/…
# snippet_import(ctx, path)    → bring file into scene (or verify stub)
#


def snippet_has_bpy() -> bool:
    try:
        import bpy  # noqa: F401

        return True
    except ImportError:
        return False


def _write_stub(path: Path, label: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(f"STUB:{label}:{path.name}\n".encode("utf-8"))
    return path


def snippet_load_workfile(
    ctx: WorkContext | None = None,
    studio_root: Path | None = None,
) -> Path:
    """Open existing workfile, or leave path ready for first save."""
    ctx = ctx or snippet_dummy_context()
    snippet_ensure_shot_tree(ctx, studio_root)
    path = snippet_assert_under_shot(
        snippet_workfile_path(ctx, studio_root), ctx, studio_root
    )

    if snippet_has_bpy():
        import bpy

        if path.is_file():
            bpy.ops.wm.open_mainfile(filepath=str(path))
        # else: keep current/new file; save will create it
    return path


def snippet_save_workfile(
    ctx: WorkContext | None = None,
    studio_root: Path | None = None,
) -> Path:
    """Save versioned .blend under work/blender/. Stub outside Blender."""
    ctx = ctx or snippet_dummy_context()
    snippet_ensure_shot_tree(ctx, studio_root)
    path = snippet_assert_under_shot(
        snippet_workfile_path(ctx, studio_root), ctx, studio_root
    )
    path.parent.mkdir(parents=True, exist_ok=True)

    if snippet_has_bpy():
        import bpy

        bpy.ops.wm.save_as_mainfile(filepath=str(path))
    else:
        _write_stub(path, "blend")
    return path


def snippet_export(
    ctx: WorkContext | None = None,
    fmt: str = "abc",
    studio_root: Path | None = None,
) -> Path:
    """Export cache to export/{fmt}/. Uses bpy ops when available; else stub."""
    ctx = ctx or snippet_dummy_context()
    snippet_ensure_shot_tree(ctx, studio_root)
    fmt_l = fmt.lower()
    path = snippet_assert_under_shot(
        snippet_export_path(ctx, fmt_l, studio_root), ctx, studio_root
    )
    path.parent.mkdir(parents=True, exist_ok=True)

    if snippet_has_bpy():
        import bpy

        if fmt_l == "abc":
            # Alembic export — API name varies by Blender build; fail loud if missing
            if not hasattr(bpy.ops.wm, "alembic_export"):
                raise RuntimeError("bpy.ops.wm.alembic_export not available in this Blender")
            bpy.ops.wm.alembic_export(filepath=str(path))
        elif fmt_l == "fbx":
            if not hasattr(bpy.ops.export_scene, "fbx"):
                raise RuntimeError("bpy.ops.export_scene.fbx not available in this Blender")
            bpy.ops.export_scene.fbx(filepath=str(path))
        else:
            raise ValueError(f"unsupported export fmt: {fmt_l}")
    else:
        _write_stub(path, f"export_{fmt_l}")
    return path


def snippet_import_file(
    ctx: WorkContext | None = None,
    source: Path | None = None,
    fmt: str = "abc",
    studio_root: Path | None = None,
) -> Path:
    """
    Import a file into the scene (bpy) or verify stub exists (OS Python).
    Default source = last export path for fmt; else a file under import/ref/.
    """
    ctx = ctx or snippet_dummy_context()
    snippet_ensure_shot_tree(ctx, studio_root)
    fmt_l = fmt.lower()

    if source is None:
        source = snippet_export_path(ctx, fmt_l, studio_root)
    source = snippet_assert_under_shot(Path(source), ctx, studio_root)

    if not source.is_file():
        # allow importing a staged ref from import/ref/
        ref_dir = snippet_import_ref_dir(ctx, studio_root)
        candidate = ref_dir / source.name
        if candidate.is_file():
            source = candidate
        else:
            raise FileNotFoundError(
                f"import source missing: {source} (and no {candidate})"
            )

    if snippet_has_bpy():
        import bpy

        if fmt_l == "abc":
            if not hasattr(bpy.ops.wm, "alembic_import"):
                raise RuntimeError("bpy.ops.wm.alembic_import not available in this Blender")
            bpy.ops.wm.alembic_import(filepath=str(source))
        elif fmt_l == "fbx":
            if not hasattr(bpy.ops.import_scene, "fbx"):
                raise RuntimeError("bpy.ops.import_scene.fbx not available in this Blender")
            bpy.ops.import_scene.fbx(filepath=str(source))
        else:
            raise ValueError(f"unsupported import fmt: {fmt_l}")
    # outside Blender: existence check is the contract exercise
    return source


if __name__ == "__main__":
    try:
        ctx = snippet_dummy_context()
        print("bpy:", "yes" if snippet_has_bpy() else "no (stub mode)")
        saved = snippet_save_workfile(ctx)
        exported = snippet_export(ctx, "abc")
        imported = snippet_import_file(ctx, exported, "abc")
        print("saved:", saved)
        print("exported:", exported)
        print("imported:", imported)
    except Exception as exc:  # noqa: BLE001 — learning cheat
        print(f"skip blender io: {exc}")
