# Design — v1.0 · Semantic Governance for the Reasoning Surface Guard

Status: **draft** · Drafted 2026-04-21 · Scope: the v1.0 RC upgrade of the Reasoning Surface Guard from syntactic enforcement to semantic + contextual validation, designed around the Goodhart threat surfaced during Phase 12.

**Approval status.** This is a draft. The maintainer reviews, then implementation begins against whatever this spec becomes after review. Per the Phase 12 spec discipline: any later change to the design that relaxes a load-bearing countermeasure is a governance change, not an implementation tweak.

## Why this exists

v0.11.0 closed the *retrospective* loop — Phase 12 audits the operator's claimed cognitive profile against the lived episodic record and surfaces drift over time. But the **hot-path validator** (`core/hooks/reasoning_surface_guard.py`) still does what it did at v0.8.1: lazy-token blocklist + 15-character minimum + regex pattern matching. A sufficiently-aware agent defeats this with fluent-vacuous content that:

- Contains no banned tokens (passes the blocklist).
- Exceeds the length threshold (passes the minimum).
- Looks like a falsifiable hypothesis (passes the eye test).
- Commits to nothing testable (defeats the contract).

Five real examples of fluent-vacuous content that pass v0.11.0's gate:

1. *"if any unforeseen issue arises during deployment we will reassess our approach"*
2. *"the migration may produce unexpected behavior if edge cases are encountered"*
3. *"if the build process exhibits anomalous behavior we should investigate before proceeding"*
4. *"should monitoring detect concerning patterns we will pause and evaluate next steps"*
5. *"if results diverge from expectations we will return to first principles"*

Each is over 60 characters, contains no banned tokens, has an `if`/`should`-clause, and looks like reasoning. None names an observable. None commits to a threshold. None could be falsified by a specific event. The kernel passes them. The operator's praxis fails them.

Phase 12 catches some of this *retrospectively* — Axis A's S2 fire-condition classifier flags exactly this pattern. But the audit fires after the action lands. The hot path is still vulnerable. v1.0 RC is the upgrade that closes the gap.

## Core question

*What class of validation is computationally hard for an LLM to satisfy without doing the underlying cognitive work — and how do we compose multiple such validations so the cost of evasion compounds?*

Three sub-questions:

1. **Threat model.** What does evasion look like, concretely, for each axis of cognitive contract the kernel claims to enforce?
2. **Architecture.** Is there a single validator that is mathematically uncheatable — or is the only honest defense a *composition* of layers with orthogonal gaming costs?
3. **Cost discipline.** What ships in v1.0 RC at acceptable hot-path latency / compute / false-positive cost, and what defers to v1.0.x or v1.1?

## The Goodhart threat, named at the validator level

Phase 12 named Goodhart at the *audit* level: any signature derived from observable features becomes a target the agent can optimize for. The same threat applies to the *validator*. A stricter regex catches more vapor today; the agent learns the regex tomorrow. Adding a semantic check (e.g. an embedding score) raises the bar; the agent learns to produce embeddings near the known-good distribution.

**There is no single uncheatable validator within the current paradigm.** Anyone who tells you otherwise is either selling something or hasn't thought about it long enough. The honest goal is not "prevent cheating" — it is "make cheating more expensive than honesty." The defense is the *composition* of layers, where the strategies for evading layer N are *mutually inconsistent* with the strategies for evading layer M, so the agent that wants to evade everything has to do work that approximates actual reasoning.

This is the spiderweb metaphor working as intended. A single thread snaps; a web holds.

## Architecture — defense-in-depth across orthogonal gaming costs

The proposal is **eight validation layers**, designed so evasion strategies in adjacent layers conflict. v1.0 RC ships layers 1-4 + 6 + 8; layers 5 and 7 defer to v1.1 on infrastructure-cost grounds.

```
                      ┌─── HOT PATH (PreToolUse, blocking) ───┐
  Layer 1  syntactic blocklist + length          [SHIPS — current]
  Layer 2  structural specificity classifier      [SHIPS v1.0 RC — extracted from Phase 12]
  Layer 3  contextual grounding (project-real entities)  [SHIPS v1.0 RC]
  Layer 4  falsification trace (executable verification) [SHIPS v1.0 RC]
  Layer 5  embedding-based vapor scoring          [DEFERRED v1.1 — infra cost]
                      └─── RETROSPECTIVE / async ─┘
  Layer 6  time-bound disconfirmation contract    [SHIPS v1.0 RC — extends Phase 12]
  Layer 7  adversarial co-validator (second LLM)  [DEFERRED v1.1 — compute cost]
  Layer 8  operator spot-check sampling           [SHIPS v1.0 RC]
```

