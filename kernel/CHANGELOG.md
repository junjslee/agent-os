# Kernel Changelog

Versioned history of the episteme kernel. The kernel is a contract;
changes to it are load-bearing for every adapter and every operator
profile downstream. This file is the audit trail.

Format: `[version] — date — change`. Versions follow semantic intent:
- **major** — a principle added, removed, or reframed.
- **minor** — a new artifact or schema field.
- **patch** — clarifications, attribution, boundary statements.

---

## [0.11.0] — 2026-04-21 — The Calibration Loop: profile becomes control signal, episodic tier writes, semantic promotion, profile-audit closes the circuit

This release closes the loop the kernel has been building toward since
0.8.0: an operator's declared cognitive profile is no longer
documentation — it is a *control signal* that modulates hook behavior
(phase 9), is checked against the *lived record* of high-impact
decisions (phase 10), is *clustered into proposals* for promotion
(phase 11), and is *audited for drift* against praxis (phase 12). The
profile-audit loop counters measure-as-target drift (failure mode 8)
by surfacing where the operator's claim and the operator's behavior
have diverged — not as a verdict, but as a re-elicitation prompt.

- **Phase 9 — profile becomes control signal.** New `core/hooks/_derived_knobs.py`
  derives 7 behavior knobs from the operator profile axes and writes
  them to `~/.episteme/derived_knobs.json`. `reasoning_surface_guard.py`
  replaces module-level `MIN_DISCONFIRMATION_LEN` /
  `MIN_UNKNOWN_LEN` constants with lookups against the derived knob,
  fallback 15. For the maintainer's v2 profile the minimum raises 15
  → 27. First end-to-end proof the v2 profile modulates hook
  behavior. 17 new tests.
- **Phase 10 — episodic-tier writer.** New PostToolUse hook
  `core/hooks/episodic_writer.py` fires on high-impact Bash pattern
  match; assembles a record per the `memory-contract-v1` schema;
  appends to `~/.episteme/memory/episodic/YYYY-MM-DD.jsonl`.
  Reasoning-Surface snapshot attached when present (snapshot now
  includes `knowns` per phase-12 requirement; previously omitted);
  secrets redacted before write; provenance confidence reflects
  available signal. Wired into `hooks/hooks.json` PostToolUse/Bash
  alongside `state_tracker` and `calibration_telemetry`, all async.
  19 new tests.
- **Phase 11 — semantic-tier promotion job.** New `src/episteme/_memory_promote.py`
  + CLI subcommand `episteme memory promote`. Reads episodic tier,
  clusters by `(domain_marker, primary high-impact pattern)`,
  computes per-cluster success rate + disconfirmation fire rate,
  emits deterministic proposals to
  `~/.episteme/memory/reflective/semantic_proposals.jsonl`. Proposal
  ids are stable hashes of the signature + sorted evidence refs, so
  re-running on identical input produces byte-identical output.
  Never touches the semantic tier; promotion is explicit. 19 new tests.
- **Phase 11.5 — coherence pass (docs-only).** Specced in
  `docs/DESIGN_V0_11_COHERENCE_PASS.md`. Both arxiv-style figures
  rasterized to PNG; native Mermaid `graph TD` flowchart added in
  `docs/ARCHITECTURE.md` mapping doxa / episteme / praxis / 결 to
  exact file-level implementations. README leads thinking-first.
