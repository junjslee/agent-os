# Customization

Three places you can shape episteme to your own working life: personal memory, skills, and hooks.

## Personal memory

Edit `core/memory/global/*.md` — these are gitignored and never leave your machine. The `*.example.md` files in the same directory are committed templates that show what belongs in each file.

Recommended additions:
- `core/memory/global/build_story.md` from `build_story.example.md` — a short, stable builder narrative (not project-specific details).

### The story layer (mental model + narrative memory)

To keep your system explainable in your own head (and to teammates), add:
- **Global:** `core/memory/global/build_story.md` — your stable builder narrative.
- **Project:** `docs/DECISION_STORY.md` — what/why/how trace for major decisions in a specific repository.

```bash
cp core/memory/global/build_story.example.md core/memory/global/build_story.md
```

Why this matters:
- Avoids "good reasoning but no coherent story."
- Preserves decision intent across sessions and tools.
- Improves handoffs by keeping causal context intact.

## Skills

- `skills/custom/` — your own skills, synced globally.
- `skills/vendor/` — curated upstream skills (declare in `runtime_manifest.json`).
- `skills/private/` — **sync-exemption boundary** for experimental / WIP / project-only skills. Tracked publicly in this repo, but **not propagated** by `episteme sync` to your global skill library. The "private" here means *local-only sync exemption*, not operator-private content (which uses the separate `~/episteme-private/` symlink pattern documented in `AGENTS.md` § Doc classification policy).

Each skill is a folder with a `SKILL.md`. See [`SKILLS_AND_PERSONAS.md`](./SKILLS_AND_PERSONAS.md) for what ships and provenance rules.

## Hooks

Edit scripts in `core/hooks/`. All hooks run under Conda `base` Python — no extra dependencies. Paths resolve dynamically so the same scripts work on any machine. See [`HOOKS.md`](./HOOKS.md) for the hook reference and governance packs.

### Python runtime override

By default the CLI uses whichever Python invoked it (`sys.executable`). To pin a specific runtime:

```bash
export EPISTEME_PYTHON_PREFIX=/path/to/prefix   # e.g. ~/miniconda3, .venv
# or pick the binary directly:
export EPISTEME_PYTHON=/path/to/bin/python
# Legacy fallbacks still honored: EPISTEME_CONDA_ROOT, COGNITIVE_OS_CONDA_ROOT
```

Set `EPISTEME_REQUIRE_CONDA=1` to make `episteme doctor` fail when Conda isn't present.

## Project scaffold

`episteme new-project [path]` creates:

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
  settings.json          permission rules
  settings.local.json    machine-local overrides (gitignored)
```
