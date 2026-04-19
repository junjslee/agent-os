# Setup — Profile, Cognition, One-Command

Deterministic onboarding for cognitive-os. Two axes:

- **profile** — *how work runs* (planning, testing, docs, automation).
- **cognition** — *how decisions are made* (reasoning depth, challenge style, uncertainty posture).

Treat `survey` / `infer` outputs as a starting point, not doctrine. For long-term quality, author your authoritative philosophy in `core/memory/global/cognitive_profile.md` using a top-down structure (reasoning → agency → adaptation → governance → operating thesis), then sync.

## Modes

- `survey` — explicit questionnaire, 4-level choices mapped to scores 0..3.
- `infer` — deterministic repo-signal scoring (docs / tests / CI / branch patterns / guardrails).
- `hybrid` — weighted merge (`60% survey + 40% infer`, rounded).

`survey` and `hybrid` accept `--answers-file templates/profile_answers.example.json` for non-interactive runs.

## Scored dimensions (all 0..3)

**Workstyle profile:**
`planning_strictness` · `risk_tolerance` · `testing_rigor` · `parallelism_preference` · `documentation_rigor` · `automation_level`.

**Cognitive profile:**
`first_principles_depth` · `exploration_breadth` · `speed_vs_rigor_balance` · `challenge_orientation` · `uncertainty_tolerance` · `autonomy_preference`.

## Commands

```bash
cognitive-os profile survey --answers-file templates/profile_answers.example.json
cognitive-os profile infer .
cognitive-os profile hybrid . --answers-file templates/profile_answers.example.json --write
cognitive-os profile show
```

Generated artifacts land under `core/memory/global/.generated/`:
- `workstyle_profile.json`
- `workstyle_scores.json`
- `workstyle_explanations.md`
- `personalization_blueprint.md` (combined user system profile)

To compile generated scores into global memory files:

```bash
cognitive-os profile hybrid . --write --overwrite
cognitive-os sync
cognitive-os doctor
```

## One-command setup (execution + thinking)

```bash
# Interactive
cognitive-os setup . --interactive

# Non-interactive with explicit post-steps
cognitive-os setup . --write --sync --governance-pack strict --doctor

# Fully scripted (survey/hybrid non-interactive requires answer files)
cognitive-os setup . \
  --profile-mode hybrid \
  --cognition-mode infer \
  --profile-answers-file templates/profile_answers.example.json \
  --cognition-answers-file templates/profile_answers.example.json \
  --write --overwrite --sync --doctor
```

**Defaults.** Non-interactive: `profile-mode=infer`, `cognition-mode=infer`. Interactive: asks whether to use questionnaire onboarding; if yes, both default to `survey`. `write`, `overwrite`, `sync`, `doctor` default to `false` (preview first). `governance-pack=balanced` when `--sync` is enabled.

**Answer-file precedence.**
1. `--profile-answers-file` / `--cognition-answers-file` (most specific)
2. `--answers-file` fallback for both

## Terminal tools (recommended)

Agents running under cognitive-os expect these to be present. `cognitive-os doctor` verifies them.

- `rg` (ripgrep) — codebase search; fast, respects `.gitignore`
- `fd` — file discovery; cleaner than `find`
- `bat` — syntax-highlighted file inspection
- `sd` — safer regex in-place replacements
- `ov` — pager that handles wide output and ANSI cleanly
