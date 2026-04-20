# Next Steps

Exact next actions, in priority order. Update this file at every handoff.

---

## Immediate (0.9.0 remainder)

1. **Record the Strict Mode demo GIF** — first maintainer to run it produces `docs/assets/strict_mode_demo.gif` and `.cast`. Instructions in [`docs/CONTRIBUTING.md`](./CONTRIBUTING.md#recording-the-strict-mode-demo). Budget ≤ 2 MB, ~30 s.
2. **Add `last_elicited` timestamp** to operator profile schema (Gap B). Lowest-risk schema extension — additive field, no adapter break.
3. **Replace ASCII control-plane diagram** in `README.md` with SVG. Concept already defined; asset production only.
4. **First telemetry pass review** — after ~1 week of real use, scan `~/.episteme/telemetry/` and answer: do predictions and outcomes pair reliably? Is `tool_use_id` present in both halves? Do any legitimate commands show up repeatedly blocked (FP signal)? Feed back into Phase 4 tuning if FPs surface.

## Short-term (0.9.0 remainder)

- `tacit-call` decision marker in Reasoning Surface schema (Gap D)
- Cynefin domain classification field in `reasoning-surface.json` (companion to KERNEL_LIMITS.md addition)

## Medium-term (roadmap)

- Multi-operator mode design (Gap C) — deferred past 0.9.0; requires profile schema rework.
- Cross-runtime MCP proxy daemon — unblocks write-then-execute interception; blocked on telemetry-informed demand evidence.

## Architectural bypass vectors — remaining open

After the 0.9.0-entry hardening, the guard now handles: backtick substitution, `eval $VAR` indirection, and shell-script execution (`./x.sh`, `bash x.sh`, `source x.sh`) with a 64 KB content scan. These remain open:

1. **Write-then-execute across calls.** Agent writes `run.sh` via `Write`, then runs it via `Bash`. Individually neither call is high-impact. Requires cross-call state persisted between `PreToolUse` invocations — not achievable in a stateless single-call hook. Candidate for the cross-runtime MCP proxy daemon (0.10+).
2. **Dynamic shell assembly.** `A=git; B=push; $A $B` assembles the command at runtime from tokens that individually don't trip any pattern. Closing this requires a lightweight shell parser (risks correctness regressions) or a deny-by-default policy on `eval`/`$()`/backticks (breaks legitimate automation, and we already block `eval $VAR`). Deferred pending cost/benefit review.
3. **Scripts larger than 64 KB.** The scanner truncates at 64 KB; high-impact ops in bytes 64k..∞ of a single script are missed. Raising the cap increases hook latency and creates a DoS surface on pathologically large files. Accepted tradeoff until a real-world FN is reported.
4. **Scripts produced at runtime.** Agents who write a `.sh` in a `Write` call immediately followed by `bash ./that.sh` are caught by the current scan (the file exists at scan time). But scripts generated via `echo "…" > run.sh && bash run.sh` *in a single Bash call* — the scan reads the old file, or none — are a residual gap. Handled partially by item 1's cross-call state.

---

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
