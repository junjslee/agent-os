# Progress

Running log of completed work. Most recent first.

---

## v1.0 RC cycle opens — 2026-04-21 — Spec drafted, reframed twice, authoritative docs aligned

Docs-only session following the v0.11.0 tag. No code yet. Three events, in order:

### Event 1 — v0.11.0 tagged and shipped

All fourteen phases of 0.11.0 closed (phases 1-11 + 11.5 coherence pass + raster follow-up + Mermaid architecture replacement + phase 12 profile-audit loop in 5 checkpoints + phase 13 CHANGELOG / version reconcile + phase 14 MANIFEST regen). Tag `v0.11.0` pushed. Commit `a78c73e` is the MANIFEST/CHANGELOG close. Test suite 202/202 passing at tag. Full detail in the 0.11.0-rc-track entry below.

### Event 2 — v1.0 RC spec drafted and approved

`docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` drafted as *v1.0 · Semantic Governance for the Reasoning Surface Guard*. Eight-layer architecture with three orthogonal pairs (L2+L3, L4+L6, L5+L7), six open questions, cost discipline (<100 ms hot-path p95), honest threat model. Maintainer approved same day. Status flipped `draft → approved`.

### Event 3 — First-pass philosophical reframe

Spec reanchored from "semantic governance / anti-vapor defense" to "structural forcing function for causal-consequence modeling — grafted onto an engine that cannot perform it natively." Two cross-cutting pillars added: **Pillar 1 · Cognitive Blueprints** (scenario-polymorphic surface schemas — Axiomatic Judgment, Fence Reconstruction, Consequence Chain, Unclassified High-Impact catchall) and **Pillar 2 · Append-Only Hash Chain** (tamper-evident episodic + pending-contracts record, SHA-256 chaining, chain-reset protocol for legitimate state loss). BYOS / skill-agnostic stance absorbed into preamble — *"the kernel intercepts state mutation regardless of what external tool, MCP server, or agent framework generated the command. Ecosystem provides the skills; kernel provides the episteme."* CP plan expanded 6 → 8 to absorb new work without breaking the one-commit-per-CP discipline. Status: `approved (reframed)`. Closed a previously-unaddressed threat class (memory-poisoning via retroactive state mutation). `docs/COGNITIVE_SYSTEM_PLAYBOOK.md` updated with BYOS paragraph + blueprint-selected-protocol insert + tamper-evident-record insert.

### Event 4 — Second-pass reframe: Protocol Synthesis & Active Guidance

Maintainer raised that the first-pass reframe addressed "LLM can't predict consequences" but not the second face of the same failure: *"When I search the internet or look at docs, how do I distinguish what is actually correct or what specifically fits MY context?"* Source A says X, Source B says Y; the agent cannot tell which fits THIS project's tooling / THIS team's constraints / THIS op-class's history because *fit* is a causal-world-model judgment. The agent defaults to a statistically-central synthesis — a Doxa that fits no context specifically. Each conflicting pair of sources contains a hidden context-dependent protocol ("in context X, do Y"); extracting it requires modeling WHY they conflict rather than averaging them.

Spec renamed to *Causal-Consequence Scaffolding & Protocol Synthesis — v1.0 RC*. Third pillar added:

- **Pillar 3 · Framework Synthesis & Active Guidance.** On every synthesis-capable blueprint firing (primarily Axiomatic Judgment, secondarily Fence Reconstruction), the kernel forces three outputs: (1) **distillation** — name why sources conflict (`conflict_cause`) + what features of the current situation select between them (`context_signature`); (2) **framework update** — commit the extracted rule (`synthesized_protocol`) to `~/.episteme/framework/protocols.jsonl`, hash-chained per Pillar 2; (3) **active guidance** — canonicalize future ops' context signatures, query the framework, surface matching protocols as stderr advisory (one per op) before blueprint enforcement runs, plus SessionStart digest + minimal `episteme guide` CLI.

Axiomatic Judgment extended with five synthesis-arm fields (`conflict_cause`, `context_signature`, `synthesized_protocol`, `framework_entry_ref`, `guidance_trigger`). Fence Reconstruction becomes the first real Pillar 3 synthesis producer in CP5 — on successful constraint-removal (rollback not triggered within window), emits a context-specific constraint-safety protocol. Guidance is advisory-only, never blocking — collapsing into enforcement would produce a feedback loop where the kernel enforces its own synthesis against the operator.

CP plan expanded 8 → 9 (CP9 = Pillar 3 active guidance surface). Hash-chain scope in RC extended to include framework protocols stream (still explicitly excludes `derived_knobs.json` and profile-axis changes — those expansions are later governance decisions). Status: `approved (reframed, second pass)`. Four new verification gates land: (a) framework holds ≥ 3 non-trivial protocols after 30-day soak; (b) ≥ 1 protocol fires as guidance on a subsequent op; (c) operator spot-check verdict recorded on that firing; (d) chain verification succeeds across all three streams (episodic, pending contracts, framework protocols). `COGNITIVE_SYSTEM_PLAYBOOK.md` §1 updated with source-chaos framing and three-axis "what Reasoning Surface is" statement; §3 extended with framework-synthesis-and-guidance paragraph.

### Event 5 — Authoritative docs aligned (superseded by Event 6's third-pass reframe)

`docs/PLAN.md`, `docs/PROGRESS.md`, `docs/NEXT_STEPS.md` updated to reflect closed 0.11.0 milestone and open v1.0 RC cycle. `NEXT_STEPS.md` resume block rewritten to point at CP1 of the 9-CP plan with full checkpoint breakdown and load-bearing spec constraints. `PLAN.md` opens a new active milestone (*v1.0.0 RC — Causal-Consequence Scaffolding & Protocol Synthesis*) with 9 CPs listed, load-bearing constraints enumerated, and open assumptions recorded; 0.11.0 moves to Closed with phases 12-14 marked complete. Event 6 supersedes the 9-CP list with the 10-CP version and promotes Blueprint D from catchall to named.

### Event 6 — Third-pass reframe: ultimate why + Blueprint D promoted + self-maintenance as fourth axis

Maintainer surfaced the true governing intent of the whole kernel, stated in own words: *"There is so much information in the world. When I search the internet or look at docs, how do I distinguish what is actually correct or what specifically fits MY context? Source A says 'do it this way', Source B says 'do it that way'. There is an underlying know-how or protocol hidden in these multiple cases. I want a system that systematically breaks this chaos down, understands WHY the sources conflict, creates a thinking framework that can continuously update itself, and then uses the insights generated from this framework to actively GUIDE me in the right direction."* The first- and second-pass reframes captured *causal-consequence modeling* and *protocol synthesis + active guidance*, but they addressed only three of four jobs the kernel must do to earn the claim of a *thinking framework*. The missing fourth job — **continuous self-maintenance** — is what happens when the agent discovers flaws, deprecations, config gaps, or core-logic drift mid-work. Without a forcing function, the agent defaults to the cheapest local patch and silently accumulates a cascade of mismatched surfaces — renamed functions with orphaned doc references, refactored schemas with unupdated CLI and visualizations, "temporary" workarounds that never get the refactor they promised.

**Changes landed in this event:**

