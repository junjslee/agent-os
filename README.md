# cognitive-os

> **cognitive-os installs an epistemic posture.** The artifacts are how the posture becomes enforceable. Markdown. Vendor-neutral. The kernel outlives the tooling.

A *posture* is how a reasoner holds themselves before a decision: which questions get asked, which unknowns get named, which options are pre-rejected, and which conditions force a pivot. Tools and memory stores cycle every 18–36 months — the posture does not. `cognitive-os` is the layer that installs the posture once and delivers it into every runtime and substrate you use.

**[What this installs →](./docs/POSTURE.md)** · **[Differential demo (off vs on) →](./demos/03_differential/)** · **[Install as plugin →](./.claude-plugin/README.md)** · **[Quick start ↓](#quick-start)**

---

## I want to… → do this

| Goal                                                | Command / pointer                                                   |
|-----------------------------------------------------|---------------------------------------------------------------------|
| Understand what this is in 3 minutes                | [`docs/POSTURE.md`](./docs/POSTURE.md) · [`kernel/SUMMARY.md`](./kernel/SUMMARY.md) |
| See the posture *off vs on* on the same prompt      | [`demos/03_differential/`](./demos/03_differential/)                |
| See what it produces end-to-end                     | [`demos/01_attribution-audit/`](./demos/01_attribution-audit/) · [`demos/02_debug_slow_endpoint/`](./demos/02_debug_slow_endpoint/) |
| Install as a Claude Code plugin (one line)          | `/plugin marketplace add junjslee/cognitive-os`                     |
| Install on my machine (CLI + editable kernel)       | `pip install -e . && cognitive-os init` — see [`INSTALL.md`](./INSTALL.md) |
| Draft a reasoning surface from a Slack thread       | `cognitive-os capture --input thread.txt --output surface.json`    |
| Sync identity to every AI tool I use                | `cognitive-os sync`                                                 |
| Encode working style + reasoning posture            | `cognitive-os setup . --interactive`                                |
| Apply the right harness for my project type         | `cognitive-os detect . && cognitive-os harness apply <type> .`      |
| Know when *not* to use this kernel                  | [`kernel/KERNEL_LIMITS.md`](./kernel/KERNEL_LIMITS.md)              |
| Find attribution for any borrowed concept           | [`kernel/REFERENCES.md`](./kernel/REFERENCES.md)                    |
| Audit my setup                                      | `cognitive-os doctor`                                               |

---

## See it in 60 seconds

Three demos, increasing in what they prove:

- [`demos/01_attribution-audit/`](./demos/01_attribution-audit/) — canonical four-artifact shape (reasoning-surface → decision-trace → verification → handoff). The kernel applied to itself, auditing whether every borrowed concept is traceable to a primary source.
- [`demos/02_debug_slow_endpoint/`](./demos/02_debug_slow_endpoint/) — posture applied to a realistic p95 regression. The fluent-wrong "add a cache" answer rejected at the Core Question gate.
- [`demos/03_differential/`](./demos/03_differential/) — **same prompt, posture off vs. on**. The demo that converts skeptics: a PM asks for a 2-sprint semantic-search scope; off answers *how*, on answers *whether*. [`DIFF.md`](./demos/03_differential/DIFF.md) shows which failure modes the posture caught.

Open any of the three. You will know what cognitive-os produces before reading any philosophy.

---

## The lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                         operator (you)                              │
│           ├── cognitive preferences   ├── working style             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                    cognitive-os sync
                               │
      ┌────────────────────────┼────────────────────────┐
      ▼                        ▼                        ▼
 Claude Code             Hermes (OMO)            future adapter
 (CLAUDE.md)             (OPERATOR.md)           (same kernel)
      │                        │                        │
      └────────────────────────┼────────────────────────┘
                               │
                       per-session loop
                               │
      ┌────────┬────────┬──────┴─────┬────────┬────────┐
      ▼        ▼        ▼            ▼        ▼        ▼
    FRAME → DECOMPOSE → EXECUTE → VERIFY → HANDOFF → (next session)
      │                                        │
      │ Reasoning Surface                      │ docs/PROGRESS.md
      │ (Knowns / Unknowns /                   │ docs/NEXT_STEPS.md
      │  Assumptions / Disconfirmation)        │ decision artifact
      │                                        │
      └────────────── feedback ────────────────┘
```

Every element is the operational form of a kernel principle. The loop is the unit of progress (IV). Orientation precedes observation (II). Knowns/Unknowns/Assumptions/Disconfirmation are explicit before action (I). Multiple lenses are required at high-impact decisions (III).

---

## The kernel

Start at **[`kernel/`](./kernel/)**. Pure markdown. No code. No vendor lock-in.

| File                                                              | What it defines                                              |
|-------------------------------------------------------------------|--------------------------------------------------------------|
| [`SUMMARY.md`](./kernel/SUMMARY.md)                               | 30-line operational distillation                             |
| [`CONSTITUTION.md`](./kernel/CONSTITUTION.md)                     | Root claim, four principles, six failure modes               |
| [`REASONING_SURFACE.md`](./kernel/REASONING_SURFACE.md)           | Knowns / Unknowns / Assumptions / Disconfirmation protocol   |
| [`FAILURE_MODES.md`](./kernel/FAILURE_MODES.md)                   | Six fluent-agent failure modes ↔ counter artifacts           |
| [`OPERATOR_PROFILE_SCHEMA.md`](./kernel/OPERATOR_PROFILE_SCHEMA.md) | Schema for encoding an operator's cognitive preferences   |
| [`KERNEL_LIMITS.md`](./kernel/KERNEL_LIMITS.md)                   | When the kernel is the wrong tool; declared gaps             |
| [`REFERENCES.md`](./kernel/REFERENCES.md)                         | Attribution for every load-bearing borrowed concept          |
| [`CHANGELOG.md`](./kernel/CHANGELOG.md)                           | Versioned kernel history                                     |

Authority hierarchy: **project docs > operator profile > kernel defaults > runtime defaults.** Specific beats general.

---

## System overview

<p align="center">
  <img src="docs/assets/system-overview.svg" alt="cognitive-os system overview" width="100%" />
</p>

Structural stack: kernel (philosophy) → operator profile (personalization) → adapters (delivery) → runtime (execution).

---

## Quick start

```bash
git clone https://github.com/junjslee/cognitive-os ~/cognitive-os
cd ~/cognitive-os
pip install -e .

cognitive-os init              # generate personal memory files from templates
cognitive-os setup . --write   # score working style + reasoning posture
cognitive-os sync              # push identity to every adapter
cognitive-os doctor            # verify wiring
```

Project-type harness:

```bash
cognitive-os detect .                         # analyze repo, recommend a harness
cognitive-os harness apply ml-research .      # apply it
cognitive-os new-project . --harness auto     # scaffold + auto-detect
```

Deep-dive onboarding modes, scored dimensions, and defaults: **[`docs/SETUP.md`](./docs/SETUP.md)**.

---

## How cognitive-os compares

Most tools in this space either build agent runtimes or provide memory APIs for applications. `cognitive-os` augments the developer tools you already use.

| Axis                  | cognitive-os                                      | Memory APIs (mem0, OpenMemory)  | Agent runtimes (Agno, opencode, omo) |
|-----------------------|---------------------------------------------------|---------------------------------|--------------------------------------|
| **What it is**        | Identity + governance layer across dev tools      | Memory API embedded in an app   | A runtime that executes agents       |
| **Where identity lives** | Governed markdown + JSON, cross-tool, versioned | Vector/graph store, per app     | System prompt per session            |
| **Sync**              | One command, all tools                            | N/A                             | N/A (per-project config)             |

The gap cognitive-os fills: no other project syncs a *governed identity + cognitive contract* across multiple developer AI tools in one command. Runtimes and memory APIs own different lanes; cognitive-os sits above them and makes them aware of *who you are* and *how you think*.

---

## Repository layout

```
cognitive-os/
├── kernel/                     philosophy (markdown; travels across runtimes)
├── demos/                      end-to-end reference deliverables
├── core/
│   ├── memory/global/          operator memory (gitignored; personal)
│   ├── hooks/                  deterministic safety + workflow hooks
│   ├── harnesses/              per-project-type operating environments
│   └── schemas/                memory + evolution contract schemas
├── adapters/                   kernel delivery layers (Claude Code, Hermes, …)
├── skills/                     reusable operator skills
├── templates/                  project scaffolds, example answer files
├── docs/                       runtime docs, architecture, contracts
├── src/cognitive_os/           CLI + core library
└── tests/
```

Repo operating contract (for any agent working here): **[`AGENTS.md`](./AGENTS.md)**. LLM sitemap: **[`llms.txt`](./llms.txt)**.

---

## CLI surface

```bash
cognitive-os init
cognitive-os doctor
cognitive-os sync [--governance-pack minimal|balanced|strict]
cognitive-os new-project [path] --harness auto
cognitive-os detect [path]
cognitive-os harness apply <type> [path]
cognitive-os profile [survey|infer|hybrid] [path] [--write]
cognitive-os cognition [survey|infer|hybrid] [path] [--write]
cognitive-os setup [path] [--interactive] [--write] [--sync] [--doctor]
cognitive-os bridge anthropic-managed --input <events.json> [--dry-run]
cognitive-os bridge substrate [list-adapters|describe|verify|push|pull] ...
cognitive-os capture [--input <file>] [--output <file>] [--by <name>]
cognitive-os viewer [--host 127.0.0.1] [--port 37776]
cognitive-os evolve [run|report|promote|rollback] ...
```

Full reference: [`docs/README.md`](./docs/README.md).

---

## Why this architecture

- **Cross-tool consistency.** One authoritative operating contract across Claude Code, Hermes, and future adapters.
- **Deterministic setup.** Onboarding is explainable (`survey` / `infer` / `hybrid`) instead of implicit drift.
- **Hard authority boundary.** Repo docs + global memory are the source of truth; tool-native memories are acceleration, not authority.
- **Declared limits.** [`KERNEL_LIMITS.md`](./kernel/KERNEL_LIMITS.md) names when the kernel is the wrong tool. A discipline without a boundary is a creed.
- **Coexistence, not replacement.** Self-evolving runtimes adapt fast locally; durable lessons get promoted into authoritative files, then re-synced. Managed runtimes (execution substrate) and cognitive-os (control plane) are complementary.

Memory model, Memory Contract v1, Evolution Contract v1, and managed-runtime coexistence: **[`docs/SYNC_AND_MEMORY.md`](./docs/SYNC_AND_MEMORY.md)**.

---

## Read next

| Topic                                      | Where                                                            |
|--------------------------------------------|------------------------------------------------------------------|
| What cognitive-os installs (posture framing) | [`docs/POSTURE.md`](./docs/POSTURE.md)                         |
| Kernel distillation (30 lines)             | [`kernel/SUMMARY.md`](./kernel/SUMMARY.md)                       |
| What the kernel produces                   | [`demos/01_attribution-audit/`](./demos/01_attribution-audit/) · [`demos/02_debug_slow_endpoint/`](./demos/02_debug_slow_endpoint/) |
| Same prompt, posture off vs. on            | [`demos/03_differential/`](./demos/03_differential/)             |
| Install paths (marketplace, CLI, dev)      | [`INSTALL.md`](./INSTALL.md)                                     |
| Benchmark with disconfirmation target      | [`benchmarks/kernel_v1/`](./benchmarks/kernel_v1/)               |
| Substrate bridge (mem0, memori, noop)      | [`docs/SUBSTRATE_BRIDGE.md`](./docs/SUBSTRATE_BRIDGE.md)         |
| Profile + cognition setup                  | [`docs/SETUP.md`](./docs/SETUP.md)                               |
| Sync matrix, memory model, contracts       | [`docs/SYNC_AND_MEMORY.md`](./docs/SYNC_AND_MEMORY.md)           |
| Harness system                             | [`docs/HARNESSES.md`](./docs/HARNESSES.md)                       |
| Hook reference + governance packs          | [`docs/HOOKS.md`](./docs/HOOKS.md)                               |
| Skills + agent personas + provenance       | [`docs/SKILLS_AND_PERSONAS.md`](./docs/SKILLS_AND_PERSONAS.md)   |
| Personal customization (memory/hooks/skills) | [`docs/CUSTOMIZATION.md`](./docs/CUSTOMIZATION.md)             |
| Agent repo operating contract              | [`AGENTS.md`](./AGENTS.md)                                       |
| Architecture deep-dive                     | [`docs/COGNITIVE_OS_ARCHITECTURE.md`](./docs/COGNITIVE_OS_ARCHITECTURE.md) |
| Cognitive system playbook                  | [`docs/COGNITIVE_SYSTEM_PLAYBOOK.md`](./docs/COGNITIVE_SYSTEM_PLAYBOOK.md) |

---

## Push-readiness checklist

```bash
PYTHONPATH=. pytest -q tests/test_profile_cognition.py
python3 -m py_compile src/cognitive_os/cli.py
cognitive-os doctor
git status && git rev-list --left-right --count @{u}...HEAD
```
