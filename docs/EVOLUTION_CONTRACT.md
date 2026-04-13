# Evolution Contract v1

Purpose: define a safe, auditable self-evolution loop for the cognitive-os cognitive+execution harness.
## Product identity
Public product identity: `cognitive-os`.
CLI/package/repo identity: `cognitive-os`.
Positioning:
- cognitive-os is the cognitive + execution harness model.
- `cognitive-os` is the distribution and CLI surface.
## Core loop
Every evolution cycle follows this immutable sequence:
1. Propose (Generator role)
2. Critique (Critic role)
3. Replay + evaluate (deterministic task suite)
4. Gate decision (promote/reject)
5. Promote with rollback reference (human-approved by default)
## Evolution episode
Each run produces an `EvolutionEpisode` record with:
- `episode_id`
- `parent_episode_id` (optional)
- `hypothesis`
- `mutation`
- `suite_ref`
- `metrics_before`
- `metrics_after`
- `gate_result`
- `decision` (`promoted | rejected | rolled_back`)
- `rollback_ref`
- `provenance`
## Role split
### Generator
- Proposes bounded changes only.
- Must declare expected improvement and risk.
### Critic
- Attempts to falsify the proposal.
- Flags safety, regression, and overfitting risks.
- Must provide at least one disconfirmation test.
## Mutation library (bounded)
Allowed mutation types in v1:
- `prompt_policy_tweak`
- `retrieval_policy_tweak`
- `planning_depth_tweak`
- `tool_selection_rule_tweak`
- `handoff_format_tweak`
Disallowed in v1:
- direct secret or auth policy modifications
- unattended destructive command policy loosening
- changes outside declared mutation target scope
## Replay and evaluation
Candidate changes must run against:
1) baseline replay set
2) hard-failure replay buffer
3) optional fresh tasks
Required metrics:
- `task_success_rate`
- `safety_violation_count`
- `latency_ms_p50`
- `token_cost`
- `style_fit_score` (alignment to operator/cognitive policy)
## Promotion gates
Promotion requires all gates to pass:
- success delta >= configured threshold
- no safety regression
- latency/cost within budget envelope
- deterministic stability across repeated seeded runs
- critic sign-off present
Default policy: human approval required before promotion.
## Distillation lanes
Memory promotion pipeline:
- lane A: raw traces (high-volume, short TTL)
- lane B: episodic summaries (candidate lessons)
- lane C: authoritative policy memory (only repeated winners)
Promotion rule:
- lane B -> C requires repeated validated wins and no safety regression.
## Conflict and rollback
- No silent replacement of authoritative policy.
- Every promotion must include rollback reference.
- Rollback updates episode state to `rolled_back` and links reason/evidence.
## Schemas
- `core/schemas/evolution/evolution_episode.json`
- `core/schemas/evolution/mutation.json`
- `core/schemas/evolution/evaluation_report.json`
- `core/schemas/evolution/gate_policy.json`
## Starter CLI model
Current command surface (implemented):
- `cognitive-os evolve run`
- `cognitive-os evolve report <episode_id>`
- `cognitive-os evolve promote <episode_id>`
- `cognitive-os evolve rollback <episode_id>`
Authoritative command:
- `cognitive-os evolve ...`
