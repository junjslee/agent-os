# Next Steps

Exact next actions, in priority order. Update this file at every handoff.

---

## Resume here — v1.0.0 RC · Causal-Consequence Scaffolding, Protocol Synthesis & Continuous Self-Maintenance (2026-04-21)

**State.** v0.11.0 has been tagged and shipped. The v1.0 RC cycle is open. The approved spec is `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` — titled *Design — Causal-Consequence Scaffolding & Protocol Synthesis — v1.0 RC*, status `approved (reframed, third pass)`. Three successive reframes on 2026-04-21 re-anchored the spec:

- **First pass** — from "semantic governance / anti-vapor defense" to "structural forcing function for causal-consequence modeling." Added Pillar 1 (Cognitive Blueprints) + Pillar 2 (Append-Only Hash Chain); absorbed BYOS.
- **Second pass** — added Pillar 3 (Framework Synthesis & Active Guidance); renamed subtitle to *Causal-Consequence Scaffolding & Protocol Synthesis*; CP plan 8 → 9.
- **Third pass** — enshrined the **ultimate why** in the preamble (information overload → context-fit protocol extraction → living thinking framework → active guidance → continuous self-maintenance). Promoted the prior "Blueprint D · Unclassified High-Impact (catchall)" to a load-bearing **Blueprint D · Architectural Cascade & Escalation** (patch-vs-refactor evaluation, symmetric cascade synchronization, continuous digging & logging). Goodhart closer for blueprint-absence preserved as a **generic maximum-rigor fallback** (Consequence-Chain-shaped), not a blueprint. CP plan 9 → 10 (CP10 = Blueprint D scaffolding + cascade detector + deferred-discovery hash-chained write).

**Next action (fresh session):** proceed to **CP9 — Pillar 3 active guidance surface**. PreToolUse framework query after scenario detection, before blueprint enforcement — one stderr advisory per op surfacing the highest-overlap matching protocol from CP7's `protocols.jsonl`. Uses CP7's `_context_signature.field_overlap` to rank candidates; threshold tuned against CP8's accumulated queue once soak volume exists. SessionStart digest (existing) gains protocol-synthesis count + pending deferred-discovery count (CP10). New `episteme guide [--context <keyword>] [--since <date>] [--deferred]` CLI — minimal read-path at RC; authoring / revision path lands v1.0.1. Advisory-only posture, never blocking — collapsing Pillar 3 into enforcement would feedback-loop the kernel's own synthesis against the operator. CP8 has shipped — 502/502 tests passing, zero regressions; `_spot_check.py` substrate + PostToolUse sampling (max-not-sum multipliers) + 7-day skip TTL + `episteme review` CLI + SessionStart pending banner + Phase 12 chain_integrity extension; see `docs/PROGRESS.md` Event 15. Recent post-rebase commit SHAs: CP3 `101d3cd`, README GTM rewrite `23abc0a`, Event 10 doc-sync `636ad53`, CP4 `2558c67`, Event 11 doc-sync `b9bb1ee`, CP5 `117fa69`, CP6 `fb09b0a`, CP7 `086c10a`; CP8 pending commit this session.

**Tone-discipline boundary (codified 2026-04-21 at Event 10):** Plain-English / newcomer-friendly framing is a `README.md` + user-facing marketing discipline only. All files in `kernel/`, all files in `docs/DESIGN_*.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/NEXT_STEPS.md`, `docs/COGNITIVE_SYSTEM_PLAYBOOK.md`, and `AGENTS.md` remain technical, precise, and rigorous by design — the technical vocabulary is load-bearing for controlling the LLM's posture and cannot be simplified inward without degrading the control signal. README cross-links into the technical surfaces; the technical surfaces do not bend inward to meet the README.

**CP4 bundle (committed `2558c67`):**

- `core/hooks/_grounding.py` (new, ~240 LOC) — regex entity extractor (snake_case / SCREAMING_CASE / path+ext / hex SHA with mandatory digit-AND-letter), project-grep grounding via `git ls-files` with `os.walk` fallback, in-process warm cache keyed on `(cwd, newest-tracked-mtime)`, FP-averse gate (reject only when grounded ≥ 2 AND not_found/named > 0.5), graceful degrade on IO exceptions.
- `core/hooks/reasoning_surface_guard.py` — absolute import of `_grounding` via the same sys.path pattern CP3 used for `_specificity` / `_scenario_detector`; `main()` wiring after Layer 2 (runs only when status still `ok` after Layer 2; "reject" downgrades to `incomplete`, "advisory" emits stderr and continues).
- `tests/test_layer3_grounding_hot_path.py` (new) — 21 tests across 7 classes: entity extractor FP-aversion (6), gate logic pure function (4), grounding against a tmp-project fixture (4), hot-path integration through `guard.main()` (3), honest Layer-3 limit on pure-English spec fluent-vacuous examples (2), graceful degrade (1), latency bounded (1).
- Tests: **361/361 passing** (340 baseline + 21 new). Zero regressions. No fixture migrations required — existing 340 tests' disconfirmation / unknowns strings contain no entity-shaped tokens the narrow extractor captures.
- **Hot-path behavior change:** surfaces that name entity-shaped tokens (snake_case / SCREAMING_CASE / path+ext / hex SHA) which do not grep to the project tree are now rejected when grounded ≥ 2 AND not_found/named > 0.5. Pure-English fluent prose with no extractable entities honestly passes Layer 3 — this is the compose-across-layers discipline per spec § Layer 2 Composition cost; those surfaces are closed at CP6 Layer 4 `verification_trace`, not CP4.
- **Honest CP4 limit (tested explicitly, not latent):** the three spec fluent-vacuous examples that CP3 could not catch (*"the migration may produce unexpected behavior..."*, *"if the build process exhibits anomalous behavior..."*, *"if results diverge from expectations..."*) contain no entity-shaped tokens. Layer 3 passes them intentionally. They close at CP6 Layer 4.

