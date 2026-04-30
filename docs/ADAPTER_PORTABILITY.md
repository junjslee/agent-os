# Adapter Portability Audit

**Status**: `audit (Event 96, 2026-04-30)` — read-only inventory + migration design. No runtime changes proposed in this document.

**Author goal (verbatim, from operator directive)**: *"The true essence of our tool requires that this 'truth-seeking' is not locked to a single vendor. Analyze what it takes to make the kernel truly model-agnostic so it works perfectly outside of Claude Code."*

This doc is the honest answer. It draws clear lines between what is genuinely portable today, what is aspirational, and what specifically needs to land before a second adapter can be wired with parity.

---

## 1. Executive summary — what is honestly model-agnostic today

| Layer | Portability | Reality |
|---|---|---|
| **Kernel constitution** (`kernel/*.md`) | Truly portable | Pure markdown. Travels to any host. Reads correctly under any runtime. |
| **Schemas** (`core/schemas/*.json`) | Truly portable | JSON schemas; tool-neutral. Memory Contract v1, Evolution Contract v1, blueprint contracts all schema-defined. |
| **Blueprints** (`core/blueprints/*.yaml`) | Truly portable | YAML; selector predicates are pure-data. |
| **Operator profile** (`core/memory/global/*.md`) | Truly portable | Markdown identity layer; renders correctly under any runtime. |
| **Hook *substrate*** (`core/hooks/_*.py` — 16 private modules) | Truly portable | Pure Python logic: chain integrity, scenario detection, blueprint validation, context-signature hashing, framework I/O. No host coupling. |
| **Hook *entry points*** (`core/hooks/*.py` — 18 entry-point scripts) | **Partially portable** | Stdin-JSON contract works on any host. BUT: tool-name strings (`"Bash"`, `"Write"`, `"Edit"`, `"MultiEdit"`), tool-input schema keys (`.command`, `.file_path`), and tool-response schema keys (`.returnCodeInterpretation`, `.interrupted`) are **Claude-Code-shaped**. Hooks already handle camelCase ⇄ snake_case duality, but the canonical tool-name vocabulary is Claude's. |
| **Adapter directory** (`adapters/{claude,hermes}/`) | **Aspirational** | Only `README.md` files exist in each. **No adapter code is written.** The "Claude adapter" is implemented entirely as a side-effect of `episteme sync` writing `~/.claude/settings.json`. |
| **Other adapter targets** (`adapters/{codex,opencode,omo,omx,cursor,...}`) | **Does not exist** | Documented as targets in `docs/LAYER_MODEL.md` § *Tool Adapters*; **no directory, no README, no code**. |

### One-line honest claim

> *"The kernel is markdown-portable. The hook layer is Claude-tool-shaped. The adapter layer is one-of-five-or-more — only Claude is wired. Outside Claude Code today, the kernel still governs identity (markdown survives), but it does not enforce the Reasoning Surface — because the enforcement mechanism (hooks + canonical event interception) only exists for Claude."*

That is what *model-agnostic* means today. Anything stronger is aspiration the audit found unfunded.

---

## 2. Adapter directory inventory

### `adapters/claude/`
- **Files**: `README.md` (2.6 KB) only.
- **Adapter implementation**: indirect — happens inside `episteme sync` (Python CLI), which writes `~/.claude/CLAUDE.md`, `~/.claude/settings.json`, `~/.claude/agents/*`, `~/.claude/skills/*`, and per-project `<repo>/.claude/settings.json`.
- **Hook registration mechanism**: `~/.claude/settings.json` references `core/hooks/*.py` by absolute path with the host runtime's Python (`sys.executable`). Hooks are spawned as subprocesses by Claude Code on each event firing.
- **Verdict**: Load-bearing reference adapter. Documented well; not isolated as code in `adapters/claude/`.

### `adapters/hermes/`
- **Files**: `README.md` (3.1 KB) only.
- **Adapter implementation**: indirect — `episteme sync` writes `~/.hermes/OPERATOR.md` and `~/.hermes/skills/*`. **No hooks are installed.** README explicitly says: *"Claude Code hooks are Claude-specific — they don't transfer to Hermes. To replicate safety behavior in Hermes, configure its built-in command approval system in `config.yaml`."*
- **Verdict**: Identity-and-skills sync only. Does NOT carry hook-level enforcement. The kernel's *governance authority* travels (markdown); the kernel's *enforcement* does not.

