#!/usr/bin/env python3
"""PostToolUse context monitor for episteme.

Uses Claude statusline bridge files (/tmp/claude-ctx-<session>.json) when available
and emits non-blocking warnings to keep execution bounded near compaction limits.
"""
from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
import sys

WARNING_THRESHOLD = 35  # remaining percentage
CRITICAL_THRESHOLD = 25
STALE_SECONDS = 90
DEBOUNCE_CALLS = 5


def _safe_session_id(raw: str) -> str:
    cleaned = "".join(ch for ch in (raw or "") if ch.isalnum() or ch in {"-", "_", "."})
    return cleaned[:128]


def _state_file(session_id: str) -> Path:
    return Path(tempfile.gettempdir()) / f"episteme-ctx-warn-{session_id}.json"


def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    session_id = _safe_session_id(str(payload.get("session_id") or "").strip())
    if not session_id:
        return 0

    bridge = Path(tempfile.gettempdir()) / f"claude-ctx-{session_id}.json"
    if not bridge.exists():
        return 0

    try:
        metrics = json.loads(bridge.read_text(encoding="utf-8"))
    except Exception:
        return 0

    ts = int(metrics.get("timestamp") or 0)
    now = int(time.time())
    if ts and (now - ts) > STALE_SECONDS:
        return 0

    remaining = metrics.get("remaining_percentage")
    used_pct = metrics.get("used_pct")
    if remaining is None:
        return 0

    try:
        remaining = float(remaining)
        used_pct = float(used_pct if used_pct is not None else (100 - remaining))
    except Exception:
        return 0

    if remaining > WARNING_THRESHOLD:
        return 0

    state_path = _state_file(session_id)
    state = {"calls_since_warn": 0, "last_level": None}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            state = {"calls_since_warn": 0, "last_level": None}

    state["calls_since_warn"] = int(state.get("calls_since_warn", 0)) + 1

    level = "critical" if remaining <= CRITICAL_THRESHOLD else "warning"
    escalated = level == "critical" and state.get("last_level") == "warning"
    if state["calls_since_warn"] < DEBOUNCE_CALLS and not escalated:
        state_path.write_text(json.dumps(state), encoding="utf-8")
        return 0

    state["calls_since_warn"] = 0
    state["last_level"] = level
    state_path.write_text(json.dumps(state), encoding="utf-8")

    if level == "critical":
        msg = (
            f"CONTEXT CRITICAL: usage {used_pct:.0f}% (remaining {remaining:.0f}%). "
            "Do not start new complex work; close loop and update docs/NEXT_STEPS.md before compaction."
        )
    else:
        msg = (
            f"CONTEXT WARNING: usage {used_pct:.0f}% (remaining {remaining:.0f}%). "
            "Prefer finishing current bounded task and avoid broad new exploration."
        )

    out = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": msg,
        }
    }
    sys.stdout.write(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
