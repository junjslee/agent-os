# Design — v1.1+ · From Reliability Engineering to Epistemology · The Proactive Reasoning Engine

Status: **drafted (vision)** · Drafted 2026-04-25 (Event 55) · Awaiting operator review · Scope: post-v1.0-GA architectural vision — extends `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` without retracting any of its load-bearing decisions.

> **This is a vision draft, not an approved spec.** The v1.0 RC spec required three reframes before it landed as `approved (reframed, third pass)`. v1.1 will require at least one operator review before any CP under it begins. The proposed CP plan in §10 is provisional. No code lands against this document until the status flips to `approved`.

---

## Why this exists

`v0.x` taught the kernel to detect named failure modes — lazy tokens, sub-15-character disconfirmations, normalized-command bypass shapes. Reactive structural validation against a fixed blocklist.

`v1.0 RC` taught the kernel to **force causal-consequence modeling** at the moment of state mutation. Three pillars made epistemic integrity load-bearing per action: Cognitive Blueprints (Pillar 1), an Append-Only Hash Chain (Pillar 2), Framework Synthesis & Active Guidance (Pillar 3). The kernel could now distinguish a fluent-vacuous Reasoning Surface from a structurally-grounded one, synthesize context-fit protocols from resolved conflicts, and proactively guide future decisions with the accumulated framework.

`v1.1+` is the next structural shift: **extend the same discipline that v1.0 applies to the agent's per-action reasoning to the kernel's own knowledge artifacts.** Protocols can decay; discoveries can pile up unread; the architecture can reach states where "detect and stop" is no longer the right shape. The transition operator named — *"from reactive logging/blocking to proactive reasoning engine"* — is the substance of v1.1.

Three structural flaws in v1.0's posture motivate this:

1. **Past truth is not present truth.** A Pillar 3 protocol synthesized in 2026-04 may be invalid by 2026-08 because the underlying dependency, convention, or threat model has shifted. v1.0 has no falsification path for its own past protocols. The `~/.episteme/framework/protocols.jsonl` stream is *append-only* — which is correct for tamper evidence, but currently silent on supersession.
2. **Volume buries pattern.** The `~/.episteme/framework/deferred_discoveries.jsonl` stream grows unbounded. Blueprint D's verification gate already names this risk: *"a log that only grows is architectural-debt accumulation, not self-maintenance"* (`docs/PROGRESS.md` Event 6). Reading 1000 entries to find the 3 that share a root-cause is operator burden the kernel should reduce — without delegating the reasoning.
3. **Reactive is the ceiling of v1.0.** Every v1.0 mechanism is *"if it breaks, detect and stop"*. The four canonical artifacts (reasoning-surface · decision-trace · verification · handoff) are *records* the chain makes trustworthy. The endgame v1.1+ is asked to point at: a system so structurally self-consistent that the records are *evidence of* — not *basis for* — its own correctness. Hash chains do not vanish in this future; they become falsification surface for an underlying consistency rather than the only thing standing between the system and silent drift.

---

## Core question

What structural mechanisms — added to v1.0's three pillars — allow the kernel to:

- **(a)** treat its own protocols as *falsifiable hypotheses* with explicit time-validity, retirement, and re-elicitation paths — so the framework is honest about what it *used to* believe vs. what it *currently* believes;
- **(b)** detect causal clusters across the deferred-discoveries stream automatically (zero-LLM entity extraction in the hot path; LLM in the reflective layer only), propose root-cause Macro Change Proposals to the operator, and resolve clusters atomically with a single chain entry rather than entry-by-entry;
- **(c)** progress measurably toward an asymptote of structural self-consistency — where new protocols cannot silently contradict existing ones, models can be promoted from converging-protocol clusters, and disconfirmation conditions can be auto-derived from causal models — without ever claiming the asymptote is reached?

Five sub-questions this spec must answer:

1. **Time-validity contract.** What fields must a synthesized protocol carry to be falsifiable across time? Who computes the falsification verdict? Who acts on it?
2. **Cluster detection without LLM in the hot path.** What deterministic mechanism extracts entities and co-occurrence weights from the deferred-discoveries stream at the kernel's < 100 ms hot-path budget?
3. **Reflective-session escape valve.** When does the LLM enter the picture, with what gate, and what does its output have to look like to enter `docs/NEXT_STEPS.md` as a Macro CP?
4. **Cross-protocol consistency.** Once protocols can decay, what stops a fresh protocol from silently contradicting a not-yet-decayed one? What is the surface where the contradiction surfaces?
5. **Goodhart at v1.1 scale.** v1.0 named the threat at the validator level (a sufficiently-aware agent gaming a fixed decomposition protocol). v1.1's mechanisms (decay, clustering, self-consistency) are themselves new optimization surfaces. What countermeasures keep them honest?

