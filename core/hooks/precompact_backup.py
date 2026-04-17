#!/usr/bin/env python3
"""PreCompact hook — backs up Claude session transcripts before compaction.

Copies .jsonl session files for the current project to
~/.cache/cognitive-os/backups/sessions/ with a timestamp prefix so compacted
history can be recovered. Writes outside the repo so transcripts never end
up tracked by git. Always exits 0.
"""
import datetime
import os
import shutil
from pathlib import Path


def encode_project_path(cwd: Path) -> str:
    """Mirror Claude Code's project directory encoding: replace / with -."""
    return str(cwd).replace("/", "-")


def _backup_root() -> Path:
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".cache"
    return base / "cognitive-os" / "backups" / "sessions"


def main() -> int:
    cwd = Path.cwd()
    encoded = encode_project_path(cwd)
    project_dir = Path.home() / ".claude" / "projects" / encoded

    if not project_dir.exists():
        return 0

    session_files = list(project_dir.glob("*.jsonl"))
    if not session_files:
        return 0

    backup_dir = _backup_root()
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    for sf in session_files:
        dest = backup_dir / f"{timestamp}_{sf.name}"
        shutil.copy2(sf, dest)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
