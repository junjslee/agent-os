"""Canonical event schema for cross-adapter portability — Event 96 design stub.

DESIGN-ONLY. This module defines the interface every adapter will satisfy
once the migration sequenced in `docs/ADAPTER_PORTABILITY.md` ships. It
contains:

  * Lifecycle / ToolKind / Decision enums
  * CanonicalEvent + ShellExecInput / FileWriteInput / FileEditInput payloads
  * HostAdapter Protocol — the interface every adapter implements
  * `claude_payload_to_canonical()` reference implementation (the only host
    currently translated; serves as the worked example for new adapters)

NO HOOKS IMPORT THIS MODULE TODAY. Existing hooks operate directly on Claude-
shaped payloads (per Phase 0 reality documented in
`docs/ADAPTER_PORTABILITY.md` § 3). Phase 3+ of the migration migrates one
hook at a time to consume CanonicalEvent instead.

Importing this module costs nothing — no runtime side effects, no I/O, no
process spawning. It is a vocabulary, not a runtime.

The canonical schema is versioned. Today: v1. Schema changes that break
canonical-event consumers are governance events (per kernel Evolution
Contract); minor additions are not.

See also:
  * `docs/ADAPTER_PORTABILITY.md` — the audit that motivated this module
  * `core/schemas/canonical-event.json` — JSON schema mirror for cross-language adapters (TODO Phase 1)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Protocol, Union, runtime_checkable


SCHEMA_VERSION = "canonical-event/v1"


# ── Enums ───────────────────────────────────────────────────────────────────


class Lifecycle(str, Enum):
    """When in the host's tool-call lifecycle the event fires.

    Mapping to host-specific event names is the adapter's responsibility.
    Hosts that lack an equivalent for a given lifecycle phase MUST declare
    it as unsupported in `HostAdapter.supported_lifecycles()`; hooks that
    depend on the absent phase degrade to no-op or advisory on that host.
    """

    INTENT_TO_EXECUTE = "intent_to_execute"
    """Host is about to invoke a tool. Hooks may BLOCK by returning DENY."""

    EXECUTION_COMPLETED = "execution_completed"
    """Host has finished invoking a tool. Hooks observe outcome (calibration,
    state tracking, telemetry). Cannot block — already executed."""

    SESSION_OPENED = "session_opened"
    """Host opens a new agent session. Hooks may print context banners,
    seed state, etc."""

    SESSION_CLOSED = "session_closed"
    """Host closes a session. Hooks may run final QA gates (tests pass?),
    persist state, perform handoff snapshots."""

    CONTEXT_COMPACTING = "context_compacting"
    """Host is about to compact long-running session context. Hooks may
    snapshot transcripts before loss."""

    PERMISSION_REQUESTED = "permission_requested"
    """Host is requesting permission for an op the operator has not
    pre-authorized. Hooks may auto-allow / deny / forward."""


class ToolKind(str, Enum):
    """What kind of tool the host is invoking.

    Hosts use different vocabularies (Claude: 'Bash' / 'Write' / 'Edit' /
    'MultiEdit'; Cursor: 'run_terminal_cmd' / 'edit_file'; Codex: function-
    call by name; ...). The adapter maps host vocabulary → ToolKind.

    `OTHER` is the fallback for tool kinds the canonical schema does not
    yet cover. Hooks that specialize on a specific ToolKind will skip
    `OTHER` events; hooks that operate on all events will see them.
    """

    SHELL_EXEC = "shell_exec"
    """Execute a shell command. Equivalent to Claude's 'Bash'."""

    FILE_WRITE = "file_write"
    """Write a new file. Equivalent to Claude's 'Write'."""

    FILE_EDIT = "file_edit"
    """Edit an existing file (single edit). Equivalent to Claude's 'Edit'."""

    FILE_MULTI_EDIT = "file_multi_edit"
    """Multiple edits to the same file in one call. Equivalent to Claude's
    'MultiEdit'."""

    FILE_READ = "file_read"
    """Read a file (rarely intercepted; reads are usually low-impact)."""

    NETWORK_FETCH = "network_fetch"
    """Network call (HTTP, MCP server, etc.). Often intercepted for
    egress policy."""

    AGENT_TASK = "agent_task"
    """Spawn a sub-agent / dispatch to another agent. Equivalent to
    Claude's 'Task' / 'Agent'."""

    OTHER = "other"
    """Tool kind not yet in the canonical vocabulary. Adapter should still
    set `host_tool_name` so hooks can disambiguate if needed."""


