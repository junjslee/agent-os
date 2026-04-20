# Plan

Current active plan for episteme development.

**Core Question (this cycle):** How do we make episteme legible to systems engineers and enterprise adopters without diluting the epistemic depth of the kernel?

**Constraint regime:**
- Allowed: augmenting kernel docs, README, issue templates, ops docs
- Forbidden: modifying `templates/` or `labs/` scaffolds; breaking kernel invariants without Evolution Contract
- Kernel changes require CHANGELOG.md entry first

---

## Active milestone: 0.6.0 — Epistemic control plane positioning

### Goal
Translate the philosophical depth of episteme into language that maps to existing infrastructure-safety intuitions (DbC, OPA, zero-trust, feedforward control), while preserving the kernel's authority and tone.

### Phases

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Bug: fix `marketplace.json` source field schema | complete |
| 2 | Cleanup: remove deprecated HTML viewer, update issue templates | complete |
| 3 | Docs: propagate DbC + feedforward into `CONSTITUTION.md`, `FAILURE_MODES.md`, `KERNEL_LIMITS.md` | complete |
| 4 | Enterprise positioning: README governance framing, zero-trust, human prompt debugging, agnostic-layer | complete |
| 5 | Gap closure: `bug.yml`, `PULL_REQUEST_TEMPLATE.md`, ops docs, README diagram | complete |

### Open assumptions
- `marketplace.json` source field fix (`"."` → GitHub URL) is the correct schema change; unverified until tested against Claude Code's marketplace validator.

---

## Roadmap items (not in current cycle)

- Calibration telemetry (Gap A in KERNEL_LIMITS.md)
- Profile staleness signal — `last_elicited` field + adapter prompt (Gap B)
- Multi-operator mode (Gap C)
- `tacit-call` decision marker (Gap D)
- Control-plane architecture diagram (SVG; replaces ASCII placeholder in README)
