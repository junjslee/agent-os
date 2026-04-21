# Design — Causal-Consequence Scaffolding & Protocol Synthesis — v1.0 RC

Status: **approved (reframed, third pass)** · Drafted 2026-04-21 · Approved 2026-04-21 · Reframed 2026-04-21 · Second-pass reframe 2026-04-21 · Third-pass reframe 2026-04-21 · Scope: v1.0 RC upgrade of the Reasoning Surface from syntactic enforcement to causal-consequence scaffolding, protocol synthesis, active guidance, **and continuous architectural self-maintenance** — grafting four things onto an auto-regressive engine that cannot perform any of them natively: a causal world-model interface, a context-indexed thinking framework that synthesizes context-dependent protocols from conflicting sources, an active-guidance loop that uses those protocols to proactively steer the operator, and a cascade-escalation loop that keeps the system's own understanding of itself coherent as the codebase evolves under its own edits.

**Approval record.** Maintainer approved the eight-layer architecture on 2026-04-21 and, later the same day, approved three successive reframes:

- **First pass (2026-04-21, morning):** re-anchored the spec from "semantic governance / anti-vapor defense" to "structural forcing function for causal-consequence modeling." Added Pillar 1 (Cognitive Blueprints), Pillar 2 (Append-Only Hash Chain), absorbed the BYOS / skill-agnostic stance into the preamble, and expanded the CP plan from 6 to 8.
- **Second pass (2026-04-21, later):** added the protocol-synthesis axis. The honest operator problem is not only "agent can't predict consequences" but also "operator can't distinguish context-fit know-how from statistical Doxa in a sea of conflicting sources." Added Pillar 3 (Framework Synthesis & Active Guidance), extended Axiomatic Judgment with synthesis fields, renamed the subtitle to *Causal-Consequence Scaffolding & Protocol Synthesis — v1.0 RC*, and expanded the CP plan from 8 to 9.
- **Third pass (2026-04-21, evening):** enshrined the *ultimate why* in the preamble — the kernel exists because an operator drowning in conflicting sources cannot, and a stock LLM will not, distil context-fit protocols from multi-case chaos, evolve those protocols as a living thinking framework, or keep a system coherent as it edits itself. Promoted the prior "Blueprint D · Unclassified High-Impact (catchall)" to a **named, load-bearing Blueprint D · Architectural Cascade & Escalation** covering three cognitive moves the framework forces on every emergent flaw: patch-vs-refactor evaluation, symmetric cascade synchronization across the full blast radius (CLI / config / schemas / visualizations / docs / external surfaces), and continuous-digging-and-logging of adjacent discoveries back into the hash-chained framework. The Goodhart closer for unclassified high-impact ops survives as a **generic maximum-rigor fallback** (Consequence-Chain-shaped) rather than as a blueprint. Expanded the CP plan from 9 to 10 (CP10 = Blueprint D scaffolding + cascade-detector + deferred-discovery logging).

None of the three reframes retract prior approvals — the eight layers, the three orthogonal pairs (L2+L3, L4+L6, L5+L7), the < 100 ms hot-path ceiling, and the 10% → 5% sample-rate schedule all stand. The reframes add pillars, blueprints, and realignments; they do not subtract countermeasures.

The six prior decisions carry forward unchanged:

1. **Layer 3 entity extraction → REGEX.** No LLM in the hot path. Regex is FP-averse and predictable; an LLM extractor introduces its own Goodhart surface and breaks the < 100 ms hot-path budget.
2. **Layer 4 required-for-highest-impact list.** `terraform apply`, `kubectl apply` against any context matching `prod`/`production`, `alembic upgrade`, `prisma migrate deploy`, `gh release create`. Advisory at v1.0.0-rc1, required at v1.0.1.
3. **Layer 6 storage and TTL.** `~/.episteme/state/pending_contracts.jsonl` with TTL = max declared window across open contracts. Cleanup at SessionStart.
4. **Layer 8 sample rate.** 10% for the first 30 days (calendar-from-install), then decay to 5%. Per-project override via `.episteme/spot_check_rate`.
5. **Hot-path latency.** Layers 2–4 combined < 100 ms p95 (HARD ceiling). Per-layer 50 ms p95 breach gates behind a `derived_knobs.json` toggle. Repeated breach is a governance event — name it, do not silently tune.
6. **Phase 12 + hot-path coexistence.** Both layers ship and run together. Retrospective distribution signal is structurally different from per-surface write-time signal.

Implementation proceeds against this reframed spec. Any deviation surfaces as a spec-amendment request before code lands. Per the Phase 12 discipline: any later change that relaxes a load-bearing countermeasure — the eight layers, the three orthogonal pairs, the < 100 ms ceiling, the sample-rate schedule, **the Cognitive Blueprint registry (four named blueprints: Axiomatic Judgment, Fence Reconstruction, Consequence Chain, Architectural Cascade & Escalation), the generic maximum-rigor fallback, the hash-chain scope, the Framework Synthesis substrate, the active-guidance loop, the cascade-synchronization discipline**, the BYOS stance — is a governance change, not an implementation tweak.

**Implementation timing.** v0.11.0 has been tagged and shipped (2026-04-21). The v1.0 RC cycle is open. CP1 is the next executable unit once this second-pass reframe is registered in the authoritative docs (`docs/PLAN.md`, `docs/PROGRESS.md`, `docs/NEXT_STEPS.md`).

## Why this exists

An LLM is an auto-regressive pattern engine. It does not predict the consequences of its actions; it predicts the next token of a plausible-sounding plan. When two sources disagree, it defaults to the statistically-central answer — the Doxa — and presents it with the same fluency it presents a verified fact. Any agentic system built on this substrate inherits the failure: the agent cannot plan because it cannot model what its action will cause.

Every visible failure mode this kernel addresses — fluent-vacuous reasoning, hallucinated dependency resolutions, confidently-wrong irreversible ops, retroactive memory distortion — is a surface expression of that single root cause. v0.11.0's hot-path validator (`core/hooks/reasoning_surface_guard.py`) catches the most trivial expression (lazy-token blocklist + 15-character minimum + regex pattern matching). It does not catch the underlying incapacity.

A sufficiently-aware agent defeats v0.11.0's gate with fluent-vacuous content that contains no banned tokens, exceeds the length threshold, looks like a falsifiable hypothesis, and commits to nothing testable. Five real examples that pass today's gate:

1. *"if any unforeseen issue arises during deployment we will reassess our approach"*
2. *"the migration may produce unexpected behavior if edge cases are encountered"*
3. *"if the build process exhibits anomalous behavior we should investigate before proceeding"*
4. *"should monitoring detect concerning patterns we will pause and evaluate next steps"*
5. *"if results diverge from expectations we will return to first principles"*

Each is over 60 characters, contains no banned tokens, has an `if`/`should`-clause, and looks like reasoning. None names an observable. None commits to a threshold. None could be falsified by a specific event. The kernel passes them. The operator's praxis fails them — but the diagnostic misnames the disease. The fluency is not the problem. The absence of a causal-consequence model behind the fluency is the problem.

**The second face of the same failure — source-chaos and context-fit.** An operator searching the internet or reading docs faces a second expression of the same root cause. Source A says "do it this way"; Source B says "do it that way." The agent, being an auto-regressive engine, cannot tell which source fits THIS operator's context — THIS project's tooling, THIS team's constraints, THIS op-class's history — because *fit* is a causal-world-model judgment, not a pattern-match over token frequency. So the agent defaults to the statistically-central synthesis of both sources — a plausible-sounding Doxa that fits no specific context and actively misleads the operator about what to do. Multiple cases contain a hidden protocol — "in context X, you must do Y" — but extracting that protocol requires modeling WHY the sources conflict (what feature of the context tips the answer) rather than averaging them. The kernel's job is to force the extraction.

**The ultimate why — information overload, context-fit, living framework, active guidance, continuous self-maintenance.** The operator's lived problem, stated plainly: *"There is so much information in the world. When I search the internet or look at docs, how do I distinguish what is actually correct or what specifically fits MY context? Source A says 'do it this way', Source B says 'do it that way'. There is an underlying know-how or protocol hidden in these multiple cases. I want a system that systematically breaks this chaos down, understands WHY the sources conflict, creates a thinking framework that can continuously update itself, and then uses the insights generated from this framework to actively GUIDE me in the right direction."* This is the kernel's ultimate governing intent. A causal-consequence scaffold is necessary but not sufficient — a per-action guardrail cannot by itself (a) extract a context-fit protocol from multi-case source chaos, (b) evolve that protocol as a living artifact over time, (c) surface it proactively at the point of the next matching decision, or (d) keep the system's own understanding of itself coherent as the agent edits the system. The v1.0 RC architecture binds all four jobs to a single structural scaffold: scenario-polymorphic blueprints force the per-action decomposition; synthesis-capable blueprints extract and hash-chain the context-fit protocol; the active-guidance loop surfaces it again at future decisions; and Blueprint D · Architectural Cascade & Escalation fires whenever emergent flaws or architectural drift are discovered mid-work, forcing patch-vs-refactor evaluation, symmetric cascade synchronization across the full blast radius, and continuous digging + logging of adjacent discoveries back into the same hash-chained framework. Protocol synthesis, active guidance, and continuous self-maintenance are not three features bolted onto a scaffold — they are three arms of the same mechanism, anchored by the same hash-chained framework, operating at three different scopes (per-decision, per-operator-history, per-system-evolution).

