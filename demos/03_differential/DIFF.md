# DIFF — what the posture changed

Side-by-side of the two paths on the same prompt. Read this after reading `kernel_off/response.md` and the four files in `kernel_on/`.

---

## Output shape

|                          | Posture OFF                                          | Posture ON                                                                     |
|--------------------------|------------------------------------------------------|--------------------------------------------------------------------------------|
| **Artifacts produced**   | 1 Slack reply.                                       | 4 versioned artifacts (reasoning-surface, decision-trace, verification, handoff) + 1 PM reply. |
| **Time to reply**        | ~10 minutes.                                         | ~40 minutes.                                                                   |
| **Auditability**         | Zero. The answer is a diff-less message in a thread. | Full. Every claim, option, assumption, and disconfirmation condition is in git. |
| **Political ergonomics** | High (sounds like "yes, here's the plan").           | High *with a different frame* (sounds like "here's how we ship before the trade show the thing that actually works"). |

## The question being answered

| Posture OFF answers                                    | Posture ON answers                                                     |
|--------------------------------------------------------|------------------------------------------------------------------------|
| *How* do we build semantic search on the KB?           | *Should* we build semantic search on the KB, and if so, *scoped against what evidence*? |

This is the single most important diff. Every other difference downstream is caused by this one.

## The failure-mode catch

| Failure mode              | Posture OFF exhibits it…                                                      | Posture ON counter                                                  |
|---------------------------|--------------------------------------------------------------------------------|---------------------------------------------------------------------|
| Question substitution     | Scopes a *how*-plan without challenging the *whether*.                        | Core Question field. "Do we have evidence…" comes before any scope. |
| WYSIATI                   | Accepts "customers can't find stuff" as the complete problem.                 | Unknowns table. Six failure-mode classes, each with its own fix.    |
| Anchoring                 | "Semantic" in the prompt → vectors/embeddings in the response.                | Options C and D in decision-trace. Synonym index and content audit on the board. |
| Planning fallacy          | 2-sprint estimate ignores eval, ops, rollback, sample-size, chunk experiments.| Decision-trace second-order-effect column. Verification plan names sample size upfront. |
| Overconfidence            | No rollback condition. No pre-stated "this didn't work, go back."             | Disconfirmation conditions, pre-stated and pre-committed before data arrives. |

## The expected business outcome

*All numbers illustrative; the point is the shape, not the specifics.*

| Scenario                                                               | Posture OFF                                               | Posture ON                                                      |
|-------------------------------------------------------------------------|-----------------------------------------------------------|-----------------------------------------------------------------|
| **Hypothesis is correct** (semantic gap is load-bearing)              | Ships on time. Wins.                                      | Spends 1 week diagnosing, then ships on time with a falsifiable success metric already in place. Wins slightly later, more durably. |
| **Hypothesis is wrong** (keyword hygiene or content is load-bearing)   | Ships, rolls back 4–6 weeks later, nothing durable captured. | Ships the *right* fix in days 3–5. Trade show met with an actually-working KB. Durable artifact (gold set, taxonomy) kept. |
| **Hypothesis is partially right** (20% semantic gap + 40% keyword hygiene + 40% content) | Ships embeddings, claims partial win, masks the actual load-bearing gap indefinitely. | Ships the 40% keyword fix first, re-evaluates embeddings with clean data, picks up the semantic gap in cycle 2. |

In **none** of the three scenarios does the fluent-off path outperform the posture-on path. In two of three, the posture-on path is substantially better. This is the expected distribution when the kernel catches a real failure mode — not when it happens to agree with the fluent answer.

## What the posture did *not* do

- It did **not** refuse to help.
- It did **not** make the engineer "look slower" — the diagnosis *is* the deliverable, produced in parallel with keyword-hygiene fixes that ship within the trade-show window regardless of the embedding decision.
- It did **not** pretend to know the right answer. The whole point is that the right answer was not knowable at 09:14 UTC on 2026-04-19 — and that pretending otherwise is how products get rolled back.

## What the posture *cost*

- 30 minutes of thinking before drafting a reply.
- One extra Slack exchange ("do you have direct evidence for semantic specifically?").
- The appearance of skepticism where confidence would have been politically easier.

The kernel is willing to pay this cost. The trade is 30 minutes of audit against 4–6 weeks of build-and-rollback. This trade is asymmetric in the direction the kernel is designed for.

## Reading this diff for your own work

If you recognize the pattern — *"we were asked to scope X, so we scoped X, and then X didn't work"* — the posture is designed for you. The point of adoption is not to produce four artifacts per decision; it is to produce the *four kinds of thinking* the artifacts represent. The files are the forcing function. Over time, the thinking becomes the default and the files become a byproduct.

The posture is installed. The question is whether the operator stays in-stance when it's politically expensive to.
