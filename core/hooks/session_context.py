#!/usr/bin/env python3
"""SessionStart hook — prints git status, NEXT_STEPS, and Reasoning Surface state.

Output appears at session open so Claude and the operator share the same
starting context without a manual paste.
"""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


SURFACE_TTL_SECONDS = 30 * 60


def _spot_check_line() -> str | None:
    """Return a one-line digest of pending Layer 8 spot-check entries,
    or None when the queue is empty / unreadable.

    Inlined pattern consistent with ``_profile_audit_line`` — the hook
    is a standalone script with no guaranteed sys.path. Graceful
    degrade on any IO / import failure so SessionStart never blocks
    on a degraded queue."""
    _hooks_dir = Path(__file__).resolve().parent
    if str(_hooks_dir) not in sys.path:
        sys.path.insert(0, str(_hooks_dir))
    try:
        import _spot_check  # type: ignore  # pyright: ignore[reportMissingImports]
        pending = _spot_check.count_pending()
    except Exception:
        return None
    if pending <= 0:
        return None
    noun = "surface" if pending == 1 else "surfaces"
    return (
        f"{pending} {noun} flagged for review — run `episteme review`"
    )


def _last_session_path() -> Path:
    import os
    home = os.environ.get("EPISTEME_HOME") or str(Path.home() / ".episteme")
    return Path(home) / "state" / "last_session.json"


def _read_last_session_ts() -> str | None:
    """Return the recorded last-session ts, or None on first run."""
    path = _last_session_path()
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    ts = data.get("last_session_ts") if isinstance(data, dict) else None
    return ts if isinstance(ts, str) and ts else None


def _write_last_session_ts(ts: str) -> None:
    """Best-effort write. Silent on IO failure — the digest line is
    advisory, not load-bearing."""
    path = _last_session_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"last_session_ts": ts}, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError:
        pass


def _noise_watch_line() -> str | None:
    """Phase A · v1.0.1 — surface `noise_watch_set` derived knob at SessionStart.

    Reads the operator's declared noise susceptibilities (e.g.
    status-pressure / false-urgency / regret / social-scripts) from
    `~/.episteme/derived_knobs.json` so the operator opens the session
    already oriented against the dominant failure modes they have
    previously flagged. Advisory-only — never blocks session open.

    Silent when the knobs file is absent, malformed, or the knob is not
    set. Graceful degrade on any import / IO failure: the SessionStart
    banner remains useful even when one producer returns None.

    Kernel anchor: `kernel/OPERATOR_PROFILE_SCHEMA.md` § 5 names
    `noise_watch_set` as a declared derived knob; Event 25 narrative
    names the consumption gap this producer closes.
    """
    _hooks_dir = Path(__file__).resolve().parent
    if str(_hooks_dir) not in sys.path:
        sys.path.insert(0, str(_hooks_dir))
    try:
        import _derived_knobs  # type: ignore  # pyright: ignore[reportMissingImports]
        watch = _derived_knobs.load_knob("noise_watch_set", None)
    except Exception:
        return None
    if not isinstance(watch, list) or not watch:
        return None
    names = [str(x) for x in watch if isinstance(x, str) and x]
    if not names:
        return None
    return f"noise watch: {', '.join(names)}"


