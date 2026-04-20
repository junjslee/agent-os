# Demo 01 — Attribution Audit

**Premise.** The kernel claims that borrowed concepts (Kahneman's WYSIATI,
Boyd's OODA, Munger's latticework, etc.) are the scaffolding of its four
principles. If that claim is true, every load-bearing borrow should be
traceable to a primary source, named in `kernel/REFERENCES.md`, and cited
at the point of use.

This demo applies episteme **to itself**: run the kernel's own workflow
loop on the question *"is the attribution of this kernel complete and
honest?"* — and ship the resulting artifacts as the demo output.

This is the canonical shape of a episteme deliverable: a
[reasoning-surface.json](./reasoning-surface.json), a
[decision-trace.md](./decision-trace.md), a
[verification.md](./verification.md), and a
[handoff.md](./handoff.md). Reading the four in order reconstructs the
reasoning the operator actually did.

---

## Why this demo

Three reasons.

1. **It is real.** The audit was performed. The repo changes it triggered
   (ten added primary citations, a new `KERNEL_LIMITS.md`, inline
   attribution footers) are visible in the commit history. Nothing in this
   demo is hypothetical.
2. **It is the smallest viable end-to-end.** A single Core Question, a
   single Reasoning Surface, a decomposed plan, a verification against
   success criteria, a handoff with named residuals. Everything the kernel
   contracts for, shown once at minimum size.
3. **It is dogfood.** The kernel is meant to improve decision quality on
   the kind of work the operator actually does. The operator writes this
   repo. The audit is work they had to do anyway. The artifacts are the
   byproduct of doing it correctly.

---

## The workflow loop, instantiated

| Stage     | Artifact                  | What it contains                            |
|-----------|---------------------------|---------------------------------------------|
| Frame     | `reasoning-surface.json`  | Core Question, Knowns, Unknowns, Assumptions, Disconfirmation |
| Decompose | `decision-trace.md`       | Options considered, method chosen, why      |
| Execute   | (commit history)          | The repo edits themselves — `kernel/REFERENCES.md`, `kernel/KERNEL_LIMITS.md`, inline attribution in `CONSTITUTION.md`, `REASONING_SURFACE.md`, `FAILURE_MODES.md` |
| Verify    | `verification.md`         | Did each Knowns/Assumptions claim hold up under re-check? Was the Core Question answered? |
| Handoff   | `handoff.md`              | Residual unknowns, next action, explicit debt |

---

## How to read this demo

Start with [`reasoning-surface.json`](./reasoning-surface.json) to see the
decision as it was framed. Then [`decision-trace.md`](./decision-trace.md)
to see which option was chosen and why. Then
[`verification.md`](./verification.md) to see what held up and what didn't.
Then [`handoff.md`](./handoff.md) to see what was left for the next cycle.

If you use episteme on a real piece of work, this is the shape of
artifact you should end up with. Not longer. Not shorter.

---

## Reuse

The four-file pattern is the canonical form. Copy this folder, empty the
files, and instantiate them for your own Core Question. An adapter may
eventually scaffold this automatically; for now, the directory itself is
the template.
