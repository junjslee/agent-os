# PRD: Deterministic Working-Style Profiler and Policy Compiler

## 1) Objective
Build a deterministic setup system that captures an operator's working style and compiles it into reproducible, cross-tool workflow policy.

This system must be:
- platform-agnostic (not tied to Hermes, Claude, or any single tool)
- deterministic (same inputs => same outputs)
- explainable (every inferred score includes evidence)
- overridable (operator can manually adjust or rerun)

## 2) Problem Statement
Current `episteme` setup relies on manually editing global memory files. This is flexible but not systematic.

Gaps:
- no structured intake for working style
- no deterministic inference path from existing repository behavior
- no explicit scorecard that explains policy decisions
- no unified command to generate profile + policy together

## 3) Goals
1. Add `episteme profile` command group with deterministic modes:
  - `survey`: explicit questionnaire-driven scoring
  - `infer`: repository signal-driven scoring
  - `hybrid`: survey + infer merge
2. Produce machine-readable profile artifacts under `core/memory/global/.generated/`.
3. Compile profile scores into human-readable markdown updates:
  - `core/memory/global/operator_profile.md`
  - `core/memory/global/workflow_policy.md`
4. Keep existing user edits safe by default (no overwrite unless requested).
5. Keep adapter-neutral architecture and documentation.

## 4) Non-Goals
- No LLM-based personality inference.
- No hidden telemetry collection.
- No auto-editing of adapter-specific config files in v1.
- No replacement of project-specific memory docs.

## 5) User Stories
- As an operator, I can answer a small survey and get a compiled policy profile quickly.
- As an operator, I can infer my style from an existing repo with transparent evidence.
- As an operator, I can run hybrid mode for better confidence.
- As an operator, I can inspect JSON outputs and understand why each policy level was selected.
- As an operator, I can rerun generation without losing manual notes unless I explicitly overwrite.

## 6) Functional Requirements

### FR-1: New CLI Surface
Add:
- `episteme profile survey [--write] [--overwrite]`
- `episteme profile infer [path] [--write] [--overwrite]`
- `episteme profile hybrid [path] [--write] [--overwrite]`
- `episteme profile show`

Behavior:
- default mode writes generated JSON under `.generated/`
- `--write` also compiles markdown memory files
- `--overwrite` allows replacing existing target markdown files

### FR-2: Deterministic Dimensions
Score dimensions (0..3):
- planning_strictness
- risk_tolerance
- testing_rigor
- parallelism_preference
- documentation_rigor
- automation_level

Interpretation:
- higher = stricter/more structured, except `risk_tolerance` where higher means more conservative risk posture

### FR-3: Survey Mode
Prompt fixed multiple-choice questions (1-4) mapped deterministically to 0..3.
Store:
- responses
- computed scores
- source = `survey`

### FR-4: Infer Mode
Collect deterministic repo signals:
- commit convention usage from recent git log
- test presence ratio in `tests/` or `test_*.py`
- docs presence (`docs/PLAN.md`, `docs/PROGRESS.md`, `docs/NEXT_STEPS.md`)
- CI presence (`.github/workflows/*`)
- worktree branch pattern evidence (`feat/`, `fix/`, `docs/`, `research/`, `ops/`)

Map signals to per-dimension scores with explicit rule table.
Store evidence snippets with each score.

### FR-5: Hybrid Mode
Combine survey + infer with fixed weighted average:
- 60% survey
- 40% infer
Rounded to nearest integer in [0,3].

### FR-6: Compiler Output
Generate:
- `.generated/workstyle_profile.json`
- `.generated/workstyle_scores.json`
- `.generated/workstyle_explanations.md`

With `--write`, compile markdown into:
- `operator_profile.md` (execution preferences + style summary)
- `workflow_policy.md` (policy sections driven by dimensions)

### FR-7: Safe Write Behavior
- If target markdown exists and `--overwrite` absent: do not replace; print guidance.
- Always allow writing generated JSON artifacts.

## 7) Deterministic Rules (v1)

### Survey mapping
Each question offers 4 options mapped directly to 0/1/2/3.

### Infer mapping (examples)
- planning_strictness:
 - +1 if PLAN and NEXT_STEPS exist
 - +1 if commit messages include `plan`/`docs`
 - +1 if project uses staged docs set (`REQUIREMENTS`, `PLAN`, `PROGRESS`, `NEXT_STEPS`)
- testing_rigor:
 - +1 test directory/file presence
 - +1 CI workflow presence
 - +1 if test-related commits in recent history
- documentation_rigor:
 - +1 if `docs/` exists
 - +1 if >=3 authoritative docs exist
 - +1 if docs commits found
- parallelism_preference:
 - +1 if worktree command usage detectable (branch prefixes)
 - +1 if branch diversity includes task-type prefixes
 - +1 if separate docs/review branches observed
- automation_level:
 - +1 if hooks configured (`core/hooks` present)
 - +1 if quality gate/checkpoint hooks are active in config templates
 - +1 if CI present
- risk_tolerance (conservative posture):
 - +1 if destructive guardrails exist
 - +1 if review-gate language present
 - +1 if no-force policy signals observed

Clamp all scores to 0..3.

## 8) Output UX Requirements
- Every run prints:
 - mode
 - score table
 - key evidence bullets
 - file paths written
- `profile show` prints current generated scorecard if available.

## 9) Developer Experience / Maintainability
- Keep logic in `src/episteme/cli.py` for v1 to minimize architecture churn.
- Use helper functions:
 - `_profile_survey()`
 - `_profile_infer(path)`
 - `_profile_hybrid(path)`
 - `_compile_workstyle_policy(...)`
- Keep rule tables as dictionaries/lists with explicit comments.

## 10) Acceptance Criteria
1. New CLI commands parse and run successfully.
2. Running each mode creates JSON artifacts in `.generated/`.
3. Hybrid outputs deterministic weighted merge.
4. `--write` generates operator/workflow markdown deterministically.
5. Existing markdown files are not replaced unless `--overwrite` is set.
6. README documents purpose, commands, and deterministic behavior.
7. Docs explain whether local integration action is required after generation.

## 11) Rollout / Local Integration
- After profile generation with `--write`, operator should run:
 1. `episteme sync` to push updated global memory to adapters
 2. `episteme doctor` to verify runtime
- This should be printed as post-run guidance.

## 12) Risks and Mitigations
- Risk: inferred signals misrepresent intent
 - Mitigation: hybrid mode + explainable evidence + overwrite opt-in
- Risk: perceived lock-in to one platform
 - Mitigation: adapter-neutral language and outputs
- Risk: user loses custom edits
 - Mitigation: default no-overwrite behavior

## 13) Future Extensions (v2+)
- per-project override files
- profile presets (research-heavy, product-delivery, ops-heavy)
- adapter-specific policy emitters from common scorecard
- `profile reconcile` command for human-guided merge of generated + manual policy
