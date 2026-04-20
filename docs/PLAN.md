# Plan

Current active plan for episteme development.

**Core Question (this cycle):** Now that v0.10.0 ships stateful interception + a deterministic friction analyzer + a profile freshness gate, what is the smallest remaining gap that prevents episteme from being the reference governance layer any agent platform can adopt?

**Constraint regime:**
- Allowed: augmenting kernel docs, README, issue templates, ops docs, schema additions that extend (not reframe) existing invariants
- Forbidden: modifying `templates/` or `labs/` scaffolds; breaking kernel invariants without Evolution Contract
- Kernel changes require `kernel/CHANGELOG.md` entry first

---

## Active milestone: 0.11.0 — Kernel depth + personalization + memory architecture (in flight)

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
| 11 | Implementation: semantic-tier promotion job (deterministic; runs on demand as `episteme memory promote`). Episodic cluster detection (keyword + domain marker + action-class match is enough for first pass) → semantic proposal into reflective tier; never auto-writes to semantic without explicit review flag. Borrows structure from `episteme evolve friction`. | not started |
| 12 | Implementation: profile-audit loop — compares claimed axis values against episodic evidence; flags drift for operator re-elicitation. Counters measure-as-target drift operationally, not just by doc. Unblocks meaningful interpretation of the 5 axes currently marked `inferred` in the maintainer's profile. | not started |
| 13 | `kernel/CHANGELOG.md` 0.11.0 entry. Version reconcile across `pyproject.toml`, `plugin.json`, `marketplace.json`. | not started |
| 14 | `kernel/MANIFEST.sha256` regenerated (`episteme kernel update`) after all kernel edits land. | not started |

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
