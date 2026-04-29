"""Profile-audit acknowledgement store — CP-AUDIT-ACK-01 (Event 78).

Append-only hash-chained record of operator acknowledgements (and
revocations) of profile-audit drift alerts. Lives at
``~/.episteme/state/profile_audit_acks.jsonl`` and uses the existing
CP7 ``cp7-chained-v1`` envelope schema (see ``core/hooks/_chain.py``).

## Why a separate ack-store

The audit record itself (in ``~/.episteme/memory/reflective/profile_audit.jsonl``)
already carries an ``acknowledged: bool`` field, but mutating that field
in-place would violate Pillar 2 append-only semantics on the reflective
tier. The ack-store is the load-bearing audit trail: each ack and each
revoke is a new chain entry, so the *trajectory* of acknowledgement
state is preserved (Pillar 2 ethos: nothing changes silently).

## Schema

Two payload ``type`` values:

```
{"type": "profile_audit_ack", "audit_id": "audit-...",
 "rationale": "<≥15 chars, no lazy tokens>",
 "acked_at": "<ISO-8601>", "acker": "<operator-id>",
 "evidence_refs": ["Event 65", ...]}

{"type": "profile_audit_ack_revoke", "audit_id": "audit-...",
 "rationale": "<≥15 chars>",
 "revoked_at": "<ISO-8601>", "acker": "<operator-id>"}
```

A revoke is *not* a delete: it appends a new chain entry whose payload
flips the latest-state-per-audit-id back to "not acked." `is_acked()`
walks the chain and reads the latest entry per id.

## Lazy-rationale rejection

Mirrors the Reasoning Surface validator's lazy-token discipline. A
rationale of "n/a", "tbd", "ok", "해당 없음", etc. is rejected with
``ValueError``. Minimum 15 characters mirrors the disconfirmation
field's substantiveness floor.

Spec: ``~/episteme-private/docs/cp-v1.0.1-polish.md`` § CP-AUDIT-ACK-01.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# Locate core/hooks/_chain.py — same lazy-import pattern the rest of
# the CLI uses for hook-tier modules.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_CORE_HOOKS_DIR = _REPO_ROOT / "core" / "hooks"
if str(_CORE_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_HOOKS_DIR))

import _chain  # type: ignore  # pyright: ignore[reportMissingImports]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


# Default location of the ack-store. Tests override via the
# ``state_dir`` keyword argument on the public functions.
DEFAULT_STATE_DIR = Path.home() / ".episteme" / "state"
ACK_STORE_FILENAME = "profile_audit_acks.jsonl"

# Mirrors the Reasoning Surface validator's lazy-token list. A rationale
# whose stripped+lowered form matches any of these is rejected. The set
# is intentionally narrow — these are the high-signal lazy tokens, not
# every possible short answer.
LAZY_RATIONALE_TOKENS: frozenset[str] = frozenset({
    # English shortforms
    "n/a", "na", "tbd", "todo",
    "none", "nothing", "nil", "null",
    "ack", "acked", "acknowledged",
    "ok", "okay", "fine",
    "later", "fix later", "do later", "address later",
    "wip", "in progress",
    # Korean equivalents (the kernel's lazy-token list spans both)
    "해당 없음", "없음", "없다", "추후", "나중에",
})

MIN_RATIONALE_CHARS = 15


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_rationale(text) -> None:
    """Raise ValueError if the rationale is missing, lazy-token-matched,
    or too short. Stripped + lowered for matching.

    Order: lazy-token check fires BEFORE min-char check so a typed
    "n/a" returns the lazy-token error message (more diagnostic) rather
    than the min-char error. Untyped param is intentional: this is a
    runtime defensive check at the public-API boundary; CLI passes
    strings but the validator must handle any input shape without
    trusting type annotations.

    Mirrors the Reasoning Surface validator's discipline — an
    acknowledgement without substance defeats the purpose of the
    structured ack-store (which exists to *record reasoning*, not just
    to silence the banner).
    """
    if not isinstance(text, str):
        raise ValueError("rationale must be a string")
    stripped = text.strip()
    lowered = stripped.lower()
    # Lazy-token check first: a lazy token of any length should report
    # as lazy, not as too-short.
    for token in LAZY_RATIONALE_TOKENS:
        if lowered == token.lower():
            raise ValueError(
                f"rationale matches lazy-token {token!r}. "
                f"Provide a substantive reason — what evidence supports the ack?"
            )
    if len(stripped) < MIN_RATIONALE_CHARS:
        raise ValueError(
            f"rationale must be at least {MIN_RATIONALE_CHARS} characters; "
            f"got {len(stripped)}. Provide a substantive reason — what "
            f"evidence supports the ack? (Empty / placeholder rationales "
            f"are rejected.)"
        )


# Audit-id format from `_profile_audit.run_audit`:
#   audit-YYYYMMDD-HHMMSS-NNNN
# where NNNN is ``uuid.uuid4().hex[:4]`` — exactly 4 lowercase hex chars.
_AUDIT_ID_PATTERN = re.compile(r"^audit-\d{8}-\d{6}-[0-9a-f]{4}$")


def normalize_audit_id(audit_id) -> str:
    """Validate + normalize an audit_id. Returns the well-formed id.

    Lenient on missing prefix: if ``audit_id`` is the bare stem
    ``YYYYMMDD-HHMMSS-NNNN``, ``audit-`` is auto-prepended. This was
    added (Event 79) after a dogfood firing of CP-AUDIT-ACK-01 (Event 78)
    where the operator copy-pasted the stem without the prefix and the
    permissive CLI silently wrote a malformed entry to the ack-store —
    the suppression check then failed because the run_id in
    ``profile_audit.jsonl`` carries the prefix.

    Strict on format: the resulting string must match
    ``^audit-\\d{8}-\\d{6}-[0-9a-f]{4}$`` exactly. Anything else raises
    ValueError with a diagnostic message.

    Untyped param is intentional: this is a runtime defensive check at
    the public-API boundary; CLI passes strings but the validator must
    handle any input shape without trusting type annotations.
    """
    if not isinstance(audit_id, str):
        raise ValueError("audit_id must be a string")
    stripped = audit_id.strip()
    if not stripped:
        raise ValueError("audit_id must be a non-empty string")

    candidate = stripped if stripped.startswith("audit-") else f"audit-{stripped}"

    if not _AUDIT_ID_PATTERN.match(candidate):
        raise ValueError(
            f"audit_id {audit_id!r} does not match the expected format "
            f"`audit-YYYYMMDD-HHMMSS-NNNN` (NNNN = 4 lowercase hex chars). "
            f"Use `episteme profile audit ack --list` to see valid ids."
        )
    return candidate


# ---------------------------------------------------------------------------
# Acker identity resolution
# ---------------------------------------------------------------------------


def _resolve_acker() -> str:
    """Default acker identity. Single-operator default; future-proofed
    for multi-operator extensions.

    Resolution order:
    1. ``$EPISTEME_ACKER`` env var (explicit override)
    2. ``$USER`` env var
    3. ``git config user.name`` (if available)
    4. literal "unknown"
    """
    explicit = os.environ.get("EPISTEME_ACKER", "").strip()
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


def _resolve_path(state_dir: Path | None = None) -> Path:
    """Return the resolved ack-store JSONL path. Tests pass an explicit
    ``state_dir`` to isolate from the operator's real ack-store."""
    base = state_dir or DEFAULT_STATE_DIR
    return base / ACK_STORE_FILENAME


