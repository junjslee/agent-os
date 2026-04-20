#!/usr/bin/env python3
"""PostToolUse hook: track files the agent writes/modifies across calls.

Purpose: close the write-then-execute bypass vector. A single PreToolUse
hook is stateless — it cannot remember that a prior `Write` or prior `Bash`
call produced the very file this call is about to execute. This tracker
persists that memory to disk so `reasoning_surface_guard.py` can deep-scan
agent-written files at execute time.

State store: `~/.episteme/state/session_context.json`
Schema v1:
    {
      "version": 1,
      "entries": {
        "<abs_path>": {
          "sha256": "<hex>",
          "ts": "<ISO-8601 UTC>",
          "tool": "Write|Edit|MultiEdit|Bash",
          "source": "direct|redirect|tee"
        }
      }
    }

Tracked inputs:
    * `Write` / `Edit` / `MultiEdit` → `tool_input.file_path` (if it has a
      tracked extension or is extension-less, i.e. a likely shell script).
    * `Bash` → redirect targets parsed out of the command text:
      `> X`, `>> X`, `| tee [-a] X`. Heredocs with variable terminators are
      *not* parsed; that gap is documented in the changelog.

Entries older than TTL_SECONDS are purged on every write so the store
does not grow unbounded.

Concurrency: exclusive `fcntl.flock` on a sibling lock file when `fcntl`
is available (POSIX); the state file itself is replaced atomically via
temp+rename. On Windows (no `fcntl`) or exotic filesystems where locking
fails, the tracker degrades to last-write-wins rather than blocking.

Any exception → return 0. This hook must never block a tool call.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import fcntl  # POSIX-only; absent on Windows.
except ImportError:
    fcntl = None  # type: ignore[assignment]


STATE_VERSION = 1
TTL_SECONDS = 24 * 3600  # 24h rolling window

# Cap hash input so a pathologically large file cannot stall the hook.
MAX_HASH_BYTES = 256 * 1024

# Extensions we consider "executable-interesting" for deep-scan coverage.
# Extension-less files are also tracked when the Write tool creates them —
# they are frequently shell scripts without a `.sh` suffix.
TRACKED_EXTS = frozenset({
    ".sh", ".bash", ".zsh", ".ksh",
    ".py", ".pyw",
    ".js", ".mjs", ".cjs", ".ts",
    ".rb", ".pl", ".php",
})

# Best-effort redirect-target parsers. Complex shell quoting and heredocs
# will slip; that tradeoff is accepted for v0.10.0-alpha.
_REDIRECT_STDOUT = re.compile(r"(?:^|[\s;&|])>>?\s*([^\s;&|<>]+)")
_REDIRECT_TEE = re.compile(r"\|\s*tee\s+(?:-a\s+)?([^\s;&|<>]+)")


def _tool_name(payload: dict) -> str:
    return str(payload.get("tool_name") or payload.get("toolName") or "").strip()


def _tool_input(payload: dict) -> dict:
    raw = payload.get("tool_input") or payload.get("toolInput") or {}
    return raw if isinstance(raw, dict) else {}


def _cwd(payload: dict) -> Path:
    return Path(payload.get("cwd") or os.getcwd())


def _state_path() -> Path:
    return Path.home() / ".episteme" / "state" / "session_context.json"


def _resolve(cwd: Path, raw: str) -> Path | None:
    cleaned = raw.strip().strip('"').strip("'")
    if not cleaned:
        return None
    try:
        p = Path(cleaned) if Path(cleaned).is_absolute() else (cwd / cleaned)
        return p.resolve(strict=False)
    except (OSError, RuntimeError):
        return None


def _should_track(path: Path) -> bool:
    suffix = path.suffix.lower()
    if suffix in TRACKED_EXTS:
        return True
    return suffix == ""  # extension-less: frequently shell scripts


def _sha256_of_file(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            h.update(f.read(MAX_HASH_BYTES))
        return h.hexdigest()
    except OSError:
        return None


def _load_state(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        if isinstance(obj, dict) and isinstance(obj.get("entries"), dict):
            return obj
    except (OSError, json.JSONDecodeError):
        pass
    return {"version": STATE_VERSION, "entries": {}}


def _purge_stale(state: dict, now: datetime) -> None:
    fresh: dict = {}
    for k, v in state.get("entries", {}).items():
        ts = v.get("ts") if isinstance(v, dict) else None
        if not isinstance(ts, str):
            continue
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if (now - dt).total_seconds() <= TTL_SECONDS:
            fresh[k] = v
    state["entries"] = fresh


def _atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(data)
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass
    os.replace(tmp, path)


def _update_state(adds: list[tuple[Path, str, str]]) -> None:
    if not adds:
        return
    path = _state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lockfile = path.with_suffix(".lock")
    with open(lockfile, "a+") as lf:
        if fcntl is not None:
            try:
                fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
            except OSError:
                pass  # degrade to last-write-wins
        # else: Windows — no advisory locking; same degrade path.
        state = _load_state(path)
        now = datetime.now(timezone.utc)
        _purge_stale(state, now)
        for p, tool, source in adds:
            sha = _sha256_of_file(p)
            if sha is None:
                continue
            state["entries"][str(p)] = {
                "sha256": sha,
                "ts": now.isoformat(),
                "tool": tool,
                "source": source,
            }
        state["version"] = STATE_VERSION
        _atomic_write(path, json.dumps(state, ensure_ascii=False, indent=2) + "\n")


def _record_write(tool: str, payload: dict) -> None:
    ti = _tool_input(payload)
    fp = ti.get("file_path") or ti.get("path") or ti.get("target_file")
    if not isinstance(fp, str) or not fp:
        return
    cwd = _cwd(payload)
    resolved = _resolve(cwd, fp)
    if resolved is None or not resolved.exists() or not resolved.is_file():
        return
    if not _should_track(resolved):
        return
    _update_state([(resolved, tool, "direct")])


def _parse_redirect_targets(cmd: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for m in _REDIRECT_STDOUT.finditer(cmd):
        raw = m.group(1)
        if raw.startswith("&"):  # fd redirect like 2>&1
            continue
        out.append((raw, "redirect"))
    for m in _REDIRECT_TEE.finditer(cmd):
        out.append((m.group(1), "tee"))
    return out


def _record_bash(payload: dict) -> None:
    ti = _tool_input(payload)
    cmd = str(ti.get("command") or ti.get("cmd") or ti.get("bash_command") or "")
    if not cmd:
        return
    targets = _parse_redirect_targets(cmd)
    if not targets:
        return
    cwd = _cwd(payload)
    adds: list[tuple[Path, str, str]] = []
    for raw, source in targets:
        resolved = _resolve(cwd, raw)
        if resolved is None or not resolved.exists() or not resolved.is_file():
            continue
        if not _should_track(resolved):
            continue
        adds.append((resolved, "Bash", source))
    _update_state(adds)


def main() -> int:
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            return 0
        payload = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        return 0

    try:
        tool = _tool_name(payload)
        if tool in {"Write", "Edit", "MultiEdit"}:
            _record_write(tool, payload)
        elif tool == "Bash":
            _record_bash(payload)
    except Exception:
        pass  # never block on tracker failure
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
