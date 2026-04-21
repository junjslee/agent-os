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

import re
import sys
from pathlib import Path
from typing import Any


# The generic fallback name is the only blueprint CP2 knows about.
# Defined as a module-level constant so CP3-CP10 callers can reference
# the exact literal without stringly-typed coupling.
GENERIC_FALLBACK = "generic"
FENCE_RECONSTRUCTION = "fence_reconstruction"


# ---------------------------------------------------------------------------
# CP5: Fence Reconstruction selector
#
# Compound AND gate — a removal-verb lexicon hit AND a constraint-
# bearing-path match must BOTH be present in the same Bash command.
# Patterns are loaded once per process from the blueprint YAML's
# `selector_triggers` (so the YAML stays the source of truth) and
# compiled lazily on first use.
# ---------------------------------------------------------------------------

_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))


_TRIGGER_CACHE: list[dict[str, Any]] | None = None


def _load_fence_triggers() -> list[dict[str, Any]]:
    """Load + compile Fence Reconstruction selector triggers from the
    blueprint YAML. Cached per-process. Graceful degrade on any parse
    error — returns empty list so Fence never fires, and the op falls
    back to generic validation rather than crashing the hot path."""
    global _TRIGGER_CACHE
    if _TRIGGER_CACHE is not None:
        return _TRIGGER_CACHE
    try:
        from _blueprint_registry import load_registry  # type: ignore  # pyright: ignore[reportMissingImports]
    except ImportError:
        _TRIGGER_CACHE = []
        return _TRIGGER_CACHE
    try:
        registry = load_registry()
        fence = registry.get(FENCE_RECONSTRUCTION)
    except Exception:
        _TRIGGER_CACHE = []
        return _TRIGGER_CACHE
    compiled: list[dict[str, Any]] = []
    for trig in fence.selector_triggers:
        if not isinstance(trig, dict):
            continue
        try:
            lex = re.compile(trig["removal_lexicon_pattern"])
            path = re.compile(trig["constraint_path_pattern"])
        except (re.error, KeyError, TypeError):
            continue
        applies_to = str(trig.get("applies_to", "Bash"))
        compiled.append({
            "lexicon": lex,
            "path": path,
            "applies_to": applies_to,
        })
    _TRIGGER_CACHE = compiled
    return compiled


def _reset_trigger_cache_for_tests() -> None:
    """Test-only: force reload of compiled triggers after fixture edits."""
    global _TRIGGER_CACHE
    _TRIGGER_CACHE = None


def _extract_bash_command(pending_op: dict[str, Any]) -> str:
    """Pull the Bash command text from a normalized payload. Returns ""
    when the payload isn't Bash or no command is present."""
    tool_name = str(
        pending_op.get("tool_name") or pending_op.get("toolName") or ""
    ).strip()
    if tool_name != "Bash":
        return ""
    raw = pending_op.get("tool_input") or pending_op.get("toolInput") or {}
    if not isinstance(raw, dict):
        return ""
    return str(
        raw.get("command")
        or raw.get("cmd")
        or raw.get("bash_command")
        or ""
    )


def _fence_fires(pending_op: dict[str, Any]) -> bool:
    """Return True iff some compiled trigger's lexicon AND path both
    match the Bash command and the trigger applies to this tool.

    Compound AND gate — either condition alone does not fire. This is
    the FP-averse discipline per spec § Blueprint B selector triggers
    and the user-approved CP5 plan decision.
    """
    cmd = _extract_bash_command(pending_op)
    if not cmd:
        return False
    triggers = _load_fence_triggers()
    if not triggers:
        return False
    tool_name = str(
        pending_op.get("tool_name") or pending_op.get("toolName") or ""
    ).strip()
    for trig in triggers:
        if trig["applies_to"] != tool_name:
            continue
        if trig["lexicon"].search(cmd) and trig["path"].search(cmd):
            return True
    return False


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
        `flaw_classification` declaration from the agent. Unused at CP5.
    project_context
        Project-level signals: cwd, git state, recent diff, etc. Unused
        at CP5 (Fence fires on Bash command text alone; CP10 will add
        diff-based triggers for Blueprint D).

    Returns
    -------
    str
        Blueprint name. At CP5: `"fence_reconstruction"` when the
        compound trigger matches (removal-verb lexicon AND
        constraint-bearing path both present in the same Bash command);
        `"generic"` otherwise.
    """
    del surface_text, project_context  # reserved for CP10
    if _fence_fires(pending_op):
        return FENCE_RECONSTRUCTION
    return GENERIC_FALLBACK
