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

### Phases (10 CPs)

| CP | Scope | Status |
|---|---|---|
| 1 | Extract `_classify_disconfirmation` from `src/episteme/_profile_audit.py` to `core/hooks/_specificity.py`. Phase 12 imports from new module; behavior unchanged. **Bundled with the Blueprint-D self-dogfood cascade sync** (see `docs/PROGRESS.md` Event 7). 304/304 tests green. | **code + cascade complete; awaiting paused-review-before-commit** |
| 2 | Scenario detector (`core/hooks/_scenario_detector.py`) + blueprint registry (`core/blueprints/`) with generic-fallback blueprint. No behavior change until CP5. | **shipped — 2026-04-21; 326/326 tests green; awaiting paused-review-before-commit** |
| 3 | Layer 2 in hot path, blueprint-aware. `reasoning_surface_guard.py` classifies against selected blueprint's fields. | **shipped + committed `101d3cd` — 2026-04-21; 340/340 tests green. 2 of 5 spec fluent-vacuous examples block at Layer 2; remaining 3 deferred to CP4/CP6 layered defense (see deferred_discovery #9).** |
| 4 | Layer 3 contextual grounding, blueprint-aware. New `core/hooks/_grounding.py`. FP-averse gating. | **shipped + committed `2558c67` — 2026-04-21; 361/361 tests green (+21 new, zero regressions). 0 of 3 remaining CP3-gap fluent-vacuous examples catch at Layer 3 — they contain no entity-shaped tokens, pass Layer 3 intentionally per compose-across-layers discipline; close at CP6 Layer 4 `verification_trace`. See `docs/PROGRESS.md` Event 11.** |
| 5 | Blueprint B (Fence Reconstruction), realized end-to-end + **first Pillar 3 synthesis output** — constraint-safety protocol emitted on successful removal. | **shipped + committed `117fa69` — 2026-04-21; 392/392 tests green (+30 new, zero regressions). YAML parser extended for list-of-dicts; compound-AND selector (command-head removal-verb ∧ constraint-path); 5 required Fence fields validated; `_classify_origin_evidence` added; per-correlation-id pending-marker + PostToolUse finalizer writes `cp5-pre-chain` protocol entries to `~/.episteme/framework/protocols.jsonl`. See `docs/PROGRESS.md` Event 12.** |
| 6 | Layer 4 `verification_trace` schema. Blueprint-shaped variants; blocking at generic high-impact (Posture A amendment); advisory-only for Axiomatic / Consequence Chain / Blueprint D stubs in RC. | **shipped — 2026-04-21; 429/429 tests green (+37 new, zero regressions). New `core/hooks/_verification_trace.py` — VerificationTrace dataclass + validate_trace + smoke_test_rollback_path. Generic blueprint promoted to `verification_trace_required: true` closing the three fluent-vacuous examples that leaked CP3/CP4 (Posture A amendment to spec § Layer 4). Fence blueprint declares `verification_trace_maps_to: rollback_path` — existing `rollback_path` wrapped as L4 command slot and smoke-tested (shlex-parse + prod-marker absence + file-extension path-existence). Three blueprint stubs shipped structure-only: `axiomatic_judgment.yaml`, `consequence_chain.yaml`, `architectural_cascade.yaml` (all with empty selector_triggers — do not fire at RC). `_blueprint_registry.py` extended with two optional scalar fields (`verification_trace_required`, `verification_trace_maps_to`); YAML parser unchanged per CP6 Deferred Discovery #17 ruling ("not needed at CP6"). See `docs/PROGRESS.md` Event 13.** |
| 7 | Pillar 2 hash chain + Pillar 3 substrate. `_chain.py` (shared) + `_pending_contracts.py` + `_framework.py` (protocols AND deferred-discovery records) + `_context_signature.py`. Phase 12 audit gains chain-verification precondition. | not started |
| 8 | Layer 8 spot-check sampling. 10% → 5% schedule; blueprint + protocol-quality verdicts; Blueprint D resolutions carry a "cascade-theater vs real sync" verdict; hash-chained queue; `episteme review` CLI. | not started |
| 9 | Pillar 3 active guidance surface. PreToolUse framework query (one advisory per op); SessionStart digest including deferred-discovery count; `episteme guide [--context] [--since] [--deferred]` CLI (minimal). | not started |
| 10 | Blueprint D (Architectural Cascade & Escalation) scaffolding. `core/blueprints/architectural_cascade.yaml`; new `core/hooks/_cascade_detector.py` (four selector triggers); structural validation of `patch_vs_refactor_evaluation` + `blast_radius_map[]` + `sync_plan[]`; every `deferred_discoveries[]` entry hash-chained into the framework at PreToolUse. Retrospective sync-plan verification lands in v1.0.1. | not started |

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
| 11.5 | Docs-only coherence pass. Specced in `docs/DESIGN_V0_11_COHERENCE_PASS.md`. Lands `docs/NARRATIVE.md` (triad spine + 결 grain), rewrites `docs/assets/system-overview.svg` (Figure 1) and `docs/assets/architecture_v2.svg` (Figure 2) in arxiv style with phase-12 drawn dashed / pending, adds `scripts/demo_posture.sh` (cinematic 75s differential · live-validated against the real guard), stitches `README.md` as thinking-first. No code changes. Makes phase 12 narratively legible before implementation. | **complete** |
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
