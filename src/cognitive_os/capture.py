"""Draft a reasoning-surface.json skeleton from an unstructured text blob.

The Reasoning Surface is the canonical artifact cognitive-os produces before a
high-impact decision. Hand-authoring one from scratch is the single biggest
adoption friction. This module takes a Slack thread / PR description / ticket /
email and emits a draft surface the operator can edit in 5 minutes instead of
authoring from a blank file.

The draft is deliberately *imperfect*:
- Heuristics are declared, not hidden — every extracted field lists its source
  and the matching sentence so the operator can confirm or overrule.
- `disconfirmation` is never auto-filled — the whole point is that the operator
  declares it, so we emit an empty array with a visible reminder.
- `core_question` is extracted only if the input contains a question sentence;
  otherwise a placeholder is emitted and the operator is required to write it.

The output validates against `core/schemas/reasoning-surface-v1.json` when
filled in — but the draft itself intentionally contains placeholders the
operator must resolve.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


# ---------------------------------------------------------------------------
# Sentence split (dependency-free; good enough for the structured inputs we
# expect: Slack threads, tickets, PRs, emails).
# ---------------------------------------------------------------------------

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(\"'\[])")
_BULLET_PREFIX = re.compile(r"^\s*(?:[-*•·]|\d+[.)])\s+")


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, preserving bullet lines as individual units.

    Bullets from Slack/markdown often lack terminal punctuation, so we treat
    each bullet line as its own sentence before falling through to prose
    splitting.
    """
    out: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        stripped = _BULLET_PREFIX.sub("", line).strip()
        if not stripped:
            continue
        if _BULLET_PREFIX.match(line):
            out.append(stripped)
            continue
        for sent in _SENTENCE_BOUNDARY.split(stripped):
            sent = sent.strip()
            if sent:
                out.append(sent)
    return out


# ---------------------------------------------------------------------------
# Heuristic classifiers
# ---------------------------------------------------------------------------

_QUESTION_MARK = re.compile(r"\?\s*$")
_INTERROGATIVE_LEAD = re.compile(
    r"^(?:why|what|how|when|where|which|who|whether|should|can|could|would|do|does|did|is|are|will)\b",
    re.IGNORECASE,
)
_NUMBER_OR_DATE = re.compile(
    r"\b(?:\d+(?:[.,]\d+)?%?|\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2})\b"
)
_PROPER_NOUN_RUN = re.compile(r"\b[A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+)*\b")
_ASSUMPTION_MARKERS = (
    "assume", "assuming", "presumably", "probably", "likely", "i think",
    "i believe", "we think", "should be", "must be", "seems to", "appears to",
    "my guess", "i'd guess", "we'd guess", "i bet", "pretty sure",
)
_CLAIM_VERBS = (
    " is ", " are ", " was ", " were ", " has ", " have ", " shipped ",
    " deployed ", " dropped ", " rose ", " climbed ", " fell ",
    " reached ", " returned ", " shows ", " showed ", " confirmed ",
)


def _is_question(sent: str) -> bool:
    if _QUESTION_MARK.search(sent):
        return True
    return bool(_INTERROGATIVE_LEAD.match(sent))


def _is_assumption(sent: str) -> bool:
    low = sent.lower()
    return any(marker in low for marker in _ASSUMPTION_MARKERS)


def _is_factual_claim(sent: str) -> bool:
    """A sentence looks factual if it has a specific (number, date, or proper
    noun) AND a declarative verb AND is not a question or assumption."""
    if _is_question(sent) or _is_assumption(sent):
        return False
    has_specific = bool(_NUMBER_OR_DATE.search(sent)) or bool(
        _PROPER_NOUN_RUN.search(sent[1:])  # skip sentence-start capitalization
    )
    low = sent.lower()
    has_verb = any(v in f" {low} " for v in _CLAIM_VERBS)
    return has_specific and has_verb


# ---------------------------------------------------------------------------
# Core extraction
# ---------------------------------------------------------------------------

_PLACEHOLDER = "<TODO: operator must fill in>"


