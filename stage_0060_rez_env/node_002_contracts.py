"""
node_002_contracts — show + software request shapes for Rez studio product

Mental model:
  SoftwareSpec  → becomes packages/{name}/{version}/package.py
  ShowEnv       → shows/{code}.yaml with a list of rez requests
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SoftwareSpec:
    """One installable/bindable unit in the packages repo."""

    name: str
    version: str
    description: str
    requires: tuple[str, ...] = ()
    tools: tuple[str, ...] = ()
    # env keys set in commands() — values may use {root}
    environ: tuple[tuple[str, str], ...] = ()
    pythonpath_append_root: bool = False
    path_append_bin: bool = False

    def request(self) -> str:
        """Exact-ish pin used in show YAML."""
        return f"{self.name}-{self.version}"


@dataclass
class ShowEnv:
    """Per-show software matrix — tracker-agnostic."""

    code: str
    name: str
    requests: list[str] = field(default_factory=list)
    description: str = ""

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "requests": list(self.requests),
        }


def snippet_demo_softwares() -> list[SoftwareSpec]:
    """Learning catalog — stubs that set env, not real vendor installs."""
    return [
        SoftwareSpec(
            name="python",
            version="3.13.0",
            description="Stub python package so local resolves need no rez-bind.",
            tools=("python",),
            environ=(("STUDIO_PYTHON_VERSION", "3.13.0"),),
            path_append_bin=True,
        ),
        SoftwareSpec(
            name="blender",
            version="4.2.0",
            description="Stub Blender package for learning Rez (bind real app later).",
            tools=("blender",),
            environ=(("BLENDER_VERSION", "4.2.0"),),
            path_append_bin=True,
        ),
        SoftwareSpec(
            name="pipeline_core",
            version="0.1.0",
            description="In-house pipeline helpers.",
            requires=("python-3.13+",),
            tools=("pipe-hello",),
            environ=(("PIPELINE_CORE_ROOT", "{root}"),),
            pythonpath_append_root=True,
            path_append_bin=True,
        ),
        SoftwareSpec(
            name="show_dumy",
            version="0.1.0",
            description="Show-level package for Dummy Show — roots + code.",
            requires=("pipeline_core-0.1+", "blender-4.2+"),
            environ=(
                ("SHOW_CODE", "DUMY"),
                ("SHOW_NAME", "Dummy Show"),
                ("SHOW_ROOT", "{root}"),
            ),
        ),
    ]


def snippet_demo_show() -> ShowEnv:
    return ShowEnv(
        code="DUMY",
        name="Dummy Show",
        description="Learning show — pins blender + pipeline + show package.",
        requests=[
            "show_dumy-0.1.0",
            "blender-4.2.0",
            "pipeline_core-0.1.0",
        ],
    )


if __name__ == "__main__":
    for soft in snippet_demo_softwares():
        print(soft.request(), "→", soft.description)
    show = snippet_demo_show()
    print("show", show.code, show.requests)
