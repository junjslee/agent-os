"""Layer 8 spot-check sampling substrate — v1.0 RC CP8.

Samples admitted ops at a configurable rate for operator review.
Queues sampled entries in a hash-chained JSONL file. Records
verdicts via separate append-only records (never mutates entries).

## Sampling schedule

- Base rate: ``10%`` for the first 30 days from the first-sample
  anchor (``~/.episteme/sample_schedule_anchor.json``), ``5%`` after
  (CP8 plan Q3 decision).
- Per-project override: ``<cwd>/.episteme/spot_check_rate`` (single
  float line). When present, overrides the schedule. Clamped to
  [0, 1].
- Multipliers (max-not-sum, capped at 1.0):
  - ``blueprint_fired`` — 2× when a named blueprint matched.
  - ``synthesis_produced`` — 2× when the op's PostToolUse synthesized
    a Pillar 3 protocol (Fence today; Axiomatic / Blueprint D at
    v1.0.1 / CP10).
  - ``blueprint_d_resolution`` — 2× when Blueprint D resolved a
    cascade. CP10 populates; CP8 defines the label.

## Install anchor

Spec wants "calendar-from-install". No clean canonical signal exists
for install time, so CP8 uses a first-sample anchor: on the first
``should_sample`` call, write
``~/.episteme/sample_schedule_anchor.json`` with the current ts; on
subsequent calls, read it. Operators can pre-seed the file with a
known install date if they care. Post-``rm -rf ~/.episteme`` the
anchor restarts — acceptable because the operator IS in a cold-start
window after a wipe.

## Hash-chained queue

All records go to ``~/.episteme/state/spot_check_queue.jsonl`` via
CP7's ``_chain.append``. Three payload types:

- ``spot_check_entry`` — PreToolUse-admitted op that was sampled.
- ``spot_check_verdict`` — operator verdict via ``episteme review``.
  Latest-wins on revision (latest by ``verdicted_at`` + file-order
  tiebreak).
- ``spot_check_skip`` — operator deferred the entry; skip records
  carry a 7-day TTL (CP8 plan Q4). The reader treats an entry with
  a non-expired skip as "hidden"; after TTL the entry re-presents.

## Verdict dimensions (locked per CP8 plan Q5)

- ``surface_validity``: ``real`` | ``vapor`` | ``wrong_blueprint``
  — required on every verdict.
- ``protocol_quality``: ``useful`` | ``vague`` | ``overfit`` |
  ``wrong_context`` — required when entry.multipliers_applied
  contains ``synthesis_produced``.
- ``cascade_integrity``: ``real_sync`` | ``theater`` | ``partial``
  — required when entry.multipliers_applied contains
  ``blueprint_d_resolution``.

## PostToolUse wiring (CP8 plan Q1)

Sampling runs at PostToolUse, NOT PreToolUse. Rationale: the
``synthesis_produced`` multiplier only has its true value after
``_fence_synthesis.finalize_on_success`` has run, and the hot-path
stays fast by deferring the sample dice roll. ``maybe_sample`` is
called from BOTH ``fence_synthesis.py`` (PostToolUse) and
``calibration_telemetry.py`` (PostToolUse). Idempotent-by-
correlation-id — the first call wins; the second is a no-op.

Spec: ``docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`` § Layer 8 ·
operator spot-check sampling.
"""
from __future__ import annotations

import json
import os
import random
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Literal

_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

from _chain import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    ChainError,
    ChainVerdict,
    append as _chain_append,
    iter_records as _chain_iter,
    verify_chain as _chain_verify,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


ENTRY_TYPE = "spot_check_entry"
VERDICT_TYPE = "spot_check_verdict"
SKIP_TYPE = "spot_check_skip"

BASE_RATE_COLD = 0.10
BASE_RATE_WARM = 0.05
COLD_WINDOW_DAYS = 30

MULTIPLIER_BLUEPRINT_FIRED = 2.0
MULTIPLIER_SYNTHESIS_PRODUCED = 2.0
MULTIPLIER_BLUEPRINT_D_RESOLUTION = 2.0

SKIP_TTL_SECONDS = 7 * 24 * 60 * 60

