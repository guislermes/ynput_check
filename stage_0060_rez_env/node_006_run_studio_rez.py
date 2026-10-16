"""
node_006_run_studio_rez — bootstrap / list / resolve show software envs

Run via main.py:
  uv run python main.py rez
  uv run python main.py rez -- bootstrap
  uv run python main.py rez -- list
  uv run python main.py rez -- resolve DUMY
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from node_003_packages_repo import (  # noqa: E402
    snippet_bootstrap_packages,
    snippet_packages_path,
    snippet_rez_root,
)
from node_004_shows import (  # noqa: E402
    snippet_bootstrap_show,
    snippet_list_shows,
    snippet_load_show,
)
from node_005_resolve import snippet_resolve_show  # noqa: E402


def cmd_bootstrap() -> None:
    root = snippet_rez_root()
    print(f"rez_studio_root: {root}")
    written = snippet_bootstrap_packages(rez_root=root)
    show_path = snippet_bootstrap_show(rez_root=root)
    print(f"packages_path: {snippet_packages_path(root)}")
    for path in written:
        print(f"  package: {path / 'package.py'}")
    print(f"  show: {show_path}")
    print("ok — bootstrap idempotent; re-run anytime.")


def cmd_list() -> None:
    root = snippet_rez_root()
    codes = snippet_list_shows(root)
    if not codes:
        print("no shows — run: main.py rez -- bootstrap")
        return
    print(f"shows under {root / 'shows'}:")
    for code in codes:
        show = snippet_load_show(code, root)
        print(f"  {show.code}  ({show.name})")
        for req in show.requests:
            print(f"      - {req}")


def cmd_resolve(show_code: str) -> None:
    report = snippet_resolve_show(show_code)
    print("=== resolve report ===")
    for key in (
        "show",
        "mode",
        "packages_path",
        "requests",
        "resolved",
        "context_path",
        "command",
        "error",
    ):
        print(f"{key}: {report.get(key)}")
    if report.get("mode") != "resolved":
        print()
        print("TD tip: authoring packages does not need Rez;")
        print("        entering the env does. Install ASWF Rez, bind platform/os/python,")
        print("        then re-run resolve — or paste the command above.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Studio Rez product — shows + software packages.",
    )
    parser.add_argument(
        "action",
        nargs="?",
        default="bootstrap",
        choices=("bootstrap", "list", "resolve"),
        help="bootstrap (default) | list | resolve",
    )
    parser.add_argument(
        "show",
        nargs="?",
        default="DUMY",
        help="show code for resolve (default DUMY)",
    )
    args = parser.parse_args(argv)

    print("=== stage_0060 studio rez ===")
    print("tip: packages once on disk; contexts are computed — not a venv copy")
    print()

    if args.action == "bootstrap":
        cmd_bootstrap()
    elif args.action == "list":
        cmd_list()
    elif args.action == "resolve":
        # ensure files exist so resolve is friendly on first run
        root = snippet_rez_root()
        if not snippet_list_shows(root):
            cmd_bootstrap()
            print()
        cmd_resolve(args.show)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — learning cheat
        print(f"skip studio rez: {exc}")
        raise SystemExit(1) from exc
