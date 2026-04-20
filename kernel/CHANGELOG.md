# Kernel Changelog

Versioned history of the episteme kernel. The kernel is a contract;
changes to it are load-bearing for every adapter and every operator
profile downstream. This file is the audit trail.

Format: `[version] — date — change`. Versions follow semantic intent:
- **major** — a principle added, removed, or reframed.
- **minor** — a new artifact or schema field.
- **patch** — clarifications, attribution, boundary statements.

---

## [0.7.0] — 2026-04-19 — Real enforcement: audit log, inject command, strict blocking

- **Added** `_write_audit()` to `core/hooks/reasoning_surface_guard.py` — every reasoning-surface check (passed / advisory / blocked) now writes a structured entry to `~/.episteme/audit.jsonl`. Audit failure is silenced so it can never itself block an operation.
- **Added** `episteme inject [path] [--no-strict]` CLI command — deploys cognitive enforcement to any repository in one command: creates `.episteme/strict-surface` (hard-block mode) and a blank reasoning-surface template. Default: strict. Closes onboarding friction gap.
- **Added** `episteme log [--limit N] [--blocked]` CLI command — reads `~/.episteme/audit.jsonl` and renders a formatted time-series audit table with 🟢/🟡/🔴 action indicators. Closes observability gap.
- **Bumped** `plugin.json` version to `0.6.0`.
- **Added** `?` / `help [subcommand]` CLI aliases — `episteme ?` and `episteme help sync` both resolve to the correct help output.

Rationale: 0.6.0 established the philosophical control plane. 0.7.0 makes it physically enforceable and observable. The hook now produces a real block (exit 2) when strict mode is active — not advisory text. The audit log turns governance from "trust the agent read the markdown" into "here is every check, timestamped." The inject command reduces onboarding from sync + setup + survey to one command for any repo that needs immediate coverage.

Architectural gap still open: enforcement scope is currently limited to Claude Code's PreToolUse hook surface. A cross-runtime MCP proxy daemon that intercepts tool calls regardless of LLM runtime is the next level.

## [0.6.0] — 2026-04-19 — Epistemic control plane, DbC framing, zero-trust positioning

- **Fixed** `.claude-plugin/marketplace.json` schema: `plugins[0].source` was `"."` (invalid relative path); corrected to `"https://github.com/junjslee/cognitive-os"`. Plugin is now installable via `/plugin marketplace add junjslee/cognitive-os`.
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
