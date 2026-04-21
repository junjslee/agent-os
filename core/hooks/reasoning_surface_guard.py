#!/usr/bin/env python3
"""PreToolUse guard: high-impact ops require a valid Reasoning Surface.

Enforces the kernel rule `irreversible or high-blast-radius -> declare a
Reasoning Surface first` (kernel/CONSTITUTION.md, kernel/REASONING_SURFACE.md).

Behavior:
- Matches a high-impact pattern in Bash commands (git push, publish,
  migrations, cloud deletes, DB destructive SQL) or Write|Edit to irreversible
  files (lock files, secrets). Command text is normalized (quotes, commas,
  brackets, parens, backticks mapped to whitespace) before matching so bypass
  shapes like `python -c "subprocess.run(['git','push'])"`,
  `os.system('git push')`, or `` `git push` `` trip the same patterns as bare
  shell.
- **Indirection heuristics** (best-effort, avoid FPs):
    * `eval $VAR` / `eval "$VAR"` — blocked as variable-indirection.
    * Direct shell-script execution (`./x.sh`, `bash x.sh`, `sh x.sh`,
      `source x.sh`, `. x.sh`) is opened and scanned for high-impact patterns
      (capped at 64 KB; silently passed through if unreadable).
- Reads `.episteme/reasoning-surface.json` in the project cwd.
- A Surface is valid when: timestamp within SURFACE_TTL_SECONDS, non-empty
  core_question, at least one substantive unknown, and a disconfirmation
  field that meets minimum length and is not a lazy placeholder
  (none, n/a, tbd, 해당 없음, 없음, ...).
- **Default mode: STRICT (blocking).** Missing, stale, incomplete, or lazy
  surfaces exit 2 and block the op. Opt out per-project by creating
  `.episteme/advisory-surface`; the hook then emits advisory context only.
- Legacy marker `.episteme/strict-surface` is now a no-op (strict is default).
- **Calibration telemetry (Gap A):** on allowed Bash executions, writes a
  prediction record to `~/.episteme/telemetry/YYYY-MM-DD-audit.jsonl` with
  correlation_id, timestamp, command_executed, epistemic_prediction. A
  companion PostToolUse hook (`calibration_telemetry.py`) writes the matching
  outcome record carrying exit_code. Records are local-only, never committed.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# v1.0 RC CP3 — Layer 2 in the hot path, blueprint-aware.
# Import sibling hook modules (_specificity, _blueprint_registry,
# _scenario_detector) via sys.path injection so the guard works
# identically whether invoked as a standalone script by the host runtime
# (its own dir is on sys.path by default) or imported under pytest
# (which sets sys.path from pyproject's pythonpath = ["src", "."]
# extension at commit 2a2ed68). Same pattern CP1 used for
# _profile_audit.py's _specificity import.
_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

from _blueprint_registry import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    BlueprintParseError as _BlueprintParseError,
    BlueprintValidationError as _BlueprintValidationError,
    load_registry as _load_registry,
)
from _scenario_detector import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    detect_scenario as _detect_scenario,
)
from _specificity import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    _classify_disconfirmation as _classify_for_layer2,
    _classify_origin_evidence as _classify_origin,
)
from _grounding import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    ground_blueprint_fields as _layer3_ground_blueprint_fields,
)
from _verification_trace import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    VerificationTrace as _VerificationTrace,
    validate_trace as _validate_trace,
    smoke_test_rollback_path as _smoke_test_rollback,
)
import _fence_synthesis  # noqa: E402  # pyright: ignore[reportMissingImports]


SURFACE_TTL_SECONDS = 30 * 60  # 30 minutes


# Per-blueprint declaration of which required_fields the Layer-2
# specificity classifier actually runs against. Some fields are
# statements-of-fact (Knowns) or provisional-beliefs (Assumptions) —
# classifying them as "trigger+observable" would be a category error.
# CP3 seeds the generic fallback (classifier runs on `disconfirmation`
# and per-entry on `unknowns`). CP5 / CP10 add named-blueprint entries
# as Fence Reconstruction / Architectural Cascade land.
_CLASSIFIED_FIELDS_BY_BLUEPRINT: dict[str, tuple[str, ...]] = {
    "generic": ("disconfirmation", "unknowns"),
    # CP5: Fence adds `removal_consequence_prediction` — a fire-shape
    # field (trigger + observable) describing what breaks if the
    # constraint is removed. `origin_evidence` has a different
    # specificity rule (evidence markers, not trigger+observable) and
    # is validated separately by `_layer_fence_validate` below.
    "fence_reconstruction": (
        "disconfirmation",
        "unknowns",
        "removal_consequence_prediction",
    ),
}

# Minimum character thresholds — lazy one-word answers are rejected.
# These are now derived from the operator profile's uncertainty_tolerance +
# testing_rigor via ~/.episteme/derived_knobs.json (written by the adapter
# at `episteme sync` time; see `core/hooks/_derived_knobs.py` and
# `kernel/OPERATOR_PROFILE_SCHEMA.md` section 5). Fallback is the historic
# default (15) when no profile-derived knobs have been computed yet.
# Inlined rather than imported so this hook stays self-contained — the hook
# is invoked as a standalone script by the host runtime with no guaranteed
# sys.path setup.
_MIN_LEN_DEFAULT = 15
_DERIVED_KNOBS_PATH = Path.home() / ".episteme" / "derived_knobs.json"


def _load_derived_knob(name: str, default):
    try:
        if not _DERIVED_KNOBS_PATH.is_file():
            return default
        with open(_DERIVED_KNOBS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or name not in data:
            return default
        value = data[name]
        if default is not None and not isinstance(value, type(default)):
            return default
        return value
    except (OSError, json.JSONDecodeError):
        return default


def _min_disconfirmation_len() -> int:
    return int(_load_derived_knob("disconfirmation_specificity_min", _MIN_LEN_DEFAULT))


def _min_unknown_len() -> int:
    return int(_load_derived_knob("unknown_specificity_min", _MIN_LEN_DEFAULT))

# Lazy-token blocklist: strings that defeat the Reasoning Surface contract
# by providing fluent-looking placeholders instead of measurable conditions.
# Matched case-insensitively against whitespace-collapsed content.
LAZY_TOKENS = frozenset({
    "none", "null", "nil", "nothing", "undefined",
    "n/a", "na", "n.a.", "n.a", "not applicable",
    "tbd", "todo", "to be determined", "to be decided",
    "unknown", "idk", "i don't know", "no idea",
    "해당 없음", "해당없음", "없음", "모름", "모르겠음",
    "해당 사항 없음", "해당사항없음",
    "-", "--", "---", "—", "...", "...",
    "pending", "later", "maybe", "?",
})

HIGH_IMPACT_BASH = [
    (re.compile(r"\bgit\s+push\b"), "git push"),
    (re.compile(r"\bgit\s+merge\b(?!\s+--abort)"), "git merge"),
    (re.compile(r"\bnpm\s+publish\b"), "npm publish"),
    (re.compile(r"\byarn\s+publish\b"), "yarn publish"),
    (re.compile(r"\bpnpm\s+publish\b"), "pnpm publish"),
    (re.compile(r"\bpoetry\s+publish\b"), "poetry publish"),
    (re.compile(r"\bcargo\s+publish\b"), "cargo publish"),
    (re.compile(r"\btwine\s+upload\b"), "twine upload"),
    (re.compile(r"\bpip\s+install\b(?!.*--dry-run)"), "pip install"),
    (re.compile(r"\bpip\s+uninstall\b"), "pip uninstall"),
    (re.compile(r"\balembic\s+upgrade\b"), "alembic upgrade"),
    (re.compile(r"\bprisma\s+migrate\s+deploy\b"), "prisma migrate deploy"),
    (re.compile(r"\bterraform\s+apply\b"), "terraform apply"),
    (re.compile(r"\bterraform\s+destroy\b"), "terraform destroy"),
    (re.compile(r"\bkubectl\s+(?:delete|apply)\b"), "kubectl delete/apply"),
    (re.compile(r"\baws\s+s3\s+rm\b"), "aws s3 rm"),
    (re.compile(r"\bgcloud\b.*\bdelete\b"), "gcloud delete"),
    (re.compile(r"\bDROP\s+(?:TABLE|DATABASE|SCHEMA)\b", re.I), "SQL DROP"),
    (re.compile(r"\bTRUNCATE\s+TABLE\b", re.I), "SQL TRUNCATE"),
    (re.compile(r"\bgh\s+pr\s+merge\b"), "gh pr merge"),
    (re.compile(r"\bgh\s+release\s+create\b"), "gh release create"),
]

IRREVERSIBLE_WRITE_PATHS = (
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Pipfile.lock",
    "Cargo.lock",
    "go.sum",
)

# Characters that separate tokens in quoted / bracketed / parenthesized /
# backtick invocations. Normalize these to a space so regex-word-boundary
# patterns catch `subprocess.run(['git','push'])`, `os.system("git push")`,
# and `` `git push` `` the same way they catch bare `git push`.
_NORMALIZE_SEPARATORS = re.compile(r"[,'\"\[\]\(\)\{\}`]")

# Indirection patterns — blocked even when the direct op name isn't literally
# present. These intentionally target constructs whose legitimate uses are
# rare enough that per-project advisory opt-out is an acceptable escape.
INDIRECTION_BASH = [
    (re.compile(r"\beval\s+[\"']?\$"), "eval with variable indirection"),
]

# Shell-script execution interceptors. Matched AFTER direct/indirection
# patterns miss; if any matches, the referenced script is opened and scanned
# for high-impact patterns. Only `.sh` files are considered (avoids scanning
# binaries / arbitrary executables).
_SCRIPT_EXEC_PATTERNS = [
    # `bash X.sh`, `sh X.sh`, `zsh X.sh`, `ksh X.sh`
    re.compile(r"\b(?:bash|sh|zsh|ksh)\s+([^\s;&|]+\.sh)\b"),
    # `source X.sh`, `. X.sh`
    re.compile(r"(?:\bsource\s+|(?:^|[;&|]\s*)\.\s+)([^\s;&|]+\.sh)\b"),
    # `./X.sh`, `/abs/path/X.sh`
    re.compile(r"(?:^|\s)((?:\.\/|\/)[^\s;&|]+\.sh)\b"),
]

# Cap script reads to keep the hook fast and bounded.
MAX_SCRIPT_SCAN_BYTES = 64 * 1024

# Variable-indirection execution shapes used with agent-written files. When
# these appear alongside a recent agent-write in the state store, we block
# even without a literal file reference — the agent has taken the file-name
# out of the command text to defeat pattern matching.
_INDIRECT_EXEC_PATTERNS = [
    re.compile(r"\b(?:bash|sh|zsh|ksh)\s+\$"),
    re.compile(r"\bpython\d?\s+\$"),
    re.compile(r"\bnode\s+\$"),
    re.compile(r"(?:^|\s)(?:\./|source\s+|\.\s+)\$"),
]


def _normalize_command(cmd: str) -> str:
    """Map shell / language token separators to spaces for robust matching."""
    return _NORMALIZE_SEPARATORS.sub(" ", cmd)


def _tool_name(payload: dict) -> str:
    return str(payload.get("tool_name") or payload.get("toolName") or "").strip()


def _tool_input(payload: dict) -> dict:
    raw = payload.get("tool_input") or payload.get("toolInput") or {}
    return raw if isinstance(raw, dict) else {}


def _bash_command(payload: dict) -> str:
    ti = _tool_input(payload)
    return str(ti.get("command") or ti.get("cmd") or ti.get("bash_command") or "")


def _write_target(payload: dict) -> str:
    ti = _tool_input(payload)
    return str(ti.get("file_path") or ti.get("path") or ti.get("target_file") or "")


def _match_against_patterns(text: str) -> str | None:
    """Return the first high-impact / indirection label that matches `text`."""
    for pattern, label in HIGH_IMPACT_BASH:
        if pattern.search(text):
            return label
    for pattern, label in INDIRECTION_BASH:
        if pattern.search(text):
            return label
    return None


def _resolve_script_path(cwd: Path, raw: str) -> Path | None:
    """Best-effort resolution of a script reference against `cwd`.

    Returns None if the path escapes bounds, doesn't exist, or is not a file.
    """
    raw = raw.strip()
    if not raw:
        return None
    try:
        candidate = Path(raw) if Path(raw).is_absolute() else (cwd / raw)
        candidate = candidate.resolve(strict=False)
    except (OSError, RuntimeError):
        return None
    if not candidate.exists() or not candidate.is_file():
        return None
    return candidate


def _match_script_execution(cwd: Path, cmd: str) -> str | None:
    """If `cmd` runs a .sh script, scan that script's content for high-impact ops.

    Best-effort: missing / unreadable / oversized scripts pass through without
    blocking. This keeps legitimate automation unaffected when script content
    is absent or produced on-the-fly.
    """
    for pattern in _SCRIPT_EXEC_PATTERNS:
        for match in pattern.finditer(cmd):
            script_ref = match.group(1)
            resolved = _resolve_script_path(cwd, script_ref)
            if resolved is None:
                continue
            try:
                with open(resolved, "rb") as f:
                    raw_bytes = f.read(MAX_SCRIPT_SCAN_BYTES + 1)
            except OSError:
                continue
            if len(raw_bytes) > MAX_SCRIPT_SCAN_BYTES:
                # Truncate at cap; still scan what we have.
                raw_bytes = raw_bytes[:MAX_SCRIPT_SCAN_BYTES]
            try:
                content = raw_bytes.decode("utf-8", errors="replace")
            except Exception:
                continue
            inner_label = _match_against_patterns(_normalize_command(content))
            if inner_label:
                return f"{inner_label} via {script_ref}"
    return None


def _state_store_path() -> Path:
    return Path.home() / ".episteme" / "state" / "session_context.json"


def _load_session_state() -> dict:
    """Load the session state store. Returns empty entries on any error."""
    try:
        with open(_state_store_path(), "r", encoding="utf-8") as f:
            obj = json.load(f)
        if isinstance(obj, dict) and isinstance(obj.get("entries"), dict):
            return obj
    except (OSError, json.JSONDecodeError):
        pass
    return {"version": 1, "entries": {}}


def _scan_agent_written_file(path: Path) -> str | None:
    """Open an agent-written file and scan its content for high-impact patterns."""
    try:
        with open(path, "rb") as f:
            raw = f.read(MAX_SCRIPT_SCAN_BYTES + 1)
    except OSError:
        return None
    if len(raw) > MAX_SCRIPT_SCAN_BYTES:
        raw = raw[:MAX_SCRIPT_SCAN_BYTES]
    try:
        content = raw.decode("utf-8", errors="replace")
    except Exception:
        return None
    return _match_against_patterns(_normalize_command(content))


def _match_agent_written_files(cmd: str) -> str | None:
    """Deep-scan recently agent-written files the command references.

    Consults the session state store (populated by `state_tracker.py` on
    PostToolUse Write/Edit/MultiEdit/Bash). Two match modes:

      1. The command text literally mentions the stored absolute path or
         the file's basename — scan that file's current content.
      2. The command uses a variable-indirection execution shape
         (`bash $X`, `python $X`, etc.) and the state store has ANY
         recently-written tracked file — scan each one. This closes
         `F=run.sh; bash $F` bypass style.
    """
    state = _load_session_state()
    entries = state.get("entries", {})
    if not entries:
        return None

    uses_indirection = any(p.search(cmd) for p in _INDIRECT_EXEC_PATTERNS)

    for abs_path in entries.keys():
        try:
            p = Path(abs_path)
        except (TypeError, ValueError):
            continue
        if not p.exists() or not p.is_file():
            continue

        basename = p.name
        mentioned = (abs_path in cmd) or (
            basename and re.search(rf"(?<![A-Za-z0-9_./-]){re.escape(basename)}\b", cmd)
        )
        if not (mentioned or uses_indirection):
            continue

        inner = _scan_agent_written_file(p)
        if inner:
            return f"{inner} via agent-written {basename}"
    return None


def _match_high_impact(tool_name: str, payload: dict) -> str | None:
    if tool_name == "Bash":
        cmd = _bash_command(payload)
        normalized = _normalize_command(cmd)
        label = _match_against_patterns(normalized)
        if label:
            return label
        cwd = Path(payload.get("cwd") or os.getcwd())
        label = _match_script_execution(cwd, cmd)
        if label:
            return label
        return _match_agent_written_files(cmd)
    if tool_name in {"Write", "Edit", "MultiEdit"}:
        target = _write_target(payload).replace("\\", "/")
        name = Path(target).name if target else ""
        for lock in IRREVERSIBLE_WRITE_PATHS:
            if name == lock:
                return f"edit {lock}"
        return None
    return None


def _read_surface(cwd: Path) -> dict | None:
    p = cwd / ".episteme" / "reasoning-surface.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _surface_age_seconds(surface: dict) -> int | None:
    ts = surface.get("timestamp")
    if not ts:
        return None
    try:
        if isinstance(ts, (int, float)):
            return int(time.time() - float(ts))
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(time.time() - dt.timestamp())
    except (ValueError, TypeError):
        return None


def _is_lazy(text: str) -> bool:
    """Return True when `text` is a placeholder rather than a real commitment."""
    collapsed = re.sub(r"\s+", " ", text.strip().lower())
    if not collapsed:
        return True
    if collapsed in LAZY_TOKENS:
        return True
    # Also catch "none." / "n/a!" etc. — trim trailing punctuation and retry.
    stripped = collapsed.rstrip(".!?,;:")
    return stripped in LAZY_TOKENS


def _surface_missing_fields(surface: dict) -> list[str]:
    """Return the list of fields that fail the kernel's validation contract.

    A field is considered missing if it is absent, empty, lazy-placeholder,
    or (for disconfirmation/unknowns) below the minimum-length threshold.
    """
    missing: list[str] = []

    core_q = str(surface.get("core_question") or "").strip()
    if not core_q or _is_lazy(core_q):
        missing.append("core_question")

    unknown_min = _min_unknown_len()
    disc_min = _min_disconfirmation_len()

    unknowns = surface.get("unknowns")
    if not isinstance(unknowns, list):
        missing.append("unknowns")
    else:
        substantive = [
            str(u).strip()
            for u in unknowns
            if str(u).strip()
            and not _is_lazy(str(u))
            and len(str(u).strip()) >= unknown_min
        ]
        if not substantive:
            missing.append("unknowns")

    disc = str(surface.get("disconfirmation") or "").strip()
    if not disc or _is_lazy(disc) or len(disc) < disc_min:
        missing.append("disconfirmation")

    return missing


def _layer2_classify_blueprint_fields(
    surface: dict,
    pending_op: dict,
) -> tuple[str, str]:
    """Layer 2 · v1.0 RC CP3: blueprint-aware specificity classifier.

    Runs AFTER Layer 1 (`_surface_missing_fields`) has already passed.
    Consults the scenario detector for the selected blueprint name,
    loads that blueprint from the registry, and classifies each of the
    blueprint's classifier-eligible fields via `_classify_disconfirmation`.

    Returns ``(verdict, detail)`` where ``verdict`` is one of:

    - ``"pass"``     — every classifier-eligible field classifies as ``fire``
                       (conditional trigger + specific observable). Surface
                       proceeds to the existing ok path.
    - ``"advisory"`` — at least one field classifies as ``absence``
                       (`if no issues arise`-shape). Surface still passes;
                       caller emits a one-line stderr advisory.
    - ``"reject"``   — at least one field classifies as ``tautological``
                       or ``unknown``. Surface is rejected with detail
                       naming the failing fields; caller treats this
                       identically to a Layer-1 ``incomplete`` result.

    Graceful degrade: any error in the scenario detector, registry
    load, or classifier yields ``("pass", "")`` plus a one-line stderr
    note. Layer 1 already passed; we do not synthesize a block from
    our own infrastructure failing.
    """
    try:
        blueprint_name = _detect_scenario(
            pending_op, surface_text=None, project_context={}
        )
        blueprint = _load_registry().get(blueprint_name)
    except (_BlueprintParseError, _BlueprintValidationError, KeyError, OSError) as exc:
        sys.stderr.write(
            f"[episteme] Layer 2 fallback: blueprint registry error "
            f"({exc.__class__.__name__}); Layer-1 validation still enforced.\n"
        )
        return ("pass", "")

    classified_fields = _CLASSIFIED_FIELDS_BY_BLUEPRINT.get(blueprint.name, ())
    if not classified_fields:
        return ("pass", "")

    rejections: list[str] = []
    advisories: list[str] = []
    required = set(blueprint.required_fields)

    for field_name in classified_fields:
        if field_name not in required:
            continue  # classifier map lists a field the blueprint doesn't require
        value = surface.get(field_name)
        if field_name == "unknowns" and isinstance(value, list):
            # Per-entry classification. Each unknown carries its own
            # trigger+observable contract under the v1.0 RC blueprint
            # rules (spec § Layer 2 — "the generic surface's
            # `disconfirmation` and `unknowns` entries are classified
            # against the same contract").
            for i, entry in enumerate(value):
                verdict = _classify_for_layer2(entry)
                if verdict in ("tautological", "unknown"):
                    rejections.append(f"unknowns[{i}] ({verdict})")
                elif verdict == "absence":
                    advisories.append(f"unknowns[{i}] (absence)")
        else:
            verdict = _classify_for_layer2(value)
            if verdict in ("tautological", "unknown"):
                rejections.append(f"{field_name} ({verdict})")
            elif verdict == "absence":
                advisories.append(f"{field_name} (absence)")

    if rejections:
        detail = (
            f"Layer 2 classifier (blueprint `{blueprint.name}`) rejected: "
            + "; ".join(rejections)
            + ". A tautological field carries a conditional trigger "
              "(`if`/`when`/`should`/`once`/`after`/`unless`) but no specific "
              "observable (numeric threshold, metric name, failure verb, "
              "log/dashboard reference). Add an observable that would "
              "falsify the claim."
        )
        return ("reject", detail)

    if advisories:
        detail = (
            f"Layer 2 advisory (blueprint `{blueprint.name}`): "
            + "; ".join(advisories)
            + ". Absence-conditions (`if no issues arise`) are less useful "
              "than fire-conditions (`if p95 > 400ms`); consider sharpening."
        )
        return ("advisory", detail)

    return ("pass", "")


_FENCE_REQUIRED_FIELDS: tuple[str, ...] = (
    "constraint_identified",
    "origin_evidence",
    "removal_consequence_prediction",
    "reversibility_classification",
    "rollback_path",
)

_FENCE_REVERSIBILITY_VALUES: frozenset[str] = frozenset({
    "reversible", "irreversible"
})


def _layer_fence_validate(surface: dict) -> tuple[str, str]:
    """Fence Reconstruction-specific validation — v1.0 RC CP5.

    Runs AFTER Layer 1 / 2 / 3 pass on a surface whose blueprint was
    selected as `fence_reconstruction`. Checks:

    1. All 5 Fence-required fields are present, non-empty, non-lazy,
       and ≥ 15 chars. Absence of any field → reject.
    2. `origin_evidence` classifies as `"evidence"` via
       `_classify_origin_evidence`. `"legacy"` / `"unknown"` → reject
       with message pointing at the evidence-marker set.
    3. `reversibility_classification` is exactly `"reversible"` or
       `"irreversible"` (case-insensitive). Anything else → reject.
    4. When `reversibility == "irreversible"` → verdict
       ``"advisory-irreversible"`` so the caller emits a stderr
       escalation to Axiomatic Judgment and does NOT write a synthesis
       marker. The op is not blocked by Fence on this axis (Axiomatic
       Judgment blueprint lands at CP6 as structure-only).
    5. When all checks pass and reversibility is `"reversible"` →
       verdict ``"pass"``; caller proceeds to synthesis marker write.

    Returns ``(verdict, detail)`` where verdict ∈ {``"pass"``,
    ``"advisory-irreversible"``, ``"reject"``}.
    """
    missing: list[str] = []
    min_len = _min_disconfirmation_len()
    for field in _FENCE_REQUIRED_FIELDS:
        value = surface.get(field)
        if not isinstance(value, str):
            missing.append(field)
            continue
        stripped = value.strip()
        if not stripped or _is_lazy(stripped):
            missing.append(field)
            continue
        # reversibility is a short enum — don't apply min-length to it.
        if field == "reversibility_classification":
            continue
        if len(stripped) < min_len:
            missing.append(f"{field} (< {min_len} chars)")

    if missing:
        detail = (
            f"Fence Reconstruction blueprint selected but required fields are "
            f"missing, lazy, or too short: {', '.join(missing)}. Add "
            f"`constraint_identified` (file:line), `origin_evidence` "
            f"(git blame / commit SHA / issue ID / dated reference), "
            f"`removal_consequence_prediction` (observable), "
            f"`reversibility_classification` (`reversible` or `irreversible`), "
            f"and `rollback_path` (concrete revert procedure) to the "
            f".episteme/reasoning-surface.json."
        )
        return ("reject", detail)

    # Reversibility enum check.
    reversibility = str(
        surface.get("reversibility_classification") or ""
    ).strip().lower()
    if reversibility not in _FENCE_REVERSIBILITY_VALUES:
        detail = (
            f"Fence Reconstruction: `reversibility_classification` must be "
            f"`reversible` or `irreversible` (got {reversibility!r}). See "
            f"spec § Blueprint B."
        )
        return ("reject", detail)

    # origin_evidence — evidence markers vs legacy hedge.
    origin = surface.get("origin_evidence", "")
    evidence_verdict = _classify_origin(origin)
    if evidence_verdict != "evidence":
        detail = (
            f"Fence Reconstruction: `origin_evidence` classified as "
            f"`{evidence_verdict}` — the constraint's origin must cite a "
            f"concrete evidence marker (commit SHA, @file:line reference, "
            f"issue/incident ID, URL, dated event, or explicit "
            f"`git blame` / `post-mortem` citation). Soft hedges like "
            f"'unclear — probably legacy' do not reconstruct the fence; "
            f"they restate its absence."
        )
        return ("reject", detail)

    if reversibility == "irreversible":
        detail = (
            "Fence Reconstruction: `reversibility_classification = "
            "irreversible` — this op exceeds Blueprint B's scope. "
            "Escalate to Blueprint A (Axiomatic Judgment) which decomposes "
            "per-source conflicts on irreversible decisions. "
            "Axiomatic Judgment structural validation lands at CP6 as "
            "structure-only; full enforcement lands v1.0.1. Until then "
            "this is an advisory-only escalation (not a block). "
            "No constraint-safety protocol will be synthesized for an "
            "irreversible op."
        )
        return ("advisory-irreversible", detail)

    return ("pass", "")


def _layer4_fence_smoke_test(
    surface: dict,
    cwd: Path,
) -> tuple[str, str]:
    """Layer 4 · CP6 — Fence rollback_path smoke test.

    Runs AFTER `_layer_fence_validate` returns ``"pass"`` on a
    reversible Fence firing. The Fence blueprint declares
    ``verification_trace_maps_to: rollback_path`` — so the existing
    ``rollback_path`` field IS the Layer 4 verification trace. This
    function runs the reversible-context smoke test
    (``shlex.split`` + prod-marker absence + path-existence) against
    it. NOT actual rollback execution — running the rollback at
    PreToolUse would undo the constraint removal before it happens.

    Returns ``(verdict, detail)`` where verdict ∈ {``"pass"``,
    ``"reject"``}. Graceful degrade: any unexpected exception inside
    the smoke test yields ``("pass", "")`` with a stderr fallback in
    the caller — Layers 1-3 + Fence structural checks stay enforced.
    """
    rollback = str(surface.get("rollback_path") or "").strip()
    if not rollback:
        # Should have been caught by _layer_fence_validate's missing-
        # field check; defensive pass-through.
        return ("pass", "")
    verdict, detail = _smoke_test_rollback(rollback, cwd)
    if verdict == "valid":
        return ("pass", "")
    return (
        "reject",
        f"Layer 4 (Fence rollback smoke test): {detail}",
    )


def _layer4_generic_validate(
    surface: dict,
    blueprint_name: str,
) -> tuple[str, str]:
    """Layer 4 · CP6 — generic verification_trace validation.

    Called when the selected blueprint declares
    ``verification_trace_required: true`` AND does NOT map the trace
    to a blueprint-specific field (``verification_trace_maps_to`` is
    None — i.e. the generic blueprint at RC). Extracts the
    ``verification_trace`` object from the surface, validates against
    the RC field contract (``_verification_trace.validate_trace``),
    returns a reject when the trace is absent, shape-invalid, has no
    parseable slot, or carries a command without a strict
    threshold_observable.

    This is the closure path for the three spec fluent-vacuous examples
    that honestly passed Layers 2+3: they carry no verification_trace,
    so L4 rejects them with the "declare a commitment" message.
    """
    raw = surface.get("verification_trace")
    trace = _VerificationTrace.from_surface_field(raw)
    verdict, detail = _validate_trace(trace)
    if verdict == "valid":
        return ("pass", "")
    return (
        "reject",
        f"Layer 4 (blueprint `{blueprint_name}`): {detail}. High-impact "
        f"ops must declare a `verification_trace` object with a parseable "
        f"`command` (+ matching `threshold_observable`), `or_dashboard` "
        f"(http(s) URL), or `or_test` (pytest / unittest id) — the "
        f"kernel uses it at Layer 6 / CP7 to check whether the "
        f"disconfirmation actually fired.",
    )


def _surface_status(cwd: Path) -> tuple[str, str]:
    # Disambiguate "file absent" from "file present but malformed". The
    # two cases surface the same `_read_surface` return (None) but ask
    # the operator to take different actions — author vs. repair. Parse
    # inline here so the status detail can name the actual failure.
    p = cwd / ".episteme" / "reasoning-surface.json"
    if not p.exists():
        return "missing", "no .episteme/reasoning-surface.json found"
    try:
        surface = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return "invalid", (
            f"surface file exists but is not valid JSON "
            f"({exc.__class__.__name__} at line {exc.lineno}, col {exc.colno})"
        )
    except OSError as exc:
        return "invalid", f"surface file exists but could not be read ({exc.__class__.__name__})"
    if not isinstance(surface, dict):
        return "invalid", "surface file is valid JSON but not an object"
    age = _surface_age_seconds(surface)
    if age is None:
        return "invalid", "surface has no parseable timestamp"
    if age > SURFACE_TTL_SECONDS:
        mins = age // 60
        return "stale", f"surface is {mins} minute(s) old (TTL {SURFACE_TTL_SECONDS // 60} min)"
    missing = _surface_missing_fields(surface)
    if missing:
        detail = (
            f"surface fails validation on: {', '.join(missing)}. "
            f"Disconfirmation must be a concrete observable condition "
            f"(>= {_min_disconfirmation_len()} chars, not 'none'/'n/a'/'tbd'/'해당 없음'). "
            f"At least one unknown must be sharp and specific (>= {_min_unknown_len()} chars)."
        )
        return "incomplete", detail
    return "ok", ""


def _write_audit(tool: str, op: str, cwd: Path, status: str, action: str, mode: str) -> None:
    audit_path = Path.home() / ".episteme" / "audit.jsonl"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": tool,
        "op": op,
        "cwd": str(cwd),
        "status": status,
        "action": action,
        "mode": mode,
    }
    try:
        with open(audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass  # Audit failure must never block operations


def _correlation_id(payload: dict, cmd: str, ts: str) -> str:
    """Derive a correlation id tying a PreToolUse prediction to its PostToolUse outcome.

    Prefers the runtime-provided `tool_use_id`. Falls back to a SHA-1 over
    (ts-second, cwd, cmd) which will match between the two hook invocations
    on any sane hook runner that fires them within the same second for the
    same call.
    """
    rid = payload.get("tool_use_id") or payload.get("toolUseId") or payload.get("request_id")
    if isinstance(rid, str) and rid.strip():
        return rid.strip()
    cwd = str(payload.get("cwd") or os.getcwd())
    bucket = ts.split(".")[0]  # truncate to whole-second resolution
    seed = f"{bucket}|{cwd}|{cmd}".encode("utf-8", errors="replace")
    return "h_" + hashlib.sha1(seed).hexdigest()[:16]


def _extract_prediction(surface: dict | None) -> dict:
    """Extract the falsifiable claims of a Reasoning Surface for calibration.

    Records only the fields load-bearing for predicted-vs-observed audit:
    the core question, disconfirmation condition, unknowns, and hypothesis.
    """
    if not isinstance(surface, dict):
        return {}
    return {
        "core_question": str(surface.get("core_question") or "").strip(),
        "disconfirmation": str(surface.get("disconfirmation") or "").strip(),
        "unknowns": [str(u).strip() for u in (surface.get("unknowns") or []) if str(u).strip()],
        "hypothesis": str(surface.get("hypothesis") or "").strip(),
    }


def _redact(cmd: str) -> str:
    """Crude secret-redaction — command_executed must not carry tokens.

    Inlined (not imported from episodic_writer) because the hook is invoked
    as a standalone script with no guaranteed sys.path. If this pattern set
    diverges from episodic_writer._redact, unify by editing both.
    """
    if not cmd:
        return cmd
    patterns = [
        (re.compile(r"(?i)((?:password|passwd|token|secret|api[_-]?key|bearer))(\s*[=:]\s*)\S+"),
         r"\1\2<REDACTED>"),
        (re.compile(r"AKIA[0-9A-Z]{16}"), "<REDACTED-AWS-KEY>"),
        (re.compile(r"(?i)ghp_[a-z0-9]{30,}"), "<REDACTED-GH-TOKEN>"),
    ]
    redacted = cmd
    for pat, repl in patterns:
        redacted = pat.sub(repl, redacted)
    return redacted


def _telemetry_path(ts: str) -> Path:
    date = ts[:10]  # YYYY-MM-DD
    return Path.home() / ".episteme" / "telemetry" / f"{date}-audit.jsonl"


def _write_telemetry(record: dict) -> None:
    """Append a JSONL record to the day-scoped telemetry file. Never raises."""
    try:
        path = _telemetry_path(record["ts"])
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except (OSError, KeyError):
        pass  # Telemetry failure must never block operations


def _write_prediction(
    payload: dict,
    tool: str,
    op: str,
    cmd: str,
    cwd: Path,
    surface: dict | None,
) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    record = {
        "ts": ts,
        "event": "prediction",
        "correlation_id": _correlation_id(payload, cmd, ts),
        "tool": tool,
        "op": op,
        "cwd": str(cwd),
        "command_executed": _redact(cmd),
        "epistemic_prediction": _extract_prediction(surface),
        "exit_code": None,
    }
    _write_telemetry(record)


def _surface_template() -> str:
    return (
        "Write .episteme/reasoning-surface.json with:\n"
        "{\n"
        '  "timestamp": "<ISO-8601 UTC>",\n'
        '  "core_question": "<one question this work answers>",\n'
        '  "knowns": ["..."],\n'
        '  "unknowns": ["<sharp, >= 15 chars, not a placeholder>"],\n'
        '  "assumptions": ["..."],\n'
        '  "disconfirmation": "<concrete observable outcome, >= 15 chars>"\n'
        "}\n"
        "Lazy values (none, n/a, tbd, 해당 없음, 없음, ...) are rejected."
    )


def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    tool_name = _tool_name(payload)
    label = _match_high_impact(tool_name, payload)
    # CP5: the Fence Reconstruction selector admits constraint-removal
    # ops as high-impact even when the command word itself (`rm`,
    # `disable`, `delete`) is not in the generic HIGH_IMPACT_BASH
    # pattern set. This is how `rm .episteme/advisory-surface` and
    # `git rm kernel/FAILURE_MODES.md` reach the surface-validation
    # gate — Fence's compound AND (removal-verb ∧ constraint-path) is
    # the specificity gate that makes admitting the op FP-averse.
    if not label:
        try:
            if _detect_scenario(
                payload, surface_text=None, project_context={}
            ) == "fence_reconstruction":
                label = "fence:constraint-removal"
        except Exception:
            pass  # graceful degrade — non-Fence ops fall through
    if not label:
        return 0

    cwd = Path(payload.get("cwd") or os.getcwd())
    status, detail = _surface_status(cwd)
    advisory_only = (cwd / ".episteme" / "advisory-surface").exists()
    mode = "advisory" if advisory_only else "strict"

    # Layer 2 · v1.0 RC CP3 — runs only after Layer 1 passes. A Layer-2
    # rejection downgrades status from "ok" to "incomplete" so the
    # existing block path handles it; an absence-advisory emits a
    # stderr warning and leaves status at "ok".
    #
    # Layer 3 · v1.0 RC CP4 — runs only after Layer 2 leaves status at
    # "ok" (including the Layer-2-advisory case). Blueprint-aware entity
    # grounding: extracts snake_case / SCREAMING_CASE / path+ext / hex-SHA
    # tokens from the blueprint's declared grounded fields and verifies
    # they exist in the project working tree. FP-averse gate per spec
    # § Layer 3. Graceful degrade: any exception yields "pass" with a
    # one-line stderr fallback — Layers 1 & 2 stay enforced.
    if status == "ok":
        layer2_surface = _read_surface(cwd)
        if layer2_surface is not None:
            l2_verdict, l2_detail = _layer2_classify_blueprint_fields(
                layer2_surface, payload
            )
            if l2_verdict == "reject":
                status = "incomplete"
                detail = l2_detail
            elif l2_verdict == "advisory":
                sys.stderr.write(f"[episteme advisory] {l2_detail}\n")

            if status == "ok":
                blueprint_name = "generic"
                try:
                    blueprint_name = _detect_scenario(
                        payload, surface_text=None, project_context={}
                    ) or "generic"
                    l3_verdict, l3_detail = _layer3_ground_blueprint_fields(
                        layer2_surface, blueprint_name, cwd
                    )
                except Exception as exc:  # graceful degrade
                    sys.stderr.write(
                        f"[episteme] Layer 3 fallback: "
                        f"{exc.__class__.__name__}; Layers 1 & 2 still enforced.\n"
                    )
                    l3_verdict, l3_detail = ("pass", "")
                if l3_verdict == "reject":
                    status = "incomplete"
                    detail = l3_detail
                elif l3_verdict == "advisory":
                    sys.stderr.write(f"[episteme advisory] {l3_detail}\n")

                # Layer · Fence (CP5) — blueprint-specific validation
                # plus Pillar 3 pending-marker write on reversible
                # success. Runs only when the scenario detector chose
                # fence_reconstruction AND Layers 1-3 left status at
                # "ok". Graceful degrade: any unexpected exception in
                # fence machinery downgrades to a stderr fallback and
                # leaves Layers 1-3 as the ultimate enforcer.
                if status == "ok" and blueprint_name == "fence_reconstruction":
                    try:
                        fence_verdict, fence_detail = _layer_fence_validate(
                            layer2_surface
                        )
                    except Exception as exc:  # graceful degrade
                        sys.stderr.write(
                            f"[episteme] Fence fallback: "
                            f"{exc.__class__.__name__}; Layers 1-3 still "
                            f"enforced.\n"
                        )
                        fence_verdict, fence_detail = ("pass", "")
                    if fence_verdict == "reject":
                        status = "incomplete"
                        detail = fence_detail
                    elif fence_verdict == "advisory-irreversible":
                        sys.stderr.write(
                            f"[episteme advisory] {fence_detail}\n"
                        )
                        # Do NOT write synthesis marker on irreversible.
                    elif fence_verdict == "pass":
                        # Layer 4 · CP6 — Fence rollback_path smoke test.
                        # Spec § Blueprint B: verification is the
                        # rollback_path executed as a smoke test in a
                        # reversible context. At RC the smoke test is
                        # syntactic + path-existence + prod-marker
                        # absence; full sandboxed execution lands in
                        # v1.0.1.
                        try:
                            l4_verdict, l4_detail = _layer4_fence_smoke_test(
                                layer2_surface, cwd
                            )
                        except Exception as exc:  # graceful degrade
                            sys.stderr.write(
                                f"[episteme] Layer 4 (Fence smoke) "
                                f"fallback: {exc.__class__.__name__}; "
                                f"Layers 1-3 + Fence structural still "
                                f"enforced.\n"
                            )
                            l4_verdict, l4_detail = ("pass", "")
                        if l4_verdict == "reject":
                            status = "incomplete"
                            detail = l4_detail
                    if status == "ok" and fence_verdict == "pass":
                        # Reversible Fence admitted AND Layer 4 smoke
                        # test green — write Pillar 3 pending-synthesis
                        # marker for the PostToolUse finalizer to act on
                        # (exit_code == 0 → constraint-safety protocol
                        # written to ~/.episteme/framework/protocols.jsonl).
                        try:
                            cmd_for_marker = (
                                _bash_command(payload)
                                if tool_name == "Bash" else ""
                            )
                            correlation = _fence_synthesis.correlation_id(
                                payload,
                                cmd_for_marker,
                                datetime.now(timezone.utc).isoformat(),
                            )
                            _fence_synthesis.write_pending_marker(
                                layer2_surface,
                                correlation,
                                cwd,
                                cmd_for_marker,
                            )
                        except Exception:
                            # Synthesis bookkeeping failure must never
                            # block the admitted op. Layers 1-3 +
                            # Fence + L4 have already validated;
                            # synthesis is advisory-in-aggregate.
                            pass

                # Layer 4 · CP6 — generic verification_trace. Runs when
                # the blueprint declares verification_trace_required:
                # true AND does NOT map the trace to a field (Fence is
                # already handled in-line above). At RC this applies to
                # the generic blueprint — closing the three fluent-
                # vacuous examples from spec § "Why this exists" that
                # honestly passed Layers 2+3.
                if status == "ok" and blueprint_name != "fence_reconstruction":
                    try:
                        _bp = _load_registry().get(blueprint_name)
                        _needs_trace = (
                            _bp.verification_trace_required
                            and _bp.verification_trace_maps_to is None
                        )
                    except (_BlueprintParseError, _BlueprintValidationError,
                            KeyError, OSError):
                        _bp = None
                        _needs_trace = False
                    if _needs_trace:
                        try:
                            l4g_verdict, l4g_detail = _layer4_generic_validate(
                                layer2_surface, blueprint_name
                            )
                        except Exception as exc:  # graceful degrade
                            sys.stderr.write(
                                f"[episteme] Layer 4 generic fallback: "
                                f"{exc.__class__.__name__}; Layers 1-3 "
                                f"still enforced.\n"
                            )
                            l4g_verdict, l4g_detail = ("pass", "")
                        if l4g_verdict == "reject":
                            status = "incomplete"
                            detail = l4g_detail

    if status == "ok":
        _write_audit(tool_name, label, cwd, status, "passed", mode)
        # Calibration telemetry: record the prediction so a PostToolUse hook
        # can pair it with the observed exit_code. Only fires for Bash, since
        # only Bash calls have a meaningful "outcome" against a prediction.
        if tool_name == "Bash":
            cmd = _bash_command(payload)
            surface = _read_surface(cwd)
            _write_prediction(payload, tool_name, label, cmd, cwd, surface)
        return 0

    header = f"REASONING SURFACE {status.upper()}: high-impact op `{label}` with {detail}."
    instruction = _surface_template()

    if not advisory_only:
        _write_audit(tool_name, label, cwd, status, "blocked", mode)
        sys.stderr.write(
            "Execution blocked by Episteme Strict Mode. "
            "Missing or invalid Reasoning Surface.\n"
            f"{header}\n{instruction}\n"
            "Opt out per-project (not recommended): "
            "`touch .episteme/advisory-surface`.\n"
        )
        return 2

    _write_audit(tool_name, label, cwd, status, "advisory", mode)
    advisory = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                f"{header} Advisory mode is active (.episteme/advisory-surface present). "
                f"Declare a Reasoning Surface before proceeding. {instruction}"
            ),
        }
    }
    sys.stdout.write(json.dumps(advisory))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