**CP3 bundle (committed `101d3cd`):**

- Layer 2 classifier in the hot path, blueprint-aware. 2 fixture migrations (sharpened with observables). 14 new tests. Tests: 340/340 passing at commit. Narrative: `docs/PROGRESS.md` Event 9. Caught 2 of 5 spec fluent-vacuous examples at Layer 2 alone; remaining 3 closed at CP4 + CP6 combined.

**CP2 bundle (committed `6ceaa44`):**

- Scenario detector + blueprint registry substrate + generic_fallback.yaml + 22 tests. Hot path untouched at CP2.

**CP1 bundle (committed on `f5f8d0f` / `3d4b20a` / `ce0f4e3`):**

- Code extraction + Blueprint-D self-dogfood cascade sync across 13 surfaces. Narrative preserved in annotated tag `v1.0-rc-cp1` (`git show v1.0-rc-cp1`).
- Follow-up fix: `2a2ed68` — pytest pythonpath closes runtime half of deferred-discovery #8.

**The ten v1.0 RC checkpoints:**

1. **CP1 — extract `_specificity.py`.** Move `_classify_disconfirmation` from `src/episteme/_profile_audit.py` to `core/hooks/_specificity.py`. Phase 12 imports from the new module; behavior unchanged. Tests stay green.
2. **CP2 — scenario detector + blueprint registry.** New `core/hooks/_scenario_detector.py`; new `core/blueprints/` directory with generic-fallback blueprint + registry loader. No behavior change until CP5 wires Fence Reconstruction.
3. **CP3 — Layer 2 in the hot path, blueprint-aware.** `reasoning_surface_guard.py` calls `_classify_disconfirmation` against the selected blueprint's fields (generic for now). Rejects on `tautological`/`unknown`; advisory on `absence`.
4. **CP4 — Layer 3 contextual grounding, blueprint-aware.** New `core/hooks/_grounding.py`. Blueprint-aware entity extraction + project grep. FP-averse gating.
5. **CP5 — Blueprint B (Fence Reconstruction), realized end-to-end + first synthesis output.** `core/blueprints/fence_reconstruction.yaml` populated; scenario detector wired to fire on constraint-removal patterns; Layer 2/3 validation against blueprint fields. On successful removal (rollback-path not triggered within window), emits a constraint-safety protocol entry to the framework — the first real Pillar 3 synthesis producer.
6. **CP6 — Layer 4 `verification_trace` schema.** Schema update with blueprint-shaped variants for Fence Reconstruction. Advisory for highest-impact ops in RC; required in v1.0.1. Axiomatic Judgment (decision + synthesis arms), Consequence Chain, and Blueprint D (cascade fields as stubs) ship as structure with advisory-only validation.
7. **CP7 — Pillar 2 hash chain + Pillar 3 substrate.** New `core/hooks/_chain.py` (shared SHA-256 chain), `core/hooks/_pending_contracts.py` (Layer 6 write), `core/hooks/_framework.py` (Pillar 3 framework read/write, hash-chained across protocol entries AND `deferred_discovery` entries), `core/hooks/_context_signature.py` (canonicalization for framework query). Phase 12 audit gains chain-verification precondition.
8. **CP8 — Layer 8 spot-check sampling.** 10%→5% schedule (30-day decay from install); blueprint-fired surfaces at 2× base; synthesized protocols at 2× base with a "protocol quality" verdict dimension; Blueprint D resolutions at 2× base with a "cascade-theater vs real sync" verdict dimension; queue hash-chained; new `episteme review` CLI.
9. **CP9 — Pillar 3 active guidance surface.** Framework query after scenario detection, before blueprint enforcement. One stderr advisory per op (highest-believability match). SessionStart digest ("N protocols synthesized since last session. M deferred discoveries pending triage."). New `episteme guide [--context <keyword>] [--since <date>] [--deferred]` CLI — minimal version; rich interactive mode in v1.0.1.
10. **CP10 — Blueprint D (Architectural Cascade & Escalation) scaffolding.** `core/blueprints/architectural_cascade.yaml` populated. New `core/hooks/_cascade_detector.py` implementing the four selector triggers (cross-surface-ref diff check, refactor/rename/deprecate lexicon, self-escalation `flaw_classification`, generated-artifact symbol-reference check). Structural validation of `patch_vs_refactor_evaluation` + `blast_radius_map[]` + `sync_plan[]`. Every `deferred_discoveries[]` entry is hash-chained into the framework as a `deferred_discovery` record at PreToolUse — operator-visible payoff even before retrospective sync-plan verification (that lands in v1.0.1). Phase 12 audit gains deferred-discovery frequency-by-class and aging queries.

