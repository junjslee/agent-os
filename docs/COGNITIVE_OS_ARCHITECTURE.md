# episteme Architecture

## Purpose

`episteme` is the cognitive + execution operating system for cross-project development and research workflows. It operationalizes decision quality, memory governance, execution cognition, and accountable evolution.

Distributed via the `episteme` CLI/package.

It provides:
- stable memory outside chat sessions
- reusable skills and workflow policy
- tool-specific adapters for Claude Code, Codex, opencode, and Hermes
- bounded execution patterns: worktrees, review gates, and handoffs

It is not:
- a project requirements document
- a plugin marketplace
- a replacement for repo-local project truth

## Positioning

episteme is the governance and identity layer that sits above agent platforms. The platforms are delivery vessels; episteme is the authority.

- episteme lives above Claude Code, Codex, opencode, and Hermes. Those tools are adapters -- they consume the cognitive contract but do not define it.
- No single agent platform is authoritative. episteme is. A context reset in Claude Code, a new Codex session, or a Cursor workspace change does not reset your identity -- only episteme holds that.
- The layer distinction matters: agent platforms handle execution (run code, call tools, respond in sessions). episteme handles governance (who the agent is, what it knows, how it behaves, what it remembers across sessions and tools).
- Sync flows one direction: from episteme outward to platforms. Platforms do not write back into episteme automatically; durable lessons are explicitly promoted via `episteme evolve` or manual authoring.
- This architecture makes episteme portable across the current toolchain and any future tools -- a new adapter can be added without changing the identity layer.

## 🧬 Layer Model: The Soul and the Vessel

The system separates **Cognition** from **Execution** deliberately. They reinforce each other — cognition without execution is theory; execution without cognition is a brittle machine.

### 🏛️ Cognitive Layer (The Soul)

Defines how the agent thinks and reasons.
- **Identity**: Who the agent is — professional profile, cognitive style, reasoning posture.
- **First Principles**: Foundational reasoning laws — epistemic humility, disconfirmation discipline.
- **Governance**: Decision-making limits and ethical boundaries.

### 🛠️ Execution Layer (The Vessel)

Defines how the agent acts and adapts.
- **Workflow**: The stages of transformation — Explore → Plan → Manifest.
- **Harnesses**: Project-type-specific operating environments — execution profiles, constraints, safety notes.
- **Lifecycle Hooks**: Deterministic quality enforcement — post-write formatting, pre-commit tests, stop-gate checks.

### 1. Global episteme

Source of truth for:
- personal workflow policy
- safety defaults
- shared skills
- shared subagent definitions
- repo templates
- harness definitions
- sync and bootstrap scripts

### 2. Project Harness

A harness defines the operating environment for a specific project type.
Provisioned once at project creation (or applied to an existing project) and lives as `HARNESS.md` in the project root.

A harness specifies:
- execution profile (`local`, `remote_gpu`, etc.)
- workflow constraints and safety notes specific to the domain
- recommended agents and skills
- extensions to `docs/RUN_CONTEXT.md`

Available harness types: `ml-research`, `python-library`, `web-app`, `data-pipeline`, `generic`.
Add custom types by dropping a JSON file into `core/harnesses/`.

Detection: `episteme detect [path]` scores signals in the repo (dependency files, file patterns, directory names) and recommends the best match.

### 3. Project Memory

Every project keeps its definitive truth in repo files:
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
- opencode:
  `~/.config/opencode/agents/episteme-governance.md` (global governance subagent),
  `AGENTS.md` (per-project behavioral contract, same file Codex reads)
- Hermes:
  `~/.hermes/OPERATOR.md` (synced composite), `~/.hermes/SOUL.md` (auto-created on first sync),
  `~/.hermes/skills/` (managed skills)
- OMO / OMX (Oh-My-OpenAgent / Oh-My-Codex):
  Syncs shared skills, agent personas, and structural governance policy to `~/.omo` or `~/.omx`

### 5. Managed Runtime Bridges (additive)

Managed runtimes (for example Anthropic Managed Agents) are execution substrates that emit durable event logs.
`episteme` ingests those events through bridge commands and converts them into Memory Contract envelopes.

Current bridge:
- `episteme bridge anthropic-managed --input <events.json>`
  - outputs `memory-contract-v1` envelopes under `core/memory/bridges/anthropic-managed/`
  - does not modify existing adapter sync behavior

### 6. Optional Plugin or Service Layer

This layer is optional and non-authoritative.

