# AGENTS.md — episteme

> Operational contract for any AI coding agent working inside this repository.
> Human-facing documentation: [`README.md`](./README.md). Durable
> first-principles: [`kernel/`](./kernel/).

If you have 500 tokens, load [`kernel/SUMMARY.md`](./kernel/SUMMARY.md).
Everything below is the operational contract; it does not replace the kernel.

---

## What this repository is

A portable cognitive kernel for AI agents. The kernel is markdown
(vendor-neutral). Adapters mount the kernel into specific runtimes
(Claude Code, Hermes, future). The kernel defines *how the agent thinks*;
everything else in this repo is delivery plumbing.

**Do not treat this repo as a general-purpose codebase.** It is a
governance + cognition product whose own artifacts are its thesis.

---

## Repository map (what lives where)

```
kernel/          philosophy; markdown; vendor-neutral; the contract
  SUMMARY.md     load first (30-line distillation)
  CONSTITUTION.md    root claim, four principles, nine failure modes (+2 planned for v1.0 RC: framework-as-Doxa, cascade-theater)
  REASONING_SURFACE.md   Knowns/Unknowns/Assumptions/Disconfirmation
  FAILURE_MODES.md       named modes ↔ counter artifacts
  OPERATOR_PROFILE_SCHEMA.md  how operators encode their worldview
  KERNEL_LIMITS.md       when this kernel is the wrong tool
  REFERENCES.md          attribution for every load-bearing borrow
  CHANGELOG.md           versioned kernel history
  HOOKS_MAP.md           kernel invariants ↔ runtime hooks
  MANIFEST.sha256        kernel integrity digest

demos/           reference deliverables produced by the loop itself
  01_attribution-audit/  canonical four-artifact shape; start here

core/
  memory/global/    operator's personal memory (gitignored; do NOT write)
  hooks/            deterministic safety + workflow hooks
  harnesses/        per-project-type operating environments
  schemas/          memory + evolution contract JSON schemas
  adapters/         adapter target configurations
  agents/           subagent persona definitions

adapters/claude/  Claude Code delivery layer
adapters/hermes/  Hermes (OMO) delivery layer
skills/           reusable operator skills (custom/vendor/private)
templates/        project scaffolds, example answer files
docs/             architecture, contracts, setup guides
src/episteme/    CLI + core library
tests/
```

---

## Build, test, sync

```bash
# Install (idempotent)
pip install -e .

# Verify health
episteme doctor

# Verify kernel integrity
episteme kernel verify   # detects drift in managed files

# Push kernel + profile to all adapters
episteme sync

# Run tests
PYTHONPATH=. pytest -q

# Static check
python3 -m py_compile src/episteme/cli.py
```

Local Python work runs in whichever Python invokes the CLI (`sys.executable`). Pin a specific runtime via `$EPISTEME_PYTHON_PREFIX` (install root) or `$EPISTEME_PYTHON` (exact binary). Set `EPISTEME_REQUIRE_CONDA=1` to enforce Conda `base`.

---

## Kernel invariants (do NOT modify without the Evolution Contract)

1. The four principles in `kernel/CONSTITUTION.md` are load-bearing. Adding, removing, or reframing one requires a major version bump in `kernel/CHANGELOG.md` and a propose → critique → gate → promote loop per `docs/EVOLUTION_CONTRACT.md`.
2. The six-failure-mode taxonomy in `kernel/FAILURE_MODES.md` is a 1:1 mapping. Removing a counter artifact means naming which failure mode is now unprotected. If the answer is "none" — the artifact was not earning its place.
3. The Reasoning Surface is four fields: Knowns, Unknowns, Assumptions, Disconfirmation. Do not rename or collapse them.
4. `kernel/KERNEL_LIMITS.md` declares the kernel's boundary. Claims to universal applicability without updating this file violate Principle I.
5. `kernel/REFERENCES.md` is the attribution contract. Introducing a new load-bearing concept into kernel wording without a primary-source entry violates Principle I.

---

## Workflow convention for non-trivial work

All consequential edits follow the kernel's own loop:

1. **Frame.** State the Core Question in one sentence. Identify the uncomfortable friction driving the work.
2. **Decompose.** Fill the Reasoning Surface (Knowns / Unknowns / Assumptions / Disconfirmation). For high-impact work, provide 2+ options with trade-offs and an explicit because-chain.
3. **Execute.** Prefer smallest reversible action that produces new information. One bounded lane per task owner.
4. **Verify.** Validate against success criteria, not effort. Re-check each assumption. Evaluate hypothesis: validated / refined / invalidated.
5. **Handoff.** Maintainer: update the project's authoritative operational record (PROGRESS / NEXT_STEPS may be private staging) and name residuals explicitly. External contributors: include a Handoff section in the PR description (what shipped, what's left, named residuals) — the maintainer integrates this into the operational record on merge.