# ---------------------------------------------------------------------------
# Write paths — append-only, hash-chained
# ---------------------------------------------------------------------------


def write_ack(
    audit_id: str,
    rationale: str,
    *,
    evidence_refs: Iterable[str] | None = None,
    acker: str | None = None,
    state_dir: Path | None = None,
    _now: datetime | None = None,  # test seam
) -> dict:
    """Write a ``profile_audit_ack`` envelope to the ack-store and
    return the full chain envelope.

    Raises ``ValueError`` on invalid ``audit_id`` or invalid
    ``rationale`` (lazy-token, too-short).
    """
    normalized_id = normalize_audit_id(audit_id)
    validate_rationale(rationale)
    now = _now or datetime.now(timezone.utc)

    payload = {
        "type": "profile_audit_ack",
        "audit_id": normalized_id,
        "rationale": rationale.strip(),
        "acked_at": now.isoformat(),
        "acker": acker or _resolve_acker(),
        "evidence_refs": list(evidence_refs) if evidence_refs else [],
    }
    return _chain.append(_resolve_path(state_dir), payload)


def write_revoke(
    audit_id: str,
    rationale: str,
    *,
    acker: str | None = None,
    state_dir: Path | None = None,
    _now: datetime | None = None,  # test seam
) -> dict:
    """Write a ``profile_audit_ack_revoke`` envelope to the ack-store.

    A revoke does NOT delete the prior ack — it appends a new chain
    entry whose latest-state-per-audit-id wins. Audit trail preserved
    by construction (Pillar 2 ethos).
    """
    normalized_id = normalize_audit_id(audit_id)
    validate_rationale(rationale)
    now = _now or datetime.now(timezone.utc)

    payload = {
        "type": "profile_audit_ack_revoke",
        "audit_id": normalized_id,
        "rationale": rationale.strip(),
        "revoked_at": now.isoformat(),
        "acker": acker or _resolve_acker(),
    }
    return _chain.append(_resolve_path(state_dir), payload)


