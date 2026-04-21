#!/usr/bin/env python3
"""Phase 12 · profile-audit loop — scaffolding (checkpoint 1 of 5).

Audit the declared operator profile (core/memory/global/operator_profile.md)
against the lived episodic record (~/.episteme/memory/episodic/*.jsonl).
Surface drift as re-elicitation, never as auto-mutation. Closes the
v0.11.0 circuit started by phases 9–11: phase 9 made the profile shape
hook behavior; phase 12 checks whether that shaping is honest against
what actually got done.

Spec: docs/DESIGN_V0_11_PHASE_12.md  (status: approved 2026-04-20)
Schema: core/schemas/profile-audit/profile_audit_v1.json
Lexicon: kernel/PHASE_12_LEXICON.md  (operator override:
         core/memory/global/phase_12_lexicon.md)

Four D-countermeasures from the spec, traced in this module:

- **D1 · multi-signature convergence.** Axes A, B, C, D each define ≥ 2
  signatures; drift requires ≥ 2 misaligned (C allows single-signature
  flagging on catastrophic fence violations — a named exception, not a
  relaxation). No single feature can trip a drift flag for a generic axis.
  Ships in checkpoints 2–5; this scaffolding returns all-axes
  `insufficient_evidence`.
- **D2 · retrospective-only.** `run_audit()` reads records already
  written by the phase 10 episodic writer. It is never invoked from a
  PreToolUse hook. Signatures are not visible to the agent at
  decision-time; the audit is post-hoc by design.
- **D3 · re-elicitation not correction.** This module writes to
  `~/.episteme/memory/reflective/profile_audit.jsonl` only. It NEVER
  mutates `core/memory/global/operator_profile.md`. Profile edits remain
  operator-exclusive.
- **D4 · named limit.** The spec's §Known Gaming Vectors section names
  four ways a sufficiently-aware agent can defeat this loop. Phase 12 is
  one layer in a defense-in-depth story (operator review, Fence-Check,
  cognitive-adoption RC gates) — not a sufficient safeguard alone.

Checkpoint 1 ships the scaffolding: all 15 axes return `insufficient_evidence`
with a pointer to the spec's sketch table. Axes C, A, D, B get real
signatures in checkpoints 2, 3, 4, 5 respectively. The remaining 11 ship
as explicit per-axis stubs (not a single generic branch) so the audit
log is readable and the drift-surfacing path is exercised even when most
axes are un-implemented.
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal, TypedDict


REPO_ROOT = Path(__file__).resolve().parents[2]

# Profile axis inventory — order matches kernel/OPERATOR_PROFILE_SCHEMA.md
# sections 4a (process) and 4b (cognitive-style). Exactly 15 axes, per the
# profile-audit-v1 JSON schema's minItems/maxItems constraint.
PROCESS_AXES: tuple[str, ...] = (
    "planning_strictness",
    "risk_tolerance",
    "testing_rigor",
    "parallelism_preference",
    "documentation_rigor",
    "automation_level",
)
COGNITIVE_AXES: tuple[str, ...] = (
    "dominant_lens",
    "noise_signature",
    "abstraction_entry",
    "decision_cadence",
    "explanation_depth",
    "feedback_mode",
    "uncertainty_tolerance",
    "asymmetry_posture",
    "fence_discipline",
)
ALL_AXES: tuple[str, ...] = PROCESS_AXES + COGNITIVE_AXES


Verdict = Literal["aligned", "drift", "insufficient_evidence"]
Confidence = Literal["high", "medium", "low"]


class AxisAuditResult(TypedDict):
    axis_name: str
    claim: Any  # str / int / list / dict / None depending on axis + declaration
    verdict: Verdict
    evidence_count: int
    signatures: dict[str, float]
    signature_predictions: dict[str, list[float]]  # [low, high]
    confidence: Confidence
    evidence_refs: list[str]
    reason: str
    suggested_reelicitation: str | None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def run_audit(
    *,
    episodic_dir: Path | None = None,
    reflective_dir: Path | None = None,
    profile_path: Path | None = None,
    lexicon_path: Path | None = None,
    since_days: int = 30,
    _now: datetime | None = None,  # test seam
) -> dict[str, Any]:
    """Run the profile audit. Returns a profile-audit-v1 record.

    At checkpoint 1, every axis returns `insufficient_evidence` with a
    reason naming the spec's sketch table. This is the correct behavior
    per spec §Cold-start (first weeks of usage) — the audit honestly
    reports when it has nothing to say.

    Never raises on missing inputs. An absent episodic dir, absent
    profile, or absent lexicon all degrade to a well-formed record with
    a descriptive reason per axis — the surfacing pipeline stays alive
    even when the substrate is empty.

    D2 · retrospective-only: this function only reads. It never writes
    (the caller — `episteme profile audit --write` — handles persistence).
    """
    episodic_dir = episodic_dir or (Path.home() / ".episteme" / "memory" / "episodic")
    reflective_dir = reflective_dir or (Path.home() / ".episteme" / "memory" / "reflective")
    profile_path = profile_path or (REPO_ROOT / "core" / "memory" / "global" / "operator_profile.md")
    lexicon_path = lexicon_path or _resolve_lexicon_path()

    now = _now or datetime.now(timezone.utc)
    run_ts = now.isoformat()
    run_id = f"audit-{now.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"

    records = _load_episodic_records(episodic_dir, since_days, now=now)
    claims = _load_profile_claims(profile_path)
    lexicon = _load_lexicon(lexicon_path)
    lexicon_fp = _lexicon_fingerprint(lexicon)

    axes: list[AxisAuditResult] = [
        _audit_axis(axis, claims.get(axis), records, lexicon) for axis in ALL_AXES
    ]

    return {
        "version": "profile-audit-v1",
        "run_id": run_id,
        "run_ts": run_ts,
        "episodic_window": f"{since_days}d",
        "lexicon_fingerprint": lexicon_fp,
        "axes": axes,
        "acknowledged": False,
    }


# ---------------------------------------------------------------------------
# Per-axis dispatch
# ---------------------------------------------------------------------------


def _audit_axis(
    axis_name: str,
    claim: Any,
    records: list[dict],
    lexicon: dict[str, frozenset[str]],
) -> AxisAuditResult:
    handler = _AXIS_HANDLERS.get(axis_name, _axis_stub)
    return handler(axis_name, claim, records, lexicon)


def _axis_stub(
    axis_name: str,
    claim: Any,
    records: list[dict],
    lexicon: dict[str, frozenset[str]],
) -> AxisAuditResult:
    """Default handler — ships for every axis at checkpoint 1 and stays
    the handler for the 11 axes deferred to 0.11.1.

    Reason field points to the spec's sketch-table row for that axis so
    the audit log is readable and self-documenting — a maintainer reading
    a `15 × insufficient_evidence` record sees exactly which spec entry
    governs each axis, not an undifferentiated wall of 'not implemented'.
    """
    sketch_ref = _SKETCH_TABLE_REFS.get(axis_name, "docs/DESIGN_V0_11_PHASE_12.md § Remaining axes")
    return AxisAuditResult(
        axis_name=axis_name,
        claim=claim,
        verdict="insufficient_evidence",
        evidence_count=0,
        signatures={},
        signature_predictions={},
        confidence="low",
        evidence_refs=[],
        reason=(
            f"Axis '{axis_name}' is stubbed at checkpoint 1 scaffolding. "
            f"Signatures specified at {sketch_ref}. Checkpoint 2-5 implement "
            f"the four deeply-worked axes; the remaining 11 ship as "
            f"insufficient_evidence until 0.11.1."
        ),
        suggested_reelicitation=None,
    )


# ---------------------------------------------------------------------------
# Axis C · fence_discipline  (checkpoint 2)
# ---------------------------------------------------------------------------
#
# Spec: docs/DESIGN_V0_11_PHASE_12.md § Axis C.
#
# Operational definition — when the agent proposes removing a constraint
# (deleting from .episteme/*, core/hooks/*, CONSTITUTION.md / POLICY.md,
# or a lockfile), the Reasoning Surface must (S1) explain why the
# constraint was there and (S2) name what would break if removed.
#
# D1 EXCEPTION (named in spec): fence_discipline is one of two axes where
# single-signature flagging is allowed. Constraint removal is high-impact
# and the false-negative cost of waiting for both S1 AND S2 to miss
# exceeds the false-positive cost of flagging early on either.

# Substring tokens. A command is a constraint-removal candidate iff it
# names one of these paths AND contains a removal-like verb. Substring
# match (not fnmatch) because episodic records store the exact command
# text — leading ./ or trailing characters do not need special handling.
_CONSTRAINT_PATH_TOKENS: tuple[str, ...] = (
    ".episteme/",
    "core/hooks/",
    "CONSTITUTION.md",
    "POLICY.md",
    "package-lock.json",
    "poetry.lock",
    "Cargo.lock",
    "yarn.lock",
    "pnpm-lock.yaml",
    "uv.lock",
)

# Removal-like verbs. A redirect `>` alone would be too loose; we anchor
# it against a path-token co-occurrence via _is_constraint_removal.
_REMOVAL_VERB_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\brm\s+(?:-[a-zA-Z]+\s+)*"),
    re.compile(r"\bgit\s+rm\b"),
    re.compile(r"\bgit\s+reset\s+--hard\b"),
    re.compile(r"\bgit\s+revert\b"),
    re.compile(r"\bgit\s+checkout\s+--\s"),
    re.compile(r"\bgit\s+restore\b"),
    re.compile(r"\bsed\s+-i\b"),
    re.compile(r"\bperl\s+-i\b"),
    re.compile(r"\btruncate\s+-s\s*0\b"),
    # Single `>` redirect = overwrite. The `>>` append form is explicitly
    # excluded so log-appending does not count as removal.
    re.compile(r"(?<!>)>(?!>)"),
)

# S1 · reconstruction markers. Deliberately narrow phrase set + commit
# hash / audit-entry back-references. Goodhart applies here too: a
# sufficiently-aware agent could pad knowns with "this constraint exists
# because ..." filler. S2 is the D1-adjacent counter (even though the
# axis allows single-signature flags, an agent that passes both must do
# both, and the two probes are independent enough to be costly to fake).
_RECONSTRUCTION_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"this\s+constraint\s+exists\s+because", re.I),
    re.compile(r"this\s+was\s+added\s+to\s+counter", re.I),
    re.compile(r"added\s+to\s+counter", re.I),
    re.compile(r"originally\s+added\s+to", re.I),
    re.compile(r"\bto\s+prevent\s+\S+", re.I),
    re.compile(r"\bto\s+guard\s+against\b", re.I),
    # Commit SHA (7-40 hex) — evidence-ref convention.
    re.compile(r"\b[0-9a-f]{7,40}\b"),
    re.compile(r"audit\s+entry", re.I),
    re.compile(r"prior\s+audit", re.I),
    re.compile(r"chesterton", re.I),
)

# S2 · counterfactual / review-trace markers. "What would break if we
# remove this" — the blast-radius probe.
_COUNTERFACTUAL_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"if\s+(?:we\s+)?remove(?:d)?\s+this", re.I),
    re.compile(r"removing\s+this\s+would", re.I),
    re.compile(r"\bif\s+removed\b", re.I),
    re.compile(r"\bblast\s+radius\b", re.I),
    re.compile(r"what\s+would\s+break", re.I),
    re.compile(r"would\s+break\s+if", re.I),
    re.compile(r"regression\s+risk", re.I),
    re.compile(r"review[- ]trace", re.I),
)


def _is_constraint_removal(record: dict) -> bool:
    """True iff the record's command targets a constraint-governed path
    with a removal-like verb. FP-averse by requiring co-occurrence."""
    details = record.get("details")
    if not isinstance(details, dict):
        return False
    cmd = details.get("command")
    if not isinstance(cmd, str) or not cmd:
        return False
    if not any(tok in cmd for tok in _CONSTRAINT_PATH_TOKENS):
        return False
    return any(pat.search(cmd) for pat in _REMOVAL_VERB_PATTERNS)


def _surface_text(record: dict, field: str) -> str:
    """Flatten a reasoning-surface field (list-of-strings or string) to
    one searchable blob. Returns '' if the field is absent or malformed.
    """
    details = record.get("details")
    if not isinstance(details, dict):
        return ""
    surface = details.get("reasoning_surface")
    if not isinstance(surface, dict):
        return ""
    value = surface.get(field)
    if isinstance(value, list):
        return " ".join(str(v) for v in value if v)
    if isinstance(value, str):
        return value
    return ""


def _has_reconstruction(record: dict) -> bool:
    """S1 probe — does the knowns field carry a reconstruction of WHY
    the constraint existed?"""
    text = _surface_text(record, "knowns")
    if not text:
        return False
    return any(pat.search(text) for pat in _RECONSTRUCTION_PATTERNS)


def _has_counterfactual(record: dict) -> bool:
    """S2 probe — do assumptions name what would break on removal?
    Falls back to scanning `unknowns` + `disconfirmation` as well, since
    a thoughtful blast-radius can land in any of those fields."""
    blob = " ".join(
        _surface_text(record, f)
        for f in ("assumptions", "unknowns", "disconfirmation")
    )
    if not blob:
        return False
    return any(pat.search(blob) for pat in _COUNTERFACTUAL_PATTERNS)


def _correlation_ref(record: dict) -> str | None:
    """Extract the record's correlation_id from provenance.evidence_refs,
    falling back to the record id. Keeps the evidence_refs field readable
    when the audit is inspected by a human."""
    prov = record.get("provenance")
    if isinstance(prov, dict):
        refs = prov.get("evidence_refs")
        if isinstance(refs, list):
            for r in refs:
                if isinstance(r, str) and r.startswith("correlation_id:"):
                    return r[len("correlation_id:"):]
    rid = record.get("id")
    return rid if isinstance(rid, str) else None


def _collect_evidence_refs(records: list[dict], cap: int = 20) -> list[str]:
    """Cap at 20 per profile_audit_v1.json schema description."""
    refs: list[str] = []
    for rec in records:
        ref = _correlation_ref(rec)
        if ref:
            refs.append(ref)
        if len(refs) >= cap:
            break
    return refs


_EVIDENCE_MINIMUM = 5


# Claim-to-band map. Each band is [drift_floor, ideal_ceiling] — observed
# rate below drift_floor = drift; within the band = aligned. The floor
# doubles as the threshold so there is no magic absolute constant; the
# claim IS the threshold.
#
# Anchored at claim 4 to the spec's §Axis C absolute values (S1 floor
# 0.70, S2 floor 0.50), so the maintainer's declared `fence_discipline: 4`
# produces exactly the spec's named threshold. Lower claims scale the
# floor down — e.g. an operator declaring `fence_discipline: 0` cannot
# drift by under-performing because the floor is 0.0: the claim already
# names near-absent practice, so 10% reconstruction is aligned with that
# claim, not a drift signal. The spec's principle — drift is the delta
# between claim and lived record — becomes load-bearing in this table.
_FENCE_BANDS_BY_CLAIM: dict[int, dict[str, list[float]]] = {
    0: {"S1_reconstruction_rate": [0.00, 0.30], "S2_review_trace_rate": [0.00, 0.15]},
    1: {"S1_reconstruction_rate": [0.10, 0.45], "S2_review_trace_rate": [0.05, 0.25]},
    2: {"S1_reconstruction_rate": [0.25, 0.65], "S2_review_trace_rate": [0.15, 0.40]},
    3: {"S1_reconstruction_rate": [0.50, 0.80], "S2_review_trace_rate": [0.30, 0.55]},
    4: {"S1_reconstruction_rate": [0.70, 1.00], "S2_review_trace_rate": [0.50, 1.00]},
    5: {"S1_reconstruction_rate": [0.90, 1.00], "S2_review_trace_rate": [0.90, 1.00]},
}


def _fence_discipline_predictions(claim: Any) -> dict[str, list[float]]:
    """Claim-dependent [drift_floor, ideal_ceiling] bands per signature.

    Non-integer or missing claim ⇒ empty dict, which downstream signals
    "no numeric claim to audit against" (we compute signatures for the
    operator's information but cannot compute drift)."""
    if not isinstance(claim, int):
        return {}
    key = max(0, min(5, claim))
    # Copy so callers cannot mutate the shared table.
    return {k: list(v) for k, v in _FENCE_BANDS_BY_CLAIM[key].items()}


def _axis_fence_discipline(
    axis_name: str,
    claim: Any,
    records: list[dict],
    lexicon: dict[str, frozenset[str]],
) -> AxisAuditResult:
    removals = [r for r in records if _is_constraint_removal(r)]
    n = len(removals)
    evidence_refs = _collect_evidence_refs(removals)
    predictions = _fence_discipline_predictions(claim)

    if n < _EVIDENCE_MINIMUM:
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="insufficient_evidence",
            evidence_count=n,
            signatures={},
            signature_predictions=predictions,
            confidence="low",
            evidence_refs=evidence_refs,
            reason=(
                f"Only {n} constraint-removal record(s) in window "
                f"(need ≥ {_EVIDENCE_MINIMUM} per docs/"
                f"DESIGN_V0_11_PHASE_12.md § Axis C · Evidence minimum). "
                f"Keep accumulating; single-signature flagging cannot "
                f"fire below the minimum."
            ),
            suggested_reelicitation=None,
        )

    s1_hits = sum(1 for r in removals if _has_reconstruction(r))
    s2_hits = sum(1 for r in removals if _has_counterfactual(r))
    s1_rate = s1_hits / n
    s2_rate = s2_hits / n
    signatures = {
        "S1_reconstruction_rate": round(s1_rate, 3),
        "S2_review_trace_rate": round(s2_rate, 3),
    }
    confidence: Confidence = "high" if n >= 10 else "medium"

    if not predictions:
        # No numeric claim declared — nothing to drift against. The
        # record surfaces the observed rates so the operator can
        # elicit a value, but the audit does not flag.
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="aligned",
            evidence_count=n,
            signatures=signatures,
            signature_predictions={},
            confidence=confidence,
            evidence_refs=evidence_refs,
            reason=(
                f"Across {n} constraint-removal record(s): "
                f"reconstruction rate {s1_rate:.0%}, review-trace rate "
                f"{s2_rate:.0%}. No numeric fence_discipline claim "
                f"declared, so no drift can be computed; report is "
                f"informational. Declare a 0-5 score in the operator "
                f"profile to enable drift detection."
            ),
            suggested_reelicitation=None,
        )

    s1_floor = predictions["S1_reconstruction_rate"][0]
    s2_floor = predictions["S2_review_trace_rate"][0]
    s1_drift = s1_rate < s1_floor
    s2_drift = s2_rate < s2_floor

    if s1_drift or s2_drift:
        misses: list[str] = []
        if s1_drift:
            misses.append(
                f"reconstruction rate {s1_rate:.0%} < "
                f"{s1_floor:.0%} floor for claim={claim!r}"
            )
        if s2_drift:
            misses.append(
                f"review-trace rate {s2_rate:.0%} < "
                f"{s2_floor:.0%} floor for claim={claim!r}"
            )
        reason = (
            f"Across {n} constraint-removal record(s): "
            + "; ".join(misses)
            + ". Spec §Axis C permits single-signature flagging because "
            "constraint-removal is high-consequence."
        )
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="drift",
            evidence_count=n,
            signatures=signatures,
            signature_predictions=predictions,
            confidence=confidence,
            evidence_refs=evidence_refs,
            reason=reason,
            suggested_reelicitation=(
                "Re-elicit fence_discipline: are constraint removals "
                "actually accompanied by reconstruction + review-trace, "
                "or is the declared score aspirational? Inspect the "
                "flagged records and either tighten practice or lower "
                "the score."
            ),
        )

    return AxisAuditResult(
        axis_name=axis_name,
        claim=claim,
        verdict="aligned",
        evidence_count=n,
        signatures=signatures,
        signature_predictions=predictions,
        confidence=confidence,
        evidence_refs=evidence_refs,
        reason=(
            f"Across {n} constraint-removal record(s): reconstruction "
            f"rate {s1_rate:.0%} ≥ {s1_floor:.0%} floor, review-trace "
            f"rate {s2_rate:.0%} ≥ {s2_floor:.0%} floor for "
            f"claim={claim!r}. Claim holds against lived record."
        ),
        suggested_reelicitation=None,
    )