### `adapters/{codex,opencode,omo,omx,cursor,...}`
- **Status**: Do not exist on disk. Documented as targets in `docs/LAYER_MODEL.md` § 4 (Tool Adapters), described as adapters that consume the cognitive contract via `AGENTS.md` (Codex, opencode) or governance subagent (opencode), or shared skills/personas (OMO/OMX).
- **Verdict**: Aspirational. No adapter code; no hook installation; no enforcement.

### Coverage matrix today

| Adapter | Markdown identity sync | Skills sync | Hook enforcement | Adapter code |
|---|:-:|:-:|:-:|:-:|
| Claude Code | ✓ | ✓ | ✓ | indirect (in `episteme sync`) |
| Hermes | ✓ | ✓ | ✗ | indirect (in `episteme sync`) |
| Codex | partial (`AGENTS.md`) | partial | ✗ | none |
| opencode | partial (`AGENTS.md`) | partial | ✗ | none |
| OMO / OMX | partial | partial | ✗ | none |
| Cursor / Continue / Cody / etc. | not addressed | not addressed | ✗ | none |

**Hook enforcement parity = 1 of 5+ targets.** The "model-agnostic" claim cannot be defended at the enforcement layer until this column has at least one more `✓`.

---

## 3. Hook coupling analysis — every Claude-specific assumption found

The hooks live in `core/hooks/`. There are 18 entry-point scripts and 16 private substrate modules. The substrate modules are pure logic — no host coupling. The entry-point scripts contain all the host-shape coupling. Below is the catalog.

### 3.1 Tool-name vocabulary (Claude-specific)

**Where it appears**: `block_dangerous.py`, `state_tracker.py`, `calibration_telemetry.py`, `episodic_writer.py`, `fence_synthesis.py`, `reasoning_surface_guard.py`, `format.py`, `test_runner.py`, `prompt_guard.py`, `workflow_guard.py`, `context_guard.py`.

**The pattern**:
```python
tool = _tool_name(payload)   # reads payload['tool_name'] or payload['toolName']
if tool in {"Write", "Edit", "MultiEdit"}: ...
elif tool == "Bash": ...
```

**Coupling severity**: **High**. These tool names are Claude Code's vocabulary. Cursor uses `run_terminal_cmd` / `edit_file`. Codex uses different internal names. OpenAI's function-calling uses arbitrary user-defined names. Without an adapter-level translation layer, hooks cannot identify the tool kind on a non-Claude host.

**Required to fix**: Replace magic strings with a `ToolKind` enum (e.g. `SHELL_EXEC`, `FILE_WRITE`, `FILE_EDIT`, `FILE_MULTI_EDIT`). Adapters translate their host's tool names → `ToolKind` before invoking the hook.

### 3.2 Tool-input schema (Claude-specific)

**Where it appears**: every Bash-handling hook reads `tool_input.command` or `.cmd` or `.bash_command`. Every Write/Edit-handling hook reads `tool_input.file_path` or `.path` or `.target_file`.

**The pattern**:
```python
ti = _tool_input(payload)
cmd = str(ti.get("command") or ti.get("cmd") or ti.get("bash_command") or "")
fp = ti.get("file_path") or ti.get("path") or ti.get("target_file")
```

**Coupling severity**: **Medium-low**. The `or`-fallback chains already accept a small dialect range. But the universe of valid keys is enumerated by Claude's schema; new hosts with different keys (e.g., Cursor's `args.command`) require additional fallbacks. This pattern is fragile by accumulation.

**Required to fix**: Canonical input schema with named fields (`shell_exec.command_text`, `file_write.target_path`). Adapters translate host schema → canonical.

### 3.3 Tool-response schema (Claude-specific, partial Gemini fallback)

**Where it appears**: `calibration_telemetry.py` (lines 66-162). This is the most polyglot file in the codebase — it explicitly handles Claude Code's `returnCodeInterpretation` + `interrupted` shape, Gemini-CLI's `isError` boolean, and the more conventional `exit_code` / `returncode` numeric fields.

**The pattern**:
```python
# Tries: exit_code, exitCode, returncode, return_code, status_code
# Then: nested under metadata/meta
# Then: isError/is_error bool mapping
# Then: Claude's returnCodeInterpretation + interrupted pattern
# Then: regex-extract from "exit code N" strings
```

