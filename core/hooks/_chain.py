"""Pillar 2 · shared SHA-256 hash chain — v1.0 RC CP7.

Append-only tamper-evident record substrate. Every Pillar 3 protocol,
every Blueprint D deferred-discovery, and every Layer 6 pending
contract is wrapped in the chain envelope defined here and written to
a JSONL file. A mutation of any byte in any record breaks the chain
from that point forward; Phase 12's audit refuses to trust records
at or after a break.

## Envelope schema

```
{
  "schema_version": "cp7-chained-v1",
  "ts":             "<ISO-8601 UTC, microseconds>",
  "prev_hash":      "sha256:<hex>" | "sha256:GENESIS",
  "payload":        {"type": "...", ...},
  "entry_hash":     "sha256:<hex>"
}
```

- ``schema_version`` — bumps only on envelope changes (never on
  payload changes).
- ``ts`` — part of the hash input so duplicate payloads at different
  times never collide.
- ``prev_hash`` — the previous record's ``entry_hash`` (or the
  literal ``"sha256:GENESIS"`` on the first record). Per CP7 plan Q5,
  the sentinel string keeps the walker's compare-loop uniform (no
  null-special-casing).
- ``payload`` — the business-layer dict. Carries ``type`` for
  dispatch at read time.
- ``entry_hash`` — SHA-256 over
  ``prev_hash || "|" || ts || "|" || canonical_json(payload)``.

## Canonicalization

Every hash input passes through ``canonical_payload_bytes``:

```
json.dumps(payload, sort_keys=True, separators=(',', ':'),
           ensure_ascii=False).encode('utf-8')
```

Sort-keys + separators guarantees byte-identical output for the same
semantic payload regardless of dict insertion order. UTF-8 avoids
the surrogate-pair attack surface of ``ensure_ascii=True`` on
non-BMP content.

Pipe separators between ``prev_hash`` / ``ts`` / payload-bytes
prevent ambiguity attacks where a payload tail could be confused
with the ``ts`` prefix of the next record's hash input.

## Attack surface (honest)

- **Mid-chain mutation** — closed. ``verify_chain`` reports the
  first break-index.
- **Swap or insert** — closed. ``prev_hash`` linkage fails.
- **Tail truncation (erase-most-recent)** — NOT closed. The
  resulting shorter file remains chain-intact from genesis up to
  whichever head survives. Mitigation: commit chain-head hash to
  git in git-tracked projects (spec § Threat model item 9; out of
  RC scope).
- **Coordinated FS rewrite (attacker rewrites file + head atomically)**
  — NOT closed. Requires cryptographic signing of chain rotations;
  deferred past v1.0 RC.

## Concurrency

Under ``fcntl.flock`` exclusive on the target file during append
+ verify. Windows fallback is a no-op (CP4's graceful-degrade
pattern) — documented; last-write-wins semantics.

Spec: ``docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`` § Pillar 2 ·
Append-Only Hash Chain.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Literal

# POSIX-only file locking. Windows fallback is a no-op per CP4 pattern.
# The module is wrapped here so Pyright can narrow types via the
# single ``_fcntl is not None`` check below; importing directly would
# trip "possibly unbound" warnings throughout.
try:
    import fcntl as _fcntl_module
    _fcntl = _fcntl_module
except ImportError:  # pragma: no cover — Windows exercised out-of-suite
    _fcntl = None


SCHEMA_VERSION = "cp7-chained-v1"
GENESIS_PREV_HASH = "sha256:GENESIS"
_HASH_PREFIX = "sha256:"


class ChainError(Exception):
    """Raised on unrecoverable chain-file I/O or format errors."""


@dataclass(frozen=True)
class ChainVerdict:
    """Output of ``verify_chain``. ``intact`` is True only when every
    entry's computed hash matches its declared hash AND every
    ``prev_hash`` links to the prior record's ``entry_hash``."""

    intact: bool
    break_index: int | None
    total_entries: int
    head_hash: str | None
    reason: str | None = None


@dataclass(frozen=True)
class ResetResult:
    status: Literal["reset", "archived_and_reset"]
    archived_path: Path | None
    new_genesis_hash: str


# ---------------------------------------------------------------------------
# Canonicalization + hashing
# ---------------------------------------------------------------------------


def canonical_payload_bytes(payload: dict) -> bytes:
    """Canonical JSON serialization. Byte-identical for semantically
    equal payloads regardless of dict insertion order."""
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def compute_entry_hash(prev_hash: str, ts: str, payload: dict) -> str:
    """SHA-256 over pipe-separated (prev_hash || ts || canonical_json(payload))."""
    hasher = hashlib.sha256()
    hasher.update(prev_hash.encode("utf-8"))
    hasher.update(b"|")
    hasher.update(ts.encode("utf-8"))
    hasher.update(b"|")
    hasher.update(canonical_payload_bytes(payload))
    return _HASH_PREFIX + hasher.hexdigest()


def _now_ts() -> str:
    """ISO-8601 UTC with microseconds. Consistent across the kernel."""
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# File-level concurrency + atomic write
# ---------------------------------------------------------------------------


