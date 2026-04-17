# 🧠 cognitive-os
**Every AI agent starts as a blank slate. cognitive-os gives them a Soul.**

You use Claude Code, Codex CLI, opencode, Hermes. Each one starts cold. You repeat yourself every session. One agent knows your workflow; the next doesn't. A context reset wipes everything. Skills and preferences drift out of sync across tools.

`cognitive-os` is the missing operating layer. One repo that acts as the persistent cognitive contract for your entire AI stack — identity, memory, skills, safety hooks, and sync.

> Stop managing configuration files. Start managing your agent's consciousness.

---

## The problem with CLAUDE.md, AGENTS.md, and .cursorrules

These files are good for project-specific instructions. They're not enough on their own:

- **They're per-project.** Your cross-project identity, cognitive posture, and workflow defaults don't live anywhere durable.
- **They're per-tool.** CLAUDE.md means nothing to Codex. .cursorrules means nothing to Claude Code. You end up maintaining divergent files.
- **They're static.** No sync mechanism. No structure. No governance. If you update one, the others fall behind.
- **They have no memory layer.** No episodic trace, no provenance, no conflict semantics. Just flat text that agents forget after a reset.

`cognitive-os` wraps around these files and gives them a backbone. Your `CLAUDE.md` becomes an index into a governed memory system. Your `AGENTS.md` inherits from a global cognitive contract. Your `.cursorrules` gets supplemented with synced skills.

---

## How cognitive-os compares

Most tools in this space either build new agent runtimes or provide memory APIs for applications. `cognitive-os` does neither. It augments the developer tools you already use.

| | cognitive-os | Manual per-tool files | mem0 / OpenMemory | Agno (Phidata) | opencode / omo |
|---|---|---|---|---|---|
| **What it is** | Identity + governance layer for your dev tools | CLAUDE.md, AGENTS.md per project | Memory API / service for AI applications | Framework for building new agent apps | Open-source AI coding agent + community harness layer |
| **Approach** | Augments existing tools (Claude Code, Hermes) | Per-tool, per-project, manual | Embedded in application code | Replaces tools with new agent runtime | Agent runtime; community configs layered on top |
| **Target** | Developers who already use AI coding tools | Same, but with no sync mechanism | App developers embedding memory in products | Teams building new AI applications | Developers who want an open-source Claude Code alternative |
| **Memory** | Governed markdown + JSON schemas, authoritative | Flat markdown, no schema, no governance | Vector/graph store, API-managed | Runtime-managed per agent | Session-scoped, no persistent identity layer |
| **Identity** | Your profile, cognitive posture, cross-tool | One file per tool, diverges over time | Not a concept | Agent-level, defined per app | System prompt per session |
| **Sync** | One command, all tools | Manual copy-paste per tool | N/A | N/A | N/A (per-project config) |

The gap cognitive-os fills: no other project syncs a governed identity + cognitive contract across Claude Code and Hermes in one command. The manual approach (maintaining separate CLAUDE.md, AGENTS.md, and per-tool configs per project) is what most developers do today. That's what cognitive-os replaces. Additional adapters (Codex, opencode, Cursor, etc.) are a 50-line shim away — the kernel is vendor-neutral by design.

mem0 and Agno are strong in their lanes -- application memory and agent app building, respectively. They are not developer tool augmentation layers. opencode and omo are excellent runtimes; cognitive-os makes them aware of who you are and how you think.

If you want to keep using the tools you already have -- and just make them sharper, more consistent, and persistent -- that's `cognitive-os`.

---

## 🏛️ The Three Pillars

1. **Identity (The Soul):** Persistent global profiles that define *who* the agent is — cognitive posture, reasoning depth, challenge orientation, operator preferences.
2. **Context (The Harness):** Repo-specific operating environments that teach the agent *how* to think about your specific tech stack and constraints.
3. **Sync (The Vessel):** Automated delivery that propagates identity + context into every tool you use, every session.

---

## System Overview

