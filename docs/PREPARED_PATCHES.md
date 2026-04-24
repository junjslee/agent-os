# Prepared Patches — v1.0.1 Hook Fixes (Event 47 · Event 49 applied Path-Y)

**Status update Event 49.** Operator authorized Path-Y
application of CP-TEL-01 + CP-DEDUP-01 mid-soak. Both landed on
`event-49-path-y-hook-fixes` branch with 604 tests passing (baseline
593 + 11 new regression pins). CP-FENCE-01 orphan cleanup ran once
(88 stale markers retired). CP-FENCE-01 protocol-synthesis-on-op
is downstream of CP-TEL-01 and SHOULD work now; but a residual
correlation-id mismatch (PreToolUse SHA-1-fallback vs PostToolUse
tool_use_id) still blocks some synthesis. Tracked as residual
CP-FENCE-02 below.

**Soak clock not reset.** Event 49's patches are additive to
evidence collection — they fix what the hook records, not what
the agent decides. The Event-38 2026-04-23T21:23:36Z anchor
continues.

Original doc below, marked with Event-49 status notes.

---

## CP-TEL-01 — **APPLIED Event 49** · exit_code extraction + returnCodeInterpretation

**Status**: ✓ **APPLIED** in `core/hooks/calibration_telemetry.py` and
`core/hooks/fence_synthesis.py`. 11 regression tests added. 597/597
test suite passing. Live verification: outcome records now populate
`exit_code` + `status` correctly (verified via `~/.episteme/state/hooks.log`
post-patch entries showing `exit=0 status=success` on successful ops
and `exit=1 status=error` on failed ops).

