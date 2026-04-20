# Kernel Limits

**Operational summary — when this kernel is the wrong tool:**
1. Cost of thinking exceeds cost of being wrong (collapse the loop).
2. Disconfirmation paralysis (ship the smallest reversible move).
3. Orientation over-fit (profile is stale; re-elicit).
4. Tacit knowledge dominates (mark decision as judgment-driven; do not fabricate legible Knowns).
5. Multi-operator loops (single-operator assumption breaks; name authority per decision class).
6. Unvalidated claims about the kernel itself (no calibration telemetry yet; recommendations rest on coherence).

Declared gaps (known, not yet closed): calibration telemetry · profile staleness · team/pair mode · tacit-call decision mode.

---

Every kernel has a domain of applicability. This file names the conditions
under which episteme is the wrong tool, or is the right tool misapplied.
Naming the limits is itself a Principle I act: the constraint that is not
stated runs without accountability.

A kernel without a declared boundary is a cult. This document is the
boundary.

---

## When the kernel is wrong

Six named conditions under which the kernel should be suspended, relaxed, or
replaced. They are not rare edge cases — they are the normal failure modes
of applying a deliberation protocol to a non-deliberation problem.

### 1. The cost of thinking exceeds the cost of being wrong

The Reasoning Surface is a forcing function for System 2. System 2 is
expensive. For decisions where the downside of the wrong answer is smaller
than the overhead of filling in four fields, the protocol is a tax on
execution speed with no matching return.

- Indicator: the reversible local work is being surrounded with more
  ceremony than the blast radius justifies.
- Correct response: skip the surface. Keep the loop (Frame → Decompose →
  Execute → Verify → Handoff) collapsed to one or two stages. The kernel
  should compress itself when the stakes compress.

### 2. Disconfirmation paralysis

"Name the evidence that would prove this wrong" is a discipline. It becomes
pathological when it becomes permission-seeking — when disconfirmation is
treated as a prerequisite that must be *satisfied* rather than a field that
must be *named*.

- Indicator: the same surface is being re-filled while no action is taken,
  or the surface is being used to delay commitment on a reversible move.
- Correct response: ship the smallest reversible action and let
  observation, not further deliberation, close the loop. Popper's point was
  that theories must be falsifiable, not that they must be falsified before
  being used.

### 3. Orientation over-fit

episteme is orientation infrastructure. Orientation shaped by last
week's context can govern this week's decisions without being re-examined.
The more coherent the operator profile, the more confidently it filters
contradicting evidence out.

- Indicator: the kernel is producing consistent answers on a problem that
  has materially changed. The profile feels sharp; the decisions feel
  narrow.
- Correct response: treat the operator profile as staleness-prone.
  Re-elicit the scorecard periodically (quarterly is a reasonable default)
  and after any significant change in role, project, or collaborators. A
  profile that never updates is not stable; it is ossified.

### 4. Tacit knowledge dominates

Some work is governed by skill that resists being made explicit. Craft
judgment, aesthetic taste, clinical intuition, negotiation read — these are
Polanyi's tacit knowledge, where *we know more than we can tell*. Forcing
the Reasoning Surface over a tacit-dominated decision produces a surface
that either omits the real basis for the choice or fabricates a legible
basis in its place.

- Indicator: the "Knowns" section either misses the actual driver of the
  decision, or reads like post-hoc justification.