- **Ultimate why enshrined in preamble.** Both `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § "Why this exists" and `docs/COGNITIVE_SYSTEM_PLAYBOOK.md` § 1 carry the operator's own-words statement and trace the four jobs the kernel must do to satisfy it: per-action causal decomposition, per-case protocol synthesis, proactive guidance at future decisions, continuous self-maintenance as the system edits itself.
- **Blueprint D promoted.** The prior "Blueprint D · Unclassified High-Impact (catchall)" is removed as a named blueprint and replaced by a named, load-bearing **Blueprint D · Architectural Cascade & Escalation**. Required fields: `flaw_classification` (fixed vocabulary of 7 classes + `other`), `posture_selected` (patch / refactor, with rationale), `patch_vs_refactor_evaluation` (the cognitive check — explicit statement of why the cheaper posture is or isn't warranted, with concrete blast-radius reference), `blast_radius_map[]` (enumerated surfaces — CLI / config / schemas / hooks / visualizations / docs / tests / generated artifacts / external surfaces including future marketing), `sync_plan[]` (one concrete atomic action per map entry; `not-applicable` must be stated with reason), `deferred_discoveries[]` (adjacent gaps uncovered mid-task; each entry immediately hash-chained into the framework as a `deferred_discovery` record). Selector triggers (CP10): cross-surface-ref diff without companion edits, refactor/rename/deprecate/migrate/cleanup lexicon against a ≥ 2-cross-ref file, self-escalation `flaw_classification`, generated-artifact symbol-reference check. Pillar 3 synthesis arm: on clean resolution (no orphan-reference regression), emits a context-specific cascade protocol at the system-architecture scope — *"In context X, posture P with blast-radius class B resolved without divergence because observable O."*
- **Goodhart closer preserved as a fallback, not a blueprint.** A **generic maximum-rigor fallback** (Consequence-Chain-shaped field set) applies to any high-impact op not matched by A / B / C / D. At least as strict as any single named blueprint; no synthesis arm; not counted as a blueprint.
- **CP plan 9 → 10.** CP10 = Blueprint D scaffolding + cascade detector + structural field validation + immediate hash-chained write of `deferred_discoveries[]` entries. Retrospective sync-plan completeness verification (cross-surface orphan-reference detection) lands in v1.0.1.
- **Pillar descriptions updated.** Pillar 1 now names four blueprints + fallback; Pillar 3 names three synthesis producers (A / B / D) operating at three scopes (per-decision / per-operator-history / per-system-evolution); Pillar 2's chain now binds deferred-discovery records as well as protocol entries.
- **New verification gates.** (1) *Blueprint D self-dogfood* — at least one real architectural-cascade op on the episteme repo during RC soak fires Blueprint D, produces a non-trivial `blast_radius_map[]` grounded to real surfaces, a `sync_plan[]` with concrete per-surface actions, ≥ 1 hash-chained `deferred_discoveries[]` entry, AND the resulting diff touches every surface named in the map without orphan-reference regression. (2) *Deferred-discovery flow-through* — ≥ 3 entries logged; ≥ 1 either promoted to a named phase/CP in NEXT_STEPS.md or triaged to "won't fix" with recorded rationale. A log that only grows is architectural-debt accumulation, not self-maintenance. (3) Chain verification soak now covers four streams (episodic, pending contracts, framework protocols, deferred-discovery).
- **New honest risk named.** Blueprint D introduces the **cascade-theater** risk: an agent fills `blast_radius_map[]` with `not-applicable` entries to get past the gate, or produces an honest but unbounded map that turns every small rename into an hour of form-filling. Mitigations named in spec: Layer 3 grounds every non-`not-applicable` entry to a real file path; Layer 8 samples Blueprint D resolutions at 2× base rate with an explicit "cascade-theater vs real sync" verdict; the selector fires only on the four trigger classes (not on every edit), so bounded-scope work remains fast.
- **Spec status.** `approved (reframed, third pass)` 2026-04-21. Subtitle unchanged (*Causal-Consequence Scaffolding & Protocol Synthesis — v1.0 RC*) — the self-maintenance axis is the third-pass elaboration of protocol synthesis applied at the system-architecture scope, not a rename of the spec.
- **Authoritative docs aligned.** `docs/PLAN.md` CP table 9 → 10; constraint regime + goal + load-bearing constraints + verification gates + open assumptions updated. `docs/NEXT_STEPS.md` resume block rewritten with 10-CP list, third-pass reframe narrative, four-named-blueprint constraint, and Blueprint-D-on-the-kernel dogfood gate. `docs/COGNITIVE_SYSTEM_PLAYBOOK.md` § 1 gains the ultimate-why paragraph and the self-maintenance paragraph; § 3 updates the blueprint list from three-plus-catchall to four-named-plus-fallback.

### What did NOT happen in this session

No code. No CP1 work. No test runs. The session was pure governance: tag 0.11.0, draft + approve + **thrice-reframe** the v1.0 RC spec, align the authoritative docs. CP1 is the next executable unit in a future session; per session discipline, code work begins after the authoritative docs are clean and the plan is ready to drive execution.

### What remains as honest open questions

- Whether Axiomatic Judgment's synthesis-arm fields produce operator-visible value in RC despite the blueprint's full realization being deferred to v1.0.1. If 30-day soak shows empty or useless synthesis-arm content, the design needs revision before v1.0.1.
- Whether the context-signature algorithm (regex + entity hashing) is FP-averse enough. Unverified until real synthesis traffic accumulates.
- Whether advisory-only Pillar 3 guidance is the right posture. If operator verdicts over soak consistently flag "missed the obvious guidance," revisit at v1.0.1.
- Whether Blueprint D's four selector triggers cover the cascade classes that actually occur in real episteme edits. If the self-dogfood gate shows the kernel editing itself without Blueprint D firing, the selector is undertriggering and the governance-gated selector-expansion request lands before v1.0.1.
- Whether cascade-theater is counterable by the named mitigations (Layer 3 grounding + Layer 8 verdict dimension) or needs a stronger structural check — e.g. minimum-entries threshold per flaw class, or retrospective orphan-reference scan on every RC Blueprint-D firing rather than a sample.
- Whether the kernel can edit itself honestly through Blueprint D without either (a) maintainer bypassing the gate under deadline pressure (Gate-28 failure) or (b) the blueprint slowing self-maintenance enough that the author stops using it. Unverified until RC soak.

---

## Event 7 — 2026-04-21 — CP1 code + Blueprint-D self-dogfood cascade sync

First real architectural-cascade op on the episteme repo itself, manually executed to the Blueprint-D contract before the blueprint's code machinery exists (that lands in CP10). This is the Gate-28-equivalent self-dogfood: the kernel's author edits the kernel under Blueprint D's discipline, proving the blueprint is a forcing function the maintainer can live with. If the cascade is wrong, or if any named blast-radius surface was silently skipped, the blueprint fails at the cognitive level regardless of whether CP10 eventually ships green code.

**Blueprint D surface (manually filled for this op):**

- `flaw_classification` = `doc-code-drift` across multiple kernel and docs/ surfaces. The v1.0 RC third-pass reframe updated five authoritative docs to the new architecture (ultimate why, four named blueprints, generic fallback, cascade & escalation) but left every other surface stale — naming Phase 12 as "pending," citing "six named failure modes" when nine+two were current, describing the Reasoning Surface as strictly four fields when the blueprint-polymorphic shape was the new contract, and carrying a legacy `COGNITIVE_OS_ARCHITECTURE.md` filename.
- `posture_selected` = `refactor`. Patch is not warranted because the drift is structural — every doc that describes the system's pillars, blueprints, or architecture must reflect the four-named-blueprint + generic-fallback + hash-chain + framework-memory + continuous-self-maintenance reality. Leaving any stale creates reader confusion and Goodhart-leaks where a new agent cites an outdated doc as ground truth.
- `patch_vs_refactor_evaluation`. A patch would mean updating only `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` / `PLAN.md` / `PROGRESS.md` / `NEXT_STEPS.md` / `COGNITIVE_SYSTEM_PLAYBOOK.md` and leaving cross-referenced surfaces inconsistent. That would produce exactly the failure mode Blueprint D exists to prevent — "hash-chained authority under a silently-mismatched surface set." The refactor posture forces symmetric update across the full blast radius.
- `blast_radius_map[]` (enumerated, non-`not-applicable` entries grounded to real files):
  - docs prose — NARRATIVE.md, POSTURE.md, ARCHITECTURE.md, EPISTEME_ARCHITECTURE.md (renamed)
  - kernel prose — kernel/REASONING_SURFACE.md, kernel/MEMORY_ARCHITECTURE.md, kernel/README.md, kernel/KERNEL_LIMITS.md, kernel/FAILURE_MODES.md
  - kernel generated — kernel/CHANGELOG.md (Unreleased entry opening the v1.0 RC cycle)
  - top-level surfaces — AGENTS.md, llms.txt (six→nine failure-mode references)
  - code — core/hooks/_specificity.py (new; CP1), src/episteme/_profile_audit.py (CP1 import rewire)
  - authoritative trio — docs/PLAN.md, docs/PROGRESS.md, docs/NEXT_STEPS.md (this event + CP1 tracking)
  - `not-applicable` with reason: `kernel/CONSTITUTION.md` (philosophy is unchanged by the reframe — the four principles still stand), `kernel/OPERATOR_PROFILE_SCHEMA.md` (operator profile schema unchanged; blueprint registry is a separate artifact), `kernel/SUMMARY.md` (needs a minor update in a follow-up pass — logged as deferred discovery below).
- `sync_plan[]` — one concrete edit per entry in the map above. All executed in this session; verification below.

**CP1 code delivery (bundled with the cascade):**

- New file `core/hooks/_specificity.py` — `_classify_disconfirmation` + three pattern tuples (`_ABSENCE_PATTERNS`, `_CONDITIONAL_TRIGGER_PATTERNS`, `_OBSERVABLE_PATTERNS`) + `DisconfirmationClass` Literal type moved verbatim from `src/episteme/_profile_audit.py`. Module docstring documents the CP1 rationale and the planned CP3 use by `reasoning_surface_guard.py`.
- `src/episteme/_profile_audit.py` — in-place definitions removed (~70 lines). `sys.path` prepend of `<repo>/core/hooks` at module load, followed by explicit `as X` re-export of the five names so `pa._classify_disconfirmation(...)` test access stays green. `# pyright: ignore[reportMissingImports]` on the dynamic import.
- Test verification — `pytest` (bare, no PYTHONPATH): **304 passed** (up from the 202 baseline cited in the spec; the spec count was stale — the real count at the v0.11.0 tag was already above 202 after the Phase 12 cascade tests landed). Zero regressions.

**Cascade sync delivery:**

- `docs/NARRATIVE.md` — §3/§4/§6/§7 Phase 12 "pending" → "shipped at v0.11.0." New §7.5 names the three pillars + four blueprints + Blueprint D continuous self-maintenance axis. Forward look is explicit.
- `docs/POSTURE.md` — "six named failure modes" → "nine named failure modes (+ two v1.0 RC additions)." New paragraph naming scenario-polymorphic blueprints + BYOS as constant-across-swaps.
- `kernel/REASONING_SURFACE.md` — Operational summary now names four fallback fields + scenario-polymorphic blueprints. New "Blueprint-polymorphic surface (v1.0 RC+)" section names all four blueprints with representative fields + the generic maximum-rigor fallback.
- `kernel/MEMORY_ARCHITECTURE.md` — Tier count 5 → 6 (added Framework tier with protocols + deferred-discovery log). Hash-chain integrity guarantee added. Framework tier section documents synthesis-at-PreToolUse, advisory-only guidance posture, storage path, retirement discipline.
- `kernel/README.md` — Added "The ultimate why" + "BYOS" sections. FAILURE_MODES file description updated (6 → 9 + 2 planned).
- `kernel/KERNEL_LIMITS.md` — Operational summary 8 → 11 limits. Three new sections: (9) framework-as-Doxa, (10) cascade-theater, (11) guidance-loop collapse. Each carries indicator + correct-response like the existing limits.
- `kernel/FAILURE_MODES.md` — Summary table extended with modes 10 (framework-as-Doxa) and 11 (cascade-theater) with named counter artifacts. Two new full sections after governance-layer mode 9.
- `kernel/CHANGELOG.md` — New `[Unreleased] — v1.0.0 RC cycle open` entry above the 0.11.0 entry. Names the three pillars, four blueprints, Blueprint D self-dogfood criterion, ten CPs, and the CP1 state.
- `docs/ARCHITECTURE.md` — Title "v0.12.0" → "v0.11.0 shipped · v1.0 RC in flight." Preamble scope note explicitly describes the diagram as the v0.11 shipped state with the four v1.0 RC additions (blueprint selector / cascade detector / hash chain / framework query) named in prose for now.
- `docs/COGNITIVE_OS_ARCHITECTURE.md` → `docs/EPISTEME_ARCHITECTURE.md` via `git mv` (history preserved). Content updated: Purpose paragraph now names governance kernel + BYOS. Added "The ultimate why" section. Positioning bullets updated with BYOS + framework synthesis.
- `AGENTS.md` + `llms.txt` — "six failure modes" → "nine failure modes (+ 2 v1.0 RC planned)." `llms.txt` gains a pointer to `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`.

