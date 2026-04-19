# Kernel Changelog

Versioned history of the cognitive-os kernel. The kernel is a contract;
changes to it are load-bearing for every adapter and every operator
profile downstream. This file is the audit trail.

Format: `[version] — date — change`. Versions follow semantic intent:
- **major** — a principle added, removed, or reframed.
- **minor** — a new artifact or schema field.
- **patch** — clarifications, attribution, boundary statements.

---

## [0.5.0] — 2026-04-19 — Posture framing, installability, differential proof

- **Reframed** the top-of-repo lede and delivery pitch around *epistemic posture*. Added [`docs/POSTURE.md`](../docs/POSTURE.md) as the canonical statement of what cognitive-os installs (texture of thought / texture of action / rationale). README lede now reads "cognitive-os installs an epistemic posture."
- **Published** [`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json) and updated [`plugin.json`](../.claude-plugin/plugin.json) with explicit `agents`, `skills`, and `hooks` discovery paths. Added [`hooks/hooks.json`](../hooks/hooks.json) using `${CLAUDE_PLUGIN_ROOT}` so the plugin is portable. Repo is now `/plugin marketplace add junjslee/cognitive-os`-installable from any machine.
- **Added** [`INSTALL.md`](../INSTALL.md) — the three install paths (marketplace one-liner, full clone + CLI, dev `--plugin-dir`).
- **Added** [`demos/03_differential/`](../demos/03_differential/) — same prompt, posture off vs. on, with a [`DIFF.md`](../demos/03_differential/DIFF.md) analysis of what the posture changed. Scenario: a PM asks for a 2-sprint semantic-search scope; posture-off answers *how*, posture-on answers *whether*. Named failure modes caught: question substitution, WYSIATI, anchoring, planning fallacy, overconfidence.
- **Added** `cognitive-os capture` CLI command ([`src/cognitive_os/capture.py`](../src/cognitive_os/capture.py)) — drafts a reasoning-surface.json skeleton from unstructured text (Slack thread, PR, ticket, email). Extracts Knowns / Unknowns / Assumptions via declared heuristics; leaves `disconfirmation[]` intentionally empty because the operator must declare it. Closes the "capture ergonomics" adoption-friction gap.

Rationale: the prior release (0.4.0) landed the substrate bridge, benchmark, plugin scaffolding, local viewer, and a second demo. This release makes the product *pitchable* (posture framing), *installable* (marketplace manifest + portable hooks), and *differentially provable* (the off-vs-on demo). The capture CLI is the first real ergonomics primitive — the Reasoning Surface stops being a blank JSON file and starts being a 5-minute edit.

## [0.4.0] — 2026-04-19 — Substrate bridge, benchmark, plugin scaffolding, viewer, demo 02

- **Added** pluggable substrate bridge ([`docs/SUBSTRATE_BRIDGE.md`](../docs/SUBSTRATE_BRIDGE.md), `src/cognitive_os/bridges/substrate/`) with three reference adapters (`noop`, `mem0`, `memori`). Contract: `global` memory never routes, `skipped ≠ failed`, provenance sacred when supported.
- **Added** [`benchmarks/kernel_v1/`](../benchmarks/kernel_v1/) — 20-prompt deterministic scorer with pre-declared disconfirmation target and strict scoring mode. First run: 18/20 strict (0.9), two modes flagged below the 0.70 per-mode bar. Honest partial PASS with integrity caveats documented.
- **Added** [`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json) and plugin README (marketplace scaffolding).
- **Added** `cognitive-os viewer` — stdlib-only local dashboard over the repo on 127.0.0.1:37776.
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