**What this spec is.** The Reasoning Surface is not a guardrail against bad output. It is the structural interface through which the kernel forces the agent to do four things the substrate cannot do natively: (1) **construct an auditable causal model** of a specific action before the action is permitted; (2) **synthesize context-dependent protocols** from conflicting sources — distill WHY they conflict, extract the "in context X, do Y" rule that fits this operator's context, and commit it to a tamper-evident framework that accumulates over time; (3) **actively guide the operator** using the accumulated framework, proactively surfacing context-match protocols at the point of future decisions rather than waiting to be asked; (4) **continuously self-maintain** the whole system — when flaws, deprecations, config gaps, or core-logic drift are discovered mid-work, force the agent to evaluate patch-vs-refactor honestly, map and synchronize the full blast radius of any change (CLI, config, schemas, visualizations, docs, external surfaces), and log adjacent discoveries back into the hash chain so the framework's self-model sharpens with every pass. The eight-layer architecture plus three pillars plus the four-blueprint registry is the mechanical scaffold for all four, grafted onto an engine that cannot perform any of them natively.

**The honest epistemic claim.** The scaffold does not make an LLM capable of causal reasoning. It makes it cheaper for the agent to perform genuine decomposition than to fake decomposition at the granularity the scaffold requires. Every layer is evaluated against that claim — not against a cheating-impossible claim. There is no uncheatable protocol. There is a protocol whose cheat-cost exceeds its honesty-cost by a factor that widens the more scaffolding is in place.

Phase 12 catches some of this retrospectively — Axis A's S2 fire-condition classifier flags the vapor pattern. But the audit fires after the action lands. The hot path is still where the causal model must be constructed. v1.0 RC is the upgrade that makes that construction mandatory, protocol-specific, and tamper-evident.

## What episteme is — and what it is not

**episteme is a cognitive and execution governance kernel. It is not a skill provider, tool provider, or agent framework.** The kernel does not give agents capabilities; it intercepts state mutation at the point of action and enforces the Reasoning Surface regardless of which external tool, MCP server, or agent framework generated the command. A `kubectl apply` from Claude Code, a `terraform plan` from a Cursor agent, a `gh pr merge` from a home-grown MCP server — the kernel does not care about provenance. It intercepts the mutation and enforces the blueprint-shaped cognitive contract before the mutation lands.

This is the **BYOS (bring-your-own-skill) stance.** The ecosystem produces skills and tools at an accelerating pace; the kernel deliberately does not compete on that axis. It owns a narrower and structurally deeper surface: the moment at which a proposed action meets reality. Whatever the tool, whatever the prompt chain, whatever the model — state mutation passes through the Reasoning Surface, or it is refused.

Two consequences of this stance the rest of the spec depends on:

- **No tool-specific code paths in validation logic.** Layers 2 through 8 operate on the surface + the pending op, not on the tool that produced them. A new skill provider integrates by having its tool calls intercepted; no adapter work is required on the kernel side.
- **No prescriptive "how to use tool X" guidance in the blueprints.** Blueprints specify required causal decomposition ("what would break if this constraint is removed?"), not tool-specific invocation patterns. An agent using `sed` and an agent using an LSP-aware refactor tool satisfy the same blueprint differently — both must satisfy it.

The kernel provides the episteme. The ecosystem provides the skills.

## Core question

*What structural protocol, when enforced at the point of state mutation, forces an LLM to (a) generate an auditable causal-consequence model specific enough to be retrospectively falsified and tamper-evident after the fact, (b) synthesize context-dependent protocols from conflicting sources into a tamper-evident framework that accumulates over time, (c) proactively surface those protocols as operator guidance at the point of future decisions, and (d) keep the system's own self-model coherent as the system edits itself — by evaluating patch-vs-refactor honestly, synchronizing cascading changes across the full blast radius, and logging adjacent discoveries back into the same hash-chained framework?*

Five sub-questions:

1. **Protocol specificity.** Is a single generic surface schema sufficient, or does the protocol need to mutate its required fields based on the causal structure of the scenario?
2. **Memory integrity.** How does the kernel know its own retrospective record — and its accumulating protocol framework — is honest, given that the agent has filesystem access to the state directory?
3. **Synthesis and guidance.** How does a resolved conflict at one decision point become a durable, context-indexed protocol that shapes the next decision, without silently collapsing into the same Doxa the scaffold was built to resist?
4. **Cascade discipline.** When the agent discovers a flaw, vulnerability, stale artifact, or core-logic drift mid-work, what structural check forces it to (a) evaluate patch-vs-refactor instead of defaulting to the cheapest local patch, (b) enumerate and synchronize the full blast radius (CLI / config / schemas / visualizations / docs / external surfaces), and (c) log adjacent discoveries so the framework's self-model sharpens over time rather than rotting?
5. **Cost discipline.** What ships in v1.0 RC at acceptable hot-path latency / compute / false-positive cost, and what defers to v1.0.x or v1.1?

## The Goodhart threat, applied to the scaffold itself

Phase 12 named Goodhart at the *audit* level. The prior v1.0 RC framing named it at the *validator* level. The reframed thesis makes the threat more legible: any fixed decomposition protocol, once known, is a target the agent can optimize for. A sufficiently-exposed blueprint becomes a form to fill rather than a model to build.

**There is no single uncheatable protocol within the current paradigm.** The defense is the composition — multiple scaffolds whose evasion strategies are mutually inconsistent, plus an integrity layer (hash chain) that makes retroactive cheat-covering detectable, plus an operator ground-truth layer (spot-check) that cannot be predicted away.

This is the spiderweb metaphor working as intended. A single thread snaps; a web holds.

## Architecture — scaffold-in-depth across orthogonal gaming costs

Eight scaffolding layers, designed so evasion strategies in adjacent layers conflict. v1.0 RC ships layers 1–4 + 6 + 8; layers 5 and 7 defer to v1.1 on infrastructure-cost grounds.

```
                      ┌─── HOT PATH (state-mutation intercept, blocking) ───┐
  Layer 1  syntactic blocklist + length          [SHIPS — current]
  Layer 2  structural specificity classifier     [SHIPS v1.0 RC — blueprint-aware]
  Layer 3  contextual grounding (project-real entities)  [SHIPS v1.0 RC — blueprint-aware entity set]
  Layer 4  falsification trace (executable verification) [SHIPS v1.0 RC — blueprint-shaped]
  Layer 5  embedding-based vapor scoring          [DEFERRED v1.1 — infra cost]
                      └─── RETROSPECTIVE / async ─┘
  Layer 6  time-bound disconfirmation contract    [SHIPS v1.0 RC — extends Phase 12; hash-chained]
  Layer 7  adversarial co-validator (second LLM)  [DEFERRED v1.1 — compute cost]
  Layer 8  operator spot-check sampling           [SHIPS v1.0 RC — blueprint-prioritized]
```

Three cross-cutting pillars sit above the layer stack and change what the layers validate (and what the kernel produces as output):

- **Pillar 1 · Cognitive Blueprints** — scenario-polymorphic surface schemas. Selected at the hot-path entry; shape the required fields in Layers 2 / 3 / 4 / 6 / 8. Four named blueprints (A Axiomatic Judgment, B Fence Reconstruction, C Consequence Chain, D Architectural Cascade & Escalation) plus a generic maximum-rigor fallback for blueprint-absence evasion. Blueprint D is the engine of the kernel's continuous self-maintenance axis — see *Ultimate Why* preamble.
- **Pillar 2 · Append-Only Hash Chain** — tamper-evident episodic record. Binds Layer 4's write-time prediction to Layer 6's retrospective audit, binds every synthesized protocol to its write-time context, and binds every deferred-discovery entry to the system-evolution log Blueprint D writes into.
- **Pillar 3 · Framework Synthesis & Active Guidance** — context-indexed protocol substrate written by synthesis-capable blueprints (A / B / D) and queried at future PreToolUse events. Turns resolved conflicts into durable operator-specific know-how at per-decision scope (Axiomatic), per-operator-history scope (Fence Reconstruction), and per-system-evolution scope (Architectural Cascade); surfaces matching protocols proactively as guidance at the next relevant decision.

The layers composed alone defend against evasion. Pillars 1 and 2 composed with the layers shift what "the layers are validating" from *surface shape* to *causal decomposition preserved against retroactive mutation*. Pillar 3 composed with the first two shifts what the kernel DOES — from "refuses bad actions" to "refuses bad actions AND extracts tacit know-how AND guides the operator with what it has extracted AND keeps the system's own self-model coherent as it edits itself."

## Pillar 1 · Cognitive Blueprints — scenario-polymorphic protocols

A surface with correctly-populated fields is not equivalent to a surface that carries causal-consequence prediction. v0.11.0's validator treats them as equivalent. v1.0 RC refuses to.

**The mechanism.** The Reasoning Surface schema becomes scenario-polymorphic. The generic four-field surface (`knowns`, `unknowns`, `assumptions`, `disconfirmation`) is the fallback. When a named scenario fires, the schema mutates to a **Cognitive Blueprint** whose fields are the causal decomposition specific to that scenario's known failure class. Layers 2, 3, 4, 6, and 8 validate against the blueprint's fields when one is selected; against the generic fields when none is.

