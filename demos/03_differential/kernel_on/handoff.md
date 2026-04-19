# Handoff — KB semantic search (posture ON)

## What shipped (at the 2026-04-19 decision point)

- **Written reply to PM** (see `decision-trace.md` → "What the PM will be told"). Reframes the ask from "scope a build" to "scope a diagnosis, then scope the right build." Offers the trade-show deadline as still-achievable.
- **1-day instrumentation spike scoped.** Capture raw query, stemmed query, returned article IDs, click-through, time-to-click. Feature-flagged behind `kb.search.telemetry=true`. Data lands in `analytics.kb_search_events`.
- **Gold-set labeling plan scoped.** 50–100 failed queries, hand-classified into six failure-mode buckets. Kept in `eval/kb_search_gold_v1.jsonl` for reuse across any future retrieval change.

## What was decided not to ship (and why — so the next session doesn't re-litigate)

- **The 2-sprint embedding build.** Not rejected; deferred until the data is in. Rejection would have been premature; acceptance would have been undiagnosed. The correct state is *conditional*.
- **The "refuse entirely" option.** A zero-cost refusal is a political refusal, not an engineering one. The diagnosis path preserves PM trust and produces data.
- **Parallel build-while-diagnosing.** Violates the posture's cost ceiling and creates a sunk-cost trap: once the build is in flight, disconfirming data becomes politically expensive to honor.

## What's open

1. **PM evidence check.** Does the PM have direct user-interview data pointing to semantic gaps? Pending reply. If yes, this reasoning surface is stale and should be rewritten.
2. **Friday 2026-04-26 checkpoint.** With a week of logs and a labeled gold set, revisit the disconfirmation table in `verification.md`. The pivot condition that fires determines the next action.
3. **Content-quality upstream hypothesis.** Queued for the next-cycle check if retrieval changes don't move the metric. No one should chase this before Friday's data lands.
4. **Query-log schema hardening.** The instrumentation schema we write Monday becomes a durable artifact for any future retrieval decision. Worth one hour of design on Monday morning, not five minutes in a Slack message.

## What the next session needs to know

- The PM's framing ("semantic search is the answer") is treated as a hypothesis. **Do not restart the conversation by accepting it as a specification.** If you open a session next week and the first thing someone says is "OK we're doing embeddings, what's left?" — re-read this reasoning surface first.
- The trade-show deadline is acknowledged and preserved. A diagnosis-first path still ships *something* before the trade show. If the something is a keyword-hygiene fix, that is not a downgrade — it is the correct answer to what the diagnosis revealed.
- If the Friday data says "semantic gap is >50% of failures," the fluent-response plan in `../kernel_off/response.md` is largely correct and should be executed *verbatim* — with the addition of a pre-stated rollback condition on CTR at the 2-week A/B checkpoint. The posture is not anti-embeddings; it is anti-undiagnosed.

## Reasoning-surface artifacts

- Final surface (forward-looking — disconfirmation conditions pending data): [`reasoning-surface.json`](./reasoning-surface.json)
- Decision trace with load-bearing-concept citations: [`decision-trace.md`](./decision-trace.md)
- Verification plan: [`verification.md`](./verification.md)

## Kernel counters that earned their keep in this cycle

| Mode caught           | Where                                                                                      |
|-----------------------|--------------------------------------------------------------------------------------------|
| Question substitution | Refused to let "how do we build X" substitute for "should we build X"                      |
| WYSIATI               | Forced the failure-mode taxonomy (typo / stop-word / content-missing / discoverability / semantic-gap / pipeline-bug) into Unknowns instead of collapsing to "can't find stuff" |
| Anchoring             | Named that the word "semantic" in the prompt had anchored the entire space; forced synonym-table + content-audit options into the comparison |
| Planning fallacy      | Made the second-order costs of Option A (eval, index ops, rollback) visible in the table; "2 sprints" stopped meaning what it seemed to mean |
| Overconfidence        | Each surviving hypothesis has a pre-stated disconfirmation condition before any action    |

## Capture of durable lessons (promote candidates)

- **Project-scoped:** the failure-mode taxonomy for KB search (six classes) is a durable artifact. Lives in `docs/KB_SEARCH_FAILURE_MODES.md` — future retrieval decisions reuse the taxonomy.
- **Global candidate:** the pattern "when asked to scope X, first check whether X is the load-bearing answer to Y" is the same pattern demos 01 and 02 exercised in different domains. Already captured in `kernel/REASONING_SURFACE.md` as the Core Question discipline. No new entry needed.
- **Not promoted:** the specific choice (pgvector vs. Pinecone, 500-token chunks, `text-embedding-3-small`). These are situation-specific and will be wrong for the next decision.