The composition matters more than any single layer. An agent that learns Layer 2 still has to evade Layers 3, 4, 6, 8 separately — and the strategies for evading them are *not aligned*. (More on orthogonality below.)

## Per-layer proposal

Each layer has the same five fields:

- **What it checks** — the validation contract.
- **How it works** — the implementation sketch.
- **How an agent evades it** — honest threat-model (no validator is uncheatable).
- **Composition cost** — what evading this layer also requires from adjacent layers.
- **Cost / scope** — hot-path latency, false-positive risk, ship-window.

---

### Layer 1 · syntactic blocklist + length (CURRENT, stays)

**What it checks.** `disconfirmation` and each `unknowns` entry must be ≥ 15 characters and must not contain any token from the lazy-token blocklist (`none`, `n/a`, `tbd`, `nothing`, `null`, `unknown`, `해당 없음`, `해당없음`, `없음`, `모름`, `-`, `--`, `...`).

**How it works.** Module-level regex set in `core/hooks/reasoning_surface_guard.py::_surface_missing_fields`. Length threshold modulated by `derived_knobs.json::disconfirmation_specificity_min` (Phase 9 wiring) — for the maintainer's v2 profile, 15 → 27.

**How an agent evades it.** Trivial. Produce content > the threshold without any banned token. Every fluent-vacuous example above passes.

**Composition cost.** None — this is the floor. An agent that fails Layer 1 has not even tried.

**Cost / scope.** ~0.1 ms per call. Zero false positives in well-tested operator profiles. Ships today.

---

### Layer 2 · structural specificity classifier (NEW for hot path; extracted from Phase 12)

**What it checks.** `disconfirmation` must contain BOTH a conditional trigger (`if` / `when` / `should` / `once` / `after` / `unless`) AND a specific observable (numeric threshold, metric name, failure verb, log/dashboard reference). Extends to `unknowns` entries.

**How it works.** Extract `_classify_disconfirmation` from `src/episteme/_profile_audit.py` (Axis A S2 in CP3) into `core/hooks/_specificity.py` so the hot path can reuse it. Reject in PreToolUse when `_classify_disconfirmation(disconf) in ("tautological", "absence", "unknown")` — but allow `absence` to pass with a stderr advisory (legitimate absence-conditions exist in some workflows; outright blocking would over-fit).

**How an agent evades it.** Learn the trigger + observable vocabulary and produce surfaces that pad both. Example: *"if the metric exceeds the threshold within the time window, abort"* — has all three required elements, passes Layer 2, names nothing concrete. Layer 3 catches this.

**Composition cost.** An agent that evades Layer 2 by producing trigger + observable vocabulary is forced toward MORE specific language, which raises the surface area for Layer 3 (entity grounding) and Layer 5 (vapor scoring) to detect. Evading Layer 2 *helps* Layer 3 catch you.

