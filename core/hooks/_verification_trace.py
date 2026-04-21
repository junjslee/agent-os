#!/usr/bin/env python3
"""Layer 4 · verification_trace schema validator — v1.0 RC CP6.

The write-time commitment field of the Reasoning Surface. Forces the
author to name an executable observable (command / dashboard URL /
test id) the kernel can retrospectively check against agent bash
history at Layer 6 (CP7).

## Why Layer 4 exists

Layers 2 and 3 classify the *shape* of a surface's trigger + observable
text. The three spec fluent-vacuous examples from
`docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § "Why this exists" —
*"the migration may produce unexpected behavior..."*, etc. — pass
Layers 2 + 3 honestly: their verbs (`produces`, `exhibits`, `diverge`)
are accepted as observable-shaped at L2, and they carry no
entity-shaped tokens so L3 has no surface area. They leak through by
committing to NOTHING executable. Layer 4 closes that gap by
requiring a parseable command / URL / test-id the agent CAN
retrospectively be held to.

## Validation rules (RC scope)

- At least ONE of `command` / `or_dashboard` / `or_test` must be
  non-empty AND parse successfully in its slot.
- `command` — `shlex.split` succeeds AND >= 2 tokens (bare single-word
  commitments like `"verify"` reject).
- `or_dashboard` — `urllib.parse.urlparse` scheme in {http, https}
  AND non-empty netloc.
- `or_test` — matches the pytest id shape `path::test_name` OR the
  unittest id shape `module.Class.test_name`. Makefile / ad-hoc
  runners belong in the `command` slot.
- `window_seconds` — positive int when present. Required for highest-
  impact-list (v1.0.1 enforcement); advisory-only at RC.
- `threshold_observable` — required when `command` is set. Strict
  grammar: must contain one of `>`, `<`, `>=`, `<=`, `==`, `!=` AND
  at least one digit sequence. Forces a real numeric comparison
  rather than a hand-wavy "I'll watch it."

## Fence Reconstruction — rollback_path as verification

Fence's blueprint declares `verification_trace_maps_to: rollback_path`.
The guard wraps the Fence surface's `rollback_path` string as a
command-slot and runs a *reversible-context smoke test* (not actual
execution — running the rollback at PreToolUse would undo the
constraint removal before it happens):

1. `shlex.split` — the command parses as a shell invocation.
2. Path-existence — any path-shaped argument resolves to a file in
   the project tree (reuses Layer 3's cached project file index).
3. Prod-absence — the command does NOT contain the narrow prod-
   marker deny-list (`prod`, `production`, `live`). Branch literals
   (`main`, `master`) excluded per CP6 plan decision — too many
   non-prod local contexts.

Full sandboxed rollback execution is v1.0.1+.

Spec: `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § Layer 4 ·
falsification-trace requirement.
"""
from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse


TraceVerdict = Literal[
    "valid",
    "absent",
    "shape_invalid",
    "unparseable_command",
    "no_observable",
]


# ---------- Field grammars (RC) ------------------------------------------

# pytest: `tests/foo.py::test_bar`, `tests/dir/foo::test_bar`,
# `foo.py::TestClass::test_method` — the common `path::name` shape.
_PYTEST_TEST_ID_RE = re.compile(r"^[\w./\-]+(?:\.py)?::[\w_:]+$")

# unittest-style: `package.module.TestClass.test_method`. Test-class
# name conventionally starts uppercase; test method starts `test_`.
_UNITTEST_TEST_ID_RE = re.compile(r"^[\w.]+\.[A-Z]\w+\.test_\w+$")

# Strict threshold_observable grammar: comparison operator AND digit.
# `p95 > 400ms` passes; `results look anomalous` does not. Loosen
# post-soak if FPs pile up on qualitative observables.
_THRESHOLD_OPERATOR_RE = re.compile(r">=|<=|==|!=|>|<")
_DIGIT_RE = re.compile(r"\d")

# Narrow prod-marker deny-list for Fence rollback_path (CP6 plan Q4).
# Branch literals `main` / `master` excluded — too many non-prod
# local contexts. Expand post-soak if real prod refs leak through.
_PROD_MARKERS_RE = re.compile(r"\b(?:prod|production|live)\b", re.IGNORECASE)

