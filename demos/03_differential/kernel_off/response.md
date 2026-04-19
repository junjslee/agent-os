# Response (posture OFF) — fluent, actionable, wrong

**Engineer reply, first draft:**

> Hey Priya — good timing, I've been wanting to look at this. Here's a rough scope for a 2-sprint build:
>
> **Sprint 1 (2 weeks)**
> - Set up `pgvector` on our existing Postgres. Cheaper than Pinecone, no new vendor, good enough at our scale.
> - Build an indexer job that pulls KB articles, chunks them at ~500 tokens, embeds with `text-embedding-3-small` (good cost/perf tradeoff), writes vectors to a new `kb_chunks` table.
> - Backfill embeddings for the existing ~4,200 articles.
>
> **Sprint 2 (2 weeks)**
> - Wire a new `/search` endpoint that does cosine similarity over the vector table, returns top-10.
> - A/B test against the current keyword search: 50/50 traffic split, measure click-through on returned results.
> - Ship it to 10% of customers behind a feature flag, ramp to 100% if CTR is up.
>
> **What I need from you**
> - Confirm the budget for embedding costs (~$40/mo at current article count — negligible).
> - Sign off on the feature flag ramp plan.
> - Agree on CTR as the primary metric.
>
> Should be doable before the trade show. I'll kick off Sprint 1 on Monday.

---

## What's wrong with this response (marked post-hoc)

This response is competent, specific, and confidently wrong in five named ways. None of them are visible to the writer at the moment of writing. All of them are visible to a posture that runs the Reasoning Surface protocol before drafting a reply.

| # | Fluent pattern                                       | Named failure mode        | What it misses                                                                                   |
|---|------------------------------------------------------|---------------------------|--------------------------------------------------------------------------------------------------|
| 1 | Immediately scopes a *how*-plan.                     | Question substitution     | The real question is *should we build this*, which requires evidence the current search is the load-bearing failure. |
| 2 | Accepts "customers can't find stuff" as the problem. | WYSIATI                   | Never asks: *what fraction of failed searches are typos, stop-word stripping, missing content, or discoverability from outside the KB?* |
| 3 | Commits to vectors/embeddings vocabulary.            | Anchoring                 | The word "semantic" in the prompt anchored the response. No alternative retrieval change (query hygiene, synonym index, better keyword stemming) was considered. |
| 4 | 2-sprint estimate with no mention of eval or ops.    | Planning fallacy          | Ignores: relevance evaluation (labeled data, gold set), index rebuild cost, cold-start latency, chunk boundary experiments, ongoing re-embedding as articles change, A/B test sample size. Each is a week or more. |
| 5 | CTR is the only success metric; no falsification.    | Overconfidence            | No pre-stated condition for *"this did not work, roll back"*. If CTR is flat or down, there is no plan for what that implies. |

### What would have happened, had this shipped

- **Week 1:** pgvector + indexer built. Looks good in staging.
- **Week 3:** A/B test launches. CTR is **statistically indistinguishable** from keyword search.
- **Week 4–5:** "Let's tune chunking." "Let's try a larger embedding model." "Let's add a rerank step." Each adds latency and complexity. None move CTR.
- **Week 6:** Roll back. The team now owns an unused pgvector index, an indexer job on its own cron, and ~$200 in sunk OpenAI bills. Zero learning captured in durable docs.
- **Week 7:** Support tickets still show "I searched but couldn't find it." Because the failure was never diagnosed.

### Why the fluent response is the *default*

LLMs and competent-but-rushed engineers share a bias: when asked *"can you scope X?"*, both produce a scope. The asker's framing becomes the problem statement. The posture exists to refuse that default when the framing is upstream-uncertain.