def _framework_digest_line() -> str | None:
    """CP9 · 'N protocols synthesized since last session (T total),
    M deferred discoveries pending'. Silent when both counts are zero.

    'Since last session' reads from ``~/.episteme/state/last_session.json``;
    main() updates that file at the end of this hook."""
    _hooks_dir = Path(__file__).resolve().parent
    if str(_hooks_dir) not in sys.path:
        sys.path.insert(0, str(_hooks_dir))
    try:
        import _framework  # type: ignore  # pyright: ignore[reportMissingImports]
        # Event 84 — pass include_superseded=True so the digest counts
        # ALL synthesis events (including superseded ones). The digest
        # is a "what changed since last session" metric, not a "what's
        # currently active" view; superseded entries still count as
        # synthesis activity worth reporting.
        all_protocols = _framework.list_protocols(include_superseded=True)
        deferred = _framework.list_deferred_discoveries(status="pending")
    except Exception:
        return None
    total = len(all_protocols)
    pending_deferred = len(deferred)
    last_ts = _read_last_session_ts()
    if last_ts is None:
        # First session — everything is "new" by definition.
        since_last = total
    else:
        since_last = sum(
            1 for env in all_protocols
            if isinstance(env, dict) and str(env.get("ts") or "") > last_ts
        )
    if total == 0 and pending_deferred == 0:
        return None
    protocol_noun = "protocol" if since_last == 1 else "protocols"
    deferred_noun = "discovery" if pending_deferred == 1 else "discoveries"
    return (
        f"framework: {since_last} {protocol_noun} synthesized since "
        f"last session ({total} total), {pending_deferred} deferred "
        f"{deferred_noun} pending"
    )


