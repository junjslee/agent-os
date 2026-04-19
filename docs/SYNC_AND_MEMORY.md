# Sync and Memory Model

How the kernel + operator profile reach every runtime, and how memory is structured, scoped, and reconciled.

## What `cognitive-os sync` propagates

| Asset                                                              | Claude Code    | Hermes                       | OMO / OMX |
|--------------------------------------------------------------------|----------------|------------------------------|-----------|
| Global memory index (`CLAUDE.md`)                                  | ✅             | —                            | —         |
| Operator / cognitive / workflow sources (`core/memory/global/*.md`)| via include    | composed into `OPERATOR.md`  | —         |
| Agent personas                                                     | ✅             | —                            | ✅        |
| Skills                                                             | ✅             | ✅                           | ✅        |
| Lifecycle hooks                                                    | ✅             | —                            | ✅        |
| Authoritative context composite (`OPERATOR.md`)                    | —              | ✅                           | —         |

This matrix describes current adapter capabilities, not architectural authority. Authoritative truth remains in repository docs and global memory — tool-native memories are acceleration only.

## Memory model

```
global memory (this repo, ~/cognitive-os/core/memory/global/)
└── stable cross-project context: who you are, how you work, safety policy

project memory (each repo's docs/)
└── what is being built, current state, next handoff, decision story

episodic memory (session/run traces)
└── observations, decisions, verification outcomes for replay and audit

plugin memory (claude-mem, tool-native, etc.)
└── cache and retrieval — never the authoritative record
```

Global memory never belongs in chat. Project memory never belongs in global. Plugins help but do not replace either.

## Memory Contract v1

Formal schema + conflict semantics for portable integrations.

- Spec: [`MEMORY_CONTRACT.md`](./MEMORY_CONTRACT.md)
- Schemas: `core/schemas/memory-contract/*.json`

Required provenance fields: `source_type`, `source_ref`, `captured_at`, `captured_by`, `confidence`.

Explicit memory classes: `global`, `project`, `episodic`.

Conflict order: `project > global > episodic`, then status / recency / confidence, with human override as terminal.

Additive bridges for external runtimes (e.g., `cognitive-os bridge anthropic-managed`) transform runtime events into memory-contract envelopes without changing existing sync behavior. See [`ANTHROPIC_MANAGED_AGENTS_BRIDGE.md`](./ANTHROPIC_MANAGED_AGENTS_BRIDGE.md).

## Evolution Contract v1

Safe self-improvement loop that preserves authoritative governance.

- Spec: [`EVOLUTION_CONTRACT.md`](./EVOLUTION_CONTRACT.md)
- Schemas: `core/schemas/evolution/*.json`

Core loop: generator proposes bounded mutation → critic attempts disconfirmation → deterministic replay + evaluation → promotion gates decide pass/fail → human-approved promotion with rollback reference.

## Coexistence with self-evolving runtimes

1. Local runtime memory evolves fast during execution (high-velocity adaptation).
2. Durable lessons are promoted into authoritative files (`core/memory/global/*`, `docs/*`, reusable skills).
3. `cognitive-os sync` republishes that contract to every runtime.
4. Runtime-native memory remains a cache, not the source of truth.

Result: fast local learning **and** deterministic cross-platform consistency.

## Managed runtime positioning

`cognitive-os` and managed runtimes (e.g., Anthropic Managed Agents) are complementary.

- **Managed runtime** — execution substrate: orchestration, sandbox/tool execution, durable session/event logs.
- **cognitive-os** — cross-runtime cognitive control plane: identity, memory governance, authoritative docs, deterministic policy sync.

Operating pattern: run long tasks in a managed runtime → bridge session events into cognitive-os envelopes → promote durable lessons into authoritative docs → sync the updated contract back to every local runtime.