@dataclass
class DraftSurface:
    core_question: str = _PLACEHOLDER
    uncomfortable_friction: str = _PLACEHOLDER
    knowns: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    captured_at: str = ""
    captured_by: str = "cognitive-os capture"
    source_excerpt: str = ""

    def to_dict(self) -> dict:
        return {
            "$schema": "https://cognitive-os.dev/schemas/reasoning-surface-v1.json",
            "captured_at": self.captured_at,
            "captured_by": self.captured_by,
            "core_question": self.core_question,
            "uncomfortable_friction": self.uncomfortable_friction,
            "knowns": self.knowns,
            "unknowns": self.unknowns,
            "assumptions": self.assumptions,
            "disconfirmation": [],
            "constraints": {
                "allowed": [],
                "forbidden": [],
                "cost_ceiling_minutes": None,
            },
            "decision_type": _PLACEHOLDER,
            "failure_modes_in_scope": [],
            "_capture_metadata": {
                "source_excerpt": self.source_excerpt,
                "notes": [
                    "This file was drafted by `cognitive-os capture`. Fields "
                    "marked <TODO: ...> must be filled in by the operator. "
                    "disconfirmation[] and constraints{} are intentionally "
                    "empty — the posture requires the operator to declare "
                    "these, not the tool.",
                ],
            },
        }


def draft_from_text(
    text: str,
    *,
    captured_by: str | None = None,
    core_question_override: str | None = None,
    friction_override: str | None = None,
    max_items: int = 8,
) -> DraftSurface:
    """Produce a draft reasoning surface from unstructured text.

    Every classified sentence is attributed to its source so the operator can
    audit and overrule. No claim is invented — only sentences that appear
    verbatim in the input are emitted, re-categorized.
    """
    sentences = _split_sentences(text)

    unknowns = [s for s in sentences if _is_question(s)]
    assumptions = [s for s in sentences if _is_assumption(s)]
    knowns = [s for s in sentences if _is_factual_claim(s)]

    # Dedupe while preserving order.
    def _dedupe(items: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for s in items:
            if s in seen:
                continue
            seen.add(s)
            out.append(s)
        return out

    unknowns = _dedupe(unknowns)[:max_items]
    assumptions = _dedupe(assumptions)[:max_items]
    knowns = _dedupe(knowns)[:max_items]

    core_question = core_question_override or (unknowns[0] if unknowns else _PLACEHOLDER)

    friction = friction_override or _PLACEHOLDER
    if friction_override is None and sentences:
        for s in sentences:
            low = s.lower()
            if any(
                marker in low
                for marker in (
                    "regression", "dropped", "broken", "stuck",
                    "not finding", "can't find", "isn't working",
                )
            ):
                friction = s
                break

    excerpt = text.strip()
    if len(excerpt) > 1200:
        excerpt = excerpt[:1200].rstrip() + " …"

    return DraftSurface(
        core_question=core_question,
        uncomfortable_friction=friction,
        knowns=knowns,
        unknowns=unknowns,
        assumptions=assumptions,
        captured_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        captured_by=captured_by or "cognitive-os capture",
        source_excerpt=excerpt,
    )


# ---------------------------------------------------------------------------
# CLI entry points (invoked from cli.py)
# ---------------------------------------------------------------------------

def run_capture(
    *,
    input_path: Path | None,
    output_path: Path | None,
    captured_by: str | None = None,
    core_question: str | None = None,
    friction: str | None = None,
    print_only: bool = False,
) -> int:
    if input_path is None:
        text = sys.stdin.read()
    else:
        text = input_path.read_text(encoding="utf-8")

    if not text.strip():
        sys.stderr.write("cognitive-os capture: empty input\n")
        return 2

    draft = draft_from_text(
        text,
        captured_by=captured_by,
        core_question_override=core_question,
        friction_override=friction,
    )
    payload = draft.to_dict()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    if print_only or output_path is None:
        sys.stdout.write(rendered)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        sys.stdout.write(f"wrote {output_path}\n")

    filled = sum(
        1
        for v in (draft.core_question, draft.uncomfortable_friction)
        if v != _PLACEHOLDER
    )
    total_slots = 2
    sys.stderr.write(
        "draft summary: "
        f"{len(draft.knowns)} knowns, "
        f"{len(draft.unknowns)} unknowns, "
        f"{len(draft.assumptions)} assumptions, "
        f"{filled}/{total_slots} lead fields resolved, "
        "disconfirmation empty (operator must fill)\n"
    )
    return 0
