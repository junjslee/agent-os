# 📒 Cognitive System Playbook

## 🏛️ Operating Thesis: The Mind-Vessel Duality

`episteme` runs on a dual-system architecture:
- **Cognitive System (The Soul)**: Governs *how to think*. Improves decision quality and reasoning integrity through formal protocols — the Reasoning Surface, the facts/inferences/preferences distinction, the hypothesis → test → update cycle, the failure-mode taxonomy applied per decision.
- **Execution System (The Vessel)**: Governs *how to act*. Improves delivery reliability and verification discipline through deterministic workflows and enforced preconditions.

**Design Rule**:
> Cognition without Execution is abstract theory.
> Execution without Cognition is a brittle machine.

**What is product, what is mechanism.** The product is the Cognitive System — the framework that forces an agent to separate facts from inferences, name unknowns it would prefer to hide, declare what would prove it wrong, and audit its own direction against named failure modes. The file-system-level blocker that exits `2` when a high-impact op arrives without a valid Reasoning Surface is **not the product**. It is the uncompromising enforcer that keeps the cognitive framework from being skipped under deadline pressure, fluent confidence, or scope creep. A prompt-only version of this framework degrades to advice the moment pressure rises; the kernel exists so advice becomes precondition. Read every section below with this ordering: cognitive discipline is what is being delivered; enforcement is how it is kept intact.

**What episteme is and is not — the BYOS stance.** episteme is a cognitive and execution governance kernel. It is not a skill provider, tool provider, or agent framework. The kernel does not give agents capabilities; it intercepts state mutation at the point of action and enforces the Reasoning Surface regardless of which external tool, MCP server, or agent framework generated the command. A `kubectl apply` from Claude Code, a `terraform plan` from a Cursor agent, a `gh pr merge` from a home-grown MCP server — the kernel does not care about provenance. It intercepts the mutation and enforces the blueprint-shaped cognitive contract before the mutation lands. This is the **BYOS (bring-your-own-skill) stance**: the ecosystem provides the skills, the kernel provides the episteme. See `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § "What episteme is — and what it is not" for the architectural consequences (no tool-specific validation paths, no prescriptive tool-usage guidance in blueprints).

**The deeper problem the kernel exists to address.** An LLM is an auto-regressive pattern engine. It does not predict the consequences of its actions; it predicts the next token of a plausible-sounding plan. When two sources disagree, it defaults to the statistically-central answer — Doxa — and presents it with the same fluency it presents a verified fact. Any agentic system built on this substrate inherits the failure: the agent cannot plan because it cannot model what its action will cause. Every visible failure mode this kernel addresses — fluent-vacuous reasoning, hallucinated dependency resolutions, confidently-wrong irreversible ops, retroactive memory distortion — is a surface expression of that single root cause.

**The second face of the same failure — source-chaos and context-fit.** The operator problem has a second shape. Searching the internet, reading docs, asking different teammates: Source A says "do it this way"; Source B says "do it that way." The agent cannot tell which source fits THIS operator's context (THIS project's tooling, THIS team's constraints, THIS op-class's history) because *fit* is a causal-world-model judgment, not a pattern-match over token frequency. So the agent defaults to the statistically-central synthesis — a plausible-sounding Doxa that fits no specific context and actively misleads. Multiple cases contain a hidden protocol — *"in context X, you must do Y"* — but extracting that protocol requires modeling WHY the sources conflict rather than averaging them. The kernel's job is to force the extraction AND to commit the extracted protocol to a tamper-evident framework that accumulates over time AND to surface accumulated protocols proactively as operator guidance on future matching contexts.

**What the Reasoning Surface actually is.** The Reasoning Surface is the structural interface through which the kernel forces the agent to do three things the substrate cannot do natively: (1) construct an auditable causal-consequence model of a specific action before the action is permitted; (2) synthesize context-dependent protocols from conflicting sources and commit them to a hash-chained framework; (3) actively guide the operator using accumulated protocols at the point of future decisions. It is the mechanical scaffold of causal reasoning, protocol synthesis, and active guidance, grafted onto an engine that cannot perform any of the three natively. See `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § "Pillar 3 · Framework Synthesis & Active Guidance" for the synthesis/guidance arm.