# ---------------------------------------------------------------------------
# Axis A · dominant_lens (checkpoint 3)
# ---------------------------------------------------------------------------
#
# Spec: docs/DESIGN_V0_11_PHASE_12.md § Axis A.
#
# `dominant_lens` is an ordered list; we audit position 0. CP3 operationalizes
# the `failure-first` value only — position-0 values other than failure-first
# return insufficient_evidence with a pointer to the 0.11.1 work that covers
# them. This matches the spec's "four worked axes first, sketched pattern for
# the rest" discipline.
#
# Two signatures:
#
#   S1 · failure-frame RATIO over unknowns + disconfirmation. Aggregate
#        token counts across qualifying records. Claim `failure-first`
#        predicts > 0.6; drift floor 0.45 (25% proportional shortfall).
#
#   S2 · fire-condition RATE across disconfirmation classifier. Each
#        record's `disconfirmation` → one of {fire, absence, tautological,
#        unknown}. Fire = conditional trigger (if/when/should/once/after)
#        AND a specific observable (numeric threshold, metric name,
#        failure verb). Absence beats fire — a clause like "if nothing
#        fails" is absence, not fire, even though it contains `fails`.
#        Claim predicts ≥ 0.70 fire-rate; drift floor 0.55.
#
# D1 convergence STRICT for Axis A: both S1 AND S2 must miss their floors
# to flag drift. A single-signature miss is logged in the record but does
# not trigger re-elicitation. This is the named default (Axis C's single-
# signature exception is the anomaly).