class Decision(str, Enum):
    """Hook decision returned to the adapter.

    The adapter translates Decision back to its host's expected return
    code / response shape (Claude: exit 0 = ALLOW, exit 2 = DENY; other
    hosts may use different signals).
    """

    ALLOW = "allow"
    """Op proceeds. Hook may have written advisory to stderr."""

    DENY = "deny"
    """Op is blocked. Hook MUST emit operator-visible reason on stderr."""

    ADVISORY = "advisory"
    """Op proceeds but hook emitted advisory message. Equivalent to ALLOW
    for hosts that don't distinguish; hosts that surface advisory text
    differently can use this signal."""

    NO_OP = "no_op"
    """Hook did nothing meaningful (event not relevant to this hook).
    Equivalent to ALLOW from the host's perspective."""


# ── Payload variants ────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ShellExecInput:
    """Canonical input for ToolKind.SHELL_EXEC events."""

    command_text: str
    """The shell command, normalized to a single string. Adapter is
    responsible for joining argv lists, dequoting, etc."""

    description: Optional[str] = None
    """Optional human-facing description of the command (Claude provides
    this; other hosts may not)."""


@dataclass(frozen=True)
class FileWriteInput:
    """Canonical input for ToolKind.FILE_WRITE events."""

    target_path: str
    """Absolute or cwd-relative path of the file being written."""

    content: Optional[str] = None
    """File content if available at hook-time. Adapters MAY omit this
    for size reasons; hooks that need content must handle absence."""


@dataclass(frozen=True)
class FileEditInput:
    """Canonical input for ToolKind.FILE_EDIT events."""

    target_path: str
    old_text: Optional[str] = None
    new_text: Optional[str] = None


@dataclass(frozen=True)
class GenericInput:
    """Catch-all input for ToolKind.OTHER and tool kinds not yet modeled.

    The full host-shaped tool input is preserved under `host_payload` so
    hooks that need host-specific fields can still access them, while
    portable hooks operate on canonical fields only.
    """

    host_payload: dict
    """The original host tool_input dict, unmodified."""


ToolInput = Union[
    ShellExecInput,
    FileWriteInput,
    FileEditInput,
    GenericInput,
]


# ── Tool response (for EXECUTION_COMPLETED events) ──────────────────────────


@dataclass(frozen=True)
class ToolResponse:
    """Canonical response shape for EXECUTION_COMPLETED events.

    Hosts disagree wildly on response field names — the audit
    documented Claude's `returnCodeInterpretation` + `interrupted` shape,
    Gemini's `isError` bool, conventional `exit_code`, etc. The adapter
    MUST translate to this canonical shape:
    """

    exit_code: Optional[int]
    """Numeric exit code if available; None if host doesn't surface one
    (in which case `status` is the load-bearing signal)."""

    status: str
    """One of: 'success', 'error', 'unknown'. Always populated."""

    stdout: Optional[str] = None
    stderr: Optional[str] = None
    interrupted: bool = False


# ── The canonical event ─────────────────────────────────────────────────────


@dataclass(frozen=True)
class CanonicalEvent:
    """The single shape every hook consumes after Phase 4 of the migration.

    Today no hook reads CanonicalEvent — Phase 3+ migrate them one at a
    time. This dataclass is the migration target.
    """

    schema_version: str
    """Always SCHEMA_VERSION (`canonical-event/v1`) for events emitted by
    this module. Future schema versions live alongside; consumers SHOULD
    check version compatibility."""

    lifecycle: Lifecycle
    tool_kind: ToolKind
    cwd: str
    correlation_id: str
    """Stable id for joining INTENT_TO_EXECUTE ↔ EXECUTION_COMPLETED
    events for the same op. Hosts that don't provide one: adapter MUST
    synthesize via SHA-1 over (timestamp, cwd, command_text) so paired
    hooks produce the same id."""

    tool_input: ToolInput
    """Type-narrowed input. Hooks that specialize on a ToolKind can rely
    on the matching dataclass shape."""

    tool_response: Optional[ToolResponse] = None
    """Populated only for EXECUTION_COMPLETED; None for other lifecycles."""

    host_tool_name: Optional[str] = None
    """The original host vocabulary tool name (e.g. 'Bash', 'run_terminal_cmd').
    Hooks SHOULD prefer ToolKind enum; this field is for debugging /
    advisory text / host-specific fallbacks."""

    host_metadata: dict = field(default_factory=dict)
    """Adapter escape hatch — anything host-specific that may matter to a
    hook but isn't canonical. Use sparingly; prefer extending the schema
    when a field becomes load-bearing across multiple hosts."""


# ── HostAdapter Protocol ────────────────────────────────────────────────────


