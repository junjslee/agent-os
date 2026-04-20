# Contributing to episteme

Short version:

1. Read `AGENTS.md` (the operational contract) and `kernel/SUMMARY.md` (30-line kernel distillation).
2. Work in a branch — `feat/<name>`, `fix/<name>`, `docs/<name>`.
3. For substantive changes, update `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/NEXT_STEPS.md` in the same PR.
4. `PYTHONPATH=. pytest -q` must pass before you ask for review.
5. Kernel changes follow `docs/EVOLUTION_CONTRACT.md` — major shifts go through propose → critique → gate → promote.

Everything below is the "how-to" for recurring maintainer tasks that aren't covered by the code itself.

---

## Recording the Strict Mode demo

The README embeds `docs/assets/strict_mode_demo.gif` as a 30-second "show, don't tell" proof that Strict Mode blocks lazy surfaces. To refresh it after a hook change:

### 1. Install the recording toolchain

```bash
# macOS
brew install asciinema agg

# Debian/Ubuntu
sudo apt install asciinema
cargo install --git https://github.com/asciinema/agg
```

- `asciinema` records a terminal session as a `.cast` file (JSON, tiny).
- `agg` renders `.cast` to an animated GIF without a browser in the loop.

### 2. Record the script

The demo script is hermetic — it runs in a tempdir and never touches a real remote. Record from the repo root:

```bash
cd ~/episteme
asciinema rec -c ./scripts/demo_strict_mode.sh docs/assets/strict_mode_demo.cast
```

The script auto-paces with `sleep` calls (tunable via `DEMO_PAUSE=<seconds>`). Do not override the pauses during recording — the default cadence is tuned for readability.

> **Heads-up:** running `bash ./scripts/demo_strict_mode.sh` will itself trip the Reasoning Surface guard (the script-scan heuristic reads the file, finds `git push`, and enforces the surface on your repo's cwd). That is working-as-intended. Make sure `.episteme/reasoning-surface.json` in your cwd is fresh (< 30 min old, valid) before you start recording.

### 3. Render to GIF

```bash
agg docs/assets/strict_mode_demo.cast docs/assets/strict_mode_demo.gif \
  --cols 92 --rows 28 --font-size 16 --theme monokai
```

Target size: ≤ 2 MB, ~30 seconds, readable at 1x on GitHub without zoom. If the GIF exceeds that budget, drop `--font-size` or re-record with a shorter `DEMO_PAUSE`.

### 4. Commit both artifacts

Commit the `.cast` file alongside the `.gif` — the cast is the source of truth, the GIF is the rendered artifact.

```bash
git add docs/assets/strict_mode_demo.cast docs/assets/strict_mode_demo.gif
git commit -m "docs: refresh strict-mode demo GIF"
```

---

## Updating calibration telemetry analysis

`~/.episteme/telemetry/YYYY-MM-DD-audit.jsonl` is operator-local and never transmitted. Each day-file interleaves `event: "prediction"` (PreToolUse) and `event: "outcome"` (PostToolUse) records, joined by `correlation_id`. When writing analysis tools:

- Never upload raw telemetry to a public artifact; it contains command lines and cwd paths.
- Match prediction ↔ outcome by `correlation_id` first; fall back to `(command_executed, cwd, ts-second)` only if `correlation_id` mismatch is observed on a specific runtime.
- A prediction without a matching outcome within the same day-file is expected when a Bash call is canceled or the PostToolUse hook misses — treat it as "prediction made, outcome unobservable," not "outcome negative."

---

## Further reading

- `AGENTS.md` — operational contract and prohibited patterns
- `kernel/CONSTITUTION.md` — the four principles
- `kernel/FAILURE_MODES.md` — six named failure modes ↔ counter artifacts
- `docs/EVOLUTION_CONTRACT.md` — how the kernel itself evolves
- `docs/MEMORY_CONTRACT.md` — what goes in repo memory vs operator memory