# Classifier rule sets. Compiled once at module load. Absence checked
# FIRST so "if nothing unexpected happens" routes away from fire — the
# whole point of the axis is that absence-conditions are the wrong shape
# for a failure-first operator.
_ABSENCE_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\bif\s+no(?:body|\s+one|\s+\w+)\s+(?:complain|object|notice|report|flag|raise|push\s+back)", re.I),
    re.compile(r"\bnothing\s+(?:unexpected|fails?|breaks?|changes|goes\s+wrong|surfaces?)", re.I),
    re.compile(r"\bno\s+(?:issues?|errors?|failures?|complaints?|problems?|regressions?)\s+(?:appear|arise|emerge|occur|surface|show\s+up)", re.I),
    re.compile(r"\b(?:everything|all)\s+(?:is|stays|remains|looks)\s+(?:fine|ok|okay|green|normal|healthy)", re.I),
    re.compile(r"\babsence\s+of\b", re.I),
    re.compile(r"\bno\s+one\s+(?:notices|complains|reports|pushes\s+back)", re.I),
    re.compile(r"\bif\s+no\s+alarm", re.I),
)

# Conditional triggers — the "if / when / should / once / after / unless"
# that opens a predicted-outcome clause.
_CONDITIONAL_TRIGGER_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\bif\b", re.I),
    re.compile(r"\bwhen\b", re.I),
    re.compile(r"\bshould\b", re.I),
    re.compile(r"\bonce\b", re.I),
    re.compile(r"\bafter\b", re.I),
    re.compile(r"\bunless\b", re.I),
)

# Specific observables — numeric thresholds, metric references, failure
# verbs naming something that can be watched for.
_OBSERVABLE_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\d+\s*%"),
    re.compile(r"\d+\s*(?:ms|sec|seconds?|min|minutes?|h|hours?|MB|GB|KB|rps|qps|errors?)\b", re.I),
    re.compile(r"\b(?:exceeds?|drops?|rises?|passes?|crosses?|hits?|reaches?|exceeds?)\s+\d"),
    re.compile(r"\b(?:fails?|errors?|times?\s*out|crashes?|exits?|panics?|throws?|rejects?|returns?\s+non-?zero|non-?zero\s+exit)\b", re.I),
    re.compile(r"\b(?:log\s+shows?|query[- ]log|telemetry|ci|pipeline|build|test\s+suite|audit\s+log)\b", re.I),
    re.compile(r"\bexit\s*code\b", re.I),
    re.compile(r"\bwithin\s+\d", re.I),
    re.compile(r"\b(?:p50|p90|p95|p99|latency|throughput|error\s+rate|regression)\b", re.I),
    re.compile(r"\b(?:returns?|responds?\s+with|produces?)\s+\S"),
)


DisconfirmationClass = Literal["fire", "absence", "tautological", "unknown"]


def _classify_disconfirmation(text: Any) -> DisconfirmationClass:
    """Syntactic classifier for a Reasoning Surface's `disconfirmation`
    field. Priority: absence > fire > tautological > unknown.

    - `unknown` reserved for empty / very-short content (< 10 chars) —
      we decline to classify rather than guess.
    - `absence` fires first so clauses like "if nothing breaks" do not
      get mis-classified as fire just because they contain 'breaks'.
    - `fire` requires a conditional trigger AND a specific observable —
      either alone is tautological.
    - everything else → `tautological` (pattern-matches the 'restates
      the knowns' case without a false-positive risk).
    """
    if not isinstance(text, str):
        return "unknown"
    stripped = text.strip()
    if len(stripped) < 10:
        return "unknown"

    low = stripped.lower()
    if any(pat.search(low) for pat in _ABSENCE_PATTERNS):
        return "absence"

    has_trigger = any(pat.search(low) for pat in _CONDITIONAL_TRIGGER_PATTERNS)
    has_observable = any(pat.search(low) for pat in _OBSERVABLE_PATTERNS)
    if has_trigger and has_observable:
        return "fire"
    return "tautological"


def _count_lexicon_hits(text: str, terms: frozenset[str]) -> int:
    """Count term occurrences in text. Multi-word terms are matched as
    word-boundary phrases; single-word terms as word-boundary lookups.
    Case-insensitive. Returns 0 on empty input or empty lexicon.

    Mirrors the PHASE_12_LEXICON.md 'whitespace-collapsed, multi-word as
    regex word-boundary phrases' match rule.
    """
    if not text or not terms:
        return 0
    # Collapse whitespace to match the lexicon's normalization rule.
    normalized = re.sub(r"\s+", " ", text.lower())
    hits = 0
    for term in terms:
        if not term:
            continue
        tl = term.lower()
        # Single pattern either way — re.escape + \b boundaries handles
        # multi-word terms cleanly because spaces are literal between
        # word characters.
        pattern = r"\b" + re.escape(tl) + r"\b"
        hits += len(re.findall(pattern, normalized))
    return hits


def _axis_a_qualifying(record: dict) -> tuple[bool, list[str], str]:
    """Return (qualifies, unknowns_list, disconfirmation_text). A record
    qualifies for Axis A when it has both non-empty unknowns and
    non-empty disconfirmation per spec §Axis A Evidence minimum."""
    details = record.get("details")
    if not isinstance(details, dict):
        return False, [], ""
    surface = details.get("reasoning_surface")
    if not isinstance(surface, dict):
        return False, [], ""
    unknowns = surface.get("unknowns")
    if not isinstance(unknowns, list):
        return False, [], ""
    unknowns_str = [str(u) for u in unknowns if isinstance(u, str) and u.strip()]
    if not unknowns_str:
        return False, [], ""
    disconf = surface.get("disconfirmation")
    if not isinstance(disconf, str) or not disconf.strip():
        return False, [], ""
    return True, unknowns_str, disconf


_AXIS_A_EVIDENCE_MINIMUM = 20

# Claim-anchored prediction bands for dominant_lens[0] = failure-first.
# Floor = drift threshold, ceiling = 1.0 (perfect alignment with claim).
# Per spec §Axis A: S1 predicts > 0.6 with drift floor 0.45; S2 predicts
# ≥ 0.70 with drift floor 0.55.
_FAILURE_FIRST_PREDICTIONS: dict[str, list[float]] = {
    "S1_failure_frame_ratio": [0.45, 1.00],
    "S2_fire_condition_rate": [0.55, 1.00],
}


def _extract_dominant_lens_primary(claim: Any) -> str | None:
    """Return position-0 lens value, or None if the claim is missing /
    malformed. `dominant_lens` is declared as an ordered list in the
    profile; position 0 is the dominant lens the operator commits to."""
    if isinstance(claim, list) and claim:
        first = claim[0]
        if isinstance(first, str) and first.strip():
            return first.strip()
    return None


