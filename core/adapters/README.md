# Adapter Registry

Each file in this directory defines how `episteme sync` delivers the cognitive contract to a specific agent platform.

## Why this exists

Platform configuration paths and conventions change. By encoding each adapter as a declarative JSON file rather than hardcoding paths in Python, episteme can:
- be updated for a platform change by editing one JSON file
- support community-contributed adapters by dropping a new JSON file here
- document exactly what each adapter does and doesn't touch
- provide a machine-readable registry for `episteme doctor` conformance checks

## File format

Each adapter JSON has:
- `name`: internal identifier
- `display`: human-readable label
- `detect`: how to determine if this platform is installed (`commands` checked via which, `paths` checked for existence)
- `docs_url`: official documentation for this platform's configuration
- `sync`: what gets written and where
- `project_contract`: the per-project file this platform reads for behavioral instructions
- `notes`: known quirks, constraints, and cross-platform behavior

## Current adapters

| File | Platform | Project contract |
|---|---|---|
| `claude.json` | Claude Code | `CLAUDE.md` |
| `codex.json` | Codex CLI | `AGENTS.md` |
| `opencode.json` | opencode | `AGENTS.md` |
| `hermes.json` | Hermes Agent | `AGENTS.md` |

## Adding a new adapter

1. Create `<name>.json` following the format above.
2. Implement `_sync_<name>_runtime()` in `src/episteme/cli.py` referencing the JSON for paths.
3. Call it from `_sync_user_runtime()`.
4. Add a `[ok]` / `[missing]` check in `_doctor()`.
5. Document it in `adapters/<name>/README.md`.

## Keeping adapters current

When an adapter platform changes its configuration paths or conventions:
1. Check `docs_url` for the current official docs.
2. Update the JSON file.
3. Update the corresponding `_sync_*` function in cli.py.
4. Run `episteme sync` and `episteme doctor` to verify.
