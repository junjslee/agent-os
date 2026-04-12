# agent-os

**Every AI tool you open starts cold. agent-os fixes that.**

`agent-os` is a platform-agnostic Python CLI that provisions the operating environment for AI coding agents — memory, skills, hooks, and project harnesses — across Claude Code, Codex CLI, Cursor, Hermes, and future adapters. It detects what kind of project you're in, configures the right constraints, and syncs everything in one command.

> Not a web UI, not a session manager, not a skill marketplace. It's the layer that runs *before* your agent starts work.

---

## The problem it solves

You use multiple AI coding agents. Each one starts cold. You repeat yourself. Skills drift out of sync. One agent knows your workflow; another doesn't. A context reset wipes everything. Every project gets the same generic scaffold regardless of whether it's ML research on a GPU cluster or a React app on your laptop.

`agent-os` fixes this with a single repo that acts as the operating layer for your entire AI stack:

```
┌─────────────────────── agent-os ────────────────────────────┐
│                                                              │
│  core/memory/     →  who you are, how you work              │
│  core/agents/     →  planner, implementer, reviewer …       │
│  core/hooks/      →  safety guards, formatter, quality gate │
│  core/harnesses/  →  per-project-type operating contexts    │
│  skills/          →  reusable prompt + tool packages        │
│  templates/       →  standard scaffold for every new project│
│                                                              │
└───────────┬──────────────────────────────────────────────────┘
            │   agent-os sync / detect / harness apply
   ┌────────┼────────┬──────────┬───────────┐
   ▼        ▼        ▼          ▼           ▼
 Claude   Codex   Cursor     Hermes    new machines
  Code     CLI   (skills)  (skills)   (agent-os init)
```

---

## Design principles

- Canonical project truth lives in repository docs (`AGENTS.md`, `docs/*`), not in any single agent tool.
- Global operator memory (cross-project) is separate from project memory (repo-local delivery context).
- Adapters (Claude, Codex, Cursor, Hermes, others) are delivery mechanisms for the same operating contract, not separate authorities.
- Plugin or tool-native memory systems accelerate retrieval, but do not replace canonical records.

---

## 1-minute model

`agent-os` has three layers:

1) **Global operator layer** (`core/memory/global/*`)
- your stable workflow + cognitive defaults across projects

2) **Project truth layer** (`AGENTS.md`, `docs/*`)
- what this specific repo is building right now

3) **Adapter layer** (Claude/Codex/Cursor/Hermes)
- delivery surfaces that consume the same contract

Adapters are not the authority. Repo docs + global memory are.

---

## Quick start

```bash
git clone https://github.com/yourname/agent-os ~/agent-os
cd ~/agent-os
pip install -e .            # installs into Conda base
agent-os init               # create personal memory files from templates
# edit core/memory/global/*.md with your context
agent-os sync               # push everything to all tools
agent-os new-project .      # scaffold any existing or new project
```

### 60-second demo (workflow + cognition + sync)

```bash
agent-os profile hybrid . --write
agent-os cognition survey --write
agent-os sync
agent-os doctor
```

Expected outcome:
- deterministic score artifacts generated under `core/memory/global/.generated/`
- global memory markdown updated (if `--write` and overwrite rules allow)
- adapters receive updated runtime context after `sync`

That's it. Every agent you open now inherits your memory, skills, and hooks.

To provision the right operating environment for your project type:

```bash
agent-os detect .                          # analyze repo and recommend a harness
agent-os harness apply ml-research .       # apply it
# or in one shot:
agent-os new-project . --harness auto      # scaffold + auto-detect harness
```

---

## What gets synced

| Asset | Claude Code | Codex CLI | Cursor | Hermes |
|---|---|---|---|---|
| Global memory index (`CLAUDE.md`) | ✅ | — | — | — |
| Operator/cognitive/workflow source files (`core/memory/global/*.md`) | via include | source only | source only | composed into `OPERATOR.md` |
| Agent personas | ✅ | — | — | — |
| Skills | ✅ | ✅ | ✅ | ✅ |
| Lifecycle hooks | ✅ | — | — | — |
| Operator context composite (`OPERATOR.md`) | — | — | — | ✅ |