<p align="center">
  <img src="docs/assets/system-overview.svg" alt="cognitive-os system overview" width="100%" />
</p>

System map source: `docs/assets/system-overview.svg`

Structure summary:
- Structural + operational stack defines roles and authority boundaries.
- Authoritative memory + policy defines what persists and how conflicts resolve.
- Workflow + evolution governs execution and safe improvement.
- `cognitive-os sync` propagates the same operating contract to Claude Code and Hermes.

---

## ⚡ Quick start

```bash
git clone https://github.com/junjslee/cognitive-os ~/cognitive-os
cd ~/cognitive-os
pip install -e .
cognitive-os init       # generate personal memory files from templates
cognitive-os sync       # push your identity to Claude Code and Hermes
cognitive-os doctor     # verify everything wired correctly
```

Expected output from `doctor`:
- `Awareness verified.`
- Claude Code and Hermes adapter checks shown as `[ok]` or `[info]`

### 60-second demo (profile + cognition + sync)

```bash
cognitive-os profile hybrid . --write     # score your work style
cognitive-os cognition survey --write     # encode your reasoning posture
cognitive-os sync                         # push to all agents
cognitive-os doctor                       # verify
```

Every agent you open now inherits your memory, skills, and governance hooks.

### Provision the right harness for your project type

```bash
cognitive-os detect .                          # analyze repo, recommend a harness
cognitive-os harness apply ml-research .       # apply it
# or in one shot:
cognitive-os new-project . --harness auto      # scaffold + auto-detect harness
```

---

## CLI command surface

```bash
cognitive-os init
cognitive-os doctor
cognitive-os sync [--governance-pack minimal|balanced|strict]
cognitive-os new-project [path] --harness auto
cognitive-os detect [path]
cognitive-os harness apply <type> [path]
cognitive-os profile [survey|infer|hybrid] [path] [--write]
cognitive-os cognition [survey|infer|hybrid] [path] [--write]
cognitive-os setup [path] [--interactive] [--governance-pack minimal|balanced|strict] [--write] [--sync] [--doctor]
cognitive-os bridge anthropic-managed --input <managed-events.json> [--project-id <id>] [--dry-run]
cognitive-os evolve [run|report|promote|rollback] ...
```

Full command reference: `docs/README.md`

| Task | Command |
|---|---|
| Initialize personal files | `cognitive-os init` |
| Push memory to all agents | `cognitive-os sync` |
| New project from scaffold | `cognitive-os new-project [path]` |
| Detect / apply harness | `cognitive-os detect` \| `harness apply <type>` |
| Deterministic onboarding | `cognitive-os setup . --interactive` |
| Verify system health | `cognitive-os doctor` |

---

## Why cognitive-os

You use multiple AI coding agents. Each one starts cold. You repeat yourself. Skills drift out of sync. One agent knows your workflow; another doesn't. A context reset wipes everything. Every project gets the same generic scaffold regardless of whether it's ML research on a GPU cluster or a React app on your laptop.

`cognitive-os` fixes this with a single repo that acts as the operating layer for your entire AI stack.

---

## Design principles

- cognitive-os operationalizes cognitive policy (how agents think) and execution policy (how agents act) into repeatable workflows.
- Authoritative project truth lives in repository docs (`AGENTS.md`, `docs/*`), not in any single agent tool.
- Global operator memory (cross-project) is separate from project memory (repo-local delivery context).
- Adapters (Claude Code, Hermes, others) are delivery mechanisms for the same operating contract, not separate authorities.
- Plugin or tool-native memory systems accelerate retrieval but don't replace authoritative records.

---

## Architecture at a glance

cognitive-os has four layers:

1) **Global operator layer** (`core/memory/global/*`)
- your stable workflow + cognitive defaults across projects

2) **Story layer** (`core/memory/global/build_story.md`, `docs/DECISION_STORY.md`)
- narratable what/why/how traces so decisions are replayable in your head and explainable to others

3) **Project truth layer** (`AGENTS.md`, `docs/*`)
- what this specific repo is building right now