def _axis_dominant_lens(
    axis_name: str,
    claim: Any,
    records: list[dict],
    lexicon: dict[str, frozenset[str]],
) -> AxisAuditResult:
    primary = _extract_dominant_lens_primary(claim)

    # Claim absent / malformed → no axis identity to audit. dominant_lens
    # is categorical (a named lens), so without a claim there is no test
    # to run — different from Axis C where a null claim can still
    # surface observed rates informationally. Here we return
    # insufficient_evidence per the CP1 baseline convention for un-
    # auditable axes, so the report reads consistently with the other
    # 11 un-implemented axes on a blank profile.
    if primary is None:
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="insufficient_evidence",
            evidence_count=0,
            signatures={},
            signature_predictions={},
            confidence="low",
            evidence_refs=[],
            reason=(
                "No dominant_lens claim declared at position 0 per "
                "docs/DESIGN_V0_11_PHASE_12.md § Axis A. CP3 audits "
                "the primary (position-0) lens; without a named lens "
                "there is no hypothesis to test."
            ),
            suggested_reelicitation=None,
        )

    # CP3 implements only failure-first. Other lens values at position 0
    # ship as insufficient_evidence with a spec sketch-table pointer.
    if primary != "failure-first":
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="insufficient_evidence",
            evidence_count=0,
            signatures={},
            signature_predictions={},
            confidence="low",
            evidence_refs=[],
            reason=(
                f"Position-0 claim is {primary!r}. CP3 operationalizes "
                f"only 'failure-first' as position 0; other lenses "
                f"follow Template A per docs/DESIGN_V0_11_PHASE_12.md "
                f"§ sketch table and ship in 0.11.1."
            ),
            suggested_reelicitation=None,
        )

    # S1 + S2 path — claim is `failure-first` at position 0.
    failure_terms = lexicon.get("failure_frame", frozenset())
    success_terms = lexicon.get("success_frame", frozenset())

    qualifying: list[dict] = []
    total_failure = 0
    total_success = 0
    fire_count = 0
    absence_count = 0

    for rec in records:
        ok, unknowns_list, disconf = _axis_a_qualifying(rec)
        if not ok:
            continue
        qualifying.append(rec)
        blob = " ".join(unknowns_list) + " " + disconf
        total_failure += _count_lexicon_hits(blob, failure_terms)
        total_success += _count_lexicon_hits(blob, success_terms)
        cls = _classify_disconfirmation(disconf)
        if cls == "fire":
            fire_count += 1
        elif cls == "absence":
            absence_count += 1

    n = len(qualifying)
    evidence_refs = _collect_evidence_refs(qualifying)
    predictions = _FAILURE_FIRST_PREDICTIONS

    if n < _AXIS_A_EVIDENCE_MINIMUM:
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="insufficient_evidence",
            evidence_count=n,
            signatures={},
            signature_predictions=predictions,
            confidence="low",
            evidence_refs=evidence_refs,
            reason=(
                f"Only {n} qualifying record(s) with non-empty unknowns "
                f"+ disconfirmation in window (need ≥ "
                f"{_AXIS_A_EVIDENCE_MINIMUM} per docs/"
                f"DESIGN_V0_11_PHASE_12.md § Axis A · Evidence minimum). "
                f"Keep accumulating; Axis A requires D1 convergence on "
                f"two signatures so the volume floor is higher than C."
            ),
            suggested_reelicitation=None,
        )

    # S1 — aggregate token ratio. Zero-denominator guard: an operator
    # whose qualifying records contain NO failure/success lexicon hits
    # has no signal; we cannot say drift, we cannot say aligned.
    denom = total_failure + total_success
    if denom == 0:
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="insufficient_evidence",
            evidence_count=n,
            signatures={},
            signature_predictions=predictions,
            confidence="low",
            evidence_refs=evidence_refs,
            reason=(
                f"{n} qualifying record(s) but zero failure-frame or "
                f"success-frame lexicon hits across all of them. "
                f"Signature S1 cannot be computed against an empty "
                f"token base."
            ),
            suggested_reelicitation=None,
        )
    s1_rate = total_failure / denom
    s2_rate = fire_count / n
    absence_rate = absence_count / n

    signatures = {
        "S1_failure_frame_ratio": round(s1_rate, 3),
        "S2_fire_condition_rate": round(s2_rate, 3),
        "S2_absence_condition_rate": round(absence_rate, 3),
    }

    s1_floor = predictions["S1_failure_frame_ratio"][0]
    s2_floor = predictions["S2_fire_condition_rate"][0]
    s1_drift = s1_rate < s1_floor
    s2_drift = s2_rate < s2_floor
    confidence: Confidence = "high" if n >= 40 else "medium"

    # D1 convergence — both must miss.
    if s1_drift and s2_drift:
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="drift",
            evidence_count=n,
            signatures=signatures,
            signature_predictions=predictions,
            confidence=confidence,
            evidence_refs=evidence_refs,
            reason=(
                f"Across {n} qualifying record(s): failure-frame ratio "
                f"{s1_rate:.0%} < {s1_floor:.0%} floor AND fire-condition "
                f"rate {s2_rate:.0%} < {s2_floor:.0%} floor. Claim "
                f"'failure-first' at position 0 not borne out by the "
                f"lived record. D1 convergence confirmed — both "
                f"signatures missed."
            ),
            suggested_reelicitation=(
                "Re-elicit dominant_lens[0]: is 'failure-first' the "
                "actual dominant lens, or is the claim aspirational? "
                "Consider re-ordering to 'causal-chain' or "
                "'first-principles' if those better match the record."
            ),
        )

    # One-or-none signatures miss → aligned per D1. Emit reason that
    # names the single-signature miss so the operator can see partial
    # evidence without the audit pretending to certainty it lacks.
    single_miss_note = ""
    if s1_drift:
        single_miss_note = (
            f" S1 single-signature miss noted "
            f"({s1_rate:.0%} < {s1_floor:.0%}); D1 convergence "
            f"requires BOTH to flag, so no drift."
        )
    elif s2_drift:
        single_miss_note = (
            f" S2 single-signature miss noted "
            f"({s2_rate:.0%} < {s2_floor:.0%}); D1 convergence "
            f"requires BOTH to flag, so no drift."
        )

    return AxisAuditResult(
        axis_name=axis_name,
        claim=claim,
        verdict="aligned",
        evidence_count=n,
        signatures=signatures,
        signature_predictions=predictions,
        confidence=confidence,
        evidence_refs=evidence_refs,
        reason=(
            f"Across {n} qualifying record(s): failure-frame ratio "
            f"{s1_rate:.0%}, fire-condition rate {s2_rate:.0%}. "
            f"Claim 'failure-first' at position 0 holds against the "
            f"lived record." + single_miss_note
        ),
        suggested_reelicitation=None,
    )


# ---------------------------------------------------------------------------
# Axis D · asymmetry_posture (checkpoint 4)
# ---------------------------------------------------------------------------
#
# Spec: docs/DESIGN_V0_11_PHASE_12.md § Axis D.
#
# `asymmetry_posture` is a single-value enum: loss-averse / balanced /
# gain-seeking, applied to irreversible-action behavior (the
# HIGH_IMPACT_BASH set defined in core/hooks/episodic_writer.py).
# CP4 operationalizes `loss-averse` only — other values return
# insufficient_evidence with a Template-D sketch-table pointer, mirroring
# the CP3 discipline.
#
# Two signatures:
#
#   S1 · stop-condition rate. Per-record syntactic classifier sorts each
#        irreversible-op disconfirmation into stop-condition (names a
#        trigger that aborts/rolls back), success-criterion (names what
#        should hold at completion), both, or unknown. Claim `loss-averse`
#        predicts (stop OR both) ≥ 0.70; drift floor 0.55.
#
#   S2 · rollback-path mention rate. Tokenizes knowns + assumptions
#        against the rollback_adjacent lexicon (kernel/PHASE_12_LEXICON.md).
#        Records mentioning ≥ 1 token count toward the rate. Claim
#        predicts ≥ 0.50 mention rate; drift floor 0.30.
#
# D1 convergence STRICT for Axis D: both S1 AND S2 must miss to flag
# drift — same default as Axis A, NOT the catastrophic-exception path
# Axis C uses. Loss-averse is a posture, not a high-consequence single-
# action invariant.

# Stop-condition vocabulary — verbs that name an abort/rollback move.
_STOP_VERB_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\b(?:abort|rollback|roll\s+back|revert|halt|kill|back\s+out|undo|stop|restore\s+(?:from|to)|recover|recovery|pause|disable)\b", re.I),
    re.compile(r"\bdo\s+not\s+(?:proceed|merge|deploy|ship|push|promote)\b", re.I),
    re.compile(r"\bblock\s+the\s+(?:rollout|deploy|merge|push|promotion)\b", re.I),
)

# Success-criterion vocabulary — verbs that name a happy-path outcome.
# Deliberately TIGHT: words like `deploy`, `promote`, `ship`, `merge`,
# `publish`, `land`, `deliver` are excluded because they're routinely
# used as nouns/objects of stop-verbs ("rollback the deploy", "do not
# promote", "abort the merge") and would mis-classify a clean stop
# clause as `both`. Only intrinsically positive-valenced markers stay.
_SUCCESS_VERB_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\b(?:succeed|succeeds|succeeded|work|works|worked|pass|passes|passed|complete|completes|completed|validate|validates|validated|render|renders|rendered|finish|finishes|finished)\b", re.I),
    re.compile(r"\b(?:green|healthy|clean)\s+(?:build|run|status|outcome|result|deploy|release)\b", re.I),
    re.compile(r"\bif\s+(?:everything|all)\s+(?:stays\s+green|is\s+green|is\s+ok|is\s+fine|works|passes)\b", re.I),
)


