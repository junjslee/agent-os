# Anthropic Managed Agents Bridge

Purpose: import Managed Agents runtime event logs into `episteme` Memory Contract v1 envelopes as `episodic` records.

This bridge is additive and non-breaking:
- It does not change `episteme sync` behavior.
- It does not modify existing adapters.
- It writes bridge output under `core/memory/bridges/anthropic-managed/` unless you override `--output`.

## Why this exists

Managed runtimes and `episteme` operate at different layers:
- Managed runtime: execution substrate — agent loop, sandboxes/tools, runtime event durability.
- `episteme`: cognitive control plane — identity, governance, cross-runtime authoritative memory.

The bridge connects these layers by transforming runtime events into portable memory envelopes that episteme can promote, audit, and sync.

## Input formats

`episteme bridge anthropic-managed` accepts either:

1) JSON object with an `events` array (preferred)
```json
{
  "session_id": "sess_abc123",
  "events": [
    {"type": "tool_call", "tool": "bash", "input": {"cmd": "pytest -q"}},
    {"type": "error", "message": "flaky timeout"}
  ]
}
```

2) Top-level JSON array
```json
[
  {"type": "decision", "summary": "Use smaller batch size"},
  {"type": "tool_call", "tool": "bash", "input": {"cmd": "python train.py"}}
]
```

## Command

```bash
episteme bridge anthropic-managed \
  --input /path/to/managed-events.json \
  --project-id my-project-id
```

Useful options:
- `--output <path>`: custom output file path
- `--session-id <id>`: override session id
- `--source-ref <ref>`: override provenance source reference
- `--captured-by <actor>`: provenance captured_by (default: `episteme bridge`)
- `--confidence low|medium|high` (default: `medium`)
- `--dry-run`: parse + summarize without writing output

## Output

Envelope file (default path):
- `core/memory/bridges/anthropic-managed/<session-id>.memory-envelope.json`

Envelope shape:
```json
{
  "contract_version": "memory-contract-v1",
  "records": [
    {
      "id": "<uuid>",
      "memory_class": "episodic",
      "summary": "...",
      "details": {"event_index": 0, "event": {...}},
      "provenance": {
        "source_type": "imported",
        "source_ref": "...",
        "captured_at": "...",
        "captured_by": "...",
        "confidence": "medium",
        "evidence_refs": ["..."]
      },
      "status": "active",
      "version": "memory-contract-v1",
      "session_id": "...",
      "event_type": "action"
    }
  ]
}
```

Event type mapping (runtime → memory contract):
- `tool_call`, `tool_result`, `action`, `execute`, `command`, `bash` → `action`
- `error`, `exception`, `failure` → `error`
- `decision` → `decision`
- `verification`, `assertion`, `check` → `verification`
- `handoff` → `handoff`
- anything else → `observation`

## Recommended promotion loop

1. Import runtime events via bridge.
2. Review episodic records and extract durable lessons.
3. Promote durable lessons into authoritative files:
   - global: `core/memory/global/*.md`
   - project: `docs/*`, `AGENTS.md`
4. Run `episteme sync` to propagate updated contract.

This preserves source-of-truth discipline while still learning from managed runtime execution.