def run(args: list[str]) -> str:
    r = subprocess.run(args, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def _is_acked_in_store(run_id: str) -> bool:
    """Inline ack-store check (CP-AUDIT-ACK-01 / Event 78). Walks
    ~/.episteme/state/profile_audit_acks.jsonl in order; latest-state-
    per-audit_id wins. Returns True iff the latest entry for ``run_id``
    is a `profile_audit_ack` (and not subsequently revoked).

    Inlined rather than importing src/episteme/_profile_audit_ack.py —
    same pattern as _profile_audit_line below: hooks run as standalone
    scripts with no guaranteed sys.path of src/episteme/.
    """
    path = Path.home() / ".episteme" / "state" / "profile_audit_acks.jsonl"
    if not path.exists():
        return False
    state: str | None = None
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                try:
                    rec = json.loads(s)
                except json.JSONDecodeError:
                    continue
                if not isinstance(rec, dict):
                    continue
                payload = rec.get("payload", {})
                if not isinstance(payload, dict):
                    continue
                if payload.get("audit_id") != run_id:
                    continue
                etype = payload.get("type")
                if etype == "profile_audit_ack":
                    state = "ack"
                elif etype == "profile_audit_ack_revoke":
                    state = "revoke"
    except OSError:
        return False
    return state == "ack"


def _profile_audit_line() -> str | None:
    """Return a re-elicitation prompt string from the latest unacknowledged
    profile-audit record, or None when nothing to surface.

    Phase 12 · D3 · re-elicitation not correction. This function only
    reads ~/.episteme/memory/reflective/profile_audit.jsonl; it never
    mutates the operator profile. Operator acks via
    `episteme profile audit ack <run_id>` (lands in a later checkpoint).

    Inlined rather than imported from src/episteme/_profile_audit.py —
    the session_context hook is invoked as a standalone script by the
    host runtime with no guaranteed sys.path setup. Matches the
    "hooks stay self-contained" convention used by reasoning_surface_guard.py
    and calibration_telemetry.py.
    """
    path = Path.home() / ".episteme" / "memory" / "reflective" / "profile_audit.jsonl"
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
        record = json.loads(last)
    except json.JSONDecodeError:
        return None
    if not isinstance(record, dict):
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
    # CP-AUDIT-ACK-01 / Event 78: also suppress if the run_id is acked
    # in the ack-store at ~/.episteme/state/profile_audit_acks.jsonl.
    # Inlined per the hooks-stay-self-contained convention — no
    # sys.path setup required.
    if _is_acked_in_store(run_id):
        return None
    if len(drifts) == 1:
        a = drifts[0]
        return (
            f"profile-audit: drift on {a.get('axis_name', '?')} — "
            f"{a.get('reason', 'see audit record')} "
            f"Re-elicit or ack via `episteme profile audit ack {run_id}`."
        )
    if len(drifts) <= 3:
        names = ", ".join(a.get("axis_name", "?") for a in drifts)
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


def _canonical_project_root(cwd: Path) -> Path:
    """Resolve project root via git toplevel with walk fallback. Mirrors
    reasoning_surface_guard._canonical_project_root — duplicated for hook
    isolation. Path-A Event 42 fix."""
    import subprocess
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=2,
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
        pass
    probe = cwd.resolve() if cwd.exists() else cwd
    for _ in range(8):
        if (probe / ".episteme").is_dir():
            return probe
        if probe.parent == probe:
            break
        probe = probe.parent
    return cwd


def _surface_line() -> str | None:
    path = _canonical_project_root(Path.cwd()) / ".episteme" / "reasoning-surface.json"
    if not path.exists():
        return "surface: none declared — write .episteme/reasoning-surface.json before high-impact ops"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return "surface: unreadable .episteme/reasoning-surface.json"

    ts = data.get("timestamp")
    age: int | None = None
    if isinstance(ts, (int, float)):
        age = int(time.time() - float(ts))
    elif isinstance(ts, str) and ts:
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age = int(time.time() - dt.timestamp())
        except ValueError:
            age = None

    core_q = str(data.get("core_question") or "").strip() or "(none)"
    if age is None:
        return f"surface: present, no timestamp — core_question: {core_q}"
    if age > SURFACE_TTL_SECONDS:
        mins = age // 60
        return f"surface: STALE ({mins} min old) — refresh before high-impact ops"
    return f"surface: fresh — core_question: {core_q}"


def main() -> int:
    lines: list[str] = []

    # Git context
    if run(["git", "rev-parse", "--is-inside-work-tree"]):
        branch = run(["git", "branch", "--show-current"]) or "detached HEAD"
        status = run(["git", "status", "--short"])
        log = run(["git", "log", "--oneline", "-5"])

        lines.append(f"branch : {branch}")
        if status:
            lines.append(f"changes:\n{status}")
        else:
            lines.append("tree   : clean")
        if log:
            lines.append(f"log    :\n{log}")

    # HARNESS.md if present — tells the agent its operating constraints
    harness = Path("HARNESS.md")
    if harness.exists():
        h_content = harness.read_text().strip()
        if h_content:
            first_line = h_content.split("\n", 1)[0].strip("# ").strip()
            lines.append(f"harness: {first_line}")

    surface_line = _surface_line()
    if surface_line:
        lines.append(surface_line)

    # Phase 12 · profile-audit drift, when present and unacknowledged
    audit_line = _profile_audit_line()
    if audit_line:
        lines.append(audit_line)

    # CP8 · Layer 8 spot-check digest — count of pending entries in
    # ~/.episteme/state/spot_check_queue.jsonl (entries without a
    # verdict and without an active skip).
    spot_line = _spot_check_line()
    if spot_line:
        lines.append(spot_line)

    # CP9 · Pillar 3 framework digest — protocols synthesized since
    # the last session + pending deferred-discovery count. Silent on
    # zero. The "since last" window is maintained via
    # ~/.episteme/state/last_session.json which we update below.
    framework_line = _framework_digest_line()
    if framework_line:
        lines.append(framework_line)

    # Phase A · v1.0.1 — noise-watch advisory derived from the operator
    # profile's cognitive.noise_signature axis. Silent when the knob is
    # absent. Ordering: AFTER the framework digest so the cognitive
    # context lands last, closest to the operator's first read.
    noise_line = _noise_watch_line()
    if noise_line:
        lines.append(noise_line)

    # NEXT_STEPS.md if present
    ns = Path("docs/NEXT_STEPS.md")
    if ns.exists():
        content = ns.read_text().strip()
        if content:
            lines.append(f"\n--- docs/NEXT_STEPS.md ---\n{content}")

    if lines:
        separator = "─" * 60
        print(f"\n{separator}")
        print("\n".join(lines))
        print(separator)

    # CP9 · update the last-session marker so the NEXT SessionStart's
    # "since last" window starts here.
    _write_last_session_ts(datetime.now(timezone.utc).isoformat())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