StopConditionClass = Literal["stop", "success", "both", "unknown"]


def _classify_stop_condition(text: Any) -> StopConditionClass:
    """Sort a disconfirmation into stop / success / both / unknown.

    Stop = conditional trigger + an abort verb (or a do-not directive).
    Success = conditional trigger + a happy-path verb.
    Both = signatures from each side present.
    Unknown = empty / very-short / neither pattern matched.

    Reuses _CONDITIONAL_TRIGGER_PATTERNS from Axis A so the trigger
    vocabulary stays consistent across the audit. Both signatures use
    word-boundary matching and case-insensitive flags.
    """
    if not isinstance(text, str):
        return "unknown"
    stripped = text.strip()
    if len(stripped) < 10:
        return "unknown"
    low = stripped.lower()

    has_stop = any(pat.search(low) for pat in _STOP_VERB_PATTERNS)
    has_success = any(pat.search(low) for pat in _SUCCESS_VERB_PATTERNS)
    # Trigger word presence is informational; stop/success markers are
    # imperative-mood enough on their own that requiring an explicit
    # if/when would over-filter ("rollback the deploy" is unambiguous).
    has_trigger = any(pat.search(low) for pat in _CONDITIONAL_TRIGGER_PATTERNS)
    del has_trigger  # reserved for a later refinement; not load-bearing today

    if has_stop and has_success:
        return "both"
    if has_stop:
        return "stop"
    if has_success:
        return "success"
    return "unknown"


def _is_irreversible_op(record: dict) -> bool:
    """True if the record fired the high-impact pattern set (the same
    pattern set used by reasoning_surface_guard.py and episodic_writer.py).
    Reads details.high_impact_patterns_matched, falling back to the
    record's tags array which carries the same labels."""
    details = record.get("details")
    if isinstance(details, dict):
        hits = details.get("high_impact_patterns_matched")
        if isinstance(hits, list) and hits:
            return True
    tags = record.get("tags")
    if isinstance(tags, list) and "high-impact" in tags:
        return True
    return False


def _has_rollback_mention(record: dict, lexicon_terms: frozenset[str]) -> bool:
    """True iff the record's knowns + assumptions mention any term from
    the rollback_adjacent lexicon. Uses the same word-boundary counter
    as Axis A so multi-word phrases like 'back out' / 'restore from
    backup' match cleanly."""
    if not lexicon_terms:
        return False
    blob = " ".join(
        _surface_text(record, f) for f in ("knowns", "assumptions")
    )
    if not blob:
        return False
    return _count_lexicon_hits(blob, lexicon_terms) > 0


_AXIS_D_EVIDENCE_MINIMUM = 15

# Claim-anchored band for `loss-averse`. Floor = drift threshold.
# Per spec §Axis D: S1 (stop OR both) predicted ≥ 0.70 with drift floor
# 0.55; S2 mention rate predicted ≥ 0.50 with drift floor 0.30.
_LOSS_AVERSE_PREDICTIONS: dict[str, list[float]] = {
    "S1_stop_condition_rate": [0.55, 1.00],
    "S2_rollback_mention_rate": [0.30, 1.00],
}


def _axis_asymmetry_posture(
    axis_name: str,
    claim: Any,
    records: list[dict],
    lexicon: dict[str, frozenset[str]],
) -> AxisAuditResult:
    # Claim shape: a string enum value. Anything else is unparseable.
    claim_str = claim.strip() if isinstance(claim, str) and claim.strip() else None

    if claim_str is None:
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="insufficient_evidence",
            evidence_count=0,
            signatures={},
            signature_predictions={},
            confidence="low",
            evidence_refs=[],
            reason=(
                "No asymmetry_posture claim declared per docs/"
                "DESIGN_V0_11_PHASE_12.md § Axis D. CP4 audits the "
                "declared posture against irreversible-op records; "
                "without a named posture there is no hypothesis to test."
            ),
            suggested_reelicitation=None,
        )

    if claim_str != "loss-averse":
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="insufficient_evidence",
            evidence_count=0,
            signatures={},
            signature_predictions={},
            confidence="low",
            evidence_refs=[],
            reason=(
                f"Claim is {claim_str!r}. CP4 operationalizes only "
                f"'loss-averse'; 'balanced' and 'gain-seeking' follow "
                f"Template D per docs/DESIGN_V0_11_PHASE_12.md § sketch "
                f"table and ship in 0.11.1."
            ),
            suggested_reelicitation=None,
        )

    rollback_terms = lexicon.get("rollback_adjacent", frozenset())
    irreversible = [r for r in records if _is_irreversible_op(r)]
    n = len(irreversible)
    evidence_refs = _collect_evidence_refs(irreversible)
    predictions = _LOSS_AVERSE_PREDICTIONS

    if n < _AXIS_D_EVIDENCE_MINIMUM:
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="insufficient_evidence",
            evidence_count=n,
            signatures={},
            signature_predictions=predictions,
            confidence="low",
            evidence_refs=evidence_refs,
            reason=(
                f"Only {n} irreversible-op record(s) in window (need ≥ "
                f"{_AXIS_D_EVIDENCE_MINIMUM} per docs/"
                f"DESIGN_V0_11_PHASE_12.md § Axis D · Evidence minimum). "
                f"Keep accumulating; Axis D requires D1 convergence on "
                f"two signatures across the irreversible-op subset."
            ),
            suggested_reelicitation=None,
        )

    stop_count = 0
    rollback_count = 0
    for rec in irreversible:
        disconf = _surface_text(rec, "disconfirmation")
        cls = _classify_stop_condition(disconf)
        if cls in ("stop", "both"):
            stop_count += 1
        if _has_rollback_mention(rec, rollback_terms):
            rollback_count += 1

    s1_rate = stop_count / n
    s2_rate = rollback_count / n
    signatures = {
        "S1_stop_condition_rate": round(s1_rate, 3),
        "S2_rollback_mention_rate": round(s2_rate, 3),
    }
    s1_floor = predictions["S1_stop_condition_rate"][0]
    s2_floor = predictions["S2_rollback_mention_rate"][0]
    s1_drift = s1_rate < s1_floor
    s2_drift = s2_rate < s2_floor
    confidence: Confidence = "high" if n >= 30 else "medium"

    if s1_drift and s2_drift:
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="drift",
            evidence_count=n,
            signatures=signatures,
            signature_predictions=predictions,
            confidence=confidence,
            evidence_refs=evidence_refs,
            reason=(
                f"Across {n} irreversible-op record(s): stop-condition "
                f"rate {s1_rate:.0%} < {s1_floor:.0%} floor AND "
                f"rollback-mention rate {s2_rate:.0%} < {s2_floor:.0%} "
                f"floor. Claim 'loss-averse' not borne out by the lived "
                f"record. D1 convergence confirmed — both signatures "
                f"missed."
            ),
            suggested_reelicitation=(
                "Re-elicit asymmetry_posture: are irreversible ops "
                "actually paired with stop-conditions and rollback "
                "paths, or has practice drifted toward 'balanced' / "
                "'gain-seeking'? Inspect the irreversible-op records "
                "and either tighten practice or revise the claim."
            ),
        )

    single_miss_note = ""
    if s1_drift:
        single_miss_note = (
            f" S1 single-signature miss noted "
            f"({s1_rate:.0%} < {s1_floor:.0%}); D1 convergence "
            f"requires BOTH to flag, so no drift."
        )
    elif s2_drift:
        single_miss_note = (
            f" S2 single-signature miss noted "
            f"({s2_rate:.0%} < {s2_floor:.0%}); D1 convergence "
            f"requires BOTH to flag, so no drift."
        )

    return AxisAuditResult(
        axis_name=axis_name,
        claim=claim,
        verdict="aligned",
        evidence_count=n,
        signatures=signatures,
        signature_predictions=predictions,
        confidence=confidence,
        evidence_refs=evidence_refs,
        reason=(
            f"Across {n} irreversible-op record(s): stop-condition rate "
            f"{s1_rate:.0%}, rollback-mention rate {s2_rate:.0%}. "
            f"Claim 'loss-averse' holds against the lived record." +
            single_miss_note
        ),
        suggested_reelicitation=None,
    )


# ---------------------------------------------------------------------------
# Axis B · noise_signature (checkpoint 5)
# ---------------------------------------------------------------------------
#
# Spec: docs/DESIGN_V0_11_PHASE_12.md § Axis B.
#
# noise_signature.primary names the dominant noise source the operator
# is susceptible to. CP5 operationalizes 'status-pressure' only — the
# maintainer's declared primary. Other primaries (regret, anxiety,
# social-scripts, false-urgency) return insufficient_evidence with a
# Template-B sketch-table pointer and ship in 0.11.1.
#
# This is the axis the spec author flagged as MOST FRAGILE: both
# signatures are weak individually. Insufficient_evidence is the
# correct first-30-day behavior, not a CP5 bug.
#
# DRIFT DIRECTION INVERTED for S1. All other axes flag drift when an
# observed rate sits BELOW a floor. Axis B's S1 flags drift when the
# observed buzzword rate sits ABOVE a ceiling: the operator's own
# stated counter-screen claim ("no buzzword names leak into body
# docs") predicts < 15% rate; high density against a counter-screen
# claim is what drift looks like for this axis. The convention break
# is documented inline because the verdict logic differs from CP2-CP4.
#
# Two signatures:
#
#   S1 · buzzword density. Per-record check on core_question + knowns
#        against the `buzzword` lexicon (kernel/PHASE_12_LEXICON.md).
#        A record "has buzzword" iff >= 1 hit. Rate = records with
#        buzzword / total qualifying. Drift if rate > 0.30 standalone
#        (single-signature catastrophic exception — same shape as
#        fence_discipline's exception, justified inline below) OR rate
#        > 0.15 paired with S2.
#
#   S2 · specificity-collapse under cadence. Partition records by
#        inferred cadence (median inter-decision gap on captured_at).
#        Mean length of disconfirmation + unknowns[0] computed per
#        partition. collapse_ratio = (loose_mean - tight_mean) /
#        loose_mean. Positive = tight is shorter (collapse present).
#        Drift if collapse_ratio < 0.30 (no collapse despite claim).
#
# Catastrophic single-signature exception JUSTIFIED for S1 > 0.30:
# decorative-language density at that level is itself the signal of
# audience-shaping behavior, regardless of cadence behavior. This
# matches the spec's literal text ("Also flag if S1 > 30% regardless
# of S2"). Same shape as Axis C's exception — a named departure from
# D1, not a relaxation of D1.