**Engineering session state at v0.11.0 tag:**

- Tests: 202/202 passing (baseline for RC work; each CP adds ~15–25 tests).
- Release: `v0.11.0` tagged and pushed, CHANGELOG entry landed, `MANIFEST.sha256` regenerated (commit `a78c73e`).
- RC engineering checklist closed during the 0.11.0 cycle: items 2, 3, 4, 7, 8, 11 (see § "Road to v1.0.0 RC" below). Items 9, 10 remain as Class B (maintainer design calls). Items 12–15 remain as RC-cycle fixes.
- Cognitive-adoption RC gates (21–28) remain as soak-window criteria; their measurement begins once CP1–CP10 land and the RC soak opens.

**Load-bearing spec constraints (any change is a governance event, not an implementation tweak):**

- The three pillars — Cognitive Blueprints, Append-Only Hash Chain, Framework Synthesis & Active Guidance.
- The four named blueprints — **Axiomatic Judgment** (per-decision source-conflict synthesis), **Fence Reconstruction** (constraint-removal safety synthesis), **Consequence Chain** (irreversible-op decomposition), **Architectural Cascade & Escalation** (emergent-flaw patch-vs-refactor + cascade sync + deferred-discovery logging) — plus the **generic maximum-rigor fallback** (Consequence-Chain-shaped) for unclassified high-impact ops.
- The three orthogonal pairs — L2+L3, L4+L6, L5+L7 — plus the new pair introduced by Pillar 1 (blueprint-selector × L8 selection sample).
- Hot-path ceiling: Layers 2–4 + scenario detector (including cascade detector) + framework query combined < 100 ms p95.
- Spot-check schedule: 10% for first 30 days (calendar-from-install), then 5%.
- Hash-chain scope in RC: episodic tier + pending contracts + framework protocols (including `deferred_discovery` records) only (NOT `derived_knobs.json`, NOT profile-axis changes).
- BYOS stance: kernel intercepts state mutation regardless of tool/MCP/agent source; no tool-specific validation paths; no prescriptive tool-usage in blueprints.
- Pillar 3 guidance is advisory-only, never blocking.
- Blueprint D dogfood — the kernel must satisfy Blueprint D on its own architectural edits (editing episteme while editing episteme). Bypassing is an RC failure regardless of test count.

---

## Road to v1.0.0 RC — concrete checklist (drafted 2026-04-20)

Derived from a read-only audit of the CLI + stateful interceptor (see *Deep Audit Discoveries* in `docs/PROGRESS.md`). Ordered by blocking-weight: items above a line block RC tag; items below are RC → GA polish.

### Blocking for v1.0.0-rc1 tag

1. **Close 0.11.0 first.** ✅ **DONE** — v0.11.0 tagged and shipped 2026-04-21. CHANGELOG entry landed, version reconcile complete across `pyproject.toml` / `.claude-plugin/plugin.json` / `.claude-plugin/marketplace.json`, `kernel/MANIFEST.sha256` regenerated (commit `a78c73e`). The RC cycle is now open against the reframed spec at `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` (status `approved (reframed, second pass)`).

**NEW — Spec-level blocking items for v1.0.0-rc1:**

