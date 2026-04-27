# Contributing to episteme

Short version:

1. Read `AGENTS.md` (the operational contract) and `kernel/SUMMARY.md` (30-line kernel distillation).
2. Work in a branch — `feat/<name>`, `fix/<name>`, `docs/<name>`.
3. For substantive changes, include narrative context (what changed, why, expected impact) in the PR description. The maintainer integrates this into the project's private operational state — external contributors do not need to update operational docs themselves.
4. `PYTHONPATH=. pytest -q` must pass before you ask for review.
5. Kernel changes follow `docs/EVOLUTION_CONTRACT.md` — major shifts go through propose → critique → gate → promote.

Everything below is the "how-to" for recurring maintainer tasks that aren't covered by the code itself.

---

## Recording the hero demo

The README embeds `docs/assets/demo_posture.gif` as the hero — a four-act **Cognitive Cascade** (Blueprint B fence reconstruction → Blueprint D architectural cascade → Pillar 3 active guidance). To refresh after a hook or narrative change:

### 1. Install the recording toolchain

```bash
# macOS
brew install asciinema agg

# Debian/Ubuntu
sudo apt install asciinema
cargo install --git https://github.com/asciinema/agg
```

### 2. Record the script

`scripts/demo_posture.sh` is cinematic — all kernel output is simulated, so it runs in any clean bash environment. Record from the repo root:

```bash
asciinema rec --cols 100 --rows 32 --idle-time-limit 2 \
  -c ./scripts/demo_posture.sh \
  docs/assets/demo_posture.cast
```

### 3. Render to GIF at 0.8× playback

```bash
agg --speed 0.8 --cols 100 --rows 32 --font-size 15 --theme monokai \
  docs/assets/demo_posture.cast docs/assets/demo_posture.gif
```

Keep it under ~2 MB — readable at 1x on GitHub without zoom, fast to load in the README hero.

### 4. Commit both artifacts

```bash
git add docs/assets/demo_posture.cast docs/assets/demo_posture.gif
git commit -m "docs: refresh hero demo GIF"
```

> The earlier `scripts/demo_strict_mode.sh` script remains runnable for ad-hoc local demos of the blocking path, but its rendered GIF is no longer shipped — the Cognitive Cascade supersedes it as the product hero.

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
