#!/usr/bin/env python3
"""Scenario detector — v1.0 RC CP2 scaffolding.

Maps `(pending_op, surface_text, project_context)` to a blueprint name.
The hot path at CP3 will call this at the top of Layer 2, feed the
returned name into the blueprint registry, and validate the Reasoning
Surface's required fields against the blueprint's shape.

## CP2 stub — always returns "generic"

No behavior change at CP2. The signature below is the contract CP3
commits to; the body is an explicit stub. Real selector logic lands
per the Implementation sequencing in
`docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § Implementation sequencing:

- **CP5** — Fence Reconstruction selector. Fires on constraint-removal
  patterns (git-diff signature against policy files + removal-lexicon
  hits like "remove", "delete", "disable" near a path inside
  `.episteme/` / security config / kernel policy).
- **CP10** — Architectural Cascade & Escalation selector. Four trigger
  classes: (1) cross-surface-ref diff without companion edits,
  (2) refactor/rename/deprecate/migrate/cleanup lexicon against files
  with >=2 cross-surface references, (3) self-escalation — agent
  declares `flaw_classification` in the surface, (4) symbol-reference
  check against generated artifacts (MANIFEST.sha256, CHANGELOG.md).

## Cost budget

Absorbed into Layer 2's 5 ms slot per the spec's hot-path latency
ceiling (<100 ms p95 for Layers 2-4 + detector + framework query
combined). At CP2 the detector is O(1) — body is a single `return`.

## Where the hot path calls this

At CP2: **nowhere.** `reasoning_surface_guard.py` does not yet consult
the detector — CP2 is substrate only. CP3 wires the call site into
`_surface_missing_fields` / its successor so Layer 2's classifier runs
against the blueprint-selected field set instead of the hardcoded four
fields.

Spec: `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § Pillar 1 · Cognitive
Blueprints § Selection logic.
"""
from __future__ import annotations

from typing import Any


# The generic fallback name is the only blueprint CP2 knows about.
# Defined as a module-level constant so CP3-CP10 callers can reference
# the exact literal without stringly-typed coupling.
GENERIC_FALLBACK = "generic"


def detect_scenario(
    pending_op: dict[str, Any],
    surface_text: str | None = None,
    project_context: dict[str, Any] | None = None,
) -> str:
    """Return the blueprint name that shapes this op's Reasoning Surface.

    Parameters
    ----------
    pending_op
        The tool-call payload under consideration. Shape depends on the
        runtime adapter; common keys include `tool_name`, `command`,
        `file_path`. The detector is tool-agnostic per the BYOS stance
        (spec § What episteme is — and what it is not) — it reads from
        a normalized shape the hook layer provides.
    surface_text
        The Reasoning Surface text (if present in cwd). Used by CP10's
        self-escalation selector to detect an explicit
        `flaw_classification` declaration from the agent.
    project_context
        Project-level signals: cwd, git state, recent diff, etc. Used
        by CP5 (constraint-removal patterns against policy-file paths)
        and CP10 (cross-surface-reference checks).

    Returns
    -------
    str
        The name of the blueprint whose field contract applies to this
        op. At CP2 this is always `"generic"` (the four-field fallback
        in `core/blueprints/generic_fallback.yaml`). CP5+ extend with
        named-scenario returns; the generic name remains the default
        when no named scenario fires.
    """
    # CP2 stub — pending_op / surface_text / project_context are read by
    # the real selectors at CP5 / CP10. Marking them as unused keeps
    # Pyright honest about the current behavior.
    del pending_op, surface_text, project_context
    return GENERIC_FALLBACK
