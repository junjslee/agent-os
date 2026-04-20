# Hooks → Kernel Mapping

Which runtime hook enforces which kernel invariant. Adapters register these hooks into the host runtime's PreToolUse / PostToolUse / SessionStart / Stop events.

## Kernel element → enforcing hook

| Kernel element | Hook | Event | Enforcement |
|---|---|---|---|
| Constraint regime — forbidden actions | `block_dangerous.py` | PreToolUse/Bash | hard block on rm -rf, force push, sudo, mkfs, etc. |
| Reasoning Surface — presence before high-impact op | `reasoning_surface_guard.py` | PreToolUse/Bash\|Write\|Edit\|MultiEdit | advisory (block in strict mode) when `.episteme/reasoning-surface.json` is missing, stale, or incomplete |
| Frame stage — session boot context | `session_context.py` | SessionStart | prints git state, NEXT_STEPS, and Reasoning Surface status |
| Execute stage — docs alignment advisory | `workflow_guard.py` | PreToolUse/Write\|Edit\|MultiEdit | nudges agent to keep docs/PLAN.md and docs/PROGRESS.md aligned |
| Execute stage — prompt-injection defense | `prompt_guard.py` | PreToolUse/Write\|Edit\|MultiEdit | flags suspicious patterns in docs/, AGENTS.md, CLAUDE.md |
| Execute stage — context pressure awareness | `context_guard.py` | PostToolUse | warns when compaction is near |
| Verify stage — tests | `test_runner.py` | PostToolUse | runs affected tests after edits |
| Verify stage — gate | `quality_gate.py` | Stop | opt-in pytest gate (presence of `.quality-gate`) |
| Handoff stage — git snapshot | `checkpoint.py` | Stop / SubagentStop | auto-commits session state |
| Memory preservation | `precompact_backup.py` | PreCompact | backs up memory before compaction |

## Reasoning Surface state file

Path: `.episteme/reasoning-surface.json` in project cwd.

```
{
  "timestamp": "2026-04-17T14:00:00Z",
  "core_question": "<one question this work answers>",
  "knowns": ["..."],
  "unknowns": ["..."],
  "assumptions": ["..."],
  "disconfirmation": "<what evidence would prove this wrong>"
}
```

TTL: 30 minutes. Any high-impact op (git push, publish, migrations, cloud deletes, DB DROP, lockfile edits) requires a fresh Surface. Missing / stale / incomplete → advisory by default; block when `.episteme/strict-surface` exists.

## Integrity manifest

`kernel/MANIFEST.sha256` tracks sha256 of every managed kernel file. Regenerate after intentional kernel edits:

```
episteme kernel update
episteme kernel verify
```

`episteme doctor` surfaces drift as a non-blocking warning.
