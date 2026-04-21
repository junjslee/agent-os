"""Fence Reconstruction synthesis — v1.0 RC CP5.

Owns the PreToolUse -> PostToolUse handoff that turns a successfully
admitted constraint-removal op into a durable constraint-safety
protocol in the Pillar 3 framework.

## Lifecycle

1. **PreToolUse** — `reasoning_surface_guard.py` detects that the
   scenario is `fence_reconstruction`, all five Fence required fields
   are present, Layer 2 fire-classifies `removal_consequence_prediction`,
   Layer 3 grounds `constraint_identified` to a real project file,
   `origin_evidence` classifies as `evidence`, and
   `reversibility_classification == "reversible"`. On that success the
   guard calls `write_pending_marker(...)` to record the Fence surface
   and correlation id in `~/.episteme/state/fence_pending/<id>.json`.

2. **PostToolUse** — `fence_synthesis.py` reads the matching marker
   by correlation id. If `exit_code == 0`, it appends a protocol entry
   to `~/.episteme/framework/protocols.jsonl` with
   `format_version: "cp5-pre-chain"` and null `prev_hash` / `entry_hash`
   (CP7 retroactively chains). Either way, the pending marker file is
   deleted.

The marker file is per-correlation-id rather than a shared JSONL (the
user-approved design decision) so concurrent Bash calls in the same
session never collide. `fcntl.flock` discipline is NOT required.

## Forward-compatibility with CP7

Every protocol entry carries `format_version: "cp5-pre-chain"` and null
chain fields. CP7's `_chain.py` walks the file, retroactively computes
`prev_hash` / `entry_hash` per entry, and bumps `format_version` to
`"cp7-chained"`. CP9's framework query treats both versions as valid
until a post-RC cleanup retires the pre-chain format.

Spec: `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § Blueprint B and
§ Pillar 3 · Framework Synthesis & Active Guidance.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths + constants
# ---------------------------------------------------------------------------

def _episteme_home() -> Path:
    return Path(os.environ.get("EPISTEME_HOME") or (Path.home() / ".episteme"))


def _pending_dir() -> Path:
    return _episteme_home() / "state" / "fence_pending"


def _framework_path() -> Path:
    return _episteme_home() / "framework" / "protocols.jsonl"


CP5_FORMAT_VERSION = "cp5-pre-chain"
MARKER_TTL_SECONDS = 24 * 60 * 60


# ---------------------------------------------------------------------------
# Secret redaction — inlined for hook self-containment (same discipline
# calibration_telemetry.py uses; see note there).
# ---------------------------------------------------------------------------

_REDACT_PATTERNS: tuple[tuple[re.Pattern, str], ...] = (
    (re.compile(r"(?i)((?:password|passwd|token|secret|api[_-]?key|bearer))(\s*[=:]\s*)\S+"),
     r"\1\2<REDACTED>"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "<REDACTED-AWS-KEY>"),
    (re.compile(r"(?i)ghp_[a-z0-9]{30,}"), "<REDACTED-GH-TOKEN>"),
)


def _redact(text: str) -> str:
    if not text:
        return text
    out = text
    for pat, repl in _REDACT_PATTERNS:
        out = pat.sub(repl, out)
    return out


# ---------------------------------------------------------------------------
# Correlation id — must match reasoning_surface_guard.py / calibration_telemetry.py
# ---------------------------------------------------------------------------

def correlation_id(payload: dict, cmd: str, ts: str) -> str:
    """Derive the correlation id used to pair Pre/Post ToolUse events.

    Priority: `tool_use_id` / `toolUseId` / `request_id` from the
    payload; fallback to a stable SHA-1 over (second-bucket, cwd, cmd)
    so the two hooks produce the same id for the same call.
    """
    rid = (
        payload.get("tool_use_id")
        or payload.get("toolUseId")
        or payload.get("request_id")
    )
    if isinstance(rid, str) and rid.strip():
        return rid.strip()
    cwd = str(payload.get("cwd") or os.getcwd())
    bucket = ts.split(".")[0]
    seed = f"{bucket}|{cwd}|{cmd}".encode("utf-8", errors="replace")
    return "h_" + hashlib.sha1(seed).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Context signature — CP5 minimal inline computation
#
# The canonical version lives in CP7's `_context_signature.py` and
# folds in project fingerprint + operator profile axes + op class +
# environment. CP5 ships a short reproducible hash over a narrower
# tuple so synthesis can land before CP7 without foreclosing the
# canonical shape.
# ---------------------------------------------------------------------------

def _context_signature(cwd: Path, constraint_identified: str) -> str:
    project = cwd.resolve().name or "unknown_project"
    # Strip the constraint identifier to a short path-like token.
    token = constraint_identified.strip().splitlines()[0][:200]
    seed = f"{project}|fence_reconstruction|{token}".encode(
        "utf-8", errors="replace"
    )
    return "cs_" + hashlib.sha256(seed).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Pending marker (PreToolUse write)
# ---------------------------------------------------------------------------

def _atomic_write_json(path: Path, data: dict) -> None:
    """Write `data` as JSON to `path` atomically via tempfile + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=path.name + ".tmp-", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_pending_marker(
    surface: dict,
    correlation: str,
    cwd: Path,
    cmd: str,
) -> Path | None:
    """Persist the Fence-admitted surface so PostToolUse can finalize.

    Returns the marker path on success, None on graceful-degrade
    failure. Never raises — the PreToolUse path must not break on
    synthesis bookkeeping failure.
    """
    try:
        marker = {
            "version": 1,
            "correlation_id": correlation,
            "written_at": datetime.now(timezone.utc).isoformat(),
            "cwd": str(cwd),
            "command_redacted": _redact(cmd),
            "surface": {
                "constraint_identified": str(surface.get("constraint_identified", "")),
                "origin_evidence": str(surface.get("origin_evidence", "")),
                "removal_consequence_prediction": str(surface.get("removal_consequence_prediction", "")),
                "reversibility_classification": str(surface.get("reversibility_classification", "")),
                "rollback_path": str(surface.get("rollback_path", "")),
            },
        }
        path = _pending_dir() / f"{correlation}.json"
        _atomic_write_json(path, marker)
        return path
    except OSError:
        return None


