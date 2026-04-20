# Plan

Current active plan for episteme development.

**Core Question (this cycle):** Now that Strict Mode is enforceable (0.8.1), what is the cheapest feedback loop that makes the cognitive contract *verifiable* over time — not just enforceable at the moment of execution?

**Constraint regime:**
- Allowed: augmenting kernel docs, README, issue templates, ops docs, schema additions that extend (not reframe) existing invariants
- Forbidden: modifying `templates/` or `labs/` scaffolds; breaking kernel invariants without Evolution Contract
- Kernel changes require `kernel/CHANGELOG.md` entry first

---

## Closed milestones

### 0.9.0-entry — Calibration telemetry + visual proof + bypass hardening — complete

- **Repository neutrality scrub** — `/Users/junlee` paths removed from `docs/PROGRESS.md`, `docs/NEXT_STEPS.md`, `docs/assets/setup-demo.svg`; `"operator": "junlee"` neutralized to `"default"` in `demos/01_attribution-audit/reasoning-surface.json`. `junjslee` GitHub URLs retained (intentional public identity).
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