High-impact decisions must record to `.episteme/reasoning-surface.json` before the action. See `kernel/HOOKS_MAP.md`.

---

## Boundaries

### Do NOT touch

- `core/memory/global/*.md` — operator's personal memory; gitignored; writing to it is an identity violation
- `.claude/settings.local.json` — machine-local overrides; gitignored
- `kernel/MANIFEST.sha256` directly — regenerate with `episteme kernel update` after intentional kernel edits
- Any file matching `**/.env*`, `secrets/*`, private keys

### Handle with care (checkpoint before acting)

- `kernel/*.md` — load-bearing contract; see kernel invariants above
- `docs/MEMORY_CONTRACT.md`, `docs/EVOLUTION_CONTRACT.md` — governance specs
- `core/schemas/*` — versioned JSON schemas; breaking changes require a contract version bump
- Adapters (`adapters/*`, `core/adapters/*.json`) — delivery layer; changes here can silently desync operator profiles across runtimes

### Safe to edit freely

- `docs/*.md` (except the contract files above)
- `skills/custom/*`, `skills/private/*`
- `templates/*`
- `tests/*`
- `src/episteme/*` under usual engineering discipline

---

## Prohibited patterns

- **No unattended code-writing-to-merge loops.** Principle IV — the loop needs integrity, not compression past it.
- **No bypassing hooks** with `--no-verify`, `--no-gpg-sign`, or equivalent without explicit user authorization.
- **No `rm -rf`, `git reset --hard`, `git push --force`** without a human checkpoint. `core/hooks/block_dangerous.py` enforces this.
- **No writing to `core/memory/global/`** from any automated flow. It is the operator's first-person memory.
- **No introducing a borrowed concept** into kernel wording without a corresponding `kernel/REFERENCES.md` entry.
- **No claiming universal applicability** for the kernel without updating `kernel/KERNEL_LIMITS.md`.

---

## Git workflow protocol — always-clean-master

> **Why this exists.** Every Event in this repo follows the pattern *branch off master → commit → push → merge back to master.* Three Events in a row (54 / 55-56 / 57) have hit the same recurring failure: `git merge --ff-only <feature-branch>` on local master fails with `Diverging branches can't be fast-forwarded`. Root cause: the chkpt hook (`core/hooks/checkpoint.py`) commits to whatever branch HEAD points at — commonly `master` — which silently diverges local master from origin/master. Once diverged, no fast-forward path exists, and operators fall back to manually opening a PR each time. The fix below holds whether or not the chkpt hook is later fixed at its root.

**Rule.** Use this exact sequence for every Event. Deviation reproduces the divergence.

### Pre-Event (before any work begins)

1. `git fetch origin`
2. Verify clean working tree: `git status` must read `nothing to commit, working tree clean`. If not — commit, stash, or revert before continuing.
3. Sync local master to origin. Order is load-bearing — `git checkout master` MUST happen BEFORE `git pull` (see Footgun A in `### Common footguns` below). Two paths depending on local state:
   - **Local master is clean and merely behind origin** →
     ```bash
     git checkout master                  # FIRST — switch off any feature branch
     git pull --ff-only origin master     # THEN — fast-forward master cleanly
     ```
     Doing these as one chained `&&` is fine, but the order matters: pull operates on the currently-checked-out branch. Running `pull` while still on a feature branch advances the FEATURE BRANCH past its remote-tracking ref and triggers Footgun A later.
   - **Local master has diverged** (chkpt commits or any local-only commits) → operator runs in their own terminal: `cp -R archive /tmp/archive-backup-pre-event` (only if `archive/` has files); `git checkout master`; `git reset --hard origin/master`; `cp -R /tmp/archive-backup-pre-event/. archive/` (restore). The agent **must not** attempt the hard-reset itself — `core/hooks/block_dangerous.py` blocks it; that block is operator policy, respected.
4. Branch off origin/master directly (avoids any leftover local-master state):
   ```bash
   git checkout -b event-NN-shortname origin/master
   ```
5. Begin work.

### During Event

6. All commits land on the feature branch. **Never commit directly to local master.** All work — including small typo fixes — goes through a feature branch.
7. **Never run `git merge` on local master.** Merging happens on origin (via PR) or via post-merge sync (step 11 below), not via local merge.
8. Conventional-commit messages, imperative mood, scoped: `kernel: …`, `docs: …`, `feat(scope): …`, `fix(scope): …`, etc. Checkpoint commits keep prefix `chkpt:` (existing chkpt hook still uses it).

### Ship Event — pick exactly one path

**Path A · PR-merge (default; preferred when local master may be diverged).**

```bash
git push -u origin event-NN-shortname
gh pr create --title "..." --body "..."     # or via GitHub UI
# Operator merges via GitHub UI or `gh pr merge --merge` (NOT --squash, NOT --rebase)
```