_AXIS_B_EVIDENCE_MINIMUM = 40
_AXIS_B_PARTITION_MINIMUM = 5

# Drift thresholds for status-pressure claim. The acceptable band is
# defined against the operator's own counter-screen claim, not against
# the bare susceptibility claim.
_S1_BUZZWORD_DRIFT_CEILING = 0.15      # above this with S2 = drift
_S1_BUZZWORD_CATASTROPHIC = 0.30       # above this alone = drift
_S2_COLLAPSE_DRIFT_FLOOR = 0.30        # below this = no collapse = drift

_STATUS_PRESSURE_PREDICTIONS: dict[str, list[float]] = {
    # S1 prediction band: counter-screen claim predicts low buzzword
    # density. The high bound IS the drift ceiling (convention break
    # documented above). Consumers should rely on verdict + signatures,
    # not derive drift from this band.
    "S1_buzzword_record_rate": [0.00, _S1_BUZZWORD_DRIFT_CEILING],
    # S2 prediction band: collapse_ratio at or above 0.30 means
    # specificity collapses under tight cadence as the claim predicts.
    "S2_collapse_ratio": [_S2_COLLAPSE_DRIFT_FLOOR, 1.00],
}


def _axis_b_qualifying(record: dict) -> tuple[bool, str, list[str], str | None, str]:
    """Return (qualifies, core_question, knowns_list, captured_at, surface_blob).

    A record qualifies for Axis B when its reasoning_surface has either
    a non-empty core_question OR a non-empty knowns list. We need at
    least one of those for S1 (the buzzword scan); records with neither
    contribute no signal."""
    details = record.get("details")
    if not isinstance(details, dict):
        return False, "", [], None, ""
    surface = details.get("reasoning_surface")
    if not isinstance(surface, dict):
        return False, "", [], None, ""
    cq = surface.get("core_question")
    cq_str = cq.strip() if isinstance(cq, str) and cq.strip() else ""
    knowns = surface.get("knowns")
    knowns_list = [str(k) for k in knowns if isinstance(k, str) and k.strip()] if isinstance(knowns, list) else []
    if not cq_str and not knowns_list:
        return False, "", [], None, ""
    captured_at = None
    prov = record.get("provenance")
    if isinstance(prov, dict):
        ts = prov.get("captured_at")
        if isinstance(ts, str) and ts.strip():
            captured_at = ts.strip()
    blob = (cq_str + " " + " ".join(knowns_list)).strip()
    return True, cq_str, knowns_list, captured_at, blob


def _axis_b_specificity_length(record: dict) -> int:
    """Length of disconfirmation + unknowns[0] for the S2 specificity
    measure. Returns 0 when both fields are absent."""
    details = record.get("details")
    if not isinstance(details, dict):
        return 0
    surface = details.get("reasoning_surface")
    if not isinstance(surface, dict):
        return 0
    disconf = surface.get("disconfirmation")
    disconf_len = len(disconf) if isinstance(disconf, str) else 0
    unknowns = surface.get("unknowns")
    first_unknown_len = 0
    if isinstance(unknowns, list) and unknowns:
        first = unknowns[0]
        if isinstance(first, str):
            first_unknown_len = len(first)
    return disconf_len + first_unknown_len


def _partition_by_inferred_cadence(
    records_with_ts: list[tuple[dict, str]],
) -> tuple[list[dict], list[dict]]:
    """Infer cadence from timestamp clustering. Sort by captured_at,
    compute inter-decision gaps, and split records on the median gap.
    Records preceded by a shorter-than-median gap go to `tight`;
    longer-than-median go to `loose`. The first record (no preceding
    gap) is dropped from both partitions — it has no cadence signal.

    Inferred-only per spec open question 2: a `cadence_marker` schema
    field is 0.11.1 work; v0.11 ships with timestamp inference and
    accepts the higher noise floor.
    """
    if len(records_with_ts) < 2:
        return [], []
    parsed: list[tuple[datetime, dict]] = []
    for rec, ts in records_with_ts:
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            parsed.append((dt, rec))
        except ValueError:
            continue
    if len(parsed) < 2:
        return [], []
    parsed.sort(key=lambda p: p[0])
    gaps = [
        (parsed[i][0] - parsed[i - 1][0]).total_seconds()
        for i in range(1, len(parsed))
    ]
    sorted_gaps = sorted(gaps)
    mid = len(sorted_gaps) // 2
    median_gap = (
        sorted_gaps[mid]
        if len(sorted_gaps) % 2 == 1
        else (sorted_gaps[mid - 1] + sorted_gaps[mid]) / 2.0
    )
    # Tied-median: assign to `tight` rather than dropping. Strict <
    # / > drops every record when the cadence is bimodal-with-ties
    # (a common shape in real telemetry — e.g. "tight burst, then
    # break" alternating). The collapse_ratio is still meaningful
    # because tight remains the lower-or-equal-cadence partition.
    tight: list[dict] = []
    loose: list[dict] = []
    for i in range(1, len(parsed)):
        gap = (parsed[i][0] - parsed[i - 1][0]).total_seconds()
        rec = parsed[i][1]
        if gap <= median_gap:
            tight.append(rec)
        else:
            loose.append(rec)
    return tight, loose


