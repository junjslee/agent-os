# Agent Operating Manual

## Purpose
This file is the vendor-neutral operating manual for agents working in this repository.

## Required Memory Files
Read in this order at session start:
- `docs/NEXT_STEPS.md` — current priority and next actions
- `docs/PROGRESS.md` — current state and key decisions
- `HARNESS.md` — project harness: execution profile, workflow constraints, safety rules (if present)
Read on demand:
- `CLAUDE.md`
- `docs/REQUIREMENTS.md`
- `docs/PLAN.md`
- `docs/RUN_CONTEXT.md`

## Workflow
1. **Explore**: Read project memory and define the reasoning surface.
2. **Deconstruct**: Separate Knowns, Unknowns, and Assumptions in `docs/REQUIREMENTS.md`.
3. **Plan**: Update `docs/PLAN.md`.
4. **Falsify**: Before implementing, state one reason why this plan might fail (Disconfirmation).
5. **Implement**: Execute implementation with staged verification.
6. **Review**: Validate against the original requirements and cognitive profile.
7. **Handoff**: Update `docs/NEXT_STEPS.md` with a "So-What Now?" summary.

## Reasoning Surface (Mandatory in Docs)
Every major decision must record:
- **Knowns**: Verified facts/constraints.
- **Unknowns**: Missing info or risks.
- **Assumptions**: What we are taking for granted.
- **Disconfirmation**: What would prove this decision wrong?

## Worktree Naming
- `feat/<name>` — new feature
- `fix/<name>` — bug fix
- `research/<name>` — investigation or query work
- `ops/<name>` — infra, scripts, tooling
- `docs/<name>` — documentation handoff

## Guardrails
- Prefer the smallest useful verification step first.
- Do not duplicate large prompt blocks in chat when they belong in project memory.
- Record environment limits, APIs, and rate limits in `docs/RUN_CONTEXT.md`.
- Keep `CLAUDE.md` short — use it as an index into live docs, not a content store.

## Bounded Automation
When running any unattended or semi-attended loop, record before starting:
- objective
- candidate set or input parameters
- max iterations or time limit
- evaluation rubric
- expected artifact outputs
- stop condition
- human review checkpoint

No unattended code-writing, auto-merge, or production-promotion loops.

## Review Gate
Review is required before merge for:
- logic changes to core domain code
- data pipeline or artifact generation changes
- any change that touches shared production artifacts

## Logging
Use `agent_logs/action_log.md` for substantive runs only:
remote executions, cleanup passes, bounded loops, major audits, branch handoffs.
Do not log every shell command. Source of truth remains `docs/PROGRESS.md`.

## Publication Boundary
Safe to commit:
- `AGENTS.md`, `CLAUDE.md`, `docs/*.md`, shared runtime files, code, tests, research artifacts.

Keep local only:
- `.claude/settings.local.json`, user auth, trust settings, `.env*`, `secrets/`, private keys, large local datasets.

## Runtime Policy
- `cognitive-os` is the source of truth for the project scaffold.
- Local Python-backed `cognitive-os` work runs in Conda `base` at `{{CONDA_ROOT}}`.
- Homebrew Python is not the supported runtime for `cognitive-os`.