Note: this matrix describes current adapter capabilities, not architectural authority. Canonical truth remains in repository docs and global agent-os memory.

---

## Included hooks (Claude Code)

Hooks run deterministically — they can't be overridden by model behavior.

| Hook | Event | What it does |
|---|---|---|
| `session_context.py` | `SessionStart` | Prints branch, git status, and `NEXT_STEPS.md` at session open |
| `block_dangerous.py` | `PreToolUse Bash` | Blocks `rm -rf`, `git reset --hard`, `git push --force`, `sudo`, `pkill`, and more |
| `format.py` | `PostToolUse Write\|Edit` | Auto-runs `ruff` (Python) or `prettier` (JS/TS) after every file write |
| `test_runner.py` | `PostToolUse Write\|Edit` | Runs pytest / jest on the file if it's a test file |
| `quality_gate.py` | `Stop` | Blocks completion if tests fail (opt-in via `.quality-gate` in project root) |
| `checkpoint.py` | `Stop` | Auto-commits uncommitted changes as `chkpt:` after every turn |
| `precompact_backup.py` | `PreCompact` | Backs up session transcripts before context compaction |

---

## Included skills

### Custom (your own)
`repo-bootstrap` · `requirements-to-plan` · `progress-handoff` · `worktree-split` · `bounded-loop-runner` · `review-gate` · `research-synthesis`

### Vendor (curated upstream)
`swing-clarify` · `swing-options` · `swing-research` · `swing-review` · `swing-trace` · `swing-mortem` · `create-prd` · `sprint-plan` · `pre-mortem` · `test-scenarios` · `prioritization-frameworks` · `retro` · `release-notes`

Add your own skills under `skills/custom/` — each skill is a folder with a `SKILL.md`.

---

## Included agent personas

Six subagent definitions installed into `~/.claude/agents/`:

`planner` · `researcher` · `implementer` · `reviewer` · `test-runner` · `docs-handoff`

---

## Project scaffold

`agent-os new-project [path]` creates a standard project structure:

```
AGENTS.md            vendor-neutral operating manual for any agent
CLAUDE.md            Claude-native memory index
docs/
  REQUIREMENTS.md    what is being built
  PLAN.md            staged execution
  PROGRESS.md        completed work and decisions
  NEXT_STEPS.md      next-session handoff
  RUN_CONTEXT.md     runtime assumptions, APIs, execution profiles
.claude/
  settings.json      permission rules
  settings.local.json  machine-local overrides (gitignored)
```

---

## Commands

```
agent-os init                               bootstrap personal memory files from templates
agent-os doctor                             verify Conda, tools, and runtime wiring
agent-os sync                               push all assets to Claude, Codex, Cursor, Hermes
agent-os update                             pull latest agent-os from git
agent-os validate                           check manifest — every declared skill needs SKILL.md
agent-os list                               show agents, skills, plugins, active hooks
agent-os new-project [path]                 scaffold a new project (alias: bootstrap)
agent-os new-project [path] --harness TYPE  scaffold and apply a harness (or --harness auto)
agent-os detect [path]                      detect the best harness type for a project
agent-os harness list                       show available harness types
agent-os harness apply <type> [path]        apply a harness to an existing project
agent-os profile survey [--answers-file JSON] [--write] [--overwrite]        deterministic survey-based workstyle scoring
agent-os profile infer [path] [--write] [--overwrite]                         deterministic repository-signal-based scoring
agent-os profile hybrid [path] [--answers-file JSON] [--write] [--overwrite]  blend survey + infer (60/40)
agent-os profile show                                                          show latest generated workstyle scorecard
agent-os cognition survey [--answers-file JSON] [--write] [--overwrite]       deterministic cognitive philosophy survey
agent-os cognition infer [path] [--write] [--overwrite]                        infer cognitive philosophy scores from repo signals
agent-os cognition hybrid [path] [--answers-file JSON] [--write] [--overwrite] blend cognitive survey + infer (60/40)
agent-os cognition show                                                        show latest generated cognitive scorecard
agent-os worktree <type> <name>             create a git worktree for a bounded task
agent-os start [claude|cursor|codex]        open a tool surface
agent-os private-skill enable <name>        enable a local experimental skill for Claude
agent-os private-skill disable <name>       disable it
agent-os private-skill status <name>        check its install state
```