**Coupling severity**: **Medium**. This is the most adapter-aware hook — it already encodes one runtime-dialect-and-a-half. But each new host (Cursor, Codex's tool-result format, etc.) needs another fallback chain branch.

**Required to fix**: Canonical tool-response schema (`{exit_code: int, status: "success" | "error" | "unknown", stdout: str, stderr: str}`). Adapter translates host response → canonical.

### 3.4 Hook event taxonomy (Claude-specific)

**Where it appears**: Every entry-point hook implicitly knows which event it fires on (PreToolUse, PostToolUse, Stop, SessionStart, PreCompact, etc.). The wiring is in `~/.claude/settings.json` — hooks don't read the event name from the payload; they're invoked because the host fired the matching event.

**The Claude event names**: `PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`, `SubagentStop`, `PreCompact`, `PermissionRequest`.

**Coupling severity**: **High**. Other hosts have completely different event taxonomies:
- **Cursor**: pre/post completion hooks, file-change watchers — different lifecycle.
- **Codex / opencode**: AGENTS.md-only — no hook system at all.
- **OpenAI Assistants API**: function-call lifecycle — no PreToolUse/PostToolUse equivalent in the same shape.
- **MCP servers**: tool-call lifecycle, but defined per server.

**Required to fix**: Canonical event taxonomy:
```
INTENT_TO_EXECUTE       (≈ PreToolUse)
EXECUTION_COMPLETED     (≈ PostToolUse)
SESSION_OPENED          (≈ SessionStart)
SESSION_CLOSED          (≈ Stop / SubagentStop)
CONTEXT_COMPACTING      (≈ PreCompact)
PERMISSION_REQUESTED    (≈ PermissionRequest)
```

Adapters bridge their host's lifecycle to the canonical taxonomy. Some hosts will not have all events — that is acceptable; the adapter declares which canonical events it supports, and hooks that depend on absent events degrade to advisory or no-op.

### 3.5 Hook registration mechanism (Claude-specific)

**Where it appears**: `episteme sync` writes `~/.claude/settings.json` with hook registrations. The format is Claude Code-specific — a JSON document with `hooks.{eventName}.commands` arrays referencing absolute paths to `core/hooks/*.py`.

**Coupling severity**: **High** *but* this is **adapter responsibility**. Each adapter knows its host's hook registration mechanism (Claude: settings.json; Cursor: workspace rules; Hermes: config.yaml command-approval; Codex: not applicable). The registration code does not need to be portable; only the canonical event abstraction does.

**Required to fix**: Per-adapter registration code, each writing the host's hook config in the host's format. The kernel provides the hook scripts; the adapter installs them.

### 3.6 Working directory + payload shape (Claude convention)

**Where it appears**: `payload.cwd` (Claude convention). `payload.tool_use_id` / `toolUseId` / `request_id` for correlation.

**Coupling severity**: **Low**. These are common conventions; most hosts provide cwd in some form. Already polyglot via `or`-chains.

**Required to fix**: Document canonical fields (`event.cwd`, `event.correlation_id`); adapters translate.

### 3.7 Color/TTY assumptions in stderr formatting

**Where it appears**: `reasoning_surface_guard.py` writes ANSI-colored advisory messages to stderr. Other hooks emit plain text.

**Coupling severity**: **None for portability** — ANSI codes work on any modern terminal. This is not a coupling concern.

---

## 4. The honest claim audit

### Claim: *"the kernel is model-agnostic"*

**Honest version**: The kernel is markdown-portable; identity and policy travel to any runtime. The enforcement mechanism (hooks) is Claude-tool-shaped today. Other adapters carry the markdown but not the enforcement.

### Claim: *"the kernel intercepts state mutation regardless of which external tool, MCP server, or agent framework generated the command"* (`docs/ARCHITECTURE.md` L22)

**Honest version**: True *within Claude Code* (where the hook layer can intercept Bash / Write / Edit / MultiEdit calls regardless of what tool generated them). Not yet true *across runtimes* (a Bash command issued from Codex does not fire any episteme hook because Codex has no hook integration).

### Claim: *"BYOS (Bring Your Own Skill)"*

**Honest version**: True. The kernel does not provide skills; it intercepts state mutation. This claim is independent of adapter coverage — once a host is wired, BYOS holds for that host.

### Claim: *"adapters are pluggable"*

**Honest version**: Aspirational. The adapter abstraction exists in documentation (`docs/LAYER_MODEL.md` § 4) but not in code. Wiring a new adapter today requires reading the Claude implementation pattern out of `episteme sync` and re-implementing it for the new host — there is no adapter base class, no canonical event schema, no plug-in interface.

---

## 5. Per-target feasibility matrix

| Target | Has equivalent hook lifecycle? | Has tool-call interception point? | Effort to wire (relative) | Blocker today |
|---|:-:|:-:|:-:|---|
| **Claude Code** (reference) | Yes — full lifecycle | Yes — PreToolUse | — | (already wired) |
| **Cursor** | Yes — workspace rules + file watchers | Partial — chat-side rules; less granular than PreToolUse | **2× Claude effort** | No canonical event schema; tool name vocabulary differs |
| **Hermes** | Yes — has hooks dir + command approval | Yes — config.yaml command approval | **3× Claude effort** | Different event taxonomy; needs canonical schema |
| **Codex** | No — AGENTS.md is read-only context, no runtime hooks | No — Codex CLI has no PreToolUse equivalent | **5× Claude effort** | Would need a wrapper-CLI proxy that intercepts before passing through to Codex; substantial architecture work |
| **opencode** | Subagent system, but no per-tool-call hook | No | **4× Claude effort** | Same as Codex — needs wrapper or LSP-shaped extension |
| **OMO / OMX** | Skills sync only | No | N/A — identity layer only | Out of scope for hook enforcement |
| **OpenAI Assistants API / MCP servers** | Function-call lifecycle, but server-side | Partial — could intercept at MCP layer | **6× Claude effort** | Would require an episteme MCP server that hosts the canonical event interface |
| **GitHub Copilot / Continue / Cody / generic IDE** | None | None | **9× Claude effort** | Would require an editor extension or LSP wrapper |

**Highest-leverage second adapter**: **Cursor**. Reasoning:
- Has a hook-shaped abstraction (workspace rules + chat-side intercept).
- Substantial user base overlap with Claude Code (developers using AI coding assistants).
- Wiring Cursor proves the canonical-event design *across two hosts*, which validates the abstraction.

**Most architecturally-revealing second adapter**: **Codex**. Wiring Codex (or any AGENTS.md-only host) forces the kernel to confront enforcement *outside* a hook lifecycle — the kernel must either build a wrapper proxy or downgrade enforcement to advisory-only. This pushes the design.

---

## 6. Migration design — canonical event schema

### 6.1 The interface

```
host event           ↓                                  ↓ canonical event       ↓ hook decision
─────────────────    adapter translation layer    ─────────────────────────    ────────────────
{                                                  CanonicalEvent(
  "tool_name":                                       lifecycle: INTENT_TO_EXECUTE,
    "Bash",                                          tool_kind:  SHELL_EXEC,
  "tool_input": {                                    cwd:         "/path",
    "command":                                       correlation_id: "claude-call-123",
      "git push"                                     payload: ShellExecInput(
  },                                                   command_text: "git push"
  "cwd": "/path",                                    ),
  "tool_use_id":                                     host_metadata: { … }
    "claude-call-123"                              )
}
```

### 6.2 Three layers, one decoupling

```
+------------------------------------------------------------+
| Adapter (per-host)                                          |
|   - Translate host events → CanonicalEvent                  |
|   - Translate kernel decisions ← canonical                  |
|   - Register hooks via host's mechanism                     |
+--------------------------+---------------------------------+
                           ↓ canonical event
+------------------------------------------------------------+
| Hook scripts (host-agnostic)                                |
|   - Operate on CanonicalEvent only                          |
|   - Match on ToolKind / Lifecycle enums, not magic strings  |
|   - Emit canonical decisions (proceed / block / advise)     |
+--------------------------+---------------------------------+
                           ↓ pure logic
+------------------------------------------------------------+
| Substrate (`core/hooks/_*.py`)                              |
|   - Already host-agnostic                                   |
|   - Chain integrity, blueprints, scenario detection,        |
|     framework I/O, context-signature hashing                |
+------------------------------------------------------------+
```

### 6.3 Stub interface — `core/hooks/_event_translation.py`

A first-pass design lives at [`/core/hooks/_event_translation.py`](../core/hooks/_event_translation.py) (added in this Event 96 PR — design-only, no runtime). Defines:

- `Lifecycle` enum
- `ToolKind` enum
- `CanonicalEvent` dataclass
- `HostAdapter` protocol — the interface every adapter satisfies
- Translation helpers: `claude_payload_to_canonical(payload: dict) -> CanonicalEvent` (reference implementation)

The current hooks are unchanged. The interface is a target for future migration, not a live dependency.

---

## 7. Recommended sequencing — what to ship first

The audit suggests six phases, in order. Each phase is small, reversible, and produces standalone value.

### Phase 1 — Define the canonical event schema (this PR)
- Add `core/hooks/_event_translation.py` (Protocol + dataclasses, no runtime)
- Add `core/schemas/canonical-event.json` (JSON schema for cross-language adapters)
- Document in `docs/ADAPTER_PORTABILITY.md` (this file)
- **Effort**: ~1 day. **Risk**: low. **Reversibility**: full.

### Phase 2 — Reference translation: Claude payload → canonical
- In `core/hooks/_event_translation.py`, implement `claude_payload_to_canonical()` 
- Build a fixture set: representative Claude payloads + expected canonical translations
- Tests verify round-trip
- **Effort**: ~1 day. **Risk**: low. **Reversibility**: full.

### Phase 3 — Refactor one hook to operate on canonical events
- Pick the simplest: `block_dangerous.py` (57 lines, single-purpose, low surface area)
- Refactor to read canonical events; use Claude translation layer for backward compat
- Existing tests must pass unchanged; behavior identical
- **Effort**: ~half-day. **Risk**: low (one hook, fully tested). **Reversibility**: full.

### Phase 4 — Refactor remaining entry-point hooks (incremental)
- One hook per Event; each on its own PR; each validated against the existing test suite
- Order by simplicity: format.py → test_runner.py → checkpoint.py → … → reasoning_surface_guard.py (last; biggest surface area)
- **Effort**: ~5 days, spread across 18 small PRs. **Risk**: medium (the big guard touches many code paths). **Reversibility**: per-hook.

### Phase 5 — Build the second adapter (Cursor)
- Add `adapters/cursor/` with installer code that registers Cursor's workspace rules pointing at `core/hooks/*.py` 
- Implement Cursor → canonical translation (the reverse of Phase 2)
- Run the same Reasoning Surface contract test suite under Cursor; verify identical decisions
- **Effort**: ~3-5 days. **Risk**: medium-high (Cursor's API surface may not support all canonical events; some hooks may degrade to advisory). **Reversibility**: full.

### Phase 6 — Cross-adapter test parity
- Build a test suite that runs the same canonical-event fixtures through both adapters and verifies identical hook decisions
- Document any host-specific gaps (e.g., "Cursor does not support PreCompact; precompact_backup.py is no-op on Cursor")
- **Effort**: ~2 days. **Risk**: low. **Reversibility**: full.

**Total effort to defensible model-agnostic claim**: ~12-15 working days, spread across 25+ small PRs.

---

## 8. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|:-:|:-:|---|
| Canonical event schema misses a host's load-bearing event | Medium | High | Phase 1 stays in design-only mode; Phase 5 (Cursor) will reveal gaps before Phase 4 (full hook refactor) commits to the schema. If Cursor reveals a needed event, schema gets a v2. |
| Hook refactor introduces behavior regressions | Medium | High | Each hook refactor is its own Event/PR with the existing test suite as a regression gate. Reasoning Surface contract tests must pass identically before merge. |
| Cursor adapter cannot achieve enforcement parity | Medium | Medium | Acceptable. Document the gaps; the canonical schema names which events are required vs optional; hooks degrade to advisory-only for missing-event hosts. |
| The "model-agnostic" claim becomes a perpetual aspiration | Low (high if we don't sequence) | High | This audit is the precondition for honest claims. After Phase 5 ships, the claim becomes defensible; before, the claim must be qualified to "Claude Code today; portable design verified." |
| Codex / opencode never get hook enforcement (no lifecycle to hook into) | High | Medium | Acceptable. AGENTS.md identity layer travels; advisory-only is honest for hookless hosts; document the limitation explicitly. |
| The canonical schema becomes its own coupling layer (kernel ↔ schema instead of kernel ↔ Claude) | Low | Medium | Schema is versioned per Memory Contract pattern; deprecation path exists if a major redesign is needed. |

---

## 9. What this audit does NOT propose

- **No runtime changes** to existing hooks. All Phase 3+ work is sequenced in future Events.
- **No removal of Claude-specific code paths**. Claude remains the reference adapter; backward compat preserved at every step.
- **No claim that Codex / opencode / generic IDEs will get full enforcement parity**. Some hosts genuinely have no hook lifecycle; advisory-only is the honest ceiling for them.
- **No commitment to a deadline**. This is a multi-quarter migration, sequenced for low risk per step.

---

## 10. Closing — what changed about the claim

Before this audit: *"episteme is model-agnostic."*

After this audit: *"episteme's identity layer (kernel + profile + memory) is model-agnostic today, ported to any host that reads markdown. The enforcement layer (hooks + Reasoning Surface contract) is Claude-Code-shaped today. The migration design is documented; the next two adapters can be wired in 12-15 working days against the canonical event schema once it lands. Hosts without a hook lifecycle (Codex, generic IDEs) will get advisory-only enforcement — honest about what's possible, not what we wish were possible."*

That second statement is the defensible one. It is also the one this audit recommends putting on the project's external surfaces (README, marketing, conference talks) the moment it becomes accurate — which is *after* Phase 5 ships, not before.

The honest claim now is the precondition for the strong claim later. The audit is the bridge.