4) **Adapter layer** (Claude Code, Hermes)
- delivery surfaces that consume the same contract

Adapters are not the authority. Repo docs + global memory are.

---

## Why this architecture wins

- Cross-tool consistency: one authoritative operating contract across Claude Code and Hermes.
- Deterministic setup: profile/cognition onboarding is explainable (`survey`/`infer`/`hybrid`) instead of implicit drift.
- Hard authority boundary: repo docs + global memory are the source of truth; tool-native memories are acceleration layers.

### Coexistence model (self-evolving agents)

`cognitive-os` is designed to work with agent runtimes that keep learning locally (Hermes memory/skills, Claude/Codex/Cursor local context):

1. Local runtime memory evolves fast during execution (high-velocity adaptation).
2. Durable lessons are promoted into authoritative files (`core/memory/global/*`, `docs/*`, reusable skills).
3. `cognitive-os sync` republishes that contract to every runtime.
4. Runtime-native memory remains a cache/acceleration layer, not the source of truth.

This gives you both: fast local learning and deterministic cross-platform consistency.

### Managed runtime positioning (Anthropic Managed Agents)

`cognitive-os` and managed runtimes are complementary by design.

- Managed runtime (e.g., Anthropic Managed Agents): execution substrate for long-horizon agent work — orchestration, sandbox/tool execution, durable runtime session/event logs.
- `cognitive-os`: cross-runtime cognitive control plane — identity, memory governance, authoritative docs, and deterministic policy sync across tools.

Practical model:
1. Run long tasks in a managed runtime.
2. Bridge managed session events into `cognitive-os` memory envelopes.
3. Promote durable lessons into authoritative global/project docs.
4. Sync the updated contract back to all local runtimes.

Result: runtime scale + reliability without sacrificing cross-tool continuity or source-of-truth discipline.

### Demo

Guided setup in one command:

![cognitive-os setup demo](docs/assets/setup-demo.svg)

---

## What gets synced

| Asset | Claude Code | Hermes | OMO / OMX |
|---|---|---|---|
| Global memory index (`CLAUDE.md`) | ✅ | — | — |
| Operator/cognitive/workflow source files (`core/memory/global/*.md`) | via include | composed into `OPERATOR.md` | — |
| Agent personas | ✅ | — | ✅ |
| Skills | ✅ | ✅ | ✅ |
| Lifecycle hooks | ✅ | — | ✅ |
| Authoritative context composite (`OPERATOR.md`) | — | ✅ | — |

Note: this matrix describes current adapter capabilities, not architectural authority. Authoritative truth remains in repository docs and global cognitive-os memory.

---

## Deterministic safety hooks (Claude adapter)

Hooks run deterministically — they can't be overridden by model behavior.

Governance packs for `sync`/`setup --sync`:
- `minimal`: baseline safety hooks only (`block_dangerous`, formatter/test/checkpoint/quality gate)
- `balanced` (default): `minimal` + workflow/context/prompt advisories
- `strict`: `balanced` + removes generic `PermissionRequest` auto-allow fallback while preserving custom permission hooks

| Hook | Event | What it does |
|---|---|---|
| `session_context.py` | `SessionStart` | Prints branch, git status, and `NEXT_STEPS.md` at session open |
| `block_dangerous.py` | `PreToolUse Bash` | Blocks `rm -rf`, `git reset --hard`, `git push --force`, `sudo`, `pkill`, and more |
| `workflow_guard.py` | `PreToolUse Write\|Edit\|MultiEdit` | Advisory nudge to keep `docs/PLAN.md`, `docs/PROGRESS.md`, and `docs/NEXT_STEPS.md` aligned with implementation edits |
| `prompt_guard.py` | `PreToolUse Write\|Edit\|MultiEdit` | Advisory detection of prompt-injection-like patterns when writing durable context files (`docs/`, `AGENTS.md`, `CLAUDE.md`) |
| `format.py` | `PostToolUse Write\|Edit` | Auto-runs `ruff` (Python) or `prettier` (JS/TS) after every file write |
| `test_runner.py` | `PostToolUse Write\|Edit` | Runs pytest / jest on the file if it's a test file |
| `context_guard.py` | `PostToolUse Bash\|Edit\|Write\|MultiEdit\|Agent\|Task` | Advisory warning when session context budget approaches compaction thresholds |
| `quality_gate.py` | `Stop` | Blocks completion if tests fail (opt-in via `.quality-gate` in project root) |
| `checkpoint.py` | `Stop` | Auto-commits uncommitted changes as `chkpt:` after every turn |
| `precompact_backup.py` | `PreCompact` | Backs up session transcripts before context compaction |

