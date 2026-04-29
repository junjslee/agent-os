# Agent Feedback

Agent-learned behavioral rules that apply across projects. This file is imported into `~/.claude/CLAUDE.md` by `episteme sync`.

This file is **distinct from operator-authored policy** (`overview.md`, `operator_profile.md`, `workflow_policy.md`, `python_runtime_policy.md`, `cognitive_profile.md` — all of which encode what the operator committed to up-front). Entries here are behavioral rules the agent learned during sessions, confirmed by the operator, and promoted to global scope because they apply regardless of project or tool.

## How to classify new agent-learned feedback

When an agent learns a new behavioral rule during a session, classify before filing:

1. **Scope.** Does the rule apply everywhere (**universal**), wherever a specific pattern exists (**universal-principled**), or only in the current project (**project-specific**)?
2. **Source.** Is it **operator-authored policy** — the operator explicitly committed to a posture that predates the session — or **agent-learned feedback** — the operator corrected/confirmed a behavior during interaction?

File accordingly:

- Universal + agent-learned → this file, under "Universal rules"
- Universal-principled + agent-learned → this file, under "Universal-principled rules", with the triggering pattern explicitly named
- Project-specific + agent-learned → per-project auto-memory at `~/.claude/projects/<project>/memory/*.md`; do NOT promote to global
- Operator-authored policy → separate global file (`operator_profile.md`, `workflow_policy.md`, etc.); do NOT mix into this file

**Promotion bar.** An agent should not unilaterally promote a feedback memory to global. Two conditions must hold: (a) the operator explicitly confirms cross-project scope, AND (b) the rule does not contradict existing operator-authored policy. If either is absent, the rule stays per-project until re-audited.

**Anti-duplication.** When a rule lands here, delete the corresponding per-project copy so the same guidance does not live in two places with drift risk. Source of truth moves with the promotion.

---

## Universal rules

Rules that apply everywhere, regardless of project, tool, or context.

<!--
Format for entries (replace this comment with rules as you accumulate them):

### <Rule title — one line>

**Rule.** State the rule plainly. Specifically forbidden / required: <list>.

Applies to: <every surface where the rule must hold — commit messages,
PR bodies, issue comments, etc.>.

**Why.** Explain the reason the rule was promoted. Often a past incident
or strong operator preference. The reason is what lets future agents
judge edge cases instead of blindly following the rule.

**How to apply.** State the operational steps. When does the rule trigger?
What's the default behavior to override?
-->

_No universal rules yet. Add entries above as agent-learned cross-project rules accumulate._

---

## Universal-principled rules

Rules whose **principle** is universal but whose **trigger** is a specific pattern. The rule applies wherever the triggering pattern exists, and is a no-op elsewhere.

<!--
Format for entries (replace this comment with rules as you accumulate them):

### <Rule title — one line>

**Triggering pattern.** Describe the specific pattern that activates this
rule. The rule should be a no-op when the pattern is absent.

**Rule.** State the rule plainly within the triggering pattern.

**Why.** Explain the reason. Often a structural property of projects with
this pattern that makes the rule load-bearing.

**How to apply.** What does the agent do when the trigger fires?
What's the default behavior, and what's the override path?
-->

_No universal-principled rules yet. Add entries above as patterned rules emerge._
