# agent-os

**One source of truth for all your AI coding agents.**

`agent-os` is a CLI that syncs global memory, skills, hooks, and workflow policy across Claude Code, Codex CLI, Cursor, and Hermes — so every agent you open starts with the same context, the same safety guards, and the same skills.

---

## The problem it solves

You use multiple AI coding agents. Each one starts cold. You repeat yourself. Skills drift out of sync. One agent knows your workflow; another doesn't. A context reset wipes everything.

`agent-os` fixes this with a single repo that acts as the operating layer for your entire AI stack:

```
┌─────────────────────── agent-os ────────────────────────────┐
│                                                              │
│  core/memory/   →  who you are, how you work                │
│  core/agents/   →  planner, implementer, reviewer …         │
│  core/hooks/    →  safety guards, formatter, quality gate   │
│  skills/        →  reusable prompt + tool packages          │
│  templates/     →  standard scaffold for every new project  │
│                                                              │
└───────────┬──────────────────────────────────────────────────┘
            │   agent-os sync
   ┌────────┼────────┬──────────┬───────────┐
   ▼        ▼        ▼          ▼           ▼
 Claude   Codex   Cursor     Hermes    new machines
  Code     CLI   (skills)  (skills)   (agent-os init)
```

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

That's it. Every agent you open now inherits your memory, skills, and hooks.

---

## What gets synced

| Asset | Claude Code | Codex CLI | Cursor | Hermes |
|---|---|---|---|---|
| Global memory (CLAUDE.md) | ✅ | — | — | — |
| Agent personas | ✅ | — | — | — |
| Skills | ✅ | ✅ | ✅ | ✅ |
| Lifecycle hooks | ✅ | — | — | — |
| Operator context (OPERATOR.md) | — | — | — | ✅ |

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
