# Workflow Policy

Operator-defined policy derived from top-down cognitive principles. This file is the operational counterpart to `cognitive_profile.md` — cognitive defaults enforced as workflow rules. Edit to match your own working style; the section structure is the canonical schema.

## Standard Flow

1. Frame
2. Decompose
3. Execute
4. Verify
5. Handoff

## Stage Definitions

1) **Frame**
- Define objective, success metric, and scope boundary.
- Declare one Core Question for this cycle.
- Identify uncomfortable friction (anomaly/inefficiency/uncomfortable truth) driving the work.
- Build a distinction map before planning:
  - known facts
  - unknowns
  - assumptions
  - preferences
- Declare constraint regime:
  - allowed actions
  - forbidden actions
  - cost/risk limits
- Classify decision type: reversible vs irreversible.

2) **Decompose**
- Convert non-linear context into explicit tasks via divide-and-conquer partitioning.
- Translate big `why` questions into operational `how` mappings (what can be measured or mapped now).
- For major implementation decisions, state method choice explicitly:
  - chosen method
  - viable alternatives considered
  - why this method was selected for this context
  - how it ties back to the abstract purpose (the governing intent)
- Produce smallest useful next action.
- For high-impact work, include at least 2 options and trade-offs.
- For each chosen action, include a short because-chain:
  - observed signal → inferred cause/constraint → decision.
- State a working hypothesis for the selected path (thinking as a bet).

3) **Execute**
- Run one bounded lane per task owner.
- Prefer reversible moves first.
- Record assumptions when data is incomplete.

4) **Verify**
- Validate against success metric, not effort spent.
- Run relevant tests/checks before completion.
- Distinguish proven facts from inferred conclusions.
- Explicitly mark residual unknowns at handoff time.
- Evaluate hypothesis result: validated, refined, or invalidated.

5) **Handoff**
- Update authoritative docs (`docs/PLAN.md`, `docs/PROGRESS.md`, `docs/NEXT_STEPS.md`).
- Capture unresolved risks and exact next action.

## Signal-over-Noise Rules

Before major action, answer briefly:

1. What is the signal (objective evidence)?
2. What is the noise (fear/regret/status-pressure/speculation)?
3. What action is justified by signal only?
4. What evidence would disconfirm the current plan?
5. So what is the concrete cost of remaining ignorant here?

If these cannot be answered, do not escalate execution scope.

## Risk and Autonomy Policy

- Reversible + low-impact: autonomous execution allowed.
- Irreversible, costly, or high-blast-radius: require explicit review checkpoint.
- No unattended code-writing-to-merge loops without explicit approval.

For paid hosted-model runs, estimate cost before triggering and ask:
> `acknowledge the cost and proceed? [y/n]`

## Project Memory Contract

Authoritative truth lives in project docs and repo policy files:

- `docs/REQUIREMENTS.md` — what is being built.
- `docs/PLAN.md` — staged execution.
- `docs/PROGRESS.md` — completed work and decisions.
- `docs/NEXT_STEPS.md` — next-session handoff.
- `docs/RUN_CONTEXT.md` — runtime assumptions, execution profiles, API env vars.

Tool-native memory (Claude / Hermes / Codex / Cursor) is acceleration only — never the source of truth.

## Parallelism Policy

- One bounded task per worktree/lane.
- One owner per lane.
- Independent review for high-impact changes.

## Local Integration

After changing global memory files (this file, `operator_profile.md`, `cognitive_profile.md`, `agent_feedback.md`, etc.):

1. `episteme sync`
2. `episteme doctor`
