# References

**Operational summary — primary sources (23) and what they anchor:**
- Kahneman → six-failure-mode taxonomy. Munger → latticework (Principle III). Boyd → OODA (Principle II + workflow tempo). Dalio → radical transparency (Assumptions without cover).
- Popper → Disconfirmation field. Shannon → signal vs noise. Polanyi → tacit/explicit boundary (Kernel Limits 4). Meadows → orientation as system structure. Alexander → composable partial models. Deming → PDSA ancestry of the workflow loop. Simon → bounded rationality. Argyris & Schön → espoused vs in-use theory. Graham + Orwell → plain language as Principle I. Taleb → antifragility. Pearl → causal reasoning.
- Ashby → requisite variety (why fixed rule-sets lose to general-capability agents; grounds escalation-by-default in the hook layer). Gall → working-simple precedes working-complex (grounds the evolution contract's incremental posture). Tetlock → calibration culture (what the telemetry loop is actually *measuring*; grounds the friction analyzer's target). Jaynes / Laplace → probabilistic inference (grounds the evidence-weighted update mechanic on assumptions). Goodhart / Strathern → measure-as-target drift (grounds scorecard audit discipline and the kernel's refusal to freeze the profile). Klein → recognition-primed decision (expert pattern-matching as legitimate tool, not System-1 failure; grounds the `tacit_call` marker). Chesterton → the fence (grounds constraint-preservation before removal; referenced in governance-layer failure modes). Feynman → self-deception as first-person failure mode (sharpens Principle I without renaming it). Festinger → cognitive dissonance (sharpens the confidence/accuracy counter — evidence conflicts with belief and belief usually wins).

Full concept→kernel-wording maps below. Introducing a new load-bearing concept into kernel wording without a primary-source entry here violates Principle I.

---

The kernel body does not import jargon from external frameworks. Concepts
are described in the kernel's own vocabulary so the principles stand on
their own, without requiring the reader to already know the source
material.

This file is the attribution trail. It names the sources the kernel
borrows from, what concept was borrowed, and where the concept shows up
in the kernel (usually under different wording). It exists so the kernel
can uphold its own Principle I — explicit over implicit — about its own
intellectual lineage.

If a concept below can no longer be traced to something in the kernel,
its attribution has lapsed and the entry should be removed.

---

## How to read this file

**Primary sources** are load-bearing: if you removed the concept, a
principle or artifact would lose its operational shape.

**Secondary sources** inform tone, a single phrase, or a framing device.
Removing them would not collapse a principle; losing the influence would
only flatten the voice.

Every entry names the specific concept borrowed and points to where it
appears in the kernel. Attribution is not a reading list — it is a map
from an idea's origin to its operational form here.

---

# Primary sources (load-bearing)

## Behavioral economics / cognitive psychology

**Daniel Kahneman — *Thinking, Fast and Slow* (2011).**

Informs the failure-mode framing in [CONSTITUTION.md](./CONSTITUTION.md)
and [FAILURE_MODES.md](./FAILURE_MODES.md). The kernel's core claim —
that the danger is confident wrongness, not incompetence — is Kahneman's
dual-process theory applied to fluent language models.

| Source term                | Kernel wording                                            |
|----------------------------|-----------------------------------------------------------|
| System 1 / System 2        | "pattern-matching" / "deliberate examination"             |
| WYSIATI                    | "reasoning only from what is present"                     |
| Question substitution      | "answering a nearby easier question"                      |
| Anchoring                  | "first-framing persistence"                               |
| Narrative fallacy          | "story-fit over evidence"                                 |
| Planning fallacy           | "systematic underestimation of effort and risk"           |
| Overconfidence             | retained as "confidence exceeding accuracy"               |

---

## Mental models / multidisciplinary reasoning

**Charlie Munger — speeches and *Poor Charlie's Almanack* (2005).**

Informs Principle III (*No model is sufficient alone*) in
[CONSTITUTION.md](./CONSTITUTION.md). The requirement to apply at least
two lenses from different disciplines before an irreversible decision is
Munger's multidisciplinary habit formalized into the kernel's protocol.

| Source term                    | Kernel wording                                          |
|--------------------------------|---------------------------------------------------------|
| Latticework of mental models   | "stack of lenses from different disciplines"            |
| Inversion                      | "failure-first: what would definitely cause failure?"   |
| Margin of safety               | "buffer if assumptions slip by 30–50%"                  |

The margin-of-safety concept is Munger via Benjamin Graham; see the
*Asymmetric risk* section below.

---

## Strategy / decision under tempo

**John Boyd — OODA loop (1970s–80s, via briefings and lectures;
collected in *The Essence of Winning and Losing*).**

Informs Principle II (*Orientation precedes observation*) and Principle
IV (*The loop is the unit of progress*) in
[CONSTITUTION.md](./CONSTITUTION.md). Orient as the dominant step — not
Observe — is the insight that grounds the kernel's entire claim to be
"orientation infrastructure."

| Source term                    | Kernel wording                                  |
|--------------------------------|-------------------------------------------------|
| Observe–Orient–Decide–Act      | "feedback loop" / "closed loop"                 |
| Orient (as dominant step)      | "orientation precedes observation"              |
| Loop speed / tempo             | "speed of iteration beats size of any step"     |

Deming's PDSA cycle (below) predates OODA and covers similar ground from
the quality-management lineage. The kernel's loop is closer in spirit to
Boyd's (emphasis on orientation as the highest-leverage step) than to
Deming's (emphasis on statistical control), but both are in the lineage.

---

## Principles / radical transparency

**Ray Dalio — *Principles: Life and Work* (2017).**

Informs Principle I (*Explicit > implicit*) and the counter to
"confidence exceeding accuracy" in [FAILURE_MODES.md](./FAILURE_MODES.md).

| Source term                     | Kernel wording                                          |
|---------------------------------|---------------------------------------------------------|
| Radical transparency            | "expose the model, including the parts that are wrong" |
| Believability-weighting         | "weight by track record, not volume or confidence"      |

Radical transparency assumes the psychological conditions for it to not
become coercive. The kernel acknowledges this tension — see Edmondson
under *Secondary sources*.

---

## Philosophy of science — falsifiability

**Karl Popper — *The Logic of Scientific Discovery* (1934, tr. 1959);
*Conjectures and Refutations* (1963).**

Grounds the Disconfirmation field in
[REASONING_SURFACE.md](./REASONING_SURFACE.md). A claim that cannot be
falsified is not a claim about the world; it is a story. The kernel
makes this Popperian requirement operational: every consequential
decision must name, in advance, the observable outcome that would prove
the plan wrong.

| Source term                     | Kernel wording                                          |
|---------------------------------|---------------------------------------------------------|
| Falsifiability                  | "disconfirmation" (the named observable outcome)        |
| Conjecture and refutation       | "plan as a bet, verified against disconfirmation"       |
| Demarcation criterion           | "a plan that cannot be falsified is a story, not a plan"|

Lakatos's refinement (research programmes with a protective belt) is
more accurate for how theories actually resist falsification in
practice, and is noted under *Secondary sources* for completeness.

---

## Information theory — signal and noise

**Claude Shannon — *A Mathematical Theory of Communication* (1948).**

The "signal vs noise" vocabulary used throughout the kernel's workflow
policy is Shannon's. The kernel uses it loosely — as a metaphor for
decision inputs — rather than technically, but the source must be named.

| Source term                     | Kernel wording                                          |
|---------------------------------|---------------------------------------------------------|
| Signal vs noise                 | "signal-over-noise rules" in workflow policy            |
| Channel capacity / bandwidth    | implicit in "what evidence is justified by signal only" |

Using "signal/noise" without naming Shannon is the kind of attribution
lapse this file is meant to catch.

---

## Organizational learning — single-loop vs double-loop

**Chris Argyris & Donald Schön — *Theory in Practice* (1974);
Argyris — *Teaching Smart People How to Learn* (1991).**

Grounds the Evolution Contract's propose → critique → gate → promote
loop in [docs/EVOLUTION_CONTRACT.md](../docs/EVOLUTION_CONTRACT.md).
Single-loop learning adjusts actions inside a fixed frame.
Double-loop learning changes the frame itself. The kernel's evolution
loop is designed to support both: promoting a durable lesson into
authoritative policy *is* a frame update, and the gates exist to make
frame updates accountable rather than silent.

| Source term                         | Kernel wording                                        |
|-------------------------------------|-------------------------------------------------------|
| Single-loop learning                | "adjust execution inside the current cycle"           |
| Double-loop learning                | "promote a lesson into authoritative policy"          |
| Espoused theory vs theory-in-use    | "declared policy vs observed behavior" (audit target) |

---

## Design / pattern languages

**Christopher Alexander — *A Pattern Language* (1977);
*The Timeless Way of Building* (1979).**

Grounds the proposed `core/patterns/` library: a set of named reasoning
protocols keyed by decision type. Alexander's insight — that recurring
design problems have recurring structural solutions, and naming them
creates a shared vocabulary — is exactly what the kernel aims to produce
for cognitive work, not architecture.

| Source term                     | Kernel wording                                              |
|---------------------------------|-------------------------------------------------------------|
| Pattern (named solution form)   | "named reasoning protocol keyed by decision type"           |
| Pattern language (composable)   | "library of patterns referenced from the reasoning surface"  |
| "Quality without a name"        | the implicit standard the kernel keeps trying to surface    |

If the pattern library is built, this section carries the full weight.

---

## Tacit knowledge — limits of explicit capture

**Michael Polanyi — *Personal Knowledge* (1958);
*The Tacit Dimension* (1966).**

The honest counterweight to Principle I (*Explicit > implicit*).
Polanyi's claim — *we know more than we can tell* — is not a denial of
explicit reasoning; it is an observation that some forms of knowledge
(skills, perceptions, pattern recognition earned over years) resist
being reduced to rules without loss.

Cited in [KERNEL_LIMITS.md](./KERNEL_LIMITS.md) as a declared limit on
the kernel's own thesis. The kernel claims explicit > implicit
*operationally*, for consequential decisions under uncertainty. It does
not claim every form of knowledge can or should be made explicit.

| Source term                     | Kernel wording                                          |
|---------------------------------|---------------------------------------------------------|
| Tacit knowledge                 | "some judgment resists capture without distortion"      |
| "We know more than we can tell" | declared limit on Principle I in KERNEL_LIMITS.md       |

---

## Asymmetric risk / margin of safety

**Benjamin Graham — *The Intelligent Investor* (1949).**
**Nassim Nicholas Taleb — *Fooled by Randomness* (2001);
*The Black Swan* (2007); *Antifragile* (2012);
*Skin in the Game* (2018).**

Graham originated *margin of safety* as an investing discipline; Taleb
generalized it into asymmetric-payoff reasoning and via-negativa
thinking (what to avoid is more reliable than what to pursue).

Informs the *buffer* component of Principle III's decision stack and the
risk-and-autonomy policy in operator workflow.

| Source term                     | Kernel wording                                                  |
|---------------------------------|-----------------------------------------------------------------|
| Margin of safety (Graham)       | "buffer if assumptions slip by 30–50%"                          |
| Convexity / antifragility       | implicit in "prefer small reversible actions"                   |
| Via negativa                    | "eliminate failure paths before optimizing success paths"       |
| Skin in the game                | authority principle: project docs over tool-native memory       |

---

## Control theory — requisite variety

**W. Ross Ashby — *An Introduction to Cybernetics* (1956); *Design for a
Brain* (1952).**

Grounds the architectural claim in
[KERNEL_LIMITS.md](./KERNEL_LIMITS.md) that a rule-based governance
layer cannot constrain a general-capability agent through fixed pattern
matches alone. Ashby's law — *only variety can destroy variety* — is the
direct explanation for why the hook layer must escalate to human
judgment when an action's shape exceeds the controller's declared
coverage, rather than silently failing open.

| Source term                     | Kernel wording                                                    |
|---------------------------------|-------------------------------------------------------------------|
| Law of requisite variety        | "controller coverage must match the controlled system's variety"  |
| Ultrastability                  | "kernel invariants that survive local rule updates"               |
| Regulator theorem               | "escalate-by-default when action class exceeds rule coverage"     |

Without Ashby, the hook architecture reads as a security layer. With
Ashby, it reads as a cognitive-governance layer aware of its own
coverage gap.

---

## Working-simple precedes working-complex

**John Gall — *Systemantics* (1975); later *The Systems Bible*.**

Grounds the evolution-contract posture: a working complex system evolves
from a working simple system. Complex systems designed from scratch do
not work and cannot be patched into working. The kernel's insistence on
incremental, small-reversible changes — and its refusal to accept
large, ungated frame changes — is Gall's observation applied to
cognitive infrastructure.

| Source term                          | Kernel wording                                                         |
|--------------------------------------|------------------------------------------------------------------------|
| Gall's law (working → complex)       | "smallest reversible action that produces new information"             |
| Axioms of systemantics               | "the kernel compresses itself when stakes compress" (KERNEL_LIMITS 1)  |

---

## Calibration under uncertainty

**Philip Tetlock — *Expert Political Judgment* (2005);
*Superforecasting: The Art and Science of Prediction* (2015, with Dan
Gardner).**

Grounds what the calibration telemetry layer is actually *measuring*.
Tetlock's finding — that accuracy on forecastable questions is a
trainable skill, and that confidence uncorrelated with accuracy is the
dominant failure — is the empirical backing for the kernel's claim that
Assumptions + Disconfirmation + outcome logging produces better
decisions over time. The friction analyzer exists to surface the
Tetlock-style gap between predicted and observed.

| Source term                      | Kernel wording                                                    |
|----------------------------------|-------------------------------------------------------------------|
| Calibration (forecast accuracy)  | "predicted vs observed outcomes, joined by correlation_id"        |
| Granularity of probability       | "sharp unknowns over vague ones"                                  |
| Update-in-proportion-to-evidence | "move assumption to known only when evidence is decisive"         |
| Active open-mindedness           | "disconfirmation as required field, not optional field"           |

---

## Probabilistic inference

**Edwin Jaynes — *Probability Theory: The Logic of Science* (2003);
Pierre-Simon Laplace — *Essai philosophique sur les probabilités*
(1814).**

Grounds the evidence-weighted update mechanic described in
[REASONING_SURFACE.md](./REASONING_SURFACE.md). Assumptions are not
boolean claims that flip to "Known" on first contact with evidence;
they are weighted beliefs whose plausibility is updated in proportion
to the likelihood of the observation under competing hypotheses. The
kernel adopts the *discipline* of proportional updating without
requiring formal probabilistic machinery.

| Source term                       | Kernel wording                                                   |
|-----------------------------------|------------------------------------------------------------------|
| Posterior update                  | "updated plausibility + sharpened falsification condition"       |
| Likelihood ratio                  | "weight new evidence against competing hypotheses"               |
| Prior as inductive bias           | "semantic tier proposes; never autofills"                        |

---

## Measurement integrity — the law of the target

**Charles Goodhart — "Problems of Monetary Management" (1975);
Marilyn Strathern's formulation (1997) — *"When a measure becomes a
target, it ceases to be a good measure."***

Grounds the scorecard audit discipline in
[OPERATOR_PROFILE_SCHEMA.md](./OPERATOR_PROFILE_SCHEMA.md) and
[KERNEL_LIMITS.md](./KERNEL_LIMITS.md). A profile axis that is elicited
and then frozen becomes the operator's aspirational image, not their
operating posture. The kernel treats each axis as a hypothesis about
the operator — periodically re-audited against episodic evidence,
re-elicited if drift is observed. This is the counter to a failure mode
the kernel itself would otherwise introduce.

| Source term                     | Kernel wording                                                    |
|---------------------------------|-------------------------------------------------------------------|
| Goodhart's law                  | "no measure survives being targeted unchanged"                    |
| Measure-target drift            | "scorecard audited against outcome data, not frozen at elicitation"|

---

## Naturalistic decision making

**Gary Klein — *Sources of Power: How People Make Decisions* (1998);
*The Power of Intuition* (2003).**

The nuance on dual-process theory: not all fast pattern-matching is
System-1 failure. Expert recognition — Klein's recognition-primed
decision (RPD) — is fast, mostly accurate within the expert's calibrated
domain, and destroyed if forced through deliberate rule-following.

Grounds the `tacit_call` marker on decision records (Gap D in
KERNEL_LIMITS) and the `expertise_map` field in the operator profile.
The kernel honors both failure modes at once: confident wrongness from
naive pattern-matching, *and* destruction-of-skill from forcing
articulated reasoning over calibrated intuition.

| Source term                             | Kernel wording                                                       |
|-----------------------------------------|----------------------------------------------------------------------|
| Recognition-primed decision (RPD)       | "expert pattern-match as legitimate basis, recorded not fabricated"  |
| Mental simulation                       | "probe → sense → respond" (Complex-domain posture)                   |
| Expertise as calibrated intuition       | "expertise_map: domain → level + preferred_mode"                     |

---

## Constraint preservation

**G.K. Chesterton — *The Thing* (1929), the "fence" essay.**

Grounds the Fence-Check gate in the governance-layer failure modes
([FAILURE_MODES.md](./FAILURE_MODES.md)). Chesterton's rule — do not
remove a constraint until you can explain why it was put there —
translates directly into an agent-specific risk: models fluently
rationalize removing constraints they do not understand. The counter is
not "never remove" but "name the constraint's purpose before removing,
or route the removal to a human."

| Source term                     | Kernel wording                                                    |
|---------------------------------|-------------------------------------------------------------------|
| Chesterton's fence              | "no constraint is removed until its reason is named"              |

---

## Self-deception

**Richard Feynman — Caltech commencement address *"Cargo Cult Science"*
(1974); *Surely You're Joking, Mr. Feynman!* (1985).**

Sharpens Principle I without adding a new principle. Feynman's single
sentence — *"the first principle is that you must not fool yourself,
and you are the easiest person to fool"* — is the first-person form of
the kernel's confident-wrongness concern. Attribution is named here
because the phrasing shows up in kernel-adjacent writing and would
otherwise drift into "common sense."

| Source term                     | Kernel wording                                                    |
|---------------------------------|-------------------------------------------------------------------|
| Self-deception as first-person  | "the agent's model of itself is the first thing to audit"         |
| Cargo-cult form                 | "discipline that cannot name its own boundary is a creed"         |

---

## Motivated reasoning

**Leon Festinger — *A Theory of Cognitive Dissonance* (1957).**

Sharpens the counter to confidence-exceeding-accuracy in
[FAILURE_MODES.md](./FAILURE_MODES.md). When evidence conflicts with a
prior commitment, the cheaper resolution for a fluent reasoner is
reinterpretation of the evidence, not revision of the commitment.
Assumptions with falsification conditions are the kernel's defense:
the falsification was named *before* the commitment, which makes
after-the-fact reinterpretation visibly a move against the record.

| Source term                     | Kernel wording                                                    |
|---------------------------------|-------------------------------------------------------------------|
| Cognitive dissonance            | "evidence conflicts with commitment; the cheaper fix is narrative"|
| Belief perseverance             | "Assumptions with falsification named *in advance*"               |

---

## Causal reasoning — the ladder of causation

**Judea Pearl — *Causality* (2000, 2nd ed. 2009);
with Dana Mackenzie, *The Book of Why* (2018).**

Grounds the kernel's core distinction between *knowing* and
*pattern-matching toward a fluent answer*. Pearl's ladder — association,
intervention, counterfactuals — is the most operational framework
available for what it means to *know* something rather than correlate it.
For a cognitive kernel aimed at language models whose native mode is
level 1 (association), Pearl is the sharpest available lens.

| Source term                           | Kernel wording                                              |
|---------------------------------------|-------------------------------------------------------------|
| Ladder of causation (Levels 1–3)      | "knowing vs pattern-matching"                               |
| Intervention (do-operator)            | "small reversible action closes a feedback loop"            |
| Counterfactual reasoning              | "disconfirmation — what evidence would prove this wrong"    |

**v1.0 RC implementation note — honest translation.** The kernel does not
construct causal graphs or run do-calculus at the hook layer. Level 3
(counterfactual) is enforced via pattern-match proxies that are testable
inside the 100 ms hot-path budget: the Blueprint D cascade detector
(cross-surface-ref diff + refactor/rename lexicon + generated-artifact
symbol-reference check + self-escalation trigger), the Fence
Reconstruction `removal_consequence_prediction` + `rollback_path` smoke
test, and the Layer 4 `verification_trace` with `threshold_observable`.
These are *proxies for* counterfactual reasoning, not direct causal
verification. Direct causal-graph construction is out of RC scope; the
proxy set is the RC-shaped approximation. If a future blueprint requires
structural causal modeling beyond what patterns can catch, that is a
governance event, not an implementation tweak.

---

## Bounded rationality

**Herbert Simon — *Administrative Behavior* (1947);
*The Sciences of the Artificial* (1969); Nobel Memorial Prize 1978.**

Grounds the kernel's notion of *minimum viable explicitness*. Rational
actors under real cognitive and time constraints do not optimize; they
satisfice. The Reasoning Surface is a satisficing artifact: not the
complete analysis of a decision, but the minimum explicit set of
known/unknown/assumption/disconfirmation entries that is enough to act.

| Source term                     | Kernel wording                                                |
|---------------------------------|---------------------------------------------------------------|
| Bounded rationality             | "reasoning under incomplete information is the default case"  |
| Satisficing                     | "minimum viable explicitness before action"                   |
| Decision premises               | "knowns, unknowns, assumptions as scaffolding"                |

---

## Quality management — PDSA

**W. Edwards Deming — *Out of the Crisis* (1982);
*The New Economics* (1993); Plan-Do-Study-Act cycle, via Shewhart.**

Grounds Principle IV's loop orientation alongside Boyd. PDSA predates
OODA by decades and comes from quality management rather than military
strategy, but the structure is the same: closed cycles of intervention
and learning. The kernel's *speed of iteration beats size of step*
directly echoes Deming's insistence that continuous small improvements
compound.

| Source term                     | Kernel wording                                         |
|---------------------------------|--------------------------------------------------------|
| Plan-Do-Study-Act (PDSA)        | "Frame → Decompose → Execute → Verify → Handoff"       |
| Common-cause vs special-cause   | implicit in facts/inferences/preferences distinction   |
| "The System"                    | authority hierarchy (project > operator > runtime)     |

---

## Systems thinking — leverage points

**Donella Meadows — *Leverage Points: Places to Intervene in a System*
(1999); *Thinking in Systems* (2008, posth.).**

Grounds the kernel's claim that *orientation* is the highest-leverage
intervention point. Meadows' list ranks leverage points from lowest
(parameter tweaks) to highest (the paradigm — the shared worldview from
which the system's goals and structure arise). The kernel positions
itself exactly there: not as a tool for the agent's work, but as the
frame from which that work proceeds.

| Source term                        | Kernel wording                                              |
|------------------------------------|-------------------------------------------------------------|
| Leverage point (top of Meadows' 12)| "orientation infrastructure"                                |
| Paradigm / shared worldview        | "the kernel is the agent's worldview, made explicit"        |
| System's goals                     | "what does doing the work well look like?" (operator overview)|

---

# Convergent contemporary work — 2025–2026

These are NOT lineage. They are external works whose architectural choices
independently parallel the kernel's. The kernel's pillars and Reasoning
Surface predate the publications below (CP1 shipped 2026-04-21; v1.0.0 GA
2026-04-28). The pattern of convergence — multiple industry frameworks and
academic papers in 2025–2026 arriving at intent-bound execution, hash-chained
audit trails, pre-invocation checkpoints, and reason-based alignment — is
itself evidence that the kernel's architectural choices track an emerging
industry consensus rather than diverging from it.

This section exists for two purposes: (1) Principle I (explicit attribution)
when the kernel's marketing or README copy references these convergent
frameworks; (2) external validation that the kernel's three-pillar
architecture is part of a wider, peer-reviewed pattern.

## Agentic AI threat taxonomy — OWASP Top 10 for Agentic Applications (2026)

**OWASP Gen AI Security Project — *OWASP Top 10 for Agentic Applications*
(2026). Peer-reviewed by 100+ industry experts. https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/**

Validates the [Reasoning Surface](./REASONING_SURFACE.md) contract and the
*Zero-trust execution* table in the project README.

| OWASP threat                    | Kernel countermeasure                                        |
|---------------------------------|--------------------------------------------------------------|
| Direct Goal Manipulation        | Core Question field — agent commits intent before execution  |
| Indirect Instruction Injection  | Knowns / Disconfirmation — surface separates trusted state from prompt content |
| Memory Poisoning                | Pillar 2 hash-chained protocols — tamper-evident chain rejects silent rewrites |
| Tool Misuse / Overreach         | PreToolUse Reasoning Surface guard — refuses high-impact ops without surface  |
| Unbounded Action / Goal Drift   | Disconfirmation field — pre-committed observable that exits the loop          |

The OWASP framework was published in 2026 as the kernel's CP10 was already
shipped; concept overlap is convergent, not derivative.

## Structured cognitive loop — R-CCAM five-phase architecture

**Myung Ho Kim — *Bridging Symbolic Control and Neural Reasoning in LLM
Agents: Structured Cognitive Loop with a Governance Layer* (2025).
arXiv:2511.17673.**

Validates the [workflow loop](../core/memory/global/workflow_policy.md)
and the *Soft Symbolic Control* role assigned to the Reasoning Surface
guard. SCL's five phases (Retrieval, Cognition, Control, Action, Memory) are
structurally analogous to the kernel's Frame → Decompose → Execute → Verify
→ Handoff. SCL's "Soft Symbolic Control" governance layer maps onto the
kernel's PreToolUse hook layer: symbolic constraints applied to probabilistic
inference while preserving neural reasoning flexibility.

| SCL term                   | Kernel wording                                              |
|----------------------------|-------------------------------------------------------------|
| Retrieval / Cognition      | Frame (Knowns + Unknowns + Assumptions)                     |
| Control                    | Decompose (constraint regime declaration)                   |
| Action                     | Execute (admitted tool execution)                           |
| Memory                     | Verify + Handoff (telemetry + persistence)                  |
| Soft Symbolic Control      | Reasoning Surface guard at the PreToolUse boundary          |

Kim's empirical validation reports zero policy violations and complete
decision traceability — the same outcomes the kernel's CP3–CP10 chain is
designed to produce.

## Memory governance — Stability and Safety Governed Memory (SSGM)

**Carmen Lam, Jiawei Li, Lei Zhang, Kai Zhao — *Governing Evolving Memory
in LLM Agents: Risks, Mechanisms, and the SSGM Framework* (2026).
arXiv:2603.11768.**

Validates the [hash chain envelope](../core/hooks/_chain.py) and Cognitive
Arm A — Temporal Integrity. SSGM prescribes consistency verification +
temporal decay modeling + dynamic access control prior to memory
consolidation; the kernel's Pillar 2 (`cp7-chained-v1` envelope) and Arm A
(supersede-with-history) ship the same mechanism.

| SSGM mechanism             | Kernel implementation                                       |
|----------------------------|-------------------------------------------------------------|
| Consistency verification   | `verify_chain` — SHA-256 walk with break-index reporting    |
| Temporal decay modeling    | Arm A — protocol decay + operator-confirmed retirement      |
| Dynamic access control     | PreToolUse vapor-verdict filter in `_guidance.query`        |
| Decoupled memory evolution | Append-only chain — execution does NOT mutate prior records |

Lam et al.'s framework was published as Arm A v1.1.0-rc1 was being cut;
independent convergence on the same architectural choice.

## Reason-based alignment — Anthropic's Claude Constitution (2026)

**Anthropic — *Claude's Constitution* (published 2026-01-22).
https://www.anthropic.com/constitution**

Validates [CONSTITUTION.md](./CONSTITUTION.md) — the kernel's principle-first
posture. Anthropic's 2026 constitution shifts from rule-based to reason-based
alignment, providing the agent with the *logic behind* ethical principles
rather than prescriptive behavior lists. The kernel's CONSTITUTION.md
predates this and uses the identical posture: principles are stated with
their reasons, and the reason is what the agent applies in novel situations.

| Anthropic concept             | Kernel wording                                              |
|-------------------------------|-------------------------------------------------------------|
| Reason-based alignment        | "principles, not rules — the principle's reason is its load-bearing element" |
| 4-tier priority (safety/ethics/compliance/helpfulness) | implicit in failure-mode counter ordering   |
| Reflective revision           | Argyris–Schön double-loop (already cited under primary)     |

Released under CC0 by Anthropic; cited here for completeness, not borrowed.

## Pre-invocation checkpoint — Capsule Security ClawGuard (2026)

**Capsule Security — *ClawGuard* open-source pre-invocation checkpoint
(public release 2026-04-14). https://www.businesswire.com/news/home/20260415670902/**

Validates [reasoning_surface_guard.py](../core/hooks/reasoning_surface_guard.py)
— the same architectural pattern. ClawGuard adds a pre-invocation checkpoint
to assess agent intent before tool calls execute; the kernel's PreToolUse
Reasoning Surface guard does the same with a Knowns / Unknowns / Assumptions
/ Disconfirmation contract instead of intent vectors.

| Capsule concept             | Kernel wording                                                |
|-----------------------------|---------------------------------------------------------------|
| Pre-invocation checkpoint   | PreToolUse hook — refuses execution without valid surface     |
| Intent assessment           | Core Question field — declares what the action is for         |
| Runtime control             | exit-code 2 admission gate (vs. policy advisory log)          |

Independent industry convergence on the file-system-level interception
pattern.

## Five-pillar agent integrity — Proofpoint AIF (2026 Edition)

**Proofpoint — *The Agent Integrity Framework — 2026 Edition* (2026-03-16).
https://www.proofpoint.com/us/resources/white-papers/agent-integrity-framework**

Validates the kernel's three pillars + workflow lifecycle. Proofpoint's
five pillars (Intent / Identity / Behavior / Transparency / Auditability)
map onto the kernel's existing artifacts:

| Proofpoint pillar           | Kernel correlate                                              |
|-----------------------------|---------------------------------------------------------------|
| Intent                      | Core Question field; Reasoning Surface contract               |
| Identity                    | Operator profile + correlation_id stamping                    |
| Behavior                    | Calibration telemetry — predicted vs observed exit_code       |
| Transparency                | Hash-chained protocols — append-only, human-readable          |
| Auditability                | Phase 12 audit + `episteme review` + verify-chain CLI         |

Proofpoint's framework was published 2026-03-16 with the kernel's CP1–CP10
already shipped; the alignment is convergent, not derivative.

---

# Secondary sources (adjacent, shape tone or single concepts)

These inform the kernel's voice or contribute a specific phrase, but
removing them would not collapse a principle.

**John Dewey — *How We Think* (1910).** Reflective thinking as explicit
process; ancestor of the reflective-practice lineage through Schön.

**Donald Schön — *The Reflective Practitioner* (1983).** "Knowing-in-
action" and reflection-on-action; influences the kernel's framing of
Verify and Handoff as reflective acts, not reporting overhead.

**Peter Senge — *The Fifth Discipline* (1990).** Mental models as shared
infrastructure in organizations; generalizes Argyris for practicing
teams. Appears implicitly whenever the kernel talks about a worldview
that travels.

**Amy Edmondson — *The Fearless Organization* (2018); research on
psychological safety (1999–).** The precondition Dalio's radical
transparency needs to not become coercive. Cited in
[KERNEL_LIMITS.md](./KERNEL_LIMITS.md) as a declared limit on the
single-operator model.

**Ed Catmull — *Creativity, Inc.* (2014).** The Pixar Braintrust as
multi-lens review in a creative organization; a lived example of
Principle III in a team setting.

**George Orwell — *Politics and the English Language* (1946).** Clarity
as an ethical act, not merely a stylistic preference. Sits under
Principle I; the essay reads as Principle I in argument form.

**Stuart Russell — *Human Compatible* (2019).** AI alignment lens on the
"confident wrongness" failure mode; grounds why fluency ≠ correctness
is an alignment problem, not just an aesthetic one.

**Stuart Russell & Peter Norvig — *Artificial Intelligence: A Modern
Approach* (4th ed., 2021).** The canonical AI textbook; provides the
shared vocabulary for agent / rational-agent framing.

**Gary Marcus — *Rebooting AI* (2019, with Ernest Davis);
*The Algebraic Mind* (2001).** Critique of pure statistical learning;
sharpens the "pattern-matching vs knowing" distinction the kernel uses.

**Melanie Mitchell — *Artificial Intelligence: A Guide for Thinking
Humans* (2019).** Accessible framing of where modern AI systems are
brittle; useful vocabulary for explaining the failure modes to a
non-specialist reader.

**François Chollet — *On the Measure of Intelligence* (2019); ARC
benchmark.** Operational definition of intelligence as skill-acquisition
efficiency over a distribution of tasks; grounds why a portable kernel
is a more useful intervention than a tool-specific optimization.

**Imre Lakatos — *Falsification and the Methodology of Scientific
Research Programmes* (1970).** Refinement of Popper: theories resist
falsification through a protective belt of auxiliary hypotheses. Noted
as a sharper model for how disconfirmation plays out in practice than
naive falsification.

**David Allen — *Getting Things Done* (2001).** Capture-clarify-organize
discipline; the workflow stage structure owes something to GTD even when
it owes more to PDSA.

**Cal Newport — *Deep Work* (2016); *A World Without Email* (2021).**
Attention as scarce resource; informs the kernel's insistence on
authoritative docs over chat-native memory.

**Douglas Hofstadter — *Gödel, Escher, Bach* (1979); *I Am a Strange
Loop* (2007).** Self-reference and strange loops as deep structure of
cognition; appears whenever the kernel claims that the agent inhabits a
worldview rather than merely follows rules.

**Endel Tulving — *Elements of Episodic Memory* (1983); Larry Squire
— work on declarative vs procedural memory (1987–).** Grounds the
memory tier taxonomy in [MEMORY_ARCHITECTURE.md](./MEMORY_ARCHITECTURE.md)
— working, episodic, semantic, procedural. The kernel adapts the
human-memory taxonomy without importing the research terminology, and
adds a "reflective" tier by analogy with metacognition research.

**David Snowden — Cynefin framework (1999–).** The problem-domain
classification (Clear / Complicated / Complex / Chaotic) used as the
*domain* marker on the Reasoning Surface and in
[KERNEL_LIMITS.md](./KERNEL_LIMITS.md). The kernel borrows the
taxonomy; the *domain precedes the Surface* posture is the kernel's
own.

**Ludwig Wittgenstein — *Tractatus Logico-Philosophicus* (1921);
*Philosophical Investigations* (1953).** The limits of explicit
language as a medium for certain kinds of truth — the companion to
Polanyi on tacit knowledge. Cited for the Kernel Limits stance that
forcing legibility where language cannot carry it produces a legible
fabrication, not understanding.

---

# Positioning anchors

A distinct class of reference: academic work that does not feed the
kernel's design (the kernel existed before these were read) but provides
*vocabulary for what the kernel already does*. Cited here so that anyone
auditing the repository can cross-walk between this kernel's concrete
artifacts and adjacent academic framings. Load-bearing test differs from
Primary/Secondary — the question is not "would removing this concept
collapse a principle?" but "does this work name, in academic register,
the failure mode or mechanism the kernel mechanically enforces?"

**"Architecting Trust in Artificial Epistemic Agents" (2026 preprint;
authors + venue + full citation to be confirmed by operator).** Names
three primitives the episteme kernel mechanically enforces: *Epistemic
Drift* (the failure class the whole kernel is a feedforward counter to;
mapped to Modes 1 + 4 in `kernel/FAILURE_MODES.md` as the specific
reasoning shapes through which drift enters), *Robust Falsifiability*
(enforced at file-system boundary by the Disconfirmation field of the
Reasoning Surface; Strict Mode validator rejects conditional-but-
observable-less phrasing), *Knowledge Sanctuaries* (implemented by the
Pillar 3 protocol stream at `~/.episteme/framework/protocols.jsonl` —
tamper-evident + context-scoped + supersession-respecting). Two
adjacent concepts from the same framework — *Cognitive Deskilling*
(countered by the kernel's Human-prompt-debugging property) and
*Technical Provenance System* (Pillar 2 hash-chain across all four
framework streams) — are cited at the positioning level without a
direct failure-mode mapping. Full cross-walk: `kernel/FAILURE_MODES.md`
§ "Mapping to the epistemic-trust framework". Positioning claim the
cross-walk supports: *episteme is a socio-epistemic infrastructure for
Claude Code (and any future agent runtime), not a memory tool and not
a prompt wrapper.*

Body-text citation surfaces as of Event 43–44: `README.md` TL;DR section
(Epistemic Drift introduction); `README.md` § "The solution" (Robust
Falsifiability after the 5-field table); `README.md` § "Protocol
Synthesis" (Knowledge Sanctuaries reframe); `README.ko.md` at matching
three insertion points; `web/src/components/site/Hero.tsx` subparagraph;
`web/src/app/layout.tsx` metadata description; `kernel/FAILURE_MODES.md`
dedicated mapping section.

---

# How to read this

The kernel does not require familiarity with any of the source material
above. If a principle is unclear, read the kernel's own description
first, then consult the source if you want the deeper exposition.

Citations are deliberately linked from the kernel file that uses the
concept. The links exist so a reader auditing the kernel can trace every
borrowed idea to its origin, in one step.

---

# Attribution maintenance

This file is part of the kernel's self-audit. It is correct when:

- Every load-bearing concept in the kernel traces to a Primary source.
- Every Primary source is still reflected somewhere in the kernel.
- Every Secondary source still contributes at least a specific phrase.
- No concept is treated as native to the kernel that is actually borrowed.

If any of those conditions fails, the corresponding entry should be
added, moved, or removed. Attribution is not a reading list; it is a
map from idea to operational form.