def _axis_noise_signature(
    axis_name: str,
    claim: Any,
    records: list[dict],
    lexicon: dict[str, frozenset[str]],
) -> AxisAuditResult:
    primary = None
    if isinstance(claim, dict):
        p = claim.get("primary")
        if isinstance(p, str) and p.strip():
            primary = p.strip()

    if primary is None:
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="insufficient_evidence",
            evidence_count=0,
            signatures={},
            signature_predictions={},
            confidence="low",
            evidence_refs=[],
            reason=(
                "No noise_signature primary declared per docs/"
                "DESIGN_V0_11_PHASE_12.md § Axis B. CP5 audits the "
                "declared primary noise source against episodic praxis; "
                "without a named primary there is no hypothesis to test."
            ),
            suggested_reelicitation=None,
        )

    if primary != "status-pressure":
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="insufficient_evidence",
            evidence_count=0,
            signatures={},
            signature_predictions={},
            confidence="low",
            evidence_refs=[],
            reason=(
                f"Primary is {primary!r}. CP5 operationalizes only "
                f"'status-pressure'; other primaries follow Template B "
                f"per docs/DESIGN_V0_11_PHASE_12.md § sketch table and "
                f"ship in 0.11.1."
            ),
            suggested_reelicitation=None,
        )

    buzzword_terms = lexicon.get("buzzword", frozenset())
    qualifying: list[dict] = []
    qualifying_with_ts: list[tuple[dict, str]] = []
    buzzword_record_count = 0

    for rec in records:
        ok, cq_str, knowns_list, ts, blob = _axis_b_qualifying(rec)
        if not ok:
            continue
        qualifying.append(rec)
        if ts:
            qualifying_with_ts.append((rec, ts))
        if buzzword_terms and _count_lexicon_hits(blob, buzzword_terms) > 0:
            buzzword_record_count += 1

    n = len(qualifying)
    evidence_refs = _collect_evidence_refs(qualifying)
    predictions = _STATUS_PRESSURE_PREDICTIONS

    if n < _AXIS_B_EVIDENCE_MINIMUM:
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="insufficient_evidence",
            evidence_count=n,
            signatures={},
            signature_predictions=predictions,
            confidence="low",
            evidence_refs=evidence_refs,
            reason=(
                f"Only {n} qualifying record(s) with non-empty "
                f"core_question or knowns in window (need ≥ "
                f"{_AXIS_B_EVIDENCE_MINIMUM} per docs/"
                f"DESIGN_V0_11_PHASE_12.md § Axis B · Evidence minimum). "
                f"Axis B is the highest-volume axis because cadence "
                f"partitioning needs population in each side; spec "
                f"flags this axis as the slowest to surface signal."
            ),
            suggested_reelicitation=None,
        )

    s1_rate = buzzword_record_count / n

    # S2 — partition by inferred cadence and compute collapse ratio.
    tight, loose = _partition_by_inferred_cadence(qualifying_with_ts)
    s2_computable = (
        len(tight) >= _AXIS_B_PARTITION_MINIMUM
        and len(loose) >= _AXIS_B_PARTITION_MINIMUM
    )

    if not s2_computable:
        # S2 cannot be computed honestly. Axis B is one of the few
        # axes where partial signature coverage genuinely degrades to
        # insufficient_evidence — flagging on S1 alone (without the
        # S1 > 30% catastrophic threshold) would violate D1.
        if s1_rate > _S1_BUZZWORD_CATASTROPHIC:
            return AxisAuditResult(
                axis_name=axis_name,
                claim=claim,
                verdict="drift",
                evidence_count=n,
                signatures={"S1_buzzword_record_rate": round(s1_rate, 3)},
                signature_predictions=predictions,
                confidence="medium",
                evidence_refs=evidence_refs,
                reason=(
                    f"Across {n} qualifying record(s): buzzword rate "
                    f"{s1_rate:.0%} > {_S1_BUZZWORD_CATASTROPHIC:.0%} "
                    f"catastrophic ceiling. Decorative-language density "
                    f"itself is evidence against the operator's "
                    f"counter-screen claim, regardless of S2 (spec "
                    f"§Axis B permits single-signature flagging at "
                    f"this threshold — same shape as Axis C's "
                    f"catastrophic exception)."
                ),
                suggested_reelicitation=(
                    "Re-elicit noise_signature: buzzword density at this "
                    "level suggests the counter-screen claim does not "
                    "hold in praxis. Either reaffirm susceptibility and "
                    "tighten the screen, or revise the primary."
                ),
            )
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="insufficient_evidence",
            evidence_count=n,
            signatures={"S1_buzzword_record_rate": round(s1_rate, 3)},
            signature_predictions=predictions,
            confidence="low",
            evidence_refs=evidence_refs,
            reason=(
                f"Cadence partitioning needs ≥ "
                f"{_AXIS_B_PARTITION_MINIMUM} records per partition; "
                f"got {len(tight)} tight, {len(loose)} loose. S2 cannot "
                f"be computed honestly. S1 buzzword rate {s1_rate:.0%} "
                f"is below catastrophic threshold so D1 prevents "
                f"flagging on S1 alone."
            ),
            suggested_reelicitation=None,
        )

    # Both signatures computable.
    tight_lens = [_axis_b_specificity_length(r) for r in tight]
    loose_lens = [_axis_b_specificity_length(r) for r in loose]
    tight_mean = sum(tight_lens) / len(tight_lens)
    loose_mean = sum(loose_lens) / len(loose_lens)
    if loose_mean <= 0:
        # Degenerate denominator — operator writes empty surfaces
        # under loose cadence too. No meaningful collapse comparison.
        s2_collapse_ratio = 0.0
    else:
        s2_collapse_ratio = (loose_mean - tight_mean) / loose_mean
    signatures = {
        "S1_buzzword_record_rate": round(s1_rate, 3),
        "S2_collapse_ratio": round(s2_collapse_ratio, 3),
    }
    confidence: Confidence = "high" if n >= 80 else "medium"

    s1_catastrophic = s1_rate > _S1_BUZZWORD_CATASTROPHIC
    s1_above_floor = s1_rate > _S1_BUZZWORD_DRIFT_CEILING
    s2_no_collapse = s2_collapse_ratio < _S2_COLLAPSE_DRIFT_FLOOR

    if s1_catastrophic:
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="drift",
            evidence_count=n,
            signatures=signatures,
            signature_predictions=predictions,
            confidence=confidence,
            evidence_refs=evidence_refs,
            reason=(
                f"Across {n} qualifying record(s): buzzword rate "
                f"{s1_rate:.0%} > {_S1_BUZZWORD_CATASTROPHIC:.0%} "
                f"catastrophic ceiling. Decorative-language density "
                f"itself is evidence against the counter-screen claim "
                f"(spec §Axis B single-signature exception)."
            ),
            suggested_reelicitation=(
                "Re-elicit noise_signature: buzzword density at this "
                "level suggests the counter-screen claim does not hold "
                "in praxis."
            ),
        )

    if s1_above_floor and s2_no_collapse:
        return AxisAuditResult(
            axis_name=axis_name,
            claim=claim,
            verdict="drift",
            evidence_count=n,
            signatures=signatures,
            signature_predictions=predictions,
            confidence=confidence,
            evidence_refs=evidence_refs,
            reason=(
                f"Across {n} qualifying record(s): buzzword rate "
                f"{s1_rate:.0%} > {_S1_BUZZWORD_DRIFT_CEILING:.0%} "
                f"floor AND specificity collapse_ratio "
                f"{s2_collapse_ratio:.0%} < "
                f"{_S2_COLLAPSE_DRIFT_FLOOR:.0%} floor. Counter-screen "
                f"failing AND no specificity collapse under tight "
                f"cadence — neither signature of claimed status-pressure "
                f"susceptibility is showing up. D1 convergence confirmed."
            ),
            suggested_reelicitation=(
                "Re-elicit noise_signature: claimed susceptibility to "
                "status-pressure but episodic record shows neither "
                "buzzword leakage signal nor specificity collapse. "
                "Either the primary is wrong or the counter-screen is "
                "doing different work than the claim describes."
            ),
        )

    single_miss_note = ""
    if s1_above_floor:
        single_miss_note = (
            f" S1 single-signature miss noted "
            f"({s1_rate:.0%} > {_S1_BUZZWORD_DRIFT_CEILING:.0%}); "
            f"D1 convergence requires BOTH to flag, so no drift."
        )
    elif s2_no_collapse:
        single_miss_note = (
            f" S2 single-signature miss noted "
            f"(collapse {s2_collapse_ratio:.0%} < "
            f"{_S2_COLLAPSE_DRIFT_FLOOR:.0%}); D1 convergence requires "
            f"BOTH to flag, so no drift."
        )

    return AxisAuditResult(
        axis_name=axis_name,
        claim=claim,
        verdict="aligned",
        evidence_count=n,
        signatures=signatures,
        signature_predictions=predictions,
        confidence=confidence,
        evidence_refs=evidence_refs,
        reason=(
            f"Across {n} qualifying record(s): buzzword rate "
            f"{s1_rate:.0%}, specificity collapse_ratio "
            f"{s2_collapse_ratio:.0%}. Claimed status-pressure primary "
            f"holds against the lived record." + single_miss_note
        ),
        suggested_reelicitation=None,
    )


# Per-axis dispatch table. Populated by checkpoints 2-5 as each axis's
# real handler lands. Every insertion into this dict is a commitment that
# the corresponding axis is fully operationalized per its spec entry.
_AXIS_HANDLERS: dict[str, Any] = {
    "fence_discipline": _axis_fence_discipline,    # checkpoint 2
    "dominant_lens": _axis_dominant_lens,          # checkpoint 3
    "asymmetry_posture": _axis_asymmetry_posture,  # checkpoint 4
    "noise_signature": _axis_noise_signature,      # checkpoint 5
}


# Axis -> spec-sketch reference. Lets each stub's reason field point to
# exactly the sketch-table row that governs its eventual implementation.
_SKETCH_TABLE_REFS: dict[str, str] = {
    # Process axes — spec §Remaining axes sketch table.
    "planning_strictness": "docs/DESIGN_V0_11_PHASE_12.md § sketch table row 'planning_strictness' (Template C)",
    "risk_tolerance": "docs/DESIGN_V0_11_PHASE_12.md § sketch table row 'risk_tolerance' (Template D)",
    "testing_rigor": "docs/DESIGN_V0_11_PHASE_12.md § sketch table row 'testing_rigor' (Template C)",
    "parallelism_preference": "docs/DESIGN_V0_11_PHASE_12.md § sketch table row 'parallelism_preference' (Template B)",
    "documentation_rigor": "docs/DESIGN_V0_11_PHASE_12.md § sketch table row 'documentation_rigor' (Template C)",
    "automation_level": "docs/DESIGN_V0_11_PHASE_12.md § sketch table row 'automation_level' (Template B)",
    # Cognitive-style axes.
    "dominant_lens": "docs/DESIGN_V0_11_PHASE_12.md § Axis A · dominant_lens: failure-first (worked in full)",
    "noise_signature": "docs/DESIGN_V0_11_PHASE_12.md § Axis B · noise_signature (worked in full)",
    "abstraction_entry": "docs/DESIGN_V0_11_PHASE_12.md § sketch table row 'abstraction_entry' (Template A)",
    "decision_cadence": "docs/DESIGN_V0_11_PHASE_12.md § sketch table rows 'decision_cadence.tempo' + 'decision_cadence.commit_after'",
    "explanation_depth": "docs/DESIGN_V0_11_PHASE_12.md § sketch table row 'explanation_depth' (Template A)",
    "feedback_mode": "docs/DESIGN_V0_11_PHASE_12.md § sketch table row 'feedback_mode' (Template A)",
    "uncertainty_tolerance": "docs/DESIGN_V0_11_PHASE_12.md § sketch table row 'uncertainty_tolerance' (Template C)",
    "asymmetry_posture": "docs/DESIGN_V0_11_PHASE_12.md § Axis D · asymmetry_posture: loss-averse (worked in full)",
    "fence_discipline": "docs/DESIGN_V0_11_PHASE_12.md § Axis C · fence_discipline: 4 (worked in full)",
}


# ---------------------------------------------------------------------------
# Input loaders — episodic records, profile claims, lexicon
# ---------------------------------------------------------------------------


