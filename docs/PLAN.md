# Plan

Current active plan for episteme development.

**Core Question (this cycle):** Now that v0.11.0 has shipped the retrospective profile-audit loop, what structural protocol — enforced at the point of state mutation — forces an LLM to (a) generate an auditable causal-consequence model, (b) synthesize context-dependent protocols from conflicting sources into a tamper-evident framework, (c) proactively surface those protocols as operator guidance at the point of future decisions, and (d) keep the system's own self-model coherent as the agent edits it (patch-vs-refactor, symmetric cascade sync, continuous digging & logging)? The v1.0 RC answer is the three-pillar / four-named-blueprint architecture specified in `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`.

**Constraint regime:**
- Allowed: augmenting kernel docs, README, issue templates, ops docs, schema additions that extend (not reframe) existing invariants; implementing the approved 10-CP v1.0 RC plan with paused-review-before-commit discipline
- Forbidden: modifying `templates/` or `labs/` scaffolds; breaking kernel invariants without Evolution Contract; relaxing load-bearing spec countermeasures (three pillars, four named blueprints + generic max-rigor fallback, three+one orthogonal pairs, <100 ms hot-path ceiling, sample-rate schedule, hash-chain scope, BYOS stance, advisory-only Pillar 3 guidance) outside a governance event
- Kernel changes require `kernel/CHANGELOG.md` entry first
- Blueprint D dogfood: the kernel must satisfy Blueprint D on its own architectural edits. Editing episteme-while-editing-episteme without firing Blueprint D is an RC failure regardless of test count.

---

## Active milestone: v1.0.0 RC — Causal-Consequence Scaffolding, Protocol Synthesis & Continuous Self-Maintenance

### Goal

Upgrade the Reasoning Surface from syntactic enforcement to a three-pillar / four-named-blueprint architecture that grafts onto the LLM substrate what it cannot perform natively: (1) **causal-consequence modeling** per action (Pillar 1 · Cognitive Blueprints, Pillar 2 · Append-Only Hash Chain), (2) **context-indexed protocol synthesis** from conflicting sources (Pillar 3 extraction arm — Axiomatic Judgment + Fence Reconstruction), (3) **active operator guidance** using accumulated protocols (Pillar 3 guidance arm), and (4) **continuous architectural self-maintenance** — patch-vs-refactor evaluation, symmetric cascade synchronization across the full blast radius, continuous digging & logging of adjacent discoveries (Blueprint D · Architectural Cascade & Escalation, synthesizing at system-architecture scope). The kernel is skill-agnostic (BYOS): it intercepts state mutation regardless of which tool / MCP server / agent framework generated the command. See `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` — *Design — Causal-Consequence Scaffolding & Protocol Synthesis — v1.0 RC* (status `approved (reframed, third pass)` 2026-04-21) for the full spec, threat model, and verification criteria.

**Forward pointer (v1.1+).** Architectural vision for the post-v1.0-GA cycle is at `docs/DESIGN_V1_1_REASONING_ENGINE.md` (Event 55 draft → Event 56 first-pass approval; status `approved (reframed, first pass)`). It introduces **3 Cognitive Arms** (Arm A · Temporal Integrity, Arm B · Causal Synthesis, Arm C · Self-Consistency Convergence) operating on top of v1.0's three Pillars — Pillars stand still (v1.0 unchanging foundation); Arms reach (v1.1 fluid active engines refactoring the kernel's own knowledge over time). Six load-bearing operator decisions in the first-pass approval (3 Cognitive Arms naming locked, staggered 30d/60d/90d verification windows confirmed, CP-MODEL-01 cross-protocol consistency check ships in v1.1, D11 Operator Fatigue Guardrails added, Claude Code first per BYOS, Zero-LLM Entity Extraction named primary technical risk). v1.1 CP work begins only after the v1.0 GA cut completes AND the soak window's gates resolve favorably — current cycle remains the v1.0.0 RC soak.

### Phases (10 CPs)