## 2) Memory architecture (authority boundaries)

Three memory classes with strict authority:

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

## 🧠 3) Cognitive Reasoning Protocol (Mandatory)

Before committing to any major path, project your reasoning onto the **Reasoning Surface**:

- **Knowns**: Verified, non-negotiable facts.
- **Unknowns**: Risks, missing data, or "black boxes."
- **Assumptions**: The logical leaps we are currently making.
- **Disconfirmation**: One specific piece of evidence that would prove our reasoning is wrong.

**The four-field surface is the fallback — not the universal shape.** At v1.0 RC and later, the Reasoning Surface is scenario-polymorphic. When a named scenario fires — conflicting-source resolution, removal of an unexplained constraint, irreversible or high-blast-radius operation — the kernel selects a **Cognitive Blueprint** whose required fields are the causal decomposition specific to that scenario's known failure class. The three v1.0 RC blueprints are **Axiomatic Judgment** (conflicting sources → requires per-source believability weighting, decision rule, per-source fail condition), **Fence Reconstruction** (constraint removal → requires origin evidence, removal-consequence prediction, rollback path), and **Consequence Chain** (irreversible ops → requires first-order and second-order effects, failure-mode inversion, base-rate reference, margin of safety). A fourth catchall — **Unclassified High-Impact** — applies the Consequence Chain fields to any high-impact op that doesn't match a named scenario, so blueprint-absence cannot be used to evade scaffolding. The blueprint is not optional and not generic; it is the structural scaffold through which the agent is forced to build a consequence model before acting. See `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § "Pillar 1 · Cognitive Blueprints" for selection logic, per-blueprint required fields, and the governance discipline on blueprint additions.

**Tamper-evident episodic record.** At v1.0 RC, every episodic-tier entry, every pending-contract record, and every framework protocol entry is written as an append-only hash chain (SHA-256 `prev_hash` + `entry_hash` + chain-head at `~/.episteme/state/chain_head.json`). Retroactive edits break the chain and are detected by Phase 12's audit precondition. This closes a previously-unaddressed memory-poisoning class: an agent or adversary with filesystem access cannot quietly rewrite its own history to pretend it predicted a consequence it actually missed, nor invent a framework protocol after the fact to "guide" the operator toward a convenient conclusion. See `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § "Pillar 2 · Append-Only Hash Chain" for scope (episodic tier + pending contracts + framework protocols only at RC; expansion is a later governance decision) and the chain-reset protocol.

**Framework synthesis and active guidance.** Resolving a blueprint at one decision is not the end of the cognitive work — it is the start of a durable extraction. Synthesis-capable blueprints (primarily Axiomatic Judgment, secondarily Fence Reconstruction) write a **context-indexed protocol** to `~/.episteme/framework/protocols.jsonl` on every resolution: the distilled *"in context X, do Y because Z"* rule extracted from the conflict or constraint-removal, hash-chained so it cannot be silently rewritten. On future PreToolUse events, the kernel canonicalizes the incoming op's context signature and queries the framework; matching protocols surface as stderr advisory (one per op, highest-believability match) before blueprint enforcement runs. SessionStart presents a digest of protocols synthesized since the last session; `episteme guide [--context <keyword>]` lists matching protocols on demand. Guidance is advisory, never blocking — the framework informs; blueprints enforce. See `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § "Pillar 3 · Framework Synthesis & Active Guidance" for the loop, risks (Framework-as-Doxa, guidance-loop gaming, stale protocols), and why the advisory posture is load-bearing (collapsing guidance into enforcement would produce a feedback loop where the kernel enforces its own synthesis against the operator).

