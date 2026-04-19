# The prompt (verbatim, as received 2026-04-19 09:14 UTC)

> **From:** Priya (PM)
> **To:** Jun (Eng)
> **Subject:** Semantic search on the KB — can we scope?
>
> Hey Jun — support is pinging me again about the knowledge base. Customers can't find stuff. Tickets with "I searched but couldn't find it" are up. I think semantic search is the answer — we should embed the KB articles and use vector similarity instead of the current keyword search. OpenAI embeddings are cheap now and Pinecone / pgvector both look straightforward.
>
> Can you scope a 2-sprint build for Q3? I'd love to ship before the trade show. What do you need from me?

## Surface metadata (for the posture-on side)

- `source_ref`: Slack DM, 2026-04-19 09:14 UTC
- `asker_role`: PM (not a KB SME, not a support lead)
- `implicit_constraints`: ship before trade show (≈6 weeks), 2 sprints
- `implicit_claims`:
  1. customers can't find stuff → load-bearing
  2. semantic search is the answer → load-bearing
  3. keyword search is the current bottleneck → load-bearing
  4. 2 sprints is enough → load-bearing
- `evidence attached`: none (one anecdote from support)
- `kernel status when received`: off (first-pass), then re-posed with posture on
