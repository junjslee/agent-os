# Hermes Adapter

`cognitive-os sync` automatically detects Hermes at `~/.hermes/` and syncs if installed.

## What Gets Synced

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

`cognitive-os sync` writes this to `~/.hermes/OPERATOR.md`.

For deterministic behavior, load it from `~/.hermes/SOUL.md`:

```markdown
<!-- in ~/.hermes/SOUL.md -->
You are a technical AI assistant working with the operator contract below.

{{read ~/.hermes/OPERATOR.md}}
```

This keeps Hermes runtime behavior aligned with authoritative `cognitive-os` memory after each sync.

## Skills

Hermes uses the [agentskills.io](https://agentskills.io) format — the same `SKILL.md`
layout cognitive-os already uses. All `custom/` and `vendor/` skills sync directly.

## Hooks

Hermes has its own `~/.hermes/hooks/` directory. Claude Code hooks (`block_dangerous.py`,
`checkpoint.py`, etc.) are Claude-specific — they do not transfer to Hermes. To replicate
safety behavior in Hermes, configure its built-in command approval system in `config.yaml`.