The merge-commit strategy preserves the audit trail matching Pillar 2's append-only ethos. Squash collapses the audit; rebase rewrites it.

**Path B · local fast-forward (only when local master is verified clean and synced AND origin permits direct push to master).**

```bash
git push -u origin event-NN-shortname
git checkout master
git pull --ff-only origin master            # confirm clean ancestor
git merge --ff-only event-NN-shortname
git push origin master
```

If step 3 of Path B fails (any divergence) — abort Path B, switch to Path A. Don't fight the divergence locally; let GitHub handle it.

**Path B caveat — branch protection.** Path B requires origin to permit direct push to master. When master branch protection is enforced (e.g., a `Require a pull request before merging` rule, recommended for any episteme deployment), `git push origin master` returns `GH006: Protected branch update failed for refs/heads/master. Changes must be made through a pull request.` and Path B is impossible. **On `junjslee/episteme`: branch protection IS enforced — Path A only.** Verify protection state on a fresh repo with `gh repo view --json branchProtectionRules,defaultBranchRef`. If branch protection is on, do not even attempt Path B; jump straight to Path A.

### Post-Event sync (BEFORE the next Event begins)

After a PR merges or a local-ff push completes:

9. `git checkout master`
10. `git fetch origin`
11. **Operator runs in their own terminal** (block_dangerous policy): `git reset --hard origin/master`. Restore `/archive/` if needed: `cp -R /tmp/archive-backup-pre-event/. archive/`.
12. Verify: `git log --oneline -5` shows the merge commit at HEAD. `git status` is clean.
13. Optional: delete the local feature branch — `git branch -d event-NN-shortname`. After a PR-merge this `-d` may refuse with `not deleting branch ... not yet merged to refs/remotes/origin/event-NN-...-prep, even though it is merged to HEAD` (Footgun B in `### Common footguns` below). The fix is `git branch -D event-NN-shortname` (force-delete) — safe in this case because the branch's tip commit IS the parent of the merge commit on master; all content is preserved. Optionally also delete the stale remote branch: `git push origin --delete event-NN-shortname`.

### Why this works

- **No local master commits → no divergence class.** The chkpt hook's local-master-commit behavior is sidestepped because operator never sits on master while working.
- **Every Event starts from origin/master directly.** Step 4's `git checkout -b event-NN-shortname origin/master` makes the branch root deterministic, regardless of local-master state.
- **PR-merge always works.** Path A doesn't depend on local-master state at all. Path B is the optimization for the clean case.
- **Post-Event hard-reset re-mirrors local to origin.** Step 11 makes local master a known-clean copy of origin/master, ready for the next Event's step 3.

### Patterns that reproduce the failure (do NOT use)

- Branching off local master without first syncing — inherits any chkpt divergence.
- `git merge --no-ff` on local master after a PR merge already landed — creates a duplicate merge commit that conflicts with origin.
- `git rebase event-NN-shortname onto master` — rewrites already-pushed feature commits.
- `gh pr merge --squash` — collapses the per-commit audit trail. Reserve for backport flows; not the default.

### Long-term root-cause fix (deferred)

The recurring divergence comes from `core/hooks/checkpoint.py` committing to local HEAD. Real fix options for v1.0.1+:

- Have the chkpt hook commit to a dedicated `chkpt/YYYY-MM-DD` branch instead of HEAD, OR
- Have it write to `~/.episteme/state/chkpt-snapshots/` (untracked) instead of git-committing.

Either kills the divergence class entirely. Soak-incompatible right now (touches `core/hooks/`); logged as deferred-discovery for the v1.0.1 cycle. The protocol above holds regardless of when the hook fix lands.

### Common footguns

Two recurring failure modes the protocol above is designed to prevent. Each names the SYMPTOM (so you recognize it in your terminal output) and the FIX. Codified Event 61 after both were observed across Events 56-60.

#### Footgun A · `git pull` on feature branch advances it past remote-tracking ref

**Symptom.** You're on a feature branch (e.g., `event-NN-shortname`). You run `git pull --ff-only origin master` to "sync local master." It says `Updating <SHA>..<SHA>  Fast-forward` and reports the diff stat. **You weren't on master.** The pull just advanced your CURRENT branch (the feature branch) by pulling origin/master into it. Your local feature-branch HEAD is now ahead of `origin/<feature-branch>` (the remote tracking ref). When you later try `git branch -d <feature-branch>`, it refuses with `error: the branch '<feature-branch>' is not fully merged ... If you are sure you want to delete it, run 'git branch -D'`.

**Why it happens.** `git pull` operates on the currently-checked-out branch, regardless of the source argument. `git pull --ff-only origin master` means "fast-forward CURRENT branch by pulling origin/master into it" — not "fast-forward LOCAL master." If your CURRENT branch is `event-NN-shortname`, that's the branch that advances.

