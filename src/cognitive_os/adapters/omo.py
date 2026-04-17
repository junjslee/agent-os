"""OMO adapter. Mounts agents, skills, and the Claude-format settings into
~/.omo if installed.
"""
from __future__ import annotations

import json

from .. import cli as _cli
from . import claude as _claude


def sync(governance_mode: str = "balanced") -> bool:
    omo_root = _cli.HOME / ".omo"
    if not omo_root.exists():
        return False

    for agent_file in (_cli.REPO_ROOT / "core" / "agents").glob("*.md"):
        _cli._copy_file(agent_file, omo_root / "agents" / agent_file.name)

    for skill_dir in _cli._managed_skills():
        _cli._copy_tree(skill_dir, omo_root / "skills" / skill_dir.name)

    settings = _claude.build_settings(governance_mode)
    _cli._write_text(
        omo_root / "settings.json",
        json.dumps(settings, indent=2) + "\n",
    )
    return True


__all__ = ["sync"]