1a. **Implement the 9-CP plan** per `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § Implementation sequencing. CP1 is the next executable unit; see the "Resume here" block above for the full checkpoint list. Each CP pauses for review; tests stay green at every commit.

1b. **End-to-end dogfood gate — Pillar 3 works, not just runs.** After 30 days of real use on the maintainer's tier, the framework must hold ≥ 3 non-trivial synthesized protocols AND ≥ 1 must fire as guidance on a subsequent op AND the operator must have a spot-check verdict recorded on that firing (useful / vague / overfit). Empty framework or never-fires guidance is a cognitive-level failure of Pillar 3 regardless of whether the code runs green. Criterion lives in the spec § Verification.

1c. **Chain integrity gate — all three streams.** Chain verification succeeds across the RC soak window for episodic tier, pending contracts, AND framework protocols. Any chain-broken event during soak is investigated and root-caused before GA.
2. **Fix `pytest` out-of-box.** `pyproject.toml` has no `[tool.pytest.ini_options]`. A fresh clone + `pip install pytest` + `pytest` produces 6 collection errors (`ModuleNotFoundError: episteme`). Only works with `PYTHONPATH=src pytest` or editable install. NEXT_STEPS already claims "176 passed, zero regressions" — true only under a non-obvious env. One-line fix: add `[tool.pytest.ini_options]` with `pythonpath = ["src"]` + `testpaths = ["tests"]`. Audit verified 176 pass under that config.
3. **Redact secrets in telemetry before write.** `core/hooks/reasoning_surface_guard.py::_write_prediction` and `core/hooks/calibration_telemetry.py::_write_telemetry` log `command_executed` verbatim to `~/.episteme/telemetry/*-audit.jsonl`. Inline secrets (e.g. `curl -H "Authorization: Bearer …"`, `AWS_SECRET_ACCESS_KEY=… terraform apply`) land in plaintext indefinitely. `episodic_writer.py` already redacts; lift that helper out and reuse it in both telemetry writers. Zero-cost, high-leverage confidentiality fix.
4. **Cross-platform support for `state_tracker.py`.** `import fcntl` at module top-level fails on Windows. Hook ships as part of a cross-platform repo; `pyproject.toml` classifiers don't exclude Windows. Wrap the import in `try/except ImportError` and fall back to no-lock (docstring already says "degrade to last-write-wins on exotic filesystems" — extend that path to "no fcntl available"). Small change; unblocks the Windows install story.
5. **Install UX — one-command bootstrap.** `INSTALL.md` currently documents a multi-step flow. For RC, ship `curl https://raw.githubusercontent.com/junjslee/episteme/main/scripts/install.sh | sh` (or the equivalent via `pipx install episteme`), and verify `episteme doctor` green on macOS + Linux after a clean install. Windows path (WSL acceptable for RC; native for GA).
6. **Release-signing + provenance.** Publish to PyPI with SLSA provenance / sigstore attestation. At minimum: tag signed with GPG, `pip install episteme==1.0.0rc1` lands the same bytes as `pip install git+…@v1.0.0rc1`.

### Fix during RC cycle (non-blocking for rc1, blocking for GA)

7. **Episode ID collision.** `_evolve_run` uses `ts.strftime('%Y%m%d-%H%M%S')` as `episode_id`; two `episteme evolve run` calls in the same second silently overwrite each other's episode files. Append microseconds or a short random suffix.
8. **`episteme evolve friction --top-n` negative-value slip.** `argparse` accepts `--top-n -1`, which slices from the end of a Python list and produces garbage output. Either constrain via `type=` with a positive-int checker or clamp `max(0, top_n)` in `_render_friction_report`.
9. **`evolve promote` / `evolve rollback` preserve provenance history.** Both overwrite `provenance.captured_at`, losing the original capture timestamp. Append to a `history: []` list instead of replacing.
10. **`evolve promote --force` must write an audit entry.** Bypassing `gate_result.passed` currently has no tamper-evident trail. Append to `~/.episteme/audit.jsonl` with `forced: true` on every force-promote.
11. **Corrupt `.episteme/reasoning-surface.json` silently reads as "missing".** A malformed JSON file produces the same message as an absent one, so the operator never learns their surface file is broken. Emit a one-line stderr note when the file exists but fails parse.
12. **Auto-mutation of `kernel/CONSTITUTION.md` from friction reports (operator-review gated).** The heuristic already names which unknowns are chronically under-elaborated; wire a `--apply` flag that proposes a CONSTITUTION diff, never auto-merged. Same pattern at `OPERATOR_PROFILE_SCHEMA.md` level via the 0.11 profile-audit loop.
13. **Fence-Check hook.** Failure mode 7 (constraint removal without understanding) is named in docs but has no hook counter. When the agent proposes removing an entry from an `.episteme/*` policy file or a security-relevant config, require a one-line "this constraint exists because …" note in the Reasoning Surface before allowing the edit.
14. **Controller-variety escalation prototype.** Failure mode 9. For PreToolUse on actions matching *neither* allow nor deny pattern sets, route to explicit human confirmation rather than defaulting to allow. Start narrow (network egress) to bound blast radius.
15. **Cross-runtime MCP proxy daemon.** Closes intra-call write-then-execute (see *Architectural bypass vectors* below). The v0.10.0 state tracker fires PostToolUse — *after* the write has landed inside a single Bash call. The daemon inspects at the syscall boundary and refuses to return control until the contract is satisfied.

### Discretionary / polish (nice for RC, not blocking)

16. **`evolve friction --since=30d` window.** `_load_telemetry_pairs` loads all history unbounded; long-running installs slow linearly.
17. **`_should_track` signal-to-noise.** Currently tracks every extension-less file (Makefile, Dockerfile, README) — TTL bounds it but inflates the state file.
18. **Lockfile cleanup.** `~/.episteme/state/session_context.json.lock` persists forever. Benign but lint-worthy.
19. **Ship a reference evaluator for `episteme evolve run`.** Currently `_default_evaluation_report` is a zero-metric stub; an episode is always born with `gate_result.passed: False`. For 1.0: either (a) document this is stub-by-design and the operator wires their own, or (b) ship a minimal reference harness that exercises the demo suite.
20. **Three-path adoption model** (already scoped to 0.12.0 below — lift into RC if it lands quickly; otherwise 1.0.1).

### Verification for RC gate — engineering

Before tagging `v1.0.0-rc1`:
- `PYTHONPATH=src pytest` → 176/176 passing (or test count updated, zero regressions).
- Plain `pytest` from a fresh clone → same result (item 2 closes this gap).
- `episteme doctor` green on macOS + Linux.
- Manual smoke: `episteme init`, `episteme sync`, declare a Reasoning Surface, run an allowed high-impact op, run a blocked one, verify audit + telemetry + episodic records written and redaction applied (item 3).
- `episteme evolve friction` against ≥ 7 days of real telemetry — Friction Report renders, no crash, no secrets in output.
- `episteme kernel verify` clean (item 1 — MANIFEST regen).

### Verification for RC gate — cognitive adoption (the soul of the product)

The engineering gates above verify the *enforcement arm*. They are necessary and insufficient. `episteme` is a framework for how an agent should think; the blocker exists only to keep that framework from being skipped under pressure. A 1.0 that passes every engineering gate but never changes how decisions are actually made is a 1.0 of the wrong product. Add these gates alongside the engineering ones:

21. **Reasoning-quality signal visible in the episodic tier.** Over ≥ 7 days of real use, inspect `~/.episteme/memory/episodic/*.jsonl`. For every high-impact decision, the record carries a *Reasoning-Surface snapshot* with a non-lazy `core_question`, ≥ 1 substantive unknown, and a falsifiable disconfirmation. Gate: sample 20 random records — 0 with lazy placeholders, 0 with disconfirmations that don't name an observable outcome. If this fails, the guard is being satisfied mechanically (operator / agent is producing fluent-looking surfaces to get through the block) rather than internalized. That is a cognitive-product failure regardless of whether the blocker is working.
22. **Disconfirmation actually fires.** Against the same window: at least one recorded decision where the declared disconfirmation *did* fire (the predicted-wrong condition was observed) AND the downstream action changed in response. Zero fires across 7 days of real work is the signature of disconfirmations written to pass validation rather than to be tested. If this happens, raise the minimum-specificity threshold (via `disconfirmation_specificity_min` in `~/.episteme/derived_knobs.json`) until declarations become honest.
23. **Facts / inferences / preferences stay separated in session artifacts.** The Reasoning Surface schema declares `knowns`, `unknowns`, `assumptions`, and (implicitly) preferences as distinct fields. Sample 10 recent surfaces — count how often a preference ("we should use X") is filed as a known, or an inference ("this probably works because …") is filed as a fact. Target < 10%. Above that, the separation is formal only and the kernel is not producing the distinction it claims to enforce.
24. **Hypothesis → test → update cycle is observable.** Pick 5 recent Reasoning Surfaces with a declared hypothesis. Trace forward in the episodic tier: was the hypothesis validated, refined, or invalidated by the outcome? Target ≥ 3 of 5 have an explicit update ("hypothesis invalidated, revised to Y" in the next surface or a reflective-tier entry). If 0 of 5, the framework is producing hypotheses but not closing the loop — the agent is declaring thinking, not doing thinking.
25. **Profile-audit loop catches reasoning drift (not just outcome drift).** Phase 12 deliverable. The audit loop compares episodic-tier reasoning patterns against the operator's declared cognitive profile (e.g. `dominant_lens: failure-first` should show up as failure-mode inversion in the decision record). Gate: the loop surfaces ≥ 1 real drift detection against the maintainer's own profile over the RC cycle. If it never surfaces anything, the loop is documentation — not a control signal.
26. **Semantic-tier proposals encode *how we think*, not just *what we do*.** The promotion job should emit patterns like "decisions flagged `domain: complex` but treated as `complicated` → recurring disconfirmation miss," not just "git push failed 3× this week." Sample semantic proposals from the 0.11 promotion job — ≥ 1 must name a *reasoning-shape* regularity, not only an outcome regularity.
27. **Failure-mode taxonomy is load-bearing in real decisions.** `kernel/FAILURE_MODES.md` names nine. Over the RC window, episodic records should *cite* at least three distinct failure-mode ids as the reason a decision was re-framed (e.g. "WYSIATI fired — unknowns field was blank because context was silent, not because unknowns were absent"). Zero citations means the taxonomy is decorative.
28. **Kernel doesn't need the kernel.** A narrower cut of #23: when working *on* episteme itself (as in this session), the maintainer's own decisions should show up in the episodic tier with the same discipline demanded of downstream users. If the kernel's author bypasses the kernel while working on the kernel, the product fails the dogfood test.

**Interpretation.** Gates 21–28 fail when the framework is producing artifacts rather than changing cognition. Every failure mode above has the same shape: *mechanically-compliant, epistemically-empty*. The enforcement arm cannot fix this — it can only prevent the *absence* of declarations. Fixing it requires sharper thresholds, clearer schema guidance, and operator review. Ship RC when both engineering gates and at least four of the eight cognitive gates pass against real usage, with the remaining four named as known-gaps in 1.0.1 scope.

---

## Immediate (v1.0 RC — drives from `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`)

**v0.11.0 shipped 2026-04-21.** All fourteen phases of the 0.11.0 plan closed (phases 1–11 + coherence pass + raster follow-up + Mermaid replacement + phase 12 profile-audit loop + phase 13 changelog/version reconcile + phase 14 MANIFEST regeneration). Tag `v0.11.0` pushed; `kernel/CHANGELOG.md` current; `MANIFEST.sha256` fresh. Full historical detail in the *Closed in 0.11.0* section below.

The v1.0 RC cycle is now open. The entry point, 9-CP plan, and load-bearing constraints are in the *Resume here* block at the top of this file. The approved spec is `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` — *Design — Causal-Consequence Scaffolding & Protocol Synthesis — v1.0 RC* — status `approved (reframed, second pass)` as of 2026-04-21.

**Why the v1.0 RC scope is not just "ship the blocker at more contexts."** The spec reframes the whole kernel around three axes the substrate cannot perform natively: (1) causal-consequence modeling per action, (2) protocol synthesis from conflicting sources into a tamper-evident framework, (3) active guidance using accumulated protocols at future decision points. The 9 CPs build these three pillars in layered commits; CP5 (Fence Reconstruction end-to-end including synthesis output) and CP9 (active-guidance surface) are the operator-visible payoffs — the rest are substrate.

## Follow-on wiring (can land alongside phases 11–14 or in 0.11.1)

Phase 9 shipped one knob end-to-end (`disconfirmation_specificity_min` + companion `unknown_specificity_min`). The other six declared knobs are *computed* in `~/.episteme/derived_knobs.json` but *not consumed* by any hook yet. Each is a small pattern-match on phase 9's wiring:

- **`default_autonomy_class`** → gate in `block_dangerous.py` or a new PreToolUse escalation shim. Highest-leverage of the six: actually changes which commands an agent can run without confirmation.
- **`noise_watch_set`** → surfaced by `session_context.py` at SessionStart as an explicit "watch for: status-pressure, false-urgency" banner. Cheap to wire.
- **`preferred_lens_order`** → pure advisory; inject into the Reasoning Surface template or the Frame-stage prompts.
- **`explanation_form`**, **`checkpoint_frequency`**, **`scaffold_vs_terse`**, **`fence_check_strictness`** → same shape, progressively lower leverage.

Episodic-tier also has three declared triggers not yet firing (only high-impact pattern match is active). Adding them:
- **Hook-blocked action** → episodic_writer reads `~/.episteme/audit.jsonl` at PostToolUse and correlates blocks to the current tool call.
- **Disconfirmation-fired** → needs the Verify stage to signal; not available without explicit operator interaction or a Verify hook.
- **Operator-elected** → needs a CLI / slash-command affordance (`episteme note "<text>"`).

## Carryover from 0.10.0 — still live, independent of the 0.11 pass

- **First friction-report pass** — after ~1 week of real v0.10.0 use, run `episteme evolve friction` against accumulated telemetry. Answer: do the ranked unknowns point at real calibration debt? Are the friction-prone ops the same ones humans are already suspicious of? Tune the heuristic (currently: skip empty envelopes; rank by raw frequency) if the top-N doesn't track intuition.
- **Stateful-interception FP audit** — scan `~/.episteme/audit.jsonl` for blocks carrying the `via agent-written <path>` label. Any false positive here is a regression-budget hit.
- **Tag and push `v0.10.0`** after one-week soak if no FP spike and no telemetry anomalies. Independent of 0.11.

## Short-term

- **Three-path adoption model (scoped to 0.12.0; endorsed by operator).** Today the repo ships the maintainer's real profile in `core/memory/global/` and `.gitignore`'s comment tells forkers to "edit them to make them your own." That implicitly forces the author's values as the forker's starting point — a schema violation (OPERATOR_PROFILE_SCHEMA.md section 4b: "null = unknown, not default"). Replace with three explicit on-ramps:
  - **Example mode** — maintainer's real filled profile ships at `examples/author/global/` as a worked reference. Forker reads, doesn't copy. Preserves the schema's "a profile must distinguish this operator" rule.
  - **Ingest mode** — `episteme init --ingest=author` copies the example verbatim to `core/memory/global/` as a quickstart. Honest: the forker's agent behaves *as the maintainer's agent would*, with a visible `confidence: ingested-from-author` metadata flag per axis so the profile-audit loop surfaces it for re-elicitation over time.
  - **Fill mode** — `episteme init` runs interactive elicitation, prompting axis-by-axis against the anchor text from the schema. Leaves anything unelicited as `null`.
- **Proposal acceptance step (phase 11.5).** `episteme memory accept <proposal-id>` reads the reflective proposal, promotes it to `~/.episteme/memory/semantic/YYYY-MM-DD.jsonl` under the schema, and marks the proposal `status: accepted` with a back-reference to the semantic record. Deferred until real usage shows whether per-proposal or bulk review is the better UX.
- **Auto-refinement of `CONSTITUTION.md` from the friction report.** The heuristic already names which unknowns are chronically under-elaborated; wire a `--apply` flag that proposes a CONSTITUTION.md diff, gated by human review — never auto-merged. Same pattern applied at `OPERATOR_PROFILE_SCHEMA.md` level via the 0.11 profile-audit loop.
- **Fence-check enforcement in hooks.** Failure mode 7 (constraint removal without understanding) is named in the docs but has no hook counter. When the agent proposes removing an entry from an `.episteme/*` policy file, a forbidden-patterns file, or a security-relevant config, require a one-line "this constraint exists because …" note in the Reasoning Surface before allowing the edit. Smaller than a full constraint-archaeology feature; closes the cheapest version of the gap.
- **Controller-variety escalation prototype.** Failure mode 9. For PreToolUse events on actions that match *neither* the allow nor deny pattern sets, route to explicit human confirmation rather than defaulting to allow. Start with a narrow action class (network egress) to bound the blast radius of a wrong default.

## Medium-term (roadmap)

- Multi-operator mode design (Gap C) — deferred past 0.10.0; requires profile schema rework.
- **Cross-runtime MCP proxy daemon — the next real Sovereign Kernel step.** v0.10.0 gives the kernel *memory* across calls. The cross-runtime daemon gives the kernel *mediation* at the syscall boundary: pause execution between the write and the exec, inspect every subprocess fork, and refuse to return control to the agent until the contract is satisfied. This is what closes intra-call indirection (see below). Blocked on telemetry-informed demand evidence from v0.10.0.

## Architectural bypass vectors — remaining open after v0.10.0

v0.10.0 closed write-then-execute *across tool calls* (state tracker + deep-scan) and variable-indirection (`bash $F` against any recent tracked write). These remain:

1. **Intra-call write-then-execute.** `echo "git push" > s.sh && bash s.sh` as a single Bash tool call is caught today only by the in-command text scanner — state tracking fires PostToolUse, after the write has landed. Fix needs a cross-runtime proxy daemon. Targeted at 0.11+.
2. **Dynamic shell assembly.** `A=git; B=push; $A $B` — unchanged from 0.8.1. Would require a lightweight shell parser, or a deny-by-default policy on `$()`/backticks (legitimate automation break). Deferred pending cost/benefit review.
3. **Heredocs with variable terminators.** The v0.10-α redirect parser is regex-based and misses `cat <<"$EOF" > f`. A shell-parser dependency is the fix; weighed against its cost.
4. **Scripts > 64 KB (scan) / > 256 KB (hash).** Unchanged caps. Raising them increases hook latency and creates a DoS surface on pathologically large files. Accepted until a real FN is reported.

---

## Closed in 0.11.0 (phases 1–11)

- **Phase 11 — semantic-tier promotion job.** New `src/episteme/_memory_promote.py` + CLI subcommand `episteme memory promote`. Reads episodic tier, clusters by `(domain_marker, primary high-impact pattern)`, computes per-cluster success rate + disconfirmation fire rate, emits deterministic proposals to `~/.episteme/memory/reflective/semantic_proposals.jsonl`. Proposal ids are stable hashes of the signature + sorted evidence refs, so re-running on identical input produces byte-identical output. Never touches the semantic tier; promotion is explicit. End-to-end verified with 6 synthetic records → 2 proposals (git push mixed, npm publish typically-succeeds). 19 new tests.
- **Phase 9 — profile becomes control signal.** New `core/hooks/_derived_knobs.py` (axis-to-knob derivation + reader/writer). `reasoning_surface_guard.py` replaces module-level `MIN_DISCONFIRMATION_LEN` / `MIN_UNKNOWN_LEN` constants with lookups against `~/.episteme/derived_knobs.json`, fallback 15. For the maintainer's v2 profile the minimum raises 15 → 27; an 18-char disconfirmation now fails, a 39-char passes. First end-to-end proof the v2 profile modulates hook behavior. 17 new tests.
- **Phase 10 — episodic-tier writer.** New PostToolUse hook `core/hooks/episodic_writer.py` fires on high-impact Bash pattern match; assembles a record per the `memory-contract-v1` schema (common.json + episodic_record.json); appends to `~/.episteme/memory/episodic/YYYY-MM-DD.jsonl`. Reasoning-Surface snapshot attached when present; secrets redacted before write; provenance confidence reflects available signal. Wired into `hooks/hooks.json` PostToolUse/Bash alongside `state_tracker` and `calibration_telemetry`, all async. Correlation-id algorithm mirrors calibration telemetry so records join. 19 new tests; end-to-end smoke-test verified a real record at `~/.episteme/memory/episodic/2026-04-20.jsonl`.
- **Operator profile v2 filled.** `core/memory/global/operator_profile.md` migrated. 6 process axes rescored 0–3 → 0–5. All 9 cognitive-style axes populated (3 flipped to `elicited` based on source-doc citations: `abstraction_entry`, `explanation_depth`, `asymmetry_posture`; 5 remain `inferred` pending phase-12 audit). Expertise map populated.
- **Test suite 121 → 176** (55 new across phases 9/10/11). Zero regressions.

## Closed in 0.11.0-entry (docs-only pass)

- **Attribution surface expansion.** `kernel/REFERENCES.md` primary-source count 14 → 23 — added Ashby (requisite variety), Gall (working-simple precedes working-complex), Tetlock (calibration), Laplace/Jaynes (probabilistic inference), Goodhart/Strathern (measure-as-target drift), Klein (recognition-primed decision), Chesterton (the fence), Feynman (self-deception), Festinger (cognitive dissonance). Secondary: Tulving/Squire, Snowden, Wittgenstein. No buzzword names leak into body docs.
- **Governance-layer failure modes named.** `kernel/FAILURE_MODES.md` adds modes 7 (constraint removal without understanding → Fence-Check), 8 (measure-as-target drift → scorecard audit vs outcome), 9 (controller-variety mismatch → escalate-by-default). Kept separate from the Kahneman six so that taxonomy stays clean.
- **Reasoning Surface — evidence-weighted update mechanic, `domain` marker, `tacit_call` marker.** Closes Gap D and the Cynefin classification gap. Assumptions no longer flip-to-Known on first evidence; they carry updated plausibility. Domain (Clear/Complicated/Complex/Chaotic) precedes the four fields. `tacit_call: true` relaxes Knowns for judgment-driven decisions without relaxing accountability.
- **Kernel limits 7 and 8.** Rule-based governance limit (controller coverage < action space → escalate, not default-allow/deny) and scorecard-as-target limit (profile axes are hypotheses, audited against episodic record, drift allowed).
- **Operator profile schema v2.** Two scorecard layers: process (0–5 with anchor text) + cognitive-style (9 typed axes — dominant lens, noise signature, abstraction entry, decision cadence, explanation depth, feedback mode, uncertainty tolerance, asymmetry posture, fence discipline). Per-axis metadata (`confidence`, `last_observed`, `evidence_refs[]`, `drift_signal`). `expertise_map` field. Declared *derived behavior knobs* adapters compute from axes — the bridge from "profile is documentation" to "profile is control signal." Audit Discipline section counters measure-as-target drift.
- **Memory architecture contract — new `kernel/MEMORY_ARCHITECTURE.md`.** Five tiers (working / episodic / semantic / procedural / reflective), each with declared purpose / lifetime / writer / reader. Retrieval is query-by-situation with similarity × recency × outcome-weight ranking. Promotion is gated: episodic → semantic requires pattern + outcome stability; semantic → profile-drift proposal requires long-window conviction and operator review — never auto-merged. Forgetting is declared per tier (TTL + compaction). Write/read discipline specified per workflow stage. Integrity guarantees: episodic append-only, promotion idempotent, forgetting itself logged.
- **SUMMARY and README updates.** Six-modes table expanded to nine. Operator-profile-v2 and memory-architecture paragraphs added to SUMMARY. File list in README adds `MEMORY_ARCHITECTURE.md`.

## Closed in 0.10.0

- **Stateful interception.** Cross-call memory shipped. `core/hooks/state_tracker.py` persists agent-written file paths + sha256 + ts to `~/.episteme/state/session_context.json` (24 h TTL). `reasoning_surface_guard.py` consults the store at execute time, deep-scanning recently-written files referenced by name OR by variable-indirection shape (`bash $F`).
- **Heuristic friction analyzer.** `episteme evolve friction` pairs prediction↔outcome telemetry by `correlation_id`, flags `exit_code ≠ 0` despite positive predictions, ranks most-violated unknowns and friction-prone ops, emits a Markdown Friction Report. Seed for automated CONSTITUTION.md refinement.
- **SVG control-plane diagram.** `docs/assets/architecture_v2.svg` replaces the ASCII diagram in `README.md`. Three-layer schematic; Stateful Interceptor loop and Calibration Telemetry feed visible.
- **Gap B — `last_elicited`.** Required metadata on `operator_profile.md`, mirrored to generated JSON; `episteme sync` injects a stale-context warning block when absent or >30 days old. Schema doc updated.
- **Final neutrality sweep.** No literal absolute-user-home strings remain in any committed doc.
- **Version reconcile** — `pyproject.toml`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` all at 0.10.0.
- Tests 86 → 121. 0 regressions.

## Closed in 0.9.0-entry
- **Repository is neutral.** Personal filesystem paths and operator identifiers removed from docs and demo artifacts. Public GitHub identity (`junjslee`) retained intentionally.
- **Calibration telemetry shipped (Gap A).** Prediction + outcome JSONL records in `~/.episteme/telemetry/YYYY-MM-DD-audit.jsonl`, joined by `correlation_id`. Local-only. Never transmitted.
- **Backtick substitution closed.** `` `git push` `` now normalizes the same way as `"git push"` and trips the pattern set.
- **`eval $VAR` blocked.** `eval "$CMD"`, `eval $CMD` block with label `"eval with variable indirection"`. Literal `eval "echo hi"` still passes.
- **Shell-script execution scanned.** Hook resolves and reads `.sh` files referenced by `./x.sh`, `bash x.sh`, `sh x.sh`, `zsh x.sh`, `source x.sh`, `. x.sh` and scans up to 64 KB for high-impact patterns. Missing scripts pass through (FP-averse).
- **Visual demo harness.** `scripts/demo_strict_mode.sh` is reproducible and recording-ready. `docs/CONTRIBUTING.md` documents the `asciinema rec → agg` flow.
- **Test coverage 17 → 35 guard/telemetry cases** (full suite 86 passed, 0 regressions).

## Closed in 0.8.1
- **Strict mode is default.** Missing / stale / incomplete / lazy Reasoning Surface → exit 2 (block). Opt out per-project via `.episteme/advisory-surface`.
- **Semantic validator shipped.** Lazy-token blocklist + 15-char minimums on `disconfirmation` and each `unknowns` entry. `"disconfirmation": "None"` and `"해당 없음"` no longer pass.
- **Command normalization closes three bypass shapes.** `subprocess.run(['git','push'])`, `os.system('git push')`, `sh -c 'npm publish'` all trip the same regex patterns as bare shell.
- **Block-mode stderr upgraded.** `"Execution blocked by Episteme Strict Mode. Missing or invalid Reasoning Surface."` + concrete validator reasons + advisory-mode opt-out pointer.
- **`episteme inject` reworked.** Default is no-marker (strict is default); `--no-strict` writes `advisory-surface` explicitly.

## Closed in 0.8.0
- Remove compat symlink `~/cognitive-os`
- Verify `/plugin marketplace add junjslee/episteme` resolves (user confirmed in-session)
- Tag + push `v0.8.0`
- Reconcile `pyproject.toml`, `plugin.json`, `marketplace.json` versions
- Add `kernel/CHANGELOG.md` 0.8.0 entry
