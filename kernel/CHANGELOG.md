# Kernel Changelog

Versioned history of the cognitive-os kernel. The kernel is a contract;
changes to it are load-bearing for every adapter and every operator
profile downstream. This file is the audit trail.

Format: `[version] — date — change`. Versions follow semantic intent:
- **major** — a principle added, removed, or reframed.
- **minor** — a new artifact or schema field.
- **patch** — clarifications, attribution, boundary statements.

---

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
