#!/usr/bin/env python3
"""Specificity classifier — moved from src/episteme/_profile_audit.py at v1.0 RC CP1.

Classifies a Reasoning Surface's `disconfirmation` field (and later, under the
v1.0 RC blueprint-polymorphic shape, any blueprint field whose contract
specifies "conditional trigger + specific observable") as one of:

- `fire` — a conditional trigger AND a specific observable are present.
- `absence` — the trigger is phrased as an absence condition (`if nothing
  breaks`, `no issues arise`). Routed away from `fire` because absence is the
  wrong shape for a failure-first operator.
- `tautological` — trigger without observable, or observable without trigger.
- `unknown` — empty / very-short content (< 10 chars). Declines to classify.

Priority: absence > fire > tautological > unknown.

Why this module exists (v1.0 RC CP1 rationale). Phase 12's profile-audit
loop defined the classifier inside `_profile_audit.py` because that was the
only caller at v0.11.0 ship time. The v1.0 RC spec (Pillar 1, Layer 2) makes
the classifier a shared asset: `reasoning_surface_guard.py` will call it in
the hot path against the selected blueprint's required fields (CP3). Moving
it out of the profile-audit module into a sibling hook module is the minimum
refactor that lets CP3 land without importing from `src/episteme/` (which
would violate the hook-self-contained convention).

Behavior is unchanged from the v0.11.0 implementation. Every rule set, every
pattern, and every priority decision is a verbatim move. `_profile_audit.py`
re-exports the names at module scope so existing `pa._classify_disconfirmation`
test access continues to work.

Kernel anchors:
- `kernel/REASONING_SURFACE.md` — the surface-polymorphic contract this
  classifier validates fields against.
- `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § "Layer 2 · structural
  specificity classifier (blueprint-aware)" — the v1.0 RC contract.
- `docs/DESIGN_V0_11_PHASE_12.md` Axis A S2 — the retrospective audit this
  classifier originally served.
"""
from __future__ import annotations

import re
from typing import Any, Literal


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


# ---------------------------------------------------------------------------
# CP5: origin_evidence classifier for Fence Reconstruction.
#
# `origin_evidence` is a WHY statement, not a fire-shape prediction. The
# trigger+observable classifier above would produce category-error
# rejections on honest surfaces. This is a separate rule set:
#
#   evidence    — presence of at least one concrete pointer shape:
#                 commit SHA, @path:line, URL, issue/ticket ID, dated
#                 event, or "git blame" / "incident" reference
#   legacy      — explicit lazy-evidence markers: "unclear",
#                 "probably legacy", "historical reasons", "no record",
#                 "don't remember", "forgotten"
#   unknown     — empty / very-short (< 10 chars); decline to classify
#
# Priority: legacy > evidence > unknown. A surface that both cites a
# SHA AND says "probably legacy" routes to `legacy` because the hedge
# indicates the evidence is thin.
# ---------------------------------------------------------------------------

OriginEvidenceClass = Literal["evidence", "legacy", "unknown"]

_LAZY_EVIDENCE_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\bunclear\b", re.I),
    re.compile(r"\bprobably\s+(?:legacy|historical|old)\b", re.I),
    re.compile(r"\bhistorical\s+(?:reasons?|artifact|cruft)\b", re.I),
    re.compile(r"\bno\s+(?:record|memory|history|trace|evidence)\b", re.I),
    re.compile(r"\b(?:don't|do\s+not|dont)\s+(?:remember|recall|know)\b", re.I),
    re.compile(r"\bforgotten\b", re.I),
    re.compile(r"\bnobody\s+(?:remembers?|knows)\b", re.I),
    re.compile(r"\bcargo[- ]cult(?:ed)?\b", re.I),
    re.compile(r"\bjust\s+there\b", re.I),
    re.compile(r"\blegacy\s+(?:code|cruft|artifact)\b", re.I),
)

_EVIDENCE_MARKER_PATTERNS: tuple[re.Pattern, ...] = (
    # Commit SHA (mixed digit+letter, 7-40 chars). Same discipline as
    # _grounding.py's hex_sha extractor.
    re.compile(r"\b(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b"),
    # @path:line anchor (e.g. "see core/hooks/foo.py:42").
    re.compile(r"[A-Za-z0-9_\-/]+\.[a-z]{1,5}:\d+"),
    # Ticket / issue / incident ID shapes.
    re.compile(r"\b(?:#\d+|[A-Z][A-Z0-9]+-\d+|INC\d+|PAGE\d+)\b"),
    # URL.
    re.compile(r"https?://\S+"),
    # Dated event (ISO-8601 or YYYY-MM-DD).
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    # "git blame" / "git log" / "commit" / "blame" / "incident" / "RFC"
    # / "ADR" / "postmortem" / "post-mortem".
    re.compile(r"\bgit\s+(?:blame|log)\b", re.I),
    re.compile(r"\b(?:incident|postmortem|post-mortem|RFC|ADR)\b"),
    # "commit <sha>" pattern — catches humans who cite commits without
    # a bare SHA in isolation.
    re.compile(r"\bcommit(?:ted)?\s+[0-9a-f]{6,}", re.I),
)


def _classify_origin_evidence(text: Any) -> OriginEvidenceClass:
    """Classify a Fence Reconstruction `origin_evidence` field.

    Priority: legacy > evidence > unknown. See the module docstring
    § CP5 for the rule set rationale.
    """
    if not isinstance(text, str):
        return "unknown"
    stripped = text.strip()
    if len(stripped) < 10:
        return "unknown"
    if any(pat.search(stripped) for pat in _LAZY_EVIDENCE_PATTERNS):
        return "legacy"
    if any(pat.search(stripped) for pat in _EVIDENCE_MARKER_PATTERNS):
        return "evidence"
    return "unknown"


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