def read_pending_marker(correlation: str) -> dict | None:
    """Read a pending marker by correlation id. Returns None on
    absence / parse error / TTL expiry. Does NOT delete."""
    path = _pending_dir() / f"{correlation}.json"
    if not path.is_file():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    # TTL check — treat very stale markers as absent.
    written = data.get("written_at")
    if isinstance(written, str):
        try:
            age = (
                datetime.now(timezone.utc)
                - datetime.fromisoformat(written.replace("Z", "+00:00"))
            ).total_seconds()
            if age > MARKER_TTL_SECONDS:
                return None
        except ValueError:
            pass
    return data


def delete_pending_marker(correlation: str) -> None:
    """Remove the pending marker. Silent on missing / unlink errors."""
    path = _pending_dir() / f"{correlation}.json"
    try:
        path.unlink()
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Synthesis protocol (PostToolUse write)
# ---------------------------------------------------------------------------

def _build_protocol(marker: dict, exit_code: int | None) -> dict:
    """Construct the protocol entry from a pending marker + exit_code."""
    surface = marker.get("surface", {}) if isinstance(marker.get("surface"), dict) else {}
    constraint = str(surface.get("constraint_identified", ""))
    origin = str(surface.get("origin_evidence", ""))
    consequence = str(surface.get("removal_consequence_prediction", ""))
    rollback = str(surface.get("rollback_path", ""))
    cwd = Path(marker.get("cwd") or "")
    context_sig = _context_signature(cwd, constraint)
    protocol_text = (
        f"In context `{cwd.resolve().name or 'unknown_project'}::"
        f"fence_reconstruction::{_short(constraint)}`, "
        f"removing `{_short(constraint)}` was safe because "
        f"`{_short(origin)}` established that `{_short(consequence)}` did "
        f"not materialize. Rollback path `{_short(rollback)}` remained "
        f"available and was not triggered."
    )
    return {
        "version": 1,
        "format_version": CP5_FORMAT_VERSION,
        "blueprint": "fence_reconstruction",
        "synthesized_at": datetime.now(timezone.utc).isoformat(),
        "correlation_id": marker.get("correlation_id", ""),
        "context_signature": context_sig,
        "guidance_trigger": context_sig,  # CP9 may refine
        "synthesized_protocol": protocol_text,
        "source_fields": {
            "constraint_identified": constraint,
            "origin_evidence": origin,
            "removal_consequence_prediction": consequence,
            "reversibility_classification": str(
                surface.get("reversibility_classification", "")
            ),
            "rollback_path": rollback,
        },
        "op_outcome": {
            "exit_code": exit_code,
            "cwd": str(marker.get("cwd", "")),
            "command_redacted": marker.get("command_redacted", ""),
        },
        "chain": {
            "prev_hash": None,
            "entry_hash": None,
        },
    }


def _short(text: str, limit: int = 160) -> str:
    """Collapse to a single-line excerpt for the protocol template."""
    if not text:
        return ""
    flat = " ".join(text.split())
    if len(flat) > limit:
        return flat[: limit - 1] + "…"
    return flat


def _append_protocol(path: Path, protocol: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(protocol, ensure_ascii=False) + "\n")


def finalize_on_success(correlation: str, exit_code: int | None) -> dict | None:
    """Read the pending marker, if exit_code == 0 append a protocol
    entry to the framework, and delete the marker in all cases.

    Returns the written protocol dict (for tests / observability) or
    None when no synthesis was produced (marker absent, exit_code != 0,
    or IO error).
    """
    marker = read_pending_marker(correlation)
    if marker is None:
        return None
    try:
        if exit_code == 0:
            protocol = _build_protocol(marker, exit_code)
            _append_protocol(_framework_path(), protocol)
            return protocol
        return None
    except OSError:
        return None
    finally:
        delete_pending_marker(correlation)


# ---------------------------------------------------------------------------
# Test helpers — not part of the public API surface.
# ---------------------------------------------------------------------------

def _reset_paths_for_tests(episteme_home: Path) -> None:
    """Point all module paths at a test-local episteme_home. Tests are
    expected to set EPISTEME_HOME via os.environ directly; this helper
    exists for the subset that cannot use env patching."""
    os.environ["EPISTEME_HOME"] = str(episteme_home)


def pending_dir_for_tests() -> Path:
    return _pending_dir()


def framework_path_for_tests() -> Path:
    return _framework_path()


def build_protocol_for_tests(marker: dict, exit_code: int | None) -> dict:
    return _build_protocol(marker, exit_code)


def _extract_payload_values_for_tests(payload: dict) -> tuple[str, str]:
    """Expose the payload-normalization helpers used by the PostToolUse
    hook — mirrors calibration_telemetry's shape for test parity."""
    cmd = ""
    ti = payload.get("tool_input") or payload.get("toolInput") or {}
    if isinstance(ti, dict):
        cmd = str(ti.get("command") or ti.get("cmd") or "")
    return cmd, str(payload.get("cwd") or os.getcwd())