**`deferred_discoveries[]` — adjacent gaps found during the cascade, logged for Phase 12 triage rather than fixed in this pass:**

1. **SVG assets `docs/assets/system-overview.svg` + `docs/assets/architecture_v2.svg` + `docs/assets/src/architecture_v2.{tex,dot}`** — still depict the v0.11.0 state. Phase 12 is drawn dashed/pending; no v1.0 RC nodes (blueprint selector / cascade detector / hash chain / framework query). Observable: grep shows "phase 12" + "pending" in the SVG sources. Log-only rationale: SVG regeneration is a separate visual-authoring workflow per the 0.11.0 coherence-pass discipline; bundling into this cascade would turn the refactor into a cross-surface SVG rework pass and exceed the bounded-scope contract.
2. **`scripts/demo_posture.sh` narration** — references "phase 12 pending" in the demo-narration strings. Observable: grep hit inside the shell script. Log-only rationale: narration is a shipped cinematic demo with timing locked to the SVG (currently stale); re-recording is coupled to #1. Both unlock together in a dedicated demo-refresh pass.
3. **`demos/01_attribution-audit/*`, `demos/03_differential/*`** — demo artifacts cite "six failure modes" or carry reasoning-surface JSON that reflects pre-v1.0 RC state. Observable: grep hits on `demos/**/*.{md,json}`. Log-only rationale: these are historical captures of specific sessions; rewriting them would destroy the record of what the kernel looked like at the time they were recorded. A new demo capture under the v1.0 RC blueprint shape is the right response, landed alongside CP5 (Fence Reconstruction end-to-end) or CP10 (Blueprint D first firing).
4. **`docs/CONTRIBUTING.md`, `docs/DEMOS.md`** — likely need a v1.0 RC paragraph update; not verified in this pass. Observable: both files exist and both pre-date the reframe. Log-only rationale: contributor/demo docs are not on the critical path for CP1-CP10 and would bundle unrelated editorial work into a cascade focused on the kernel-spec surfaces.
5. **`kernel/SUMMARY.md`** — the 30-line kernel distillation. May need an update to reference the blueprint registry, hash chain, and framework tier. Observable: file is the "load first" pointer in `kernel/README.md` and hasn't been touched by the reframe. Log-only rationale: the file's 30-line budget makes a surgical insert tricky without a full rebalance; logged for a dedicated pass after CP1-CP2 land so the code-level references are concrete.
6. **`docs/DESIGN_V0_11_PHASE_12.md`, `docs/DESIGN_V0_11_COHERENCE_PASS.md`** — old in-flight specs that now describe shipped work. They carry "phase 12 pending" / "v0.11 in flight" state. Log-only rationale: these are archival spec docs — their historical value is preserved by NOT rewriting them; a header note or status-line update is the right minimum intervention and can land in a single small commit later.
7. **`core/hooks/session_context.py`, `src/episteme/_memory_promote.py`, `src/episteme/cli.py`, `tests/test_profile_audit.py`** — grep-hits for "phase 12" exist in code/test. Almost certainly legitimate references to the shipped module (now that it's shipped, the references are fine — no rewrite needed). Flagged for Phase 12 audit completeness rather than as an action item.
8. **No pyright configuration for `core/hooks/` on the project path** — the `# pyright: ignore[reportMissingImports]` on the dynamic import in `_profile_audit.py` is honest but it would be cleaner to extend `pyproject.toml`'s Pyright config with `extraPaths = ["core/hooks"]` so the static analyzer can follow the import. **Partially resolved 2026-04-21 follow-up:** pytest's `pythonpath` was extended from `["src"]` to `["src", "."]` after the venv surfaced 7 `ModuleNotFoundError: No module named 'core'` collection errors that the conda env was silently forgiving. This closes the runtime half of item #8 for `pytest` callers (hook tests collect in stock venv now). The Pyright-side fix (`extraPaths = ["core/hooks"]`) still pending — the right bundle point remains CP3, when `reasoning_surface_guard.py` starts importing from `_specificity.py` and the convention-vs-import question needs resolving at the project level anyway.

Every deferred entry above would become an immediate hash-chained `deferred_discovery` framework record once CP7 + CP10 ship. For this pre-CP7 cascade, they live in this document — the same information, same provenance, same intent.

---

## Event 8 — 2026-04-21 — CP2 shipped: scenario detector + blueprint registry substrate

Substrate-only delivery per the spec's CP2 scope ("No behavior change until CP5 wires Fence Reconstruction"). Three new files + one test file; `reasoning_surface_guard.py` is untouched. Tests: **326/326 passing** (+22 on top of the 304 baseline).

**CP2 delivery:**

- **`core/blueprints/generic_fallback.yaml`** — source of truth for the historic four fields (`knowns` / `unknowns` / `assumptions` / `disconfirmation`). Shape: `name`, `description`, `version`, `required_fields[]`, `optional_fields[]`, `synthesis_arm`, `selector_triggers[]`. `synthesis_arm: false` (generic does not emit framework protocols — only named blueprints A / B / D do). `selector_triggers: []` (the generic fallback applies when NO named selector fires). `version: 1` is defensive for future blueprint-schema evolution.
- **`core/hooks/_blueprint_registry.py`** — hand-rolled YAML subset parser (zero PyYAML dependency, matching Phase 9's `_derived_knobs.py` convention) + `Blueprint` frozen dataclass + `Registry` class with lazy-load + cache + duplicate-name rejection + missing-directory tolerance. Parser covers scalars / block-folded strings (`>`) / block lists of scalars / inline empty list/dict (`[]`/`{}`) / comments / blank lines. Additional shapes (lists of dicts, nested maps) land with the blueprints that need them (CP5+). Exceptions: `BlueprintParseError` (structural), `BlueprintValidationError` (CP2-minimum contract — non-empty `name`, list-typed `required_fields` / `optional_fields` / `selector_triggers`, int-typed `version`).
- **`core/hooks/_scenario_detector.py`** — `detect_scenario(pending_op, surface_text, project_context) -> str` stub returning `"generic"` for every input. Signature is the contract CP3 commits to; docstring names where real selectors land (CP5 Fence Reconstruction, CP10 Architectural Cascade). `GENERIC_FALLBACK` module-level constant so downstream callers reference the literal without stringly-typed coupling.
- **`tests/test_scenario_detector.py`** — 22 tests (not 10 — the extra 12 cover edge cases that surfaced during writing): generic loads with exact four-field tuple in order · synthesis-arm false · selector-triggers empty · version 1 · source-path resolves · detector returns generic for empty / plausible-Fence / plausible-Cascade inputs · signature parameters stable (locks CP3's call contract) · constant matches blueprint name · unknown blueprint raises KeyError listing known names · malformed YAML raises BlueprintParseError · missing-name / non-list / duplicate-name raise BlueprintValidationError · empty + nonexistent dirs yield empty registry (supports forks without blueprints/) · cache idempotent (same dataclass instance across calls) · reload invalidates cache · folded block scalar parsed · Blueprint dataclass frozen (immutable; safe to share across hot-path calls).

**What did NOT happen:**

- `reasoning_surface_guard.py` unchanged. The hot path does not yet consult the detector or registry.
- No synthesis arm. No hash chain. No framework. Those land at CP5 / CP7 / CP9 respectively.
- No Pyright fix for `core.hooks` import resolution — still the runtime-works-but-static-analyzer-can't-follow gap tracked as deferred-discovery #8's Pyright half. Right bundle point remains CP3.

**Honest open questions carrying into CP3:**

- Whether the hand-rolled YAML parser's scope (CP2 subset) is correctly bounded. If CP5's Fence Reconstruction blueprint needs list-of-dicts for selector triggers, the parser extends there — which is fine, but the extension shouldn't retroactively break CP2's generic_fallback parsing. Guard: test coverage.
- Whether `GENERIC_FALLBACK = "generic"` is the right literal. Spec uses "generic" throughout, so this is likely stable, but renaming costs zero at CP2 and costs CP3 call-site churn after CP3 lands.

**Commit plan:** one atomic commit for CP2, message subject `feat(v1.0-rc): CP2 scenario detector + blueprint registry substrate`. Awaiting paused-review per CP discipline.

---

## 0.11.0-rc-track — 2026-04-20 — Framing shift + RC-gate fixes + Phase 12 CP1 scaffolding

One long session. Five commits. Repository's narrative posture and engineering posture realigned around the same thesis the code has always been enforcing: **the cognitive framework is the product; the file-system blocker is the uncompromising enforcer, not the pitch.** Engineering fixes close concrete v1.0.0 RC-blockers; Phase 12 foundation lands so Checkpoint 2 (first real cognitive-drift signature) can start from a scaffolded, tested base.

### Commits (in order shipped)

- **`d3cf98f` — `fix(1.0-rc): pytest config, telemetry redaction, Windows fcntl fallback`**. Three critical audit findings surfaced during a read-only audit of `evolve friction` + stateful interceptor:
  - `pyproject.toml` had no `[tool.pytest.ini_options]`; bare `pytest` on a fresh clone produced 6 collection errors (`ModuleNotFoundError: episteme`). Added `pythonpath = ["src"]` + `testpaths = ["tests"]`. Full suite now green without any PYTHONPATH manipulation.
  - `reasoning_surface_guard._write_prediction` and `calibration_telemetry` (outcome record) wrote `command_executed` verbatim to telemetry — inline secrets (`password=`, `token=`, `AKIA…`, `ghp_…`) landed on disk in plaintext. Both now pass through a `_redact` helper. **Bonus bug found during the lift:** the existing `_redact` in `episodic_writer.py` had a replacement-string evaluated at module load that produced `\\g<0>=<REDACTED>`, *appending* `=<REDACTED>` after the match instead of replacing the value — so `password=hunter2` was becoming `password=hunter2=<REDACTED>`. Fixed: capture `(key)(separator)`, replace the value with `<REDACTED>`. Verified against `password=`, `token=`, `api_key:`, `AKIA…`, `ghp_…`.
  - `state_tracker.py` had `import fcntl` at module top-level — POSIX-only, crashed on Windows first PostToolUse. Now `try/except ImportError` with a graceful no-lock fallback that matches the "exotic filesystems" path the docstring already named.

- **`b008b3e` — `docs(1.0-rc): reframe lede — thinking framework is the product, blocker is enforcement`**. Prior README lede pivoted from "installs a posture" straight to "episteme blocks (exit 2) any high-impact op", selling the project as a security tool. **Load-bearing framing correction.** Changes:
  - `README.md` — new two-paragraph lede. §1 names the cognitive framework (five-field surface → nine countered failure modes → facts/inferences/preferences separation, hypothesis→test→update, profile-audit loop). §2 introduces the blocker as *"the uncompromising enforcer of the cognitive discipline above — not a security product pretending to be a thinking framework."* "Why this architecture" reordered so cognitive claims lead; OPA/OWASP/governance falls out as consequences. "AI safety" reframed as "by construction, not bolt-on."
  - `docs/COGNITIVE_SYSTEM_PLAYBOOK.md` — added the *"What is product, what is mechanism"* paragraph to the Operating Thesis making the product/enforcer split explicit.
  - `docs/NEXT_STEPS.md` — added **Cognitive-adoption RC gates (items 21–28)** alongside the engineering gates. These verify that reasoning-quality drift is surfaced (not just outcome drift): disconfirmation actually fires, facts/inferences/preferences stay separated, hypothesis→test→update is observable, profile-audit catches *reasoning* drift, failure-mode taxonomy is load-bearing, kernel doesn't bypass kernel while working on kernel (Gate 28). Ship criterion: engineering gates + ≥ 4 of 8 cognitive gates pass; remaining named as 1.0.1.
  - `docs/NARRATIVE.md` deliberately **not touched** — already leads with *"What this kernel installs is an epistemic posture"* and situates the blocker as machine-enforceable discipline. Rewriting would have destroyed the 0.11 coherence pass's intentional work.

- **`9a7cd1b` — `fix(1.0-rc): RC-cycle items 7, 8, 11 — episode id, top-n clamp, malformed-surface signal`**. Three bounded Class A fixes from the NEXT_STEPS RC-cycle list. **Authored against an explicit Reasoning Surface** (in-session `.episteme/reasoning-surface.json`; gitignored per operator-local convention). The surface's hypothesis predicted items 9 and 10 would promote to Class B (design calls) — and they did, exactly as predicted, after `grep` of `core/schemas/evolution/evolution_episode.json` revealed `additionalProperties: false` on both the top-level and provenance sub-object (item 9 is a schema-contract-version decision); and a design question about whether CLI-side audit writes share `~/.episteme/audit.jsonl` with hook-side audit or land in a separate stream (item 10 needs maintainer input). Shipped:
  - Item 7 — `_evolve_run` episode-ID collision: appended `uuid.uuid4().hex[:4]` to `ep-YYYYMMDD-HHMMSS` for collision-free ids under rapid invocation; prefix still lexicographically sortable. No consumers of the exact old 17-char format (`grep -rn 'ep-[0-9]'` confirmed repo-wide).
  - Item 8 — `_render_friction_report` negative `--top-n`: `top_n = max(0, top_n)` at entry; argparse accepts negatives, Python slice `[:-1]` previously sliced from the tail and leaked ranked entries into a report that should have had none.
  - Item 11 — `reasoning_surface_guard._surface_status` no longer reads corrupt JSON as "missing": parse inline, distinguish `JSONDecodeError` + `OSError` + non-dict-JSON as status=`"invalid"` with detail naming the failure (including JSON line + column for parse errors). `_read_surface` left untouched for the `_write_prediction` call site.
  - Tests: 176 → 180 (+4). Uniqueness under rapid calls (10 distinct ids); negative-top-n clamp (matches top_n=0 behavior, no leakage); malformed-surface (`INVALID` + `"not valid JSON"`) distinguishable from missing (`MISSING` + `"not found"`).

- **`9c26201` — `docs(0.11-phase-12): approved design spec for profile-audit loop`**. `docs/DESIGN_V0_11_PHASE_12.md` — ~490 lines. The design for phase 12 (profile-audit loop closing the v0.11 circuit) with four countermeasures against the Goodhart threat named up front:
  - **D1 · multi-signature convergence** — each axis has ≥ 2 signatures; drift flags require ≥ 2 misaligned.
  - **D2 · retrospective-only** — signatures computed from already-written episodic records; never visible to the agent at decision-time.
  - **D3 · re-elicitation, not correction** — the loop writes a prompt for the operator; never auto-mutates `operator_profile.md`.
  - **D4 · named limit** — explicit §Known Gaming Vectors section; phase 12 is one defense-in-depth layer, not a sufficient safeguard alone.

  Four axes operationalized in full (A `dominant_lens: failure-first`, B `noise_signature: status-pressure`, C `fence_discipline: 4`, D `asymmetry_posture: loss-averse`); 11 remaining axes pattern-sketched with template references. Spec includes 6 open questions — all accepted as proposed by the maintainer. Status flipped `draft → approved` with decisions recorded inline.

- **`38374c0` — `feat(0.11-phase-12): checkpoint 1 — profile-audit scaffolding`**. End-to-end foundation. All 15 axes return `insufficient_evidence` with a reason pointing to the spec's sketch-table row — honest cold-start output until CP2+ land real signatures. Files:
  - `kernel/PHASE_12_LEXICON.md` — five default lexicons (failure_frame, success_frame, buzzword, causal_connective, rollback_adjacent), operator override path at `core/memory/global/phase_12_lexicon.md`, explicit "Goodhart limit" section naming the threat model.
  - `core/schemas/profile-audit/profile_audit_v1.json` — schema with `additionalProperties: false` throughout and `minItems`/`maxItems` = 15 on axes.
  - `src/episteme/_profile_audit.py` — library: `run_audit`, `render_text_report`, `write_audit_record` (append-only to reflective tier), `read_latest_audit`, `surface_drift_line`. Custom YAML-ish parser for the operator profile's axis claims (no `pyyaml` dep — keeps `pyproject.toml`'s `dependencies = []` invariant). Dispatch table `_AXIS_HANDLERS` is empty at CP1; checkpoints 2-5 populate it one axis at a time.
  - `src/episteme/cli.py` — `episteme profile audit [--since=30d] [--write] [--json]`. Human text provisional; `--json` is the stable machine-consumable contract.
  - `core/hooks/session_context.py` — `_profile_audit_line()` reads latest unacknowledged record; emits one line between surface status and NEXT_STEPS. Inlined per the hooks-stay-self-contained convention.
  - `tests/test_profile_audit.py` — 22 new tests (180 → 202). 7 classes cover: scaffolding empty-input path, episodic loader tolerance, profile claim parser on all shapes, lexicon loader + fingerprint determinism, append-only persistence, drift-surfacing contract, end-to-end session_context integration, text renderer.

  Dogfood verified: `episteme profile audit` against the maintainer's real profile correctly parses `planning_strictness=4` (int), `noise_signature={primary:status-pressure, secondary:false-urgency}` (dict), `dominant_lens=[failure-first, causal-chain, first-principles, …]` (list). All 15 axes `insufficient_evidence`. Lexicon fingerprint stable `60963970fc2aa64b`.

### Deep Audit Discoveries (logged from the opening read-only audit)

Recorded after-the-fact per the session's initial audit directive. All either shipped or promoted to the RC checklist:

- **`pytest` fails out of the box** — shipped fix in `d3cf98f`. Now 202/202 bare.
- **Cleartext secrets in telemetry** — shipped fix in `d3cf98f`. Bonus latent bug in existing `_redact` helper also fixed.
- **`state_tracker.py` POSIX-only `import fcntl`** — shipped fix in `d3cf98f`.
- **`evolve run` episode-ID collision within same second** — shipped fix in `9a7cd1b`.
- **`--top-n -1` silently slices from the tail** — shipped fix in `9a7cd1b`.
- **Corrupt `reasoning-surface.json` indistinguishable from missing** — shipped fix in `9a7cd1b`.
- **`evolve promote/rollback` overwrites `provenance.captured_at`** — promoted to Class B; schema-contract decision (evolution-contract-v1's `additionalProperties: false`) blocks silent fix.
- **`evolve promote --force` writes no audit trail** — promoted to Class B; design decision needed on CLI-event audit stream (shared with hook audit? separate file?).
- **`_default_evaluation_report` is a stub** — by-design per spec; flagged as 1.0 roadmap item 19.
- **Unbounded telemetry loader + extension-less file tracker noise + persistent lockfile** — discretionary polish items 16, 17, 18 in NEXT_STEPS.

### Metrics

- Tests: **176 → 202** (+26; 0 regressions).
- Commits: **5** shipped + 1 in-flight auto-checkpoint (`98e2933`).
- RC checklist: **items 2, 3, 4, 7, 8, 11** closed. Items 9, 10 promoted to Class B alongside phase 12.
- Phase 12: **CP1 of 5** shipped. Dispatch table `_AXIS_HANDLERS = {}` awaiting CP2 (axis C · fence_discipline).

### Pause point

Session ends cleanly after CP1. Next session resumes at Phase 12 Checkpoint 2 — Axis C (`fence_discipline`) — per the approved spec's depth-first sequencing (C first because single-signature flagging is allowed, then A, D, B). No blockers; foundation is tested; real signatures land one commit at a time.

---

## 0.12.0-mermaid-architecture — 2026-04-20 — Mermaid architecture diagram replaces arxiv PNG figures

`docs/ARCHITECTURE.md` created — arXiv-quality Mermaid flowchart (`graph TD`) mapping philosophical concepts to exact technical implementations. Four subgraphs: ① Agentic Mind (Intention) — Agent → Reasoning Surface → Doxa / Episteme; ② Sovereign Kernel (Interception) — `core/hooks/reasoning_surface_guard.py` stateful interceptor → Hard Block exit 2 / PASS exit 0; ③ Praxis & Reality (Execution) — tool execution → observed outcome via `core/hooks/calibration_telemetry.py`; ④ 결 · Gyeol (Cognitive Evolution) — prediction ↔ outcome joined by `correlation_id` in `~/.episteme/telemetry/YYYY-MM-DD-audit.jsonl` → `episteme evolve friction` (`src/episteme/cli.py · _evolve_friction`) → Operator Profile + `kernel/CONSTITUTION.md` → posture loop closed. ClassDefs: red (Doxa / Hard Block), green (Episteme / Praxis), blue (Gyeol), purple (Kernel), dark-grey (neutral). `README.md` Figures 1 and 2 (PNG image tags) replaced with the embedded Mermaid diagram + link to `docs/ARCHITECTURE.md`. Architecture entry added to the "Read next" table.

---

## 0.11.0-coherence-raster — 2026-04-20 — PNG rasterization of the two arxiv-style figures

Follow-up to the coherence pass. `docs/assets/system-overview.svg` and `docs/assets/architecture_v2.svg` both rasterize cleanly via `rsvg-convert -w 1600` into deterministic PNG siblings (`system-overview.png` 361 KB · `architecture_v2.png` 287 KB). `README.md` Figures 1 and 2 now reference the PNGs directly — removes any GitHub-side SVG rendering variance (font fallback, CSS class handling, `<desc>` truncation). SVG sources remain in the repo as the authoring format; PNGs are the display format. No content change; no code change; test suite untouched. Regen command: `rsvg-convert -w 1600 docs/assets/<fig>.svg -o docs/assets/<fig>.png`.

---

## 0.11.0-coherence — 2026-04-20 — visual + narrative coherence pass (docs-only)

Interstitial between phase 11 (shipped) and phase 12 (pending). Six artifacts land so that phase 12 has a narrative home and the repo's visual story catches up to the code that phases 9–11 already shipped.

- **`docs/DESIGN_V0_11_COHERENCE_PASS.md`** — spec. Eight decisions, five sequenced steps, audit punch list as Appendix A enumerating three concrete layout bugs in the prior `architecture_v2.svg` (stateful-loop arrow curving outside its layer; PASS/BLOCK arrows floating with no source node; telemetry arrow crossing node bodies) and the content drift in `system-overview.svg` (no doxa content; no v0.11 components surfaced; MEMORY_ARCHITECTURE invisible).
- **`docs/NARRATIVE.md`** — load-bearing prose spine. Seven parts. Declares the doxa / episteme / praxis triad (ontology, three strata) traversed by the grain 결 · gyeol (motion, how the posture flows). Phase 12 named throughout as in-flight, mirroring `kernel/CHANGELOG.md`'s deferred-until-shipped discipline. Kernel-limit stated honestly: *structural discipline in the hot path; semantic quality over time*.
- **`docs/assets/system-overview.svg`** (Figure 1). Rewrite in arxiv publication-figure style. Three bands (DOXA · EPISTEME · PRAXIS). Biggest omission closed: doxa band populated with all nine named failure modes and their counters. Episteme band adds MEMORY_ARCHITECTURE + components-by-role section naming phases 9/10/11/12. Praxis band holds the four canonical artifacts + four delivery adapters. 1600×1400, single accent (sync pill), off-white ground, near-black ink.
- **`docs/assets/architecture_v2.svg`** (Figure 2). Rewrite in arxiv style. Three layout bugs resolved per Appendix A. Episteme band expanded to six components across two rows (row 1: Reasoning-Surface Guard / Stateful Interceptor / Calibration Telemetry; row 2 new: Derived Knobs / Episodic Writer / Semantic Promoter). Phase 12 profile-audit loop drawn dashed with *pending* marker — when it ships, the stroke solidifies with zero structural rework. Single accent on the BLOCK arrow (the kernel's signature behavior).
- **`scripts/demo_posture.sh`** — cinematic 75 s differential. Four beats (prompt · doxa vs episteme · specificity ladder · memory loop closes). Live-validated against the real Reasoning-Surface Guard; three disconfirmations verified BLOCK / PASS / PASS. Narration per beat answers (a) what is shown, (b) why load-bearing, (c) what failure mode it counters. The PASS on the 43-char fluent-vacuous string is the demo's pedagogical climax — honest about the kernel limit instead of hiding it.
- **`README.md`** — stitched. Hero callout rewritten as *two demos, two halves of the posture*: posture-as-thinking (demo_posture.sh, cinematic) and posture-as-blocking (strict-mode gif, now supporting). `System overview` and `Control plane` section headings become `Figure 1 · Structural stratification` and `Figure 2 · Control-plane interposition`. Kernel table updated (failure-mode counts 6→9; MEMORY_ARCHITECTURE.md added). NARRATIVE.md promoted in the pointer bar.

Code unchanged. Test suite unchanged (176 passing). Zero risk to phase 11's delivery; phase 12 now has an aligned narrative home.

---

## 0.11.0 — 2026-04-20 — Kernel depth + profile v2 runtime + episodic + semantic promotion

Docs + code. Phases 1–11 complete; phases 12–14 remain (profile-audit loop, CHANGELOG, MANIFEST regen).

### Phase 11 — semantic-tier promotion

- New module `src/episteme/_memory_promote.py`. Reads episodic records from `~/.episteme/memory/episodic/*.jsonl`; clusters by `(domain_marker, primary high-impact pattern)`; computes per-cluster outcome distribution + disconfirmation-fire-rate; emits **proposals** (not promotions) into `~/.episteme/memory/reflective/semantic_proposals.jsonl`. Stability labels: `typically-succeeds` (success_rate ≥ 0.8), `typically-fails` (≤ 0.2), `mixed` otherwise. Clusters below min-size (default 3) or with zero observed exit codes are dropped.
- New CLI subcommand `episteme memory promote [--episodic-dir PATH] [--reflective-dir PATH] [--output PATH] [--min-cluster N]`. Wired into the existing `memory` subcommand group alongside `record`/`list`/`search`. Prints the report to stdout; writes file only when `--output` is given; the reflective jsonl is only created when there's at least one proposal (so "no candidates yet" never creates an empty noise file).
- Deterministic: proposal ids are `prop_<sha1(signature|sorted_evidence_refs)[:16]>`, so re-running on the same episodic input produces byte-identical ids. Proposals sort stably by `(-sample_size, action_pattern)`. Re-run verified end-to-end.
- Never touches the semantic tier. `~/.episteme/memory/semantic/` is not created by this command; proposal acceptance is a deferred phase. The design keeps the single most important discipline from MEMORY_ARCHITECTURE.md: *propose → review → accept*, never silent promotion.
- End-to-end smoke: 6 synthetic records (3 `git push` mixed, 3 `npm publish` success) → 2 proposals with correct stability labels and disconfirmation fire rates (33% and 0% respectively). Report markdown + jsonl both landed.
- Tests: `tests/test_memory_promote.py`, 19 cases. Load + cluster correctness, signature rules, proposal shape conforms to `memory-contract-v1`, determinism (same input → same ids + same order), write discipline (reflective only, never semantic), CLI-level `--output` and min-cluster gates, render of empty and populated reports.
- Test suite 157 → 176 (+19). Zero regressions.
- Interconnection: the proposal's `evidence_refs` carry episodic record ids, so phase 12 (profile audit) can trace back to source when it uses semantic-tier stability as a signal against profile axis claims.

### Phases 9–10 — profile becomes control signal, memory becomes storage

### Phases 9–10 — profile becomes control signal, memory becomes storage

- **Phase 9 — derived behavior knobs, end-to-end.** New module `core/hooks/_derived_knobs.py` carries the axis-to-knob derivation rules declared in kernel/OPERATOR_PROFILE_SCHEMA.md section 5. Adapter computes knobs from profile and atomic-writes to `~/.episteme/derived_knobs.json`. `core/hooks/reasoning_surface_guard.py` inlines a minimal reader (no sibling import; hook stays self-contained) and replaces the module-level `MIN_DISCONFIRMATION_LEN` / `MIN_UNKNOWN_LEN` constants with callable lookups against the knob file, fallback 15 on any failure. First knob wired: `disconfirmation_specificity_min` (and the companion `unknown_specificity_min`), both derived from `uncertainty_tolerance` (epistemic) + `testing_rigor` (consequential). For the maintainer's profile (uncertainty 4 / testing 4) the minimum raises 15 → 27. An 18-char disconfirmation that would have passed at default-15 now fails; a 39-char disconfirmation passes. This is the first moment the v2 profile actually modulates hook behavior, proving the bridge end-to-end before the other seven knobs follow.
- **Phase 10 — episodic-tier writer.** New PostToolUse hook `core/hooks/episodic_writer.py` assembles a record per the `memory-contract-v1` schema (common.json + episodic_record.json) and appends to `~/.episteme/memory/episodic/YYYY-MM-DD.jsonl`. First-pass trigger is the high-impact Bash pattern set only; the three other triggers declared in MEMORY_ARCHITECTURE.md (hook-blocked, Disconfirmation-fired, operator-elected) need signals this hook does not yet have. Records attach a Reasoning-Surface snapshot when the surface exists in cwd; `confidence` on provenance reflects available signal (high = surface+exit, medium = one, low = neither). Secrets are redacted before write (AWS keys, GH tokens, `password=`-shape args). Wired into `hooks/hooks.json` under PostToolUse/Bash alongside `state_tracker` and `calibration_telemetry`, all async. Correlation-id algorithm mirrors `calibration_telemetry.py` so episodic + telemetry records join.
- Test suite: 121 → 157 (**36 new**; 17 derived-knobs, 19 episodic-writer). Full suite green; zero regressions.
- End-to-end smoke: fired a synthetic `git push` payload through `episodic_writer.py`; record appeared at `~/.episteme/memory/episodic/2026-04-20.jsonl` with the expected shape. `~/.episteme/derived_knobs.json` carries the compiled knob set for the maintainer's v2 profile.

### Operator profile v2 — filled and partly elicited

- `core/memory/global/operator_profile.md` migrated to v2 schema on 2026-04-20. All 6 process axes rescored 0–3 → 0–5 with anchor-backed rationale (`elicited`). All 9 cognitive-style axes filled; 3 flipped from `inferred` to `elicited` where source documents directly support the value: `abstraction_entry: purpose-first` (cognitive_profile.md: "top-down: abstraction first, then mechanism, then iteration"), `explanation_depth: causal-chain` (cognitive_profile.md: "prefer depth and causal clarity"), `asymmetry_posture: loss-averse` (workflow_policy separates reversible vs irreversible by construction). 5 axes remain `inferred`: `dominant_lens` (ordering is judgment), `noise_signature` (operator's own susceptibility — my least-confident guess), `decision_cadence` (tempo unstated in source), `uncertainty_tolerance` (specific 0–5 value is judgment), `fence_discipline` (specific 0–5 value is judgment). Per-axis metadata (`confidence`, `last_observed`, `evidence_refs`) populated. Expertise map populated with 7 domains.

### Axis sharpening (schema self-audit on first landing)

Three of the 9 cognitive-style axes originally read like generic best-practice advice — the exact failure the schema's own rule forbids. Fixed in OPERATOR_PROFILE_SCHEMA.md:
- `abstraction_entry`: textbook `top-down/bottom-up/middle-out` → concrete entry points (`purpose-first / mechanism-first / boundary-first / analogy-first`) each with a named agent-explanation consequence.
- `decision_cadence`: reframed to `{tempo, commit_after}` so it is orthogonal to `planning_strictness` (tempo = loop frequency, not planning depth).
- `uncertainty_tolerance`: labeled explicitly epistemic (open Unknowns) vs `risk_tolerance` as consequential (act under uncertainty). The two are independent.

### Attribution surface expansion — `kernel/REFERENCES.md`
- Nine new primary sources added: Ashby (requisite variety → grounds escalate-by-default in hook layer); Gall (working-simple precedes working-complex → grounds evolution posture); Tetlock (calibration culture → grounds telemetry loop target); Laplace/Jaynes (probabilistic inference → grounds evidence-weighted plausibility update); Goodhart / Strathern (measure-as-target drift → grounds scorecard audit discipline); Klein (recognition-primed decision → grounds `tacit_call` + `expertise_map`); Chesterton (the fence → grounds Fence-Check gate); Feynman (self-deception → sharpens Principle I); Festinger (cognitive dissonance → sharpens confidence/accuracy counter).
- Four secondary sources added: Tulving / Squire (memory-tier taxonomy), Snowden (Cynefin domain marker), Wittgenstein (limits of explicit language).
- Primary-source count: 14 → 23. Operational summary at top of REFERENCES.md rewritten.

### Body-doc weaves — no buzzwords, only concepts
- `CONSTITUTION.md` — added variety-match and fence-check lenses to Principle III stack; added "a working complex system evolves from a working simple one" paragraph to Principle IV; added "not a frozen measurement of the operator" caveat to *What it is not*.
- `FAILURE_MODES.md` — new section "Governance-layer failure modes" holding three non-Kahneman modes (constraint removal w/o understanding, measure-as-target drift, controller-variety mismatch) separated from the six primary so the Kahneman taxonomy stays intact. Operational-summary table updated.
- `REASONING_SURFACE.md` — three additions: evidence-weighted update mechanic (Assumption plausibility updates; moves to Known only on decisive evidence), the `domain` marker (Clear/Complicated/Complex/Chaotic — precedes the four fields), the `tacit_call` boolean marker (closes Gap D — relaxes Knowns for judgment-driven calls without relaxing accountability).
- `KERNEL_LIMITS.md` — added limits 7 (rule-based governance against general-capability agents → escalate-by-default) and 8 (scorecard as target → per-axis audit against episodic record; drift is allowed). Operational summary updated.

### Operator profile schema v2 — `kernel/OPERATOR_PROFILE_SCHEMA.md` (rewrite)
- Two scorecard layers now: (a) process axes widened to 0–5 with anchor text per level; (b) new cognitive-style layer — nine typed axes: `dominant_lens`, `noise_signature`, `abstraction_entry`, `decision_cadence`, `explanation_depth`, `feedback_mode`, `uncertainty_tolerance` (0–5), `asymmetry_posture`, `fence_discipline` (0–5).
- Three axes sharpened post-landing to eliminate overlap with the process layer and pass the schema's own "generic best-practice = failed profile" rule: `abstraction_entry` reframed from top-down/bottom-up/middle-out (textbook, no agent-behavior consequence) to `purpose-first / mechanism-first / boundary-first / analogy-first` (names where the operator actually enters a problem, with a clear agent-explanation consequence for each); `decision_cadence` reframed to `{ tempo, commit_after }` so it is orthogonal to `planning_strictness` (tempo = loop frequency, not planning depth); `uncertainty_tolerance` clarified as *epistemic* (how long open Unknowns are tolerated) vs `risk_tolerance` as *consequential* (how willing to act under uncertainty) — the two are now explicitly independent.
- Per-axis metadata: `value`, `confidence` (elicited / inferred / default), `last_observed`, `evidence_refs[]`, optional `drift_signal` (0.0–1.0). Replaces the single `Last elicited` file-level line: staleness is now per-axis because axes drift at different rates.
- `expertise_map` field: `{ domain → { level, preferred_mode } }`. Closes the "scaffold an expert" / "go terse on a learner" default failures.
- New section: *Derived behavior knobs* — the declared set of control signals adapters compute from axes (`default_autonomy_class`, `disconfirmation_specificity_min`, `preferred_lens_order`, `noise_watch_set`, `explanation_form`, `checkpoint_frequency`, `scaffold_vs_terse`, `fence_check_strictness`). Bridges "profile is documentation" → "profile is control signal."
- New section: *Audit discipline* — the counter to measure-as-target drift. Scored axes are hypotheses about the operator, not signed contracts; periodically audited against the episodic record; divergence over N cycles flags re-elicitation, never auto-updates.

### Memory architecture — new doc `kernel/MEMORY_ARCHITECTURE.md`
- Five tiers declared with purpose / lifetime / writer / reader:
  1. **Working** — session scratchpad, compresses under context pressure; nothing persists past session end.
  2. **Episodic** — per-decision records (Reasoning Surface + action + observed outcome + Disconfirmation state); 90-day raw + compacted summary afterward. Write triggers declared: high-impact action, hook-blocked or escalated action, Disconfirmation fired (full or partial), operator-elected record.
  3. **Semantic** — cross-session patterns derived from episodic; persistent; pruned on contradicting evidence. Proposes priors to the Frame stage; never autofills the Surface.
  4. **Procedural** — operator-specific reusable action templates, distinct from universal workflow policy and project-local templates.
  5. **Reflective** — memory about memory (staleness, drift signals, elicitation queue). Derivable; materialized view, not source of truth.
- Retrieval contract: query-by-situation (Reasoning Surface shape-match), not query-by-key. Ranking: `similarity × recency_decay × outcome_weight`. No-match is a valid output; spurious priors are more costly than no priors.
- Promotion contract: episodic → semantic requires pattern recurrence + outcome stability; semantic → profile-drift proposal requires long-window conviction + divergence from claimed axis value. Both gated. Profile-drift proposals go into reflective tier for operator review at next SessionStart; the kernel never auto-merges a profile update.
- Forgetting contract: per-tier TTL + compaction rule declared. Two categories never written: secrets (detected at write, rejected) and operator-identifying paths (normalized before write).
- Write/read discipline: each workflow stage has a declared write responsibility and read set. Frame reads profile + semantic priors + recent episodic; Handoff writes the episodic record + updates authoritative docs.
- Integrity guarantees: episodic is append-only (compaction produces new records via `supersedes`/`superseded_by`); promotion is idempotent; forgetting is itself logged in reflective.

### Summary / README updates
- `kernel/SUMMARY.md` — six-modes table expanded to nine (six reasoner + three governance-layer); new Operator-profile-v2 paragraph; new Memory-architecture paragraph; scope boundary updated with limits 7 and 8; *next load* list adds `MEMORY_ARCHITECTURE.md`.
- `kernel/README.md` — file list adds `MEMORY_ARCHITECTURE.md` with a one-line description; `OPERATOR_PROFILE_SCHEMA.md` description updated to reflect v2 structure.

### What did *not* land in this pass (explicit)
- **Phase 12 remains:** profile-audit loop that compares claimed scored axes against episodic + semantic evidence and flags drift for re-elicitation. Phases 9–11 shipped three bridges (profile → hook, decision → episodic record, episodic patterns → semantic proposals); phase 12 is the last bridge, closing the calibration loop by letting observed evidence propose profile updates.
- **Proposal acceptance step is deferred.** Phase 11 writes proposals to the reflective tier but does not (yet) provide an `episteme memory accept <proposal-id>` affordance that promotes a reviewed proposal to the semantic tier. That step is scoped to 0.11.1 or 0.12, pending evidence from real usage about whether bulk-review or per-proposal-review is the right UX.
- **Seven derived knobs still unwired:** phase 9 shipped one end-to-end (`disconfirmation_specificity_min` + its companion `unknown_specificity_min`). The other six knobs declared in OPERATOR_PROFILE_SCHEMA.md section 5 (`default_autonomy_class`, `preferred_lens_order`, `noise_watch_set`, `explanation_form`, `checkpoint_frequency`, `scaffold_vs_terse`, `fence_check_strictness`) are computed and written to `~/.episteme/derived_knobs.json` but no hook reads them yet. Each is a one-file wiring pattern-match on phase 9.
- **Three episodic-tier triggers still deferred:** phase 10 fires only on high-impact Bash pattern match (trigger #1 of the four declared in MEMORY_ARCHITECTURE.md). Hook-blocked actions (trigger #2) need PreToolUse-side cooperation; Disconfirmation-fired (trigger #3) needs signal the writer doesn't see; operator-elected (trigger #4) needs UI affordance.
- `kernel/MANIFEST.sha256` is stale — regenerated after phase 14. `episteme doctor` will emit drift warnings until then.
- `kernel/CHANGELOG.md` 0.11.0 entry deferred until phases 11–12 land so the changelog reflects a complete loop. Current `CHANGELOG.md` still reads 0.10.0.
- Version strings in `pyproject.toml` / `plugin.json` / `marketplace.json` unchanged at 0.10.0 — bump pinned to 0.11.0 tag readiness (after phases 11–14).
- Adoption-path split (move author's profile to `examples/` + ship schema stubs + interactive `episteme init`) is explicitly a **0.12.0** scope, not 0.11. Rationale in NEXT_STEPS.md.

### Residual architectural gaps — still honest
1. **Intra-call indirection** — unchanged from 0.10.0. Still needs a cross-runtime proxy daemon.
2. **Dynamic shell assembly** (`A=git; B=push; $A $B`) — unchanged.
3. **Heredocs with variable terminators** — unchanged.
4. **Scripts > scan cap** — unchanged.
5. **Governance-layer failure mode 9 (controller-variety mismatch)** is now named and documented; the *enforcement* (escalate-by-default for out-of-coverage action classes) is not built. Presently no-op — the kernel admits the gap and does not silently paper over it.

---

## 0.10.0 — 2026-04-20 — The Sovereign Kernel: stateful interception + heuristic friction analyzer + profile freshness gate

Four atomic commits, 35 new tests, full suite 121 passing, zero regressions. High-level framing: 0.9.0-entry proved telemetry could be paired locally; 0.10.0 carries that same file-on-disk discipline across the execution boundary between Write and Bash — the kernel now remembers what the agent just wrote.

### Stateful interception (Phase 1)
- New `core/hooks/state_tracker.py` — PostToolUse hook on Write/Edit/MultiEdit + Bash. Persists `{path → {sha256, ts, tool, source}}` to `~/.episteme/state/session_context.json`. 24 h rolling TTL, atomic `temp+os.replace`, `fcntl.flock` on a sibling lockfile.
- Tracked inputs: `.sh`, `.bash`, `.zsh`, `.ksh`, `.py`, `.pyw`, `.js`, `.mjs`, `.cjs`, `.ts`, `.rb`, `.pl`, `.php`, plus extension-less files (frequently shell scripts). Bash redirect/tee targets (`>`, `>>`, `| tee [-a]`) also captured.
- `core/hooks/reasoning_surface_guard.py` extended with `_match_agent_written_files`: two match modes — (1) literal file name or abs path in command → scan that file; (2) variable-indirection shape against any recent tracked write → scan every recent entry.
- `hooks/hooks.json` — state_tracker wired to both PostToolUse matchers (Write/Edit/MultiEdit and Bash), async.
- Tests (`tests/test_stateful_interception.py`, 12 cases): tracker records `.sh`/`.py`/`.js`/extension-less writes; skips `.md`; records Bash redirects and `tee`; purges stale entries; deep-scans `run.py` on `python run.py`; catches `bash $F` against recent write; innocuous agent-written files pass; empty state store is a no-op.

### SVG architecture overhaul (Phase 2)
- `docs/assets/architecture_v2.svg` — 1200×780 schematic, three layers (Agent Runtime / Episteme Control Plane / Hardware · OS). Dedicated nodes for Reasoning-Surface Guard, Stateful Interceptor (with the cross-call memory loop), and Calibration Telemetry (with the feedback arrow to the guard). Cybernetic aesthetic — near-black background, cyan/amber/emerald accents, mono typography.
- `README.md` — ASCII box-drawing diagram under "System overview" removed; SVG embedded with a short narrative on PASS / BLOCK, stateful loop, and calibration feed.

### Heuristic friction analyzer (Phase 3)
- New CLI subcommand `episteme evolve friction [--telemetry-dir PATH] [--output PATH] [--top N]`. Scans `~/.episteme/telemetry/*-audit.jsonl`, pairs prediction↔outcome by `correlation_id`, flags `exit_code ≠ 0` against *positive* predictions (predictions with empty envelopes are skipped — not a calibration signal), and emits a Markdown Friction Report ranking most-violated unknowns, friction-prone ops, and recent events.
- Empty telemetry → graceful "No friction detected yet" message. Malformed lines are skipped silently.
- Tests (`tests/test_evolve_friction.py`, 7 cases): empty dir, unknowns ranked by frequency, empty envelope skipped, missing outcome ignored, malformed line survived, `--output` writes file, `--top N` truncates.

### Gap B — `last_elicited` + stale warning (Phase 4a)
- `core/memory/global/operator_profile.md` — added `Last elicited: 2026-04-13` metadata line.
- `_compile_operator_profile` in `src/episteme/cli.py` — emits the line on every profile regenerate.
- `_write_workstyle_artifacts` — mirrors `last_elicited` into both generated JSON artifacts.
- New helpers `_read_last_elicited`, `_profile_staleness`, `_render_stale_profile_warning` (kernel const `PROFILE_STALE_DAYS = 30`).
- `src/episteme/adapters/claude.py` — `render_user_claude_md()` now checks staleness and injects a visible "Stale Context Warning" block above the memory imports when absent or older than 30 days.
- `kernel/OPERATOR_PROFILE_SCHEMA.md` — field documented as required.
- Tests (`tests/test_last_elicited.py`, 16 cases): parser accepts `_italic_`, `bullet`, plain forms; rejects malformed dates; staleness classification (missing / unknown / fresh / stale); warning block content and suppression.

### Final neutrality sweep (Phase 4b)
- `docs/PLAN.md:18`, `docs/PROGRESS.md:10-11` — literal absolute-user-home strings in *descriptions of the prior scrub* replaced with generic `~/...` language. Public `junjslee` GitHub identity retained intentionally (open-source attribution).
- `grep -r /Users/junlee episteme/` now returns zero matches.

### Version bumps + changelog
- `pyproject.toml` 0.8.0 → 0.10.0.
- `.claude-plugin/plugin.json` 0.8.0 → 0.10.0.
- `.claude-plugin/marketplace.json` plugin 0.8.0 → 0.10.0.
- `kernel/CHANGELOG.md` — new 0.10.0 entry + retroactive 0.9.0-entry entry to bring the audit trail in line (the 0.9.0 work had landed without a kernel-changelog bump).

### Residual architectural gaps — honest
1. **Intra-call indirection.** A single Bash call that both writes and executes (`echo "git push" > s.sh && bash s.sh` as *one* tool-use) is caught today only by the existing in-command text scanner. State tracking adds no new coverage because the PostToolUse recorder fires *after* the call. The true fix needs a cross-runtime proxy daemon that can pause between the write and the exec — the 0.11+ Sovereign Kernel. Naming v0.10 "The Sovereign Kernel" is directional, not complete.
2. **Dynamic shell assembly.** `A=git; B=push; $A $B` — unchanged from 0.8.1.
3. **Heredocs with variable terminators.** Redirect parser is regex-based; `cat <<"$EOF" > f` is missed.
4. **Scripts > 256 KB (hash) / > 64 KB (scan).** Unchanged caps.

### Test count
- 86 → **121** passing, 8 subtests. 0 regressions.

---

## 0.9.0-entry — 2026-04-20 — Privacy scrub + calibration telemetry + visual demo + bypass hardening

### Repository neutrality (Phase 1)
- Replaced absolute user-home paths with `~/...` or placeholder equivalents in `docs/PROGRESS.md`, `docs/NEXT_STEPS.md`, `docs/assets/setup-demo.svg`.
- Neutralized operator identifier to `"operator": "default"` in `demos/01_attribution-audit/reasoning-surface.json`.
- `junjslee` GitHub references retained — public identity for the open-source repo.
- `.gitignore` confirmed clean: `.episteme/`, `core/memory/global/*.md` (personal), secrets, and generated profile artifacts all covered. New telemetry writes to `~/.episteme/telemetry/` (outside repo), no gitignore change needed.

### Calibration telemetry (Phase 2 — Gap A closure)
- `core/hooks/reasoning_surface_guard.py` — on allowed Bash (`status == "ok"`), writes a `prediction` record to `~/.episteme/telemetry/YYYY-MM-DD-audit.jsonl` with `correlation_id`, `timestamp`, `command_executed`, `epistemic_prediction` (core_question + disconfirmation + unknowns + hypothesis), `exit_code: null`.
- `core/hooks/calibration_telemetry.py` — new PostToolUse hook; writes the matching `outcome` record with observed `exit_code` and `status`. Correlates via `tool_use_id` first, SHA-1 `(ts-second, cwd, cmd)` fallback when absent.
- `hooks/hooks.json` — new PostToolUse Bash matcher wires `calibration_telemetry.py` (async).
- Telemetry is operator-local, append-only JSONL, never transmitted.

### Visual demo (Phase 3)
- `scripts/demo_strict_mode.sh` — hermetic three-act script: (1) lazy agent writes `disconfirmation: "None"`, (2) `git push` attempt blocked with exit 2 + stderr shown, (3) valid surface rewritten, retry passes. Narrated via `sleep` for asciinema cadence (overridable with `DEMO_PAUSE`).
- `docs/CONTRIBUTING.md` — recording workflow documented (`brew install asciinema agg`, `asciinema rec -c ./scripts/demo_strict_mode.sh`, `agg` to render GIF, size/cadence targets).
- `README.md` — placeholder `![Episteme Strict Mode Block](docs/assets/strict_mode_demo.gif)` embedded above the "I want to…" table. GIF asset itself produced in a separate maintainer pass.

### Bypass-vector hardening (Phase 4 — best-effort)
- `_NORMALIZE_SEPARATORS` now includes backticks — catches `` `git push` `` command substitution.
- `INDIRECTION_BASH` list added; blocks `eval $VAR` / `eval "$VAR"`. Literal-string `eval "echo hi"` still passes (no `$` trigger).
- `_match_script_execution` — resolves scripts referenced by `./x.sh`, `bash x.sh`, `sh x.sh`, `zsh x.sh`, `source x.sh`, `. x.sh`; reads up to 64 KB; scans content with the same pattern set as inline commands. Missing / unreadable scripts pass through (FP-averse).
- Label format: `"<inner label> via <script path>"` — e.g., `"git push via deploy.sh"` — so the block message carries the provenance.

### Test coverage
- `tests/test_reasoning_surface_guard.py` — +10 cases: backtick substitution, eval-of-variable (two shapes), eval-of-literal (pass), script-scan blocks (bash/`.sh`, `./script.sh`, `source`), benign-script pass-through, missing-script pass-through, allowed-Bash telemetry write, blocked-Bash telemetry suppression.
- `tests/test_calibration_telemetry.py` — new file, 7 cases: non-Bash ignored, success outcome recorded, failure outcome recorded, missing exit_code → null, `returncode` fallback honored, empty command skipped, malformed payload never raises.
- Full suite: **86 passed** (was 68), 8 subtests passed, 0 regressions.

### Residual gaps (deferred, logged to NEXT_STEPS.md)
- **Write-then-execute across two tool calls** remains uncatchable by a stateless hook. Candidate for cross-runtime MCP proxy daemon (0.10+).
- **Dynamic shell assembly** (`A=git; B=push; $A $B`) still evades detection. Would require a lightweight shell parser. Deferred pending cost/benefit evidence.
- **Strict Mode demo GIF** — the asset file itself is one `asciinema rec` away; README placeholder is in place.

---

## 0.8.1 — 2026-04-20 — Strict-by-default enforcement + semantic validator + bypass-resistant matching

### Hook behavior changes (`core/hooks/reasoning_surface_guard.py`)
- **Default inverted**: missing / stale / incomplete / lazy Reasoning Surface now exits 2 and blocks the tool call. Previously advisory; hard-block required `.episteme/strict-surface`.
- **Opt-out mechanism**: per-project advisory mode via `.episteme/advisory-surface` marker. Legacy `.episteme/strict-surface` is now a no-op (strict is default).
- **Semantic validator added** to `_surface_missing_fields`:
  - Min lengths: `MIN_DISCONFIRMATION_LEN = 15`, `MIN_UNKNOWN_LEN = 15`
  - Lazy-token blocklist: `none`, `null`, `nil`, `nothing`, `undefined`, `n/a`, `na`, `not applicable`, `tbd`, `todo`, `unknown`, `idk`, `해당 없음`, `해당없음`, `없음`, `모름`, `해당 사항 없음`, `-`, `--`, `---`, `—`, `...`, `?`, `pending`, `later`, `maybe`
  - Case-insensitive + whitespace-collapsed + trailing-punctuation-trimmed matching
- **Bypass resistance** via `_normalize_command`: `[,'"\[\]\(\)\{\}]` → space before regex match. Caught in tests: `subprocess.run(['git','push'])`, `os.system('git push')`, `sh -c 'npm publish'`.
- **Block message upgraded**: stderr leads with `"Execution blocked by Episteme Strict Mode. Missing or invalid Reasoning Surface."` + concrete validator reasons + advisory-mode opt-out pointer.
- **Audit entry** `mode` field replaces the old `strict` bool.

### CLI (`src/episteme/cli.py`)
- `_inject` rewritten: strict (default) creates no marker and removes any pre-existing `advisory-surface`; `--no-strict` writes `.episteme/advisory-surface` explicitly.
- Template unknowns placeholder updated to reflect the ≥ 15 char rule.
- Post-inject hint text lists lazy-token rejection explicitly.

### Tests (`tests/test_reasoning_surface_guard.py`)
- Rewritten from 9 advisory-flavored cases → 17 cases covering:
  - Strict-by-default on every failure mode (missing / stale / incomplete / lockfile)
  - Advisory-marker downgrade path
  - Legacy `strict-surface` marker no-op behavior
  - Lazy-token rejection: 8 subtest values (`none`, `N/A`, `TBD`, `해당 없음`, `없음`, `null`, `-`, `nothing`)
  - Short-string rejection (disconfirmation and unknowns)
  - Bypass vectors: subprocess list form, `os.system`, `sh -c` wrapping

### Docs
- `kernel/CHANGELOG.md` — 0.8.1 entry added
- `kernel/HOOKS_MAP.md` — enforcement row + state-file description rewritten to match new default
- `README.md` — lede paragraph rewritten: no more "advisory by default" hedge; now explicitly states block-by-default, the validator contract, and the advisory opt-out pointer
- `docs/PLAN.md`, `docs/NEXT_STEPS.md` — strict-by-default and validator items moved to Closed

### Verification
- `PYTHONPATH=. pytest tests/ -v` → **68 passed**, 8 subtests passed (17 in the guard suite, 51 pre-existing elsewhere — zero regressions)
- Hook tested end-to-end via the suite: block exit code 2, advisory-mode exit 0, normalized bypass shapes caught, lazy tokens rejected

### Architectural gaps surfaced (not fixed, logged to `NEXT_STEPS.md`)
- **Shell script files calling high-impact ops** are not caught (e.g., `./deploy.sh` that internally runs `git push`). Intercepting requires script-content reading — out of scope for this patch.
- **Write-then-execute patterns** (write a script to disk, then run it) are not caught without a stateful hook. Requires cross-call state, which is out of scope.
- **Bash variable indirection** (`CMD="git push" && $CMD`) is not caught; normalization handles quote/bracket separators but not variable substitution.

---

## 0.8.0 — 2026-04-19 — Core migration: cognitive-os → episteme

### Version alignment (0.8.0 follow-on)
- `pyproject.toml` version: `0.2.0` → `0.8.0` (was stale across 0.6.0/0.7.0/0.8.0 cycles)
- `.claude-plugin/plugin.json` version: `0.6.0` → `0.8.0`
- `.claude-plugin/marketplace.json` plugin version: `0.6.0` → `0.8.0`
- `pip install -e .` re-run so the registered `episteme` console script reports 0.8.0
- `git tag v0.8.0 && git push --tags` — migration tagged and pushed

### Python package
- `git mv src/cognitive_os → src/episteme` (history preserved)
- All internal imports updated: `from cognitive_os` → `from episteme`
- `pyproject.toml`: `name`, `description`, `[project.scripts]` entry (`episteme = "episteme.cli:main"`)
- Env vars: `COGNITIVE_OS_CONDA_ROOT` → `EPISTEME_CONDA_ROOT` (+ `_LEGACY` variant)

### Plugin & tooling
- `.claude-plugin/marketplace.json` + `plugin.json` display names updated; `source.url` and `homepage` retained (GitHub repo path unchanged)
- `.github/` issue templates, PR template, CI workflow updated
- `core/adapters/*.json`, `core/harnesses/*.json` string refs updated
- `core/hooks/*.py` log/message strings updated
- `kernel/MANIFEST.sha256` regenerated against new content
- `.git/hooks/pre-commit` updated (imports `episteme.cli`, reads `EPISTEME_CONDA_ROOT` with `COGNITIVE_OS_CONDA_ROOT` fallback)

### Documentation
- README, AGENTS, INSTALL, all `docs/*` and `kernel/*` narrative + CLI examples updated
- Runtime directory convention: `.cognitive-os/` → `.episteme/`
- Schema identifier: `cognitive-os/reasoning-surface@1` → `episteme/reasoning-surface@1`

### Templates & labs
- Only CLI command literals updated; epistemic kernel rules, schemas, and structural logic untouched

### Verification
- `PYTHONPATH=src:. pytest -q` → 60 passed
- `py_compile` across `src/episteme/` and `core/hooks/` → clean
- Pre-commit validate hook → all kernel, agents, skills pass
- `pip install -e .` metadata resolves: `episteme = "episteme.cli:main"`

### Environment completion (completed in-session)
- GitHub repo renamed via `gh repo rename` → `github.com/junjslee/episteme` (old URL 301-redirects)
- Local `origin` remote updated; all in-repo URLs now point at the new canonical URL
- Physical repo directory renamed `~/cognitive-os` → `~/episteme`
- Pip: `pip uninstall cognitive-os` → `pip install -e .` (registers `episteme` console script)
- `~/.claude/settings.json` hook command paths rewritten to `~/episteme/core/hooks/*`
- `~/.zshrc` aliases and hint function renamed (`ainit`, `awt`, `cci`, `aci`, `adoctor`, `aos`)
- `episteme sync` regenerated `~/.claude/CLAUDE.md` with new `@~/episteme/...` includes

### Dynamic Python runtime (0.8.0 follow-on)
- `CONDA_ROOT` hardcoded to `~/miniconda3` → `PYTHON_PREFIX` derived from `sys.prefix`
- New env vars: `EPISTEME_PYTHON_PREFIX`, `EPISTEME_PYTHON`, `EPISTEME_REQUIRE_CONDA`
- Legacy `EPISTEME_CONDA_ROOT` / `COGNITIVE_OS_CONDA_ROOT` still honored as fallbacks
- `episteme doctor` skips conda checks on non-conda runtimes unless `EPISTEME_REQUIRE_CONDA=1`

### Temporary compatibility shim
- Symlink `~/cognitive-os → ~/episteme` created to keep the current shell session's cwd valid. Remove with `rm ~/cognitive-os` after restarting any shells/editors that had the old path cached.

---

## 0.7.0 — 2026-04-19

### Real enforcement pass
- `core/hooks/reasoning_surface_guard.py` — added `_write_audit()` writing structured entries to `~/.episteme/audit.jsonl` on every check (passed / advisory / blocked)
- `src/episteme/cli.py` — added `_inject()`, `_surface_log()`, parser registration, and dispatch for `inject` and `log` commands
- `.claude-plugin/plugin.json` — version bumped to 0.6.0
- `kernel/CHANGELOG.md` — 0.7.0 entry added
- Verified: `episteme inject /tmp` creates strict-surface + template; hook fires real exit-2 block; `episteme log` shows timestamped audit entries

## 0.6.0 — 2026-04-19

### Gap closure (second pass)
- `kernel/CONSTITUTION.md` — added DbC contract paragraph to Principle I; added feedforward control paragraph to Principle IV; added feedforward + DbC bullets to "What this generates"
- `kernel/FAILURE_MODES.md` — added feedforward framing to intro; renamed review checklist to "pre-execution checklist" to make the feedforward intent explicit
- `.github/ISSUE_TEMPLATE/bug.yml` — added "Kernel alignment" field mapping bugs to failure modes and kernel layers
- `.github/PULL_REQUEST_TEMPLATE.md` — added "Kernel impact" checklist block
- `README.md` — replaced TODO comment with ASCII control-plane architecture diagram
- `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/NEXT_STEPS.md` — created (ops docs were absent; hook advisory fired on every kernel edit)

### Initial pass
- `.claude-plugin/marketplace.json` — fixed `source: "."` → `"https://github.com/junjslee/episteme"` (schema fix; unverified against live validator)
- `src/episteme/viewer/index.html` — removed (deprecated UI artifact)
- `.github/ISSUE_TEMPLATE/feature.yml` — added "Epistemic alignment" field; improved acceptance criteria template
- `README.md` — added governance/control-plane opening paragraph; feedforward + DbC + OPA framing in "Why this architecture"; "Zero-trust execution" section with OWASP counter-mapping table; "Human prompt debugging" section; interoperability statement; ASCII control-plane diagram
- `kernel/KERNEL_LIMITS.md` — added Cynefin problem-domain classification table
- `kernel/CHANGELOG.md` — added [0.6.0] entry
