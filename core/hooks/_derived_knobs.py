#!/usr/bin/env python3
"""Derived behavior knobs — the bridge from operator profile to hook behavior.

The operator profile declares scored axes (kernel/OPERATOR_PROFILE_SCHEMA.md
section 4a/4b). Adapters compute a narrow, declared set of control signals
from those axes and write them to ~/.episteme/derived_knobs.json so the hook
layer can read them without parsing the profile itself on every invocation.

This module is the reader. The writer is adapter-side (episteme sync compiles
the knobs from the profile at sync time). Hooks should never block or fail on
missing knobs — each call returns a declared default when the knob is absent.

File format (JSON):

    {
      "disconfirmation_specificity_min": 27,
      "unknown_specificity_min": 27,
      "default_autonomy_class": "confirm-irreversible",
      "preferred_lens_order": ["failure-first", "causal-chain", ...],
      "noise_watch_set": ["status-pressure", "false-urgency"],
      "explanation_form": "causal-chain",
      "checkpoint_frequency": "medium",
      "scaffold_vs_terse": {"<domain>": "terse-technical"},
      "fence_check_strictness": 4
    }

Kernel anchor: `kernel/OPERATOR_PROFILE_SCHEMA.md` section 5 ("Derived
behavior knobs — what adapters compute"). Adding a new knob requires naming
which axis it derives from AND which failure mode its default would allow.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_KNOBS_PATH = Path.home() / ".episteme" / "derived_knobs.json"


def _load_all() -> dict:
    try:
        if not _KNOBS_PATH.is_file():
            return {}
        with open(_KNOBS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def load_knob(name: str, default: Any) -> Any:
    """Read a named knob from ~/.episteme/derived_knobs.json.

    Returns `default` on any failure (missing file, malformed JSON, missing
    key, type mismatch against default type). Hooks must not block on this.
    """
    knobs = _load_all()
    if name not in knobs:
        return default
    value = knobs[name]
    # Type-compatibility check: if default has a non-None type, require value
    # to match. Prevents a malformed knob file from silently changing a
    # numeric threshold to a string, etc.
    if default is not None and not isinstance(value, type(default)):
        return default
    return value


def compute_knobs_from_scores(
    process: dict[str, int],
    cognitive: dict[str, Any],
) -> dict[str, Any]:
    """Derive the declared knob set from scored profile axes.

    Inputs match the operator_profile.md v2 structure:
      `process` carries 0-5 integers for planning_strictness, risk_tolerance,
      testing_rigor, parallelism_preference, documentation_rigor,
      automation_level.
      `cognitive` carries the typed cognitive-style axes.

    This function is called by the adapter at sync time; hooks never call it
    directly. The formulas below are first-pass — conservative scaling from
    defaults, easy to revise once the friction analyzer produces evidence.
    """
    knobs: dict[str, Any] = {}

    def _int_or(v: Any, default: int) -> int:
        # Strict: malformed values (strings, None, nested structures) fall back
        # rather than coerce. Adapter must not silently rewrite the contract.
        return v if isinstance(v, int) and not isinstance(v, bool) else default

    # disconfirmation_specificity_min + unknown_specificity_min derive from
    # uncertainty_tolerance (epistemic) and testing_rigor (consequential).
    # Base 15; each point above 2 on either axis adds 3 chars.
    ut = _int_or(cognitive.get("uncertainty_tolerance"), 2)
    tr = _int_or(process.get("testing_rigor"), 2)
    base = 15
    bump = 3 * max(0, ut - 2) + 3 * max(0, tr - 2)
    knobs["disconfirmation_specificity_min"] = base + bump
    knobs["unknown_specificity_min"] = base + bump

    # default_autonomy_class derives from risk_tolerance + asymmetry_posture.
    rt = _int_or(process.get("risk_tolerance"), 2)
    ap = str(cognitive.get("asymmetry_posture") or "balanced")
    if rt <= 1 or ap == "loss-averse":
        knobs["default_autonomy_class"] = "confirm-irreversible"
    elif rt >= 4 and ap == "convexity-seeking":
        knobs["default_autonomy_class"] = "permit-reversible"
    else:
        knobs["default_autonomy_class"] = "confirm-irreversible"

    # preferred_lens_order is the cognitive.dominant_lens list verbatim.
    dl = cognitive.get("dominant_lens")
    if isinstance(dl, list) and dl:
        knobs["preferred_lens_order"] = [str(x) for x in dl if isinstance(x, str)]

    # noise_watch_set is the operator's self-declared susceptibility.
    ns = cognitive.get("noise_signature") or {}
    watch: list[str] = []
    if isinstance(ns, dict):
        for key in ("primary", "secondary"):
            v = ns.get(key)
            if isinstance(v, str) and v:
                watch.append(v)
    if watch:
        knobs["noise_watch_set"] = watch

    # explanation_form mirrors cognitive.explanation_depth.
    ed = cognitive.get("explanation_depth")
    if isinstance(ed, str) and ed:
        knobs["explanation_form"] = ed

    # fence_check_strictness mirrors cognitive.fence_discipline.
    fd = cognitive.get("fence_discipline")
    if isinstance(fd, int) and not isinstance(fd, bool):
        knobs["fence_check_strictness"] = fd

    return knobs


def write_knobs(knobs: dict[str, Any]) -> Path:
    """Atomic write of the derived-knobs file. Adapter entry point."""
    _KNOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = _KNOBS_PATH.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(knobs, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    tmp.replace(_KNOBS_PATH)
    return _KNOBS_PATH


def knobs_path() -> Path:
    """Public accessor for the knobs file location (used by doctor/tests)."""
    return _KNOBS_PATH
