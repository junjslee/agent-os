# AGENTS.md — cognitive-os

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
  CONSTITUTION.md    root claim, four principles, six failure modes
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
src/cognitive_os/ CLI + core library
tests/
```

---

## Build, test, sync

```bash
# Install (idempotent)
pip install -e .

# Verify health
cognitive-os doctor

# Verify kernel integrity
cognitive-os kernel verify   # detects drift in managed files

# Push kernel + profile to all adapters
cognitive-os sync

# Run tests
PYTHONPATH=. pytest -q

# Static check
python3 -m py_compile src/cognitive_os/cli.py
```

All local Python work runs in **Conda `base`** (root: `~/miniconda3` or `$COGNITIVE_OS_CONDA_ROOT`). Homebrew Python is not supported.

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
5. **Handoff.** Update `docs/PROGRESS.md`, `docs/NEXT_STEPS.md`. Name residuals explicitly.

High-impact decisions must record to `.cognitive-os/reasoning-surface.json` before the action. See `kernel/HOOKS_MAP.md`.

---

## Boundaries

### Do NOT touch

- `core/memory/global/*.md` — operator's personal memory; gitignored; writing to it is an identity violation
- `.claude/settings.local.json` — machine-local overrides; gitignored
- `kernel/MANIFEST.sha256` directly — regenerate with `cognitive-os kernel update` after intentional kernel edits
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
- `src/cognitive_os/*` under usual engineering discipline

---

## Prohibited patterns

- **No unattended code-writing-to-merge loops.** Principle IV — the loop needs integrity, not compression past it.
- **No bypassing hooks** with `--no-verify`, `--no-gpg-sign`, or equivalent without explicit user authorization.
- **No `rm -rf`, `git reset --hard`, `git push --force`** without a human checkpoint. `core/hooks/block_dangerous.py` enforces this.
- **No writing to `core/memory/global/`** from any automated flow. It is the operator's first-person memory.
- **No introducing a borrowed concept** into kernel wording without a corresponding `kernel/REFERENCES.md` entry.
- **No claiming universal applicability** for the kernel without updating `kernel/KERNEL_LIMITS.md`.

---

## Commit and handoff conventions

- Commit messages: imperative mood, scoped (`kernel: …`, `docs: …`, `adapters: …`). Checkpoint commits use prefix `chkpt:`.
- Every substantive change updates `docs/PROGRESS.md` with a Reasoning Surface block.
- Every session ends by updating `docs/NEXT_STEPS.md` with a one-sentence "So-What Now?".
- Branch naming: `feat/<name>`, `fix/<name>`, `research/<name>`, `ops/<name>`, `docs/<name>`.

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
