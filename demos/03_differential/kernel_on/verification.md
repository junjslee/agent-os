# Verification — KB semantic search (posture ON)

This is a forward-looking decision. Unlike demos 01 and 02, the evidence step lives in the *future*. The posture's job here is to pre-commit to what will be measured and what will falsify — so that when the data arrives, nobody gets to move the goalposts.

## Against the Core Question

**Core Question.** Do we have evidence that keyword search is the load-bearing failure in KB discoverability, before we commit 2 sprints to a semantic-search build?

**Answer as of 2026-04-19.** No — not yet. The evidence to answer it will be produced by the 1-day instrumentation spike (Option C). Until then, any scope commitment is a bet on an undiagnosed hypothesis.

**What would count as evidence (pre-declared, not post-hoc rationalized).**
- A 1-week query log with: raw query, stemmed query, returned article IDs, click-through (yes/no), time-to-click.
- A hand-labeled gold set of 50–100 failed queries, each classified into: `typo`, `stop_word_loss`, `content_missing`, `pipeline_index_bug`, `discoverability_external`, `genuine_semantic_gap`, `other`.
- A numeric fraction per class. Threshold for "semantic search is justified": genuine_semantic_gap ≥ 50%.

## Against each assumption (pre-committed evaluation plan)

| Assumption                                                                         | How it will be tested                                                                 | Status      |
|------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|-------------|
| PM's framing is a hypothesis, not a specification.                                 | Direct ask in the reply: "do you have direct evidence for semantic gap specifically?" | Pending PM reply |
| 1–2 weeks of query logs is enough to classify failure modes at 90%+ confidence.    | Power calculation: at 1,200 queries/day × 5% failure rate = 60 failures/day. 1 week → ~420 failures. 100-sample label gives ±10% confidence band on any class ≥15% — enough. | Validated at planning time |
| <30% semantic-gap failures → semantic search will not measurably improve CTR.      | Post-logging: compute the fraction, check against the 30% bar.                        | Pending data |
| Base rate for KB-redesign rollbacks is ~40%.                                        | Cited to industry reports 2021–2024. Weak but directional; used only to argue "diagnose before build", not to block any specific build. | Load-bearing at planning only |

## Against each disconfirmation condition

| Condition                                                                                          | What the posture does in that case                                |
|----------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| Query log shows >50% true semantic-gap failures.                                                    | Pivot to fluent-response plan. Scope the 2-sprint build. Ship.    |
| PM produces direct user-interview evidence of semantic-gap failures.                                | Rewrite the reasoning surface with that evidence as a Known. Re-run.|
| 1-day tsvector/synonym fix closes >40% of failure modes.                                            | Ship the fix. Remove semantic search from the roadmap for this cycle. |
| Trade-show deadline is load-bearing AND diagnosis is infeasible in-window.                          | Escalate to senior sign-off. Not a unilateral engineering call.   |

## Against the fluent-off plan (what we pre-reject)

Had we shipped the Option-A plan verbatim:

- Week 3: A/B test shows CTR flat or regressed.
- Week 4–5: temptation to keep tuning (larger model, different chunk size, rerank step).
  - Without a pre-stated disconfirmation condition, the team's escape route from sunk cost is ad-hoc. Most teams keep tuning.
- Week 6: roll back, or continue tuning into Q4. Either way, the original Core Question is still unanswered.

**The posture is not claiming semantic search is wrong.** It is claiming that *deciding without diagnosis is wrong*. The data may yet say "build it" — and if it does, the plan ships with a falsifiable success bar already in place.

## Residual unknowns (honest)

- Whether the PM's "customers can't find stuff" stream contains signal we haven't audited in Slack/Zendesk. A 1-hour review of the last 30 tickets, by keyword, would sharpen the Unknowns list.
- Whether the KB's *content quality* is the upstream bottleneck (articles that exist but are stale, vague, or wrong). No amount of retrieval improvement fixes that. Flagged for the next-cycle check if retrieval doesn't move the metric.

## Confidence

- **Diagnosis plan (Option C) will produce actionable data:** high.
- **Diagnosis will favor one specific fix class:** not predicted — deliberately. The posture's job is to not pre-commit to an answer.
- **2-sprint semantic-search build is the right move regardless of data:** low. This is the claim the fluent response implicitly makes; this posture refuses it until Friday.

## The kernel's test, post-hoc

The kernel will be judged on two things when the data lands next Friday:
1. Did the pre-stated disconfirmation conditions actually fire as specified, or did the team quietly move them?
2. Was the chosen action (fluent build / query hygiene fix / content audit / escalation) the one that matches the data, or the one that matched the initial framing?

If (1) is *moved*, the kernel was decoration. If (2) is *initial framing*, the kernel was decoration. The artifacts in this directory are timestamped and in git so the answer is auditable.