@contextmanager
def _locked(path: Path) -> Iterator[None]:
    """Acquire an exclusive lock on the chain file during append +
    verify. No-op fallback on Windows with a stderr hint; documented
    degradation per CP4 pattern.

    The lock file is the target file itself — opening with ``a+`` so
    we can hold the descriptor even on an empty / missing file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    # ``a+`` creates the file if absent and leaves the position at end.
    lock_fd = open(path, "a+", encoding="utf-8")
    try:
        if _fcntl is not None:
            _fcntl.flock(lock_fd.fileno(), _fcntl.LOCK_EX)
        yield
    finally:
        try:
            if _fcntl is not None:
                _fcntl.flock(lock_fd.fileno(), _fcntl.LOCK_UN)
        finally:
            lock_fd.close()


def atomic_replace_file(path: Path, new_contents: bytes) -> None:
    """Replace ``path`` atomically with ``new_contents``. Used only
    by the retroactive upgrade path; normal chain writes append
    in-place under ``_locked``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".tmp-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(new_contents)
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
# Append
# ---------------------------------------------------------------------------


def _read_head_hash(path: Path) -> str:
    """Return the ``entry_hash`` of the last record in ``path``, or
    ``GENESIS_PREV_HASH`` if the file is missing / empty. Raises
    ``ChainError`` if the file exists but the tail is malformed —
    refusing to guess a hash for an unparseable last line."""
    if not path.is_file():
        return GENESIS_PREV_HASH
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ChainError(f"read head hash: {exc}") from exc
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return GENESIS_PREV_HASH
    try:
        last = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise ChainError(
            f"chain tail at {path} is not valid JSON: {exc}"
        ) from exc
    head = last.get("entry_hash")
    if not isinstance(head, str) or not head.startswith(_HASH_PREFIX):
        raise ChainError(
            f"chain tail at {path} missing entry_hash (got {head!r})"
        )
    return head


def append(path: Path, payload: dict, *, ts: str | None = None) -> dict:
    """Append a new record to the chain at ``path``. Returns the full
    envelope. Never partially writes — if the append-side I/O fails,
    the chain file is left in its prior state.

    Under exclusive flock on POSIX. On Windows the lock is a no-op
    — concurrent PreToolUse hooks on Windows accept last-write-wins.
    """
    if not isinstance(payload, dict):
        raise ChainError(f"payload must be a dict (got {type(payload).__name__})")
    if "type" not in payload or not isinstance(payload["type"], str):
        raise ChainError("payload must carry a non-empty `type` string")

    envelope_ts = ts or _now_ts()

    with _locked(path):
        prev = _read_head_hash(path)
        entry_hash = compute_entry_hash(prev, envelope_ts, payload)
        envelope = {
            "schema_version": SCHEMA_VERSION,
            "ts": envelope_ts,
            "prev_hash": prev,
            "payload": payload,
            "entry_hash": entry_hash,
        }
        line = json.dumps(envelope, ensure_ascii=False) + "\n"
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(line)
                f.flush()
                os.fsync(f.fileno())
        except OSError as exc:
            raise ChainError(f"append to {path}: {exc}") from exc
        return envelope


# ---------------------------------------------------------------------------
# Verify + iterate
# ---------------------------------------------------------------------------


def verify_chain(path: Path) -> ChainVerdict:
    """Walk the chain, verifying each entry_hash + prev_hash linkage.

    Returns a ``ChainVerdict`` with:
    - ``intact``: True only when every record verifies.
    - ``break_index``: 0-based index of the first broken record
      (None when intact).
    - ``total_entries``: count of records that parsed as JSON.
    - ``head_hash``: last valid entry_hash (None on empty / missing).
    - ``reason``: short diagnostic on break, None on intact.
    """
    if not path.is_file():
        return ChainVerdict(intact=True, break_index=None, total_entries=0, head_hash=None)

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return ChainVerdict(
            intact=False, break_index=0, total_entries=0,
            head_hash=None, reason=f"read error: {exc}",
        )

    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return ChainVerdict(intact=True, break_index=None, total_entries=0, head_hash=None)

    expected_prev = GENESIS_PREV_HASH
    head_hash: str | None = None
    for idx, line in enumerate(lines):
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            return ChainVerdict(
                intact=False, break_index=idx, total_entries=idx,
                head_hash=head_hash, reason=f"json decode at line {idx}: {exc}",
            )
        if not isinstance(rec, dict):
            return ChainVerdict(
                intact=False, break_index=idx, total_entries=idx,
                head_hash=head_hash, reason=f"record {idx} is not a JSON object",
            )
        declared_prev = rec.get("prev_hash")
        declared_entry = rec.get("entry_hash")
        ts = rec.get("ts")
        payload = rec.get("payload")
        if not isinstance(declared_prev, str) or not isinstance(declared_entry, str):
            return ChainVerdict(
                intact=False, break_index=idx, total_entries=idx,
                head_hash=head_hash,
                reason=f"record {idx} missing prev_hash / entry_hash string",
            )
        if not isinstance(ts, str) or not isinstance(payload, dict):
            return ChainVerdict(
                intact=False, break_index=idx, total_entries=idx,
                head_hash=head_hash,
                reason=f"record {idx} missing ts / payload",
            )
        if declared_prev != expected_prev:
            return ChainVerdict(
                intact=False, break_index=idx, total_entries=idx,
                head_hash=head_hash,
                reason=(
                    f"record {idx} prev_hash mismatch "
                    f"(expected {expected_prev[:20]}..., got {declared_prev[:20]}...)"
                ),
            )
        computed = compute_entry_hash(declared_prev, ts, payload)
        if computed != declared_entry:
            return ChainVerdict(
                intact=False, break_index=idx, total_entries=idx,
                head_hash=head_hash,
                reason=f"record {idx} entry_hash mismatch (payload or ts tampered)",
            )
        head_hash = declared_entry
        expected_prev = declared_entry

    return ChainVerdict(
        intact=True, break_index=None, total_entries=len(lines), head_hash=head_hash,
    )


