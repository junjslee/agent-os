"""Pillar 3 · active guidance surface — v1.0 RC CP9.

PreToolUse framework query. Surfaces the highest-overlap protocol
from ``~/.episteme/framework/protocols.jsonl`` as a one-line stderr
advisory when the current op's context signature crosses the
``min_overlap`` threshold. Never blocks admission — advisory-only
posture per spec § Pillar 3.

## The payoff for CP5

CP5 wrote the first protocol entries via Fence Reconstruction
synthesis. CP7 chained them. CP8 sampled them. Until CP9 fires the
advisory, Pillar 3 is a write-only memory — zero retrieval value.
This module is what makes the synthesis visible to the operator at
the point of the next matching decision.

## Match logic

- Candidate signature (from ``_context_signature.build``) carries six
  conservative fields: project_name / project_tier / blueprint /
  op_class / constraint_head / runtime_marker.
- For each protocol, compute ``field_overlap(candidate, stored)``
  (exact-match count, 0..6).
- Filter out protocols whose latest CP8 spot-check verdict has
  ``surface_validity == "vapor"`` — verdict-marked vapor protocols
  MUST NOT surface again as guidance.
- Rank remaining candidates by ``(overlap desc, ts desc)``.
- Return top match iff ``overlap >= min_overlap`` (default 4/6).

Project scope: the query filters ``list_protocols`` by the
candidate's ``project_name`` so protocols synthesized in project A
never surface in project B. A cross-project match could still reach
threshold 4/6, but semantically tacit operator knowledge from one
project isn't reliable advice for another without a stronger signal.
Post-soak v1.0.1 revisits this if real cross-project signal appears.

## Min-overlap override (per-project)

``<cwd>/.episteme/guidance_min_overlap`` — single int line (0..6).
Clamped to valid range; parse failure falls back to the default.
Consistent with CP8's ``spot_check_rate`` override pattern.

## Advisory format

Two physical lines, one logical advisory (single stderr write):

```
[episteme guide] <ts-date> · <blueprint> · overlap=<N>/6 · cid=<prefix>
  Protocol: <synthesized_protocol text, truncated at 180 chars>
```

``cid`` is the first 12 chars of the source protocol's
``correlation_id`` — lets the operator grep for the full record
without bloating the advisory line.

## Cost

Hot-path query = chain walk + O(entries × 6) overlap comparisons +
verdict lookup. For RC-scale framework (< 100 protocols), < 5 ms
p95. Warm cache keyed on ``(cwd, protocols_path_mtime)`` so
repeat-within-same-process reads don't re-walk.

Spec: ``docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`` § Pillar 3 ·
Framework Synthesis & Active Guidance.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

from _context_signature import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    ContextSignature,
    field_overlap,
)
from _framework import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    list_protocols,
)
from _spot_check import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    list_entries,
)


# ---------------------------------------------------------------------------
# Defaults + overrides
# ---------------------------------------------------------------------------


MIN_OVERLAP_DEFAULT = 4
MIN_OVERLAP_FLOOR = 0
MIN_OVERLAP_CEILING = 6
_ADVISORY_PROTOCOL_MAX_CHARS = 180
_CID_PREFIX_CHARS = 12


def load_min_overlap(cwd: Path) -> int:
    """Read ``<cwd>/.episteme/guidance_min_overlap`` (single int).
    Clamps to [0, 6]. Falls back silently to ``MIN_OVERLAP_DEFAULT``
    on missing / malformed file."""
    override_path = cwd / ".episteme" / "guidance_min_overlap"
    if not override_path.is_file():
        return MIN_OVERLAP_DEFAULT
    try:
        text = override_path.read_text(encoding="utf-8").strip()
    except OSError:
        return MIN_OVERLAP_DEFAULT
    try:
        value = int(text.splitlines()[0].strip()) if text else MIN_OVERLAP_DEFAULT
    except (ValueError, IndexError):
        return MIN_OVERLAP_DEFAULT
    return max(MIN_OVERLAP_FLOOR, min(MIN_OVERLAP_CEILING, value))


# ---------------------------------------------------------------------------
# Match dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GuidanceMatch:
    protocol_payload: dict
    overlap: int
    synthesized_at: str
    correlation_id: str


# ---------------------------------------------------------------------------
# Verdict filter — skip protocols marked `vapor` via CP8 spot-check
# ---------------------------------------------------------------------------


def _build_vapor_correlation_set() -> set[str]:
    """Build the set of correlation_ids whose LATEST spot-check
    verdict has ``surface_validity == "vapor"``. CP8's ``list_entries``
    already resolves latest-wins on verdict revision; we trust its
    resolution."""
    vapor: set[str] = set()
    try:
        entries = list_entries()
    except Exception:
        return vapor  # Degrade open — better to guide too much than not at all.
    for entry in entries:
        verdict = entry.verdict
        if not isinstance(verdict, dict):
            continue
        verdicts = verdict.get("verdicts")
        if not isinstance(verdicts, dict):
            continue
        if verdicts.get("surface_validity") == "vapor":
            cid = entry.payload.get("correlation_id")
            if isinstance(cid, str) and cid:
                vapor.add(cid)
    return vapor


# ---------------------------------------------------------------------------
# Warm cache — invalidates on protocols.jsonl mtime change
# ---------------------------------------------------------------------------


_CACHE: dict[tuple[str, float], list[dict]] = {}


def _protocols_path() -> Path:
    from _framework import _protocols_path as _p  # type: ignore  # pyright: ignore[reportMissingImports]
    return _p()


def _cache_key() -> tuple[str, float] | None:
    path = _protocols_path()
    try:
        mtime = path.stat().st_mtime if path.is_file() else 0.0
    except OSError:
        return None
    return (str(path), mtime)


def _load_protocols_cached(project_name: str) -> list[dict]:
    """Chain-verified read filtered by project_name. Cached per
    (path, mtime, project). Cache clears on file change — the mtime
    key handles it automatically."""
    key_base = _cache_key()
    if key_base is None:
        return []
    cache_key = (key_base[0], key_base[1])
    cached = _CACHE.get(cache_key)
    if cached is None:
        cached = list_protocols(project_name=project_name) or []
        _CACHE[cache_key] = cached
        return cached
    # Refilter for the specific project_name — the cache holds the
    # unfiltered verified-chain walk result.
    return [
        env for env in cached
        if isinstance(env.get("payload"), dict)
        and (env["payload"].get("context_signature", {}) or {}).get("project_name")
        == project_name
    ]


def _clear_cache_for_tests() -> None:
    _CACHE.clear()


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------


def query_top_k(
    candidate_signature: ContextSignature,
    *,
    k: int = 3,
    cwd: Path,
    min_overlap: int | None = None,
) -> list[GuidanceMatch]:
    """Ranked-with-disclosure helper — Event 86 / CP-ACTIVE-GUIDANCE-
    RANKING-AUDIT-01. Returns the top-K matching protocols (descending
    by overlap, then ts) instead of just the top-1.

    Spec: kernel/ACTIVE_GUIDANCE_RANKING.md. Operators use this for
    forensic / spot-check / 'why did the kernel surface THIS protocol?'
    workflows. The hot-path `query()` (single-result) remains the
    primary active-guidance API.
    """
    threshold = min_overlap if min_overlap is not None else load_min_overlap(cwd)
    try:
        protocols = _load_protocols_cached(candidate_signature.project_name)
    except Exception:
        return []
    if not protocols:
        return []

    vapor_cids = _build_vapor_correlation_set()

    ranked: list[tuple[int, str, dict]] = []
    for envelope in protocols:
        if not isinstance(envelope, dict):
            continue
        payload = envelope.get("payload")
        if not isinstance(payload, dict):
            continue
        cid = payload.get("correlation_id")
        if isinstance(cid, str) and cid in vapor_cids:
            continue
        stored = payload.get("context_signature")
        if not isinstance(stored, dict):
            continue
        overlap = field_overlap(candidate_signature, {"context_signature": stored})
        if overlap < threshold:
            continue
        ts = str(envelope.get("ts") or "")
        ranked.append((overlap, ts, payload))

    if not ranked:
        return []
    # Same sort as `query`: primary = overlap desc (specificity);
    # secondary = ts desc (recency tiebreaker). Anti-Doxa: NO
    # popularity / use-count / frequency input. Audit doc:
    # kernel/ACTIVE_GUIDANCE_RANKING.md.
    ranked.sort(key=lambda t: (t[0], t[1]), reverse=True)
    matches: list[GuidanceMatch] = []
    for overlap_val, ts_val, payload_val in ranked[:k]:
        matches.append(GuidanceMatch(
            protocol_payload=payload_val,
            overlap=overlap_val,
            synthesized_at=ts_val,
            correlation_id=str(payload_val.get("correlation_id") or ""),
        ))
    return matches


def query(
    candidate_signature: ContextSignature,
    *,
    cwd: Path,
    min_overlap: int | None = None,
) -> GuidanceMatch | None:
    """Return the top-ranked matching protocol or None when the
    threshold is not met.

    Pipeline:
      1. Load project-scoped protocols (verified chain walk, cached).
      2. Build the vapor-verdict filter set from CP8's spot-check queue.
      3. For each protocol: compute field_overlap, skip if cid in vapor set.
      4. Rank by (overlap desc, ts desc).
      5. Return top iff ``overlap >= min_overlap``.
    """
    threshold = min_overlap if min_overlap is not None else load_min_overlap(cwd)
    try:
        protocols = _load_protocols_cached(candidate_signature.project_name)
    except Exception:
        return None
    if not protocols:
        return None

    vapor_cids = _build_vapor_correlation_set()

    ranked: list[tuple[int, str, dict]] = []
    for envelope in protocols:
        if not isinstance(envelope, dict):
            continue
        payload = envelope.get("payload")
        if not isinstance(payload, dict):
            continue
        cid = payload.get("correlation_id")
        if isinstance(cid, str) and cid in vapor_cids:
            continue
        stored = payload.get("context_signature")
        if not isinstance(stored, dict):
            continue
        overlap = field_overlap(candidate_signature, {"context_signature": stored})
        if overlap < threshold:
            continue
        ts = str(envelope.get("ts") or "")
        ranked.append((overlap, ts, payload))

    if not ranked:
        return None
    ranked.sort(key=lambda t: (t[0], t[1]), reverse=True)
    top_overlap, top_ts, top_payload = ranked[0]
    return GuidanceMatch(
        protocol_payload=top_payload,
        overlap=top_overlap,
        synthesized_at=top_ts,
        correlation_id=str(top_payload.get("correlation_id") or ""),
    )


# ---------------------------------------------------------------------------
# Advisory formatting
# ---------------------------------------------------------------------------


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def format_advisory(match: GuidanceMatch) -> str:
    """Return the single-stderr-write guidance line. Two physical
    lines (header + body), one logical advisory."""
    blueprint = str(match.protocol_payload.get("blueprint") or "unknown_blueprint")
    date = match.synthesized_at[:10] if len(match.synthesized_at) >= 10 else match.synthesized_at
    cid_prefix = (match.correlation_id or "")[:_CID_PREFIX_CHARS]
    protocol_text = str(
        match.protocol_payload.get("synthesized_protocol") or ""
    ).strip()
    truncated = _truncate(protocol_text, _ADVISORY_PROTOCOL_MAX_CHARS)
    header = (
        f"[episteme guide] {date} · {blueprint} · "
        f"overlap={match.overlap}/6 · cid={cid_prefix}"
    )
    return f"{header}\n  Protocol: {truncated}"
