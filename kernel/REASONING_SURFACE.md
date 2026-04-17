# The Reasoning Surface

The Reasoning Surface is the operational form of Principle I
(*Explicit > Implicit*). It is the minimum viable explicitness required
before any consequential decision.

If the four fields cannot be filled in, the decision is not ready to be
made. That is not ceremony. It is the kernel refusing to let a
fluent-sounding answer pass for an examined one.

---

## The four fields

### 1. Knowns

What is observably true, right now, with current evidence.

- Must be verifiable. "The function returns `None` on empty input" is a
  known only if the function was read or tested.
- Do not include assumptions phrased as facts. This is the most common
  failure of the field.
- Separate from inferences. If the claim required a reasoning step to
  reach, it belongs in a different field.

### 2. Unknowns

What would change the decision if it were known, and is not known.

- A blank Unknowns section is a red flag. Every consequential decision has
  unknowns; an empty list means nothing has been looked at.
- Prefer sharp unknowns ("does the caller hold a lock here?") over vague
  ones ("edge cases around concurrency").
- Rank by impact on the decision, not by how interesting the question is.

### 3. Assumptions

What is being treated as true in order to proceed, while acknowledged as
unverified.

- Name the assumption itself, not the conclusion that depends on it.
- Include a falsification condition where possible: "assuming input is
  never larger than 10k rows — false if a 50k row job shows up."
- An assumption is a debt. Pay it down (verify, or move to Knowns) as
  cheaply as possible.

### 4. Disconfirmation

What evidence, if observed, would prove the current plan wrong.

- Must be a specific, observable outcome. "If the tests pass" is not
  disconfirmation unless the tests actually exercise the thing that could
  be wrong.
- The purpose is to prevent story-fit over evidence: a plan that cannot be
  falsified is a story, not a plan.
- If no disconfirmation can be named, the decision has not been understood
  yet. Stay there until it sharpens.

---

## When to fill it in

- **Always** before an irreversible action.
- **Always** before an action with blast radius beyond the local change:
  shared systems, data loss risk, external side effects.
- **Usually** before a non-trivial design choice the decision will be hard
  to revisit.
- **Optionally** for small reversible local work — but the habit of
  surfacing unknowns even for small tasks catches many errors cheaply.

---

## Role in the loop

The Reasoning Surface is the input to the Decide step of the feedback
loop. It is also the artifact updated by the Verify step: once the action
is taken, observations move assumptions into Knowns, sharpen Unknowns, or
trigger Disconfirmation.

A decision made without a Reasoning Surface is a closed loop with no
entry point for new information. A decision made with one is an open loop
that can be corrected.

---

## Failure modes to watch for

- **Knowns filled with assumptions.** The single most common failure.
  Unverified claims are not knowns.
- **Empty Unknowns.** Treat as a claim of omniscience. Be suspicious.
- **Assumptions without falsification conditions.** Dead weight — nothing
  is named that would pay down the debt.
- **Disconfirmation that cannot happen.** "If the approach is wrong" is
  not disconfirmation. Name the observable outcome.
- **The surface as ceremony.** If filling it out did not change what was
  about to happen, the surface was not engaged with.
