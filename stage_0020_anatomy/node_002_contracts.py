"""
node_002_contracts — path tokens for the dummy show (stage_0020)

Mental model:
  WorkContext = named production tokens + version.
  Anatomy helpers turn this into paths. No network, no bpy, no DB.

Dummy defaults match the stage briefing: DUMY / SEQ010 / SH010 / modeling / v001.
"""

from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# MIND MAP
# ---------------------------------------------------------------------------
#
# WorkContext
# ├── project_code / project_name
# ├── sequence / shot
# ├── task          # e.g. modeling — drives workfile stem
# ├── version       # int → v001 in filenames
# └── variant       # optional token between task and version
#
# Naming rule:
#   {projectCode}_{entityCode}_{task}[_variant]_v{###}.{ext}
#


@dataclass(frozen=True)
class WorkContext:
    """Production tokens used to resolve disk paths. Resolve by these — not UI."""

    project_code: str = "DUMY"
    project_name: str = "Dummy Show"
    sequence: str = "SEQ010"
    shot: str = "SH010"
    task: str = "modeling"
    version: int = 1
    variant: str | None = None

    def version_token(self) -> str:
        """v001, v002, … — always zero-padded to 3."""
        if self.version < 1:
            raise ValueError(f"version must be >= 1, got {self.version}")
        return f"v{self.version:03d}"

    def entity_code(self) -> str:
        """Shot (or later asset) code used in filenames."""
        return self.shot

    def file_stem(self) -> str:
        """Filename without extension."""
        parts = [self.project_code, self.entity_code(), self.task]
        if self.variant:
            parts.append(self.variant)
        parts.append(self.version_token())
        return "_".join(parts)

    def filename(self, ext: str) -> str:
        """ext without or with leading dot — normalized."""
        clean = ext.lstrip(".")
        return f"{self.file_stem()}.{clean}"


def snippet_dummy_context(
    version: int = 1,
    task: str = "modeling",
    variant: str | None = None,
) -> WorkContext:
    """Canonical learning show — change version/task only when testing bumps."""
    return WorkContext(version=version, task=task, variant=variant)


if __name__ == "__main__":
    ctx = snippet_dummy_context()
    print("project:", ctx.project_code, ctx.project_name)
    print("entity:", ctx.sequence, ctx.shot, "task:", ctx.task)
    print("stem:", ctx.file_stem())
    print("blend:", ctx.filename("blend"))
    print("abc:", ctx.filename("abc"))
