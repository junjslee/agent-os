# Agent roles

This directory defines focused role prompts used by cognitive-os delegation workflows.

Core execution roles:
- planner.md
- implementer.md
- reviewer.md
- researcher.md
- test-runner.md
- docs-handoff.md

Ontological governance roles:
- ontologist.md
- epistemic-auditor.md
- governance-safety.md
- orchestrator.md
- domain-owner.md

Layer mapping:
- L0 Ontology: ontologist
- L1 Epistemics: epistemic-auditor
- L2 Governance: governance-safety
- L3 Execution: planner/implementer/reviewer/test-runner/docs-handoff
- L4 Orchestration + outcomes: orchestrator/domain-owner

Guidelines:
- Keep each role narrow and composable.
- Operationalize decision quality, memory governance, execution cognition, and accountable evolution.
- Encode decision-quality standards (known/unknown/assumptions/disconfirmation).
- Prefer reversible next actions and explicit verification criteria.
