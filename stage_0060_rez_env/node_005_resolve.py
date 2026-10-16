"""
node_005_resolve — resolve a show env via Rez API, or print rez-env CLI

Fails loud on missing show YAML. Soft-degrades when Rez is not installed:
returns the exact command a TD would run after system Rez is available.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from node_003_packages_repo import snippet_packages_path, snippet_rez_root  # noqa: E402
from node_004_shows import snippet_load_show  # noqa: E402


def snippet_has_rez() -> bool:
    try:
        import rez  # noqa: F401

        return True
    except ImportError:
        return False


def snippet_rez_env_command(
    show_code: str,
    rez_root: Path | None = None,
) -> str:
    """Shell command equivalent — always available as the contract."""
    show = snippet_load_show(show_code, rez_root)
    root = rez_root or snippet_rez_root()
    packages = snippet_packages_path(root)
    reqs = " ".join(show.requests)
    # REZ_PACKAGES_PATH prepends our learning repo
    return (
        f'REZ_PACKAGES_PATH="{packages}" '
        f"rez-env {reqs}"
    )


def snippet_resolve_show(
    show_code: str,
    rez_root: Path | None = None,
    save_context: bool = True,
) -> dict[str, Any]:
    """
    Resolve show requests.
    Returns a report dict: mode, command, packages, context_path?, error?
    """
    root = rez_root or snippet_rez_root()
    show = snippet_load_show(show_code, root)
    packages_path = snippet_packages_path(root)
    command = snippet_rez_env_command(show_code, root)

    report: dict[str, Any] = {
        "show": show.code,
        "requests": list(show.requests),
        "packages_path": str(packages_path),
        "command": command,
        "mode": "cli-only",
        "resolved": [],
        "context_path": None,
        "error": None,
    }

    if not snippet_has_rez():
        report["error"] = (
            "rez not importable — packages/show files are ready; "
            "install ASWF Rez then re-run resolve, or use the printed command"
        )
        return report

    try:
        from rez.resolved_context import ResolvedContext

        # Learning stubs often lack platform/arch/os/python binds.
        # Try with add_implicit_packages=False so demo packages can resolve alone
        # when they only require each other; if that fails, surface the error.
        ctx = ResolvedContext(
            show.requests,
            package_paths=[str(packages_path)],
            add_implicit_packages=False,
        )
        if not ctx.success:
            report["mode"] = "resolve-failed"
            report["error"] = f"status={ctx.status}"
            return report

        report["mode"] = "resolved"
        report["resolved"] = [
            getattr(p, "qualified_package_name", str(p))
            for p in ctx.resolved_packages
        ]

        if save_context:
            ctx_dir = root / "contexts"
            ctx_dir.mkdir(parents=True, exist_ok=True)
            ctx_path = ctx_dir / f"{show.code}.rxt"
            ctx.save(str(ctx_path))
            report["context_path"] = str(ctx_path)
    except Exception as exc:  # noqa: BLE001 — report, don't hide
        report["mode"] = "resolve-error"
        report["error"] = str(exc)

    return report


if __name__ == "__main__":
    from node_003_packages_repo import snippet_bootstrap_packages
    from node_004_shows import snippet_bootstrap_show

    snippet_bootstrap_packages()
    snippet_bootstrap_show()
    info = snippet_resolve_show("DUMY")
    for key, value in info.items():
        print(f"{key}: {value}")