| CP | Scope | Status |
|---|---|---|
| 1 | Extract `_classify_disconfirmation` from `src/episteme/_profile_audit.py` to `core/hooks/_specificity.py`. Phase 12 imports from new module; behavior unchanged. **Bundled with the Blueprint-D self-dogfood cascade sync** (see `docs/PROGRESS.md` Event 7). 304/304 tests green. | **code + cascade complete; awaiting paused-review-before-commit** |
| 2 | Scenario detector (`core/hooks/_scenario_detector.py`) + blueprint registry (`core/blueprints/`) with generic-fallback blueprint. No behavior change until CP5. | **shipped — 2026-04-21; 326/326 tests green; awaiting paused-review-before-commit** |
| 3 | Layer 2 in hot path, blueprint-aware. `reasoning_surface_guard.py` classifies against selected blueprint's fields. | **shipped + committed `101d3cd` — 2026-04-21; 340/340 tests green. 2 of 5 spec fluent-vacuous examples block at Layer 2; remaining 3 deferred to CP4/CP6 layered defense (see deferred_discovery #9).** |
| 4 | Layer 3 contextual grounding, blueprint-aware. New `core/hooks/_grounding.py`. FP-averse gating. | **shipped + committed `2558c67` — 2026-04-21; 361/361 tests green (+21 new, zero regressions). 0 of 3 remaining CP3-gap fluent-vacuous examples catch at Layer 3 — they contain no entity-shaped tokens, pass Layer 3 intentionally per compose-across-layers discipline; close at CP6 Layer 4 `verification_trace`. See `docs/PROGRESS.md` Event 11.** |
| 5 | Blueprint B (Fence Reconstruction), realized end-to-end + **first Pillar 3 synthesis output** — constraint-safety protocol emitted on successful removal. | **shipped + committed `117fa69` — 2026-04-21; 392/392 tests green (+30 new, zero regressions). YAML parser extended for list-of-dicts; compound-AND selector (command-head removal-verb ∧ constraint-path); 5 required Fence fields validated; `_classify_origin_evidence` added; per-correlation-id pending-marker + PostToolUse finalizer writes `cp5-pre-chain` protocol entries to `~/.episteme/framework/protocols.jsonl`. See `docs/PROGRESS.md` Event 12.** |
| 6 | Layer 4 `verification_trace` schema. Blueprint-shaped variants; blocking at generic high-impact (Posture A amendment); advisory-only for Axiomatic / Consequence Chain / Blueprint D stubs in RC. | **shipped — 2026-04-21; 429/429 tests green (+37 new, zero regressions). New `core/hooks/_verification_trace.py` — VerificationTrace dataclass + validate_trace + smoke_test_rollback_path. Generic blueprint promoted to `verification_trace_required: true` closing the three fluent-vacuous examples that leaked CP3/CP4 (Posture A amendment to spec § Layer 4). Fence blueprint declares `verification_trace_maps_to: rollback_path` — existing `rollback_path` wrapped as L4 command slot and smoke-tested (shlex-parse + prod-marker absence + file-extension path-existence). Three blueprint stubs shipped structure-only: `axiomatic_judgment.yaml`, `consequence_chain.yaml`, `architectural_cascade.yaml` (all with empty selector_triggers — do not fire at RC). `_blueprint_registry.py` extended with two optional scalar fields (`verification_trace_required`, `verification_trace_maps_to`); YAML parser unchanged per CP6 Deferred Discovery #17 ruling ("not needed at CP6"). See `docs/PROGRESS.md` Event 13.** |
| 7 | Pillar 2 hash chain + Pillar 3 substrate. `_chain.py` (shared) + `_pending_contracts.py` + `_framework.py` (protocols AND deferred-discovery records) + `_context_signature.py`. Phase 12 audit gains chain-verification precondition. | **shipped — 2026-04-21; 469/469 tests green (+40 new, zero regressions). Four new hook modules: `_chain.py` (SHA-256 envelope + GENESIS sentinel + atomic append + verify + reset), `_context_signature.py` (conservative six-field dict — project_name / project_tier / blueprint / op_class / constraint_head / runtime_marker; profile-axis folding deferred to CP9 per CP7 plan Q3), `_pending_contracts.py` (Layer 6 write + expiry sweep + 72h grace archive + idempotent re-write + collision rejection), `_framework.py` (two independent streams — protocols.jsonl + deferred_discoveries.jsonl; list filters; retroactive `upgrade_cp5_prechain` walker). Fence synthesis writer switched to `_framework.write_protocol`; new records land as `cp7-chained-v1` envelopes. Guard wiring: on Layer 4 pass AND `window_seconds` declared, writes hash-chained pending contract. Phase 12 audit gains additive `chain_integrity` field (per-stream verdicts; per-stream isolation — a framework break does NOT halt episodic-derived axes). Three `episteme chain` CLI subcommands: `verify`, `reset` (with operator confirmation), `upgrade`. Retroactive upgrade produced no-op on live state (no CP5 records ever synthesized on exit-zero — CP5's dogfood tripped its own selector); walker verified on synthetic 3-record fixture with byte-identical re-run output (determinism gate). See `docs/PROGRESS.md` Event 14.** |
| 8 | Layer 8 spot-check sampling. 10% → 5% schedule; blueprint + protocol-quality verdicts; Blueprint D resolutions carry a "cascade-theater vs real sync" verdict; hash-chained queue; `episteme review` CLI. | **shipped — 2026-04-21; 502/502 tests green (+33 new, zero regressions). New `core/hooks/_spot_check.py` (substrate). PostToolUse sampling per CP8 plan Q1 — called from both `fence_synthesis.py` and `calibration_telemetry.py`, idempotent-by-correlation-id. First-sample install anchor at `~/.episteme/sample_schedule_anchor.json` (plan Q3). 10%/5% step-down at 30 days with per-project override at `<cwd>/.episteme/spot_check_rate`. Multiplier algebra: `base × max(blueprint_fired / synthesis_produced / blueprint_d_resolution)`, capped at 1.0. Verdict enums locked: surface_validity {real/vapor/wrong_blueprint}, protocol_quality {useful/vague/overfit/wrong_context}, cascade_integrity {real_sync/theater/partial}. Verdicts append-only (latest-wins on revision per plan Q2). 7-day skip TTL (plan Q4). `episteme review {--list,--stats,--correlation-id,--revise}` CLI. SessionStart banner in `session_context.py`. Phase 12 chain_integrity adds `spot_check_queue` stream (per-stream isolation). See `docs/PROGRESS.md` Event 15.** |
| 9 | Pillar 3 active guidance surface. PreToolUse framework query (one advisory per op); SessionStart digest including deferred-discovery count; `episteme guide [--context] [--since] [--deferred]` CLI (minimal). | **shipped — 2026-04-21; 528/528 tests green (+26 new, zero regressions). New `core/hooks/_guidance.py` — query + verdict filter + advisory formatter + warm cache keyed on `protocols.jsonl` mtime. Default `min_overlap=4/6` (conservative per CP9 plan); override at `<cwd>/.episteme/guidance_min_overlap`. Hot-path wiring in `reasoning_surface_guard.py` between scenario detection and Layer 3 — never blocking, silent on zero match. Advisory format: two physical lines with `[episteme guide]` prefix + 12-char cid prefix. Verdict filter: protocols with latest CP8 `surface_validity == "vapor"` skipped. Project-scoped query — cross-project protocols suppressed. SessionStart digest extended with `"framework: N protocols since last session (T total), M deferred discoveries pending"` + `~/.episteme/state/last_session.json` tracker. `episteme guide {--context,--since,--deferred,--json}` CLI (read-path only; authoring v1.0.1). Spec § Pillar 3 substrate section updated to pin the CP9 decisions. See `docs/PROGRESS.md` Event 16.** |
| 10 | Blueprint D (Architectural Cascade & Escalation) scaffolding. `core/blueprints/architectural_cascade.yaml`; new `core/hooks/_cascade_detector.py` (four selector triggers); structural validation of `patch_vs_refactor_evaluation` + `blast_radius_map[]` + `sync_plan[]`; every `deferred_discoveries[]` entry hash-chained into the framework at PreToolUse. Retrospective sync-plan verification lands in v1.0.1. | **shipped — 2026-04-22; 565/565 tests green (+37 new, zero regressions). New `core/hooks/_cascade_detector.py` (4 triggers: self-escalation, sensitive-path target, refactor-lexicon + cross-ref ≥ 2, generated-artifact symbol reference with ≥ 5-char word-bounded stem match). New `core/hooks/_blueprint_d.py` (validator + deferred-discovery writer). `core/blueprints/architectural_cascade.yaml` populated. `core/hooks/_scenario_detector.py` dispatches cascade after Fence per CP10 priority decision (Fence > Blueprint D > generic — Fence's tighter compound AND wins on `rm kernel/*.md`). Guard wires `_validate_blueprint_d` + deferred-discovery writes after Layer 3 passes for cascade blueprint. Kernel-state-file exemption added post-live-dogfood: writes targeting `.episteme/reasoning-surface.json` / `.episteme/advisory-surface` / `.episteme/strict-surface` bypass cascade detection (the CP10 commit itself got caught in the detector's own circular loop — exemption landed in the same commit). Locked decisions per plan: threshold = 2, core/hooks/ in sensitive paths, strict MANIFEST/CHANGELOG scope, blocking on missing fields, `other` advisory, theater advisory + L8 review. See `docs/PROGRESS.md` Event 17.** |

### Load-bearing spec constraints

Any reduction in these is a governance event, not an implementation tweak:

- Three pillars: Cognitive Blueprints, Append-Only Hash Chain, Framework Synthesis & Active Guidance.
- Four named blueprints + generic maximum-rigor fallback: Axiomatic Judgment, Fence Reconstruction, Consequence Chain, Architectural Cascade & Escalation (named) + Consequence-Chain-shaped fallback for unclassified high-impact ops.
- Four orthogonal pairs: L2+L3, L4+L6, L5+L7, blueprint-selector × L8 selection sample.
- Hot-path ceiling: < 100 ms p95 (Layers 2-4 + scenario detector including cascade detector + framework query combined).
- Sample-rate schedule: 10% for first 30 days (calendar-from-install) → 5%.
- Hash-chain scope in RC: episodic tier + pending contracts + framework protocols (including `deferred_discovery` records) only.
- BYOS: no tool-specific validation paths; no prescriptive tool-usage in blueprints.
- Pillar 3 guidance is advisory-only (never blocking).
- Blueprint D on the kernel itself: editing episteme-while-editing-episteme without firing Blueprint D fails the RC.

### Verification gates

- All 10 CPs land with paused-review-before-commit; test suite green at every commit (baseline 202; each CP adds ~15-25 tests).
- Hot-path p95 < 100 ms for full hot-path stack.
- Five fluent-vacuous evasion examples from the spec § "Why this exists" blocked at write time.
- End-to-end dogfood on a real constraint-removal op: Fence Reconstruction fires, blueprint-populated surface produced, hash-chained Layer 6 record written, framework protocol emitted, protocol subsequently surfaces as guidance on a matching future op.
- **Blueprint D dogfood on the kernel itself:** at least one real architectural-cascade op on the episteme repo fires Blueprint D, produces a non-trivial `blast_radius_map[]` grounded to real surfaces, a `sync_plan[]` with concrete actions per surface, ≥ 1 hash-chained `deferred_discoveries[]` entry, AND the resulting diff touches every surface named in the map without orphan-reference regression.
- **Deferred-discovery flow-through:** ≥ 3 deferred-discovery entries logged during the soak; ≥ 1 either promoted to a named phase/CP in NEXT_STEPS.md or triaged to "won't fix" with rationale. A log that only grows is architectural-debt accumulation, not self-maintenance.
- After 30-day RC soak: `disconfirmation_unverified` rate < 10% on maintainer's tier; framework holds ≥ 3 non-trivial protocols with ≥ 1 fired-as-guidance; chain verification succeeds across all three streams (episodic, pending contracts, framework protocols including deferred-discovery records); Layer 8 delivers ≥ 1 actionable verdict per week.

### Open assumptions

- Fence Reconstruction is the strongest end-to-end demonstration because it binds to an existing audit axis (`fence_discipline`). If a later reading of the spec identifies a stronger first-realized blueprint, CP5 is open to change before implementation.
- Pillar 3's context-signature algorithm (regex + entity hashing) is FP-averse enough for a useful framework query rate in the first 30 days. Unverified until real synthesis traffic accumulates.
- Advisory-only guidance is the right posture — collapsing into blocking would feedback-loop the kernel's own synthesis against the operator. If operator spot-check verdicts over the soak consistently flag "missed the obvious guidance," revisit at v1.0.1.
- Axiomatic Judgment's synthesis-arm fields (structure only in RC) accumulate enough operator-visible value during soak to justify full realization in v1.0.1. If synthesis-arm fields are empty or useless across 30 days, the design needs revision before v1.0.1.
- Blueprint D's four selector triggers (cross-surface-ref diff check, refactor/rename/deprecate lexicon, self-escalation `flaw_classification`, generated-artifact symbol-reference check) cover the cascade classes that actually occur in real episteme edits. Unverified until soak produces real firings; missed classes join a governance-gated selector-expansion request before v1.0.1.
- The Blueprint D risk of cascade-theater (filling `blast_radius_map[]` with `not-applicable` entries to pass the gate) is sufficiently countered by Layer 3 entity grounding + Layer 8 "cascade-theater vs real sync" verdict dimension. If soak shows high theater rate, the selector raises rigor or the blueprint adds a minimum-entries threshold per flaw class.

---

## Parallel work stream: GTM site + visualization dashboard (`web/`)

External-surface work that runs alongside the v1.0 RC soak. Does not touch kernel code or RC gates. Tracked here for visibility and for retrospective Blueprint-D orphan-reference scope when the site begins referring to kernel names.

### Goal

Ship a marketing landing page + interactive operator-console dashboard that visualize the three kernel artifacts (`reasoning-surface.json`, hash-chained `protocols.jsonl` / `deferred_discoveries.jsonl`, Blueprint D four-trigger cascade state). Narrative contract: frame episteme as a *thinking framework* that extracts context-fit protocols and actively guides; do not frame as a security blocker. Aesthetic contract: dark operator-console (near-black substrate, bone-white text, four scarce signal accents); Fraunces + Satoshi + JetBrains Mono typography; no gradients; no Inter / Roboto / Space Grotesk.

### Stages

| Stage | Scope | Status |
|---|---|---|
| v1 static | Next.js 16 + React 19 + Tailwind 4 scaffold at `web/`; typed domain models mirror `episteme/reasoning-surface@1`; `ReasoningMatrix` + `HashChainStream` hero visuals; landing + dashboard pages; static JSONL fixtures under `public/data/` generated by `scripts/build-fixtures.mjs`; `pnpm build` green (both routes statically prerendered). | **shipped — 2026-04-22; see `docs/PROGRESS.md` Event 18** |
| v2 local-live | Three route handlers at `web/src/app/api/{chain,protocols,surface}/route.ts`; `web/src/lib/server/` envelope-schema + readers matching CP7's `cp7-chained-v1` envelope across both framework streams; `useLiveResource` SWR-lite hook; three `Live*` wrappers preserving the prop-based viz contract; `EPISTEME_MODE=fixtures` default under `NODE_ENV=production` so public deploys stay rich without kernel access; `pnpm build` green; smoke-tested against the kernel's own on-disk state (5 real deferred-discovery records render with `integrity: ok`). | **shipped — 2026-04-22; see `docs/PROGRESS.md` Event 19** |
| v1.1 polish | Seven reference-inspired richness cues without touching typography or narrative: `.atmosphere` chromatic glow mesh, `.panel-gradient` light-from-top borders, `.gradient-blur` progressive top-nav blur, `.column-grid` animated data streams, `CornerMarkers` +-glyphs, `AmbientStatus` header chrome (wired live to `/api/{surface,chain,protocols}`), `.mask-word` staggered hero reveal. Build green; aesthetic signal counts verified in rendered markup. | **shipped — 2026-04-22; see `docs/PROGRESS.md` Event 20** |
| visual coherence | `docs/ARCHITECTURE.md` Mermaid + `docs/assets/src/architecture_v2.dot` + `docs/assets/system-overview.svg` all rewritten to v1.0 RC shipped state (three pillars + four named blueprints + Blueprint D cascade detector); SVGs regenerated via `dot -Tsvg`; PNGs rasterized via `rsvg-convert` at 144 dpi; README.md stale "in flight" line flipped. Kernel repo untouched. Blueprint D self-dogfood gate fired twice and was satisfied both times during the pass. | **shipped — 2026-04-22; see `docs/PROGRESS.md` Event 21** |
| demo + launch prep | `scripts/demo_posture.sh` rewritten as the 4-act Cognitive Cascade (Blueprint B → Blueprint D → Pillar 3 active guidance) and recorded by the operator as `docs/assets/demo_posture.{cast,gif}`; Event 17 DD #2 formally closed. `web/next.config.ts` hardened (strict mode, powered-by off, server-actions limit). `web/README.md` rewritten as the Vercel deploy contract with the full `NODE_ENV × EPISTEME_MODE` matrix; root `README.md` gains a one-line pointer. Header layout fix — `AmbientStatus` gated `xl:flex` + three-row compact; nav ul `shrink-0` with `lg:block`-gated marketing links so `dashboard →` stops breaking at the `lg`-but-not-`xl` range. Fixtures-default on production re-verified. | **shipped — 2026-04-22; see `docs/PROGRESS.md` Event 22** |
| post-deploy hotfix | `README.md` + `docs/DEMOS.md` + `demos/03_differential/README.md` all flipped from the stale `posture_demo.gif` filename to the new `demo_posture.gif`; obsolete v0.11 assets deleted (`docs/assets/posture_demo.{cast,gif}`, root `strict_demo.cast`). Rasterized PNGs kept pending a README hero decision. | **shipped — 2026-04-22; see `docs/PROGRESS.md` Event 23** |
| post-live asset audit | Strict `![alt](path)` embed-vs-link audit across the repo: the only live image embed is `README.md:7 → demo_posture.gif`. Four unused files deleted (`architecture_v2.png`, `system-overview.png`, `strict_mode_demo.{cast,gif}`; ~2 MB freed). `docs/CONTRIBUTING.md` and `docs/DEMOS.md` rewritten to point at the Cognitive Cascade hero demo instead of the deprecated strict-mode cast. SVGs retained (linked from NARRATIVE.md); `scripts/demo_strict_mode.sh` retained as a runnable local demo even though its GIF no longer ships. | **shipped — 2026-04-22; see `docs/PROGRESS.md` Event 24** |
| v3 streaming | SSE from an `episteme serve` daemon; viz components react live to real kernel activity. | **deferred past v1.0 GA** |
| deploy | Deploy target selection (Vercel leading candidate given Next 16). Scope includes production env-var plumbing for `EPISTEME_HOME` or static-export mode. | **decision pending** |

### Constraint regime (GTM-specific)

- Allowed: `web/` edits; fixture regeneration; TS type additions that mirror kernel schemas.
- Forbidden: vocabulary drift toward security / blocker / guardrail framing; font family additions outside the three declared families; new color accents without operator sign-off.
- Kernel repo untouched by this work stream; the kernel's Blueprint D does not apply to `web/` edits today (no cross-refs to kernel files yet). First kernel-name cross-reference in `web/` (e.g. mentioning `_cascade_detector.py` by filename) promotes `web/` into the Blueprint D blast radius for subsequent edits.

### Open assumptions

- Satoshi's Fontshare public download is stable enough to rely on during soak; the two variable woff2 files are committed to `web/public/fonts/satoshi/` so CI reproduction does not depend on Fontshare availability.
- Tailwind 4 `@theme` token → utility generation produces the expected classes (`bg-void`, `border-hairline`, `text-chain`, `font-display`) at build; verified for v1 via `pnpm build` green. Regression only if tokens are renamed.
- Deployment host TBD; the static-export option preserves shippability even if a node runtime target is not yet chosen.

---

## Closed milestone: 0.11.0 — Kernel depth + personalization + memory architecture — complete 2026-04-21

### Goal
Close the two structural weak legs identified in the v0.10 retrospective: the personalization layer (operator profile was 6 thin axes, mostly process-shaped) and the memory architecture (schemas existed but tiering/retrieval/promotion contract did not). Also expand the kernel's attribution surface to cover frameworks now load-bearing but previously uncited — requisite variety, Gall's law, Tetlock calibration, Laplace/Jaynes probabilistic update, Goodhart's law, Klein's RPD, Chesterton's fence, Feynman's self-deception, Festinger's dissonance. Body docs stay jargon-free; attribution lives only in `REFERENCES.md`.

### Phases

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | `kernel/REFERENCES.md` — add 9 primary sources, 4 secondary (Tulving/Squire, Snowden, Wittgenstein, etc.). Bumps primary-source count 14 → 23. | **complete** |
| 2 | `kernel/CONSTITUTION.md` — variety-match and fence-check lenses added to Principle III stack; working-simple-precedes-working-complex note added to Principle IV; "not a frozen measurement" caveat added to *What it is not*. No buzzwords in body. | **complete** |
| 3 | `kernel/FAILURE_MODES.md` — added "Governance-layer failure modes" section with three new modes (constraint-removal, measure-as-target drift, controller-variety mismatch) as a separate layer so the Kahneman six-mode taxonomy stays intact. | **complete** |
| 4 | `kernel/REASONING_SURFACE.md` — evidence-weighted update mechanic, `domain` marker (Clear/Complicated/Complex/Chaotic), `tacit_call` boolean. Closes Gap D and the Cynefin gap. | **complete** |
| 5 | `kernel/KERNEL_LIMITS.md` — added limits 7 (rule-based governance against general-capability agents) and 8 (scorecard as target). | **complete** |
| 6 | `kernel/OPERATOR_PROFILE_SCHEMA.md` v2 — rewrote with two scorecard layers (process 0–5 + cognitive-style 9 typed axes), per-axis metadata (`confidence`, `last_observed`, `evidence_refs[]`, `drift_signal`), `expertise_map`, declared *derived behavior knobs* adapters compute from axes, and the Audit Discipline section that counters measure-as-target drift. | **complete** |
| 7 | `kernel/MEMORY_ARCHITECTURE.md` (new) — five tiers (working / episodic / semantic / procedural / reflective) with purpose / lifetime / writer / reader each. Retrieval contract (query-by-situation, similarity scoring). Promotion contract (episodic → semantic → profile-drift proposal, gated). Forgetting contract (TTL + compaction per tier). Write/read discipline per workflow stage. Integrity guarantees (episodic append-only, promotion idempotent, forgetting logged). | **complete** |
| 8 | `kernel/SUMMARY.md` + `kernel/README.md` — pointer updates to new docs; summary table expanded (six modes + three governance-layer modes; two scorecard layers; five memory tiers). | **complete** |
| 9 | Implementation: hook-layer consumption of derived behavior knobs. New `core/hooks/_derived_knobs.py` carries the axis-to-knob derivation rules; `reasoning_surface_guard.py` reads `disconfirmation_specificity_min` + `unknown_specificity_min` from `~/.episteme/derived_knobs.json` with default-15 fallback. For the maintainer's v2 profile (uncertainty_tolerance 4 + testing_rigor 4) the minimum raises 15 → 27. 17 new tests; full suite green. | **complete** |
| 10 | Implementation: episodic-tier writer — new PostToolUse hook `core/hooks/episodic_writer.py` fires on high-impact Bash pattern match, assembles a record conforming to `memory-contract-v1` (common + episodic_record schemas), appends to `~/.episteme/memory/episodic/YYYY-MM-DD.jsonl`. Reasoning-Surface snapshot attached when present in cwd; secrets redacted before write; confidence-on-provenance reflects available signal. Wired into `hooks/hooks.json` under PostToolUse/Bash, async. 19 new tests; end-to-end smoke-test record appeared at `~/.episteme/memory/episodic/2026-04-20.jsonl` with the expected shape. | **complete** |
| 11 | Implementation: semantic-tier promotion job. New `src/episteme/_memory_promote.py` + `episteme memory promote` CLI subcommand. Reads episodic tier, clusters by (domain marker, primary high-impact pattern), computes outcome distribution + disconfirmation-fire-rate per cluster, emits deterministic proposals (stable hashed ids, stable ordering by sample_size desc) into `~/.episteme/memory/reflective/semantic_proposals.jsonl`. Renders an operator-facing Markdown report. Never writes to semantic tier; promotion is gated at a future acceptance step. 19 new tests. | **complete** |
| 11.5 | Docs-only coherence pass. (Original spec archived pre-Event-54; rationale recoverable from git history.) Lands `docs/NARRATIVE.md` (triad spine + 결 grain), rewrites `docs/assets/system-overview.svg` (Figure 1) and `docs/assets/architecture_v2.svg` (Figure 2) in arxiv style with phase-12 drawn dashed / pending, adds `scripts/demo_posture.sh` (cinematic 75s differential · live-validated against the real guard), stitches `README.md` as thinking-first. No code changes. Makes phase 12 narratively legible before implementation. | **complete** |
| 12 | Implementation: profile-audit loop — compares claimed axis values against episodic evidence; flags drift for operator re-elicitation. Counters measure-as-target drift operationally, not just by doc. Unblocks meaningful interpretation of the 5 axes currently marked `inferred` in the maintainer's profile. Narrative home and SVG slot pre-drawn by phase 11.5. Shipped across 5 checkpoints (CP1 scaffolding, CP2 Axis C `fence_discipline`, CP3 Axis A `dominant_lens`, CP4 Axis D `asymmetry_posture`, CP5 Axis B `noise_signature` + dogfood). | **complete** |
| 13 | `kernel/CHANGELOG.md` 0.11.0 entry. Version reconcile across `pyproject.toml`, `plugin.json`, `marketplace.json`. | **complete** |
| 14 | `kernel/MANIFEST.sha256` regenerated (`episteme kernel update`) after all kernel edits land. Shipped at commit `a78c73e`. | **complete** |

### Open assumptions
- No-buzzword-in-body discipline survives contact with the new memory architecture doc. If a reader has to import `Tulving` or `Snowden` as prior knowledge to read the body text, the attribution-only rule failed and the body text needs another pass.
- The derived-behavior-knobs table is the right bridge between profile and hooks. Unverified until phase 9 actually wires a hook to read one of the knobs; may need to retreat to a smaller set if the wiring surface is bigger than expected.
- Per-axis `last_observed` is worth the metadata overhead vs the single `Last elicited` line. Expected yes because axes drift at different rates, but no runtime evidence yet.
- The 90-day episodic TTL with compaction is a reasonable default. Compaction rules (what the summary preserves) not yet specified in code.

---

## Closed milestones

### 0.10.0 — The Sovereign Kernel — complete

- **Stateful interception** — new `core/hooks/state_tracker.py` (PostToolUse Write/Edit/MultiEdit + Bash) persists agent-written file paths + sha256 + ts to `~/.episteme/state/session_context.json` (24h TTL, atomic temp+rename, `fcntl.flock`). `reasoning_surface_guard.py` extended with a state-store consult: literal path/basename reference → deep-scan that file; variable-indirection shape (`bash $F`, `python $F`, `./$X`, `source $X`) → deep-scan every recent tracked write. Closes the write-then-execute-across-calls bypass and the `F=run.sh; bash $F` indirection shape.
- **Heuristic friction analyzer** — new `episteme evolve friction` CLI subcommand pairs prediction↔outcome JSONL by `correlation_id`, flags `exit_code ≠ 0` against positive predictions, ranks most-violated unknowns and friction-prone ops, emits a Markdown Friction Report. Deterministic; seed for future automated CONSTITUTION.md refinement.
- **SVG architecture diagram** — `docs/assets/architecture_v2.svg` replaces the ASCII control-plane diagram in `README.md`. Cybernetic-governance aesthetic, three-layer (Agent Runtime / Episteme Control Plane / Hardware · OS), with Stateful Interceptor loop and Calibration Telemetry feed visible.
- **Gap B — `last_elicited` profile freshness.** Required `Last elicited: YYYY-MM-DD` metadata line on `operator_profile.md`; mirror field in `.generated/workstyle_profile.json`; `episteme sync` injects a visible "Stale Context Warning" block into the rendered CLAUDE.md when absent or older than 30 days. Schema doc updated.
- **Final neutrality sweep** — historical narrative in `docs/PLAN.md`, `docs/PROGRESS.md`, and `kernel/CHANGELOG.md` no longer carries literal absolute user-home strings. Public `junjslee` GitHub identity retained intentionally.
- **Version reconcile** — `pyproject.toml` 0.10.0, `.claude-plugin/plugin.json` 0.10.0, `.claude-plugin/marketplace.json` 0.10.0.
- Test suite 86 → 121 (35 new). Zero regressions.
- See `kernel/CHANGELOG.md` 0.10.0 entry and `docs/PROGRESS.md` 0.10.0 block. Architectural gaps that remain open are listed honestly in both.

### 0.9.0-entry — Calibration telemetry + visual proof + bypass hardening — complete

- **Repository neutrality scrub** — user-home paths removed from `docs/PROGRESS.md`, `docs/NEXT_STEPS.md`, `docs/assets/setup-demo.svg`; operator identifiers neutralized to `"default"` in `demos/01_attribution-audit/reasoning-surface.json`. `junjslee` GitHub URLs retained (intentional public identity).
- **Calibration telemetry (Gap A)** shipped — PreToolUse guard writes prediction records to `~/.episteme/telemetry/YYYY-MM-DD-audit.jsonl`; new PostToolUse hook `core/hooks/calibration_telemetry.py` writes matching outcome records with exit_code; correlation by `tool_use_id` or a SHA-1 fallback over `(second-bucket, cwd, cmd)`. Local-only; never transmitted.
- **Visual demo harness** — `scripts/demo_strict_mode.sh` runs hermetically in a tempdir and narrates the block→fix→pass loop. README embeds a GIF placeholder at `docs/assets/strict_mode_demo.gif`; `docs/CONTRIBUTING.md` documents the `asciinema rec` → `agg` workflow for the maintainer.
- **Bypass-vector hardening** — normalizer now maps backticks; `INDIRECTION_BASH` blocks `eval $VAR` / `eval "$VAR"`; `_match_script_execution` opens `.sh` scripts referenced via `./x.sh`, `bash x.sh`, `sh x.sh`, `source x.sh` (capped at 64 KB) and runs the same pattern set against the content. FP budget preserved — benign scripts and literal-string `eval`s pass through.
- Test coverage 17 → 35 guard/telemetry cases; full suite 86 passed (was 68), zero regressions.

### 0.8.1 — Strict-by-default enforcement — complete
- Flipped `reasoning_surface_guard.py` default from advisory to strict (blocking).
- Added semantic validator: lazy-token blocklist (`none`, `n/a`, `tbd`, `해당 없음`, `없음`, ...) + min-length thresholds (≥ 15 chars on disconfirmation and each unknown).
- Added command-text normalization to catch bypass shapes (`subprocess.run(['git','push'])`, `os.system('git push')`, `sh -c 'npm publish'`).
- `episteme inject` now writes `advisory-surface` marker only under `--no-strict`; strict is the default no-op.
- Block-mode stderr leads with `"Execution blocked by Episteme Strict Mode. Missing or invalid Reasoning Surface."`
- Test coverage expanded to 17 cases (strict defaults, lazy-token rejection, short-string rejection, 3 bypass vectors).
- See `kernel/CHANGELOG.md` 0.8.1 entry and `docs/PROGRESS.md` 0.8.1 block.

### 0.8.0 — Identity migration (cognitive-os → episteme) — complete
- Python package, runtime dir, env vars, GitHub repo, plugin/marketplace manifests, `pyproject.toml` all aligned to `episteme`.
- Dynamic Python runtime (no hard Conda dependency).
- `v0.8.0` tagged and pushed; marketplace install verified end-to-end.
- See `kernel/CHANGELOG.md` 0.8.0 entry and `docs/PROGRESS.md` 0.8.0 block.

### 0.7.0 — Real enforcement — complete
- Audit log, `episteme inject`, strict blocking.

### 0.6.0 — Epistemic control plane positioning — complete
- DbC + feedforward + OPA framing; README governance rewrite; ops docs seeded.

---

## Active milestone: 0.9.0 — Kernel-limits gap closure (entry phase shipped; remainder in flight)

### Goal
Close the cheapest gaps in `kernel/KERNEL_LIMITS.md` that turn the kernel from advisory into self-observing, and harden the hook surface so Strict Mode is not bypassable by common agent indirection patterns.

### Candidate phases (priority order)

| Phase | Scope | Gap | Status |
|-------|-------|-----|--------|
| 1 | Repository neutrality scrub — strip personal paths and operator identifiers | — | **complete** |
| 2 | Calibration telemetry — JSONL prediction + outcome pair in `~/.episteme/telemetry/` | A | **complete** |
| 3 | `scripts/demo_strict_mode.sh` + GIF placeholder + recording instructions | — | **complete** (GIF asset production pending first asciinema run) |
| 4 | Bypass-vector hardening — backtick normalization, `eval $VAR`, script-scan heuristic | — | **complete** |
| 5 | `last_elicited` timestamp field in operator profile schema + adapter prompt when stale | B | not started |
| 6 | Replace ASCII control-plane diagram in `README.md` with SVG asset | — | not started |
| 7 | `tacit-call` decision marker in Reasoning Surface schema | D | not started |
| 8 | Cynefin domain classification field in `reasoning-surface.json` | — | not started |

### Open assumptions
- The telemetry schema (`prediction` + `outcome` joined by `correlation_id`) is rich enough to answer "which disconfirmations actually fired" — unverified until a week of records exists.
- Script-scan 64 KB cap is acceptable — larger scripts scan partially. No runtime evidence yet that partial scans miss a meaningful bypass.
- `tool_use_id` is consistent across Claude Code's PreToolUse and PostToolUse payloads on the current runtime — falls back to SHA-1 bucket hash if mismatched.

---

## Deferred to later milestones

- Multi-operator mode (Gap C) — requires profile schema rework.
- Cross-runtime MCP proxy daemon (noted in 0.7.0 CHANGELOG rationale) — larger architectural bet; not scoped until calibration telemetry produces data worth proxying.