**Selection logic.** A new component — `core/hooks/_scenario_detector.py` — runs at the top of the hot path (regex + entity triggers; budget: absorbed into Layer 2's 5 ms slot). It maps `(pending_op, surface_text, project_context)` to at most one blueprint. If none fires, the generic schema applies — zero regression for existing surfaces.

### Blueprint A · Axiomatic Judgment

*Scenario: conflicting-source resolution. Source A says X, Source B says Y; the agent must pick. Axiomatic Judgment is not only a decision protocol — it is the primary **Protocol Synthesis & User-Guidance engine** of the kernel (Pillar 3). Every firing must (a) distill why the sources conflict, (b) extract a context-dependent protocol that fits this operator's situation, (c) commit that protocol to the hash-chained framework so the system's understanding of "what fits this project" evolves, and (d) register a guidance-trigger so the protocol surfaces proactively on future matching contexts.*

Required fields (decision arm):

- `sources[]` with per-source `believability_weight` and rationale (demonstrated track record, not authority or fluency — the rationale must name an observable from the source's history)
- `conflict_axis` — what specifically disagrees (not "they conflict" but, e.g., "A claims the migration is reversible; B claims it is not")
- `decision_rule` — the named axiom being applied (e.g., "prefer reversible; prefer the source with recent-incident evidence over the source with theoretical completeness")
- `fail_condition_per_source` — the observable that would retroactively invalidate each source
- `fallback_if_both_wrong` — the irreversibility-bounded path if the decision rule produces a wrong answer

Required fields (synthesis arm — the "protocol synthesis" escalation):

- `conflict_cause` — the underlying axis on which the sources disagree, stated as a context feature (not "they conflict" but, e.g., *"A assumes a single-writer database; B assumes multi-writer. The conflict is not a matter of correctness but of context."*). Distilling the chaos.
- `context_signature` — the features of the current situation that fix which source applies here (project framework + operator profile axes + op-class + environment + team constraint). This is the "X" in "in context X, do Y." Stated concretely enough that a future context-match can be computed, not a vague description.
- `synthesized_protocol` — the extracted rule, stated generally enough to fire again on the next context-match: *"In context `<signature>`, apply `<decision_rule>` because the dominant axis of `<conflict_cause>` is resolved by `<feature>`."* This is the durable know-how the kernel extracts from the conflict; it is what transforms a one-off decision into accumulated framework.
- `framework_entry_ref` — pointer to the hash-chained framework record (`~/.episteme/framework/protocols.jsonl`) where the `synthesized_protocol` is committed. Written at PreToolUse success; hash-chained per Pillar 2.
- `guidance_trigger` — the context-match predicate that should cause this protocol to surface as proactive operator guidance on future ops. Typically a canonicalization of `context_signature`; keeps the matching predicate honest and auditable.

Hooks to Phase 12 Axis A (disconfirmation specificity), the believability-weighting rule named in `COGNITIVE_SYSTEM_PLAYBOOK.md` §3 (Dalio, Radical Transparency), and Pillar 3 (Framework Synthesis & Active Guidance). Full realization of the synthesis-arm fields is the v1.0.1 deliverable that ships alongside the first operator-visible `episteme guide` queries; the *structure* lands in v1.0 RC so CP5's Fence Reconstruction has a companion synthesis slot and can begin contributing protocols (constraint-safety know-how) even before Axiomatic Judgment's full realization.

### Blueprint B · Fence Reconstruction

*Scenario: removal or relaxation of an unexplained constraint. Maps to `fence_discipline` axis (operator profile: value 4, confidence inferred).*

Required fields:

- `constraint_identified` — pointer to the specific code / config / policy being removed (line-level precision)
- `origin_evidence` — git blame, doc reference, or incident record establishing **why** the constraint was imposed (not "unclear — probably legacy")
- `removal_consequence_prediction` — what breaks if the constraint is removed, named with an observable
- `reversibility_classification` — reversible (continue), irreversible (stop; escalate to Axiomatic Judgment blueprint)
- `rollback_path` — the concrete revert procedure if the prediction is wrong

Hooks to Phase 12 Axis C (fence_discipline). This is the first realized blueprint in v1.0 RC because it binds cleanly to an axis the kernel already enforces retrospectively — end-to-end example from scenario to selector to blueprint to validation to hash-chained record to Phase 12 audit.

### Blueprint C · Consequence Chain

*Scenario: irreversible or high-blast-radius operation — `terraform apply` against prod, `kubectl apply` against prod, `alembic upgrade`, `prisma migrate deploy`, `gh release create`.*

Required fields:

- `first_order_effect` with observable
- `second_order_effect` — what happens downstream of the immediate effect; named, not hand-waved
- `failure_mode_inversion` — what would cause this to fail; at least one named mode per consequence tier
- `base_rate_reference` — historical distribution of this op-class in this project (or in the operator's broader experience if project-local data is sparse)
- `margin_of_safety` — buffer if assumptions slip 30–50%; explicit statement of what becomes unacceptable at that slip

Hooks to the mental-model lattice in `COGNITIVE_SYSTEM_PLAYBOOK.md` §3 (Munger: inversion, second-order, base rates, margin of safety).

### Blueprint D · Architectural Cascade & Escalation

*Scenario: while working on one intended task, the agent discovers a flaw, vulnerability, stale/deprecated artifact, config gap, or evidence that core logic must change to preserve system coherence. Without a forcing function on this axis, the default behavior is to apply the cheapest local patch and silently leave a cascade of mismatched surfaces (renamed function with orphaned doc references, changed schema with unupdated CLI, refactored core with untouched visualizations). Each unrepaired cascade raises the cost of the next correct action — the codebase decays under its own edits. Blueprint D makes the cognitive cost of the cheap local patch visible at the moment of decision.*

This blueprint is the engine of the kernel's **continuous self-maintenance** axis (see Ultimate Why, preamble). It fires both when the agent is editing unrelated systems *and* when the agent is editing episteme itself — a kernel that does not satisfy Blueprint D when it edits its own architecture fails the dogfood test.

Required fields:

- `flaw_classification` — what kind of issue was discovered, named from a fixed vocabulary: `vulnerability`, `stale-artifact`, `config-gap`, `core-logic-misalignment`, `deprecated-dependency`, `doc-code-drift`, `schema-implementation-drift`. Unknown-shape discoveries route to `other` with a required free-text description (advisory, logged for Phase 12 vocabulary expansion).
- `posture_selected` — one of `patch` or `refactor`, each with a one-line rationale naming the axis of the decision (scope, reversibility, propagation cost, or risk of divergence).
- `patch_vs_refactor_evaluation` — **the cognitive check.** If `posture_selected = patch`, explicit statement of why refactor is NOT warranted: which blast-radius surfaces stay consistent without the refactor, and what would have to become true to force an escalation. If `refactor`, the same check in reverse — why localizing the fix would leave inconsistent state. Generic phrasing ("it's simpler") fails; the statement must name concrete surfaces.
- `blast_radius_map[]` — enumerated surfaces that must update symmetrically. The vocabulary covers at minimum: CLI commands, config files, JSON schemas, hook scripts, visualizations (SVG / Mermaid / PNG), doc prose, test fixtures, generated artifacts (MANIFEST, CHANGELOG), external-facing surfaces (README lede, marketplace listing, future marketing copy). Entries not applicable to the op must be named and marked `not-applicable` — silent omission is a Goodhart evasion and is rejected.
- `sync_plan[]` — concrete one-line atomic action per surface in `blast_radius_map`. `no change needed because <reason>` is valid. Entries missing a rationale are rejected.
- `deferred_discoveries[]` — adjacent gaps the agent uncovered mid-task but is not fixing in this pass. Each carries `(description, observable, log_only_rationale)`. Every entry is hash-chained into the framework as a `deferred_discovery` record immediately; Phase 12 audits the accumulated log for (a) frequency (which classes of discovery recur and suggest a structural issue) and (b) aging (how long discoveries sit before being promoted or triaged).

Hooks to (a) Munger's second-order thinking (blast radius = second-order effect), (b) Dalio's radical transparency (surface the cascade, don't hide it), (c) systems-thinking default from `COGNITIVE_SYSTEM_PLAYBOOK.md` Collaboration Stance ("preserve whole-system coherence, not local optimizations that break global intent"), and (d) fence_discipline (refactor-vs-patch is the "why was this constraint here" question asked about the posture itself).

Selector triggers (CP10, see *Implementation sequencing*):

- Proposed diff touches a schema file, policy file, or kernel doc without companion edits in doc / CLI / test / visualization surfaces that reference the changed entity (git-grep cross-reference check at scenario-detector time).
- Operator or agent uses `refactor`, `cleanup`, `rename`, `deprecate`, or `migrate` in the op context against a file path with ≥ 2 cross-surface references.
- Agent explicitly declares `flaw_classification` in the surface (self-escalation — always fires regardless of other signals).
- Proposed diff renames or deletes a symbol whose exported name appears in generated artifacts (MANIFEST.sha256, CHANGELOG.md).

Pillar 3 synthesis arm. On successful Blueprint D resolution (all blast-radius surfaces updated coherently within the declared window; no orphan-reference regression detected retrospectively), the blueprint emits a **context-specific cascade protocol** to the framework: *"In context `<project + subsystem + flaw_class>`, posture `<patch|refactor>` with blast-radius class `<surfaces>` resolved without divergence because `<observable>`."* Over time, the framework accumulates architectural know-how about *how this specific system cascades* — which renames actually propagate, which schema changes break visualizations, which doc sections rot when CLI flags change. This is the same synthesis loop Axiomatic Judgment and Fence Reconstruction ride on; Blueprint D writes at a different scope (system-architecture-level rather than per-op-decision-level).

### Generic maximum-rigor fallback (Goodhart closer)

*When no named blueprint (A / B / C / D) fires for a high-impact op, the kernel applies a **generic maximum-rigor schema** — the union of Consequence Chain's fields applicable to the op shape — rather than falling back to the generic four-field surface.* This is the Goodhart closer for blueprint-absence evasion: an agent cannot avoid blueprint enforcement by producing actions whose shape matches no named pattern, because the fallback is *at least as rigorous as* any single named blueprint. The fallback is not counted as a blueprint — it has no synthesis arm and does not emit framework protocols — but it preserves the write-time rigor that prevents "unclassified" ops from slipping through with only the generic four-field surface.

### Blueprint registry governance

Blueprints live at `core/blueprints/*.yaml` (one file per blueprint). Additions require a governance event with the same discipline as profile-axis changes: named failure class, audit evidence justifying the decomposition, operator sign-off. Phase 12 audits blueprint effectiveness quarterly — which blueprints fired, how often, with what retrospective-verification rate. Blueprints with sustained low bind-rate or low verification-rate are candidates for revision or retirement.

v1.0 RC ships **four named blueprints** plus a generic maximum-rigor fallback:

- Blueprint B (Fence Reconstruction) — full implementation end-to-end (selector → fields → L2/3/4 validation → hash-chained L6 record → framework protocol emission → Phase 12 audit input).
- Blueprint A (Axiomatic Judgment) — schema structure lands (decision arm + synthesis arm); selector can fire it; field-level validation advisory-only; skeleton protocol entries flow to the framework on firing.
- Blueprint C (Consequence Chain) — schema structure lands; field-level validation advisory-only.
- Blueprint D (Architectural Cascade & Escalation) — schema structure lands; selector fires on the four trigger classes above; `patch_vs_refactor_evaluation` + `blast_radius_map` + `sync_plan` validated structurally; `deferred_discoveries[]` committed to the hash-chained framework on every firing (this is operator-visible payoff even before full cascade-synchronization verification ships). Retrospective verification of sync-plan completeness lands in v1.0.1.
- Generic fallback — Consequence-Chain-shaped, applies to any high-impact op not matched by A / B / C / D.

Full realization of Axiomatic Judgment, Consequence Chain, and Blueprint D's retrospective sync-plan verification lands in v1.0.1 with audit data justifying final field shapes.

### How this reshapes the existing layers

| Layer | Pre-reframe behavior | Post-reframe behavior |
|---|---|---|
| L2 | Generic trigger+observable specificity | Required observables are the blueprint's fields; generic classifier applies only under fallback |
| L3 | Grep entities named in surface | Grep entities the **blueprint** names (Fence Reconstruction grounds `constraint_identified` to a real file; Consequence Chain grounds `base_rate_reference`) |
| L4 | Optional `verification_trace` | Blueprint-shaped — Consequence Chain requires verification per consequence tier; Axiomatic Judgment requires per-source check |
| L6 | Time-bound contract checker | Blueprint declares which fields are verifiable and in what window; hash-chained (pillar 2) |
| L8 | Random spot-check | Blueprint-fired surfaces sampled at a higher rate — operator calibration signal lands where the cognitive claim is largest |

### Risks named honestly

- **Blueprint proliferation.** Four named blueprints plus the generic maximum-rigor fallback is the budget. Governance-gated additions only. Quarterly Phase 12 review for retirement candidates.
- **Selector Goodhart.** An agent learning which inputs trigger the hardest blueprint will shape input to avoid it. Mitigations: the generic maximum-rigor fallback (at least as strict as any single named blueprint); operator spot-check includes a sample of scenario-selection outcomes; Phase 12 audits selection distribution drift.
- **Blueprint authoring cost.** Blueprints are grown from Phase 12 audit data, not imposed generically. v1.0 RC ships the four named above because each maps cleanly to a failure mode the kernel already names (Axiomatic → source-conflict Doxa; Fence → `fence_discipline`; Consequence Chain → irreversible-op incidents; Architectural Cascade → the self-editing coherence problem this project has already hit multiple times in its own repo).
- **Blueprint D cascade cost.** Forcing blast-radius enumeration on every cross-surface edit risks either (a) cascade-theater — the agent fills `blast_radius_map[]` with `not-applicable` entries to get past the gate, or (b) productivity collapse — the map is so honest every small rename takes an hour. Mitigations: Layer 3 grounds `blast_radius_map[]` entries against real file paths; Layer 8 spot-checks Blueprint D resolutions at 2× base rate with an explicit "cascade-theater vs real sync" verdict dimension; the selector fires only on the four trigger classes (not on every edit), so bounded-scope edits remain fast.

## Pillar 2 · Append-Only Hash Chain — episodic integrity

Layer 6's current design records pending contracts to `~/.episteme/state/pending_contracts.jsonl`. The file is mutable. An agent (or anyone with write access to the state directory) can edit past records to retroactively look like it predicted outcomes it actually missed. The prior honest-threat-model did not name this class. This pillar closes it.

**Mechanism.** Every episodic-tier record and every pending-contract record carries:

- `prev_hash` — SHA-256 of the previous entry's full serialized content
- `entry_hash` — SHA-256 of this entry's content (including `prev_hash`)
- Chain-head at `~/.episteme/state/chain_head.json`. In git-tracked projects, chain-head rotation commits provide a second tamper-evidence layer.

**Scope — v1.0 RC.** Episodic tier + pending contracts only. Explicitly out of scope: `derived_knobs.json` mutations, profile-axis changes, global memory files. The kernel proves the mechanism at the lowest-blast-radius surface first; expansion is a later governance decision.

**Properties this gives:**

- Retroactive mutation detected. Any edit breaks the chain downstream.
- Phase 12 audit gains a **precondition**: chain verifies, or audit refuses to proceed on the tampered range.
- L4 → L6 composition strengthens measurably. A faked `verification_trace` cannot be quietly repaired later — the original record's hash is frozen into its successor.

**Chain-reset protocol.** Legitimate state loss is real (disk failure, workstation rebuild). The kernel distinguishes:

- *Chain absent* (no `chain_head.json` or zero-entry log) — new install or legitimate reset. Genesis proceeds cleanly.
- *Chain broken* (hash mismatch mid-chain) — governance event. Operator is notified at SessionStart; audit refuses to proceed on the broken range until the operator issues a signed `chain_reset` event (itself chained into the new genesis).

**Hash choice.** SHA-256. The kernel is not defending against computational adversaries; it is defending against trivial tampering. Schema is versioned so a later upgrade to SHA-3 is a format bump, not a rewrite.

**Cost.** ~0.1 ms per hash. Writes happen async to the state dir (same as L6 today). Zero hot-path impact.

## Pillar 3 · Framework Synthesis & Active Guidance

The first two pillars govern per-action cognition: decompose causally, record tamper-evidently, audit retrospectively. They are necessary and insufficient. The honest operator problem has a second shape that a per-action scaffold cannot touch: **which source, which protocol, which "accepted wisdom" actually fits THIS project, THIS operator, THIS op-class?** A sea of internet docs, vendor guides, Stack Overflow posts, prior-team-lead folklore, and LLM-synthesized "best practice" produces a Doxa that is fluent everywhere and correct nowhere specific. Each conflicting pair of sources contains a hidden context-dependent protocol ("in context X, do Y"), but extracting it requires a causal model of what makes one source apply and another not — and the substrate cannot do that on its own.

Pillar 3 is the extraction and guidance loop. When a synthesis-capable blueprint fires and resolves — Axiomatic Judgment (source-conflict → context-fit decision protocol), Fence Reconstruction (constraint-removal → context-fit constraint-safety protocol), and Architectural Cascade & Escalation (emergent-flaw resolution → context-fit cascade protocol) — its output is not only the decision for the current op; it is a **context-indexed protocol entry** that lands in the framework and becomes queryable at future PreToolUse events. Over time, the framework accumulates the operator's lived tacit know-how across three scopes: per-decision (Axiomatic Judgment), per-operator-history (Fence Reconstruction), and per-system-evolution (Architectural Cascade & Escalation) — all made explicit, hash-chained, and auditable.

**Three outputs per synthesis firing:**

1. **Distillation.** The blueprint forces the agent to name *why* sources conflict (`conflict_cause`) and what features of the current situation select between them (`context_signature`). This is the decomposition the kernel exists to force; without it, the "decision" degrades back into averaged Doxa.
2. **Framework update.** The `synthesized_protocol` is committed to `~/.episteme/framework/protocols.jsonl` — append-only, hash-chained per Pillar 2, indexed by `context_signature` and `guidance_trigger`. The framework is not a cache; it is the durable artifact of synthesis across the operator's working history.
3. **Active guidance.** On future PreToolUse events, the kernel canonicalizes the incoming op's context signature and queries the framework. Matching protocols are surfaced to the operator (and the agent) as stderr advisory *before* blueprint enforcement runs — informing the decision without blocking it. At SessionStart, protocols synthesized since the last session are presented in a digest.

**Substrate — what ships in v1.0 RC.**

- `core/hooks/_framework.py` — read/write access to `~/.episteme/framework/protocols.jsonl`. Hash-chained using the same mechanism as Pillar 2 (shared implementation; single code path for SHA-256 `prev_hash` / `entry_hash` / chain-head verification).
- `core/hooks/_context_signature.py` — canonicalization of `(project_fingerprint, operator_profile_axes, op_class, environment)` into a signature string suitable for exact-or-substring query. Regex + entity hashing, same FP-averse discipline as Layer 3.
- **Query at PreToolUse** — after scenario detection, before blueprint enforcement, query the framework by the incoming op's context signature. Matches emit one stderr advisory line per match: *"Framework · context-match protocol: `<synthesized_protocol>` (synthesized <date> from `<source-conflict-summary>`)"*. Advisory only — never blocking. Cost budget: absorbed into the scenario detector's 5 ms slot.
- **SessionStart digest** — *"N protocols synthesized since last session. Review with `episteme guide --since last`."* Zero hot-path cost.
- **`episteme guide` CLI** — v1.0 RC ships a minimal version: query by context keyword, list matching protocols, show synthesis provenance. Rich interactive query and protocol revision are v1.0.1 deliverables.

**Scope — what synthesis-capable blueprints actually write in v1.0 RC.**

- **Axiomatic Judgment — structure only.** Full synthesis-field enforcement is v1.0.1 alongside the blueprint's full realization. In RC the framework receives skeleton protocol entries from Axiomatic Judgment firings; rich `conflict_cause` / `context_signature` / `synthesized_protocol` content lands when the blueprint's full field-validation ships.
- **Fence Reconstruction — first real protocol producer.** On every successful constraint-removal (rollback not triggered within the window), the blueprint synthesizes a context-specific constraint-safety protocol: *"In context `<operator + project + tooling>`, constraints of shape `<origin_evidence_class>` were safe to remove with rollback-path `<path>` because predicted consequence `<X>` did not fire."* Accumulates operator-specific tacit know-how about constraint removal. This is the working end-to-end example of synthesis in v1.0 RC — modest in ambition, honest about what the kernel can extract from one blueprint class without the full Axiomatic Judgment engine.
- **Architectural Cascade & Escalation — second real protocol producer, architecture-scope.** Every firing writes two kinds of framework entries: (a) on resolution, a context-specific cascade protocol (see Blueprint D § Pillar 3 synthesis arm) capturing *how this subsystem's blast radius actually propagates*, and (b) one `deferred_discovery` entry per item in `deferred_discoveries[]`, written immediately at PreToolUse regardless of whether the main op succeeds. The deferred-discovery stream is the kernel's own backlog of architectural debt, accumulated and hash-chained so no discovered gap is silently forgotten. Phase 12 surfaces the deferred-discovery log for operator triage at SessionStart.

**How Pillar 3 composes with the other pillars:**

- Pillar 1 (Blueprints) produces the structured synthesis outputs. Without blueprint-shaped fields, there is nothing to synthesize — the generic four-field surface does not carry `context_signature` or `synthesized_protocol`.
- Pillar 2 (Hash Chain) makes the framework tamper-evident. A framework that could be silently rewritten is worse than no framework — it would proactively guide the operator with whatever protocol the agent last invented to look good. The chain closes that attack surface.
- Pillar 3 feeds Phase 12 audit. Framework bind-rate (how often protocols are retrieved and matched) and synthesis quality (operator verdicts on surfaced protocols via Layer 8 spot-check) become audit signals. Low bind-rate plus high synthesis-rate means the framework is hoarding know-how no future decision uses — a pattern-match-for-show symptom that the audit surfaces.

**Risks named honestly.**

- **Framework-as-Doxa.** If synthesized protocols are too vague or too eager to generalize, the framework becomes the very Doxa the scaffold was built to resist — except now it is the operator's OWN Doxa, served back with tamper-evident authority. Mitigation: `context_signature` is validated by Layer 3 (must ground to real project entities); synthesis is Layer 8 spot-checked at a high sample rate in the first 30 days; Phase 12 audits the synthesis distribution for drift toward generic-advice shape.
- **Guidance-loop gaming.** An agent that writes overly-specific protocols (ones that will never match a future context) or overly-broad ones (that match everything) games the guidance loop in opposite directions. Mitigation: Layer 8 operator verdicts include a "protocol quality: useful / vague / overfit" dimension; the framework entries carry their verdict in the next audit.
- **Stale protocols.** Projects evolve; a protocol synthesized six months ago may now be wrong. Mitigation: every framework query also reports the protocol's age and last-verified-verdict from Layer 8. Stale-unverified protocols are surfaced with that caveat inline. Retirement of stale protocols is a Phase 12 audit recommendation, never automatic.
- **Guidance overload.** A framework that fires three advisory lines on every PreToolUse becomes noise the operator learns to ignore. Mitigation: stderr budget of one advisory per op unless operator explicitly runs `episteme guide` for a full listing; the advisory selects the highest-believability single match.

**Cost.** ~0.1 ms per hash write (Pillar 2 mechanism). ~5 ms per query (absorbed into scenario-detector budget). Zero hot-path latency addition when the framework is empty (the common case in the first weeks of use).

## Per-layer proposal

Each layer has the same five fields:

- **What it checks** — the validation contract.
- **How it works** — the implementation sketch.
- **How an agent evades it** — honest threat model (no layer is uncheatable).
- **Composition cost** — what evading this layer also requires from adjacent layers.
- **Cost / scope** — hot-path latency, false-positive risk, ship-window.

Where the layer is blueprint-aware, the blueprint's fields are what the layer validates; generic fallback applies when no blueprint fires.

---

### Layer 1 · syntactic blocklist + length (CURRENT, stays)

**What it checks.** `disconfirmation` and each `unknowns` entry must be ≥ 15 characters and must not contain any token from the lazy-token blocklist (`none`, `n/a`, `tbd`, `nothing`, `null`, `unknown`, `해당 없음`, `해당없음`, `없음`, `모름`, `-`, `--`, `...`).

**How it works.** Module-level regex set in `core/hooks/reasoning_surface_guard.py::_surface_missing_fields`. Length threshold modulated by `derived_knobs.json::disconfirmation_specificity_min` (Phase 9 wiring) — for the maintainer's v2 profile, 15 → 27.

**How an agent evades it.** Trivial. Produce content > the threshold without any banned token. Every fluent-vacuous example above passes.

**Composition cost.** None — this is the floor. An agent that fails Layer 1 has not even tried.

**Cost / scope.** ~0.1 ms per call. Zero false positives in well-tested operator profiles. Ships today.

---

### Layer 2 · structural specificity classifier (blueprint-aware)

**What it checks.** When a blueprint is selected, the blueprint's required fields must each satisfy the classifier: a conditional trigger (`if`/`when`/`should`/`once`/`after`/`unless`) AND a specific observable (numeric threshold, metric name, failure verb, log/dashboard reference). When no blueprint fires, the generic surface's `disconfirmation` and `unknowns` entries are classified against the same contract.

**How it works.** Extract `_classify_disconfirmation` from `src/episteme/_profile_audit.py` (Axis A S2 in Phase 12 CP3) into `core/hooks/_specificity.py` so the hot path can reuse it. The classifier is called per-field per-blueprint. Reject in PreToolUse when any required field classifies as `tautological`, `absence`, or `unknown` — with `absence` allowed to pass with a stderr advisory on non-critical fields.

**How an agent evades it.** Learn the trigger + observable vocabulary and pad it into blueprint fields. Example: *"if the metric exceeds the threshold within the time window, abort"* — has all three required elements, passes Layer 2, names nothing concrete. Layer 3 catches this via blueprint-scoped entity grounding.

**Composition cost.** An agent that evades Layer 2 by producing trigger + observable vocabulary is forced toward MORE specific language, which raises surface area for Layer 3 (blueprint entity grounding) and Layer 5 (vapor scoring). Evading Layer 2 *helps* Layer 3 catch you.

**Cost / scope.** ~5 ms (regex set against 1–2 KB of surface text) including the scenario-detector that shares this budget. Estimated FP rate < 5% on well-formed surfaces. Ships v1.0 RC.

---

### Layer 3 · contextual grounding (blueprint-aware entity set)

**What it checks.** Entities named in the surface must EXIST in the project. When a blueprint fires, the entities checked are the blueprint's named entities — Fence Reconstruction must ground `constraint_identified` (real file, real line); Consequence Chain must ground `base_rate_reference` (real incident record, real telemetry query); Axiomatic Judgment must ground each `sources[].rationale` observable.

**How it works.** Best-effort grep of the project working tree. Entity extraction is regex-based (not LLM): numeric units, snake_case identifiers, file paths, environment variables, service names, git-object references. For each, check `git ls-files | xargs grep -l`. Failure to ground is a *warning* when project context is sparse; the gate fires only when ≥ 2 grounded entities are found AND the named-but-not-found ratio exceeds 50%. Fresh repos emit no false positives.

**How an agent evades it.** Either (a) reference the project's real entities honestly, or (b) introduce real entities that match its claim (write a fake test, add a fake metric). Path (a) is the honest path — the cognitive work happened. Path (b) is detectable by the stateful interceptor (v0.10) AND by Layer 8.

**Composition cost.** Evading Layer 3 dishonestly leaves at least two traceable artifacts. Evading Layer 3 honestly IS the goal.

**Cost / scope.** ~50 ms cold cache; ~5 ms warm. FP-averse gating. Ships v1.0 RC.

---

### Layer 4 · falsification-trace requirement (blueprint-shaped)

**What it checks.** The Reasoning Surface schema gains `verification_trace`. When a blueprint is active, the trace shape is blueprint-specific. Generic shape:

```json
{
  "verification_trace": {
    "command": "kubectl logs -n prod canary | grep 'p95.*latency' | tail -100",
    "or_dashboard": "https://grafana.internal/d/api-latency",
    "or_test": "tests/test_canary.py::test_p95_under_threshold",
    "window_seconds": 600,
    "threshold_observable": "p95 > 400"
  }
}
```

Blueprint-specific shapes:

- **Consequence Chain** — one verification per consequence tier (first-order, second-order, failure-mode). Separate windows allowed.
- **Axiomatic Judgment** — one verification per source's `fail_condition`. Validates the source's believability-weight against an observable.
- **Fence Reconstruction** — verification is the `rollback_path` executed as a smoke test in a reversible context (not against prod).

When `verification_trace` is present, the validator parses it and checks that at least one of `command` / `or_dashboard` / `or_test` is non-empty AND specific:

- `command` — shell-parseable (`shlex.split` succeeds) AND ≥ 2 tokens. Bare single-word commitments (`"verify"`, `"check"`) reject because the kernel cannot hold the agent to them at Layer 6.
- `or_dashboard` — `urllib.parse.urlparse` scheme in `{http, https}` AND non-empty netloc.
- `or_test` — pytest id shape `path::test_name` OR unittest id shape `module.Class.test_name`. Makefile / ad-hoc runners belong in the `command` slot.
- `threshold_observable` — required when `command` is set. Strict grammar: must contain a comparison operator (`>`, `<`, `>=`, `<=`, `==`, `!=`) AND a digit sequence. Forces a concrete numeric comparison rather than a hand-wavy "I'll watch it."

**Blocking posture (CP6 amendment, 2026-04-21).** The pre-CP6 language ("stderr advisory on absent, block deferred to v1.0.1") was written for backward compatibility with v0.11.0 surfaces. In practice, three spec fluent-vacuous examples (*"the migration may produce unexpected behavior..."*, *"if the build process exhibits anomalous behavior..."*, *"if results diverge from expectations..."*) honestly passed Layers 2 + 3 — the only available closure path was Layer 4. CP6 promotes Layer 4 to a **blocking gate for the generic blueprint when the op matches `HIGH_IMPACT_BASH`.** Backward compatibility is preserved for the backward-compat population that actually matters — non-high-impact Bash, Write/Edit of non-lockfile paths, and Read — none of which reach the Layer 4 dispatch. The blueprint stubs shipped at CP6 (Axiomatic Judgment decision + synthesis arms, Consequence Chain, Architectural Cascade cascade fields) ship with `verification_trace_required: false` and **advisory-only** validation — their full Layer 4 realization lands with their selectors in v1.0.1.

By v1.0.1, `verification_trace` becomes required for the highest-impact ops (`terraform apply`, `kubectl apply` against prod, db migrations) with stricter rules — `window_seconds` required, per-tier traces for Consequence Chain.

**Fence Reconstruction — rollback_path as verification.** The blueprint declares `verification_trace_maps_to: rollback_path`. The existing `rollback_path` surface field is wrapped as the Layer 4 command slot and smoke-tested in a *reversible context*:

1. `shlex.split` — the command parses as a shell invocation with ≥ 2 tokens.
2. Prod-marker absence — the command does NOT contain `prod`, `production`, or `live`. Branch literals (`main`, `master`) intentionally excluded — too many non-prod local contexts. The deny-list may widen post-soak if real prod references leak through.
3. Path-existence — any path-shaped token (ending in a recognised code / config file extension) resolves to a file present in the project tree. Reuses Layer 3's cached project fingerprint. Bare directories (`tests/`) and git refs (`HEAD`, `main`) pass — the check is about catching nonexistent-FILE references, not every `/`-bearing token.

Smoke test is syntactic + referential, NOT actual execution — executing the rollback at PreToolUse would undo the constraint removal before it happens. Full sandboxed execution lands in v1.0.1+.

**How an agent evades it.** Write a fake command. The hot path can't run it at write time (side effect). Layer 6 (time-bound contract, hash-chained) checks whether the named command was actually run within the declared window. Write-time vapor becomes audit-time failure.

**Composition cost.** Faking `verification_trace` at Layer 4 commits the agent to a Layer 6 violation — the named command must show up in the agent's bash history within the declared window, or the surface is retrospectively invalidated. The pillar-2 hash chain makes retroactive repair impossible.

**Cost / scope.** ~1 ms parse + structural check. Non-breaking additive schema. Ships v1.0 RC.

---

### Layer 5 · embedding-based vapor scoring (DEFERRED v1.1)

**What it checks.** Each surface field is embedded by a small local model. The embedding is compared to a corpus of known-good surfaces and known-bad surfaces. Surfaces whose embeddings fall outside the known-good distribution by > N sigma are flagged.

**How it works.** Bundle a small sentence-transformer model (`all-MiniLM-L6-v2` or similar, ~80 MB) with the kernel; compute embedding for `core_question` + `disconfirmation` + concatenated `unknowns` (or the blueprint-specific equivalent fields); cosine-similarity against a known-good centroid; reject if score < threshold.

**How an agent evades it.** Produce embeddings near the centroid. Mitigation: the corpus *grows* with the operator's accepted surfaces over time — operator-specific centroid not knowable from public training data.

**Composition cost.** An agent whose surfaces pass Layer 5 by producing high specificity and varied vocabulary has done much of what Layers 2, 3, 4 wanted — Layer 5 is partially redundant with the lower layers, which is defense in depth working.

**Cost / scope.** ~200 ms per call. Adds ~80 MB to the install footprint. Defers to v1.1 unless an acceptable-cost embedding API path is found.

---

### Layer 6 · time-bound disconfirmation contract (hash-chained)

**What it checks.** When `verification_trace.window_seconds` is declared, the kernel records a *pending contract* in `~/.episteme/state/pending_contracts.jsonl` with the full blueprint surface snapshot. **Each record is chained** (pillar 2). After the window expires, an async checker (cron or SessionStart hook) verifies: was the named command executed (stateful interceptor records)? Did the named test run? Did the dashboard get viewed (browser-extension hook, optional)? If none of the verification methods fired, the surface is retrospectively tagged `disconfirmation_unverified` in the episodic tier (also hash-chained).

`disconfirmation_unverified` records feed Phase 12 — the audit counts unverified-rate per axis per blueprint and surfaces it as drift if it exceeds threshold. Phase 12 refuses to audit across a broken chain range.

**How an agent evades it.** Run the named command performatively (`echo "kubectl logs..." && true`). Mitigations: (a) Layer 6 checks for command + non-zero output + recency; an echoed command produces no real output; (b) cross-reference with project telemetry — if `kubectl logs` was named and actual logs were produced, real check fired; (c) the hash chain prevents retroactive "I actually did run it" edits after the window expires.

**Composition cost.** Layer 6 makes Layer 4 verifiable. Without Layer 6, Layer 4 is just another schema field. Together with the hash chain, they form a write-time-commit + audit-time-verify + tamper-evident contract.

**Cost / scope.** ~0 ms hot path (write pending contract record + one hash). Async check runs at SessionStart or via cron. Ships v1.0 RC as an extension to the Phase 12 audit pipeline.

---

### Layer 7 · adversarial co-validator (DEFERRED v1.1+)

**What it checks.** A second LLM (different model family — ideally a small open-weights model the operator runs locally) reads the surface and answers: *"if the agent that wrote this were trying to make it look good without actually thinking, how would they have written it? Show me a fluent-vacuous variant."* The adversarial variant is compared to the actual surface (via Layer 5's embedding similarity). Too-similar surfaces are rejected with the adversarial variant attached as evidence.

**How an agent evades it.** Produce a surface that doesn't pattern-match "trying to look good." This requires actually committing to a falsifiable hypothesis — exactly what the kernel wants.

**Composition cost.** Layer 7 is the strongest semantic gate but also the most expensive. Most useful in adversarial settings (CTF-like, security review). For day-to-day praxis, Layers 2 + 3 + 4 + 6 cover ~90% of evasion shapes at a fraction of the compute.

**Cost / scope.** ~2–5 seconds per call. $0.001–$0.01 per check. Defers to v1.1; possibly never default-enabled.

---

### Layer 8 · operator spot-check sampling (blueprint-prioritized)

**What it checks.** A configurable percentage of high-impact surfaces is flagged for explicit operator review even when they pass Layers 1–4. Default rate: 10% for the first 30 days from install (calendar-from-install), then decay to 5%. Blueprint-fired surfaces sampled at 2× the base rate — the operator's calibration signal lands where the cognitive claim is largest. Selection decisions (which blueprint fired for which op) are themselves spot-checked at a lower rate to cover selector-Goodhart.

Flagged surfaces queue to `~/.episteme/state/spot_check_queue.jsonl` (hash-chained). SessionStart presents them at the start of the next session ("3 surfaces flagged for review since last session — `episteme review`"). Operator verdicts (real / vapor / wrong-blueprint) train per-operator tuning over time.

**How an agent evades it.** Cannot. The operator is the ground truth. Sampling is random; the agent cannot predict which surfaces get reviewed.

**Composition cost.** Layer 8 is the calibration layer for all the others. Operator verdicts tune thresholds in Layers 2, 3, 5 and adjust blueprint bind-rates — making the system self-correcting against drift in either direction.

**Cost / scope.** ~0 ms hot path (queue write + hash). Operator burden: ~5% of high-impact surfaces × 30 seconds review = a few minutes per session for a maintainer doing ~10 high-impact ops/day. Ships v1.0 RC; sample rate configurable per-project.

## Why these layers compose well

The orthogonality test: for each pair of adjacent layers, can a single evasion strategy defeat both?

| Pair | Aligned strategy? | Mutually inconsistent? |
|---|---|---|
| L1 + L2 | Yes (verbose + has trigger+observable) | No |
| L2 + L3 | **No — verbose specific text is more grep-able for blueprint-named entities** | **Yes** ← orthogonality |
| L3 + L4 | Partial (real entities help, but L4 needs executable command) | Partial |
| L4 + L6 | **No — fake command at L4 produces L6 violation at audit time; hash chain closes retroactive repair** | **Yes** ← orthogonality |
| L5 + L7 | **No — embedding-near-centroid surfaces look like "trying to look good"** | **Yes** ← orthogonality |
| L6 + L8 | Mostly orthogonal (audit signal vs operator ground truth) | Mostly |
| Blueprint-selector + L8 (selection sample) | **No — an agent that games the selector gets sampled on its selection choice, not just its surface content** | **Yes** ← new orthogonality introduced by pillar 1 |

The three original orthogonal pairs (L2+L3, L4+L6, L5+L7) remain load-bearing. The reframe adds a fourth orthogonality axis (selector vs spot-check) that the pillar creates.

An agent that wants to evade everything has to:

- Select the hardest-to-fake blueprint for the action (defeats selector-Goodhart)
- Be specific (defeats L2)
- Reference real project entities per the blueprint's required grounding (defeats L3)
- Commit to executable verification per consequence tier (defeats L4)
- Actually execute the verification within the window (defeats L6)
- Not mutate the record afterwards to cover a miss (defeats the hash chain)
- Produce varied semantic content (defeats L5)
- Avoid pattern-matching "performance of specificity" (defeats L7)
- Hope it's not in the spot-check sample (defeats L8 statistically; ground-truth eventually catches if not this sample, the next)

By the time an agent does all of this, it has approximately performed the causal decomposition the kernel was trying to enforce. **That is the entire goal.** Not "make cheating impossible" — make cheating cost more than honesty, and make retroactive cheat-covering detectable.

## What ships in v1.0 RC

**Hot-path additions (block at PreToolUse):**

- Scenario detector + blueprint selector + blueprint registry scaffold (`core/blueprints/`).
- Layer 2 — structural specificity classifier, blueprint-aware (extracted from Phase 12 to `core/hooks/_specificity.py`).
- Layer 3 — contextual grounding, blueprint-aware entity set (including blast-radius-map entity grounding for Blueprint D).
- Layer 4 — `verification_trace` schema field, blueprint-shaped (optional in v1.0; required for highest-impact ops in v1.0.1).
- Blueprint B — **Fence Reconstruction**, fully realized end-to-end (selector → blueprint → Layer 2/3/4 validation → hash-chained Layer 6 record → framework protocol entry → Phase 12 audit input).
- Blueprint D — **Architectural Cascade & Escalation** scaffolding (selector firing on the four trigger classes; structural validation of `patch_vs_refactor_evaluation` + `blast_radius_map` + `sync_plan`; immediate hash-chained write of every `deferred_discoveries[]` entry to the framework as a `deferred_discovery` record).
- **Pillar 3 active-guidance query** — framework query after scenario detection, before blueprint enforcement. One stderr advisory per op.

**Async additions (retrospective):**

- Layer 6 — time-bound contract checker with append-only hash chain, plumbed into Phase 12's audit pipeline.
- Layer 8 — spot-check sampling + operator review CLI (`episteme review`), blueprint-prioritized and protocol-quality-aware. Blueprint D resolutions carry an explicit "cascade-theater vs real sync" verdict dimension.
- **Pillar 3 SessionStart digest** — "N protocols synthesized since last session. M deferred discoveries pending triage."
- **`episteme guide` CLI (minimal)** — list matching protocols + synthesis provenance; `--deferred` flag lists pending deferred discoveries.

**Stays as-is:**

- Layer 1 — current syntactic + length validator.

**Ships as structure only, full realization in v1.0.1:**

- Blueprint A (Axiomatic Judgment) — schema lands in `core/blueprints/` (decision arm + synthesis arm); selector can fire it; field-level validation is advisory-only in RC. Skeleton protocol entries flow to the framework from any firing; rich `conflict_cause` / `context_signature` / `synthesized_protocol` enforcement lands in v1.0.1.
- Blueprint C (Consequence Chain) — schema lands; field-level validation advisory-only in RC.
- Blueprint D (Architectural Cascade & Escalation) — hot-path structural validation ships; retrospective sync-plan completeness verification (cross-surface orphan-reference detection) ships in v1.0.1.
- Generic maximum-rigor fallback — Consequence-Chain-shaped schema applied to any high-impact op not matched by A / B / C / D (Goodhart closer for blueprint-absence evasion).
- **`episteme guide` rich-query mode** — interactive query, protocol revision, retirement proposals. RC ships the read path; v1.0.1 ships the authoring path.

**Deferred to v1.1:**

- Layer 5 — embedding-based vapor scoring (infra + footprint cost).
- Layer 7 — adversarial co-validator (compute cost + only useful in adversarial settings).

## Implementation sequencing

Ten commits, mirroring the Phase 12 checkpoint discipline. Each checkpoint pauses for review. Tests stay green at every commit.

1. **CP1 — extract `_specificity.py`.** Move `_classify_disconfirmation` from `src/episteme/_profile_audit.py` to `core/hooks/_specificity.py`. Phase 12 imports from the new module; behavior unchanged.
2. **CP2 — scenario detector + blueprint registry.** New `core/hooks/_scenario_detector.py`. New `core/blueprints/` directory with generic-fallback blueprint plus registry loader. No behavior change — detector always returns "generic" until CP5 wires Fence Reconstruction. Tests cover registry load + generic fallback.
3. **CP3 — Layer 2 in the hot path.** `reasoning_surface_guard.py` calls `_classify_disconfirmation` against the selected blueprint's fields (generic for now). Rejects on `tautological` / `unknown`; advisory on `absence`. New test class.
4. **CP4 — Layer 3 contextual grounding.** New `core/hooks/_grounding.py`. Blueprint-aware entity extraction + project grep. FP-averse gating. New test class.
5. **CP5 — Blueprint B (Fence Reconstruction), realized end-to-end + first synthesis output.** Populate `core/blueprints/fence_reconstruction.yaml`; wire scenario detector to fire it on constraint-removal patterns (git-diff signature + lexicon hits); Layer 2 / 3 validation against its fields. On successful removal (rollback-path not triggered within the window), write a constraint-safety protocol entry to the framework — the first real Pillar 3 synthesis producer. New test class covering scenario firing, blueprint selection, field validation, fallback behavior, and protocol emission.
6. **CP6 — Layer 4 verification_trace schema.** Update `core/schemas/reasoning-surface/...`; optional field; structural validation; blueprint-shaped variants for Fence Reconstruction. Advisory for highest-impact ops; required lands in v1.0.1. Schemas for Axiomatic Judgment (including synthesis-arm fields as stubs), Consequence Chain, and Blueprint D (cascade fields as stubs) land as structure; their blueprint validation is advisory-only at RC.
7. **CP7 — Pillar 2 hash chain + Pillar 3 substrate.** New `core/hooks/_chain.py` (shared SHA-256 chain implementation) and `core/hooks/_pending_contracts.py` (Layer 6 write). Same commit lands `core/hooks/_framework.py` (Pillar 3 framework read/write, sharing the chain implementation) and `core/hooks/_context_signature.py` (canonicalization for framework query). Write at PreToolUse when `verification_trace` declared; check at SessionStart; tag `disconfirmation_unverified`. Phase 12 audit input gains chain-verification precondition. New test class covering chain integrity, chain-absent genesis, chain-broken governance event, chain-reset protocol, and framework write from CP5's Fence Reconstruction path.
8. **CP8 — Layer 8 spot-check sampling.** Configurable rate (default 10% → 5%) at PreToolUse; blueprint-fired surfaces sampled at 2× base; synthesized protocols sampled at 2× base with a "protocol quality" verdict dimension; Blueprint D resolutions sampled at 2× base with an explicit "cascade-theater vs real sync" dimension; queue to `spot_check_queue.jsonl` (hash-chained); new `episteme review` CLI; SessionStart surface. Operator verdicts training into per-operator tuning is scoped out of CP8 — lands in v1.0.1.
9. **CP9 — Pillar 3 active guidance surface.** Wire framework query into the hot path after scenario detection, before blueprint enforcement. One stderr advisory per op (highest-believability match). SessionStart digest of protocols synthesized since last session + count of pending deferred discoveries. New `episteme guide [--context <keyword>] [--since <date>] [--deferred]` CLI — minimal version: lists matching protocols + synthesis provenance; `--deferred` lists pending deferred-discovery entries. Tests cover query determinism, stale-protocol caveat rendering, empty-framework no-op, overload budget (≤ 1 advisory per op), deferred-discovery listing.
10. **CP10 — Blueprint D (Architectural Cascade & Escalation) scaffolding.** Populate `core/blueprints/architectural_cascade.yaml`. New `core/hooks/_cascade_detector.py` — runs inside the scenario-detector slot, implements the four selector triggers (cross-surface-ref diff check, refactor/rename/deprecate lexicon hits, self-escalation `flaw_classification`, generated-artifact symbol-reference check). Structural validation of `patch_vs_refactor_evaluation` (non-generic rationale required), `blast_radius_map[]` (every entry either names a real surface or is marked `not-applicable` with reason), `sync_plan[]` (every map entry has a matching plan line). On every firing, each `deferred_discoveries[]` entry is written immediately to the hash-chained framework as a `deferred_discovery` record — this payoff lands in RC even before retrospective sync-plan verification (v1.0.1). Phase 12 audit gains two new queries: deferred-discovery frequency-by-class and deferred-discovery aging. New test class covering selector firing on all four trigger classes, `not-applicable` discipline, deferred-discovery hash-chain write, and the orphan-reference detection stub (advisory-only in RC, full retrospective check in v1.0.1).

## Honest threat model — what STILL evades after v1.0

Per Phase 12's discipline of naming what the system does NOT cover:

1. **Coordinated multi-call evasion.** An agent splits a high-impact op into many low-impact ops, each with bare-minimum surfaces, evading the high-impact gate per call. Mitigation: stateful interceptor (v0.10) catches some; Layer 6 retrospective audit can detect patterns. Truly mitigating requires session-level surface aggregation — out of v1.0 RC scope.

2. **Operator collusion.** If the operator stops doing real spot-checks (Layer 8) and rubber-stamps everything, the calibration loop poisons. The operator is the ground truth; there is no recourse if ground truth is corrupted. This is by design.

3. **Adversarial-trained agent.** An agent specifically trained on bypassing episteme's validators is a different threat class. Mitigation: Layer 7 (deferred). Full defense requires a closed-system runtime or a different threat model entirely.

4. **High-volume noise drowning the signal.** An agent producing 10× the normal surface volume saturates Layer 8's sample budget and Phase 12's audit windows. Mitigation: Layer 6 records contracts independently; spot-check rate scales with volume. Not a hard solve.

5. **Semantic Goodhart on Layer 5 / Layer 7.** Once the embedding model or adversarial co-validator is known, the agent can be fine-tuned against it. Mitigation: rotate the embedding model on each kernel release; never publish the adversarial co-validator's weights. Ongoing arms race; the kernel cannot win it permanently, only stay ahead.

6. **Memory poisoning via retroactive state mutation.** *[Closed by pillar 2 — hash chain.]* An agent edits `~/.episteme/state/*.jsonl` to look like it predicted outcomes it actually missed. Chain verification breaks on any such edit; Phase 12 refuses to audit across broken ranges.

7. **Blueprint-absence evasion.** An agent produces actions that don't match any named blueprint so validation falls to generic schema. *[Closed by the generic maximum-rigor fallback.]* Any op classified as high-impact that does not match A / B / C / D receives the Consequence-Chain-shaped field set by default — at least as strict as any single named blueprint.

8. **Blueprint-selector gaming.** An agent learns which inputs trigger the hardest blueprint and shapes input to avoid it. Partially closed by Layer 8 sampling a percentage of selection outcomes, and by Phase 12 auditing selection distribution drift over time. New Goodhart surface introduced knowingly by pillar 1.

9. **Offline chain attack.** An adversary with FS access edits the chain *and* the chain-head atomically — a coordinated rewrite. Mitigation outside v1.0 RC scope: cryptographic signing of chain-head rotations. For v1.0 RC, chain-head committed to git in git-tracked projects provides second-layer evidence; accepting that non-git workflows remain vulnerable to this specific attack.

This section is load-bearing. Any later change to v1.0 RC scope that claims to close one of these without explicit mitigation is a governance change, not an implementation tweak.

## Non-goals

- **Provably uncheatable validation.** Out of scope. The honest claim is "evasion costs more than honesty, and retroactive cheat-covering is detectable," not "evasion is impossible."
- **Real-time LLM-based validation in the hot path.** Latency cost too high for v1.0 RC. Layer 7 is async-only.
- **Operator profile mutations from spot-check verdicts.** Verdicts inform threshold tuning per project, never auto-edit the global operator profile.
- **Replacing Phase 12.** v1.0 RC extends the retrospective loop; it does not substitute for it. Both ship and run together.
- **Cross-operator validation.** Multi-operator coordination is on the deferred multi-operator roadmap; v1.0 RC stays single-operator like v0.11.0.
- **Providing tools, skills, or agent capabilities.** *[BYOS constraint.]* The kernel intercepts state mutation regardless of source. It does not ship tools, skill libraries, MCP servers, or agent frameworks. Skill provision is the ecosystem's concern; cognitive and execution governance is the kernel's.
- **Tool-specific validation code paths.** Layers 2–8 operate on the surface + pending op, never on the tool that produced them. A new skill provider integrates transparently.
- **Expanding the hash chain to `derived_knobs.json` or profile-axis changes.** Explicitly out of scope for v1.0 RC. Chain scope in RC is episodic tier + pending contracts + **framework protocols** only; expansion is a later governance decision after the core mechanism is proven.
- **Auto-retiring stale protocols from the framework.** Phase 12 audit recommends retirement; the operator approves. Kernel never silently forgets a synthesized protocol — that would be the framework's version of measure-as-target drift.
- **Blocking execution on framework-guidance alone.** Pillar 3 is advisory, never blocking. Guidance informs; blueprints (Pillar 1) enforce. Collapsing the two would produce a feedback loop where the kernel enforces its own synthesis against the operator.

## Verification — v1.0 RC is "done" when

- All ten checkpoints land with paused-review-before-commit discipline.
- Test suite stays green at every commit (baseline 202; CP1 holds; CP2–CP10 each add ~15–25 tests).
- Hot-path latency profile shows p95 < 100 ms added by Layers 2–4 + scenario detector (including cascade detector) + framework query combined.
- Five fluent-vacuous evasion examples from "Why this exists" are now blocked at write time by some combination of Layers 2–4 + Fence Reconstruction blueprint where applicable.
- End-to-end dogfood on a real constraint-removal op fires Fence Reconstruction, produces a blueprint-populated surface, writes a hash-chained Layer 6 record, **and emits a synthesized constraint-safety protocol to the framework**. If this end-to-end example does not produce a framework entry that subsequently surfaces as guidance on a matching future op, CP5+CP9 failed regardless of what the tests show. The framework is not "done" when it exists; it is done when its output changes an operator decision.
- **Blueprint D dogfood — the kernel satisfies itself.** Over the RC soak, at least one real architectural-cascade op *on the episteme repo itself* (a rename, a refactor, a schema change, or a core-logic update) fires Blueprint D, produces a non-trivial `blast_radius_map[]` grounded against real surfaces, a `sync_plan[]` with concrete actions per surface, ≥ 1 `deferred_discoveries[]` entry committed to the hash-chained framework, AND the proposed diff ultimately touches every surface named in the map (no orphan-reference regression detected retrospectively). If the kernel's author edits the kernel without Blueprint D firing — or fires it but ships orphan references — the self-maintenance axis failed regardless of test count. This is the Gate-28 equivalent for Blueprint D.
- Phase 12 audit dogfood shows `disconfirmation_unverified` rate < 10% on the maintainer's tier after 30 days of Layer 6 active. Above 10% means the kernel is enforcing contracts the operator isn't honoring — either tighten the operator's discipline or relax the contract; the audit surfaces the gap.
- **Pillar 3 dogfood** — after 30 days of real use on the maintainer's tier, the framework holds ≥ 3 non-trivial protocols AND ≥ 1 has fired as guidance on a subsequent op AND the operator has a spot-check verdict recorded on that firing (useful / vague / overfit). If the framework is empty or guidance never fires, Pillar 3 failed at the cognitive level regardless of whether the code runs.
- **Deferred-discovery flow-through.** Over the RC soak, ≥ 3 deferred-discovery entries are logged and at least one is either (a) promoted to a named phase/CP in NEXT_STEPS.md, or (b) triaged to "won't fix" with recorded rationale. A deferred-discovery log that only grows is an architectural-debt accumulator, not a self-maintenance loop.
- Chain verification succeeds across the full RC soak window for all three chained streams (episodic tier, pending contracts, framework protocols — including `deferred_discovery` records). Any chain-broken event during the soak is investigated and root-caused before GA.
- Layer 8 spot-check delivers ≥ 1 actionable operator verdict per week of normal use over the RC soak. Below this, sample rate is too low; above 5/week, sample rate is too high (operator burden).
- This document remains `approved (reframed, third pass)` through RC; any further philosophical shift is a new spec amendment.

## What this spec does NOT cover

- Implementation-level code (function bodies, exact regex patterns, full test fixtures). Those emerge during the checkpoint sequence, traceable back to this spec.
- Final field shapes for Blueprints A (Axiomatic Judgment) and C (Consequence Chain). Structure ships in RC; full realization in v1.0.1 with audit data.
- The Layer 5 corpus assembly (which surfaces count as known-good?). Deferred along with Layer 5 itself.
- The Layer 7 adversarial-co-validator model choice. Deferred along with Layer 7.
- Hash-chain signing for chain-head rotations. v1.0 RC uses plain SHA-256 chaining + optional git co-commit. Cryptographic signing is a post-GA hardening step.
- Performance optimization beyond the worst-case latency budget. Out-of-scope until profile data exists.
- v1.0 GA scope. v1.0 RC is the gate; GA is `v1.0.0` after the soak window confirms the engineering AND cognitive-adoption gates.

---

## Review checklist for the maintainer

Before considering this spec fully settled:

1. The reframed thesis — "structural forcing function for causal-consequence modeling, protocol synthesis, active guidance, AND continuous architectural self-maintenance, grafted onto an engine that cannot perform any of them natively" — is the correct level of claim. If any of the four axes overclaims (especially the self-maintenance axis, which is the newest), name the weaker version you'd prefer before implementation.
2. The BYOS stance is absorbed correctly in the preamble — episteme intercepts, does not provide. If a future skill-adjacent feature is proposed, it's a governance event.
3. The four named blueprints (A Axiomatic Judgment, B Fence Reconstruction, C Consequence Chain, D Architectural Cascade & Escalation) plus the generic maximum-rigor fallback are the right starting set. Additions are governance-gated. If the Blueprint D selector triggers miss a cascade class you expect to see in real use, name it before CP10.
4. Fence Reconstruction is the right end-to-end example for RC because it binds to an existing audit axis AND becomes the first real Pillar 3 synthesis producer. If another blueprint would give a stronger end-to-end demonstration of both arms, name it before CP5.
5. The hash-chain scope (episodic tier + pending contracts + framework protocols, including `deferred_discovery` records) is correctly bounded. Expansion to `derived_knobs.json` or profile-axis changes is a later governance decision, not a scope creep.
6. Pillar 3's guidance surface is advisory-only in RC. Making it blocking would create a feedback loop where the kernel enforces its own synthesis against the operator. Confirm the advisory posture is correct before CP9.
7. The ten v1.0 RC checkpoints are sized at one logical commit each. If any feels too large (CP7 bundles chain + framework substrate; CP10 bundles selector + validation + hash-chained deferred-discovery write), split before implementation.
8. The honest threat model names every evasion class you can think of after reading. New ones join the list rather than being silently countered. Cascade-theater (filling `blast_radius_map[]` with `not-applicable` entries to pass) is specifically called out in Pillar 1 Risks — confirm the Layer-3 grounding + Layer-8 verdict dimension is sufficient, or escalate before CP10.
9. The "make cheating cost more than honesty, make retroactive cheat-covering detectable, turn resolved conflicts into durable context-indexed know-how, AND keep the system's own self-model coherent as it edits itself" framing is correct. If you believe an uncheatable protocol is achievable within v1.0 RC scope, this spec needs to be rebuilt around that claim.
10. Blueprint D on the kernel itself — the Gate-28 equivalent for self-maintenance. Confirm the maintainer accepts that editing episteme in a way that does not satisfy Blueprint D fails the RC, even if all code tests pass.

Once these are settled, implementation begins as v1.0.0-rc1 work. Per the *Implementation timing* record above, v0.11.0 has been tagged and shipped (2026-04-21); RC cycle is open.