**Expanded diagnosis in Event 49.** The original CP-TEL-01 diagnosis
(camelCase `isError` vs snake_case `is_error`) was PARTIALLY CORRECT but
incomplete. Claude Code's actual Bash tool_response shape has no
`isError` field either — it uses `returnCodeInterpretation` (None on
success / non-empty string like "No matches found" or "command exited
with exit code N" on error) plus `interrupted` (bool, True on SIGINT).
The applied patch handles all three variants (explicit numeric exit code,
bool isError/is_error, Claude-Code returnCodeInterpretation pattern).
Regex extracts explicit exit code `N` from rci strings matching
`exit code N`; otherwise non-empty rci defaults to exit 1;
`interrupted: True` maps to 130 (SIGINT convention).

### Original diagnosis (pre-Event-49)

**Root cause** (confirmed Event 47 via `core/hooks/calibration_telemetry.py`
lines 66-90 + `core/hooks/fence_synthesis.py` lines 60-92): both
hooks' `_extract_exit_code()` and `_extract_status()` look for
snake_case keys on `tool_response` (`is_error`, `exit_code`,
`returncode`, …). Claude Code's Bash tool_response uses camelCase
`isError` + `stdout` / `stderr` / `interrupted`, and does NOT include
a numeric `exit_code` field at all.

Evidence: 3,357 predictions logged vs 80 outcomes captured across
5 days (42× gap). Of the 80 outcomes captured, 80/80 have
`exit_code: null` and `status: "unknown"`. Consistent with the
extraction logic finding zero matches in the payload's
tool_response.

**Symmetric hook-level handling** for camelCase already exists on
`tool_name` / `tool_input` keys (see `_tool_name()` / `_tool_input()`
helpers) — the authors knew about the duality. It's a code-inconsistency
bug, not a design limitation.

### Prepared diff — `core/hooks/calibration_telemetry.py`

Replace the `_extract_exit_code` function body with:

```python
def _extract_exit_code(payload: dict) -> int | None:
    """Walk the tool_response structure for a numeric exit code.

    Claude Code's Bash tool_response provides `isError` (camelCase
    bool) — 0 on False, 1 on True. Other runtimes may provide
    explicit numeric exit codes. This handles both shapes.
    """
    resp = (
        payload.get("tool_response")
        or payload.get("toolResponse")
        or {}
    )
    if not isinstance(resp, dict):
        return None
    for key in (
        "exit_code", "exitCode", "returncode", "return_code",
        "status_code",
    ):
        v = resp.get(key)
        if isinstance(v, int):
            return v
        if isinstance(v, str) and v.strip().lstrip("-").isdigit():
            return int(v.strip())
    for wrapper_key in ("metadata", "meta"):
        wrapper = resp.get(wrapper_key)
        if isinstance(wrapper, dict):
            for key in (
                "exit_code", "exitCode", "returncode", "return_code",
            ):
                v = wrapper.get(key)
                if isinstance(v, int):
                    return v
    # Claude Code shape — map isError / is_error bool to 0 or 1.
    for bool_key in ("isError", "is_error"):
        if bool_key in resp:
            return 1 if resp[bool_key] else 0
    return None
```

And the `_extract_status` function:

```python
def _extract_status(payload: dict) -> str:
    """Best-effort status string: 'success' / 'error' / 'unknown'."""
    resp = (
        payload.get("tool_response")
        or payload.get("toolResponse")
        or {}
    )
    if not isinstance(resp, dict):
        return "unknown"
    for bool_key in ("isError", "is_error"):
        if bool_key in resp:
            return "error" if resp[bool_key] else "success"
    if "error" in resp and resp["error"]:
        return "error"
    s = resp.get("status")
    if isinstance(s, str) and s:
        return s.lower()
    return "unknown"
```

### Prepared diff — `core/hooks/fence_synthesis.py`

Same pattern — replace `_extract_exit_code` body with the block above
(the fence hook's version already had the `is_error` fallback; add
`isError` variant next to it).

### Verification procedure

After applying:

1. Run any Bash command via Claude Code.
2. `tail -1 ~/.episteme/telemetry/$(date -u +%F)-audit.jsonl | jq .`
3. Confirm `exit_code` is `0` (not `null`) and `status` is `"success"`
   (not `"unknown"`).
4. Run 10 commands; confirm 10 outcomes with valid exit codes.
5. Retire the `100% null exit_code` blocker on Gate 22 grading.

---

## CP-FENCE-01 — **APPLIED Event 49 (orphan cleanup)** · PARTIAL (synthesis still blocked by CP-FENCE-02)

**Orphan cleanup status**: ✓ `tools/fence_marker_cleanup.py` shipped +
ran once Event 49; 88 stale markers removed (89 → 1 at run time; a few
new ones have since appeared as expected).

**Protocol synthesis status**: ⚠ PARTIAL. Downstream of CP-TEL-01 as
originally diagnosed — exit_code extraction now works so the
`if exit_code == 0` gate in `finalize_on_success` no longer blocks.
BUT a separate bug (CP-FENCE-02 below) still prevents most fence
firings from producing protocols.

### Original diagnosis (pre-Event-49)

**Root cause** (confirmed Event 47):
1. **Downstream of CP-TEL-01.** `fence_synthesis.finalize_on_success()`
   writes a protocol iff `exit_code == 0`. Exit code is None for every
   invocation, so the `if exit_code == 0:` branch never fires. Fix
   CP-TEL-01 → fence synthesis starts producing.
2. **Orphan markers.** `~/.episteme/state/fence_pending/` contains 88
   `h_*.json` marker files from the pre-fix era when `tool_use_id`
   was not present in PreToolUse payloads and the correlation_id fell
   back to the SHA-1 hash. PostToolUse then computed a different
   correlation_id (from `toolu_*`), never found the marker, never
   called `delete_pending_marker()`. Each orphan is tiny but they
   accumulate.

### Prepared fix A — unblock protocol writes

**No code change needed.** Fix CP-TEL-01 and fence synthesis starts
working. Verify by:

1. Run any high-impact Bash command that fires fence_reconstruction.
2. Check `~/.episteme/framework/protocols.jsonl` exists after the
   command.
3. Gate 26 grading: `python3 tools/grade_gates.py` should report
   Gate 26 as PARTIAL (≥ 1 protocol) or PASS (≥ 1 reasoning-shape
   protocol).

### Prepared fix B — orphan-marker cleanup (optional)

Add a small tool that walks `fence_pending/` and deletes markers
whose `written_at` is > 24 hours old (existing TTL). Either:

**Option B-1**: Standalone cleanup script at
`tools/fence_marker_cleanup.py`:

```python
#!/usr/bin/env python3
"""One-shot cleanup of stale fence_pending markers beyond TTL."""
from pathlib import Path
from datetime import datetime, timezone
import json, sys

MARKER_TTL_SECONDS = 24 * 60 * 60
pending = Path.home() / ".episteme" / "state" / "fence_pending"
now = datetime.now(timezone.utc)
removed = 0
for p in pending.glob("*.json"):
    try:
        with open(p) as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        p.unlink(missing_ok=True); removed += 1; continue
    written = data.get("written_at", "")
    try:
        age = (now - datetime.fromisoformat(written.replace("Z", "+00:00"))).total_seconds()
    except ValueError:
        age = float("inf")
    if age > MARKER_TTL_SECONDS:
        p.unlink(missing_ok=True)
        removed += 1
print(f"removed {removed} stale markers", file=sys.stderr)
```

**Option B-2**: Inline sweep at top of `fence_synthesis.py` main() —
walks pending/ and deletes stale markers on each invocation. Bounded
cost (typical dir size < 100 files).

Recommend Option B-1 for a v1.0.1 that doesn't re-edit hot-path code.

### Verification procedure

1. Before: `ls ~/.episteme/state/fence_pending/ | wc -l` reports 89+.
2. Run `python3 tools/fence_marker_cleanup.py` (or re-run hook 24h
   after applying Option B-2).
3. After: only markers < 24h old remain.

---

## CP-DEDUP-01 — **APPLIED Event 49** · deferred-discovery dedup on log

**Status**: ✓ **APPLIED** in `core/hooks/_framework.py`. Pre-write
tail-scan-200 check on `(flaw_classification, description[:120])` key.
Three regression tests added (`test_cp_dedup_01_*`). When a match is
found, returns `{"suppressed_duplicate": True, "matched_entry_hash":
..., "matched_ts": ...}` instead of writing a new chain entry.
Existing 1,294 records untouched (retroactive cleanup is CP-DEDUP-02
territory — not in scope).

Also callable with `dedup=False` kwarg for explicit opt-out (test
corpus uses this for multi-write scenarios).

### Original diagnosis (pre-Event-49)

**Observation** (Phase 2 triage): 1,294 deferred_discoveries records
collapse to 40 unique findings. 32× dup rate. Cause: every
`cascade:architectural` firing re-logs identical `deferred_discovery`
entries without checking whether the same finding already exists.

**Prepared fix** — add a pre-write dedup check in the framework
writer. Candidate location: wherever `deferred_discoveries[]`
entries are chained into the framework stream (likely in
`core/hooks/_framework.py` or the cascade detector). Write
pseudocode:

```python
def append_deferred_discovery(new: dict, framework_path: Path) -> bool:
    """Return True if written, False if suppressed as duplicate."""
    new_class = new.get("flaw_classification", "")
    new_desc = (new.get("description") or "")[:120]
    # Walk last N entries (bounded; full scan is O(n) per write)
    cutoff = max(0, total_entries - 200)  # check last 200 only
    for existing in tail_entries(framework_path, n=200):
        existing_payload = existing.get("payload", {})
        if existing_payload.get("type") != "deferred_discovery":
            continue
        if (existing_payload.get("flaw_classification", "") == new_class
                and (existing_payload.get("description") or "")[:120]
                    == new_desc):
            return False  # duplicate
    append_chained(framework_path, new)
    return True
```

**Design constraint**: cannot break chain integrity — append must
still produce valid hash-chained entries. Dedup suppression is the
write-path behavior, not a chain-level change.

### Verification procedure

1. Pre-fix: count records per day in deferred_discoveries.jsonl.
2. Apply fix.
3. Post-fix: new records only when description/class actually novel.
   Monitor for 24 hours; expect <10 new records vs pre-fix ~70/day.

---

## CP-FENCE-02 — **APPLIED Event 50** · correlation-id PreToolUse/PostToolUse mismatch

**Status**: ✓ **APPLIED** in `core/hooks/_fence_synthesis.py` (new
`candidate_correlation_ids` + `finalize_on_success_with_fallback` helpers),
`core/hooks/reasoning_surface_guard.py` (loop writes markers under all
candidates), `core/hooks/fence_synthesis.py` (postToolUse uses fallback
finalizer). 3 new regression tests; 600/600 test suite passing.

**Strategy B selected** (dual-write + fallback-read rather than unify on
SHA-1). Rationale: degrades gracefully if Claude Code populates
tool_use_id on PreToolUse in a future version — dual-write still works;
single-unify-on-SHA-1 would discard the stronger uniqueness signal.

### Original diagnosis (pre-Event-50)

**Observation (Event 49 diagnostic)**. Even after CP-TEL-01 patch
unblocks exit_code extraction, the fence synthesis pipeline still
does not reliably produce protocols on live ops. Root cause (partial):
`~/.episteme/state/fence_pending/` contains markers with `h_*`
correlation id prefix (SHA-1 hash fallback) when the PreToolUse
payload lacked `tool_use_id`. PostToolUse then computes correlation
from `tool_use_id` (present in PostToolUse payload), producing a
`toolu_*` prefix that does not match. `read_pending_marker()`
returns None; `finalize_on_success()` early-exits; no protocol
written.

**Why PreToolUse lacks tool_use_id (hypothesis — unverified).** Claude
Code may send different payload shapes to Pre vs Post invocations —
tool_use_id might only be populated on PostToolUse for deliverability
guarantees. Or the current hook-dispatching path reads a different
subset of fields at PreToolUse time.

**Prepared fix (design sketch — not yet implemented).**
1. Instrument `reasoning_surface_guard.py`'s PreToolUse path to log
   which correlation-id source was used (tool_use_id vs SHA-1
   fallback).
2. If SHA-1 fallback dominates, inspect actual PreToolUse payload
   keys (same diagnostic pattern Event 49 used on tool_response).
3. If `tool_use_id` genuinely isn't available at PreToolUse,
   switch BOTH pre and post to use the SHA-1 fallback key (cwd +
   second-bucket + cmd) even when tool_use_id IS available on
   Post. That way both sides compute the same id. Cost: loses
   tool_use_id's stronger uniqueness but gains pairing reliability.
4. Alternatively: PreToolUse writes the marker under BOTH candidate
   correlation-ids (SHA-1 + whatever-id-is-available); PostToolUse
   tries all candidate ids when reading.

**Priority**: HIGH for Gate 26 PASS; MEDIUM for overall v1.0.1
because Gate 26 PARTIAL is achievable via a subset of fence firings
that happen to match.

**Effort**: 2-3 hours including diagnostic + fix + tests.

---

## CP-PHASE12-01 — operator action

**Resolved Event 47** (see POST_SOAK_TRIAGE §1.5). No code change
needed. Operator action required before Day-7 grading:

```bash
episteme profile audit --write
```

This writes to `~/.episteme/memory/reflective/profile_audit.jsonl`.
Gate 25 grades against that file.

---

## Application order recommendation

When the operator is ready to apply these (post-soak or
Path-A-authorized mid-soak):

1. **CP-PHASE12-01** — operator runs `episteme profile audit
   --write` (no code change).
2. **CP-TEL-01** — apply the exit_code/status patches. Verify
   non-null outcomes start appearing.
3. **CP-FENCE-01** — no code change (downstream of #2); verify
   protocols.jsonl starts populating. Then run the orphan cleanup
   script once.
4. **CP-DEDUP-01** — design + apply the dedup check. Requires
   design review for the tail-scan bound.
5. **Re-run Phase 1 grading**. Gates 22, 25, 26 should materially
   move.

## Risk assessment

| Patch | Soak impact if applied mid-soak | Effort |
|---|---|---|
| CP-TEL-01 | LOW — adds keys to extraction; cannot break existing data | 30 min |
| CP-FENCE-01 A | LOW — downstream of CP-TEL-01, no own code change | 0 min |
| CP-FENCE-01 B-1 | NONE — standalone cleanup script, run once | 30 min |
| CP-DEDUP-01 | MEDIUM — modifies framework write path; test required | 2-4 hrs |
| CP-PHASE12-01 | NONE — operator CLI invocation only | 5 min |

Total to unblock Gates 22, 25, 26: ~1 hour of operator time +
diff review.
