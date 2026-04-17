"""OMX adapter. Mounts agents, skills, and the Claude-format settings into
~/.omx if installed.
"""
from __future__ import annotations

import json

from .. import cli as _cli
from . import claude as _claude


def sync(governance_mode: str = "balanced") -> bool:
    omx_root = _cli.HOME / ".omx"
    if not omx_root.exists():
        return False

    for agent_file in (_cli.REPO_ROOT / "core" / "agents").glob("*.md"):
        _cli._copy_file(agent_file, omx_root / "agents" / agent_file.name)

    for skill_dir in _cli._managed_skills():
        _cli._copy_tree(skill_dir, omx_root / "skills" / skill_dir.name)

    settings = _claude.build_settings(governance_mode)
    _cli._write_text(
        omx_root / "settings.json",
        json.dumps(settings, indent=2) + "\n",
    )
    return True


__all__ = ["sync"]