- **Phase 12 — profile-audit loop (4 worked axes).** New
  `src/episteme/_profile_audit.py` library + `episteme profile audit`
  CLI surface. On-demand comparison of each declared cognitive
  axis against the episodic record, emitted to
  `~/.episteme/memory/reflective/profile_audit.jsonl`. SessionStart
  surfaces unacknowledged drift via `core/hooks/session_context.py`.
  Four axes operationalized in 0.11.0; 11 axes ship as explicit
  per-axis stubs pointing to the spec sketch table for 0.11.1:
    - **Axis C · `fence_discipline` (CP2).** Constraint-removal
      records must carry reconstruction (S1) and review-trace (S2).
      Single-signature catastrophic exception per spec §Axis C —
      either signature failing flags drift, because constraint
      removal is high-consequence. Drift thresholds are
      claim-relative: `_FENCE_BANDS_BY_CLAIM` maps 0-5 to
      `[drift_floor, ideal_ceiling]` per signature. Claim 4
      reproduces the spec's 0.70 / 0.50 thresholds; claim 0 has
      floor 0.0 and cannot drift by under-performing.
    - **Axis A · `dominant_lens: failure-first` (CP3).** Two
      signatures: failure-frame ratio over unknowns +
      disconfirmation (S1, against `failure_frame` /
      `success_frame` lexicons in `kernel/PHASE_12_LEXICON.md`),
      and fire-condition rate from a per-record syntactic
      classifier on disconfirmation (S2). D1 strict — both must
      miss to flag drift. CP3 implements only `failure-first` at
      position 0; other lens values follow Template A.
    - **Axis D · `asymmetry_posture: loss-averse` (CP4).** Two
      signatures: stop-condition rate from a syntactic classifier
      on disconfirmation (S1), and rollback-mention rate against
      the `rollback_adjacent` lexicon over knowns + assumptions
      (S2). D1 strict. Success-verb vocabulary is deliberately
      tight — words like `deploy`, `promote`, `ship`, `merge`
      are excluded because they're routinely the noun-objects
      of stop verbs.
    - **Axis B · `noise_signature: status-pressure` (CP5).** Two
      signatures: buzzword density per record (S1, against the
      `buzzword` lexicon) and specificity-collapse under inferred
      cadence (S2). DRIFT DIRECTION INVERTED for S1 — high
      buzzword density against a counter-screen claim is what
      drift looks like. Catastrophic single-signature exception
      at S1 > 0.30 (decorative-language density at that level is
      itself the signal). Highest evidence floor (N ≥ 40) of all
      four axes.
- **Schema additions.** New `core/schemas/profile-audit/profile_audit_v1.json`
  governs the audit record shape. New `kernel/PHASE_12_LEXICON.md`
  ships five default lexicons (`failure_frame`, `success_frame`,
  `buzzword`, `causal_connective`, `rollback_adjacent`); operator
  override path at `core/memory/global/phase_12_lexicon.md`. Each
  audit record carries a `lexicon_fingerprint` so lexicon drift is
  visible in the record stream, never silent.
- **Operator profile v2 filled.** `core/memory/global/operator_profile.md`
  migrated from 0-3 to 0-5 process axes; all 9 cognitive-style
  axes populated. 5 axes remain `inferred` pending phase-12 audit
  signal — that the audit currently returns insufficient_evidence
  on the maintainer's small tier is correct cold-start behavior
  per spec §Cold-start, not a phase-12 bug.
