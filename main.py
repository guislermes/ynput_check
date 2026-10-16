"""
ynput-check entry — run staged pipeline demos from the repo root.

Mental model:
  main.py chooses a stage → stage node runs the lesson
  default = full work loop (0020→0050 glue)

Examples:
  uv run python main.py
  uv run python main.py loop
  uv run python main.py anatomy
  uv run python main.py blender
  uv run python main.py kitsu
  uv run python main.py rez
  uv run python main.py rez -- bootstrap
  uv run python main.py rez -- resolve DUMY
  uv run python main.py --list
"""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# stage folder → runnable module path (relative to ROOT)
STAGES: dict[str, Path] = {
    "anatomy": ROOT / "stage_0020_anatomy" / "node_004_run_ensure_tree.py",
    "blender": ROOT / "stage_0030_blender_io" / "node_003_run_io_roundtrip.py",
    "kitsu": ROOT / "stage_0040_kitsu_context" / "node_003_run_task_context.py",
    "loop": ROOT / "stage_0050_work_loop" / "node_003_run_work_loop.py",
    "rez": ROOT / "stage_0060_rez_env" / "node_006_run_studio_rez.py",
}

ALIASES = {
    "0020": "anatomy",
    "0030": "blender",
    "0040": "kitsu",
    "0050": "loop",
    "0060": "rez",
    "all": "loop",
    "work": "loop",
    "software": "rez",
    "env": "rez",
}


def _load_stage_main(script: Path):
    """Load a stage run file and return its main() — keeps stages as the source of truth."""
    if not script.is_file():
        raise FileNotFoundError(f"stage script missing: {script}")

    stage_dir = script.parent
    if str(stage_dir) not in sys.path:
        sys.path.insert(0, str(stage_dir))

    spec = importlib.util.spec_from_file_location(script.stem, script)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "main"):
        raise AttributeError(f"{script.name} has no main()")
    return module.main


def _resolve_stage(name: str) -> str:
    key = name.lower().strip()
    key = ALIASES.get(key, key)
    if key not in STAGES:
        known = ", ".join(STAGES)
        raise SystemExit(f"unknown stage {name!r}. choose: {known}")
    return key


def _call_stage_main(run, stage_args: list[str]) -> None:
    """Pass argv through when the stage main accepts it (e.g. rez)."""
    try:
        sig = inspect.signature(run)
        params = list(sig.parameters.values())
    except (TypeError, ValueError):
        run()
        return

    if not params:
        run()
        return

    first = params[0]
    # main(argv: list[str] | None = None) style
    if first.name in {"argv", "args"} or first.kind == inspect.Parameter.VAR_POSITIONAL:
        run(stage_args if stage_args else None)
        return
    run()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run dummy studio pipeline stages "
            "(anatomy → blender → kitsu → loop → rez)."
        ),
    )
    parser.add_argument(
        "stage",
        nargs="?",
        default="loop",
        help="anatomy | blender | kitsu | loop | rez (default: loop)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list stages and exit",
    )
    parser.add_argument(
        "stage_args",
        nargs=argparse.REMAINDER,
        help="args passed to the stage (use: main.py rez -- resolve DUMY)",
    )
    args = parser.parse_args(argv)

    if args.list:
        print("stages:")
        for name, path in STAGES.items():
            print(f"  {name:8}  {path.relative_to(ROOT)}")
        return

    stage = _resolve_stage(args.stage)
    script = STAGES[stage]
    stage_args = list(args.stage_args)
    if stage_args and stage_args[0] == "--":
        stage_args = stage_args[1:]

    print(f"ynput-check → stage={stage}")
    print(f"  script: {script.relative_to(ROOT)}")
    if stage_args:
        print(f"  args: {' '.join(stage_args)}")
    print("  tip: resolve by path/id — selection is UX, not a contract")
    print()

    run = _load_stage_main(script)
    _call_stage_main(run, stage_args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — learning cheat
        print(f"skip main: {exc}")
        raise SystemExit(1) from exc
