# Active-Guidance Ranking — Anti-Doxa Discipline at the Protocol-Routing Layer

**Operational summary** (load first if you have a token budget):

- The kernel exists to counter Doxa (statistical-mean reasoning). If active-guidance routes synthesized protocols by popularity-frequency-recency, the kernel reinstalls Doxa at the routing layer.
- This file is the audit + the documentation of the ranking strategy actually implemented in `core/hooks/_guidance.py:query`. It is the load-bearing claim that the routing layer is anti-Doxa-aligned.
- **Ranking strategy:** primary key = `field_overlap` (context-signature specificity); secondary key = `ts` (recency tiebreaker). NO popularity / frequency-of-fire / use-count input.
- v1.1 first slice (Event 86 / CP-ACTIVE-GUIDANCE-RANKING-AUDIT-01): doc + audit + ranked-with-disclosure helper (`query_top_k`) + anti-Doxa test cases. Future enhancements (full ranked-with-disclosure UX, additional ranking strategies as opt-in modes) deferred.

---

## What this is

Pillar 3 active guidance fires at decision points. Multiple synthesized protocols may match the same candidate `context_signature`. The kernel MUST rank them when surfacing to the operator.

Each candidate ranking algorithm carries built-in bias:

| Ranking strategy | Hidden bias |
|---|---|
| By recency | recency-bias |
| By frequency-of-fire | popularity = **Doxa** |
| By use-count | success-bias (popular ≠ correct) |
| By chain-position | freshness-bias |
| By weighted-blend | hidden-Doxa-via-coefficients |
| **By context-signature specificity** | **none — context-fit is exactly the kernel's thesis** |

The kernel's central anti-Doxa thesis applied at the protocol-routing layer: **rank by context-signature specificity, not by popularity or use-count.** The protocol whose `context_signature` matches MORE precisely wins, regardless of how many times it has fired previously.

If the kernel's protocol-routing used statistical-mean ranking, the kernel would be the very statistical-mean engine it set out to destroy — applied to its own knowledge layer.

---

## Audit (current state)

**Code path:** `core/hooks/_guidance.py:query`.

**Ranking function:**

```python
ranked.sort(key=lambda t: (t[0], t[1]), reverse=True)
top_overlap, top_ts, top_payload = ranked[0]
```

Where each tuple is `(overlap, ts, payload)`:
- `overlap` (int 0..6) — `field_overlap(candidate, stored)` from `_context_signature.py`. Counts how many of the 6 canonical context-signature fields (`project_name`, `project_tier`, `blueprint`, `op_class`, `constraint_head`, `runtime_marker`) match between the query candidate and the stored protocol.
- `ts` (str ISO-8601) — chain envelope timestamp.

**Filter inputs (applied BEFORE ranking):**
- Vapor verdict filter (CP8 spot-check) — skips protocols whose latest spot-check verdict marks them `vapor`.
- Project scope — `_load_protocols_cached` filters by `context_signature.project_name`.
- Threshold — `min_overlap` (per-project configurable; default 4 of 6).
- Supersede filter (Event 84 / Item 4) — `list_protocols` (default) filters out superseded entries.

**Anti-Doxa-aligned conclusions:**

1. **Primary key is specificity, not popularity.** A protocol that has fired 1,000 times with overlap=4 LOSES to a protocol that has fired once with overlap=5. The kernel routes by context-fit.
2. **Secondary key is recency, not use-count.** The tiebreaker on equal-overlap is timestamp descending, NOT firing frequency. Ties go to "more-recent context-fit context"; the alternative (use-count) would be popularity-via-track-record.
3. **No frequency / popularity input anywhere.** `_load_protocols_cached` returns the verified chain-walk result; ranking sees only the per-protocol `overlap` + `ts`. The chain itself contains use-count via repeated synthesis events of the same protocol, but the ranker does NOT count those.

**Status: anti-Doxa-aligned at the ranking layer.** The audit confirms the implementation matches the spec's "context-fit, not statistical-fit" principle.

---

## Ranked-with-disclosure helper

`core/hooks/_guidance.py:query_top_k` (Event 86) returns the top-K matching protocols WITH ranking-rationale + provenance trail, instead of just the top-1. Operators surfacing the routing decision can see the runner-up + understand why one won.

The `query` function (single-result API) remains unchanged — used by hot-path active-guidance. `query_top_k` is operator-facing for spot-check / forensic / "why did the kernel surface THIS protocol?" workflows.