def iter_records(path: Path, *, verify: bool = True) -> Iterator[dict]:
    """Yield envelopes in file order. When ``verify=True`` (default),
    stops at (not including) the first broken record. When
    ``verify=False``, yields every JSON-parseable record regardless of
    chain state — for recovery / forensic reads only."""
    if not path.is_file():
        return
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return
    lines = [ln for ln in text.splitlines() if ln.strip()]
    expected_prev = GENESIS_PREV_HASH
    for line in lines:
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            if verify:
                return
            continue
        if verify:
            if not isinstance(rec, dict):
                return
            declared_prev = rec.get("prev_hash")
            declared_entry = rec.get("entry_hash")
            ts = rec.get("ts")
            payload = rec.get("payload")
            if (
                not isinstance(declared_prev, str)
                or not isinstance(declared_entry, str)
                or not isinstance(ts, str)
                or not isinstance(payload, dict)
            ):
                return
            if declared_prev != expected_prev:
                return
            if compute_entry_hash(declared_prev, ts, payload) != declared_entry:
                return
            expected_prev = declared_entry
        yield rec


# ---------------------------------------------------------------------------
# Reset protocol (legitimate state loss)
# ---------------------------------------------------------------------------


def reset_stream(
    path: Path,
    *,
    reason: str,
    operator_confirmation: str,
    previous_head: str | None = None,
    mode: str = "reset",
    what_was_lost: str | None = None,
) -> ResetResult:
    """Archive any existing chain file and start a new chain with a
    ``chain_reset`` genesis record carrying the audit trail.

    The archived file is renamed to ``<name>.broken-<ts>.jsonl`` next
    to the original so forensics can recover it. The new chain begins
    with a single record whose payload conforms to the recovery-
    attestation envelope schema documented in
    ``kernel/CHAIN_RECOVERY_PROTOCOL.md``: ``type``, ``mode``,
    ``reason``, ``operator_confirmation``, ``previous_head``,
    ``recovered_at``, ``archived_from``, ``what_was_lost``.

    ``mode`` defaults to ``"reset"`` for backward compatibility with
    pre-Event-80 callers (which only used full-rewind reset). New CP-
    CHAIN-RECOVERY-PROTOCOL-01 callers via ``episteme chain recover
    --mode={reset,selective,migrate}`` pass an explicit mode + an
    optional ``what_was_lost`` description.

    Never auto-called. CLI (``episteme chain reset ...`` or ``episteme
    chain recover --mode=reset ...``) or explicit programmatic
    invocation only — auto-reset would be the largest evasion surface
    on the whole pillar.
    """
    if not isinstance(reason, str) or not reason.strip():
        raise ChainError("reset_stream: reason must be a non-empty string")
    if not isinstance(operator_confirmation, str) or not operator_confirmation.strip():
        raise ChainError(
            "reset_stream: operator_confirmation must be a non-empty string "
            "(typically the operator types 'I ACKNOWLEDGE CHAIN RESET' or similar)"
        )

    archived: Path | None = None
    if path.is_file():
        ts_slug = _now_ts().replace(":", "").replace(".", "-")
        archived = path.with_suffix(f".broken-{ts_slug}.jsonl")
        path.rename(archived)

    # Start fresh chain with a chain_reset genesis carrying the
    # recovery-attestation envelope payload (Event 80 / CP-CHAIN-
    # RECOVERY-PROTOCOL-01). Schema documented in
    # kernel/CHAIN_RECOVERY_PROTOCOL.md § Common payload fields.
    genesis_payload = {
        "type": "chain_reset",
        "mode": mode,
        "reason": reason.strip(),
        "operator_confirmation": operator_confirmation.strip(),
        "previous_head": previous_head,
        "recovered_at": _now_ts(),
        "archived_from": str(archived) if archived else None,
        "what_was_lost": what_was_lost.strip() if what_was_lost else None,
    }
    envelope = append(path, genesis_payload)
    return ResetResult(
        status="archived_and_reset" if archived else "reset",
        archived_path=archived,
        new_genesis_hash=envelope["entry_hash"],
    )
