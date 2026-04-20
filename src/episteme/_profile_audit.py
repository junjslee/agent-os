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


# Per-axis dispatch table. Populated by checkpoints 2-5 as each axis's
# real handler lands. Every insertion into this dict is a commitment that
# the corresponding axis is fully operationalized per its spec entry.
_AXIS_HANDLERS: dict[str, Any] = {
    # Checkpoint 2 will insert: "fence_discipline": _axis_fence_discipline
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