@runtime_checkable
class HostAdapter(Protocol):
    """The interface every adapter implements.

    Implementations live under `adapters/<host_name>/` and are wired into
    `episteme sync` so the right adapter is invoked when registering
    hooks for a given host.
    """

    name: str
    """Stable identifier — `'claude'`, `'cursor'`, `'hermes'`, etc."""

    def supported_lifecycles(self) -> set[Lifecycle]:
        """Lifecycles this host can fire. Hooks that depend on absent
        lifecycles will be registered as no-op on this host."""
        ...

    def supported_tool_kinds(self) -> set[ToolKind]:
        """Tool kinds this host distinguishes. Hosts that only have
        coarse-grained tool calls may map all to OTHER."""
        ...

    def to_canonical(self, host_payload: dict) -> CanonicalEvent:
        """Translate a host-shaped JSON payload into a CanonicalEvent.

        MUST NOT raise for malformed payloads — adapter should return a
        best-effort event with `tool_kind = OTHER` and
        `host_metadata['translation_warning']` populated.
        """
        ...

    def from_decision(self, decision: Decision) -> int:
        """Translate a hook Decision back to the host's expected exit
        code. Default convention: ALLOW = 0, DENY = 2, ADVISORY = 0,
        NO_OP = 0. Hosts with different conventions override this."""
        ...

    def install_hooks(
        self,
        hooks_dir: str,
        registration_target: Optional[str] = None,
    ) -> None:
        """Register the kernel's hook scripts with the host's hook
        mechanism. Adapter-specific: Claude writes ~/.claude/settings.json;
        Cursor writes workspace rules; Hermes writes config.yaml; etc."""
        ...


# ── Reference implementation: Claude payload → CanonicalEvent ───────────────


_CLAUDE_TOOL_KIND_MAP: dict[str, ToolKind] = {
    "Bash": ToolKind.SHELL_EXEC,
    "Write": ToolKind.FILE_WRITE,
    "Edit": ToolKind.FILE_EDIT,
    "MultiEdit": ToolKind.FILE_MULTI_EDIT,
    "Read": ToolKind.FILE_READ,
    "WebFetch": ToolKind.NETWORK_FETCH,
    "WebSearch": ToolKind.NETWORK_FETCH,
    "Task": ToolKind.AGENT_TASK,
    "Agent": ToolKind.AGENT_TASK,
}

_CLAUDE_LIFECYCLE_MAP: dict[str, Lifecycle] = {
    # Claude's hook event names. Set by the adapter when registering
    # hooks; included in the payload only on some Claude versions.
    "PreToolUse": Lifecycle.INTENT_TO_EXECUTE,
    "PostToolUse": Lifecycle.EXECUTION_COMPLETED,
    "SessionStart": Lifecycle.SESSION_OPENED,
    "Stop": Lifecycle.SESSION_CLOSED,
    "SubagentStop": Lifecycle.SESSION_CLOSED,
    "PreCompact": Lifecycle.CONTEXT_COMPACTING,
    "PermissionRequest": Lifecycle.PERMISSION_REQUESTED,
}


