# PHASE_12_LEXICON — default lexicons for the profile-audit loop

Status: **authoritative** · Version: 1.0 · Loaded by: `src/episteme/_profile_audit.py`

These are the five lexicons the profile-audit loop uses to compute the signatures defined in `docs/DESIGN_V0_11_PHASE_12.md`. They are deliberately *modest* — not exhaustive. A lexicon that enumerates every possible token invites false-positive matches and false-confidence coverage; a narrow one is honest about what it detects.

**Operator override.** To extend or replace these lexicons for a specific project, create `core/memory/global/phase_12_lexicon.md` with the same heading structure. When the override file is present, the audit uses it instead of this default and records the fingerprint of the lexicon-in-use in every audit record — so a change in lexicon is visible in the record stream, not silent.

**Match rule.** Terms are matched case-insensitively against whitespace-collapsed content. Multi-word terms (e.g. "rolls back") are matched as regex word-boundary phrases. This matches the hot-path normalization pattern already used by `core/hooks/reasoning_surface_guard.py`.

**The Goodhart limit.** A sufficiently aware agent can pad its Reasoning Surfaces with failure-frame tokens to pass axis A's signature. The defense is D1 (multi-signature convergence — A's second signature is syntactic, not lexical) plus operator review, not a longer lexicon. Growing the lexicon to catch more shapes also grows the surface area for false positives; this file is version-stamped so any growth is deliberate and reviewable.

---

## failure_frame

Used by: **axis A · `dominant_lens: failure-first`** — signature S1 (failure-frame ratio in `unknowns` + `disconfirmation`).

An operator with `failure-first` as their dominant lens names what could break before what should work. High density in this lexicon across episodic records predicts the claim; low density is a weak signal against.

- fails
- breaks
- rejects
- errors
- regresses
- blocks
- denies
- timeout
- timeouts
- invalidates
- violates
- leaks
- diverges
- corrupts
- exhausts
- stalls
- rolls back
- reverts
- aborts
- crashes
- loses data
- data loss
- hangs
- deadlocks

## success_frame

Used by: **axis A · `dominant_lens: failure-first`** — signature S1 (denominator of the ratio).

The counterpart. Dominance of success-frame language over failure-frame is evidence against the `failure-first` claim. Used as the denominator in the ratio: `failure / (failure + success)`.

- succeeds
- works
- passes
- completes
- validates
- approves
- renders
- delivers
- ships
- finishes
- resolves
- returns ok
- returns success
- green
- healthy

## buzzword

Used by: **axis B · `noise_signature: status-pressure`** — signature S1 (buzzword density in `core_question` + `knowns`).

Fluent, impressive-sounding descriptors that survive by being unfalsifiable. An operator with a claimed susceptibility to status-pressure is predicted to emit these at above-baseline rates — and an operator with a claimed *counter-screen* against buzzword-leak (per `core/memory/global/operator_profile.md`) is held accountable for keeping the rate below baseline.

- robust
- seamless
- end-to-end
- enterprise-grade
- world-class
- best-in-class
- holistic
- synergy
- synergies
- cutting-edge
- battle-tested
- production-ready
- scalable
- resilient
- elegant
- idiomatic
- next-generation
- next-gen
- paradigm shift
- game-changer
- game-changing
- disruptive

## causal_connective

Used by: **axis 5 · `explanation_depth: causal-chain`** — signature (density of causal connectives in `knowns` + `assumptions`).

Explanation-depth `causal-chain` predicts high density of because-chains. Reserved for checkpoint ≥ 3 implementation of this axis; lexicon available here so checkpoint 1 can fingerprint it in the audit record.

- because
- therefore
- so that
- as a result
- which causes
- due to
- hence
- consequently
- leads to
- results in
- thereby
- thus
- owing to

## rollback_adjacent

Used by: **axis D · `asymmetry_posture: loss-averse`** — signature S2 (rollback-path mention on irreversible-op records).

An operator with loss-averse posture on irreversible ops is predicted to mention rollback / recovery / abort paths in their Reasoning Surface's `knowns` or `assumptions` before committing. Absence is weak evidence against the claim.

- rollback
- revert
- undo
- abort
- back out
- restore from
- restore from backup
- recovery
- disaster recovery
- kill switch
- circuit breaker
- feature flag
- feature-flag
- emergency stop

---

## Lexicon fingerprint

Each audit record carries a `lexicon_fingerprint` field — the first 16 hex chars of the sha256 over the sorted, canonicalized lexicon contents. A change in any lexicon produces a different fingerprint, so readers of `profile_audit.jsonl` can detect lexicon drift between runs even if the filename didn't change. See `src/episteme/_profile_audit.py::_lexicon_fingerprint` for the canonicalization.