Examples:
- Claude-only plugins such as `claude-mem`
- MCP servers
- Codex-side memory tooling

These additions may accelerate work but must never become the only place where project truth lives.

## Source of Truth Order

When layers disagree, this order wins:
1. Repo requirements and execution docs
2. Repo runtime files
3. Global `episteme` defaults
4. Optional plugins or memory services

Plugins and local memory services are helpers, not authorities.

## Memory Model

The memory model is split on purpose.

`episteme profile` adds a deterministic onboarding layer that generates explainable scorecards and compiles workflow policy from explicit rules. Generated artifacts live under `core/memory/global/.generated/` and remain non-authoritative until compiled to global memory markdown (`--write`). Survey-driven modes also support non-interactive `--answers-file` JSON input.

`episteme cognition` adds a deterministic cognitive layer for philosophy, decision attitude, and thinking posture. It supports survey, infer, and hybrid modes, and compiles into `cognitive_profile.md` when requested.

### Memory Contract v1

For portable integrations and deterministic reconciliation, see:
- Spec: `docs/MEMORY_CONTRACT.md`
- Schemas: `core/schemas/memory-contract/*.json`

Contract highlights:
- explicit classes: global, project, episodic
- required provenance metadata for trust/audit
- deterministic conflict semantics with human override precedence

### Evolution Contract v1

For safe, auditable self-improvement, see:
- Spec: `docs/EVOLUTION_CONTRACT.md`
- Schemas: `core/schemas/evolution/*.json`

Contract highlights:
- generator/critic role split
- bounded mutation library
- deterministic replay + promotion gates
- human-approved promotion with rollback linkage

### Global Memory

Put stable, cross-project information here:
- operator preferences
- naming conventions
- safety policy
- runtime policy
- cross-project workflow defaults

### Project Memory

Put project-specific truth here:
- what is being built
- current milestone
- current blockers
- execution constraints
- accepted decisions
- next handoff

### Plugin Memory

Treat plugin-managed memory as a cache or retrieval layer, not as the authoritative record.

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

### opencode
Strengths:
- open-source, provider-agnostic (Claude, OpenAI, local models)
- TUI-first, built by terminal power users
- AGENTS.md-compatible (same contract as Codex)
- strong multi-agent / subagent support via @agent-name invocation

episteme syncs a global governance subagent to `~/.config/opencode/agents/`.
Per-project contract is AGENTS.md, same as Codex. No per-project adapter file needed.

## Execution Model

The standard execution pattern:
1. Explore
2. Plan
3. Implement
4. Review
5. Handoff

The standard scaling pattern:
- one bounded objective per worktree
- one active owner per worktree
- review gate before merge

The standard automation boundary:
- allow bounded loops for clearly defined search or evaluation tasks
- block unattended destructive changes, auto-merge, and uncontrolled code-writing loops

## Safety and Governance

- Keep credentials, auth state, and machine-specific overrides local.
- Keep shared workflow docs and reproducible runtime files in Git.
- Use Conventional Commits.
- Prefer review gates for risky code or schema changes.
- Keep local Python-backed `episteme` work on Conda `base`.

## Plugin Integration Policy

Before adding a plugin or memory layer, verify:
1. Is it cross-tool or Claude-only?
2. Does it replace authoritative docs, or only accelerate retrieval?
3. Can the project still operate without it?
4. Does it introduce a second source of truth?

### Optional adapters

`claude-mem` overlaps with `episteme` only partially.

What `episteme` already covers:
- explicit markdown memory
- handoff docs
- stable workflow policy
- cross-project and cross-tool structure

What `claude-mem` adds:
- automatic Claude-session capture
- retrieval of past Claude activity across sessions
- plugin-managed memory search

So `claude-mem` is a useful optional Claude layer, but it does not replace `episteme`.

### Codex and `claude-mem`

`claude-mem` is Claude-specific. It should not be treated as a Codex memory solution.

For Codex, the current base is:
- shared repo docs
- `AGENTS.md`
- `.codex/config.toml`
- global and repo skills

If deeper Codex memory is needed later, add a Codex-native or tool-neutral layer rather than depending on a Claude-only plugin.

## Bootstrap and Sync

The workflow:
1. Edit `episteme`
2. Run `episteme sync`
3. Bootstrap new repos with `episteme bootstrap`
4. Use worktrees and repo memory inside each project

## Non-Goals

- no automatic merge to `main`
- no plugin-specific lock-in as the base architecture
- no assumption that one tool's private memory is enough for team-visible project truth