def claude_payload_to_canonical(
    payload: dict,
    *,
    lifecycle_hint: Optional[Lifecycle] = None,
) -> CanonicalEvent:
    """Reference translation: Claude Code stdin payload → CanonicalEvent.

    Lifecycle resolution order:
      1. If `payload['hook_event_name']` is present and known, use the
         `_CLAUDE_LIFECYCLE_MAP` mapping (some Claude Code versions
         include the event name on the payload itself).
      2. Otherwise use `lifecycle_hint` (the lifecycle the hook is wired
         to via settings.json — the adapter knows because it registered
         the hook for that specific event).
      3. Default to `Lifecycle.INTENT_TO_EXECUTE`.

    This function is illustrative — in the migration's Phase 2 it becomes
    the only place Claude's payload shape is referenced; every hook
    consumes the resulting CanonicalEvent.
    """
    lifecycle = (
        _CLAUDE_LIFECYCLE_MAP.get(
            str(payload.get("hook_event_name") or payload.get("hookEventName") or "")
        )
        or lifecycle_hint
        or Lifecycle.INTENT_TO_EXECUTE
    )
    host_tool_name = (
        payload.get("tool_name") or payload.get("toolName") or ""
    ).strip()
    tool_kind = _CLAUDE_TOOL_KIND_MAP.get(host_tool_name, ToolKind.OTHER)

    raw_input = payload.get("tool_input") or payload.get("toolInput") or {}
    if not isinstance(raw_input, dict):
        raw_input = {}

    if tool_kind is ToolKind.SHELL_EXEC:
        tool_input: ToolInput = ShellExecInput(
            command_text=str(
                raw_input.get("command")
                or raw_input.get("cmd")
                or raw_input.get("bash_command")
                or ""
            ),
            description=raw_input.get("description"),
        )
    elif tool_kind is ToolKind.FILE_WRITE:
        tool_input = FileWriteInput(
            target_path=str(
                raw_input.get("file_path")
                or raw_input.get("path")
                or raw_input.get("target_file")
                or ""
            ),
            content=raw_input.get("content"),
        )
    elif tool_kind is ToolKind.FILE_EDIT:
        tool_input = FileEditInput(
            target_path=str(
                raw_input.get("file_path")
                or raw_input.get("path")
                or raw_input.get("target_file")
                or ""
            ),
            old_text=raw_input.get("old_string"),
            new_text=raw_input.get("new_string"),
        )
    else:
        tool_input = GenericInput(host_payload=dict(raw_input))

    response_data = payload.get("tool_response") or payload.get("toolResponse")
    response: Optional[ToolResponse] = None
    if isinstance(response_data, dict):
        response = _claude_response_to_canonical(response_data)

    correlation_id = (
        payload.get("tool_use_id")
        or payload.get("toolUseId")
        or payload.get("request_id")
        or _synthesize_correlation_id(payload, tool_input)
    )

    return CanonicalEvent(
        schema_version=SCHEMA_VERSION,
        lifecycle=lifecycle,
        tool_kind=tool_kind,
        cwd=str(payload.get("cwd") or ""),
        correlation_id=str(correlation_id),
        tool_input=tool_input,
        tool_response=response,
        host_tool_name=host_tool_name or None,
        host_metadata={
            "host": "claude",
            "raw_payload_keys": sorted(payload.keys()),
        },
    )


def _claude_response_to_canonical(resp: dict) -> ToolResponse:
    """Translate Claude's tool_response shape to canonical.

    Mirrors `core/hooks/calibration_telemetry.py` extraction logic. Once
    Phase 3 lands and that hook consumes CanonicalEvent, the extraction
    code unifies here and that hook becomes a thin caller.
    """
    exit_code: Optional[int] = None
    for key in ("exit_code", "exitCode", "returncode", "return_code", "status_code"):
        v = resp.get(key)
        if isinstance(v, int):
            exit_code = v
            break

    if exit_code is None:
        for bool_key in ("isError", "is_error"):
            if bool_key in resp and isinstance(resp[bool_key], bool):
                exit_code = 1 if resp[bool_key] else 0
                break

    interrupted = bool(resp.get("interrupted", False))
    if exit_code is None and interrupted:
        exit_code = 130  # SIGINT convention

    rci = resp.get("returnCodeInterpretation")
    if exit_code is None and ("returnCodeInterpretation" in resp or "isImage" in resp):
        if rci is None or (isinstance(rci, str) and not rci.strip()):
            exit_code = 0
        elif isinstance(rci, str):
            import re as _re
            m = _re.search(r"exit\s+code\s+(-?\d+)", rci, _re.IGNORECASE)
            exit_code = int(m.group(1)) if m else 1

    if exit_code is None:
        status = "unknown"
    elif exit_code == 0:
        status = "success"
    else:
        status = "error"

    return ToolResponse(
        exit_code=exit_code,
        status=status,
        stdout=resp.get("stdout"),
        stderr=resp.get("stderr"),
        interrupted=interrupted,
    )


def _synthesize_correlation_id(payload: dict, tool_input: ToolInput) -> str:
    """When the host doesn't provide a correlation id, synthesize one.

    Mirrors the SHA-1 fallback in `calibration_telemetry.py`.
    """
    import hashlib
    import time

    cwd = str(payload.get("cwd") or "")
    bucket = str(int(time.time()))
    if isinstance(tool_input, ShellExecInput):
        seed = f"{bucket}|{cwd}|{tool_input.command_text}"
    elif isinstance(tool_input, (FileWriteInput, FileEditInput)):
        seed = f"{bucket}|{cwd}|{tool_input.target_path}"
    else:
        seed = f"{bucket}|{cwd}|other"
    return "h_" + hashlib.sha1(seed.encode("utf-8", errors="replace")).hexdigest()[:16]


__all__ = [
    "SCHEMA_VERSION",
    "Lifecycle",
    "ToolKind",
    "Decision",
    "ShellExecInput",
    "FileWriteInput",
    "FileEditInput",
    "GenericInput",
    "ToolInput",
    "ToolResponse",
    "CanonicalEvent",
    "HostAdapter",
    "claude_payload_to_canonical",
]
