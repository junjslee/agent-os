# Agent OS Architecture

## Purpose
`agent-os` is the cross-project operating system for the user's development and research workflow.

It exists to provide:
- stable memory outside chat sessions
- reusable skills and workflow policy
- tool-specific adapters for Claude, Codex, and editor-driven work
- bounded execution patterns such as worktrees, review gates, and handoffs

It is not:
- a project requirements document
- a plugin marketplace
- a replacement for repo-local project truth

## Layer Model
The system is intentionally layered.

### 1. Global `agent-os`
This is the source of truth for:
- personal workflow policy
- safety defaults
- shared skills
- shared subagent definitions
- repo templates
- harness definitions
- sync and bootstrap scripts

### 2. Project Harness
A harness defines the operating environment for a specific project type.
It is provisioned once at project creation (or applied to an existing project)
and lives as `HARNESS.md` in the project root.

A harness specifies:
- execution profile (`local`, `remote_gpu`, etc.)
- workflow constraints and safety notes specific to the domain
- recommended agents and skills
- extensions to `docs/RUN_CONTEXT.md`

Available harness types: `ml-research`, `python-library`, `web-app`, `data-pipeline`, `generic`.
Add custom types by dropping a JSON file into `core/harnesses/`.

Detection: `agent-os detect [path]` scores signals in the repo (dependency files, file
patterns, directory names) and recommends the best match.

### 3. Shared Project Memory
Every project should keep its canonical truth in repo files such as:
- `AGENTS.md`
- `docs/REQUIREMENTS.md`
- `docs/PLAN.md`
- `docs/PROGRESS.md`
- `docs/RUN_CONTEXT.md`
- `docs/NEXT_STEPS.md`

This layer must remain tool-agnostic.

### 4. Tool Adapters
Tool-specific runtime files shape behavior without replacing project memory.

Current adapters:
- Claude:
  `CLAUDE.md`, `.claude/settings.json`, hooks, plugins, and project-local agents if needed
- Codex:
  `AGENTS.md`, `.codex/config.toml`, repo or global skills, and project-local agents if needed
- Cursor:
  editor and review surface only unless a future repo explicitly promotes it beyond that role
- Hermes:
  `~/.hermes/OPERATOR.md` (synced composite), `~/.hermes/SOUL.md` (auto-created on first sync),
  `~/.hermes/skills/` (managed skills)

### 5. Optional Plugin Or Service Layer
This layer is optional and non-canonical.

Examples:
- Claude-only plugins such as `claude-mem`
- MCP servers
- Codex-side memory tooling

These additions may accelerate work, but they must not become the only place where project truth lives.

## Source Of Truth Order
When layers disagree, use this order:
1. Repo requirements and execution docs
2. Repo runtime files
3. Global `agent-os` defaults
4. Optional plugins or memory services

Plugins and local memory services are helpers, not authorities.

## Memory Model
The memory model is split on purpose.

`agent-os profile` adds a deterministic onboarding layer that generates explainable scorecards and compiles workflow policy from explicit rules. Generated artifacts live under `core/memory/global/.generated/` and remain non-canonical until compiled to global memory markdown (`--write`). Survey-driven modes also support non-interactive `--answers-file` JSON input.

`agent-os cognition` adds a deterministic cognitive layer for philosophy, decision attitude, and thinking posture. It supports survey, infer, and hybrid modes, and compiles into `cognitive_profile.md` when requested.

### Global Memory
Put stable, cross-project information here:
- operator preferences
- naming conventions
- safety policy
- runtime policy
- cross-project workflow defaults

### Repo Memory
Put project truth here:
- what is being built
- current milestone
- current blockers
- execution constraints
- accepted decisions
- next handoff

### Plugin Memory
Treat plugin-managed memory as a cache or retrieval layer, not as the canonical record.

If a plugin retrieves something important enough to matter later, write it back into repo docs or the relevant global memory file.

## Tool Matrix
### Claude
Strengths:
- hooks
- plugins
- MCP
- project and local settings scopes
- built-in worktree support

Use Claude when you want:
- lifecycle hooks
- plugin-backed enhancements
- deeper Claude-native orchestration

### Codex
Strengths:
- strong repo instruction handling through `AGENTS.md`
- repo-local config
- global and repo skills
- project-local agents

Use Codex when you want:
- Codex-first implementation work
- direct use inside Codex CLI or IDE surfaces
- the same shared repo memory with lighter tool-specific overhead

### Cursor
Strengths:
- editing
- diff review
- navigation

Use Cursor as the editing and inspection surface, not as the primary runtime authority.

## Execution Model
The standard execution pattern is:
1. Explore
2. Plan
3. Implement
4. Review
5. Handoff

The standard scaling pattern is:
- one bounded objective per worktree
- one active owner per worktree
- review gate before merge

The standard automation boundary is:
- allow bounded loops for clearly defined search or evaluation tasks
- block unattended destructive changes, auto-merge, and uncontrolled code-writing loops

## Safety And Governance
- Keep credentials, auth state, and machine-specific overrides local.
- Keep shared workflow docs and reproducible runtime files in Git.
- Use Conventional Commits.
- Prefer review gates for risky code or schema changes.
- Keep local Python-backed `agent-os` work on Conda `base`.

## Plugin Integration Policy
Use this test before adding a plugin or memory layer:
1. Is it cross-tool or Claude-only?
2. Does it replace canonical docs, or only accelerate retrieval?
3. Can the project still operate without it?
4. Does it introduce a second source of truth?

### Optional adapters
`claude-mem` overlaps with `agent-os` only partially.

What `agent-os` already covers:
- explicit markdown memory
- handoff docs
- stable workflow policy
- cross-project and cross-tool structure

What `claude-mem` adds:
- automatic Claude-session capture
- retrieval of past Claude activity across sessions
- plugin-managed memory search

So `claude-mem` is a useful optional Claude layer, but it does not replace `agent-os`.

### Codex And `claude-mem`
`claude-mem` is Claude-specific. It should not be treated as a Codex memory solution.

For Codex, the current base is:
- shared repo docs
- `AGENTS.md`
- `.codex/config.toml`
- global and repo skills

If deeper Codex memory is needed later, add a Codex-native or tool-neutral layer rather than depending on a Claude-only plugin.

## Bootstrap And Sync
The workflow is:
1. Edit `agent-os`
2. Run `agent-os sync`
3. Bootstrap new repos with `agent-os bootstrap`
4. Use worktrees and repo memory inside each project

## Non-Goals
- no automatic merge to `main`
- no plugin-specific lock-in as the base architecture
- no assumption that one tool's private memory is enough for team-visible project truth
