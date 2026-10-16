"""
node_004_shows — per-show YAML catalog (software request matrix)

Show YAML is the contract artists/tools read; Kitsu stays tracking SoT.
"""

from __future__ import annotations

from pathlib import Path

from node_002_contracts import ShowEnv, snippet_demo_show
from node_003_packages_repo import snippet_rez_root

# Prefer PyYAML when present; otherwise minimal dump/load for our show files.
try:
    import yaml as _yaml

    _HAS_YAML = True
except ImportError:  # pragma: no cover
    _HAS_YAML = False


def snippet_shows_dir(rez_root: Path | None = None) -> Path:
    return (rez_root or snippet_rez_root()) / "shows"


def snippet_show_path(code: str, rez_root: Path | None = None) -> Path:
    return snippet_shows_dir(rez_root) / f"{code.upper()}.yaml"


def _dump_yaml(data: dict) -> str:
    if _HAS_YAML:
        return _yaml.safe_dump(data, sort_keys=False, default_flow_style=False)
    # minimal fallback
    lines = [
        f"code: {data['code']}",
        f"name: {data['name']}",
        f"description: {data.get('description', '')}",
        "requests:",
    ]
    for req in data.get("requests", []):
        lines.append(f"  - {req}")
    return "\n".join(lines) + "\n"


def _load_yaml(text: str) -> dict:
    if _HAS_YAML:
        data = _yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            raise ValueError("show YAML must be a mapping")
        return data
    # tiny parser for our own dumps
    out: dict = {"requests": []}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            out["requests"].append(line[2:].strip())
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip()
            if key != "requests":
                out[key] = val
    return out


def snippet_write_show(show: ShowEnv, rez_root: Path | None = None) -> Path:
    path = snippet_show_path(show.code, rez_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_dump_yaml(show.as_dict()), encoding="utf-8")
    return path


def snippet_load_show(code: str, rez_root: Path | None = None) -> ShowEnv:
    path = snippet_show_path(code, rez_root)
    if not path.is_file():
        raise FileNotFoundError(
            f"show YAML missing: {path} — run bootstrap first"
        )
    data = _load_yaml(path.read_text(encoding="utf-8"))
    return ShowEnv(
        code=str(data["code"]),
        name=str(data.get("name", data["code"])),
        description=str(data.get("description", "")),
        requests=[str(r) for r in data.get("requests", [])],
    )


def snippet_list_shows(rez_root: Path | None = None) -> list[str]:
    folder = snippet_shows_dir(rez_root)
    if not folder.is_dir():
        return []
    return sorted(p.stem for p in folder.glob("*.yaml"))


def snippet_bootstrap_show(rez_root: Path | None = None) -> Path:
    return snippet_write_show(snippet_demo_show(), rez_root)


if __name__ == "__main__":
    path = snippet_bootstrap_show()
    show = snippet_load_show("DUMY")
    print("wrote", path)
    print(show.code, show.requests)
