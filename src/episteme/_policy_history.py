"""Operator-policy section-change history — Cognitive Arm A · Item 2
(CP-TEMPORAL-INTEGRITY-EXPANSION-01; Event 83).

Append-only hash-chained record of edits to the operator-authored policy
files (cognitive_profile.md, workflow_policy.md, agent_feedback.md).
Lives at ``~/.episteme/memory/reflective/policy_history.jsonl`` and uses
the existing CP7 ``cp7-chained-v1`` envelope (see ``core/hooks/_chain.py``).

## Why this exists

Item 1 (Event 82, ``_profile_history.py``) covers axis-level changes to
``operator_profile.md``. The OTHER three operator-authored policy files
(``cognitive_profile.md``, ``workflow_policy.md``, ``agent_feedback.md``)
are also temporal source-of-truth — operators evolve their decision
protocol, workflow rules, and agent-learned feedback over time. When
edited in-place, the trajectory is lost.

This module covers section-level changes to those 3 files using the same
supersede-with-history pattern as Item 1.

## Schema

Single payload type:

```
{"type": "policy_change",
 "file_name": "<one of cognitive_profile / workflow_policy / agent_feedback>",
 "section":   "<free-form section name; e.g., 'Decision Engine'>",
 "old_content": "<free-form before-state description>",
 "new_content": "<free-form after-state description>",
 "reason":      "<≥15 chars, no lazy tokens>",
 "recorded_at": "<ISO-8601 UTC>",
 "recorder":    "<operator-id>",
 "evidence_refs": ["Event 65", ...]}
```

``file_name`` is enum-strict (3 valid values). ``section`` is free-form
because these files don't have a strict schema like operator_profile.md's
16-axis enumeration. ``old_content`` / ``new_content`` are free-form
description strings — operators record the SHAPE of the change, not
necessarily the full section text (which would bloat the chain).

## Validation discipline

- ``file_name`` must be one of the 3 valid policy files.
- ``section`` must be a non-empty string.
- ``reason`` must be ≥ 15 chars + must NOT match the lazy-token list
  (mirrors ``_profile_history.py`` discipline).

Spec: ``~/episteme-private/docs/cp-v1.1-architectural.md``
§ CP-TEMPORAL-INTEGRITY-EXPANSION-01 Item 2.
"""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_CORE_HOOKS_DIR = _REPO_ROOT / "core" / "hooks"
if str(_CORE_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_HOOKS_DIR))

import _chain  # type: ignore  # pyright: ignore[reportMissingImports]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


DEFAULT_REFLECTIVE_DIR = Path.home() / ".episteme" / "memory" / "reflective"
HISTORY_FILENAME = "policy_history.jsonl"


# Valid policy files. ``operator_profile`` is excluded — Item 1 covers
# its axis-level changes via ``_profile_history.py``.
VALID_POLICY_FILES: frozenset[str] = frozenset({
    "cognitive_profile",
    "workflow_policy",
    "agent_feedback",
})


# Mirrors `_profile_history.LAZY_REASON_TOKENS` (which mirrors
# `_profile_audit_ack.py`). Reason validation is consistent across all
# reflective-tier records.
LAZY_REASON_TOKENS: frozenset[str] = frozenset({
    "n/a", "na", "tbd", "todo",
    "none", "nothing", "nil", "null",
    "ack", "acked", "acknowledged",
    "ok", "okay", "fine",
    "later", "fix later", "do later", "address later",
    "wip", "in progress",
    "해당 없음", "없음", "없다", "추후", "나중에",
})

MIN_REASON_CHARS = 15


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_file_name(file_name) -> None:
    """Reject empty / non-string / non-enum file_name. Strict against the
    3-file enumeration."""
    if not isinstance(file_name, str):
        raise ValueError("file_name must be a string")
    stripped = file_name.strip()
    if not stripped:
        raise ValueError("file_name must be a non-empty string")
    if stripped not in VALID_POLICY_FILES:
        raise ValueError(
            f"unknown file_name {file_name!r}. Must be one of: "
            f"{sorted(VALID_POLICY_FILES)}. "
            f"Use `episteme history policy --list` to see valid files."
        )


def validate_section(section) -> None:
    """``section`` is free-form; only require non-empty string. The section
    name comes from the file's actual section structure (e.g., 'Decision
    Engine' in cognitive_profile.md)."""
    if not isinstance(section, str):
        raise ValueError("section must be a string")
    if not section.strip():
        raise ValueError("section must be a non-empty string")