# ---------------------------------------------------------------------------
# Read paths
# ---------------------------------------------------------------------------


def _walk_latest_state(state_dir: Path | None = None) -> dict[str, str]:
    """Walk the ack-store chain and return ``{audit_id: "ack"|"revoke"}``
    for every audit_id seen, where the value is the LATEST entry's type.

    Quietly skips non-dict payloads + entries with non-string audit_ids
    so the read path never raises on a malformed entry.
    """
    path = _resolve_path(state_dir)
    if not path.exists():
        return {}

    latest: dict[str, str] = {}
    for envelope in _chain.iter_records(path, verify=True):
        payload = envelope.get("payload", {})
        if not isinstance(payload, dict):
            continue
        entry_type = payload.get("type")
        entry_id = payload.get("audit_id")
        if not isinstance(entry_id, str):
            continue
        if entry_type == "profile_audit_ack":
            latest[entry_id] = "ack"
        elif entry_type == "profile_audit_ack_revoke":
            latest[entry_id] = "revoke"
    return latest


def is_acked(audit_id: str, *, state_dir: Path | None = None) -> bool:
    """Return True iff the LATEST entry for ``audit_id`` is an ack
    (and not subsequently revoked)."""
    return _walk_latest_state(state_dir).get(audit_id) == "ack"


def acked_ids(*, state_dir: Path | None = None) -> set[str]:
    """Return set of all audit_ids currently in the acked state.
    Used by SessionStart banner suppression for batch lookup."""
    return {aid for aid, state in _walk_latest_state(state_dir).items() if state == "ack"}


def list_all_entries(*, state_dir: Path | None = None) -> list[dict]:
    """Return all chain envelopes in file order. Forensic / audit
    helper — used by `episteme profile audit ack --list-history` if/when
    that flag lands; not currently CLI-exposed."""
    path = _resolve_path(state_dir)
    if not path.exists():
        return []
    return list(_chain.iter_records(path, verify=True))


def list_outstanding_audits(
    *,
    reflective_dir: Path | None = None,
    state_dir: Path | None = None,
) -> list[dict]:
    """Return audit records that have drift AND are not currently acked.

    Each returned dict carries: ``{run_id, run_ts, drift_axes}``. Used by
    ``episteme profile audit ack --list``.
    """
    reflective_dir = reflective_dir or (Path.home() / ".episteme" / "memory" / "reflective")
    audit_path = reflective_dir / "profile_audit.jsonl"
    if not audit_path.exists():
        return []

    acked = acked_ids(state_dir=state_dir)
    outstanding: list[dict] = []

    try:
        with open(audit_path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                try:
                    rec = json.loads(s)
                except json.JSONDecodeError:
                    continue
                if not isinstance(rec, dict):
                    continue
                run_id = rec.get("run_id")
                if not isinstance(run_id, str):
                    continue
                if run_id in acked:
                    continue
                drift_axes = [
                    a.get("axis_name")
                    for a in rec.get("axes", [])
                    if isinstance(a, dict) and a.get("verdict") == "drift"
                ]
                if not drift_axes:
                    continue
                outstanding.append({
                    "run_id": run_id,
                    "run_ts": rec.get("run_ts"),
                    "drift_axes": [name for name in drift_axes if isinstance(name, str)],
                })
    except OSError:
        return []
    return outstanding


# ---------------------------------------------------------------------------
# Chain verification (delegates to _chain)
# ---------------------------------------------------------------------------


def verify_chain(state_dir: Path | None = None):
    """Return ``_chain.ChainVerdict`` for the ack-store. Used by
    ``episteme chain verify`` to integrate the ack-store stream into the
    Pillar 2 verification surface."""
    return _chain.verify_chain(_resolve_path(state_dir))