---

## Memory model

```
global memory (this repo)
  └── stable cross-project context: who you are, how you work, safety policy

project memory (each repo's docs/)
  └── what is being built, current state, next handoff

plugin memory (claude-mem, etc.)
  └── cache and retrieval — never the canonical record
```

Global memory never belongs in chat. Project memory never belongs in global. Plugins help but don't replace either.

---

## Customising

### Personal memory
Edit `core/memory/global/*.md` — these are gitignored and never leave your machine. The `*.example.md` files in the same directory are committed templates that show what belongs in each file.

### Skills
- Add to `skills/custom/` for your own skills
- Add to `skills/vendor/` and declare in `runtime_manifest.json` for curated upstream skills
- Add to `skills/private/` for experimental skills that are never synced globally

### Hooks
Edit scripts in `core/hooks/`. All hooks run with your Conda Python — no extra dependencies needed. The path is resolved dynamically so the same scripts work on any machine.

### Conda root
```bash
export AGENT_OS_CONDA_ROOT=/path/to/your/conda   # default: ~/miniconda3
```

---

## Harness system

A **harness** defines the operating environment for a specific project type — execution profile, workflow constraints, safety notes, and recommended agents. Where a generic scaffold gives every project the same shape, a harness gives it the right shape.

```
agent-os detect .
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
  agent-os harness apply ml-research .
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

## Deterministic workstyle setup

`agent-os profile` and `agent-os cognition` are deterministic onboarding layers:

- **profile** = how work runs (planning, testing, docs, automation)
- **cognition** = how decisions are made (reasoning depth, challenge style, uncertainty posture)

`agent-os` now includes a deterministic profile system for onboarding operator working style and compiling policy.

Modes:
- `survey` — explicit questionnaire, 4-level choices mapped to scores 0..3
- `infer` — deterministic repo-signal scoring (docs/tests/CI/branch patterns/guardrails)
- `hybrid` — weighted merge (`60% survey + 40% infer`, rounded)

Tip: `survey` and `hybrid` support `--answers-file templates/profile_answers.example.json` for non-interactive runs.

Dimensions (all scored 0..3):
- `planning_strictness`
- `risk_tolerance`
- `testing_rigor`
- `parallelism_preference`
- `documentation_rigor`
- `automation_level`

Examples:

```bash
agent-os profile survey --answers-file templates/profile_answers.example.json
agent-os profile infer .
agent-os profile hybrid . --answers-file templates/profile_answers.example.json --write
agent-os profile show
```

Generated artifacts (machine-generated):
- `core/memory/global/.generated/workstyle_profile.json`
- `core/memory/global/.generated/workstyle_scores.json`
- `core/memory/global/.generated/workstyle_explanations.md`

To compile generated scores into global memory files:

```bash
agent-os profile hybrid . --write --overwrite
```

Local integration after `--write`:

```bash
agent-os sync
agent-os doctor
```

### Deterministic cognitive profile

For philosophy of work, thinking posture, and decision attitude:

Modes:
- `survey` — explicit cognitive questionnaire
- `infer` — deterministic repo-signal cognitive scoring
- `hybrid` — weighted merge (`60% survey + 40% infer`, rounded)

Tip: `survey` and `hybrid` support `--answers-file templates/profile_answers.example.json` for non-interactive runs.

```bash
agent-os cognition survey --answers-file templates/profile_answers.example.json
agent-os cognition infer .
agent-os cognition hybrid . --answers-file templates/profile_answers.example.json --write
agent-os cognition show
```

Cognitive dimensions (0..3):
- `first_principles_depth`
- `exploration_breadth`
- `speed_vs_rigor_balance`
- `challenge_orientation`
- `uncertainty_tolerance`
- `autonomy_preference`

Generated cognitive artifacts:
- `core/memory/global/.generated/cognitive_profile.json`
- `core/memory/global/.generated/cognitive_explanations.md`

With `--write`, output compiles into:
- `core/memory/global/cognitive_profile.md`

Then sync locally:

```bash
agent-os sync
agent-os doctor
```

### Safety and overwrite behavior

- Generated artifacts in `core/memory/global/.generated/*` are machine-generated and non-canonical.
- `--write` compiles generated scores into canonical global memory markdown.
- Existing canonical files are not replaced unless you pass `--overwrite`.
- Recommended flow: run once without `--overwrite`, review output, then rerun with `--overwrite` only if desired.

### Troubleshooting (quick)

- `answers file not found`:
  - check path and file name
  - try: `templates/profile_answers.example.json`
- `invalid JSON in answers file`:
  - ensure valid JSON object
  - either `{ "answers": { ... } }` or direct key/value object
- `Skipped existing file (use --overwrite)`:
  - expected safety behavior; rerun with `--overwrite` only if you want replacement
- Scores look off:
  - run `profile/cognition show`
  - inspect `.generated/*_explanations.md` evidence
  - adjust answers file and rerun hybrid

### Who this is for

Best fit:
- you use multiple AI agents and want one stable operating contract
- you maintain project docs as canonical truth
- you want deterministic, explainable behavior defaults

Not ideal (yet):
- single-tool workflows with no cross-project memory needs
- users expecting fully automatic behavior without reviewing canonical docs

---

## Portability

`agent-os` works on any machine:

1. `git clone` this repo
2. `pip install -e .`
3. `agent-os init` — creates your personal memory files from templates
4. Fill in your context
5. `agent-os sync`

Your personal memory files are gitignored. Clone on a new machine, fill in once, you're running.

### Remote machines and HPC clusters

A few things differ on shared compute clusters:

**Work filesystem** — home directories on HPC systems are often quota-limited or slow. Clone to a work/scratch filesystem instead:
```bash
git clone https://github.com/yourname/agent-os /work/path/to/agent-os
cd /work/path/to/agent-os
pip install -e .
```

**Python via environment modules** — many clusters use `module` rather than Conda. If the system Python or pip is broken/too old, load a working Python first:
```bash
module load <python-module>   # e.g. miniforge3, python/3.11, anaconda3
pip install -e .
```
Add the `module load` line to your `~/.bashrc` (or equivalent) so it's available in every session.

**Non-standard Python path** — if your Python isn't at `~/miniconda3`, tell agent-os where it is:
```bash
export AGENT_OS_CONDA_ROOT=/path/to/your/python/env
```

**Syncing skills and settings from your primary machine** — `agent-os sync` installs skills from the repo, but vendor skills, plugins, and `settings.json` from your primary machine need an explicit push:
```bash
rsync -av ~/.claude/skills/   user@remote-host:~/.claude/skills/
rsync -av ~/.claude/plugins/  user@remote-host:~/.claude/plugins/
rsync -av ~/.claude/commands/ user@remote-host:~/.claude/commands/
rsync -av ~/.claude/settings.json user@remote-host:~/.claude/settings.json
```
Re-run this whenever you add or update skills on your primary machine.

---

## Architecture reference

See [`docs/AGENT_OS_ARCHITECTURE.md`](docs/AGENT_OS_ARCHITECTURE.md) for the full layer model, source-of-truth ordering, tool matrix, and plugin integration policy.

---

## Recommended GitHub topics

Add these in your repo settings for discoverability:

`claude-code` · `ai-agents` · `llm-tools` · `developer-tools` · `automation` · `workflow` · `hermes-agent` · `codex` · `dotfiles` · `prompt-engineering`

---

## License

MIT