---

## Skills included

### Custom (your own)
`repo-bootstrap` · `requirements-to-plan` · `progress-handoff` · `worktree-split` · `bounded-loop-runner` · `review-gate` · `research-synthesis`

### Vendor (curated upstream)
`swing-clarify` · `swing-options` · `swing-research` · `swing-review` · `swing-trace` · `swing-mortem` · `create-prd` · `sprint-plan` · `pre-mortem` · `test-scenarios` · `prioritization-frameworks` · `retro` · `release-notes`

Add your own skills under `skills/custom/` — each skill is a folder with a `SKILL.md`.

---

## Agent personas included

Eleven subagent definitions installed into `~/.claude/agents/`:

Execution: `planner` · `researcher` · `implementer` · `reviewer` · `test-runner` · `docs-handoff`

Structural governance: `domain-architect` · `reasoning-auditor` · `governance-safety` · `orchestrator` · `domain-owner`

---

## Project scaffold

`cognitive-os new-project [path]` creates a standard project structure:

```
AGENTS.md            vendor-neutral operating manual for any agent
CLAUDE.md            Claude-native memory index
docs/
  REQUIREMENTS.md    what is being built
  PLAN.md            staged execution
  PROGRESS.md        completed work and decisions
  NEXT_STEPS.md      next-session handoff
  RUN_CONTEXT.md     runtime assumptions, APIs, execution profiles
  DECISION_STORY.md  narratable what/why/how for major decisions
.claude/
  settings.json      permission rules
  settings.local.json  machine-local overrides (gitignored)
```

---

## Read this next

- Governing philosophy: `docs/CONSTITUTION.md`
- Docs index: `docs/README.md`
- Architecture: `docs/COGNITIVE_OS_ARCHITECTURE.md`
- Cognitive System Playbook: `docs/COGNITIVE_SYSTEM_PLAYBOOK.md`

---

## Memory model

```
global memory (this repo)
└── stable cross-project context: who you are, how you work, safety policy, build narrative

project memory (each repo's docs/)
└── what is being built, current state, next handoff, decision story (what/why/how)

episodic memory (session/run traces)
└── observations, decisions, verification outcomes for replay and audit

plugin memory (claude-mem, etc.)
└── cache and retrieval — never the authoritative record
```

Global memory never belongs in chat. Project memory never belongs in global. Plugins help but don't replace either.

### Memory Contract v1 (schema + conflict semantics)

For portable integrations and deterministic reconciliation, `cognitive-os` defines a formal contract:
- Spec: `docs/MEMORY_CONTRACT.md`
- Schemas: `core/schemas/memory-contract/*.json`

Includes:
- required provenance fields (`source_type`, `source_ref`, `captured_at`, `captured_by`, `confidence`)
- explicit memory classes (`global`, `project`, `episodic`)
- conflict order (`project > global > episodic`, then status/recency/confidence, with human override)
- additive bridges for external runtimes (for example: `cognitive-os bridge anthropic-managed`) that transform runtime events into memory-contract envelopes without changing existing sync behavior

### Evolution Contract v1 (gated self-evolution)

cognitive-os adds a safe self-improvement loop inspired by self-evolving agent systems while preserving authoritative governance:
- Spec: `docs/EVOLUTION_CONTRACT.md`
- Schemas: `core/schemas/evolution/*.json`

