# Memory Contract v1

Purpose: define a portable, deterministic memory model for cognitive-os and adapter runtimes.

This contract is designed for cross-tool continuity (Claude/Codex/Cursor/Hermes) while preserving a single source of truth.

## Scope

Memory classes:
1. Global memory (cross-project operator context)
2. Project memory (repo-local delivery truth)
3. Episodic memory (session/run observations and outcomes)

Authoritative precedence:
1. Project docs/runtime files in repo
2. Global memory in cognitive-os
3. Tool-native/plugin memory caches

Tool-native memory is acceleration only. It is never authoritative by itself.

## Authoritative paths

- Global memory: `core/memory/global/*.md`
- Project memory: `docs/*.md`, `AGENTS.md`, runtime policy docs
- Optional generated artifacts: `core/memory/global/.generated/*` (non-authoritative until compiled)

## Record model

Every memory record (all classes) uses common required fields:

- `id`: stable identifier (UUID preferred)
- `memory_class`: `global | project | episodic`
- `summary`: short, human-readable statement
- `details`: structured content body
- `provenance`: source + actor + timestamp + confidence metadata
- `status`: lifecycle state (`active | superseded | archived`)
- `version`: schema version (`memory-contract-v1`)

## Provenance contract (required)

Provenance fields capture trust and replay context:

- `source_type`: `human | agent | tool | imported`
- `source_ref`: path, URL, or runtime artifact id
- `captured_at`: ISO-8601 UTC timestamp
- `captured_by`: actor/tool identifier
- `confidence`: `low | medium | high`
- `evidence_refs`: optional list of supporting artifacts (tests, logs, diffs, docs)

## Conflict semantics

When records disagree, apply this order:

1. Class precedence
  - project > global > episodic
2. Status
  - `active` preferred over `archived`; `superseded` loses to current active replacement
3. Recency (same class + same authority)
  - latest `captured_at` wins
4. Confidence tie-break
  - `high` > `medium` > `low`
5. Human override
  - explicit human-authored correction wins and should mark prior record as `superseded`

Mandatory behavior:
- Never silently delete conflicting records.
- Keep losing record with `status=superseded` and `supersedes`/`superseded_by` linkage when possible.
- Emit a conflict note in project docs for high-impact decisions.

## Adapter expectations

Adapters SHOULD:
- preserve `id`, `version`, and full `provenance`
- avoid rewriting authoritative class boundaries
- write back durable lessons to authoritative files, not only tool-local stores

Adapters MUST NOT:
- treat local cache memory as authoritative source of truth
- drop provenance fields during sync/transform

## Schemas

JSON Schemas for this contract:
- `core/schemas/memory-contract/common.json`
- `core/schemas/memory-contract/global_record.json`
- `core/schemas/memory-contract/project_record.json`
- `core/schemas/memory-contract/episodic_record.json`
- `core/schemas/memory-contract/memory_envelope.json`

## Versioning

- Backward-incompatible changes require new major contract version (v2).
- Additive fields can be introduced via minor docs update without breaking v1 consumers.
