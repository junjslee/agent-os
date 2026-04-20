#!/usr/bin/env python3
"""SessionStart hook — prints git status, NEXT_STEPS, and Reasoning Surface state.

Output appears at session open so Claude and the operator share the same
starting context without a manual paste.
"""
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


SURFACE_TTL_SECONDS = 30 * 60


def run(args: list[str]) -> str:
    r = subprocess.run(args, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def _profile_audit_line() -> str | None:
    """Return a re-elicitation prompt string from the latest unacknowledged
    profile-audit record, or None when nothing to surface.

    Phase 12 · D3 · re-elicitation not correction. This function only
    reads ~/.episteme/memory/reflective/profile_audit.jsonl; it never
    mutates the operator profile. Operator acks via
    `episteme profile audit ack <run_id>` (lands in a later checkpoint).

    Inlined rather than imported from src/episteme/_profile_audit.py —
    the session_context hook is invoked as a standalone script by the
    host runtime with no guaranteed sys.path setup. Matches the
    "hooks stay self-contained" convention used by reasoning_surface_guard.py
    and calibration_telemetry.py.
    """
    path = Path.home() / ".episteme" / "memory" / "reflective" / "profile_audit.jsonl"
    if not path.exists():
        return None
    last: str | None = None
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s:
                    last = s
    except OSError:
        return None
    if not last:
        return None
    try:
        record = json.loads(last)
    except json.JSONDecodeError:
        return None
    if not isinstance(record, dict):
        return None
    if record.get("acknowledged", False):
        return None
    drifts = [
        a for a in record.get("axes", [])
        if isinstance(a, dict) and a.get("verdict") == "drift"
    ]
    if not drifts:
        return None
    run_id = record.get("run_id", "unknown")
    if len(drifts) == 1:
        a = drifts[0]
        return (
            f"profile-audit: drift on {a.get('axis_name', '?')} — "
            f"{a.get('reason', 'see audit record')} "
            f"Re-elicit or ack via `episteme profile audit ack {run_id}`."
        )
    if len(drifts) <= 3:
        names = ", ".join(a.get("axis_name", "?") for a in drifts)
        return (
            f"profile-audit: drift on {names} — run "
            f"`episteme profile audit` for details. "
            f"Ack via `episteme profile audit ack {run_id}`."
        )
    return (
        f"profile-audit: drift on {len(drifts)} axes — run "
        f"`episteme profile audit` for details. "
        f"Ack via `episteme profile audit ack {run_id}`."
    )


def _surface_line() -> str | None:
    path = Path(".episteme/reasoning-surface.json")
    if not path.exists():
        return "surface: none declared — write .episteme/reasoning-surface.json before high-impact ops"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return "surface: unreadable .episteme/reasoning-surface.json"

    ts = data.get("timestamp")
    age: int | None = None
    if isinstance(ts, (int, float)):
        age = int(time.time() - float(ts))
    elif isinstance(ts, str) and ts:
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age = int(time.time() - dt.timestamp())
        except ValueError:
            age = None

    core_q = str(data.get("core_question") or "").strip() or "(none)"
    if age is None:
        return f"surface: present, no timestamp — core_question: {core_q}"
    if age > SURFACE_TTL_SECONDS:
        mins = age // 60
        return f"surface: STALE ({mins} min old) — refresh before high-impact ops"
    return f"surface: fresh — core_question: {core_q}"


def main() -> int:
    lines: list[str] = []

    # Git context
    if run(["git", "rev-parse", "--is-inside-work-tree"]):
        branch = run(["git", "branch", "--show-current"]) or "detached HEAD"
        status = run(["git", "status", "--short"])
        log = run(["git", "log", "--oneline", "-5"])

        lines.append(f"branch : {branch}")
        if status:
            lines.append(f"changes:\n{status}")
        else:
            lines.append("tree   : clean")
        if log:
            lines.append(f"log    :\n{log}")

    # HARNESS.md if present — tells the agent its operating constraints
    harness = Path("HARNESS.md")
    if harness.exists():
        h_content = harness.read_text().strip()
        if h_content:
            first_line = h_content.split("\n", 1)[0].strip("# ").strip()
            lines.append(f"harness: {first_line}")

    surface_line = _surface_line()
    if surface_line:
        lines.append(surface_line)

    # Phase 12 · profile-audit drift, when present and unacknowledged
    audit_line = _profile_audit_line()
    if audit_line:
        lines.append(audit_line)

    # NEXT_STEPS.md if present
    ns = Path("docs/NEXT_STEPS.md")
    if ns.exists():
        content = ns.read_text().strip()
        if content:
            lines.append(f"\n--- docs/NEXT_STEPS.md ---\n{content}")

    if lines:
        separator = "─" * 60
        print(f"\n{separator}")
        print("\n".join(lines))
        print(separator)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