Core loop:
1. Generator proposes bounded mutation
2. Critic attempts disconfirmation
3. Deterministic replay + evaluation
4. Promotion gates decide pass/fail
5. Human-approved promotion + rollback reference

---

## Customization

### Personal memory
Edit `core/memory/global/*.md` — these are gitignored and never leave your machine. The `*.example.md` files in the same directory are committed templates that show what belongs in each file.

Recommended additions:
- `core/memory/global/build_story.md` from `build_story.example.md`
- keep it short and stable; it should describe your recurring builder narrative, not project-specific details.

### Skills
- Add to `skills/custom/` for your own skills
- Add to `skills/vendor/` and declare in `runtime_manifest.json` for curated upstream skills
- Add to `skills/private/` for experimental skills that are never synced globally

### Hooks
Edit scripts in `core/hooks/`. All hooks run with your Conda Python — no extra dependencies needed. The path is resolved dynamically so the same scripts work on any machine.

### Conda root
```bash
export COGNITIVE_OS_CONDA_ROOT=/path/to/your/conda   # default: ~/miniconda3
```

---

## Harness system

A **harness** defines the operating environment for a specific project type — execution profile, workflow constraints, safety notes, and recommended agents. Where a generic scaffold gives every project the same shape, a harness gives it the right shape.

```
cognitive-os detect .
```

```
Analyzing /your/project ...

Harness scores:

ml-research            score 11  ← recommended
· dependency: torch
· dependency: transformers
· file: **/*.ipynb (3+ found)
· directory: checkpoints/

Recommended: ml-research
cognitive-os harness apply ml-research .
```

Applying a harness writes `HARNESS.md` to the project root and extends `docs/RUN_CONTEXT.md` with profile-specific context — GPU constraints, cost acknowledgment requirements, data safety rules, or dev-server reminders, depending on type.

| Harness | Best for |
|---|---|
| `ml-research` | PyTorch / JAX / HuggingFace projects, GPU training, experiment tracking |
| `python-library` | Packages and libraries intended for distribution or reuse |
| `web-app` | React / Vue / Next.js frontends with optional backend |
| `data-pipeline` | ETL, dbt, Airflow, Prefect, analytics workflows |
| `generic` | Everything else |

Add your own by dropping a JSON file into `core/harnesses/`.

---

## Story layer (mental model + narrative memory)

To make your system explainable in your own head (and to teammates), add:
- Global: `core/memory/global/build_story.md` (your stable builder narrative)
- Project: `docs/DECISION_STORY.md` (what/why/how trace for major decisions)

```bash
cp core/memory/global/build_story.example.md core/memory/global/build_story.md
```

Why this matters:
- avoids "good reasoning but no coherent story"
- preserves decision intent across sessions/tools
- improves handoffs by keeping causal context

## Deterministic profile + cognition setup

`cognitive-os profile` and `cognitive-os cognition` are deterministic onboarding layers:

- **profile** = how work runs (planning, testing, docs, automation)
- **cognition** = how decisions are made (reasoning depth, challenge style, uncertainty posture)

Important: treat survey/infer outputs as a starting point, not doctrine.
For long-term quality, manually author your authoritative philosophy in `core/memory/global/cognitive_profile.md`
using a top-down structure (reasonings -> agency -> adaptation -> governance -> operating thesis), then sync.

`cognitive-os` includes deterministic profiling to bootstrap this process and keep it explainable.

Modes:
- `survey` — explicit questionnaire, 4-level choices mapped to scores 0..3
- `infer` — deterministic repo-signal scoring (docs/tests/CI/branch patterns/guardrails)
- `hybrid` — weighted merge (`60% survey + 40% infer`, rounded)

Tip: `survey` and `hybrid` support `--answers-file templates/profile_answers.example.json` for non-interactive runs.

Dimensions (all scored 0..3):

**Workstyle Profile:**
- `planning_strictness`
- `risk_tolerance`
- `testing_rigor`
- `parallelism_preference`
- `documentation_rigor`
- `automation_level`

