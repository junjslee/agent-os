#!/usr/bin/env python3
"""PostToolUse hook: diff watched files + emit Arm A trajectory entries.

Cognitive Arm A auto-instrumentation (Event 91, CP-TEMPORAL-INTEGRITY-
EXPANSION-01 follow-up). Pairs with `_arm_a_pre.py` via correlation_id.

Flow:
  1. Read marker from `~/.episteme/state/arm_a_pending/<cid>.json`.
  2. Read post-edit file content.
  3. Diff:
     - profile (operator_profile.md): parse axis blocks → diff per
       (axis_name, field) → call `_profile_history.record_change` per
       changed axis.
     - policy (cognitive_profile / workflow_policy / agent_feedback.md):
       split by H2 sections → diff body content → call
       `_policy_history.record_change` per changed section.
  4. Delete marker (regardless of write outcome).

Never blocks. Auto-recorded entries get `auto_recorded: true` payload
flag so future audits can filter manual vs automated trajectory data.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Hook self-path resolution
_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

# src/episteme — for _profile_history / _policy_history imports
_REPO_ROOT = _HOOKS_DIR.parent.parent
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


# ---------------------------------------------------------------------------
# Marker path + lifecycle (mirrors fence_synthesis)
# ---------------------------------------------------------------------------


def _pending_dir() -> Path:
    return Path.home() / ".episteme" / "state" / "arm_a_pending"


MARKER_TTL_SECONDS = 3600


def _read_marker(correlation: str) -> dict | None:
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


def _delete_marker(correlation: str) -> None:
    try:
        (_pending_dir() / f"{correlation}.json").unlink()
    except OSError:
        pass


def _candidate_correlation_ids(payload: dict, file_path: str) -> list[str]:
    """Same Event 50 pattern: PreToolUse may lack tool_use_id; we try
    multiple candidates on read."""
    out: list[str] = []
    seen: set[str] = set()
    rid = (
        payload.get("tool_use_id")
        or payload.get("toolUseId")
        or payload.get("request_id")
    )
    if isinstance(rid, str) and rid.strip():
        c = rid.strip()
        out.append(c)
        seen.add(c)
    # Try the SHA-1 fallback at second-bucket (matches Pre's ts).
    # Both ±1 second since Pre and Post may straddle a second boundary.
    now_iso = datetime.now(timezone.utc).isoformat()
    bucket = now_iso.split(".")[0]
    for offset in (0, -1, 1):
        try:
            base_ts = datetime.fromisoformat(bucket.replace("Z", "+00:00"))
            from datetime import timedelta
            ts = (base_ts + timedelta(seconds=offset)).isoformat()
            seed = f"{ts.split('.')[0]}|{file_path}".encode("utf-8", errors="replace")
            h = "h_" + hashlib.sha1(seed).hexdigest()[:16]
            if h not in seen:
                out.append(h)
                seen.add(h)
        except (ValueError, OSError):
            continue
    return out


# ---------------------------------------------------------------------------
# Payload helpers
# ---------------------------------------------------------------------------


def _tool_name(payload: dict) -> str:
    return str(payload.get("tool_name") or payload.get("toolName") or "").strip()


def _tool_input(payload: dict) -> dict:
    raw = payload.get("tool_input") or payload.get("toolInput") or {}
    return raw if isinstance(raw, dict) else {}


def _file_path_from_payload(payload: dict) -> str | None:
    ti = _tool_input(payload)
    fp = ti.get("file_path") or ti.get("filePath") or ti.get("path")
    if isinstance(fp, str) and fp.strip():
        return fp.strip()
    return None


# ---------------------------------------------------------------------------
# Profile axis parser — operator_profile.md
# ---------------------------------------------------------------------------


# Top-level axis-name keys: lowercase + underscore + colon at line start
# inside YAML code fences. Exclude indented sub-fields by requiring no
# leading whitespace.
_AXIS_NAME_RE = re.compile(r"^([a-z_][a-z0-9_]*):\s*$")
# Axis sub-field: 2-space indent, key, colon, value
_AXIS_FIELD_RE = re.compile(r"^  ([a-z_][a-z0-9_]*):\s*(.*?)\s*$")


# Mirrors VALID_AXIS_NAMES in _profile_history.py — kept inline so this
# hook has no sibling-import dependency at runtime.
_VALID_AXES = frozenset({
    "planning_strictness", "risk_tolerance", "testing_rigor",
    "parallelism_preference", "documentation_rigor", "automation_level",
    "dominant_lens", "noise_signature", "abstraction_entry",
    "decision_cadence", "explanation_depth", "feedback_mode",
    "uncertainty_tolerance", "asymmetry_posture", "fence_discipline",
    "expertise_map",
})

# Fields whose changes are worth recording (skip "note" — prose-heavy,
# generates noise, change-detected via H2-section hash).
_TRACKED_AXIS_FIELDS = ("value", "confidence", "last_observed", "evidence_refs")


def _parse_profile_axes(text: str) -> dict[str, dict[str, str]]:
    """Parse axis blocks from operator_profile.md content.

    Returns ``{axis_name: {field_name: value_str, ...}}``. Only tracks
    fields in _TRACKED_AXIS_FIELDS. Multi-line note fields are ignored.
    """
    out: dict[str, dict[str, str]] = {}
    in_fence = False
    current_axis: str | None = None

    for raw_line in text.splitlines():
        # Code fence toggle (``` lines)
        if raw_line.strip().startswith("```"):
            in_fence = not in_fence
            current_axis = None
            continue
        if not in_fence:
            current_axis = None
            continue
        # Blank line resets current axis
        if not raw_line.strip():
            current_axis = None
            continue
        # Top-level axis name (no leading whitespace, ends with `:`)
        m = _AXIS_NAME_RE.match(raw_line)
        if m and not raw_line.startswith(" "):
            name = m.group(1)
            if name in _VALID_AXES:
                current_axis = name
                out.setdefault(name, {})
            else:
                current_axis = None
            continue
        # Sub-field (2-space indent)
        if current_axis is not None:
            mf = _AXIS_FIELD_RE.match(raw_line)
            if mf:
                field, value = mf.group(1), mf.group(2)
                if field in _TRACKED_AXIS_FIELDS:
                    out[current_axis][field] = value
    return out


def _diff_profile(pre_text: str, post_text: str) -> list[tuple[str, str, str, str]]:
    """Return list of (axis_name, field, old_value, new_value) for every
    tracked-field change between pre and post operator_profile.md content.

    Treats axis_field absence as ``"(absent)"`` so adding/removing fields
    is also captured."""
    pre = _parse_profile_axes(pre_text)
    post = _parse_profile_axes(post_text)
    deltas: list[tuple[str, str, str, str]] = []
    all_axes = set(pre.keys()) | set(post.keys())
    for axis in sorted(all_axes):
        pre_fields = pre.get(axis, {})
        post_fields = post.get(axis, {})
        for field in _TRACKED_AXIS_FIELDS:
            old = pre_fields.get(field, "(absent)")
            new = post_fields.get(field, "(absent)")
            if old != new:
                deltas.append((axis, field, old, new))
    return deltas


# ---------------------------------------------------------------------------
# Policy section parser — H2-delimited
# ---------------------------------------------------------------------------


_H2_RE = re.compile(r"^##\s+(.+?)\s*$")


def _parse_policy_sections(text: str) -> dict[str, str]:
    """Split markdown by H2 (`## `) headings. Returns
    ``{section_title: body_content}``. Content before the first H2 is
    keyed under ``"(preamble)"``. Trailing whitespace on body trimmed."""
    out: dict[str, str] = {}
    current_title = "(preamble)"
    current_body: list[str] = []
    for line in text.splitlines():
        m = _H2_RE.match(line)
        if m:
            out[current_title] = "\n".join(current_body).rstrip()
            current_title = m.group(1).strip()
            current_body = []
        else:
            current_body.append(line)
    out[current_title] = "\n".join(current_body).rstrip()
    return out


def _diff_policy(pre_text: str, post_text: str) -> list[tuple[str, str, str]]:
    """Return list of (section_title, old_body, new_body) for every
    changed H2 section. Drops `(preamble)` if unchanged; includes it
    when changed."""
    pre = _parse_policy_sections(pre_text)
    post = _parse_policy_sections(post_text)
    deltas: list[tuple[str, str, str]] = []
    all_sections = set(pre.keys()) | set(post.keys())
    for section in sorted(all_sections):
        old = pre.get(section, "")
        new = post.get(section, "")
        if old != new:
            deltas.append((section, old, new))
    return deltas


# ---------------------------------------------------------------------------
# Hook log
# ---------------------------------------------------------------------------


def _log_line(msg: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    line = f"{ts} arm_a_post {msg}\n"
    try:
        path = Path.home() / ".episteme" / "state" / "hooks.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        try:
            sys.stderr.write(line)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            return 0
        payload = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        return 0

    try:
        tool = _tool_name(payload)
        if tool not in ("Write", "Edit", "MultiEdit"):
            return 0
        file_path = _file_path_from_payload(payload)
        if not file_path:
            return 0

        # Find marker via candidate correlation ids (Event 50 pattern).
        candidates = _candidate_correlation_ids(payload, file_path)
        marker = None
        for cid in candidates:
            m = _read_marker(cid)
            if m is not None:
                marker = m
                break
        if marker is None:
            # No marker found → file isn't watched OR pre hook didn't
            # snapshot OR Pre/Post correlation drift exceeded ±1s.
            return 0

        file_kind = marker.get("file_kind")
        pre_content = marker.get("pre_content", "") or ""

        # Read post-edit content. Missing file = empty (deletion edge).
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                post_content = f.read()
        except (OSError, UnicodeDecodeError):
            post_content = ""

        # Short-circuit if no actual content change
        if pre_content == post_content:
            _log_line(f"no-op: file={Path(file_path).name} pre==post")
            for cid in candidates:
                _delete_marker(cid)
            return 0

        if file_kind == "profile":
            from episteme import _profile_history as ph_mod  # type: ignore  # pyright: ignore[reportAttributeAccessIssue]
            deltas = _diff_profile(pre_content, post_content)
            written = 0
            for axis, field, old, new in deltas:
                # Only `value` / `confidence` are first-class trajectory
                # markers per OPERATOR_PROFILE_SCHEMA.md. Other tracked
                # fields ride along in old/new value strings (encoded
                # as `"<field>=<value>"`) so the trajectory stream
                # captures the meaningful per-axis snapshot.
                old_repr = f"{field}={old}"
                new_repr = f"{field}={new}"
                reason = (
                    f"auto-instrumented: {axis}.{field} changed via "
                    f"post-edit hook on operator_profile.md"
                )
                try:
                    ph_mod.record_change(
                        axis,
                        old_repr,
                        new_repr,
                        reason,
                        auto_recorded=True,
                    )
                    written += 1
                except ValueError as exc:
                    _log_line(f"profile validation skip: {axis}.{field} — {exc}")
                except Exception as exc:
                    _log_line(f"profile EXCEPTION: {axis}.{field} — {exc}")
            _log_line(
                f"profile: deltas={len(deltas)} written={written} "
                f"file={Path(file_path).name}"
            )
        elif file_kind == "policy":
            from episteme import _policy_history as polh_mod  # type: ignore  # pyright: ignore[reportAttributeAccessIssue]
            policy_basename = marker.get("policy_basename")
            if not isinstance(policy_basename, str) or not policy_basename:
                _log_line(f"policy: missing basename in marker; skip")
            else:
                deltas = _diff_policy(pre_content, post_content)
                written = 0
                for section, old_body, new_body in deltas:
                    reason = (
                        f"auto-instrumented: {section!r} updated via "
                        f"post-edit hook on {policy_basename}.md"
                    )
                    try:
                        polh_mod.record_change(
                            policy_basename,
                            section,
                            old_body,
                            new_body,
                            reason,
                            auto_recorded=True,
                        )
                        written += 1
                    except ValueError as exc:
                        _log_line(
                            f"policy validation skip: "
                            f"{policy_basename}:{section!r} — {exc}"
                        )
                    except Exception as exc:
                        _log_line(
                            f"policy EXCEPTION: "
                            f"{policy_basename}:{section!r} — {exc}"
                        )
                _log_line(
                    f"policy: deltas={len(deltas)} written={written} "
                    f"file={policy_basename}.md"
                )

        # Cleanup all candidates so stale siblings don't pile up
        for cid in candidates:
            _delete_marker(cid)
    except Exception as exc:  # pragma: no cover — defensive
        _log_line(f"EXCEPTION: {type(exc).__name__}: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
