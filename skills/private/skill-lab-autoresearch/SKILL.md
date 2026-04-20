---
name: skill-lab-autoresearch
description: Private Claude-only lab skill for iteratively improving a copied skill candidate with explicit evaluation goals and manual promotion.
---
Use this skill only for private skill-lab work inside `~/episteme`.

This wrapper is inspired by `olelehmann100kMRR/autoresearch-skill`, but it is adapted for a private lab workflow where live skills are never edited directly.

## Required Inputs
Before doing any work, collect or confirm:
- `target_candidate_path`: path to a copied candidate `SKILL.md` under `labs/skills/<skill-name>/candidate/`
- `eval_goal`: what improvement is being optimized
- `iteration_cap`: maximum number of iterations
- `output_dir`: path under `labs/skills/<skill-name>/runs/`

If any of these are missing, stop and ask for them.

## Hard Refusals
Refuse the task if `target_candidate_path` points anywhere inside:
- `skills/custom/`
- `skills/vendor/`
- `~/.claude/skills/`
- `~/.codex/skills/`

Refuse the task if `output_dir` is not inside `labs/skills/<skill-name>/runs/`.

Refuse any request to overwrite a live skill automatically.

## Workflow
1. Validate the target path is a lab candidate copy.
2. Read the candidate `SKILL.md`.
3. Clarify the evaluation objective and the iteration limit.
4. Propose a compact evaluation rubric tied to the stated goal.
5. Generate one revised candidate at a time.
6. Record observations, tradeoffs, and reasons for each revision under `output_dir`.
7. Stop when:
  - the iteration cap is reached
  - the objective appears satisfied
  - further changes are speculative
8. Finish with:
  - the current best candidate path
  - an evaluation summary
  - a promotion recommendation

## Outputs
Produce:
- revised candidate content or patch guidance for the lab copy
- concise evaluation notes
- a recommendation: keep iterating, promote manually, or discard

## Promotion Rule
Promotion into the live skill set is always manual.

Do not copy changes into `skills/house` or `skills/vendor`.
