# episteme docs index

Primary navigation for episteme documentation.

## Start here

- `../README.md` — project overview, what problem it solves, quickstart, full command surface
- `../kernel/` — the canonical markdown spec: constitution, reasoning surface, system-1 counters, operator-profile schema
- `../kernel/CONSTITUTION.md` — the governing philosophy: why this system exists, what it believes, and what it is not
- `ARCHITECTURE.md` — v1.0 RC runtime flowchart (Mermaid) with node annotations and cross-references
- `LAYER_MODEL.md` — layer model, tool/adapter matrix, bootstrap policy, source-of-truth order

## Contracts

- `MEMORY_CONTRACT.md` — memory classes, provenance schema, conflict resolution semantics
- `EVOLUTION_CONTRACT.md` — gated self-evolution lifecycle, mutation library, promotion gates

## Runtime bridges

- `ANTHROPIC_MANAGED_AGENTS_BRIDGE.md` — import Anthropic Managed Agents runtime events into Memory Contract v1 episodic envelopes

## Open-source guidance

- `OPEN_SOURCE_YOUR_PROFILE.md` — how and why to share your personal episteme profile as a reference implementation

## Recommended reading order

Read the kernel first. Everything else is derived from it.

1) `../kernel/CONSTITUTION.md`
2) `../kernel/REASONING_SURFACE.md`
3) `../kernel/SYSTEM_1_COUNTERS.md`
4) `../kernel/OPERATOR_PROFILE_SCHEMA.md`
5) `../README.md`
6) `ARCHITECTURE.md`
7) `LAYER_MODEL.md`
8) `MEMORY_CONTRACT.md`
9) `EVOLUTION_CONTRACT.md`

## Contribution quality gate (docs changes)

For major docs updates, ensure:
- clear problem statement and intended user outcome
- knowns/unknowns/assumptions/disconfirmation for substantive claims
- consistency with `episteme` naming and command examples
- links and commands verified
