# Deterministic Safety Hooks

Hooks run deterministically — the model cannot override them. Each hook is a named counter to a specific class of unsafe or inconsistent action; together they form the execution-time enforcement layer for kernel invariants.

## Governance packs

Packs are applied via `episteme sync` or `episteme setup --sync`.

| Pack       | Contents                                                                                                   |
|------------|------------------------------------------------------------------------------------------------------------|
| `minimal`  | Baseline safety only: `block_dangerous`, formatter, test runner, checkpoint, quality gate.                 |
| `balanced` | `minimal` + workflow / context / prompt advisories (**default**).                                          |
| `strict`   | `balanced` + removes the generic `PermissionRequest` auto-allow fallback while preserving custom permissions. |

## Hook reference

| Hook                    | Event                                                    | What it does                                                                                    |
|-------------------------|----------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `session_context.py`    | `SessionStart`                                           | Prints branch, git status, and `NEXT_STEPS.md` at session open (if present in your project)     |
| `block_dangerous.py`    | `PreToolUse Bash`                                        | Blocks `rm -rf`, `git reset --hard`, `git push --force`, `sudo`, `pkill`, and more              |
| `workflow_guard.py`     | `PreToolUse Write\|Edit\|MultiEdit`                      | Advisory nudge to keep authoritative docs (`PLAN.md` / `PROGRESS.md` / `NEXT_STEPS.md`) aligned with edits, when present |
| `prompt_guard.py`       | `PreToolUse Write\|Edit\|MultiEdit`                      | Advisory detection of prompt-injection patterns when writing durable context                    |
| `format.py`             | `PostToolUse Write\|Edit`                                | Auto-runs `ruff` (Python) or `prettier` (JS/TS) after every file write                          |
| `test_runner.py`        | `PostToolUse Write\|Edit`                                | Runs pytest / jest on the file if it is a test file                                             |
| `context_guard.py`      | `PostToolUse Bash\|Edit\|Write\|MultiEdit\|Agent\|Task`  | Advisory warning when session context approaches compaction thresholds                          |
| `quality_gate.py`       | `Stop`                                                   | Blocks completion if tests fail (opt-in via `.quality-gate` in project root)                    |
| `checkpoint.py`         | `Stop`                                                   | Auto-commits uncommitted changes as `chkpt:` after every turn                                   |
| `precompact_backup.py`  | `PreCompact`                                             | Backs up session transcripts before context compaction                                          |

## Customization

Hook scripts live in `core/hooks/`. They run with whichever Python invoked the CLI (`sys.executable`). Paths resolve dynamically so the same scripts work on any machine. Pin a specific runtime via:

```bash
export EPISTEME_PYTHON_PREFIX=/path/to/prefix    # e.g. ~/miniconda3, .venv
# or pick the binary directly:
export EPISTEME_PYTHON=/path/to/bin/python
```

Set `EPISTEME_REQUIRE_CONDA=1` to enforce Conda `base` in `episteme doctor`.

## Invariant mapping

See [`kernel/HOOKS_MAP.md`](../kernel/HOOKS_MAP.md) for the mapping from kernel invariants to the hooks that enforce them at runtime, and for the Reasoning Surface state file (`.episteme/reasoning-surface.json`) + integrity manifest commands.
