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


SURFACE_TTL_SECONDS = 30 * 60  # 30 minutes

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


def _surface_status(cwd: Path) -> tuple[str, str]:
    surface = _read_surface(cwd)
    if surface is None:
        return "missing", "no .episteme/reasoning-surface.json found"
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
        "command_executed": cmd,
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
    if not label:
        return 0

    cwd = Path(payload.get("cwd") or os.getcwd())
    status, detail = _surface_status(cwd)
    advisory_only = (cwd / ".episteme" / "advisory-surface").exists()
    mode = "advisory" if advisory_only else "strict"

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
