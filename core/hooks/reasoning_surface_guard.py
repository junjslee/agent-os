#!/usr/bin/env python3
"""PreToolUse guard: high-impact ops require a recent Reasoning Surface.

Enforces the kernel rule `irreversible or high-blast-radius -> declare a
Reasoning Surface first` (kernel/CONSTITUTION.md, kernel/REASONING_SURFACE.md).

Behavior:
- Matches a high-impact pattern in Bash commands (git push, publish,
  migrations, cloud deletes, DB destructive SQL) or Write|Edit to irreversible
  files (lock files, secrets).
- Reads `.episteme/reasoning-surface.json` in the project cwd.
- A Surface is valid when: timestamp within SURFACE_TTL_SECONDS, has non-empty
  core_question, at least one unknown, and a disconfirmation field.
- Advisory by default (non-blocking). Block (exit 2) when the project contains
  `.episteme/strict-surface`.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


SURFACE_TTL_SECONDS = 30 * 60  # 30 minutes

HIGH_IMPACT_BASH = [
    (re.compile(r"\bgit\s+push\b"), "git push"),
    (re.compile(r"\bgit\s+merge\b(?!\s+--abort)"), "git merge"),
    (re.compile(r"\bnpm\s+publish\b"), "npm publish"),
    (re.compile(r"\byarn\s+publish\b"), "yarn publish"),
    (re.compile(r"\bpnpm\s+publish\b"), "pnpm publish"),
    (re.compile(r"\bpoetry\s+publish\b"), "poetry publish"),
    (re.compile(r"\bcargo\s+publish\b"), "cargo publish"),
    (re.compile(r"\btwine\s+upload\b"), "twine upload"),
    (re.compile(r"\bpip\s+install\b(?!.*--dry-run)"), "pip install"),
    (re.compile(r"\bpip\s+uninstall\b"), "pip uninstall"),
    (re.compile(r"\balembic\s+upgrade\b"), "alembic upgrade"),
    (re.compile(r"\bprisma\s+migrate\s+deploy\b"), "prisma migrate deploy"),
    (re.compile(r"\bterraform\s+apply\b"), "terraform apply"),
    (re.compile(r"\bterraform\s+destroy\b"), "terraform destroy"),
    (re.compile(r"\bkubectl\s+(?:delete|apply)\b"), "kubectl delete/apply"),
    (re.compile(r"\baws\s+s3\s+rm\b"), "aws s3 rm"),
    (re.compile(r"\bgcloud\b.*\bdelete\b"), "gcloud delete"),
    (re.compile(r"\bDROP\s+(?:TABLE|DATABASE|SCHEMA)\b", re.I), "SQL DROP"),
    (re.compile(r"\bTRUNCATE\s+TABLE\b", re.I), "SQL TRUNCATE"),
    (re.compile(r"\bgh\s+pr\s+merge\b"), "gh pr merge"),
    (re.compile(r"\bgh\s+release\s+create\b"), "gh release create"),
]

IRREVERSIBLE_WRITE_PATHS = (
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Pipfile.lock",
    "Cargo.lock",
    "go.sum",
)


def _tool_name(payload: dict) -> str:
    return str(payload.get("tool_name") or payload.get("toolName") or "").strip()


def _tool_input(payload: dict) -> dict:
    raw = payload.get("tool_input") or payload.get("toolInput") or {}
    return raw if isinstance(raw, dict) else {}


def _bash_command(payload: dict) -> str:
    ti = _tool_input(payload)
    return str(ti.get("command") or ti.get("cmd") or ti.get("bash_command") or "")


def _write_target(payload: dict) -> str:
    ti = _tool_input(payload)
    return str(ti.get("file_path") or ti.get("path") or ti.get("target_file") or "")


def _match_high_impact(tool_name: str, payload: dict) -> str | None:
    if tool_name == "Bash":
        cmd = _bash_command(payload)
        for pattern, label in HIGH_IMPACT_BASH:
            if pattern.search(cmd):
                return label
        return None
    if tool_name in {"Write", "Edit", "MultiEdit"}:
        target = _write_target(payload).replace("\\", "/")
        name = Path(target).name if target else ""
        for lock in IRREVERSIBLE_WRITE_PATHS:
            if name == lock:
                return f"edit {lock}"
        return None
    return None


def _read_surface(cwd: Path) -> dict | None:
    p = cwd / ".episteme" / "reasoning-surface.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _surface_age_seconds(surface: dict) -> int | None:
    ts = surface.get("timestamp")
    if not ts:
        return None
    try:
        if isinstance(ts, (int, float)):
            return int(time.time() - float(ts))
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(time.time() - dt.timestamp())
    except (ValueError, TypeError):
        return None


def _surface_missing_fields(surface: dict) -> list[str]:
    missing: list[str] = []
    if not str(surface.get("core_question") or "").strip():
        missing.append("core_question")
    unknowns = surface.get("unknowns")
    if not isinstance(unknowns, list) or not any(str(u).strip() for u in unknowns):
        missing.append("unknowns")
    if not str(surface.get("disconfirmation") or "").strip():
        missing.append("disconfirmation")
    return missing


def _surface_status(cwd: Path) -> tuple[str, str]:
    surface = _read_surface(cwd)
    if surface is None:
        return "missing", "no .episteme/reasoning-surface.json found"
    age = _surface_age_seconds(surface)
    if age is None:
        return "invalid", "surface has no parseable timestamp"
    if age > SURFACE_TTL_SECONDS:
        mins = age // 60
        return "stale", f"surface is {mins} minute(s) old (TTL {SURFACE_TTL_SECONDS // 60} min)"
    missing = _surface_missing_fields(surface)
    if missing:
        return "incomplete", f"surface missing required fields: {', '.join(missing)}"
    return "ok", ""


def _write_audit(tool: str, op: str, cwd: Path, status: str, action: str, strict: bool) -> None:
    audit_path = Path.home() / ".episteme" / "audit.jsonl"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": tool,
        "op": op,
        "cwd": str(cwd),
        "status": status,
        "action": action,
        "strict": strict,
    }
    try:
        with open(audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass  # Audit failure must never block operations


def _surface_template() -> str:
    return (
        "Write .episteme/reasoning-surface.json with:\n"
        "{\n"
        '  "timestamp": "<ISO-8601 UTC>",\n'
        '  "core_question": "<one question this work answers>",\n'
        '  "knowns": ["..."],\n'
        '  "unknowns": ["..."],\n'
        '  "assumptions": ["..."],\n'
        '  "disconfirmation": "<what evidence would prove this wrong>"\n'
        "}"
    )


def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    tool_name = _tool_name(payload)
    label = _match_high_impact(tool_name, payload)
    if not label:
        return 0

    cwd = Path(payload.get("cwd") or os.getcwd())
    status, detail = _surface_status(cwd)
    strict = (cwd / ".episteme" / "strict-surface").exists()

    if status == "ok":
        _write_audit(tool_name, label, cwd, status, "passed", strict)
        return 0

    header = f"REASONING SURFACE {status.upper()}: high-impact op `{label}` with {detail}."
    instruction = _surface_template()

    if strict:
        _write_audit(tool_name, label, cwd, status, "blocked", strict)
        sys.stderr.write(
            f"{header}\nBlocked by strict-surface mode.\n{instruction}\n"
        )
        return 2

    _write_audit(tool_name, label, cwd, status, "advisory", strict)
    advisory = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                f"{header} Declare a Reasoning Surface before proceeding. {instruction}"
            ),
        }
    }
    sys.stdout.write(json.dumps(advisory))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