---

## The cognitive arc — v0.x → v1.0 → v1.1

| Stage | Posture | Mechanism | What's new |
|---|---|---|---|
| **v0.x** | *Detect named failure modes.* | Lazy-token blocklist; ≥ 15-char minimums; normalized-command scanning; structural validation against a fixed schema. | Reactive — the kernel knows what *vapor* looks like and refuses it. |
| **v1.0 RC** | *Force causal-consequence modeling.* | Pillar 1 Cognitive Blueprints (A · B · C · D + generic fallback) + Pillar 2 hash-chained streams + Pillar 3 framework synthesis & active-guidance loop. | The agent's per-action reasoning becomes tamper-evidently structured. The kernel surfaces context-fit protocols from prior decisions at the next matching op. |
| **v1.1+** | *Refactor the kernel's own knowledge.* | Three new cognitive arms operating on the kernel's own artifacts (protocols, discoveries, models): Temporal Integrity, Causal Synthesis, Self-Consistency Convergence. | Records gain the same discipline they used to merely *record*. The framework can falsify itself; clusters can resolve atomically; protocols can promote to models that derive disconfirmations structurally. |

The v1.0 pillars remain load-bearing and unchanged. v1.1 adds three arms that reach above them — pulling the kernel's posture from *per-action discipline* toward *per-system self-maintenance*.

---

## v1.1 cognitive arm A · Temporal Integrity (Protocol Decay)

> *Pillar 3 protocols are written-once, read-forever. They reflect a past truth. The kernel needs to falsify its own past beliefs.*

### Problem statement (causal-chain)

`~/.episteme/framework/protocols.jsonl` is append-only by Pillar 2 design — that's correct for tamper evidence. But the active-guidance loop at PreToolUse currently treats every entry as currently-valid. A protocol synthesized at 2026-04-21 from a context where library X v3 was canonical does not know that library X v4 (released 2026-08) has flipped the convention. The kernel surfaces the v3 protocol as advisory at a v4 op, the agent uses it, the resulting Reasoning Surface inherits a stale assumption, the op proceeds, the chain records a *fluent-confident-wrong* entry. v1.0's Goodhart resistance protects per-action decomposition; it does not protect against *the framework itself becoming the Doxa*.

This is the named failure mode `framework-as-Doxa` (mode 10 in `kernel/FAILURE_MODES.md`, added during v1.0 RC drafting). v1.0 named the risk; v1.1 specs the mechanism.

### Mechanism

The protocol envelope (currently the `cp7-chained-v1` shape under `~/.episteme/framework/protocols.jsonl`) gains a **validity block**. Proposed shape — operator-reviewable at first review pass:

- **synthesis timestamp** — already present; clarified semantics.
- **falsification condition** — an observable that, when fired N times, marks the protocol as decayed. Mirrors the Reasoning Surface's `disconfirmation` field but at the protocol's own scope rather than the firing op's.
- **re-elicit window** — optional time-bound (default null = falsification-only). When set, the protocol decays automatically at the named time regardless of observed outcomes — used for protocols anchored to release cycles, regulatory windows, or external-dependency support windows.
- **supersession reference** — null at synthesis; populated when the protocol is retired by a newer entry. Hash-chained; the original entry stays in place (Pillar 2 immutability), but the read-loop knows to skip it.

A new audit subcommand under the existing `episteme evolve` family (proposed name to be reviewed at v1.1 spec-approval pass) compares each active protocol's predicted outcomes against the recent episodic record:

- The recent-window default mirrors the Phase 12 audit's default (30 days cold-start; revisit to 90 days at the same trigger).
- For each active protocol, the audit measures: (i) how many ops with matching context-signature fired in the window, (ii) how many of those produced an outcome consistent with the protocol's claim, (iii) how many produced a contradicting outcome, (iv) whether the falsification condition fired N times.
- A protocol crosses the decay threshold when contradicting outcomes / total matching ops exceeds an operator-tunable rate (proposed default: 50%, audited at every run).
- Decayed protocols are flagged for **re-elicitation, not auto-rewrite** — this carries forward Phase 12's D3 countermeasure (the loop never auto-mutates the operator's framework; it surfaces a prompt).
- The active-guidance loop excludes decayed protocols from advisory output at PreToolUse. The chain still carries them. The loop knows to skip.

