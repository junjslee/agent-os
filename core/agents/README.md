# Agent roles

This directory defines focused role prompts used by episteme delegation workflows.

Each role is narrow and composable. Composability is the point — you don't want a single god-agent trying to plan, implement, review, and govern simultaneously. You want specialized roles that hand off cleanly.

## Execution roles

| Role | Purpose |
|---|---|
| `planner.md` | Multi-step work decomposition, risk surfacing, phase sequencing |
| `implementer.md` | Bounded coding work with clear file scope and verification |
| `researcher.md` | Primary-source technical research before implementation decisions |
| `reviewer.md` | Code review for correctness, regressions, edge cases, deploy risk |
| `test-runner.md` | Targeted verification, failure isolation, smallest-fix identification |
| `docs-handoff.md` | Project continuity — updates PROGRESS.md and NEXT_STEPS.md |

## Structural governance roles

| Role | Purpose |
|---|---|
| `domain-architect.md` | System layers, entity boundaries, invariants, vocabulary |
| `reasoning-auditor.md` | Decision quality gate — known/unknown/assumptions/disconfirmation |
| `governance-safety.md` | Policy conformance, risk classification, promotion gate checks |
| `orchestrator.md` | Multi-agent coordination, role-to-task mapping, integration |
| `domain-owner.md` | Domain outcome framing, utility criteria, acceptance criteria |

## Layer mapping

- L0 System Structure: `domain-architect`
- L1 Reasoning Principles: `reasoning-auditor`
- L2 Governance: `governance-safety`
- L3 Execution: `planner` / `implementer` / `reviewer` / `test-runner` / `docs-handoff`
- L4 Orchestration + outcomes: `orchestrator` / `domain-owner`

## Guidelines

- Keep each role narrow and composable.
- Encode decision-quality standards (known/unknown/assumptions/disconfirmation) in every non-trivial prompt.
- Prefer reversible next actions and explicit verification criteria.
- When running shell searches, prefer `rg` for content search and `fd` for file discovery.
