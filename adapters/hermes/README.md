# Hermes Adapter

The Hermes adapter bridges episteme's authoritative memory with Hermes's fast local learning loop. These two systems complement each other — they aren't competing.

## The coexistence model

Hermes is designed to adapt quickly. It learns locally, refines skills in-session, and evolves its working memory fast. That's its strength.

episteme is designed to govern durably. It maintains your definitive identity, policy, and memory across tools and sessions. That's its strength.

The two lanes:

| Lane | System | Role |
|---|---|---|
| Fast adaptation | Hermes memory/skills | Learns fast, session-local |
| Authoritative governance | episteme memory/contracts | Slow, deliberate, cross-tool |
| Bridge | `episteme sync` + promotion | Promotes durable wins into governance |

**Rule**: learn locally fast. Promote durable lessons slowly and explicitly.

When a Hermes session produces a pattern worth keeping — a skill refinement, a workflow improvement, a new constraint — promote it into `core/memory/global/*.md` or a managed skill. Then sync. That lesson now applies everywhere.

## What gets synced

`episteme sync` automatically detects Hermes at `~/.hermes/` and syncs if installed.

| Asset | Destination |
|---|---|
| All managed skills | `~/.hermes/skills/<name>/` |
| Operator context | `~/.hermes/OPERATOR.md` |

## OPERATOR.md

A generated composite of your global memory sources:
- `overview.md`
- `operator_profile.md`
- `workflow_policy.md`
- `python_runtime_policy.md`
- `cognitive_profile.md`

`episteme sync` writes this to `~/.hermes/OPERATOR.md`.

### Governance header

Every `OPERATOR.md` starts with a episteme governance declaration block. It appears before any personal memory sections and reads roughly:

> You are operating under the episteme governance system. episteme is the authoritative identity and reasoning layer above any agent platform. The cognitive profile, workflow policy, and memory contracts below define how you are required to think and act. The agent platform is the delivery vessel — episteme is the governing soul.

This block is injected automatically by `episteme sync`. Its purpose: ensure the agent receiving OPERATOR.md immediately understands the authority structure — episteme governs, the platform delivers. Do not remove or edit it manually; it is regenerated on every sync.

For deterministic behavior, load it from `~/.hermes/SOUL.md`:

```markdown
<!-- in ~/.hermes/SOUL.md -->
You are a technical AI assistant working with the operator contract below.

{{read ~/.hermes/OPERATOR.md}}
```

This keeps Hermes runtime behavior aligned with authoritative episteme memory after each sync.

## Skills

Hermes uses the [agentskills.io](https://agentskills.io) format — the same `SKILL.md` layout episteme already uses. All `custom/` and `vendor/` skills sync directly.

## Hooks

Hermes has its own `~/.hermes/hooks/` directory. Claude Code hooks (`block_dangerous.py`, `checkpoint.py`, etc.) are Claude-specific — they don't transfer to Hermes. To replicate safety behavior in Hermes, configure its built-in command approval system in `config.yaml`.