def _load_episodic_records(
    episodic_dir: Path,
    since_days: int,
    *,
    now: datetime,
) -> list[dict]:
    """Load episodic records within the rolling window. Tolerant of
    malformed JSONL lines (phase 10 writer is best-effort and may truncate
    on crash; we match that contract here).
    """
    if not episodic_dir.exists() or not episodic_dir.is_dir():
        return []
    cutoff = now - timedelta(days=since_days)
    records: list[dict] = []
    for path in sorted(episodic_dir.glob("*.jsonl")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(rec, dict):
                        continue
                    ts = rec.get("ts")
                    if isinstance(ts, str):
                        try:
                            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            if dt < cutoff:
                                continue
                        except ValueError:
                            continue
                    records.append(rec)
        except OSError:
            continue
    return records


def _load_profile_claims(profile_path: Path) -> dict[str, Any]:
    """Parse the operator profile's axis claims.

    The profile is Markdown with YAML-ish blocks inside code fences. This
    parser is narrow by design: it extracts the `value` (or `primary`/
    `secondary` pair for noise_signature, or `tempo`/`commit_after` for
    decision_cadence) for each known axis. Unknown axes or malformed
    blocks yield None for that axis — never raises.

    Zero external YAML dependency — pyproject.toml's `dependencies = []`
    is a repo invariant.
    """
    claims: dict[str, Any] = {name: None for name in ALL_AXES}
    if not profile_path.exists():
        return claims
    try:
        text = profile_path.read_text(encoding="utf-8")
    except OSError:
        return claims
    for axis in ALL_AXES:
        claims[axis] = _extract_axis_claim(text, axis)
    return claims


def _extract_axis_claim(text: str, axis_name: str) -> Any:
    """Return the declared value for an axis. None if the block cannot
    be located or parsed. Shape varies by axis."""
    # Axis blocks start with `<name>:` at column 0 followed by an indented
    # body. Match the block, then inspect the body.
    block_re = re.compile(
        rf"^{re.escape(axis_name)}:\s*\n((?:[ \t]+.+(?:\n|$))+)",
        re.MULTILINE,
    )
    m = block_re.search(text)
    if not m:
        return None
    block = m.group(1)

    # noise_signature: primary + secondary, no `value` field.
    if axis_name == "noise_signature":
        primary = _extract_yaml_field(block, "primary")
        secondary = _extract_yaml_field(block, "secondary")
        if primary is None:
            return None
        return {"primary": primary, "secondary": secondary}

    # decision_cadence: tempo + commit_after.
    if axis_name == "decision_cadence":
        tempo = _extract_yaml_field(block, "tempo")
        commit_after = _extract_yaml_field(block, "commit_after")
        if tempo is None and commit_after is None:
            return None
        return {"tempo": tempo, "commit_after": commit_after}

    # All others: `value: <scalar>` or `value: [a, b, c]`.
    raw = _extract_yaml_field(block, "value")
    if raw is None:
        return None
    if raw.startswith("[") and raw.endswith("]"):
        return [s.strip() for s in raw[1:-1].split(",") if s.strip()]
    try:
        return int(raw)
    except ValueError:
        return raw


def _extract_yaml_field(block: str, field_name: str) -> str | None:
    m = re.search(
        rf"^[ \t]+{re.escape(field_name)}:\s*(.*?)\s*$",
        block,
        re.MULTILINE,
    )
    if not m:
        return None
    value = m.group(1).strip()
    return value or None


def _resolve_lexicon_path() -> Path:
    """Operator override at core/memory/global/phase_12_lexicon.md takes
    precedence; else the kernel default."""
    override = REPO_ROOT / "core" / "memory" / "global" / "phase_12_lexicon.md"
    if override.exists():
        return override
    return REPO_ROOT / "kernel" / "PHASE_12_LEXICON.md"


def _load_lexicon(path: Path) -> dict[str, frozenset[str]]:
    """Parse a lexicon file. Format: Markdown `## <name>` headings
    followed by bullet-list terms. Returns name → frozenset of lowercase
    terms.
    """
    lexicon: dict[str, frozenset[str]] = {}
    if not path.exists():
        return lexicon
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return lexicon

    current_name: str | None = None
    current_terms: list[str] = []

    def flush():
        nonlocal current_name, current_terms
        if current_name is not None and current_terms:
            lexicon[current_name] = frozenset(t.lower() for t in current_terms)
        current_name = None
        current_terms = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            flush()
            name = stripped[3:].strip()
            # Only accept lexicon sections — skip prose h2s like "## Lexicon fingerprint".
            if _is_valid_lexicon_name(name):
                current_name = name
            else:
                current_name = None
        elif current_name and stripped.startswith("- "):
            term = stripped[2:].strip()
            if term:
                current_terms.append(term)
    flush()
    return lexicon


_VALID_LEXICON_NAMES = frozenset({
    "failure_frame",
    "success_frame",
    "buzzword",
    "causal_connective",
    "rollback_adjacent",
})


def _is_valid_lexicon_name(name: str) -> bool:
    return name in _VALID_LEXICON_NAMES


def _lexicon_fingerprint(lexicon: dict[str, frozenset[str]]) -> str:
    """First 16 hex chars of sha256 over the sorted canonicalized lexicon.

    Deterministic: same contents produce the same fingerprint. Captures
    lexicon drift across audit runs even when the filename is unchanged.
    """
    h = hashlib.sha256()
    for name in sorted(lexicon.keys()):
        h.update(name.encode("utf-8"))
        h.update(b":")
        for term in sorted(lexicon[name]):
            h.update(term.encode("utf-8"))
            h.update(b"\n")
        h.update(b"\n")
    return h.hexdigest()[:16]


# ---------------------------------------------------------------------------
# Output rendering helpers — used by the CLI
# ---------------------------------------------------------------------------


def render_text_report(result: dict[str, Any]) -> str:
    """Human-readable Markdown report. PROVISIONAL format — may evolve
    during the RC cycle based on real-use feedback. Consumers that need
    a stable format must use `--json`.
    """
    lines: list[str] = []
    lines.append(f"# Profile Audit — `{result.get('run_id', 'unknown')}`")
    lines.append("")
    lines.append(
        f"_run_ts: {result.get('run_ts', '?')} · "
        f"window: {result.get('episodic_window', '?')} · "
        f"lexicon: {result.get('lexicon_fingerprint', '?')[:12]}_"
    )
    lines.append("")

    buckets: dict[str, list[AxisAuditResult]] = {
        "drift": [],
        "aligned": [],
        "insufficient_evidence": [],
    }
    for axis in result.get("axes", []):
        buckets[axis["verdict"]].append(axis)

    lines.append(
        f"Axes: **{len(buckets['drift'])}** in drift · "
        f"**{len(buckets['aligned'])}** aligned · "
        f"**{len(buckets['insufficient_evidence'])}** insufficient_evidence"
    )
    lines.append("")

    if buckets["drift"]:
        lines.append("## Drift — re-elicitation candidates")
        lines.append("")
        for a in buckets["drift"]:
            lines.append(f"- **{a['axis_name']}** — {a['reason']}")
            if a.get("suggested_reelicitation"):
                lines.append(f"  - suggested: _{a['suggested_reelicitation']}_")
        lines.append("")

    if buckets["aligned"]:
        lines.append("## Aligned (no action)")
        lines.append("")
        for a in buckets["aligned"]:
            lines.append(f"- {a['axis_name']}")
        lines.append("")

    if buckets["insufficient_evidence"]:
        lines.append("## Insufficient evidence")
        lines.append("")
        for a in buckets["insufficient_evidence"]:
            lines.append(f"- {a['axis_name']} — {a['reason']}")
        lines.append("")

    return "\n".join(lines)


def write_audit_record(result: dict[str, Any], reflective_dir: Path | None = None) -> Path:
    """Append the record to profile_audit.jsonl. Append-only, never
    overwrites. Returns the path written.

    D3 · re-elicitation not correction: this writes to the reflective
    tier only. Never mutates core/memory/global/operator_profile.md.
    """
    reflective_dir = reflective_dir or (Path.home() / ".episteme" / "memory" / "reflective")
    reflective_dir.mkdir(parents=True, exist_ok=True)
    path = reflective_dir / "profile_audit.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
    return path


def read_latest_audit(reflective_dir: Path | None = None) -> dict[str, Any] | None:
    """Return the most-recent audit record, or None. Used by
    session_context.py to surface unacknowledged drift at SessionStart.
    """
    reflective_dir = reflective_dir or (Path.home() / ".episteme" / "memory" / "reflective")
    path = reflective_dir / "profile_audit.jsonl"
    if not path.exists():
        return None
    last: str | None = None
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s:
                    last = s
    except OSError:
        return None
    if not last:
        return None
    try:
        rec = json.loads(last)
    except json.JSONDecodeError:
        return None
    return rec if isinstance(rec, dict) else None


def surface_drift_line(record: dict[str, Any] | None) -> str | None:
    """Produce the one-line SessionStart surfacing string, or None.

    Silent when the record is absent, acknowledged, or contains no
    drift. Matches the `profile-audit: ...` shape documented in the
    spec §SessionStart surfacing.
    """
    if not record:
        return None
    if record.get("acknowledged", False):
        return None
    drifts = [
        a for a in record.get("axes", [])
        if isinstance(a, dict) and a.get("verdict") == "drift"
    ]
    if not drifts:
        return None
    run_id = record.get("run_id", "unknown")
    if len(drifts) == 1:
        a = drifts[0]
        return (
            f"profile-audit: drift on {a['axis_name']} — "
            f"{a.get('reason', 'see audit record')} "
            f"Re-elicit or ack via `episteme profile audit ack {run_id}`."
        )
    if len(drifts) <= 3:
        names = ", ".join(a["axis_name"] for a in drifts)
        return (
            f"profile-audit: drift on {names} — run "
            f"`episteme profile audit` for details. "
            f"Ack via `episteme profile audit ack {run_id}`."
        )
    return (
        f"profile-audit: drift on {len(drifts)} axes — run "
        f"`episteme profile audit` for details. "
        f"Ack via `episteme profile audit ack {run_id}`."
    )
