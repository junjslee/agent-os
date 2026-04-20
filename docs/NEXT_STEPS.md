# Next Steps

Exact next actions, in priority order. Update this file at every handoff.

---

## Immediate (0.11.0 — phases 9–10 landed, phases 11–14 to go)

Phases 1–10 of the 0.11.0 plan are complete. The v2 profile now modulates at least one hook (`disconfirmation_specificity_min`), and the memory layer has its first active writer (episodic tier). Phases 11–12 close the calibration loop; phases 13–14 package the release.

1. **Semantic-tier promotion job (`episteme memory promote`).** Deterministic CLI subcommand. Clusters similar episodic records (embedding-free first pass: keyword + domain marker + action-class match). Emits proposals into the reflective tier; never auto-writes to semantic without an explicit review flag. Borrows its structure from `episteme evolve friction` — same shape of tool, operating one tier up. Unblocks phase 12 (profile audit needs the semantic tier for pattern-stability signals).
2. **Profile-audit loop.** On-demand comparison of each claimed scored axis against the episodic record. Flags drift to the reflective tier; surfaces as a re-elicitation prompt at SessionStart. Operationalizes the *Audit Discipline* section of OPERATOR_PROFILE_SCHEMA.md. Without this loop, measure-as-target drift (failure mode 8) is named in docs but unchecked in running code. This is the loop that gives the 5 axes currently marked `inferred` in the maintainer's profile actual meaning — drift surfaces them for elicitation, rather than them silently decaying into defaults.
3. **`kernel/CHANGELOG.md` 0.11.0 entry** + version reconcile (`pyproject.toml`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`). Deferred until items 1–2 land so the changelog describes a delivered, not aspirational, version.
4. **`kernel/MANIFEST.sha256` regeneration** via `episteme kernel update`. Currently stale — `episteme doctor` emits drift warnings until regenerated. Run last so a single regen covers all 0.11 kernel edits.

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

## Closed in 0.11.0 (phases 1–10)

- **Phase 9 — profile becomes control signal.** New `core/hooks/_derived_knobs.py` (axis-to-knob derivation + reader/writer). `reasoning_surface_guard.py` replaces module-level `MIN_DISCONFIRMATION_LEN` / `MIN_UNKNOWN_LEN` constants with lookups against `~/.episteme/derived_knobs.json`, fallback 15. For the maintainer's v2 profile the minimum raises 15 → 27; an 18-char disconfirmation now fails, a 39-char passes. First end-to-end proof the v2 profile modulates hook behavior. 17 new tests.
- **Phase 10 — episodic-tier writer.** New PostToolUse hook `core/hooks/episodic_writer.py` fires on high-impact Bash pattern match; assembles a record per the `memory-contract-v1` schema (common.json + episodic_record.json); appends to `~/.episteme/memory/episodic/YYYY-MM-DD.jsonl`. Reasoning-Surface snapshot attached when present; secrets redacted before write; provenance confidence reflects available signal. Wired into `hooks/hooks.json` PostToolUse/Bash alongside `state_tracker` and `calibration_telemetry`, all async. Correlation-id algorithm mirrors calibration telemetry so records join. 19 new tests; end-to-end smoke-test verified a real record at `~/.episteme/memory/episodic/2026-04-20.jsonl`.
- **Operator profile v2 filled.** `core/memory/global/operator_profile.md` migrated. 6 process axes rescored 0–3 → 0–5. All 9 cognitive-style axes populated (3 flipped to `elicited` based on source-doc citations: `abstraction_entry`, `explanation_depth`, `asymmetry_posture`; 5 remain `inferred` pending phase-12 audit). Expertise map populated.
- **Test suite 121 → 157** (36 new). Zero regressions.

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
