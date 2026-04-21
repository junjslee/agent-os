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


# Per-axis dispatch table. Populated by checkpoints 2-5 as each axis's
# real handler lands. Every insertion into this dict is a commitment that
# the corresponding axis is fully operationalized per its spec entry.
_AXIS_HANDLERS: dict[str, Any] = {
    "fence_discipline": _axis_fence_discipline,  # checkpoint 2
    # Checkpoint 3 will insert: "dominant_lens": _axis_dominant_lens
    # Checkpoint 4 will insert: "asymmetry_posture": _axis_asymmetry_posture
    # Checkpoint 5 will insert: "noise_signature": _axis_noise_signature
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