# Path-shaped token heuristic — must end in a recognised code / config
# file extension. Bare directories (`tests/`, `docs/`) and git refs
# (`main`, `HEAD`) are intentionally NOT flagged as paths: the
# rollback command can legitimately reference them. The path-existence
# check is about catching references to nonexistent FILES (`docs/GONE.md`),
# not every `/`-containing token. Loosen post-soak if real file
# references leak through without extensions.
_PATH_SHAPED_EXT_RE = re.compile(
    r"\.(?:py|md|yaml|yml|json|toml|sh|js|ts|jsx|tsx|go|rs|java|"
    r"cpp|hpp|c|h|sql|css|html|ini|cfg|conf|lock|txt|rst|xml|proto)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class VerificationTrace:
    """A Layer 4 verification trace. Fields are all optional at the
    dataclass level; `validate_trace` enforces the "at least one of
    command/or_dashboard/or_test" rule and the command-implies-observable
    rule."""

    command: str | None = None
    or_dashboard: str | None = None
    or_test: str | None = None
    window_seconds: int | None = None
    threshold_observable: str | None = None

    @classmethod
    def from_surface_field(cls, value: Any) -> "VerificationTrace | None":
        """Parse the `verification_trace` key from a surface dict.

        Returns None when absent or shape-invalid at the dict level.
        Validation failures surface as TraceVerdict through
        `validate_trace`, not as exceptions here.
        """
        if not isinstance(value, dict):
            return None

        def _str_or_none(x: Any) -> str | None:
            if not isinstance(x, str):
                return None
            stripped = x.strip()
            return stripped or None

        def _int_or_none(x: Any) -> int | None:
            # bool is a subclass of int — reject it explicitly.
            if isinstance(x, bool):
                return None
            if isinstance(x, int) and x > 0:
                return x
            return None

        return cls(
            command=_str_or_none(value.get("command")),
            or_dashboard=_str_or_none(value.get("or_dashboard")),
            or_test=_str_or_none(value.get("or_test")),
            window_seconds=_int_or_none(value.get("window_seconds")),
            threshold_observable=_str_or_none(value.get("threshold_observable")),
        )


# ---------- Slot parsers -------------------------------------------------


def _parse_command(text: str) -> list[str] | None:
    """shlex-split. Returns the token list when >= 2 tokens, else None.

    A single-word commitment (`"verify"`, `"check"`) is not a runnable
    command — the kernel cannot hold the agent to it. Reject.
    """
    try:
        tokens = shlex.split(text)
    except ValueError:
        return None
    return tokens if len(tokens) >= 2 else None


def _parse_dashboard(text: str) -> bool:
    try:
        parsed = urlparse(text)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _parse_test_id(text: str) -> bool:
    return bool(
        _PYTEST_TEST_ID_RE.match(text) or _UNITTEST_TEST_ID_RE.match(text)
    )


def _threshold_is_specific(text: str) -> bool:
    """Strict grammar: comparison operator AND digit sequence both present."""
    return bool(
        _THRESHOLD_OPERATOR_RE.search(text) and _DIGIT_RE.search(text)
    )


# ---------- Trace validator ----------------------------------------------


def validate_trace(
    trace: "VerificationTrace | None",
) -> tuple[TraceVerdict, str]:
    """Validate a VerificationTrace against the RC field contract.

    Returns ``(verdict, detail)`` where ``detail`` is a one-line
    message naming the exact failure. Caller decides whether to block
    or advisory based on (a) the op's high-impact classification and
    (b) the blueprint's ``verification_trace_required`` flag.
    """
    if trace is None:
        return ("absent", "verification_trace is not present in the surface")

    slots_filled: list[str] = []

    if trace.command:
        if _parse_command(trace.command) is None:
            return (
                "unparseable_command",
                f"verification_trace.command is not a shell-parseable command "
                f"with >= 2 tokens (got {trace.command!r})",
            )
        slots_filled.append("command")

    if trace.or_dashboard:
        if not _parse_dashboard(trace.or_dashboard):
            return (
                "shape_invalid",
                f"verification_trace.or_dashboard is not a parseable http(s) "
                f"URL (got {trace.or_dashboard!r})",
            )
        slots_filled.append("or_dashboard")

    if trace.or_test:
        if not _parse_test_id(trace.or_test):
            return (
                "shape_invalid",
                f"verification_trace.or_test does not match pytest id "
                f"`path::test_name` or unittest id `module.Class.test_name` "
                f"(got {trace.or_test!r}). Makefile / ad-hoc runners belong "
                f"in the `command` slot.",
            )
        slots_filled.append("or_test")

    if not slots_filled:
        return (
            "shape_invalid",
            "verification_trace must declare at least one of `command`, "
            "`or_dashboard`, or `or_test` with a non-empty value",
        )

    # command-implies-observable: `command` without `threshold_observable`
    # is the fluent-vacuous escape shape — author names an executable
    # but declines to name what counts as failure.
    if "command" in slots_filled:
        if not trace.threshold_observable:
            return (
                "no_observable",
                "verification_trace.command requires a matching "
                "`threshold_observable` (must contain a comparison operator "
                "`>`, `<`, `>=`, `<=`, `==`, `!=` AND a digit sequence — "
                "e.g. `p95 > 400ms`, `exit_code != 0`)",
            )
        if not _threshold_is_specific(trace.threshold_observable):
            return (
                "no_observable",
                f"verification_trace.threshold_observable fails strict grammar "
                f"(must contain a comparison operator AND a digit sequence; "
                f"got {trace.threshold_observable!r})",
            )

    return ("valid", "")


# ---------- Fence rollback_path smoke test -------------------------------


def smoke_test_rollback_path(
    rollback_path: str,
    cwd: Path,
) -> tuple[TraceVerdict, str]:
    """Treat the Fence surface's `rollback_path` as a Layer 4 command
    slot. Runs a reversible-context smoke test per spec § Blueprint B:

    1. ``shlex.split`` succeeds AND command has >= 2 tokens.
    2. Prod-marker absence — the command does NOT contain
       ``prod`` / ``production`` / ``live``.
    3. Path-existence — any path-shaped argument resolves to a file
       present in the project tree. Reuses Layer 3's cached project
       file index. Tolerant: if the index cannot be built, the check
       is skipped (syntactic + prod-marker remain enforced).

    Returns ``(verdict, detail)``. ``valid`` = smoke test green;
    other verdicts block.
    """
    tokens = _parse_command(rollback_path)
    if tokens is None:
        return (
            "unparseable_command",
            f"Fence rollback_path is not a shell-parseable command with "
            f">= 2 tokens (got {rollback_path!r})",
        )

    if _PROD_MARKERS_RE.search(rollback_path):
        return (
            "shape_invalid",
            f"Fence rollback_path references a production marker "
            f"(prod / production / live). The rollback must operate in a "
            f"reversible context, not against prod. Rewrite against the "
            f"staging or local branch.",
        )

    # Path-existence — lazy import of Layer 3's fingerprint index.
    import sys

    _hooks_dir = Path(__file__).resolve().parent
    if str(_hooks_dir) not in sys.path:
        sys.path.insert(0, str(_hooks_dir))
    try:
        from _grounding import (  # type: ignore  # pyright: ignore[reportMissingImports]
            _load_project_fingerprint as _fingerprint,
        )
    except ImportError:
        return ("valid", "")

    # Only path-shaped tokens go through the grounding check. Drop the
    # first token (command executable like `git`, `cp`), then filter
    # for tokens ending in a recognised code / config file extension.
    # Bare directories (`tests/`), git refs (`main`, `HEAD`), and env
    # var assignments (`PYTHONPATH=.`) intentionally pass — the check is
    # about catching nonexistent-FILE references, not every `/`-bearing
    # token.
    tail = tokens[1:] if tokens else []
    path_shaped = [
        tok for tok in tail
        if _PATH_SHAPED_EXT_RE.search(tok) and not tok.startswith("-")
    ]
    if not path_shaped:
        return ("valid", "")

    try:
        filenames, _ = _fingerprint(cwd)
    except Exception:
        return ("valid", "")

    missing: list[str] = []
    for tok in path_shaped:
        # Strip leading `./` and trailing `/`; normalize once.
        normalized = tok.lstrip("./").rstrip("/")
        if not normalized:
            continue
        if normalized in filenames:
            continue
        # Also accept basename match (git ls-files already includes
        # both full relpath and basename per _grounding's loader).
        if Path(normalized).name in filenames:
            continue
        missing.append(tok)

    if missing:
        return (
            "shape_invalid",
            f"Fence rollback_path references path(s) absent from the "
            f"project tree: {', '.join(missing)}. A rollback that names "
            f"nonexistent paths cannot restore the constraint.",
        )

    return ("valid", "")