- **D-countermeasures intact across CP2-CP5.** D1 multi-signature
  convergence (with the two named single-signature exceptions for
  Axis C and Axis B's catastrophic threshold), D2 retrospective-
  only, D3 re-elicitation never auto-correction, D4 named limits
  cited in every axis reason string.
- **Demo + README narrative re-centered.** `scripts/demo_posture.sh`
  gains a 2.2-second Beat 0 title card naming the Reasoning
  Surface fields, the Beat 3 BLOCK rendered in dim red (matching
  the script narration that calls it "the shallowest thing the
  kernel does"), and the falsifiable PASS in bright green as the
  actual climax. README posture-demo bullet re-captioned to put
  the Reasoning Surface itself at the climax — the specificity
  ladder is now framed as the *test* of the surface, not the
  point of it. New `docs/DEMOS.md` houses the second demo
  (renamed "posture as enforcement of the surface") so the
  homepage no longer puts cognition and enforcement at parity.
- **Versions reconciled:** `pyproject.toml`,
  `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
  all 0.10.0 → 0.11.0.
- **Tests:** 121 → 304 passing (+183 across phases 9, 10, 11, 12).
  Zero regressions.

**What 0.11.0 is honestly NOT:**
1. **Coverage on 11 of 15 axes.** The spec-sketch table lays out
   templates for them; CP2-CP5 ship the four worked axes that prove
   the patterns. Remaining 11 are explicit per-axis stubs deferred
   to 0.11.1 — chosen over a generic fallback so the audit log is
   readable rather than 11 identical "not yet implemented" lines.
2. **Cross-axis consistency checks.** Per spec open question 5,
   v0.11 does per-axis only. `fence_discipline` high +
   `risk_tolerance` low expected; `fence_discipline` low +
   `risk_tolerance` low internally inconsistent — both pass in
   v0.11. Cross-axis lands in a follow-on.
3. **A schema field for cadence.** Per spec open question 2,
   v0.11 infers cadence from timestamp clustering; the
   `cadence_marker` field is 0.11.1 work.
4. **Goodhart-resistance beyond layer 1.** Reasoning Surface Guard
   still does syntactic + length checks. A sufficiently-aware
   agent can still defeat the gate with fluent-vacuous content
   that passes both. Phase 12 catches this OVER TIME via the
   audit loop, but the hot-path validator remains syntactic.
   v1.0 RC scope work — see `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`
   for the proposed defense-in-depth upgrade.

## [0.10.0] — 2026-04-20 — The Sovereign Kernel: stateful interception + heuristic friction analyzer + profile freshness gate

- **Added** `core/hooks/state_tracker.py` — PostToolUse recorder that persists every agent-written file path, sha256, and timestamp to `~/.episteme/state/session_context.json` (24 h TTL, atomic temp+rename, `fcntl.flock` serialization). Tracks `Write`/`Edit`/`MultiEdit` targets across a curated extension set (`.sh`, `.bash`, `.zsh`, `.ksh`, `.py`, `.pyw`, `.js`, `.mjs`, `.cjs`, `.ts`, `.rb`, `.pl`, `.php`, plus extension-less files) and `Bash` redirect targets (`>`, `>>`, `| tee [-a]`).
- **Extended** `core/hooks/reasoning_surface_guard.py` to consult the state store. Two new match modes: (1) literal path/basename reference in a Bash command → deep-scan that file's current content against the high-impact pattern set; (2) variable-indirection shape (`bash $F`, `python $F`, `./$X`, `source $X`) against any recent tracked write → deep-scan every recent entry. Closes the write-then-execute-across-calls bypass and the `F=run.sh; bash $F` indirection shape.
- **Added** `episteme evolve friction` heuristic telemetry analyzer. Pairs prediction↔outcome JSONL records by `correlation_id`, flags `exit_code ≠ 0` against positive predictions, ranks most-violated unknowns and friction-prone ops, and emits a Markdown Friction Report. Deterministic, no ML. Seed for future automated `CONSTITUTION.md` refinement — see `docs/NEXT_STEPS.md`.
- **Added** `Last elicited: YYYY-MM-DD` required metadata on the operator profile markdown (Gap B). `episteme sync` parses it and injects a visible "Stale Context Warning" block into the rendered CLAUDE.md when absent or older than 30 days. Mirror field `last_elicited` also written to `.generated/workstyle_profile.json` and `.generated/workstyle_scores.json`. Schema doc (`kernel/OPERATOR_PROFILE_SCHEMA.md`) updated to make the field required.
- **Replaced** the ASCII control-plane diagram in `README.md` with `docs/assets/architecture_v2.svg` — three-layer schematic (Agent Runtime / Episteme Control Plane / Hardware · OS) with the Stateful Interceptor loop and Calibration Telemetry feed visible.
- **Neutrality sweep.** Final pass on historical narrative in `docs/PLAN.md` and `docs/PROGRESS.md`: residual absolute-user-home string references in *descriptions of the prior scrub* replaced with generic `~/...` language. Public `junjslee` GitHub identity retained intentionally.
- **Versions reconciled:** `pyproject.toml`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` all 0.8.0 → 0.10.0.
- **Tests:** 86 → 121 passing (35 new: 12 stateful interception, 7 friction analyzer, 16 last_elicited). Zero regressions.

**Architectural gaps that remain open (honest):**
1. **Intra-call indirection.** A single `Bash` call that both writes and executes a script (`echo "git push" > s.sh && bash s.sh` as *one* tool call) is caught today only by the existing in-command scanner (normalized text contains `git push`). State tracking adds no new coverage for this case because the PostToolUse recorder fires *after* the call completes. The true fix — pausing execution between the write and the exec — requires a cross-runtime proxy daemon (the next-phase Sovereign Kernel, 0.11+). The "Sovereign Kernel" name in 0.10.0 is directional — a first cut, not a finished claim.
2. **Dynamic shell assembly.** `A=git; B=push; $A $B` still passes — same reasoning as 0.8.1.
3. **Heredocs with variable terminators.** The redirect parser is regex-based and will miss `cat <<"$EOF" > f`.
4. **Scripts > 256 KB (hash) / > 64 KB (scan).** Unchanged caps from 0.9.0.

Rationale: 0.9.0-entry proved that a file-on-disk telemetry feed is enough to pair prediction↔outcome for a single operator. 0.10.0 extends that same discipline — file-on-disk state — across the *execution boundary* between a Write and a Bash. The kernel still rides the hook runtime; it does not yet mediate every syscall. The claim of a "Sovereign Kernel" is directionally honest: the control plane now remembers what the agent just wrote, which is the smallest step that meaningfully closes write-then-execute while staying within the Claude Code hook contract. The cross-runtime proxy daemon is the version of this that deserves the name without qualification — it is deferred to 0.11+ and explicitly gated on real-world FN evidence from 0.10.0 telemetry.

## [0.9.0-entry] — 2026-04-20 — Privacy scrub + calibration telemetry + visual demo + bypass hardening

- **Repository neutralized.** Personal filesystem paths and operator identifiers stripped from `docs/PROGRESS.md`, `docs/NEXT_STEPS.md`, `docs/assets/setup-demo.svg`, and `demos/01_attribution-audit/reasoning-surface.json`. Public `junjslee` GitHub identity retained intentionally.
- **Calibration telemetry shipped (Gap A).** `reasoning_surface_guard.py` writes a `prediction` record (correlation_id, command_executed, epistemic_prediction) to `~/.episteme/telemetry/YYYY-MM-DD-audit.jsonl` on every allowed high-impact Bash. New `core/hooks/calibration_telemetry.py` (PostToolUse) writes the matching `outcome` record carrying `exit_code` and status. Local-only; never transmitted.
- **Backtick substitution closed.** Command normalization maps backticks to whitespace; `` `git push` `` now trips the same patterns as bare shell.
- **`eval $VAR` blocked.** New indirection pattern label `"eval with variable indirection"` blocks `eval "$CMD"` / `eval $CMD`. Literal `eval "echo hi"` still passes.
- **Shell-script execution scanned.** `_match_script_execution` resolves and scans up to 64 KB of `.sh` files referenced by `./x.sh`, `bash x.sh`, `sh x.sh`, `zsh x.sh`, `source x.sh`, `. x.sh`. Missing scripts pass through (FP-averse).
- **Visual demo harness.** `scripts/demo_strict_mode.sh` is reproducible and recording-ready; `docs/CONTRIBUTING.md` documents the `asciinema rec → agg` flow.
- **Test coverage** 17 → 86 cases covering guard, telemetry, profile cognition, managed file, kernel integrity, workflow guard, context guard.

## [0.8.1] — 2026-04-20 — Strict-by-default enforcement + semantic validator + bypass-resistant matching

- **Flipped** `core/hooks/reasoning_surface_guard.py` default from advisory to **strict (blocking)**. Missing / stale / incomplete / lazy surfaces now exit 2 and block the tool call. Opt-out per-project: `touch .episteme/advisory-surface` (legacy `.episteme/strict-surface` is now a no-op — strict is default).
- **Added** semantic validator to `_surface_missing_fields`: `disconfirmation` and each `unknowns` entry must be ≥ 15 chars and must not match the lazy-token blocklist (`none`, `n/a`, `tbd`, `nothing`, `null`, `unknown`, `해당 없음`, `해당없음`, `없음`, `모름`, `-`, `--`, `...`, etc.). Closes the Lazy Agent Problem — an agent writing `"disconfirmation": "None"` or `"해당 없음"` no longer passes the gate.
- **Added** command-text normalization before regex matching: quotes, commas, brackets, parens, and braces map to whitespace, so bypass shapes like `python -c "subprocess.run(['git','push'])"`, `os.system('git push')`, and `sh -c 'npm publish'` trip the same high-impact patterns as bare shell invocations. Closes a concrete bypass vector where the `\b...\s+...\b` patterns missed quoted/bracketed forms.
- **Updated** `episteme inject`: strict mode is now the default no-op (nothing to create); `--no-strict` writes `.episteme/advisory-surface` explicitly. Removes the old `strict-surface` marker creation — redundant under the new default.
- **Strengthened** block-mode stderr output: leads with `"Execution blocked by Episteme Strict Mode. Missing or invalid Reasoning Surface."` and includes a one-line advisory-mode opt-out pointer.
- **Expanded** test coverage in `tests/test_reasoning_surface_guard.py` to 17 cases covering: strict-by-default on every failure mode (missing/stale/incomplete/lockfile), advisory-marker downgrade, legacy-marker no-op behavior, lazy-token rejection for disconfirmation and unknowns, short-string rejection, and three bypass-vector tests (subprocess list form, os.system, sh -c wrapping).
- **Synchronized** `kernel/HOOKS_MAP.md` with the new default and validator contract.

Rationale: 0.8.0's claim of a "deterministic control plane" was architecturally true (the PreToolUse hook does intercept every high-impact op) but operationally hedged — the default was advisory, and the validator only checked for non-empty strings. 0.8.1 closes both gaps. The system now delivers what the README has been claiming since 0.6.0: a strict cognitive contract that blocks execution until Knowns / Unknowns / Assumptions / Disconfirmation are filled with concrete, measurable, non-placeholder content.

## [0.8.0] — 2026-04-19 — Core migration: cognitive-os → episteme (name alignment + version reconciliation)

- **Renamed** Python package `src/cognitive_os/` → `src/episteme/`; all imports and console script (`episteme = "episteme.cli:main"`) updated. `git mv` preserved history.
- **Renamed** runtime directory convention `.cognitive-os/` → `.episteme/`; schema identifier `cognitive-os/reasoning-surface@1` → `episteme/reasoning-surface@1`.
- **Renamed** GitHub repo `junjslee/cognitive-os` → `junjslee/episteme` (old URL 301-redirects); all in-repo references updated.
- **Renamed** env vars `COGNITIVE_OS_CONDA_ROOT` → `EPISTEME_CONDA_ROOT` (legacy var still honored).
- **Made dynamic** the Python runtime: `CONDA_ROOT` hardcoded path → `PYTHON_PREFIX` derived from `sys.prefix`. New vars `EPISTEME_PYTHON_PREFIX` / `EPISTEME_PYTHON` / `EPISTEME_REQUIRE_CONDA`. `episteme doctor` skips conda checks on non-conda runtimes unless explicitly required.
- **Reconciled** versions: `pyproject.toml` (0.2.0 → 0.8.0), `.claude-plugin/plugin.json` (0.6.0 → 0.8.0), `.claude-plugin/marketplace.json` plugin (0.6.0 → 0.8.0). Three surfaces now agree.
- **Added** `.gitignore` rules for `.episteme/` and legacy `.cognitive-os/` runtime dirs.
- **Verified** `v0.8.0` git tag pushed to `origin`; `/plugin marketplace add junjslee/episteme` resolves.

Rationale: the name `cognitive-os` implied a replacement OS-layer; the project is an epistemic *posture* that rides existing runtimes. `episteme` (ἐπιστήμη — "justified, audited knowledge") matches the kernel's actual claim: knowledge is provisional unless it can be traced to evidence and disconfirmation conditions. No kernel principle or schema field changed — this is a cosmetic/identity migration, hence minor-version bump despite touching every adapter surface.

## [0.7.0] — 2026-04-19 — Real enforcement: audit log, inject command, strict blocking

- **Added** `_write_audit()` to `core/hooks/reasoning_surface_guard.py` — every reasoning-surface check (passed / advisory / blocked) now writes a structured entry to `~/.episteme/audit.jsonl`. Audit failure is silenced so it can never itself block an operation.
- **Added** `episteme inject [path] [--no-strict]` CLI command — deploys cognitive enforcement to any repository in one command: creates `.episteme/strict-surface` (hard-block mode) and a blank reasoning-surface template. Default: strict. Closes onboarding friction gap.
- **Added** `episteme log [--limit N] [--blocked]` CLI command — reads `~/.episteme/audit.jsonl` and renders a formatted time-series audit table with 🟢/🟡/🔴 action indicators. Closes observability gap.
- **Bumped** `plugin.json` version to `0.6.0`.
- **Added** `?` / `help [subcommand]` CLI aliases — `episteme ?` and `episteme help sync` both resolve to the correct help output.

Rationale: 0.6.0 established the philosophical control plane. 0.7.0 makes it physically enforceable and observable. The hook now produces a real block (exit 2) when strict mode is active — not advisory text. The audit log turns governance from "trust the agent read the markdown" into "here is every check, timestamped." The inject command reduces onboarding from sync + setup + survey to one command for any repo that needs immediate coverage.

Architectural gap still open: enforcement scope is currently limited to Claude Code's PreToolUse hook surface. A cross-runtime MCP proxy daemon that intercepts tool calls regardless of LLM runtime is the next level.

## [0.6.0] — 2026-04-19 — Epistemic control plane, DbC framing, zero-trust positioning

- **Fixed** `.claude-plugin/marketplace.json` schema: `plugins[0].source` was `"."` (invalid relative path); corrected to `"https://github.com/junjslee/episteme"`. Plugin is now installable via `/plugin marketplace add junjslee/episteme`.
- **Removed** `src/episteme/viewer/index.html` — deprecated UI artifact; `episteme viewer` CLI command remains.
- **Reframed** `README.md` opening with explicit governance positioning: episteme as a *deterministic control plane* and *epistemic policy engine*, not just a workflow tool. Added feedforward-vs-feedback contrast, DbC contract framing (Preconditions / Postconditions / Invariants), and OPA analogy.
- **Added** "Zero-trust execution" section to `README.md`: maps OWASP Agentic AI Top 10 risks to Reasoning Surface counters (prompt injection → Core Question gate, overreach → constraint regime, hallucination → mandatory Unknowns, infinite loops → Disconfirmation).
- **Added** "Human prompt debugging" section to `README.md`: frames the Knowns/Unknowns mapping as a mechanism for exposing logical gaps in the *user's original intent* before execution proceeds.
- **Added** interoperability statement and control-plane architecture diagram placeholder to `README.md`.
- **Added** Cynefin problem-domain classification table to `KERNEL_LIMITS.md`: requires agents to classify Clear / Complicated / Complex / Chaotic before populating the Reasoning Surface. Closes the most common misuse pattern—running analysis loops on Complex domains.
- **Updated** `.github/ISSUE_TEMPLATE/feature.yml`: added "Epistemic alignment" field requiring proposers to address kernel-principle impact, failure-mode mapping, and layer placement (kernel vs. profile vs. adapter). Replaced generic acceptance-criteria placeholder with falsifiable, disconfirmation-aware template.

Rationale: 0.5.0 made the system installable and demonstrable. 0.6.0 makes it *legible to engineers and systems thinkers*—the governance positioning, DbC contract model, and zero-trust framing translate the epistemic depth into language that maps to existing infrastructure-safety intuitions. The Cynefin addition closes a real misuse gap: structured deliberation is only correct for Complicated domains; Complex domains need probes, not plans.

## [0.5.0] — 2026-04-19 — Posture framing, installability, differential proof

- **Reframed** the top-of-repo lede and delivery pitch around *epistemic posture*. Added [`docs/POSTURE.md`](../docs/POSTURE.md) as the canonical statement of what episteme installs (texture of thought / texture of action / rationale). README lede now reads "episteme installs an epistemic posture."
- **Published** [`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json) and updated [`plugin.json`](../.claude-plugin/plugin.json) with explicit `agents`, `skills`, and `hooks` discovery paths. Added [`hooks/hooks.json`](../hooks/hooks.json) using `${CLAUDE_PLUGIN_ROOT}` so the plugin is portable. Repo is now `/plugin marketplace add junjslee/cognitive-os`-installable from any machine.
- **Added** [`INSTALL.md`](../INSTALL.md) — the three install paths (marketplace one-liner, full clone + CLI, dev `--plugin-dir`).
- **Added** [`demos/03_differential/`](../demos/03_differential/) — same prompt, posture off vs. on, with a [`DIFF.md`](../demos/03_differential/DIFF.md) analysis of what the posture changed. Scenario: a PM asks for a 2-sprint semantic-search scope; posture-off answers *how*, posture-on answers *whether*. Named failure modes caught: question substitution, WYSIATI, anchoring, planning fallacy, overconfidence.
- **Added** `episteme capture` CLI command ([`src/episteme/capture.py`](../src/episteme/capture.py)) — drafts a reasoning-surface.json skeleton from unstructured text (Slack thread, PR, ticket, email). Extracts Knowns / Unknowns / Assumptions via declared heuristics; leaves `disconfirmation[]` intentionally empty because the operator must declare it. Closes the "capture ergonomics" adoption-friction gap.

Rationale: the prior release (0.4.0) landed the substrate bridge, benchmark, plugin scaffolding, local viewer, and a second demo. This release makes the product *pitchable* (posture framing), *installable* (marketplace manifest + portable hooks), and *differentially provable* (the off-vs-on demo). The capture CLI is the first real ergonomics primitive — the Reasoning Surface stops being a blank JSON file and starts being a 5-minute edit.

## [0.4.0] — 2026-04-19 — Substrate bridge, benchmark, plugin scaffolding, viewer, demo 02

- **Added** pluggable substrate bridge ([`docs/SUBSTRATE_BRIDGE.md`](../docs/SUBSTRATE_BRIDGE.md), `src/episteme/bridges/substrate/`) with three reference adapters (`noop`, `mem0`, `memori`). Contract: `global` memory never routes, `skipped ≠ failed`, provenance sacred when supported.
- **Added** [`benchmarks/kernel_v1/`](../benchmarks/kernel_v1/) — 20-prompt deterministic scorer with pre-declared disconfirmation target and strict scoring mode. First run: 18/20 strict (0.9), two modes flagged below the 0.70 per-mode bar. Honest partial PASS with integrity caveats documented.
- **Added** [`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json) and plugin README (marketplace scaffolding).
- **Added** `episteme viewer` — stdlib-only local dashboard over the repo on 127.0.0.1:37776.
- **Added** [`demos/02_debug_slow_endpoint/`](../demos/02_debug_slow_endpoint/) — posture applied to a realistic p95 regression (DROP INDEX hidden in a rename migration). The fluent-wrong "add a Redis cache" answer rejected at the Core Question gate.

## [0.3.0] — 2026-04-19 — Attribution, boundary, and summary

- **Added** `kernel/SUMMARY.md` — 30-line operational distillation loaded first by agents.
- **Added** `kernel/KERNEL_LIMITS.md` — six conditions under which the kernel is the wrong tool, plus four declared structural gaps (calibration telemetry, profile staleness, multi-operator mode, tacit/explicit trade-off).
- **Added** operational summaries to each kernel file (two-tier structure: 5–7 line agent-efficient summary above full essay).
- **Expanded** `kernel/REFERENCES.md` from 4 to 14 primary citations with concept→wording maps; 15+ secondary sources documented. Primary additions: Popper, Shannon, Argyris & Schön, Alexander, Polanyi, Graham/Taleb, Pearl, Simon, Deming, Meadows.
- **Added** inline attribution footers to `CONSTITUTION.md`, `REASONING_SURFACE.md`, `FAILURE_MODES.md`.
- **Linked** `KERNEL_LIMITS.md` from `CONSTITUTION.md`'s "what it is not" section.

Rationale: a kernel whose claims cannot be traced to primary sources is unfalsifiable at the source-of-ideas level. A kernel without a declared boundary is a creed. Both gaps closed in this version.

## [0.2.0] — 2026-03 — Kernel extraction

- **Separated** `kernel/` from runtime and adapter code. Pure markdown; vendor-neutral.
- **Added** `CONSTITUTION.md`, `REASONING_SURFACE.md`, `FAILURE_MODES.md`, `OPERATOR_PROFILE_SCHEMA.md`, `HOOKS_MAP.md`, `MANIFEST.sha256`.

## [0.1.0] — 2026-02 — First principles

- Initial four-principle statement and six-failure-mode taxonomy.
- Workflow loop: Frame → Decompose → Execute → Verify → Handoff.

---

## How to edit this file

- Propose kernel changes as a version entry here *before* editing the kernel files.
- Reference the Evolution Contract (`docs/EVOLUTION_CONTRACT.md`) for the propose → critique → gate → promote flow on load-bearing changes.
- The current version number is mirrored in `MANIFEST.sha256` generation.