**Cognitive Profile:**
- `first_principles_depth`
- `exploration_breadth`
- `speed_vs_rigor_balance`
- `challenge_orientation`
- `uncertainty_tolerance`
- `autonomy_preference`

Examples:

```bash
cognitive-os profile survey --answers-file templates/profile_answers.example.json
cognitive-os profile infer .
cognitive-os profile hybrid . --answers-file templates/profile_answers.example.json --write
cognitive-os profile show
```

Generated artifacts (machine-generated):
- `core/memory/global/.generated/workstyle_profile.json`
- `core/memory/global/.generated/workstyle_scores.json`
- `core/memory/global/.generated/workstyle_explanations.md`
- `core/memory/global/.generated/personalization_blueprint.md` (combined user system profile)

To compile generated scores into global memory files:

```bash
cognitive-os profile hybrid . --write --overwrite
```

Local integration after `--write`:

```bash
cognitive-os sync
cognitive-os doctor
```

### One-command setup (execution + thinking)

For first-time setup (or reconfiguration), use:

This flow sets your agent's soul: stable execution defaults + thinking posture.

Defaults:
- Non-interactive (`cognitive-os setup .`): `profile-mode=infer`, `cognition-mode=infer`
- Interactive (`cognitive-os setup . --interactive`): asks whether to use questionnaire onboarding now; if yes, both modes default to `survey`
- `write=false` (preview first)
- `overwrite=false`
- `sync=false`
- `doctor=false`
- `governance-pack=balanced` (applies when `--sync` is enabled)

Important:
- In non-interactive setup, `survey` or `hybrid` requires complete answers via `--profile-answers-file` / `--cognition-answers-file` (or shared `--answers-file`).
- In interactive setup, missing answers are prompted in-terminal for selected survey/hybrid modes.
- Interactive prompt order is: onboarding choice -> mode selection (if not questionnaire) -> write/overwrite/sync/doctor -> survey questions.
- Setup binds both execution policy (workstyle) and cognitive policy (thinking posture) in one flow.

```bash
# interactive prompts
cognitive-os setup . --interactive

# non-interactive with explicit post-steps
cognitive-os setup . --write --sync --governance-pack strict --doctor

# fully scripted with separate answer files (required for survey/hybrid in non-interactive mode)
cognitive-os setup . \
--profile-mode hybrid \
--cognition-mode infer \
--profile-answers-file templates/profile_answers.example.json \
--cognition-answers-file templates/profile_answers.example.json \
--write --overwrite --sync --doctor
```

Answer-file precedence in setup:
1) `--profile-answers-file` / `--cognition-answers-file` (most specific)
2) `--answers-file` fallback for both

---

## Quick terminal tools (strongly recommended)

Agents running under cognitive-os use these tools for codebase search, file discovery, and inspection. Install them for the best experience:
- `rg` (ripgrep): agents use it for codebase search — fast, respects .gitignore, structured output
- `fd`: agents use it for file discovery — cleaner interface than find, predictable behavior
- `bat`: cleaner file inspection — syntax highlighting and line numbers in agent-readable output
- `sd`: safer in-place replacements — explicit, regex-capable, less footgun-prone than sed
- `ov`: better pager for long outputs — handles wide output and ANSI without mangling it

`rg`, `fd`, and `bat` are treated as local-only (expected on dev workstations). `cognitive-os doctor` checks their presence.

---

## Push-readiness checklist

Before publishing:
- `PYTHONPATH=. pytest -q tests/test_profile_cognition.py`
- `python3 -m py_compile src/cognitive_os/cli.py`
- `cognitive-os doctor`
- `git status` and `git rev-list --left-right --count @{u}...HEAD`

If these pass, the repo is in a clean, reproducible state for push.

## Vendor skill provenance (inspired, not copied)

- Required vendor attribution map: `skills/vendor/SOURCES.md`
- Every vendor skill should include a `## Provenance` section in `SKILL.md` when imported/adapted
- Run `cognitive-os validate` to surface manifest/provenance warnings before shipping
