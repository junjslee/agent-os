#!/usr/bin/env python3
"""PreToolUse hook: snapshot watched-file content before Write/Edit/MultiEdit.

Cognitive Arm A auto-instrumentation (Event 91, CP-TEMPORAL-INTEGRITY-
EXPANSION-01 follow-up). Pairs with `_arm_a_post.py` via correlation_id.
The post hook reads the snapshot, reads the post-edit file, diffs, and
emits one `record_change` per detected delta.

Watched files (kernel canonicals at fixed offsets from kernel root):
- core/memory/global/operator_profile.md  → axis-level → profile_history
- core/memory/global/cognitive_profile.md → section-level → policy_history
- core/memory/global/workflow_policy.md   → section-level → policy_history
- core/memory/global/agent_feedback.md    → section-level → policy_history

Marker layout: ``~/.episteme/state/arm_a_pending/<correlation_id>.json``

```
{"version": 1,
 "correlation_id": "...",
 "written_at": "<ISO-8601 UTC>",
 "file_path": "<absolute path>",
 "file_kind": "profile" | "policy",
 "policy_basename": "cognitive_profile" | "workflow_policy" | "agent_feedback" | null,
 "pre_content": "<full file content or empty string for new files>"}
```

Never blocks. Any exception → return 0. Pre-edit bookkeeping must not
break the agent's tool execution path.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Watched files — canonical kernel paths
# ---------------------------------------------------------------------------

# Kernel root: this file is at <kernel>/core/hooks/_arm_a_pre.py
_KERNEL_ROOT = Path(__file__).resolve().parent.parent.parent
_GLOBAL_DIR = _KERNEL_ROOT / "core" / "memory" / "global"

PROFILE_PATH = (_GLOBAL_DIR / "operator_profile.md").resolve()
POLICY_FILES = {
    "cognitive_profile": (_GLOBAL_DIR / "cognitive_profile.md").resolve(),
    "workflow_policy": (_GLOBAL_DIR / "workflow_policy.md").resolve(),
    "agent_feedback": (_GLOBAL_DIR / "agent_feedback.md").resolve(),
}

# Marker TTL — same convention as fence_synthesis (1 hour). Stale markers
# get treated as absent on read.
MARKER_TTL_SECONDS = 3600


# ---------------------------------------------------------------------------
# Marker dir + atomic write (mirrors _fence_synthesis._atomic_write_json)
# ---------------------------------------------------------------------------


def _pending_dir() -> Path:
    return Path.home() / ".episteme" / "state" / "arm_a_pending"


def _atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".tmp-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Payload helpers (mirror existing PostToolUse hooks for shape compat)
# ---------------------------------------------------------------------------


def _tool_name(payload: dict) -> str:
    return str(payload.get("tool_name") or payload.get("toolName") or "").strip()


def _tool_input(payload: dict) -> dict:
    raw = payload.get("tool_input") or payload.get("toolInput") or {}
    return raw if isinstance(raw, dict) else {}


def _file_path_from_payload(payload: dict) -> str | None:
    ti = _tool_input(payload)
    fp = ti.get("file_path") or ti.get("filePath") or ti.get("path")
    if isinstance(fp, str) and fp.strip():
        return fp.strip()
    return None


def _candidate_correlation_ids(payload: dict, file_path: str) -> list[str]:
    """Return all candidate correlation ids — same Event 50 pattern as
    fence_synthesis: PreToolUse may lack tool_use_id while PostToolUse
    has it, so we write under EACH candidate so PostToolUse always finds
    a match.
    """
    out: list[str] = []
    seen: set[str] = set()
    rid = (
        payload.get("tool_use_id")
        or payload.get("toolUseId")
        or payload.get("request_id")
    )
    if isinstance(rid, str) and rid.strip():
        c = rid.strip()
        out.append(c)
        seen.add(c)
    # Stable SHA-1 fallback over (second-bucket, file_path) so the two
    # hooks compute the same id when tool_use_id is missing.
    ts = datetime.now(timezone.utc).isoformat()
    bucket = ts.split(".")[0]
    seed = f"{bucket}|{file_path}".encode("utf-8", errors="replace")
    h = "h_" + hashlib.sha1(seed).hexdigest()[:16]
    if h not in seen:
        out.append(h)
    return out


# ---------------------------------------------------------------------------
# File classification
# ---------------------------------------------------------------------------


def _classify(file_path: str) -> tuple[str, str | None] | None:
    """Return (file_kind, policy_basename) for a watched file, else None.

    file_kind: "profile" or "policy". policy_basename only set when
    file_kind == "policy"; one of cognitive_profile / workflow_policy /
    agent_feedback.
    """
    try:
        resolved = Path(file_path).resolve()
    except OSError:
        return None
    if resolved == PROFILE_PATH:
        return ("profile", None)
    for name, p in POLICY_FILES.items():
        if resolved == p:
            return ("policy", name)
    return None


# ---------------------------------------------------------------------------
# Hook log (matches episodic_writer convention)
# ---------------------------------------------------------------------------


def _hook_log_path() -> Path:
    return Path.home() / ".episteme" / "state" / "hooks.log"


def _log_line(msg: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    line = f"{ts} arm_a_pre {msg}\n"
    try:
        path = _hook_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        try:
            sys.stderr.write(line)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


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
        if tool not in ("Write", "Edit", "MultiEdit"):
            return 0
        file_path = _file_path_from_payload(payload)
        if not file_path:
            return 0
        classification = _classify(file_path)
        if classification is None:
            return 0
        file_kind, policy_basename = classification

        # Snapshot pre-content. Missing file (Write creating) = empty.
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                pre_content = f.read()
        except (OSError, UnicodeDecodeError):
            pre_content = ""

        candidates = _candidate_correlation_ids(payload, file_path)
        marker = {
            "version": 1,
            "correlation_id": candidates[0],
            "written_at": datetime.now(timezone.utc).isoformat(),
            "file_path": file_path,
            "file_kind": file_kind,
            "policy_basename": policy_basename,
            "pre_content": pre_content,
        }
        # Write under EACH candidate — Event 50 pattern.
        for cid in candidates:
            try:
                _atomic_write_json(_pending_dir() / f"{cid}.json", marker)
            except OSError:
                continue
        _log_line(
            f"snapshot: file={Path(file_path).name} kind={file_kind} "
            f"cids={candidates} pre_chars={len(pre_content)}"
        )
    except Exception as exc:  # pragma: no cover — defensive
        _log_line(f"EXCEPTION: {type(exc).__name__}: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
