# Harness System

A **harness** defines the operating environment for a specific project type — execution profile, workflow constraints, safety notes, recommended agents. A generic scaffold gives every project the same shape; a harness gives it the right shape.

## Detect and apply

```bash
episteme detect .
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
episteme harness apply ml-research .
```

Applying a harness writes `HARNESS.md` to the project root and extends `docs/RUN_CONTEXT.md` with profile-specific context — GPU constraints, cost acknowledgment requirements, data safety rules, or dev-server reminders, depending on type.

## Bundled harnesses

| Harness          | Best for                                                                        |
|------------------|---------------------------------------------------------------------------------|
| `ml-research`    | PyTorch / JAX / HuggingFace projects, GPU training, experiment tracking         |
| `python-library` | Packages and libraries intended for distribution or reuse                       |
| `web-app`        | React / Vue / Next.js frontends with optional backend                           |
| `data-pipeline`  | ETL, dbt, Airflow, Prefect, analytics workflows                                 |
| `generic`        | Everything else                                                                 |

## Adding your own

Drop a JSON file into `core/harnesses/`. Fields:

- `id` — stable identifier used by `episteme harness apply <id>`
- `signals` — detection signals (file globs, dependency names, directory presence), each with a score weight
- `execution_profile` — constraints (memory, GPU, long-running tolerance, dev server, data classification)
- `run_context_additions` — blocks appended to `docs/RUN_CONTEXT.md` on apply
- `agents` — recommended subagent personas activated for this project type

The detector walks every `*.json` in `core/harnesses/` and ranks by summed signal score.
