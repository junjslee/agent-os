# Demo 03 — Differential: same prompt, posture off vs. on

The same engineering decision, presented twice. Once with a fluent agent that answers the question as asked. Once with the episteme posture engaged. Both are good-faith attempts to help. One ships software that gets rolled back six weeks later. One does not.

## Premise

- Operator: a product engineer asked by a PM to scope a feature.
- Prompt (in full, as posed): [`prompt.md`](./prompt.md).
- Decision class: forward-looking greenfield (not a diagnosis). Verification is therefore partial — the posture still produces a falsifiable plan, but the evidence step lives in the future.

This demo is the one that convinces skeptics. The kernel's value is not a fix after the fact — it is a different answer at the first turn.

## How to read

1. **Read the prompt first.** [`prompt.md`](./prompt.md). It is intentionally open-ended and slightly flattering, as real product asks tend to be.
2. **Read the posture-off response.** [`kernel_off/response.md`](./kernel_off/response.md). Notice the answer is fluent, well-structured, actionable. It is also wrong in a specific, named way.
3. **Read the posture-on artifacts.**
   - [`kernel_on/reasoning-surface.json`](./kernel_on/reasoning-surface.json) — the Core Question and Knowns/Unknowns/Assumptions/Disconfirmation.
   - [`kernel_on/decision-trace.md`](./kernel_on/decision-trace.md) — options considered, because-chain, pre-rejected paths.
   - [`kernel_on/verification.md`](./kernel_on/verification.md) — what the posture pre-commits to measuring, and what would falsify the plan.
   - [`kernel_on/handoff.md`](./kernel_on/handoff.md) — what to tell the PM, what to refuse, what to queue.
4. **Read the diff.** [`DIFF.md`](./DIFF.md) — side-by-side analysis of what the posture changed and which named failure modes it caught.

## The kernel is not trying to sound smarter. It is trying to answer a different question.

Posture-off answers the *asked* question: *"how do we build semantic search?"*
Posture-on surfaces the *answerable* question: *"do we have evidence that keyword search is the load-bearing failure, or are we about to build a solution to the wrong problem?"*

If the load-bearing failure is *unclear queries*, semantic search will not help and may hurt (hallucinated relevance). If the failure is *outdated content*, no retrieval change matters. If the failure is *discoverability from outside the KB*, the solution is SEO, not embeddings. The posture exists to refuse to ship before that fork is resolved.

## What named failure modes this demo catches

| Mode                  | How it appears in the posture-off response                                     | Counter                      |
|-----------------------|---------------------------------------------------------------------------------|------------------------------|
| Question substitution | Answers "how do we build X" when the real question is "should we build X"      | Core Question field          |
| WYSIATI               | Treats the PM's framing as the complete picture; never asks what's missing      | Unknowns field               |
| Anchoring             | The word "semantic" anchors the conversation to embeddings/vectors              | Disconfirmation condition    |
| Planning fallacy      | Proposes a 2-sprint plan with no mention of index ops, eval, or rollback cost   | Options table + second-order effects |
| Overconfidence        | Commits to a build plan with no pre-stated condition for abandoning it          | Disconfirmation condition    |

## Outcome (as scored post-hoc)

- Posture-off path, had it shipped: 2 engineer-sprints → cold-start evaluation finds relevance no better than BM25 → roll back → 6 weeks sunk, zero learning captured in durable docs.
- Posture-on path: 2 days → instrumentation shows 68% of failed searches are typos and stop-word stripping misses, not semantic gaps → ships a query-hygiene fix in 3 days → re-evaluates embeddings question against fresh data.

The *fix* in the posture-on path is not always embeddings-avoidance. It is that the decision is now *answerable*.
