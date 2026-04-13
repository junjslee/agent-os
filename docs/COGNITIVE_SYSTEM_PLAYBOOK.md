# Cognitive System Playbook

Purpose: make cognitive-os practical for real delivery while preserving epistemic rigor.

This playbook defines how to run a cognitive system (how to think) and workflow system (how to execute) together.

## 1) Operating thesis

cognitive-os operationalizes a dual system:
- cognitive system: improves decision quality and epistemic integrity
- execution system: improves delivery reliability and verification discipline

Design rule:
- cognition without execution becomes abstract
- execution without cognition becomes brittle

## 2) Memory architecture (authoritative boundaries)

Use 3 classes with strict authority:

1. Project memory (highest day-to-day authority)
- where: `docs/*`, `AGENTS.md`, `HARNESS.md`
- content: requirements, constraints, milestones, decisions
- role: source of truth for what must be delivered now

2. Global memory
- where: `core/memory/global/*`
- content: stable operator defaults, cognitive posture, workflow policy
- role: source of truth for how work is generally done

3. Episodic memory
- where: session traces / evolution episodes
- content: observations, outcomes, experiments, run artifacts
- role: evidence for learning and promotion, not direct authority

Conflict precedence:
- project > global > episodic
- explicit human correction overrides inferred memory

## 3) Decision protocol (mandatory)

For major changes, always write:
- Knowns
- Unknowns
- Assumptions
- Disconfirmation test

Minimal template:

- Knowns: what is directly verified
- Unknowns: what could invalidate the plan
- Assumptions: what is currently believed but unproven
- Disconfirmation: one test that could prove us wrong quickly

This keeps reasoning auditable and prevents “plausible but wrong” drift.

## 4) Workflow protocol (delivery loop)

Stage loop:
1. Explore context (`docs/NEXT_STEPS.md`, `docs/PROGRESS.md`, `HARNESS.md`)
2. Plan with risk and verification checkpoints
3. Implement smallest reversible increment
4. Verify with compile/tests/smoke checks
5. Handoff with explicit next action

Output rule:
- every stage must produce an artifact (plan update, test output, decision note, handoff note)

## 5) Self-evolution protocol (accountable improvement)

Use evolution only as a gated system:
1. propose bounded mutation
2. critique/falsify the proposal
3. replay/evaluate on known suite
4. gate decision
5. promote or rollback with references

Promotion requirements:
- no safety regression
- measurable improvement or justified neutral impact
- replay evidence stored
- rollback path confirmed

Do not allow direct ungated self-modification.

## 6) Hermes coexistence model

Treat Hermes as adaptive runtime, cognitive-os as canonical governance.

Pattern:
- Hermes memory/skills = fast adaptation lane
- cognitive-os memory/contracts = canonical lane
- sync + promotion = bridge lane

Rule:
- learn locally fast
- promote durable lessons slowly and explicitly

## 7) Adapter conformance checklist

For each runtime adapter (Claude/Codex/Cursor/Hermes), verify:
- canonical files are readable from the runtime
- runtime does not override authority boundaries
- required safety behavior is active
- handoff docs are honored
- sync reproduces deterministic state

If any fail, adapter is non-conformant and must be fixed before trusting automation.

## 8) Practical anti-drift controls

- Keep generated artifacts in `.generated/` and mark them non-canonical until compiled
- Use deterministic commands for bootstrap/setup
- Keep command surface single-name (`cognitive-os`)
- run CI on every PR/push
- record high-impact decisions in `docs/DECISION_STORY.md`

## 9) Success metrics

Track these over time:
- delivery reliability: completed planned tasks / committed tasks
- verification quality: regression count, escaped defect count
- cognitive quality: % of major decisions with known/unknown/assumptions/disconfirmation
- adaptation quality: promoted evolution episodes with sustained improvement
- cross-runtime parity: same task outcome consistency across adapters

## 10) 30-day maturity roadmap

Week 1:
- stabilize naming/contracts/CI
- enforce decision protocol in templates

Week 2:
- add adapter conformance smoke checks
- add replay harness for evolution evaluation

Week 3:
- collect and promote repeated winning patterns into canonical memory/skills

Week 4:
- publish conformance report + evolution outcomes
- tighten gates based on observed regressions

---

This playbook is intentionally opinionated.
If a future change weakens authority boundaries, auditability, or rollback safety, reject it.