**Fix.** Always `git checkout master` BEFORE `git pull`. The Pre-Event step 3 above codifies this order explicitly. If you've already hit Footgun A, the recovery is in Footgun B.

#### Footgun B · Post-PR-merge `git branch -d` refuses with stale-upstream-tracking complaint

**Symptom.** Your PR has merged on origin (verified by `git log --oneline origin/master | head -1` showing the merge commit). You're on local master, synced to origin/master. You run `git branch -d event-NN-shortname` to clean up. Git refuses with:

```
warning: not deleting branch 'event-NN-shortname' that is not yet merged to
         'refs/remotes/origin/event-NN-shortname', even though it is merged to HEAD
error: the branch 'event-NN-shortname' is not fully merged
hint: If you are sure you want to delete it, run 'git branch -D event-NN-shortname'
```

The phrase **"even though it is merged to HEAD"** is the load-bearing tell — git itself confirms the branch IS merged to master.

**Why it happens.** When a PR merges on origin, the source branch on origin (`origin/event-NN-shortname`) is NOT auto-deleted or auto-updated; it stays at whatever SHA was the last push. Your local feature-branch's UPSTREAM tracking ref still points at that stale origin SHA. Meanwhile your local feature-branch HEAD may have advanced (Footgun A) OR stayed where it was — but EITHER way, `git branch -d` checks the local-vs-upstream relationship, sees the upstream is stale, and refuses. It's checking the wrong thing. The branch IS merged to master (via the merge commit on master, whose parent IS the branch's tip).

**Fix.** `git branch -D event-NN-shortname` (force-delete). Safe here because: (a) git itself confirmed `even though it is merged to HEAD`; (b) the branch's tip commit is reachable from master via the merge commit; (c) `-D` only removes the local ref pointer, not the underlying commits. Optionally also delete the stale remote branch:

```bash
git branch -D event-NN-shortname
git push origin --delete event-NN-shortname
```

`-D` is the operator-only command on this repo — `block_dangerous.py` may refuse the agent's attempt depending on its substring rules. Operator runs both lines themselves; ~5 seconds.

**When NOT to use `-D`.** If the branch genuinely has unmerged work (e.g., a feature branch you abandoned mid-Event without merging), `-d` refuses for the right reason. Distinguish Footgun B from a real unmerged-work case by the `even though it is merged to HEAD` line in the warning — that line confirms safety. If git's warning does NOT say `merged to HEAD`, the branch has real unmerged commits and you must decide: merge them or accept the loss.

---

## Commit and handoff conventions

- Commit messages: imperative mood, scoped (`kernel: …`, `docs: …`, `adapters: …`). Checkpoint commits use prefix `chkpt:`.
- Maintainer workflow: every substantive change updates the project's authoritative operational record (PROGRESS / NEXT_STEPS — may be in private staging) with a Reasoning Surface block, and every session ends with a one-sentence "So-What Now?".
- External contributor workflow: include the Reasoning Surface block + "So-What Now?" inline in the PR description; the maintainer integrates these into the operational record on merge. Contributors do not need to update operational docs themselves.
- Branch naming: `event-NN-shortname` for maintainer-ordered Events (numbering tracked in the maintainer's operational record); `feat/<name>`, `fix/<name>`, `research/<name>`, `ops/<name>`, `docs/<name>` for non-Event work.

---

## Scaling by delegation

Subagents live in `core/agents/` and install into `~/.claude/agents/`.

- **Planner** — multi-step sequencing and risk mapping.
- **Researcher** — deep dives into codebases, docs, unknown libraries.
- **Implementer** — focused staged coding once the plan is solid.
- **Reviewer** — cross-referencing implementation against requirements and safety.
- **Orchestrator** — parallel workstream coordination.
- **Structural governance:** domain-architect, reasoning-auditor, governance-safety, domain-owner.

Every delegation begins with a **Shared Context Brief** and ends with a **Verification Artifact**.

---

## When to stop and ask

Stop and surface to the human operator before:

- Editing `kernel/*.md` in any way other than fixing a typo.
- Introducing a new runtime adapter.
- Modifying `core/schemas/*`.
- Any irreversible operation (force-push, hard reset, branch deletion, history rewrite).
- Any change that would require bumping `kernel/CHANGELOG.md` major.

The kernel's Principle IV rule applies to itself: small reversible actions beat large irreversible bets. Asking is cheap. Recovery is not.

---

## Attribution

This file inherits its discipline from the kernel:
- Workflow convention — Deming / Shewhart (PDSA), Boyd (OODA tempo).
- Reasoning Surface — Popper (disconfirmation), Kahneman (WYSIATI counter).
- Boundaries — Principle I (explicit > implicit): what is not named is not governed.

Full sources: [`kernel/REFERENCES.md`](./kernel/REFERENCES.md).
