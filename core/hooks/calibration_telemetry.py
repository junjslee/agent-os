#!/usr/bin/env python3
"""PostToolUse hook: record the observed exit_code for calibration telemetry.

Pairs with `reasoning_surface_guard.py`. The PreToolUse guard writes a
`prediction` record to `~/.episteme/telemetry/YYYY-MM-DD-audit.jsonl` when a
high-impact Bash command is allowed through. This hook fires after the same
tool call completes and appends the matching `outcome` record carrying the
exit code.

Join key: `correlation_id` — derived from `tool_use_id` when present,
otherwise a SHA-1 over (second-bucket, cwd, cmd) so the two hooks produce
the same id for the same call.

Records are append-only JSONL, local-only, and strictly opt-in to external
use. Episteme never transmits them; they exist so an operator can audit
whether their predicted disconfirmations actually fired.

This hook must never block. Any exception → return 0.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def _redact(cmd: str) -> str:
    """Crude secret-redaction — command_executed must not carry tokens.

    Inlined (not imported from episodic_writer) because the hook is invoked
    as a standalone script with no guaranteed sys.path. If this pattern set
    diverges from episodic_writer._redact, unify by editing both.
    """
    if not cmd:
        return cmd
    patterns = [
        (re.compile(r"(?i)((?:password|passwd|token|secret|api[_-]?key|bearer))(\s*[=:]\s*)\S+"),
         r"\1\2<REDACTED>"),
        (re.compile(r"AKIA[0-9A-Z]{16}"), "<REDACTED-AWS-KEY>"),
        (re.compile(r"(?i)ghp_[a-z0-9]{30,}"), "<REDACTED-GH-TOKEN>"),
    ]
    redacted = cmd
    for pat, repl in patterns:
        redacted = pat.sub(repl, redacted)
    return redacted


def _tool_name(payload: dict) -> str:
    return str(payload.get("tool_name") or payload.get("toolName") or "").strip()


def _tool_input(payload: dict) -> dict:
    raw = payload.get("tool_input") or payload.get("toolInput") or {}
    return raw if isinstance(raw, dict) else {}


def _bash_command(payload: dict) -> str:
    ti = _tool_input(payload)
    return str(ti.get("command") or ti.get("cmd") or ti.get("bash_command") or "")


def _extract_exit_code(payload: dict) -> int | None:
    """Walk the tool_response structure for a numeric exit code.

    Different runtimes spell this differently. This tries the common shapes
    and returns None if none match — the outcome record still carries a
    best-effort success/failure signal via `status`.
    """
    resp = payload.get("tool_response") or payload.get("toolResponse") or {}
    if not isinstance(resp, dict):
        return None
    for key in ("exit_code", "exitCode", "returncode", "return_code", "status_code"):
        v = resp.get(key)
        if isinstance(v, int):
            return v
        if isinstance(v, str) and v.strip().lstrip("-").isdigit():
            return int(v.strip())
    # Some runtimes nest under a `metadata` or `meta` key.
    for wrapper_key in ("metadata", "meta"):
        wrapper = resp.get(wrapper_key)
        if isinstance(wrapper, dict):
            for key in ("exit_code", "exitCode", "returncode", "return_code"):
                v = wrapper.get(key)
                if isinstance(v, int):
                    return v
    return None


def _extract_status(payload: dict) -> str:
    """Best-effort status string: 'success' / 'error' / 'unknown'."""
    resp = payload.get("tool_response") or payload.get("toolResponse") or {}
    if not isinstance(resp, dict):
        return "unknown"
    if "is_error" in resp:
        return "error" if resp["is_error"] else "success"
    if "error" in resp and resp["error"]:
        return "error"
    s = resp.get("status")
    if isinstance(s, str) and s:
        return s.lower()
    return "unknown"


def _correlation_id(payload: dict, cmd: str, ts: str) -> str:
    rid = payload.get("tool_use_id") or payload.get("toolUseId") or payload.get("request_id")
    if isinstance(rid, str) and rid.strip():
        return rid.strip()
    cwd = str(payload.get("cwd") or os.getcwd())
    bucket = ts.split(".")[0]
    seed = f"{bucket}|{cwd}|{cmd}".encode("utf-8", errors="replace")
    return "h_" + hashlib.sha1(seed).hexdigest()[:16]


def _telemetry_path(ts: str) -> Path:
    return Path.home() / ".episteme" / "telemetry" / f"{ts[:10]}-audit.jsonl"


def _write_telemetry(record: dict) -> None:
    try:
        path = _telemetry_path(record["ts"])
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except (OSError, KeyError):
        pass


def main() -> int:
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            return 0
        payload = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        return 0

    try:
        if _tool_name(payload) != "Bash":
            return 0
        cmd = _bash_command(payload)
        if not cmd:
            return 0
        ts = datetime.now(timezone.utc).isoformat()
        record = {
            "ts": ts,
            "event": "outcome",
            "correlation_id": _correlation_id(payload, cmd, ts),
            "tool": "Bash",
            "cwd": str(payload.get("cwd") or os.getcwd()),
            "command_executed": _redact(cmd),
            "exit_code": _extract_exit_code(payload),
            "status": _extract_status(payload),
        }
        _write_telemetry(record)
    except Exception:
        pass  # Never block on telemetry failure
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
