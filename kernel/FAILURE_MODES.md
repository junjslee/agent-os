# Failure Modes and Their Counters

**Operational summary — six modes ↔ counters:**

| # | Failure mode                          | Counter artifact                                      |
|---|---------------------------------------|-------------------------------------------------------|
| 1 | Reasoning only from what is present   | Unknowns field (Reasoning Surface)                    |
| 2 | Answering a nearby easier question    | Core Question (required in Frame)                     |
| 3 | First-framing persistence (anchoring) | Disconfirmation field                                 |
| 4 | Story-fit over evidence               | Facts / inferences / preferences split                |
| 5 | Systematic underestimation of risk    | Failure-first + 30–50% buffer (high-impact)           |
| 6 | Confidence exceeding accuracy         | Assumptions field + weight-by-track-record            |

Removing or bypassing a counter means naming which mode is now unprotected. If the answer is "none," the counter was not earning its place.

---

The [Constitution](./CONSTITUTION.md) names six failure modes as the reason
agents produce confident wrongness. This document maps each one to the
specific kernel artifact that counters it.

The mapping is the audit trail: every element of episteme exists against
a named failure mode. If a proposed change removes or bypasses one of these
artifacts, name which failure mode is now unprotected against. If the answer
is "none" — the artifact was not earning its place.

**These counters are feedforward, not feedback.** They are enforced before
execution begins, not applied as corrections after a failure is observed.
Each field of the Reasoning Surface is a pre-execution gate. An agent that
fills the Surface after acting is doing retrospective documentation, not
cognitive governance.

---

## The six modes

### 1. Reasoning only from what is present

**The mode.** The agent reasons from whatever is in the context window as
if that were the whole picture. Absence of information is not felt; the
model produces a coherent answer from whatever is there, and that coherence
is indistinguishable from sufficiency.

**Why fluent models are especially vulnerable.** A fluent model does not
experience the difference between "I have enough" and "I have what was
given." There is no internal flag for the missing piece.

**The counter.** The **Unknowns** field of the
[Reasoning Surface](./REASONING_SURFACE.md). A blank Unknowns section is
a refusal signal. The kernel treats it as evidence that nothing has been
examined, not as evidence that nothing is missing.

---

### 2. Answering a nearby easier question

**The mode.** When the actual question is hard, the generation process
silently swaps in a nearby easier question and answers that one. The answer
is fluent. It also addresses the wrong problem.

**Why fluent models are especially vulnerable.** The swap happens inside
generation and produces an answer that reads as responsive. There is no
"this is not the question that was asked" flag.

**The counter.** The **Core Question** requirement in the Decompose stage.
Every work cycle must name what it is actually trying to answer, in one
sentence, before any option is generated. A plan without a Core Question
is not a plan — it is a search for a nearby question to answer.

---

### 3. First-framing persistence

**The mode.** The first framing encountered dominates. Later evidence
adjusts from that anchor but almost never enough. The initial framing
becomes the frame even after it is contradicted.

**Why fluent models are especially vulnerable.** The earliest tokens in a
context window disproportionately shape everything that follows. The first
framing an agent receives becomes the frame it reasons from, even when
later context contradicts it outright.

**The counter.** The **Disconfirmation** field of the
[Reasoning Surface](./REASONING_SURFACE.md). Before committing to a frame,
name the evidence that would prove it wrong. The act of naming forces
active engagement with alternative frames, not passive drift away from the
initial one.

---

### 4. Story-fit over evidence

**The mode.** Sparse data gets assembled into a coherent causal story. The
story feels explanatory. The gaps in the data get papered over by the
shape of the narrative, not by the evidence inside it.

**Why fluent models are especially vulnerable.** Producing coherent prose
is what fluent models are optimized for. The failure mode is the skill.

**The counter.** The **facts / inferences / preferences** separation in
the distinction map. Each claim is tagged by epistemic status. A narrative
that does not survive being decomposed into those three categories is a
story, not an analysis.

---

### 5. Systematic underestimation of effort and risk

**The mode.** Effort, time, and risk are systematically underestimated.
Benefits are systematically overestimated. Confidence in plans reliably
exceeds their accuracy.

**Why fluent models are especially vulnerable.** Training data
over-represents plans that succeeded, because plans that failed were
abandoned rather than written about. The models inherit the survivorship
bias baked into their corpus.

**The counter.** The **failure-first + buffer** requirement for
high-impact decisions. Instead of asking only "what does success look
like?", also answer: "what would definitely cause failure?" and "what is
the margin if estimates slip by 30–50%?" If the answer to either is
unacceptable, the plan is not ready.

---

### 6. Confidence exceeding accuracy

**The mode.** Expressed confidence consistently exceeds actual accuracy.
The model does not know what it does not know, and sounds equally certain
about both.

**Why fluent models are especially vulnerable.** The same training signal
that rewards fluent output also rewards delivery-level confidence.
Uncertainty is dispreferred even when uncertainty is the correct signal.

**The counter.** Two layered counters:

- The **Assumptions** field of the [Reasoning Surface](./REASONING_SURFACE.md)
  forces conclusions to sit on their scaffolding in plain sight.
- The **weight-by-track-record** rule, when inputs conflict: prefer the
  source with demonstrated accuracy on this class of problem over the
  source that is loudest, fastest, or most assertive. Loud and right are
  different signals.

---

## Using this as a pre-execution checklist

These are feedforward gates — run them before the Execute stage opens,
not after a problem surfaces. The cost of skipping is deferred, not avoided.

1. What did "reasoning only from what is present" miss? Is the Unknowns
   section non-empty and honest?
2. What Core Question does this cycle claim to answer? Is it the actual
   question, or a nearby easier substitute?
3. What is the anchor framing? What disconfirmation condition is named
   against it?
4. Which claims are facts, which are inferences, which are preferences?
   Can each survive being labeled?
5. What would definitely cause this plan to fail? What is the margin if
   estimates slip by 30–50%?
6. Where is expressed confidence higher than the evidence supports? Name it.

Six gates, six failure modes. If any gate is skipped, execution proceeds
with that failure mode unprotected. Name the trade-off explicitly rather
than leaving it implicit.

---

## Attribution

The six-mode taxonomy is Kahneman's (*Thinking, Fast and Slow*, 2011),
re-expressed in kernel language and mapped against specific artifacts rather
than left as general advice. Counter-artifacts draw on Popper
(disconfirmation), Shannon (signal vs noise), and Dalio
(weight-by-track-record). Full citations: [REFERENCES.md](./REFERENCES.md).
