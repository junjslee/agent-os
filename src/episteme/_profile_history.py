"""Operator-profile axis-change history — Cognitive Arm A · Item 1
(CP-TEMPORAL-INTEGRITY-EXPANSION-01 first slice; Event 82).

Append-only hash-chained record of operator-profile axis changes. Lives
at ``~/.episteme/memory/reflective/profile_history.jsonl`` and uses the
existing CP7 ``cp7-chained-v1`` envelope schema (see
``core/hooks/_chain.py``).

## Why this exists

The kernel's operator profile (`core/memory/global/operator_profile.md`)
encodes 16 cognitive-style axes as YAML in-place. When an axis is
re-elicited, inferred-to-elicited, or value-shifted, the OLD claim is
overwritten — the *trajectory* is lost. The Phase 12 audit detects
drift (axis-claim diverges from observed behavior); the operator
re-elicits or revises; but the journey from old-claim to new-claim has
historically been preserved only in the axis's `note` field as prose,
which doesn't compose into auditable trajectory data.

This module fixes the gap. Every meaningful axis change can be recorded
as a chain entry with old_value → new_value, the reason for the change,
and optional evidence_refs (e.g., Event numbers that supported the
re-elicitation). Future audits can walk the trajectory of any axis
across its lifetime.

## Schema

Single payload type:

```
{"type": "profile_axis_change",
 "axis_name": "<one of 16 valid axis names>",
 "old_value": "<free-form string description of prior state>",
 "new_value": "<free-form string description of new state>",
 "reason":    "<≥15 chars, no lazy tokens>",
 "recorded_at": "<ISO-8601 UTC>",
 "recorder":  "<operator-id>",
 "evidence_refs": ["Event 65", ...]}
```

Old / new values are FREE-FORM strings — operators may record
"inferred:loss-averse@2026-04-13" or "20% stop-condition rate" or
whatever shape captures the trajectory honestly. The history is
documentary, not enum-strict.

## Validation discipline

- `axis_name` must be one of the 16 declared operator-profile axes.
- `reason` must be ≥ 15 chars + must NOT match the lazy-token list
  (mirrors `_profile_audit_ack.py` discipline).
- `old_value` and `new_value` must be strings.

## Auto-instrumentation status

This module ships the API + CLI for **manual** trajectory recording.
**Auto-instrumentation** of profile-write paths (so every CLI-driven
profile change emits a history entry without operator action) is
deferred to a follow-up Event. Operators use the `episteme history axis
<name> --record` CLI to backfill or record manually until then.

Spec: ``~/episteme-private/docs/cp-v1.1-architectural.md``
§ CP-TEMPORAL-INTEGRITY-EXPANSION-01 Item 1.
"""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# Locate core/hooks/_chain.py — same lazy-import pattern other src/episteme/
# library modules use for hook-tier modules.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_CORE_HOOKS_DIR = _REPO_ROOT / "core" / "hooks"
if str(_CORE_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_HOOKS_DIR))

import _chain  # type: ignore  # pyright: ignore[reportMissingImports]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


DEFAULT_REFLECTIVE_DIR = Path.home() / ".episteme" / "memory" / "reflective"
HISTORY_FILENAME = "profile_history.jsonl"


# Valid axis names from `kernel/OPERATOR_PROFILE_SCHEMA.md` v2 schema.
# Must match the YAML keys in `core/memory/global/operator_profile.md`.
VALID_AXIS_NAMES: frozenset[str] = frozenset({
    # Process axes (§ 4a)
    "planning_strictness",
    "risk_tolerance",
    "testing_rigor",
    "parallelism_preference",
    "documentation_rigor",
    "automation_level",
    # Cognitive-style axes (§ 4b)
    "dominant_lens",
    "noise_signature",
    "abstraction_entry",
    "decision_cadence",
    "explanation_depth",
    "feedback_mode",
    "uncertainty_tolerance",
    "asymmetry_posture",
    "fence_discipline",
    # Expertise map (§ 4c)
    "expertise_map",
})


# Mirrors `_profile_audit_ack.py:LAZY_RATIONALE_TOKENS`. Reasoning Surface
# validator's lazy-token discipline applied to the reason field of a
# profile-axis-change record.
LAZY_REASON_TOKENS: frozenset[str] = frozenset({
    # English shortforms
    "n/a", "na", "tbd", "todo",
    "none", "nothing", "nil", "null",
    "ack", "acked", "acknowledged",
    "ok", "okay", "fine",
    "later", "fix later", "do later", "address later",
    "wip", "in progress",
    # Korean equivalents
    "해당 없음", "없음", "없다", "추후", "나중에",
})

MIN_REASON_CHARS = 15


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_axis_name(axis_name) -> None:
    """Reject empty / non-string / non-schema-axis axis_name. Strict
    against the v2 schema's 16-axis enumeration."""
    if not isinstance(axis_name, str):
        raise ValueError("axis_name must be a string")
    stripped = axis_name.strip()
    if not stripped:
        raise ValueError("axis_name must be a non-empty string")
    if stripped not in VALID_AXIS_NAMES:
        raise ValueError(
            f"unknown axis_name {axis_name!r}. Must be one of the 16 "
            f"declared axes in kernel/OPERATOR_PROFILE_SCHEMA.md. "
            f"Use `episteme history axis --list` to see valid axes."
        )


