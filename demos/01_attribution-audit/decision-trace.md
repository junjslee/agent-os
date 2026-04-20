# Decision Trace — Attribution Audit

This document records the Decompose stage: the options considered, the
method chosen, and the because-chain from signal to decision.

---

## Core Question (reprise)

Are the concepts load-bearing the episteme kernel attributed to their
primary sources — or is the kernel presenting borrowed ideas as its own?

---

## Options considered

### Option A — Preserve current four citations; add a disclaimer

Keep REFERENCES.md at Kahneman/Munger/Boyd/Dalio and add a single line:
*"many other concepts inform this work."* Lowest effort, lowest honesty.

- **For:** zero additional reading; REFERENCES.md stays small.
- **Against:** the disclaimer is rhetorical, not accountable. A reader
  cannot trace any specific kernel wording to its origin. Fails Principle
  I: the constraint ("we borrowed from many places") is named but not
  explicit.

### Option B — Expand REFERENCES.md to a full reading list (30+ entries)

Cite every author whose work touches the themes of the kernel, including
secondary influences and useful adjacent reading.

- **For:** demonstrates the intellectual breadth behind the project.
- **Against:** REFERENCES.md becomes a bibliography, not an attribution
  map. A reader cannot tell which source was *load-bearing* (the kernel
  wording depends on it) vs which is *adjacent* (useful reading, not
  directly influential). Violates signal-over-noise: the signal (specific
  attribution) gets buried in the noise (breadth of reading).

### Option C — Targeted primary-source attribution with inline pointers (chosen)

Identify every concept in the kernel that is (a) load-bearing, (b)
borrowed, (c) currently unattributed. Add the primary source to
REFERENCES.md with a concept-to-wording table. Add a brief "See also"
footer in each kernel file that points readers to the relevant
REFERENCES.md entries. Structure REFERENCES.md into "primary" (load-bearing)
vs "secondary" (adjacent) sections.

- **For:** honest about lineage; structure makes attribution traceable;
  inline pointers preserve reading flow while closing the audit loop.
- **Against:** requires an actual audit — concept-by-concept — not just a
  list of names. Higher effort. Only option that survives Principle I.

---

## Chosen: Option C

**Because-chain:**

- *Signal:* The operator's own cognitive_profile.md names its influences
  precisely; the kernel files did not. The mismatch is evidence that the
  kernel's attribution was incidental, not load-bearing.
- *Inferred cause:* Attribution was done once, informally, and never
  re-audited as the kernel grew. Concepts were borrowed and rephrased into
  kernel vocabulary; the bridge back to the primary source was never
  written.
- *Decision:* Do the audit. Treat every load-bearing concept in kernel
  wording as a claim that requires a primary-source footnote. Structure
  REFERENCES.md so a reader can cross the bridge in both directions —
  from concept to source (top of entry) and from source to where it lives
  in the kernel (cross-reference line).

The governing intent (make borrowed cognition visible and auditable) is
an application of Principle I. Option A and B both leave the attribution
silent or unstructured; Option C operationalizes it.

---

## Concepts identified as load-bearing and unattributed

Assembled by walking every kernel file and tagging each claim:

| Concept in kernel wording               | Primary source                                       | Kernel file                     |
|-----------------------------------------|------------------------------------------------------|---------------------------------|
| Falsifiability / disconfirmation field  | Popper, *Conjectures and Refutations* (1963)         | REASONING_SURFACE.md            |
| Signal vs noise                         | Shannon, *Mathematical Theory of Communication* (1948) | cognitive_profile.md (global), kernel decision protocol |
| Tacit vs explicit knowledge boundary    | Polanyi, *Personal Knowledge* (1958)                 | CONSTITUTION.md Principle I, KERNEL_LIMITS.md |
| Leverage points / mental models shape system | Meadows, *Leverage Points* (1999)               | CONSTITUTION.md Principle II    |
| Pattern language as composable partial models | Alexander, *A Pattern Language* (1977)         | CONSTITUTION.md Principle III   |
| PDSA cycle as ancestor of the workflow loop | Deming / Shewhart                                | CONSTITUTION.md Principle IV    |
| Bounded rationality under cost          | Simon, *Administrative Behavior* (1947)              | CONSTITUTION.md Principle III, KERNEL_LIMITS.md |
| Espoused theory vs theory-in-use        | Argyris & Schön, *Theory in Practice* (1974)         | CONSTITUTION.md Principle I     |
| Writing-as-thinking; plain language     | Graham (essays), Orwell (*Politics and the English Language*) | CONSTITUTION.md Principle I |
| Antifragility / convexity under stress  | Taleb, *Antifragile* (2012)                          | KERNEL_LIMITS.md, workflow_policy.md |
| Causal reasoning vs correlation         | Pearl, *The Book of Why* (2018)                      | cognitive_profile.md, kernel decision protocol |

Ten primary sources added. Plus ~15 secondary (Dewey, Schön reflective
practice, Senge, Edmondson, Catmull, Russell & Norvig, Mitchell, Chollet,
Marcus, Lakatos, Allen, Newport, Hofstadter) that inform adjacent themes
but are not load-bearing on specific kernel wording.

---

## Method choice: why inline pointers beat centralized citations

Two candidate forms:

1. **Centralized only.** REFERENCES.md carries all attribution; kernel
   files stay citation-free.
2. **Inline pointers + centralized entries.** Each kernel file ends with a
   brief "Attribution" section listing the 2–4 primary sources whose
   concepts govern that file, pointing to REFERENCES.md for detail.

Form 2 chosen. Rationale: a reader inside CONSTITUTION.md should not have
to leave the file to learn that Principle II inherits Boyd's OODA and
Meadows on leverage points. The inline pointer closes the loop in the
place the reasoning is being done. REFERENCES.md remains the single source
of truth for full citation — the inline pointer is navigation, not
duplication.

Failure condition: if inline pointers drift out of sync with
REFERENCES.md, the kernel says one thing in one place and another in
another. Mitigation: inline pointers are keyword-level ("Polanyi on
tacit/explicit") not full citations, so the only thing to keep in sync is
the spelling of the name.

---

## Scope boundary declared

Out of scope for this cycle: building calibration telemetry, writing a
multi-operator mode, or converting the kernel to a runtime that enforces
the Reasoning Surface as a hard gate. These are named as residuals in
handoff.md and in KERNEL_LIMITS.md as declared gaps.

In scope: the audit itself, the ten additions, the inline pointers,
KERNEL_LIMITS.md, and this demo as the artifact of the work.
