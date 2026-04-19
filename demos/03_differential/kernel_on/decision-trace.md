# Decision Trace — KB semantic search (posture ON)

## Options considered

| # | Option                                                                | First-order effect                             | Second-order effect                                                                                   | Reversibility |
|---|-----------------------------------------------------------------------|------------------------------------------------|-------------------------------------------------------------------------------------------------------|---------------|
| A | Ship the 2-sprint embedding build as PM requested.                    | Lower latency to shipping the feature.         | If diagnosis is wrong, 4 weeks sunk + rollback. Team owns a vector index with no proven value. Base-rate says ~40% of these projects roll back. | Partially reversible (code removal cheap; reputation & trust less so) |
| B | Refuse entirely; tell PM to come back with user research.             | Zero engineering cost this sprint.             | PM → support → eng reputation ("engineering is blocking us"). Does not produce data. No progress. | Fully reversible |
| C | 1-day instrumentation spike: capture 1 week of query logs + click-through; label 50-query gold set; classify failure modes. | Produces the data that makes the decision answerable. | Costs 1 engineer-day + 1 week of calendar waiting on data. Keeps trade-show window alive. Produces durable artifact (query log infra) regardless of which build we pick. | Fully reversible |
| D | Apply cheap keyword-search fixes in parallel with C (synonym table, improve tsvector config, stemming). | If ~40% of failures are keyword-hygiene issues, this closes them in 2–3 days. | If it does nothing, we learned keyword hygiene is not the load-bearing gap, which *strengthens* the evidence for C. Either outcome is informative. | Fully reversible |
| E | Commit A + C in parallel (build while diagnosing).                    | Max optionality; ship either direction.        | Doubles cost; burns political capital if we later roll back the build that was "in flight." Violates the kernel's cost_ceiling_days_before_next_checkpoint. | Partially reversible |

## Because-chain

- **Observed signal:** PM requested a 2-sprint scope for semantic search, citing support tickets.
- **Inferred cause candidates:**
  (1) genuine semantic gap — embeddings would help;
  (2) keyword hygiene gap — a config fix would help;
  (3) content gap — no retrieval change helps;
  (4) discoverability gap (users don't reach the KB) — marketing/SEO problem, not retrieval.
- **Decision:** run **C + D in parallel** as the next 1–2 days of engineering time. Reject A at the Core Question gate — no diagnosis, no build. Reject B because it produces no data. Reject E because it burns cost before the checkpoint.

## What the kernel forced into view

1. **Core Question** blocked Option A from being reflexively scoped. "How do we build semantic search" was substituted for "is semantic search the answer".
2. **Unknowns** turned "customers can't find stuff" into a classifiable taxonomy (typo / stop-word / content-missing / discoverability-external / genuine-semantic-gap) — each with a different fix. The fluent response treated them as one problem.
3. **Assumptions** named the load-bearing assumption that *the PM's framing is a hypothesis, not a specification*, and declared the condition under which that assumption collapses (PM produces direct evidence we haven't seen).
4. **Disconfirmation** pre-committed to the pivot condition: if >50% of failed searches are true semantic gaps, the fluent response becomes correct and we build. If <30%, we don't.

## Load-bearing concepts in this decision

| Concept               | Source                                                    | Role here                                                                   |
|-----------------------|------------------------------------------------------------|------------------------------------------------------------------------------|
| Question substitution | Kahneman — *Thinking, Fast and Slow* Ch. 9                 | Blocked "how do we build X" from substituting for "should we build X"       |
| Base-rate neglect     | Kahneman — *Thinking, Fast and Slow* Ch. 14                | Named the ~40% rollback rate for analogous KB-redesign projects              |
| Second-order effects  | Munger — *Poor Charlie's Almanack*                         | Forced the eval / index ops / rollback cost into the decision, not just the build cost |
| Inversion             | Munger — *Poor Charlie's Almanack*                         | "What would tell us semantic search is NOT the answer?" → seeded disconfirmation conditions |
| Falsification         | Popper — *Conjectures and Refutations*                     | Pre-stated disconfirmation condition for every surviving hypothesis         |
| OODA loop             | Boyd — *Patterns of Conflict*                              | Orient (collect query logs) before Decide (scope a build)                   |

All six are cited in [`kernel/REFERENCES.md`](../../../kernel/REFERENCES.md).

## Chosen path

**C + D over the next 5 business days**, with a checkpoint on 2026-04-26 to re-evaluate against the disconfirmation table. Rejected A at the gate with an explicit, written reason the PM can challenge. Queued the semantic-search build as a conditional downstream task, not a committed one.

## What the PM will be told (draft reply)

> Priya — thanks for flagging this. Before I scope the build, I want to spend 1 day setting up query logging + labeling a small gold set, because I don't currently know whether the failure is semantic or something cheaper. I'll have a read on it by next Friday. If the data says semantic search is the gap, the 2-sprint plan you sketched is basically right and we can absolutely ship before the trade show. If the data says it's something else — a synonym table, a pipeline bug, a discoverability problem — we'll save four weeks and ship the thing that actually moves the metric. Either way, you get a shipped answer before the trade show; the question is which answer.
>
> One ask back: do you have any direct evidence (user interviews, session recordings, specific tickets) that points to *semantic* gaps specifically vs. the general "can't find it" complaint? If yes, I'd weight that heavily.