def validate_reason(text) -> None:
    """Lazy-token + min-char rejection. Mirrors validate_rationale from
    _profile_audit_ack.py and validate_reason from _profile_history.py."""
    if not isinstance(text, str):
        raise ValueError("reason must be a string")
    stripped = text.strip()
    lowered = stripped.lower()
    for token in LAZY_REASON_TOKENS:
        if lowered == token.lower():
            raise ValueError(
                f"reason matches lazy-token {token!r}. "
                f"Provide a substantive reason — what triggered the change?"
            )
    if len(stripped) < MIN_REASON_CHARS:
        raise ValueError(
            f"reason must be at least {MIN_REASON_CHARS} characters; "
            f"got {len(stripped)}. Provide a substantive reason."
        )


def _validate_content(value, field_name: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    # Empty strings ARE allowed — represent "section did not exist before"
    # (new section) or "section was deleted" (removal).


# ---------------------------------------------------------------------------
# Recorder identity (same pattern as _profile_history.py + _profile_audit_ack.py)
# ---------------------------------------------------------------------------


def _resolve_recorder() -> str:
    explicit = os.environ.get("EPISTEME_RECORDER", "").strip()
    if explicit:
        return explicit
    user = os.environ.get("USER", "").strip()
    if user:
        return user
    try:
        result = subprocess.run(
            ["git", "config", "--get", "user.name"],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def _resolve_path(reflective_dir: Path | None = None) -> Path:
    base = reflective_dir or DEFAULT_REFLECTIVE_DIR
    return base / HISTORY_FILENAME


# ---------------------------------------------------------------------------
# Write path
# ---------------------------------------------------------------------------


def record_change(
    file_name: str,
    section: str,
    old_content: str,
    new_content: str,
    reason: str,
    *,
    evidence_refs: Iterable[str] | None = None,
    recorder: str | None = None,
    reflective_dir: Path | None = None,
    _now: datetime | None = None,  # test seam
) -> dict:
    """Append a ``policy_change`` envelope and return the chain envelope.

    Raises ValueError on invalid file_name / section / reason / non-string
    content.
    """
    validate_file_name(file_name)
    validate_section(section)
    _validate_content(old_content, "old_content")
    _validate_content(new_content, "new_content")
    validate_reason(reason)
    now = _now or datetime.now(timezone.utc)

    payload = {
        "type": "policy_change",
        "file_name": file_name,
        "section": section.strip(),
        "old_content": old_content,
        "new_content": new_content,
        "reason": reason.strip(),
        "recorded_at": now.isoformat(),
        "recorder": recorder or _resolve_recorder(),
        "evidence_refs": list(evidence_refs) if evidence_refs else [],
    }
    return _chain.append(_resolve_path(reflective_dir), payload)


# ---------------------------------------------------------------------------
# Read paths
# ---------------------------------------------------------------------------


def walk_file_history(
    file_name: str,
    *,
    section: str | None = None,
    reflective_dir: Path | None = None,
) -> list[dict]:
    """Return all envelopes for ``file_name`` in chronological order.
    If ``section`` is provided, filter to that section only."""
    validate_file_name(file_name)
    if section is not None:
        validate_section(section)
    path = _resolve_path(reflective_dir)
    if not path.exists():
        return []

    entries: list[dict] = []
    for envelope in _chain.iter_records(path, verify=True):
        payload = envelope.get("payload", {})
        if not isinstance(payload, dict):
            continue
        if payload.get("type") != "policy_change":
            continue
        if payload.get("file_name") != file_name:
            continue
        if section is not None and payload.get("section") != section:
            continue
        entries.append(envelope)
    return entries


def list_files_with_history(*, reflective_dir: Path | None = None) -> set[str]:
    """Return set of file_names that have at least one recorded change."""
    path = _resolve_path(reflective_dir)
    if not path.exists():
        return set()
    files: set[str] = set()
    for envelope in _chain.iter_records(path, verify=True):
        payload = envelope.get("payload", {})
        if not isinstance(payload, dict):
            continue
        if payload.get("type") != "policy_change":
            continue
        f = payload.get("file_name")
        if isinstance(f, str):
            files.add(f)
    return files


# ---------------------------------------------------------------------------
# Chain verification
# ---------------------------------------------------------------------------


def verify_chain(reflective_dir: Path | None = None):
    return _chain.verify_chain(_resolve_path(reflective_dir))