---

## Falsifiability — what would falsify the anti-Doxa claim

Per `kernel/FALSIFIABILITY_CONDITIONS.md` discipline, the anti-Doxa property of the ranking layer must be falsifiable:

**Claim.** Active-guidance routes by context-signature specificity, not by popularity or use-count.

**Falsification condition.** A test scenario where:
- Protocol A has `context_signature` matching the query candidate by 5 of 6 fields, has fired ONCE.
- Protocol B has `context_signature` matching the query candidate by 4 of 6 fields, has fired 100 TIMES (e.g., emitted on every cascade for a noisy op-class).
- `query()` returns Protocol B (the popular-but-less-context-fit one) instead of Protocol A.

If this scenario fires, the ranker has acquired a popularity coefficient it was not supposed to have.

**Test case** at `tests/test_guidance_ranking_audit.py:test_anti_doxa_specificity_wins`. Concrete adversarial fixture verifies the ranker prefers the higher-overlap protocol regardless of how many times the lower-overlap one was emitted.

---

## Action on disconfirmation

If the falsification fires:

1. **Investigate before demoting** (per `kernel/FALSIFIABILITY_CONDITIONS.md` action-on-disconfirmation policy). Drift may be real OR a test-fixture bug.
2. **If drift is real:** the ranker has acquired hidden-Doxa coefficients. Audit the sort key; remove popularity input; re-test.
3. **If drift is a tied-overlap edge case:** the secondary key (`ts`) is NOT popularity but recency-bias. Document that recency-tiebreaking IS a recency-bias choice (rebuttable: there isn't a non-arbitrary tiebreaker in the spec; recency is the explicit choice over use-count).

---

## Counter-pattern — context-signature specificity is the right primary key

The kernel's broader principle: *context-fit, not statistical-fit*. The active-guidance ranking IS context-fit applied at the routing layer. Three reasons:

1. **The whole synthesis discipline rewards context-specific protocols.** Pillar 3 emits a protocol scoped to the context-signature it was synthesized from. Routing by specificity preserves that scoping all the way through to the surfacing decision.
2. **The kernel's failure-mode taxonomy explicitly counters statistical-mean reasoning.** `kernel/FAILURE_MODES.md` mode 10 (Framework-as-Doxa) names this exact failure shape at the framework layer. Ranking-by-popularity would be the same failure at the routing layer.
3. **The federation extension preserves it.** CP-FEDERATED-COGNITIVE-NETWORK-01 (`~/episteme-private/docs/cp-v1.2-federation.md`) extends the anti-Doxa discipline from local-active-guidance to federated class-pattern aggregation. Both layers share the same principle: aggregate at the class level, not the protocol level; route by context-fit, not statistical-fit.

---

## Cross-references

- [`kernel/CONSTITUTION.md`](./CONSTITUTION.md) — the four principles whose anti-Doxa thesis this file operationalizes at the routing layer.
- [`kernel/FAILURE_MODES.md`](./FAILURE_MODES.md) § 10 (Framework-as-Doxa) — the failure mode this ranker counters at its layer.
- [`kernel/FALSIFIABILITY_CONDITIONS.md`](./FALSIFIABILITY_CONDITIONS.md) — falsifiability discipline this audit honors.
- `core/hooks/_guidance.py:query` — the audited ranking implementation.
- `core/hooks/_guidance.py:query_top_k` — ranked-with-disclosure helper (Event 86).
- `core/hooks/_context_signature.py:field_overlap` — overlap-counting primitive.
- `~/episteme-private/docs/cp-v1.1-architectural.md` § CP-ACTIVE-GUIDANCE-RANKING-AUDIT-01 — spec source.
- `~/episteme-private/docs/cp-v1.2-federation.md` § CP-FEDERATED-COGNITIVE-NETWORK-01 — anti-Doxa preservation at federation scope.

---

## Maintenance

This file is correct when:

- The `query` function in `core/hooks/_guidance.py` matches the ranking strategy described above.
- The `query_top_k` helper exists and exposes ranking rationale.
- `tests/test_guidance_ranking_audit.py` includes the anti-Doxa specificity-wins test.
- Cross-references resolve.

Version: v1.0 (Event 86, 2026-04-29). First slice: audit + doc + ranked-with-disclosure helper + anti-Doxa tests. Future enhancements (full UX for top-K disclosure, opt-in alternate ranking modes for spot-check experiments) deferred.
