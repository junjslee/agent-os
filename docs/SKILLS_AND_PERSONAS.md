# Skills and Agent Personas

Two extension surfaces shipped with cognitive-os: **skills** (reusable operator capabilities) and **personas** (subagent definitions). Both propagate via `cognitive-os sync`.

## Skills

### Custom (your own)

`repo-bootstrap` · `requirements-to-plan` · `progress-handoff` · `worktree-split` · `bounded-loop-runner` · `review-gate` · `research-synthesis`

### Vendor (curated upstream)

`swing-clarify` · `swing-options` · `swing-research` · `swing-review` · `swing-trace` · `swing-mortem` · `create-prd` · `sprint-plan` · `pre-mortem` · `test-scenarios` · `prioritization-frameworks` · `retro` · `release-notes`

### Adding your own

Drop a folder under `skills/custom/` with a `SKILL.md`. Experimental skills that should never sync globally live under `skills/private/`.

### Vendor skill provenance (inspired, not copied)

- Required vendor attribution map: `skills/vendor/SOURCES.md`.
- Every vendor skill should include a `## Provenance` section in its `SKILL.md` when imported or adapted.
- Run `cognitive-os validate` to surface manifest or provenance warnings before shipping.

## Agent personas

Eleven subagent definitions install into `~/.claude/agents/` on sync.

**Execution:** `planner` · `researcher` · `implementer` · `reviewer` · `test-runner` · `docs-handoff`.

**Structural governance:** `domain-architect` · `reasoning-auditor` · `governance-safety` · `orchestrator` · `domain-owner`.

Every delegated task begins with a **Shared Context Brief** and ends with a **Verification Artifact** — see the workflow convention in [`../AGENTS.md`](../AGENTS.md).