def validate_reason(text) -> None:
    """Lazy-token + min-char rejection. Mirrors `_profile_audit_ack.py:
    validate_rationale` discipline — a reason without substance defeats
    the purpose of the trajectory record."""
    if not isinstance(text, str):
        raise ValueError("reason must be a string")
    stripped = text.strip()
    lowered = stripped.lower()
    # Lazy-token check first: a lazy token of any length should report
    # as lazy, not as too-short.
    for token in LAZY_REASON_TOKENS:
        if lowered == token.lower():
            raise ValueError(
                f"reason matches lazy-token {token!r}. "
                f"Provide a substantive reason — what triggered the change?"
            )
    if len(stripped) < MIN_REASON_CHARS:
        raise ValueError(
            f"reason must be at least {MIN_REASON_CHARS} characters; "
            f"got {len(stripped)}. Provide a substantive reason — what "
            f"triggered the change? (Empty / placeholder reasons rejected.)"
        )


def _validate_value(value, field_name: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    if not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


# ---------------------------------------------------------------------------
# Recorder identity resolution (same pattern as _profile_audit_ack.py)
# ---------------------------------------------------------------------------


def _resolve_recorder() -> str:
    """Default recorder identity. Resolution order:
    EPISTEME_RECORDER env var → USER env var → git config user.name → 'unknown'."""
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


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------


def _resolve_path(reflective_dir: Path | None = None) -> Path:
    base = reflective_dir or DEFAULT_REFLECTIVE_DIR
    return base / HISTORY_FILENAME


# ---------------------------------------------------------------------------
# Write path
# ---------------------------------------------------------------------------


def record_change(
    axis_name: str,
    old_value: str,
    new_value: str,
    reason: str,
    *,
    evidence_refs: Iterable[str] | None = None,
    recorder: str | None = None,
    auto_recorded: bool = False,
    reflective_dir: Path | None = None,
    _now: datetime | None = None,  # test seam
) -> dict:
    """Append a ``profile_axis_change`` envelope to the history stream
    and return the full chain envelope.

    Raises ValueError on invalid axis_name (must be one of the 16
    declared schema axes), invalid reason (lazy-token / too-short), or
    non-string old_value / new_value.

    ``auto_recorded`` (Event 91): forward-compat field for entries
    written by the post-edit hook pair. Defaults False (manual). Auto
    entries still pass full validation; the flag lets future audits
    filter manual vs automated trajectory data.
    """
    validate_axis_name(axis_name)
    _validate_value(old_value, "old_value")
    _validate_value(new_value, "new_value")
    validate_reason(reason)
    now = _now or datetime.now(timezone.utc)

    payload = {
        "type": "profile_axis_change",
        "axis_name": axis_name,
        "old_value": old_value.strip(),
        "new_value": new_value.strip(),
        "reason": reason.strip(),
        "recorded_at": now.isoformat(),
        "recorder": recorder or _resolve_recorder(),
        "evidence_refs": list(evidence_refs) if evidence_refs else [],
        "auto_recorded": bool(auto_recorded),
    }
    return _chain.append(_resolve_path(reflective_dir), payload)


# ---------------------------------------------------------------------------
# Read paths
# ---------------------------------------------------------------------------


def walk_axis_history(
    axis_name: str,
    *,
    reflective_dir: Path | None = None,
) -> list[dict]:
    """Return all envelopes for ``axis_name``, in chronological (chain)
    order. Returns empty list if no history file or no entries for the axis.

    Filters out non-`profile_axis_change` payloads (defensive — the
    stream is single-payload-type by design but the filter ensures
    forward-compat with future payload types)."""
    validate_axis_name(axis_name)
    path = _resolve_path(reflective_dir)
    if not path.exists():
        return []

    entries: list[dict] = []
    for envelope in _chain.iter_records(path, verify=True):
        payload = envelope.get("payload", {})
        if not isinstance(payload, dict):
            continue
        if payload.get("type") != "profile_axis_change":
            continue
        if payload.get("axis_name") != axis_name:
            continue
        entries.append(envelope)
    return entries


def list_axes_with_history(*, reflective_dir: Path | None = None) -> set[str]:
    """Return set of axis_names that have at least one recorded change."""
    path = _resolve_path(reflective_dir)
    if not path.exists():
        return set()
    axes: set[str] = set()
    for envelope in _chain.iter_records(path, verify=True):
        payload = envelope.get("payload", {})
        if not isinstance(payload, dict):
            continue
        if payload.get("type") != "profile_axis_change":
            continue
        axis = payload.get("axis_name")
        if isinstance(axis, str):
            axes.add(axis)
    return axes


# ---------------------------------------------------------------------------
# Chain verification (delegates to _chain)
# ---------------------------------------------------------------------------


def verify_chain(reflective_dir: Path | None = None):
    """Return ``_chain.ChainVerdict`` for the profile_history stream.
    Used by ``episteme chain verify`` to integrate the history stream
    into the Pillar 2 verification surface."""
    return _chain.verify_chain(_resolve_path(reflective_dir))