# Enum allow-lists — enforced by the CLI verdict writer.
SURFACE_VALIDITY_VALUES = frozenset({"real", "vapor", "wrong_blueprint"})
PROTOCOL_QUALITY_VALUES = frozenset({"useful", "vague", "overfit", "wrong_context"})
CASCADE_INTEGRITY_VALUES = frozenset({"real_sync", "theater", "partial"})

# Multiplier labels the entry can carry.
MULTIPLIER_LABELS = frozenset({
    "blueprint_fired",
    "synthesis_produced",
    "blueprint_d_resolution",
})


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------


def _episteme_home() -> Path:
    return Path(os.environ.get("EPISTEME_HOME") or (Path.home() / ".episteme"))


def _queue_path() -> Path:
    return _episteme_home() / "state" / "spot_check_queue.jsonl"


def _anchor_path() -> Path:
    return _episteme_home() / "sample_schedule_anchor.json"


def _project_override_path(cwd: Path) -> Path:
    return cwd / ".episteme" / "spot_check_rate"


# ---------------------------------------------------------------------------
# Rate computation
# ---------------------------------------------------------------------------


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def read_or_seed_anchor(now: datetime | None = None) -> datetime:
    """Read the sample-schedule anchor or seed it with ``now``.

    The anchor is a best-effort proxy for install time. First call
    writes ``~/.episteme/sample_schedule_anchor.json``; subsequent
    calls read it. Corrupt / unreadable anchors are re-seeded —
    CP8's discipline is "prefer a fresh 30-day cold window over
    an opaque error state."
    """
    path = _anchor_path()
    now_dt = now or datetime.now(timezone.utc)
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            stamp = data.get("installed_at")
            if isinstance(stamp, str) and stamp.strip():
                dt = datetime.fromisoformat(stamp)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
        except (OSError, json.JSONDecodeError, ValueError):
            pass
    # Seed.
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(
            json.dumps({"installed_at": _iso(now_dt)}, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError:
        pass
    return now_dt


def _read_project_override(cwd: Path) -> float | None:
    """Parse ``<cwd>/.episteme/spot_check_rate`` — single float line.
    Returns None on absence or parse failure (silent fallback to the
    schedule)."""
    path = _project_override_path(cwd)
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    try:
        value = float(text.splitlines()[0].strip()) if text else None
    except (ValueError, IndexError):
        return None
    if value is None:
        return None
    return max(0.0, min(1.0, value))


def base_rate(
    now: datetime | None = None,
    *,
    cwd: Path | None = None,
    anchor: datetime | None = None,
) -> float:
    """Return the base sampling rate. Project override wins; otherwise
    schedule: 10% within 30 days of anchor, 5% after."""
    if cwd is not None:
        override = _read_project_override(cwd)
        if override is not None:
            return override
    now_dt = now or datetime.now(timezone.utc)
    anchor_dt = anchor or read_or_seed_anchor(now=now_dt)
    age_days = (now_dt - anchor_dt).total_seconds() / 86400.0
    return BASE_RATE_COLD if age_days < COLD_WINDOW_DAYS else BASE_RATE_WARM


def effective_rate(base: float, multipliers: Iterable[str]) -> float:
    """``base * max(multiplier-values)``, capped at 1.0.

    Max-not-sum: if two multipliers apply (e.g. ``blueprint_fired`` +
    ``synthesis_produced``), the effective rate is still 2× base.
    Compounding would flood low-volume sessions on the same signal.
    """
    mset = set(multipliers) & MULTIPLIER_LABELS
    factors = [1.0]
    if "blueprint_fired" in mset:
        factors.append(MULTIPLIER_BLUEPRINT_FIRED)
    if "synthesis_produced" in mset:
        factors.append(MULTIPLIER_SYNTHESIS_PRODUCED)
    if "blueprint_d_resolution" in mset:
        factors.append(MULTIPLIER_BLUEPRINT_D_RESOLUTION)
    return min(1.0, base * max(factors))


_DEFAULT_RNG = random.SystemRandom()


def decide_sample(rate: float, *, rng: random.Random | None = None) -> bool:
    """Returns True with probability ``rate``. ``rng=None`` uses
    ``SystemRandom`` in production; tests inject a seeded
    ``random.Random`` for determinism."""
    if rate <= 0.0:
        return False
    if rate >= 1.0:
        return True
    r = rng or _DEFAULT_RNG
    return r.random() < rate


# ---------------------------------------------------------------------------
# Queue I/O
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SampleResult:
    queued: bool
    correlation_id: str
    effective_rate: float
    multipliers: tuple[str, ...]
    entry_hash: str | None
    reason: str  # "queued" | "rate_zero" | "already_queued" | "random_miss" | "error"


def _correlation_already_queued(
    correlation_id: str, path: Path | None = None
) -> bool:
    """Idempotence check — has an entry record with this
    correlation_id already been written to the queue?"""
    target = path if path is not None else _queue_path()
    for rec in _chain_iter(target, verify=False):
        payload = rec.get("payload") if isinstance(rec, dict) else None
        if not isinstance(payload, dict):
            continue
        if payload.get("type") != ENTRY_TYPE:
            continue
        if payload.get("correlation_id") == correlation_id:
            return True
    return False


def maybe_sample(
    *,
    correlation_id: str,
    op_label: str,
    blueprint: str,
    context_signature: dict,
    surface_snapshot: dict,
    synthesis_produced: bool = False,
    blueprint_d_resolution: bool = False,
    cwd: Path | None = None,
    now: datetime | None = None,
    rng: random.Random | None = None,
    path: Path | None = None,
) -> SampleResult:
    """Decide whether to sample this admitted op and queue the entry
    if so. Idempotent by ``correlation_id`` — a second call with the
    same id is a no-op.

    All parameters are keyword-only. The function never raises —
    unexpected errors return ``SampleResult(queued=False,
    reason="error")`` with a stderr advisory.
    """
    if not isinstance(correlation_id, str) or not correlation_id.strip():
        return SampleResult(
            queued=False, correlation_id="", effective_rate=0.0,
            multipliers=(), entry_hash=None, reason="error",
        )
    try:
        if _correlation_already_queued(correlation_id, path=path):
            return SampleResult(
                queued=False, correlation_id=correlation_id,
                effective_rate=0.0, multipliers=(), entry_hash=None,
                reason="already_queued",
            )

        multipliers: list[str] = []
        if blueprint and blueprint != "generic":
            multipliers.append("blueprint_fired")
        if synthesis_produced:
            multipliers.append("synthesis_produced")
        if blueprint_d_resolution:
            multipliers.append("blueprint_d_resolution")

        now_dt = now or datetime.now(timezone.utc)
        base = base_rate(now=now_dt, cwd=cwd)
        rate = effective_rate(base, multipliers)
        if rate <= 0.0:
            return SampleResult(
                queued=False, correlation_id=correlation_id,
                effective_rate=0.0, multipliers=tuple(multipliers),
                entry_hash=None, reason="rate_zero",
            )
        if not decide_sample(rate, rng=rng):
            return SampleResult(
                queued=False, correlation_id=correlation_id,
                effective_rate=rate, multipliers=tuple(multipliers),
                entry_hash=None, reason="random_miss",
            )

        payload = {
            "type": ENTRY_TYPE,
            "correlation_id": correlation_id,
            "queued_at": _iso(now_dt),
            "op_label": op_label,
            "blueprint": blueprint,
            "context_signature": context_signature,
            "surface_snapshot": surface_snapshot,
            "multipliers_applied": multipliers,
            "effective_rate_at_sample": rate,
        }
        target = path if path is not None else _queue_path()
        envelope = _chain_append(target, payload)
        return SampleResult(
            queued=True, correlation_id=correlation_id,
            effective_rate=rate, multipliers=tuple(multipliers),
            entry_hash=envelope["entry_hash"], reason="queued",
        )
    except (ChainError, OSError) as exc:  # graceful degrade
        sys.stderr.write(
            f"[episteme spot_check] sample error: "
            f"{exc.__class__.__name__}; admit path untouched\n"
        )
        return SampleResult(
            queued=False, correlation_id=correlation_id,
            effective_rate=0.0, multipliers=(), entry_hash=None,
            reason="error",
        )


# ---------------------------------------------------------------------------
# Read-side helpers
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QueuedEntry:
    envelope: dict
    payload: dict
    verdict: dict | None           # latest verdict record (payload dict) or None
    skip_until: datetime | None    # non-None when a non-expired skip was recorded
    entry_hash: str


def _parse_iso(value: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _read_all_records(path: Path | None = None) -> list[dict]:
    target = path if path is not None else _queue_path()
    return list(_chain_iter(target, verify=True))


def list_entries(
    *,
    path: Path | None = None,
    now: datetime | None = None,
) -> list[QueuedEntry]:
    """Return every entry in file order, joined with the latest
    verdict and skip state. Verdict is the most recent verdict record
    for that correlation_id (by ``verdicted_at`` — file order
    tiebreak). Skip state is set when the latest skip record for the
    entry is still within its 7-day TTL.
    """
    now_dt = now or datetime.now(timezone.utc)
    records = _read_all_records(path=path)
    entries: list[tuple[dict, dict]] = []      # (envelope, payload)
    verdicts_by_cid: dict[str, tuple[str, dict]] = {}   # cid -> (verdicted_at, payload)
    skips_by_cid: dict[str, datetime] = {}  # cid -> skip expires_at

    for rec in records:
        payload = rec.get("payload") if isinstance(rec, dict) else None
        if not isinstance(payload, dict):
            continue
        ptype = payload.get("type")
        if ptype == ENTRY_TYPE:
            entries.append((rec, payload))
        elif ptype == VERDICT_TYPE:
            cid = payload.get("correlation_id")
            stamp = payload.get("verdicted_at")
            if isinstance(cid, str) and isinstance(stamp, str):
                prior = verdicts_by_cid.get(cid)
                if prior is None or stamp > prior[0]:
                    verdicts_by_cid[cid] = (stamp, payload)
        elif ptype == SKIP_TYPE:
            cid = payload.get("correlation_id")
            expires_str = payload.get("expires_at")
            expires = _parse_iso(expires_str) if isinstance(expires_str, str) else None
            if isinstance(cid, str) and expires is not None and expires > now_dt:
                prior = skips_by_cid.get(cid)
                if prior is None or expires > prior:
                    skips_by_cid[cid] = expires

    out: list[QueuedEntry] = []
    for envelope, payload in entries:
        cid = payload.get("correlation_id")
        verdict_pair = verdicts_by_cid.get(cid) if isinstance(cid, str) else None
        skip_until = skips_by_cid.get(cid) if isinstance(cid, str) else None
        out.append(QueuedEntry(
            envelope=envelope,
            payload=payload,
            verdict=verdict_pair[1] if verdict_pair else None,
            skip_until=skip_until,
            entry_hash=envelope.get("entry_hash", ""),
        ))
    return out


def list_pending(
    *,
    path: Path | None = None,
    now: datetime | None = None,
) -> list[QueuedEntry]:
    """Entries with no verdict AND no active skip. Ordered by
    ``queued_at`` ascending — oldest-first."""
    entries = list_entries(path=path, now=now)
    pending = [
        e for e in entries
        if e.verdict is None and e.skip_until is None
    ]
    pending.sort(key=lambda e: str(e.payload.get("queued_at", "")))
    return pending


def count_pending(
    *,
    path: Path | None = None,
    now: datetime | None = None,
) -> int:
    return len(list_pending(path=path, now=now))


def get_entry(
    correlation_id: str,
    *,
    path: Path | None = None,
    now: datetime | None = None,
) -> QueuedEntry | None:
    for e in list_entries(path=path, now=now):
        if e.payload.get("correlation_id") == correlation_id:
            return e
    return None


def stats(
    *,
    path: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Summary counts suitable for the ``--stats`` CLI flag."""
    entries = list_entries(path=path, now=now)
    total = len(entries)
    verdicted = [e for e in entries if e.verdict is not None]
    pending = [e for e in entries if e.verdict is None and e.skip_until is None]
    skipped = [e for e in entries if e.skip_until is not None]
    distribution: dict[str, int] = {}
    for e in verdicted:
        verdicts = e.verdict.get("verdicts") if e.verdict else None
        if isinstance(verdicts, dict):
            sv = verdicts.get("surface_validity")
            if isinstance(sv, str):
                distribution[sv] = distribution.get(sv, 0) + 1
    return {
        "total": total,
        "verdicted": len(verdicted),
        "pending": len(pending),
        "skipped": len(skipped),
        "surface_validity_distribution": distribution,
    }


# ---------------------------------------------------------------------------
# Verdict / skip writes
# ---------------------------------------------------------------------------


def _validate_verdict(
    entry: QueuedEntry,
    verdicts: dict,
) -> str | None:
    """Return None when the verdict dict is shape-valid; return an
    error string when a required dimension is missing, absent, or
    carries an out-of-enum value."""
    if not isinstance(verdicts, dict):
        return "verdicts must be a dict"
    sv = verdicts.get("surface_validity")
    if sv not in SURFACE_VALIDITY_VALUES:
        return (
            f"surface_validity is required — one of "
            f"{sorted(SURFACE_VALIDITY_VALUES)} (got {sv!r})"
        )
    multipliers = set(entry.payload.get("multipliers_applied") or [])
    pq = verdicts.get("protocol_quality")
    if "synthesis_produced" in multipliers:
        if pq not in PROTOCOL_QUALITY_VALUES:
            return (
                f"protocol_quality required for synthesis_produced entries "
                f"— one of {sorted(PROTOCOL_QUALITY_VALUES)} (got {pq!r})"
            )
    elif pq is not None and pq not in PROTOCOL_QUALITY_VALUES:
        return f"protocol_quality out of enum (got {pq!r})"
    ci = verdicts.get("cascade_integrity")
    if "blueprint_d_resolution" in multipliers:
        if ci not in CASCADE_INTEGRITY_VALUES:
            return (
                f"cascade_integrity required for blueprint_d_resolution "
                f"entries — one of {sorted(CASCADE_INTEGRITY_VALUES)} "
                f"(got {ci!r})"
            )
    elif ci is not None and ci not in CASCADE_INTEGRITY_VALUES:
        return f"cascade_integrity out of enum (got {ci!r})"
    return None


def write_verdict(
    correlation_id: str,
    verdicts: dict,
    *,
    note: str = "",
    is_revision: bool = False,
    path: Path | None = None,
    now: datetime | None = None,
) -> dict:
    """Append a ``spot_check_verdict`` record. Never mutates the
    original entry. Raises ``ChainError`` when the entry does not
    exist or the verdict shape violates the required dimensions.

    Returns the full envelope.
    """
    entry = get_entry(correlation_id, path=path, now=now)
    if entry is None:
        raise ChainError(
            f"write_verdict: no entry with correlation_id {correlation_id!r}"
        )
    existing_verdict = entry.verdict is not None
    if existing_verdict and not is_revision:
        raise ChainError(
            f"write_verdict: entry {correlation_id} already has a verdict; "
            f"pass is_revision=True to record a new one"
        )
    err = _validate_verdict(entry, verdicts)
    if err is not None:
        raise ChainError(f"write_verdict: {err}")

    now_dt = now or datetime.now(timezone.utc)
    payload = {
        "type": VERDICT_TYPE,
        "correlation_id": correlation_id,
        "entry_hash": entry.entry_hash,
        "verdicted_at": _iso(now_dt),
        "verdicts": dict(verdicts),
        "note": str(note or "").strip(),
        "is_revision": bool(is_revision),
    }
    target = path if path is not None else _queue_path()
    return _chain_append(target, payload)


def write_skip(
    correlation_id: str,
    *,
    path: Path | None = None,
    now: datetime | None = None,
    ttl_seconds: int = SKIP_TTL_SECONDS,
) -> dict:
    """Defer the entry for ``ttl_seconds`` (default 7 days). A skip
    record hides the entry from ``list_pending`` until its
    ``expires_at`` passes; after the TTL the entry re-presents so it
    doesn't silently drop out of review."""
    entry = get_entry(correlation_id, path=path, now=now)
    if entry is None:
        raise ChainError(
            f"write_skip: no entry with correlation_id {correlation_id!r}"
        )
    now_dt = now or datetime.now(timezone.utc)
    payload = {
        "type": SKIP_TYPE,
        "correlation_id": correlation_id,
        "entry_hash": entry.entry_hash,
        "skipped_at": _iso(now_dt),
        "expires_at": _iso(now_dt + timedelta(seconds=ttl_seconds)),
    }
    target = path if path is not None else _queue_path()
    return _chain_append(target, payload)


# ---------------------------------------------------------------------------
# Chain verification (Phase 12 precondition)
# ---------------------------------------------------------------------------


def verify_chain(path: Path | None = None) -> ChainVerdict:
    target = path if path is not None else _queue_path()
    return _chain_verify(target)


# ---------------------------------------------------------------------------
# PostToolUse integration helpers
# ---------------------------------------------------------------------------


def _telemetry_dir_for_date(ts_date: str) -> Path:
    return _episteme_home() / "telemetry" / f"{ts_date}-audit.jsonl"


def _read_prediction_record(correlation_id: str) -> dict | None:
    """Walk today's + yesterday's telemetry files for a prediction
    record matching ``correlation_id``. PostToolUse commonly lands
    seconds after PreToolUse; a two-day window covers midnight rollover.
    """
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    yesterday = (now - timedelta(days=1)).date().isoformat()
    for day in (today, yesterday):
        path = _telemetry_dir_for_date(day)
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        # Walk lines in reverse — newest prediction wins for the
        # correlation id.
        for line in reversed(text.splitlines()):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if (
                rec.get("event") == "prediction"
                and rec.get("correlation_id") == correlation_id
            ):
                return rec
    return None


def _build_surface_snapshot(prediction: dict) -> dict:
    """Normalize the prediction record's epistemic_prediction into the
    ``surface_snapshot`` shape. Preserves the business fields needed
    for operator review; strips provenance fields that live at the
    envelope level."""
    ep = prediction.get("epistemic_prediction")
    if not isinstance(ep, dict):
        ep = {}
    return {
        "core_question": str(ep.get("core_question") or "").strip(),
        "disconfirmation": str(ep.get("disconfirmation") or "").strip(),
        "unknowns": list(ep.get("unknowns") or []),
        "hypothesis": str(ep.get("hypothesis") or "").strip(),
    }


def build_post_context(correlation_id: str) -> dict | None:
    """PostToolUse helper — read the prediction record and assemble
    the fields ``maybe_sample`` needs. Returns None when the
    prediction is absent (op wasn't admitted, or ran before CP8
    landed).

    The context_signature is rebuilt at PostToolUse time from the
    prediction's cwd + blueprint + op_label; this is structurally
    equivalent to the PreToolUse signature because the four
    deterministic inputs (project_name / project_tier / blueprint /
    op_class) don't change between Pre and Post.
    """
    prediction = _read_prediction_record(correlation_id)
    if prediction is None:
        return None

    op_label = str(prediction.get("op") or "").strip()
    blueprint = str(prediction.get("blueprint_name") or "generic").strip()
    cwd_str = str(prediction.get("cwd") or "").strip()
    cwd = Path(cwd_str) if cwd_str else Path.cwd()

    try:
        from _context_signature import (  # type: ignore  # pyright: ignore[reportMissingImports]
            build as _build_sig,
        )
        sig = _build_sig(cwd, blueprint_name=blueprint, op_class=op_label)
        context_signature = sig.as_dict()
    except Exception:
        # Graceful degrade — a minimal signature rather than no sample.
        context_signature = {
            "project_name": cwd.name if cwd else "unknown_project",
            "project_tier": "unknown",
            "blueprint": blueprint,
            "op_class": op_label,
            "constraint_head": None,
            "runtime_marker": "ad_hoc",
        }

    return {
        "op_label": op_label,
        "blueprint": blueprint,
        "cwd": cwd,
        "surface_snapshot": _build_surface_snapshot(prediction),
        "context_signature": context_signature,
    }