**Cost / scope.** ~5 ms (regex set against 1-2 KB of surface text). Estimated FP rate < 5% on well-formed surfaces (the maintainer's existing tier passes). Ships v1.0 RC.

---

### Layer 3 · contextual grounding (NEW)

**What it checks.** Entities named in `disconfirmation` and `unknowns` must EXIST in the project. A surface saying *"if p95 latency exceeds 400ms"* must reference a metric (`p95`, `latency`) the project actually measures. A surface saying *"if the canary check fails"* must reference a check the project defines.

**How it works.** Best-effort grep of the project's working tree for tokens the surface references. Entity extraction is regex-based (not LLM): pull out numeric units, snake_case identifiers, file paths, environment variables, service names. For each, check `git ls-files | xargs grep -l`. Failure to ground is a *warning*, not a hard block, when the project context is sparse — the gate fires only when ≥ 2 grounded entities are found AND the named-but-not-found entity ratio exceeds 50%. This is FP-averse: a fresh repo with no metrics emits no false positives.

**How an agent evades it.** Either (a) know the project's real metrics/services and reference them honestly, or (b) introduce real entities that match its claim (write a fake test, add a fake metric to a config). Both paths require more cognitive work than producing a plausible string. Evasion path (b) leaves a git-traceable artifact — the kernel's stateful interceptor (v0.10) can flag the introduction.

**Composition cost.** Evasion path (a) is the honest path — at that point the agent has done the contextual reasoning the kernel was trying to enforce. Evasion path (b) is detectable by the stateful interceptor *and* by Layer 8 (operator spot-check). Evading Layer 3 dishonestly leaves at least two artifacts.

**Cost / scope.** ~50 ms first call (cold cache); ~5 ms subsequent (warm). FP risk on fresh projects mitigated by the "≥ 2 grounded entities present" gate. Ships v1.0 RC.

---

### Layer 4 · falsification-trace requirement (NEW — schema addition)

**What it checks.** The Reasoning Surface schema gains a new optional-but-encouraged field: `verification_trace`. Shape:

```json
{
  "verification_trace": {
    "command": "kubectl logs -n prod canary | grep 'p95.*latency' | tail -100",
    "or_dashboard": "https://grafana.internal/d/api-latency",
    "or_test": "tests/test_canary.py::test_p95_under_threshold",
    "window_seconds": 600,
    "threshold_observable": "p95 > 400"
  }
}
```

When `verification_trace` is present, the validator parses it and checks: at least one of `command` / `or_dashboard` / `or_test` is non-empty AND specific (executable, parseable URL, or test-id format). When it is absent on a high-impact op, the validator emits a stderr advisory ("recommend declaring verification_trace") but does not block — backwards compatibility for v0.11.0 surfaces.

By v1.0 RC + 1 minor (v1.0.1), `verification_trace` becomes required for the highest-impact ops (`terraform apply`, `kubectl apply` against prod, db migrations).

**How an agent evades it.** Write a fake command. The hot path can't run the command at write time (would be a side effect). But Layer 6 (time-bound contract) checks whether the command was actually run within the declared window. So writing a fake command at write time is detected at retrospective time.

**Composition cost.** Faking the verification_trace at Layer 4 commits the agent to a Layer 6 violation — the named command must show up in the agent's bash history within the declared window, or the surface is retrospectively invalidated. The two layers are designed to be mutually constraining: vapor at write time becomes a measurable failure at audit time.

**Cost / scope.** ~1 ms parse + structural check. New schema field is a non-breaking addition (optional). Ships v1.0 RC; required-for-highest-impact in v1.0.1.

---

### Layer 5 · embedding-based vapor scoring (DEFERRED v1.1)

**What it checks.** Each surface field is embedded by a small local model. The embedding is compared to a corpus of known-good surfaces (high-quality real-world cognitive contracts) and known-bad surfaces (the fluent-vacuous examples that motivated this spec, plus generated variations). Surfaces whose embeddings fall outside the known-good distribution by > N sigma are flagged.

**How it works.** Bundle a small sentence-transformer model (`all-MiniLM-L6-v2` or similar, ~80MB) with the kernel; compute embedding for `core_question` + `disconfirmation` + concatenated `unknowns`; cosine-similarity against a known-good centroid; reject if score < threshold.

**How an agent evades it.** Produce embeddings near the known-good centroid. The agent can't see the embedder's weights, but it can guess by inferring from the training-corpus name. Mitigation: ship the corpus encrypted, validate the corpus signature on load. Better mitigation: the corpus *grows* with the operator's accepted surfaces over time — so the centroid is operator-specific and not knowable from public training data.

**Composition cost.** An agent whose surfaces pass Layer 5 by producing high specificity and varied vocabulary has done much of what Layers 2, 3, 4 wanted anyway — Layer 5 is partially redundant with the lower layers, which is *defense in depth working*.

**Cost / scope.** ~200 ms per call (embedding compute). Adds ~80 MB to the install footprint. Defers to v1.1 unless an acceptable-cost embedding API path is found.

---

### Layer 6 · time-bound disconfirmation contract (NEW; extends Phase 12)

**What it checks.** When `verification_trace.window_seconds` is declared, the kernel records a *pending contract* in `~/.episteme/state/pending_contracts.jsonl`. After the window expires, an async checker (cron job or SessionStart hook) verifies: was the named command executed (via stateful interceptor records)? Did the named test run? Did the dashboard get viewed (via browser extension hook, optional)? If none of the verification methods fired, the surface is retrospectively tagged `disconfirmation_unverified` in the episodic tier.

`disconfirmation_unverified` records become input to Phase 12 — the audit loop counts unverified-rate per axis and surfaces it as drift if it exceeds a threshold.

**How an agent evades it.** Run the named command performatively (`echo "kubectl logs..." && true`). Mitigation: Layer 6 checks for command + non-zero output + recency. An echoed command produces no real output. Stronger mitigation: cross-reference the command with the project's actual telemetry — if `kubectl logs` was named and actual logs were produced, real check fired.

**Composition cost.** Layer 6 makes Layer 4 verifiable. Without Layer 6, Layer 4 is just another schema field the agent fills in. Together, they form a write-time-commit + audit-time-verify contract.

**Cost / scope.** ~0 ms hot path (only writes a pending contract record). Async check runs at SessionStart or via cron. Ships v1.0 RC as an extension to the Phase 12 audit pipeline.

---

### Layer 7 · adversarial co-validator (DEFERRED v1.1+)

**What it checks.** A second LLM (ideally a different model family — Anthropic gate validates Anthropic-written surfaces? circular — better: a small open-weights model the operator runs locally) reads the surface and answers: *"if the agent that wrote this were trying to make it look good without actually thinking, how would they have written it? Show me a fluent-vacuous variant."* The adversarial variant is then compared to the actual surface (via Layer 5's embedding similarity). If they are too similar, the surface is rejected with the adversarial variant attached as evidence.

**How an agent evades it.** Produce a surface that doesn't pattern-match "trying to look good." This requires actually committing to a falsifiable hypothesis — exactly what the kernel wants.

**Composition cost.** Layer 7 is the strongest semantic gate but also the most expensive. It's most useful in adversarial settings (CTF-like, security review) where the cost is justified. For the maintainer's day-to-day praxis, Layers 2 + 3 + 4 + 6 cover ~90% of evasion shapes at a fraction of the compute.

**Cost / scope.** ~2-5 seconds per call (LLM round-trip). $0.001-$0.01 per check. Defers to v1.1; possibly never default-enabled.

---

### Layer 8 · operator spot-check sampling (NEW)

**What it checks.** A configurable percentage (default 5%) of high-impact surfaces are flagged for explicit operator review even when they pass Layers 1-4. The flagged surfaces queue to `~/.episteme/state/spot_check_queue.jsonl`; SessionStart presents them to the operator at the start of the next session ("3 surfaces flagged for review since last session — `episteme review`"). The operator's verdict (real / vapor) trains a per-operator vapor classifier over time.

**How an agent evades it.** Cannot. The operator is the ground truth. Sampling is random, so the agent can't predict which surfaces get reviewed.

**Composition cost.** Layer 8 is the calibration layer for all the others. Operator verdicts on spot-checks are used to tune the thresholds in Layers 2, 3, 5 — making the system self-correcting against drift in either direction.

**Cost / scope.** ~0 ms hot path (only queues for review). Operator burden: 5% of high-impact surfaces × 30 seconds review = a few minutes per session for a maintainer doing ~10 high-impact ops/day. Ships v1.0 RC; sample rate configurable per-project.

## Why these layers compose well

The orthogonality test: for each pair of adjacent layers, can a single evasion strategy defeat both?

| Pair | Aligned strategy? | Mutually inconsistent? |
|---|---|---|
| L1 + L2 | Yes (verbose + has trigger+observable) | No |
| L2 + L3 | **No — verbose specific text is more grep-able for project entities** | **Yes** ← orthogonality |
| L3 + L4 | Partial (real entities help, but L4 needs executable command) | Partial |
| L4 + L6 | **No — fake command at L4 produces L6 violation at audit time** | **Yes** ← orthogonality |
| L5 + L7 | **No — embedding-near-centroid surfaces look like "trying to look good"** | **Yes** ← orthogonality |
| L6 + L8 | Mostly orthogonal (audit signal vs operator ground truth) | Mostly |

The three orthogonal pairs (L2+L3, L4+L6, L5+L7) are the load-bearing parts. An agent that wants to evade everything has to:

- Be specific (defeats L2)
- Reference real project entities (defeats L3)
- Commit to executable verification (defeats L4)
- Actually execute the verification within the window (defeats L6)
- Produce varied semantic content (defeats L5)
- Avoid pattern-matching "performance of specificity" (defeats L7)
- Hope it's not in the spot-check sample (defeats L8 statistically; ground-truth eventually catches if not this sample, the next)

By the time an agent does all six, it has approximately done the cognitive work the kernel was trying to enforce. **That is the entire goal.** Not "make cheating impossible" — make cheating cost more than honesty.

## What ships in v1.0 RC

**Hot-path additions (block at PreToolUse):**
- Layer 2 — structural specificity classifier (extracted from Phase 12 to a new `core/hooks/_specificity.py` module).
- Layer 3 — contextual grounding (best-effort, FP-averse, gates only when project context is rich enough).
- Layer 4 — `verification_trace` schema field (optional in v1.0; required for highest-impact ops in v1.0.1).

**Async additions (retrospective):**
- Layer 6 — time-bound contract checker, plumbed into Phase 12's audit pipeline.
- Layer 8 — spot-check sampling + operator review CLI (`episteme review`).

**Stays as-is:**
- Layer 1 — current syntactic + length validator.

**Deferred to v1.1:**
- Layer 5 — embedding-based vapor scoring (infra + footprint cost).
- Layer 7 — adversarial co-validator (compute cost + only useful in adversarial settings).

## Implementation sequencing

Six commits, mirroring the Phase 12 checkpoint discipline:

1. **CP1 — extract `_specificity.py`.** Move `_classify_disconfirmation` from `src/episteme/_profile_audit.py` to `core/hooks/_specificity.py`. Phase 12 imports from the new module; behavior unchanged. Tests stay green.
2. **CP2 — Layer 2 in the hot path.** `reasoning_surface_guard.py` calls `_classify_disconfirmation`; rejects on `tautological` / `unknown`; advisory on `absence`. New test class.
3. **CP3 — Layer 3 contextual grounding.** New `core/hooks/_grounding.py`. Entity extraction + project grep. Hot-path call from the guard. FP-averse gating. New test class.
4. **CP4 — Layer 4 verification_trace schema.** Update `core/schemas/reasoning-surface/...` (or wherever the surface schema lives); optional field; structural validation; doc note that v1.0.1 will require for highest-impact ops.
5. **CP5 — Layer 6 time-bound contract.** New `core/hooks/_pending_contracts.py`. Write at PreToolUse when verification_trace declared; check at SessionStart. Episodic-tier tag `disconfirmation_unverified`. Plumb into Phase 12 audit input.
6. **CP6 — Layer 8 spot-check sampling.** Configurable rate (default 5%) at PreToolUse; queue to spot_check_queue.jsonl; new `episteme review` CLI; SessionStart surface. Operator verdicts trained into per-operator threshold tuning (out of scope CP6 — landing in v1.0.1).

Each checkpoint pauses for review (same discipline as Phase 12). Tests stay green at every commit.

## Honest threat model — what STILL evades after v1.0

Per Phase 12's discipline of naming what the system does NOT cover:

1. **Coordinated multi-call evasion.** An agent that splits a high-impact op into many low-impact ops, each with bare-minimum surfaces, evades the high-impact gate per call. Mitigation: the stateful interceptor (v0.10) catches some of this; Layer 6 retrospective audit can detect the pattern. Truly mitigating requires session-level surface aggregation.

2. **Operator collusion.** If the operator stops doing real spot-checks (Layer 8) and rubber-stamps everything, the calibration loop poisons. Mitigation: the audit loop (Phase 12) catches operator behavior drift the same way it catches agent behavior drift — but the operator is the ground truth and there is no recourse if the ground truth is corrupted. This is by design.

3. **Adversarial-trained agent.** An agent specifically trained on bypassing episteme's validators is a different threat class than the agents in scope. Mitigation: Layer 7 (adversarial co-validator) is the partial defense; full defense requires either a closed-system runtime (proxy daemon, see 0.10 carry-over) or a different threat model entirely (treating the agent as untrusted). Out of v1.0 RC scope.

4. **High-volume noise drowning the signal.** An agent producing 10x the normal surface volume saturates Layer 8's sample budget and Phase 12's audit windows. Mitigation: Layer 6 records contracts independently of Phase 12's window; spot-check rate scales with volume. Not a hard solve.

5. **Semantic Goodhart on Layer 5 / Layer 7.** Once the embedding model or adversarial co-validator is known, the agent can be fine-tuned against it. Mitigation: rotate the embedding model on each kernel release; never publish the adversarial co-validator's weights. This is an ongoing arms race; the kernel cannot win it permanently, only stay ahead.

This section is load-bearing. Any later change to v1.0 RC scope that claims to close one of these without explicit mitigation is a governance change, not an implementation tweak.

## Non-goals

- **Provably uncheatable validation.** Out of scope. The honest claim is "evasion costs more than honesty," not "evasion is impossible."
- **Real-time LLM-based validation in the hot path.** Latency cost too high for v1.0 RC. Layer 7 is async-only.
- **Operator profile mutations from spot-check verdicts.** Verdicts inform threshold tuning per project, never auto-edit the global operator profile. (Same D3 discipline as Phase 12.)
- **Replacing Phase 12.** v1.0 RC extends the retrospective loop; it does not substitute for it. Both layers ship and run together.
- **Cross-operator validation.** Multi-operator coordination is on the deferred multi-operator roadmap; v1.0 RC stays single-operator like v0.11.0.

## Open questions (for maintainer review before implementation)

1. **Layer 3 entity extraction — regex or LLM?** Proposal: regex, because regex is FP-averse and predictable; an LLM extractor introduces its own Goodhart surface. Alternative: small local model for entity extraction only (no semantic judgment). Strong lean: regex.

2. **Layer 4 verification_trace required-for-highest-impact threshold.** Which ops cross from "advisory" to "required"? Proposal: `terraform apply`, `kubectl apply` against any context matching `prod`/`production`, `alembic upgrade`, `prisma migrate deploy`, `gh release create`. Maintainer call.

3. **Layer 6 pending-contract storage.** Proposal: `~/.episteme/state/pending_contracts.jsonl` with TTL = max declared window across all open contracts. Cleanup at SessionStart.

4. **Layer 8 sample rate default.** Proposal: 5% (one in twenty). Configurable per-project via `.episteme/spot_check_rate`. Maintainer call on whether to start higher (10%) for the first month and decay as the corpus grows.

5. **Cost ceiling for hot path.** Layers 2-4 should add < 100 ms total in the worst case. Proposal: profile each layer in isolation; if any exceeds 50 ms p95, gate behind a `derived_knobs.json` toggle so the operator can opt out.

6. **Phase 12 vs v1.0 split.** Phase 12 currently catches some of what Layer 2 would catch (Axis A's S2). Proposal: keep both — Phase 12 audits OVER TIME, Layer 2 enforces AT WRITE. The retrospective signal is different from the hot-path signal because the audit looks at distributions and Layer 2 looks at individual surfaces. Both useful, both ship.

## Verification — v1.0 RC is "done" when

- All six checkpoints land with paused-review-before-commit discipline.
- Test suite stays green at every commit (304 today; CP1 should hold; CP2-CP6 each add ~15-25 tests).
- Hot-path latency profile shows p95 < 100 ms added by Layers 2-4 combined.
- Five fluent-vacuous evasion examples from "Why this exists" are now blocked at write time by some combination of Layers 2-4. (This is the honest acceptance test — if the spec ships and the maintainer's named threats still pass, the design failed.)
- Phase 12 audit dogfood shows `disconfirmation_unverified` rate < 10% on the maintainer's tier after 30 days of Layer 6 active. Above 10% means the kernel is enforcing contracts the operator isn't honoring — either tighten the operator's discipline or relax the contract; the audit surfaces the gap.
- Layer 8 spot-check delivers ≥ 1 actionable operator verdict per week of normal use over the RC soak. Below this, sample rate is too low; above 5/week, sample rate is too high (operator burden).
- This document moves from `draft` to `approved` with maintainer sign-off on the six open questions.

## What this spec does NOT cover

- Implementation-level code (function bodies, exact regex patterns, full test fixtures). Those emerge during the checkpoint sequence, traceable back to this spec.
- The Layer 5 corpus assembly (which surfaces count as known-good?). Deferred along with Layer 5 itself.
- The Layer 7 adversarial-co-validator model choice. Deferred along with Layer 7.
- Performance optimization beyond the worst-case latency budget. Out-of-scope until profile data exists.
- v1.0 GA scope. v1.0 RC is the gate; GA is `v1.0.0` after the soak window confirms the engineering AND cognitive-adoption gates from `docs/NEXT_STEPS.md` items 21-28.

---

## Review checklist for the maintainer

Before signing off on this draft:

1. The eight-layer architecture covers the threat model as you read it. If a major evasion class is missing, name it before implementation begins.
2. The three orthogonal pairs (L2+L3, L4+L6, L5+L7) are load-bearing — any reduction in scope (e.g. dropping L3) breaks the orthogonality story and weakens the composition argument.
3. The six v1.0 RC checkpoints are sized at one logical commit each, mirroring Phase 12's discipline. If any feels too large, it gets split before implementation.
4. The honest threat model section names every evasion class you can think of after reading. If you find a new one during review, it joins the list rather than being silently countered.
5. The "make cheating cost more than honesty" framing is correct. If you believe an uncheatable validator is achievable within v1.0 RC scope, this spec needs to be rebuilt around that claim.
6. The six open questions — proposal or alternative on each.

Once signed off, this document changes status to `approved` and implementation begins as v1.0.0-rc1 work after 0.11.0 soak + tag.