**Why this protocol exists -- Kahneman's Dual-Process Theory**: AI agents run almost entirely on
System 1: fast, automatic, pattern-matching reasoning that produces fluent, plausible-sounding
answers whether or not they are correct. The training signal that makes agents useful -- rewarding
confident, coherent responses -- also makes them systematically prone to specific failure modes.

The Reasoning Surface is a System 2 forcing function. Each field blocks a named System 1 failure:
- **Unknowns field** blocks WYSIATI (What You See Is All There Is): reasoning only from what is
  present in context, never flagging what is missing. A blank Unknowns section means the agent
  has not looked for what it does not know.
- **Core Question** blocks question substitution: silently replacing the hard real question with
  a nearby easier one and answering that instead. Name the actual question.
- **Disconfirmation** blocks anchoring: the first framing encountered dominates and later
  information adjusts insufficiently. Force an active falsification attempt before committing.
- **Facts / Inferences / Preferences separation** blocks narrative fallacy: sparse data assembled
  into a coherent causal story that feels discovered but was constructed.

**Radical Transparency (Dalio)**: Surface uncertainty even when it makes the agent appear less
capable. Believability-weighting applies when inputs conflict: weight by demonstrated track record,
not authority, fluency, or volume. The most confident voice is often the most dangerous to follow
uncritically.

**Mental Model Lattice (Munger)**: Every model is a lens with a built-in blind spot. For high-impact
or irreversible decisions, apply at least 2 models from different domains. Convergence = proceed.
Conflict = mandatory investigation, not a tiebreaker. Default lattice: inversion (what would make
this fail?), second-order effects (what happens downstream?), base rates (what does the historical
distribution say?), margin of safety (what buffer if assumptions slip?).

## 🎭 4) Manifestation Loop (Workflow)

**This loop is an OODA loop (Boyd)**: Observe -> Orient -> Decide -> Act. episteme is the
**Orientation infrastructure** -- the system that shapes the agent's worldview before observation
even begins. Orientation (mental models, memory, reasoning protocols) is the most critical step
because it filters what gets observed and how decisions are framed. Faster loop iterations beat
stronger single iterations: prefer reversible, small actions that close the loop quickly over
large, confident, slow bets.

1. **Awareness** [Observe]: Ingest the **Cognitive Harness** (`HARNESS.md`) and state of the world (`PROGRESS.md`).
2. **Projection** [Orient]: Map the logic into `docs/PLAN.md` with explicit verification checkpoints.
3. **Manifestation** [Decide + Act]: Implement the smallest reversible increment.
4. **Verification** [Observe again]: Execute deterministic quality checks (tests, lint, audit).
5. **Synchronization** [Orient again]: Update memory and hand off with a "So-What Now?" summary.

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

Treat Hermes as adaptive runtime, episteme as authoritative governance.

Pattern:
- Hermes memory/skills = fast adaptation lane
- episteme memory/contracts = authoritative lane
- sync + promotion = bridge lane

Rule:
- learn locally fast
- promote durable lessons slowly and explicitly

## 7) Adapter conformance checklist

For each runtime adapter (Claude/Codex/opencode/Hermes), verify:
- authoritative files are readable from the runtime
- runtime does not override authority boundaries
- required safety behavior is active
- handoff docs are honored
- sync reproduces deterministic state

If any fail, the adapter is non-conformant and must be fixed before trusting automation.

## 8) Practical anti-drift controls

- Keep generated artifacts in `.generated/` and mark them non-authoritative until compiled
- Use deterministic commands for bootstrap/setup
- Keep command surface single-name (`episteme`)
- Run CI on every PR/push
- Record high-impact decisions in `docs/DECISION_STORY.md`

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
- collect and promote repeated winning patterns into authoritative memory/skills

Week 4:
- publish conformance report + evolution outcomes
- tighten gates based on observed regressions

---

This playbook is intentionally opinionated.
If a future change weakens authority boundaries, auditability, or rollback safety, reject it.
