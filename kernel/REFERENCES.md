# References

**Operational summary — primary sources (14) and what they anchor:**
- Kahneman → six-failure-mode taxonomy. Munger → latticework (Principle III). Boyd → OODA (Principle II + workflow tempo). Dalio → radical transparency (Assumptions without cover).
- Popper → Disconfirmation field. Shannon → signal vs noise. Polanyi → tacit/explicit boundary (Kernel Limits 4). Meadows → orientation as system structure. Alexander → composable partial models. Deming → PDSA ancestry of the workflow loop. Simon → bounded rationality. Argyris & Schön → espoused vs in-use theory. Graham + Orwell → plain language as Principle I. Taleb → antifragility. Pearl → causal reasoning.

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