### Goodhart resistance at v1.1 scale

A naive decay mechanism is itself gameable. Three counters carry forward from v1.0 / Phase 12 and one is added:

- **D1 · Multi-signature convergence (carried forward).** No single feature triggers a decay flag. The audit measures contradiction-rate AND falsification-condition-fire AND inter-protocol-consistency. Optimizing for one feature leaves the others misaligned.
- **D2 · Retrospective-only computation (carried forward).** The decay verdict is computed from already-written episodic records. The agent does not see the decay-condition function at decision time. Goodhart's *"when a measure becomes a target"* gets a windowing defense: the target is invisible at the moment the agent could optimize for it.
- **D3 · Re-elicitation, not auto-edit (carried forward).** The audit emits a *prompt* for the operator. The framework is not auto-rewritten. The operator decides whether the decay verdict is correct, the protocol's claim was always wrong, or the context shifted under it.
- **D5 · Decay rate as a Phase 12 axis (new in v1.1).** Abnormally high decay rate across the synthesis output of a particular blueprint (for example, Axiomatic Judgment producing protocols that decay within 30 days at > 80% rate) is itself a Phase 12 audit signal — surfaced as `protocol_churn` drift, prompting the operator to ask whether the blueprint is being asked to synthesize from contexts it cannot model. This is the kernel auditing its own audit's outputs — one level of self-reference further than v1.0 reached.

### Verification gate (proposed)

Temporal Integrity ships when, after a 30-day window with the v1.1 mechanism live: ≥ 1 protocol has been validly decayed (operator-confirmed); ≥ 0 protocols have been spuriously decayed (operator-confirmed false-positive rate within tolerance); the active-guidance loop demonstrably skips the decayed protocol on a matching op without skipping non-decayed protocols on the same op-class.

---

## v1.1 cognitive arm B · Causal Synthesis (Causal Clustering & Macro-CP Closure)

> *Deferred discoveries pile up faster than humans can read. The kernel should let the operator see patterns at a glance — and resolve clusters atomically.*

### Problem statement (causal-chain)

Blueprint D's deferred-discovery flow is correct in structure: when an op surfaces an adjacent gap, that gap is hash-chained immediately rather than ignored or silently absorbed. But the operator-side flow is *read 1000 entries → notice the 15 that all touch authentication → realize it's a single architectural flaw → manually open one CP that fixes it → manually mark the 15 as resolved.* Every step except the first is a candidate for kernel-side reduction without delegating the reasoning.

The kernel currently does the equivalent of *taking detailed daily case notes* and stopping there. The reflective doctor's-rounds equivalent — *"these 15 patients all show the same constellation; what's the underlying syndrome?"* — has no kernel surface.

### Mechanism — three steps, three operator gates

**Step 1 — Graphing (deterministic, hot-path-safe, zero-LLM).**

A new background worker (proposed location `tools/discovery_graph.py`, scheduled via the same cron pattern as `clone.yml` or run on-demand via a CLI subcommand) reads `~/.episteme/framework/deferred_discoveries.jsonl` and extracts entities deterministically:

- Module / file paths via path-regex matching against the project tree.
- Flaw-classification labels (the same fixed vocabulary v1.0 uses).
- Context-signature components (the existing six-field dict from `core/hooks/_context_signature.py`).
- Error-pattern lexemes (lifted from existing PHASE_12_LEXICON-style bounded lists; new lexicons added per recurring class observed).

A directed graph is built: nodes are entities; edges are co-occurrence in the same deferred-discovery entry; weight is co-occurrence frequency over a sliding window. The graph is persisted as a derived chain stream (proposed name to be specced — same `cp7-chained-v1` envelope so Pillar 2 invariants are preserved).

Hot-path budget: extraction is regex + dictionary lookup, no LLM. Per-entry cost is bounded by entity-vocabulary size; the workers run nightly, not in PreToolUse. Layer-3-grounding discipline applies — every claimed entity must grep against the project tree.

**Step 2 — Reflective Session (LLM-driven, operator-gated).**

A new subcommand under `episteme evolve` (proposed name to be specced) operates on the discovery graph:

