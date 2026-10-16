"""
node_006_rez — Rez mind map (learn what Academy Software Foundation Rez does)

Install (system tool — not a normal app dependency):
  https://rez.readthedocs.io/en/stable/installation.html
  Typical: clone ASWF rez → python install.py -v DEST_DIR
  Then bind essentials: rez-bind platform && rez-bind arch && rez-bind os && rez-bind python

Docs:  https://rez.readthedocs.io/
API:   https://rez.readthedocs.io/en/stable/api/rez.resolved_context.html
Pkg:   https://rez.readthedocs.io/en/stable/package_definition.html

Mental model:
  Package repo on disk:  {packages_path}/{name}/{version}/package.py
  Request list          → dependency resolve → ResolvedContext
  Context               → env vars / PATH (does NOT copy apps into a venv)
  Same requests later   → reproducible environment (save/load context)

Rez configures environments dynamically. It is not conda/pip replacing site-packages.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# MIND MAP (API / CLI surface)
# ---------------------------------------------------------------------------
#
# CLI (studio daily drivers)
# ├── rez-bind          # wrap already-installed software as a package
# ├── rez-build         # build a developer package into the repo
# ├── rez-env REQ...    # resolve + enter shell (or run -- command)
# ├── rez-context       # inspect a saved .rxt context
# └── rez-search        # find packages in configured paths
#
# Python
# ├── rez.resolved_context.ResolvedContext(requests, package_paths=...)
# │     ├── success / status / resolved_packages / graph
# │     ├── get_resolve_as_str() / print_info()
# │     ├── save(path) / load(path)          # .rxt reproducibility
# │     ├── execute_shell(command=...)       # spawn configured shell
# │     └── get_environ()                    # dict of env for this context
# ├── rez.packages.get_latest_package / iter_packages
# ├── rez.package_maker.PackageMaker         # author packages in code (advanced)
# └── package.py attributes
#       name, version, description, authors, tools
#       requires = ["python-3.10+", "blender-4+"]
#       def commands(): env.PATH.append("{root}/bin"); env.PYTHONPATH.append(...)
#
# Request syntax (solver language)
#   "blender"           any version
#   "blender-4.2"       exact-ish family match rules per rez versioning
#   "blender-4.2+"      4.2 or newer
#   "python-3.10+<3.12" range
#   "!java-1.8+"        conflict / exclusion
#
# Studio layout (typical)
#   /packages/ext/...     vendor / bound apps
#   /packages/int/...     in-house tools
#   /packages/show/...    per-show override packages (optional)
#


def snippet_has_rez() -> bool:
    try:
        import rez  # noqa: F401

        return True
    except ImportError:
        return False


def snippet_package_py_example() -> str:
    """Canonical package.py shape — strings only; learn the file, not a class."""
    return '''\
name = "pipeline_core"

version = "0.1.0"

description = "In-house pipeline helpers for the dummy studio."

requires = [
    "python",
]

tools = [
    "pipe-hello",
]

def commands():
    env.PIPELINE_CORE_ROOT = "{root}"
    env.PYTHONPATH.append("{root}/python")
    env.PATH.append("{root}/bin")
'''


def snippet_resolve_context(
    requests: list[str] | None = None,
    package_paths: list[str] | None = None,
):
    """
    Resolve a context in-process. Needs a working Rez install + packages on disk.
    Fails loud if rez is missing — stage_0060 prints the equivalent rez-env command.
    """
    if not snippet_has_rez():
        raise ImportError(
            "rez is not importable. Install ASWF Rez into a dedicated prefix "
            "(see docs), then ensure that prefix's python/site-packages is on PYTHONPATH. "
            "Or use stage_0060 which can print `rez-env ...` without importing."
        )

    from rez.resolved_context import ResolvedContext

    requests = requests or ["python"]
    kwargs = {}
    if package_paths:
        kwargs["package_paths"] = package_paths

    ctx = ResolvedContext(requests, **kwargs)
    if not ctx.success:
        raise RuntimeError(f"resolve failed for {requests}: {ctx.status}")
    return ctx


def snippet_print_resolve(ctx) -> None:
    """Human dump of what the solver picked."""
    print("requests:", [str(r) for r in ctx.requested_packages])
    print("resolved:")
    for pkg in ctx.resolved_packages:
        # Package objects expose name/version/path depending on rez version
        print(f"  - {pkg.qualified_package_name} @ {pkg.base}")


def snippet_save_and_reload(ctx, path: str):
    """Pin a resolve to disk (.rxt) — Pipeline TD: never rely on 'latest' alone."""
    ctx.save(path)
    from rez.resolved_context import ResolvedContext

    return ResolvedContext.load(path)


def snippet_execute_command(ctx, command: str = "python --version"):
    """Run one command inside the resolved environ (non-interactive)."""
    import subprocess

    # execute_shell returns a Popen-like handle in many rez versions
    proc = ctx.execute_shell(command=command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return proc.returncode, out, err


def snippet_iter_packages(name: str = "python", package_paths: list[str] | None = None):
    """List versions of a package visible on package paths."""
    if not snippet_has_rez():
        raise ImportError("rez not importable")

    from rez.packages import iter_packages

    paths = package_paths
    for pkg in iter_packages(name, paths=paths):
        yield pkg


# ---------------------------------------------------------------------------
# CHEAT — graceful without system Rez
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Rez mental model: requests → resolve → env (no venv copy).")
    print("package.py example:\n")
    print(snippet_package_py_example())
    if snippet_has_rez():
        print("rez import: OK — try snippet_resolve_context(['python'])")
        try:
            ctx = snippet_resolve_context(["python"])
            snippet_print_resolve(ctx)
        except Exception as exc:  # noqa: BLE001 — learning cheat
            print(f"resolve skipped (bind packages / set paths): {exc}")
    else:
        print("rez import: MISSING — install ASWF Rez, or continue to stage_0060_rez_env")
        print("docs: https://rez.readthedocs.io/en/stable/installation.html")