- Correct response: name the tacit dimension explicitly ("this is an
  aesthetic call grounded in N years of practice") and mark the decision as
  judgment-driven, not evidence-driven. Record the decision with its tacit
  label; track whether it validated. Over time, tacit patterns that
  correlate with outcome become explicit Knowns. Tacit knowledge is not
  inferior to explicit — it is prior to it.

### 5. Single-operator assumption

The kernel is designed around one operator with one coherent worldview.
Team decisions, pair work, and multi-stakeholder calls do not fit cleanly.
Whose Core Question? Whose Disconfirmation? Whose risk tolerance governs
the scorecard?

- Indicator: two humans in the same loop with materially different
  cognitive profiles and no explicit reconciliation.
- Correct response (current): name the operator whose profile is
  authoritative for this specific loop. Other participants' profiles apply
  to their own work. Cross-profile tension (one operator values speed,
  another values thoroughness) is surfaced as a constraint regime
  negotiation, not resolved by averaging.
- Correct response (future): a multi-operator mode is a known gap. Until
  built, high-disagreement loops should fall back to psychological-safety
  discipline (Edmondson) — an explicit contract that dissent is first-class
  input, not friction to be smoothed over.

### 6. Unvalidated claims about the kernel itself

The kernel claims to counter named failure modes. Those claims are
hypotheses, not measurements. There is no telemetry yet validating that
operators using the kernel make better-calibrated decisions, ship faster,
or avoid the failure modes more often than operators using a well-ordered
notebook.

- Indicator: the kernel is being recommended on the basis of its internal
  coherence rather than outcome data.
- Correct response: treat the kernel as a testable proposal. The stated
  counters (Unknowns → WYSIATI, Disconfirmation → anchoring, etc.) are
  falsifiable. Collect calibration data over time: recorded Assumptions
  with falsification conditions, marked outcomes, running hit rate.
  A kernel that does not track its own calibration cannot distinguish
  discipline from superstition.

---

## Gaps the kernel does not yet close

Four structural gaps that attribution and footnotes do not fix. They are
on the roadmap, not on the current surface.

### A. Calibration telemetry

There is no built-in mechanism to compare predictions to outcomes. The
kernel surfaces Unknowns and Assumptions with falsification conditions but
does not (yet) track which predictions were right, which assumptions held,
which disconfirmation conditions actually fired. Without that loop, the
kernel improves reasoning hygiene without proving it improves accuracy.

Minimum viable follow-up: a lightweight log — `decisions/*.md` or a single
append-only file — that stores (decision, assumptions, disconfirmation,
observed outcome, was-falsified?). Reviewed quarterly. The data says
whether the protocol is earning its overhead.

### B. Profile staleness

The operator profile is static. Cognitive preferences evolve; project
contexts change. The profile written in month one governs month twelve
without any signal that it has drifted from the operator's current
practice.

Minimum viable follow-up: a timestamped `last_elicited` field on each
profile file, and a soft prompt ("this profile was last elicited N months
ago; re-elicit?") surfaced by the adapter when it exceeds a threshold.

### C. Team and pair workflows

See limit 5. The current contract assumes one operator. Real knowledge
work often is not solo. The kernel needs an explicit multi-operator mode
— not averaged profiles, but named authority per decision class,
escalation protocols, and first-class dissent.

### D. Tacit/explicit trade-off unmodeled

See limit 4. The kernel treats explicit reasoning as the desired end
state. Polanyi's point cuts the other way: explicit articulation of
fundamentally tacit skill destroys the skill. The kernel should have a
declared mode for tacit-dominated decisions that records them
differently.

Minimum viable follow-up: an explicit `tacit-call` marker on decision
records, acknowledging the judgment-driven basis and skipping the
fabricated-Knowns failure mode.

---

## Problem domain classification (Cynefin)

Before populating the Reasoning Surface, classify the problem domain using the Cynefin framework. The most common agent failure is treating *Complex* problems as *Complicated* ones—running analysis loops on a domain that requires probing, not analysis.

| Domain | Nature | Agent posture |
|--------|--------|---------------|
| **Clear** | Cause-effect known; best practice exists | Apply directly; minimal surface needed |
| **Complicated** | Cause-effect discoverable with analysis | Full Reasoning Surface; expert analysis applies |
| **Complex** | Cause-effect only visible in retrospect | Probe → sense → respond; limit execution scope; flag in Unknowns |
| **Chaotic** | No discernible cause-effect | Act first to stabilize; surface after, not before |

- **Indicator of misclassification:** the agent fills in a confident Knowns section on a domain where the actual knowability is contested or context-dependent. Confident-sounding Knowns on a Complex problem are a fabrication failure, not a reasoning success.
- **Correct response:** when the domain is Complex or Chaotic, the Reasoning Surface must explicitly name the domain classification in Unknowns and limit the execution plan to the smallest reversible probe. Full analysis plans on Complex problems should be rejected at the Core Question gate.

The Cynefin classification does not replace the Reasoning Surface. It precedes it.

---

## How to use this file

When a decision feels like the kernel is fighting the work instead of
serving it, walk this list. If the situation matches one of the six named
limits, the kernel is misapplied — relax it for this decision, and record
which limit triggered the relaxation.

When a recommendation to "just use episteme here" meets resistance,
check whether the resistance is the kernel encountering one of its own
declared limits. The limit is not a failure of discipline. It is a
boundary of applicability, named in advance so discipline does not become
cargo.

A discipline that cannot name its own boundary is not a discipline. It
is a creed.

---

## Attribution

- **Tacit vs explicit boundary** — Polanyi, *Personal Knowledge* (1958).
- **Multi-operator dissent as first-class input** — Edmondson,
  *psychological safety* (1999).
- **Falsifiable-but-not-yet-falsified** — Popper, *Conjectures and
  Refutations* (1963).
- **Self-aware boundary as the test of a discipline** — Lakatos on
  research programs and degenerative vs progressive problem shifts.

Full citations in [REFERENCES.md](./REFERENCES.md).