- It identifies clusters: high-weight subgraphs whose member entries share ≥ N entities and span ≥ M days. Defaults are operator-tunable; vision-draft proposes N = 3, M = 7 — auditable in the audit record.
- For each cluster, it composes a structured prompt for the LLM: the cluster's entries (entry texts only, no surrounding context the LLM doesn't need), the shared entities, the cluster's time span, the project's `core/memory/global/cognitive_profile.md` and active blueprints. The prompt asks: *"What is the SINGLE root-cause architectural flaw these N entries point at, if any? If they are coincidental, say so."*
- The LLM drafts a Macro Change Proposal: a root-cause hypothesis, a proposed remediation that would close the entire cluster, a verification trace (observable + threshold) that would falsify the hypothesis if the remediation does not actually fix things.
- The Macro CP is written to a holding area for operator review — never auto-merged, never auto-promoted to `docs/NEXT_STEPS.md`. This carries forward Phase 12's D3 countermeasure: the LLM proposes; the operator disposes.

**Step 3 — Macro CP & Cascade Closure.**

If the operator accepts the Macro CP, it is promoted to a named CP in `docs/NEXT_STEPS.md` (operator-driven; the kernel does not write to authoritative docs). Once the CP executes and merges, a closure protocol fires:

- A single chain entry references the resolving commit and the cluster identifier (a deterministic hash over the cluster's member-entry IDs). This entry's payload claims: *commit X resolves deferred-discovery entries [ID-1, ID-2, ..., ID-N]*.
- Each member entry is hash-chained with its own closure annotation pointing at the same single closure entry. The append-only invariant is preserved — closures are new entries, not edits of old entries.
- Future audits of the deferred-discoveries stream filter closed clusters by default; an explicit flag re-includes them for archaeological review.

If the operator rejects the Macro CP, the rejection is also chained: *"cluster K considered, root-cause hypothesis Y rejected because Z, member entries remain open."* This is the Pillar 2 promise applied to negative decisions — what the operator declined to do is as load-bearing as what they did.

### Goodhart resistance — Causal Synthesis specifics

- **D6 · Cluster threshold is auditable (new).** The minimum entries-per-cluster and minimum-time-span are operator-tunable; abnormally low thresholds (a cluster of 2 entries proposing a Macro CP) surface as a parameter-tuning event in the audit, not silently. A tighter threshold demands stronger evidence; a looser threshold makes false-clusters more likely.
- **D7 · Per-entry independent verification on closure (new).** A Macro CP's commit must produce per-entry verification — each closed entry's individual claim is independently checked against the post-resolution episodic record. A wrong root-cause hypothesis would close N entries, but the per-entry verification would mark M < N of them as `claimed-resolved-but-evidence-missing`, surfacing the macro-failure rather than hiding it.
- **D3 · Re-elicitation carries forward.** The LLM never directly modifies authoritative state. The operator gates every promotion.

### Verification gate (proposed)

Causal Synthesis ships when, after a 60-day window: ≥ 3 Macro CPs have been proposed; ≥ 1 has been accepted by the operator; the accepted Macro CP closed ≥ 5 deferred-discovery entries with per-entry verification at ≥ 80% claimed-resolved-and-evidence-present rate; ≥ 1 Macro CP has been *correctly rejected* by the operator (the kernel proposed a wrong cluster and the operator caught it — this is a *positive* signal that the operator-gate is doing real work).

---

## v1.1 cognitive arm C · Self-Consistency Convergence

> *The endgame is structural self-consistency. The chain becomes evidence of, not basis for, correctness. The kernel ceases to be a "governance logging system" and becomes a true "Reasoning Engine."*

### Problem statement (causal-chain)

Every mechanism in v1.0 — and the two v1.1 arms above — is *reactive in the limit*. Even Pillar 3's active-guidance loop is reactive in posture: the kernel waits for an op to arrive, then surfaces guidance. The endgame the operator points at asks a stronger question: *can the system reach a state where it is structurally impossible to enter a configuration that would require detection?*

The honest answer is *no, never fully*. But progress toward the asymptote is measurable. The convergence arc is:

- v1.0 makes records of reasoning trustworthy.
- v1.1 arm A makes those records *time-aware* — past records can be falsified by present evidence.
- v1.1 arm B makes those records *cluster-aware* — many entries can collapse into one root-cause.
- v1.1 arm C makes the records' *underlying claims structurally consistent with each other* — and, eventually, deductive enough that the records become evidence of, not basis for, the kernel's reasoning correctness.

This is asymptotic by construction. The discipline is not reaching the asymptote; the discipline is being honest about which step you are currently at.

### Mechanism — three concrete v1.1 sub-deliverables

**(a) Per-blueprint invariant declaration.**

Each named blueprint (A · B · C · D and the generic fallback) currently declares its required fields, its selector triggers, and its synthesis arm if any. v1.1 adds an invariants section: *"any protocol synthesized by this blueprint must satisfy [property P1, P2, ...] when read against any other protocol from the same blueprint."* Examples (proposed; operator-reviewable):

- Axiomatic Judgment invariant: two protocols with identical context-signatures cannot prescribe contradictory actions. If a fresh synthesis would create such a pair, the kernel refuses synthesis and surfaces a contradiction event for operator review.
- Fence Reconstruction invariant: two protocols with the same constraint-removal pattern cannot have opposite verdicts (constraint safe to remove vs. unsafe to remove). Same refuse-and-surface flow.
- Consequence Chain invariant: two protocols with the same op-class and same first-order effect cannot have contradictory second-order claims.
- Architectural Cascade (Blueprint D) invariant: two protocols on the same blast-radius shape cannot disagree on patch-vs-refactor verdict.

The cross-protocol consistency check fires at synthesis time, not at audit time — so the contradiction is caught before the framework gains a silent disagreement.

**(b) Protocol-to-model promotion.**

When N protocols (operator-tunable; vision-draft proposes N = 5) accumulate in a single context-signature class and converge on a common rule (the rule is invariant across all N — same `if-then` shape modulo context), the kernel proposes promotion: the per-case protocol becomes a *model* — a structural axiom in the next synthesis layer. Models are operator-reviewed before promotion (Phase 12 D3 carries forward).

A model is operationally distinct from a protocol:

- A protocol describes *"in context X, do Y"* and is consulted as advisory at PreToolUse.
- A model describes *"contexts of class C share invariant I"* and is consumed by future synthesis as a precondition: a fresh protocol in a context of class C is held to invariant I, refused if it would violate, accepted only if compatible.

This is the convergence arrow: per-case protocols → context-class models → invariant axioms → structural deduction.

**(c) Auto-disconfirmation generation.**

Once a model exists, observable falsification conditions can be derived from it: the model claims invariant I; falsifying I requires an observation of behavior O. The kernel auto-attaches O as the default `disconfirmation` field for any matching context-signature. The operator can override the auto-derived disconfirmation but cannot leave the field blank — the same v1.0 anti-vapor invariant holds.

This is the Cognitive Deskilling counter at v1.1 scale: the operator's burden of authoring disconfirmation conditions decreases as models accumulate, but the *structural commitment to falsifiability* increases — every Reasoning Surface in a model-covered context inherits a disconfirmation condition derived from the structural invariant rather than the operator's per-case intuition.

### Goodhart resistance — Convergence specifics

- **D8 · Model promotion requires N protocols across DIFFERENT contexts (new).** Five protocols all from the same project, same operator, same week is not convergence — it's pattern-match within a narrow window. The promotion gate requires N protocols that span at least M contexts (different repos, different op-classes, different operators where applicable). Carries forward the v1.0 D1 multi-signature pattern at the meta-level.
- **D9 · Models inherit decay (new).** Every promoted model carries the same time-validity contract as protocols (cognitive arm A applies uniformly). A model is not a forever-axiom; it is an axiom *for as long as the underlying observations support it*. Sufficient contradicting evidence demotes the model and (on operator review) retires it.
- **D10 · Auto-disconfirmation is operator-overridable (new).** The kernel proposes the disconfirmation; the operator can override. Override events are chained — abnormally high override rate on auto-derived disconfirmations surfaces as a model-quality drift signal.
- **D3 · Re-elicitation carries forward.** Every model promotion is operator-gated. Models do not auto-promote.

### What the asymptote looks like (and does not look like)

What it looks like:

- Hash chains continue to exist. They are now evidence of, not basis for, the kernel's reasoning correctness.
- A given Reasoning Surface in a model-covered context is structurally complete on the agent's first pass — knowns + assumptions are constrained by the model, disconfirmation is auto-derived, unknowns are the operator's residual.
- Most contradictions are caught at synthesis, not at audit. Most root-cause clusters resolve before reaching the threshold. Most decayed protocols are caught by their own falsification condition firing rather than by the audit.

What it does not look like:

- Hash chains gone. (They never go.)
- Operator out of the loop. (D3 holds at every level.)
- Self-rewriting framework. (D3 holds at every level.)
- Magical correctness. (The kernel does not become smarter than the substrate it sits on; it becomes *more disciplined* about what its substrate cannot know.)

### Verification gate (proposed)

Self-Consistency Convergence ships its v1.1 minimum when, after a 90-day window: ≥ 1 cross-protocol consistency check has fired and been operator-confirmed; ≥ 1 protocol-to-model promotion has been proposed; ≥ 0 auto-derived disconfirmations have been operator-rejected (the rate is itself the signal — a 0% rejection rate is suspicious; a 100% rejection rate is broken; the honest target is operator-tunable).

The full asymptote is *not* a v1.1 deliverable. v1.1 ships *one measurable step toward* it.

---

## Threat model — what could break v1.1

| # | Threat | Surface | Counter |
|---|---|---|---|
| 1 | **Protocol churn erodes framework trust.** Aggressive decay marks too many protocols dead, the active-guidance loop goes silent, the agent regresses to v1.0 default behavior. | Cognitive arm A. | Decay rate is a Phase 12 audit signal (D5). Abnormal churn surfaces as drift, not silently. Operator can re-tune the decay threshold per blueprint. |
| 2 | **False clusters waste operator attention.** The discovery graph over-fits on noise; the reflective session generates Macro CPs that are pattern-match without architectural substance. | Cognitive arm B. | Cluster threshold is auditable (D6). Per-entry independent verification on closure (D7) — a wrong macro hypothesis closes N but only verifies M < N, surfacing failure. |
| 3 | **Model ossification turns axioms unfalsifiable.** A promoted model becomes a fence whose original purpose drifts; new evidence is rejected because it contradicts the model rather than the model being decayed by the new evidence. | Cognitive arm C. | Models inherit decay (D9). The same time-validity contract applies. Sufficient contradicting evidence demotes the model. |
| 4 | **Endgame Goodhart — agents game the convergence asymptote.** A sufficiently-aware agent emits protocols that *look* consistent with each other (sharing surface vocabulary) but encode nothing falsifiable, producing a fast-promoted model that locks in vapor. | Cognitive arm C. | Model promotion requires N protocols across DIFFERENT contexts (D8). Same-window same-operator same-project clusters do not promote. Multi-signature convergence at the meta-level. |
| 5 | **Operator-attention bottleneck.** v1.1's mechanisms generate operator-gate events (decay re-elicitations, cluster Macro CPs, model promotions, auto-disconfirmation overrides). At scale, the operator cannot keep up; gates rubber-stamp; D3 quietly fails. | All three arms. | Operator-attention budget is itself a Phase 12 axis. Abnormally fast gate-clearance times (operator clearing 10 gates / minute) surface as `attention_bottleneck` drift. The kernel watches for the operator's own discipline decaying. |
| 6 | **Cross-tool drift.** v1.1 mechanisms ship in the Claude Code adapter first; Codex / opencode / Hermes adapters lag. An operator using multiple adapters sees inconsistent kernel behavior. | All three arms; cross-cutting. | Adapter-parity is a v1.1 GA gate (named in `docs/POST_SOAK_TRIAGE.md` discipline). Adapter-specific gaps are documented-as-deferred at each landing. |

The four prior load-bearing v1.0 countermeasures (D1 multi-signature convergence, D2 retrospective-only computation, D3 re-elicitation never auto-edit, D4 named-limit honesty) carry forward into v1.1 unchanged. The v1.1 additions (D5 decay rate as audit signal, D6 cluster threshold auditable, D7 per-entry verification on closure, D8 promotion requires diverse contexts, D9 models inherit decay, D10 auto-disconfirmation overridable) extend the family.

---

## Out of scope (declared non-goals)

These are explicit non-goals — naming them prevents scope creep and silent-import from adjacent ecosystems.

1. **No auto-merge of Macro CPs without operator gate.** D3 re-elicitation discipline is non-negotiable. The kernel proposes; the operator disposes. v1.1 does not relax this.
2. **No removal of the hash chain.** The chain is evidence-of correctness in the asymptote, but it never goes away. A future where the chain is "unnecessary" is a future where the chain is *redundant with structural deduction*, not a future where it has been deleted. v1.1 does not propose deletion at any stage.
3. **No LLM in the hot-path entity extraction.** The < 100 ms hot-path budget holds. Cognitive arm B's Step 1 is regex + dictionary lookup. The LLM enters at Step 2 in the reflective layer, off the hot path.
4. **No retraction of v1.0 commitments.** Pillars 1-3, the four named blueprints, the generic max-rigor fallback, the BYOS stance, the < 100 ms hot-path ceiling, the 10% → 5% sample-rate schedule — all carry forward unchanged. v1.1 extends; v1.1 does not contradict.
5. **No replacement of the operator profile or cognitive profile schemas.** Phase 12's profile-audit loop continues operating at v1.1; new audit signals (decay rate, cluster threshold, model promotion rate, attention bottleneck) are *additive axes*, not a re-architecture of the schema.
6. **No automatic profile-axis mutation.** Phase 12's D3 — the loop writes a *prompt* for the operator, never a profile mutation — applies at v1.1 unchanged. New v1.1 audit signals follow the same discipline.
7. **No promise that the convergence asymptote is reached in v1.1.** The v1.1 deliverable is *one measurable step* per cognitive arm. The asymptote is direction, not deliverable.

---

## Proposed CP plan (PROVISIONAL — not yet approved)

> **Status: vision-draft proposal.** No CP under this plan begins until the v1.1 spec status flips from `drafted (vision)` to `approved`. The CP names below namespace the v1.1 work to avoid colliding with v1.0 / v1.0.1 CP identifiers.

### Cognitive arm A · Temporal Integrity (proposed CPs)

1. **CP-DECAY-01** — Validity-block schema additions to the existing protocol envelope; new audit subcommand under `episteme evolve` that compares protocols against episodic records over a 30-day window; supersession-write flow on operator-confirmed retirement.
2. **CP-DECAY-02** — Falsification-condition validation gate at synthesis time. A blueprint's synthesis arm cannot emit a protocol with a missing or fluent-vacuous falsification condition. Carries forward v1.0's anti-vapor invariant to the protocol-level.
3. **CP-DECAY-03** — Phase 12 audit gains the decay-rate axis. Abnormal churn surfaces as `protocol_churn` drift signal in the audit report.

### Cognitive arm B · Causal Synthesis (proposed CPs)

4. **CP-CLUSTER-01** — `tools/discovery_graph.py` background worker (or whatever the operator names it at first review): zero-LLM entity extraction + graph builder; persists to a derived chain stream under the existing `~/.episteme/framework/` path tree.
5. **CP-CLUSTER-02** — New reflective-session subcommand under `episteme evolve`: cluster identification, LLM prompt composition, Macro CP draft to a holding area for operator review.
6. **CP-CLUSTER-03** — Closure protocol: single chain entry per cluster resolution; per-entry annotation pointing back at the closure entry; per-entry independent verification that surfaces wrong-macro-hypothesis as M < N closures-with-evidence.

### Cognitive arm C · Self-Consistency Convergence (proposed CPs)

7. **CP-MODEL-01** — Per-blueprint invariant declarations (one section per named blueprint); cross-protocol consistency check at synthesis time; refuse-and-surface flow on contradiction.
8. **CP-MODEL-02** — Protocol-to-model promotion: detection of N converging protocols across M contexts; operator-gated promotion to a new `models` chain stream.
9. **CP-MODEL-03** — Auto-disconfirmation generation from models; auto-attach as default for matching context-signatures; operator override flow with chained override events.

### Sequencing and dependencies

```
  CP-DECAY-01 ──→ CP-DECAY-02 ──→ CP-DECAY-03
                                       │
                                       ├──→ Phase 12 axis adds
                                       │
  CP-CLUSTER-01 ──→ CP-CLUSTER-02 ──→ CP-CLUSTER-03
                                       │
                                       ├──→ Macro CP holding area
                                       │
  CP-MODEL-01 ──→ CP-MODEL-02 ──→ CP-MODEL-03
       │                              │
       └──── depends on CP-DECAY-01 ──┘
                  (validity-block schema)
```

CP-DECAY-01 is the prerequisite for CP-MODEL series because models inherit decay (D9). CP-CLUSTER series can ship independently of either.

Estimated calendar: 3-5 weeks per arm, sequenced after operator approves the v1.1 spec post-soak. Total v1.1 delivery window: ~3 months from approval.

---

## Verification gates (consolidated)

| Arm | Window | Gate |
|---|---|---|
| A · Temporal Integrity | 30 days post-CP-DECAY-03 | ≥ 1 valid decay confirmed; false-positive decay rate within operator tolerance; active-guidance loop demonstrably skips decayed protocols. |
| B · Causal Synthesis | 60 days post-CP-CLUSTER-03 | ≥ 3 Macro CPs proposed; ≥ 1 accepted; accepted CP closes ≥ 5 entries at ≥ 80% per-entry verification rate; ≥ 1 correctly rejected (operator catches a wrong cluster). |
| C · Self-Consistency Convergence | 90 days post-CP-MODEL-03 | ≥ 1 cross-protocol consistency check fires; ≥ 1 protocol-to-model promotion proposed; auto-derived disconfirmation override-rate within operator-honest target. |

Failure of any gate triggers operator review of the corresponding arm's mechanism, not silent re-tuning.

---

## Relationship to v1.0 spec and existing roadmap

This document **extends** `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`. Every load-bearing v1.0 commitment carries forward unchanged:

- Three pillars (Cognitive Blueprints · Hash Chain · Framework Synthesis & Active Guidance).
- Four named blueprints (A · Axiomatic, B · Fence, C · Consequence, D · Architectural Cascade) + generic max-rigor fallback.
- BYOS (bring-your-own-skill) stance.
- < 100 ms hot-path p95 ceiling.
- 10% → 5% spot-check sample rate at 30 days.
- Hash-chain scope (episodic + pending contracts + framework protocols + deferred discoveries).
- Phase 12 profile-audit loop and its four named countermeasures (D1 · D2 · D3 · D4).
- The four canonical artifacts (reasoning-surface · decision-trace · verification · handoff).

This document **is referenced by** `docs/ROADMAP_POST_V1.md` as the architectural anchor for the v1.1+ branch. The roadmap remains the operational planning artifact (Day-7 branched paths, milestone themes, ecosystem-adopt analyses, audit log of removed items). This design document carries the architectural reasoning — *why* v1.1 has this shape, *what* the threat model is, *which* countermeasures hold across the new mechanisms.

This document **does not** retract anything in `docs/COGNITIVE_SYSTEM_PLAYBOOK.md`, `kernel/CONSTITUTION.md`, `kernel/REASONING_SURFACE.md`, `kernel/FAILURE_MODES.md`, or any kernel-tier file. The kernel files describe the *posture* the system installs; v1.1 extends the *mechanism* by which that posture is maintained over time.

---

## References

- `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` — v1.0 RC spec; the substrate this document extends.
- `docs/ROADMAP_POST_V1.md` — operational roadmap; cross-references this design doc for the v1.1+ branch.
- `docs/COGNITIVE_SYSTEM_PLAYBOOK.md` — practical cognitive + workflow operating protocol; load-bearing prose anchor for the kernel's posture.
- `docs/POST_SOAK_TRIAGE.md` — Day-7 gate-grading rubric and form-filling discriminator; v1.1 gates extend the same discipline.
- `kernel/CONSTITUTION.md` — root claim, four principles, eleven failure modes (9 v0.x + 2 v1.0 RC additions).
- `kernel/FAILURE_MODES.md` — named failure modes; mode 10 (`framework-as-Doxa`) is the named risk that motivates Cognitive arm A.
- `kernel/REASONING_SURFACE.md` — v0.x → v1.0 surface protocol; the schema v1.1 protocol-validity block extends.
- `kernel/MEMORY_ARCHITECTURE.md` — five memory tiers; v1.1's Causal Synthesis arm operates at the procedural-tier boundary.
- `kernel/PHASE_12_LEXICON.md` — bounded lexicon discipline; v1.1 Causal Synthesis Step 1 uses the same FP-averse pattern.
- `core/memory/global/agent_feedback.md` — universal-principled rules; v1.1 mechanisms must satisfy `Rule shape — positive vs negative system must be a conscious choice` at every gate.

---

## Operator review checklist

Before flipping status from `drafted (vision)` to `approved`, the operator should answer:

1. Does the **Pillar 4-6** naming continuation (Temporal Integrity · Causal Synthesis · Self-Consistency Convergence) match the operator's mental model, or is a different framing (cognitive arm / extension axis / discipline / layer) preferred?
2. Are the proposed v1.1 verification windows (30d / 60d / 90d) calibrated for the v1.1 cycle, or should they mirror the v1.0 90-day post-soak window across all arms?
3. Is **Cognitive arm C** ready to ship one measurable v1.1 step (CP-MODEL-01 cross-protocol consistency check), or should arm C stay as a documented direction-statement deferred to v1.2?
4. Are the proposed Goodhart counters D5-D10 sufficient, or does any v1.1 mechanism need an additional countermeasure?
5. Is the cross-tool parity assumption (Claude Code first, others follow) acceptable for v1.1, or should multi-adapter parity be a v1.1 GA gate?
6. Is anything missing? — a fourth structural epiphany the operator has surfaced since this draft was written, or an inter-epiphany consistency hole this synthesis has not seen.

Once answered, the spec status flips to `approved (reframed, first pass)` or further reframes are requested. v1.1 CP work begins after approval, post-v1.0-GA cut.
