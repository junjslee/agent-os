# Handoff — Attribution Audit

The last step of the loop: name what was decided, name what was left, and
produce the minimum context the next cycle needs to pick up cleanly.

---

## What was decided

1. Load-bearing borrowed concepts in the kernel must be traceable to
   primary sources. Attribution is a Principle I obligation, not a
   courtesy.
2. `kernel/REFERENCES.md` is the single source of truth for citations,
   structured into *primary* (load-bearing) and *secondary* (adjacent)
   sections. Primary entries carry a concept-to-wording table.
3. Inline "Attribution" footers in each kernel file point readers to
   REFERENCES.md using keyword-level source names (not full citations),
   so that drift cost is minimal.
4. The kernel declares its own boundary. `kernel/KERNEL_LIMITS.md` names
   six conditions under which the kernel is misapplied and four gaps
   the kernel does not yet close. A discipline without a declared
   boundary is a creed.

---

## What was shipped

- `kernel/REFERENCES.md` — expanded from 4 to 14 primary entries + ~15
  secondary, each primary with concept→wording table.
- `kernel/KERNEL_LIMITS.md` — new. Six named limits, four declared gaps.
- `kernel/CONSTITUTION.md` — attribution section expanded;
  KERNEL_LIMITS.md linked from "what it is not."
- `kernel/REASONING_SURFACE.md` — Attribution footer added (Popper,
  Kahneman, Dalio).
- `kernel/FAILURE_MODES.md` — Attribution footer added (Kahneman,
  Popper, Shannon, Dalio).
- `demos/01_attribution-audit/` — this demo. Four artifacts demonstrating
  the kernel's workflow loop applied to a real decision.

---

## What was explicitly left for next cycles

Each item has a named trigger — the signal that the next cycle should
pick it up.

### 1. Calibration telemetry

**What.** A lightweight mechanism (append-only `decisions/*.md` or a
single ledger) to record each decision's assumptions, disconfirmation
conditions, and observed outcome — so the kernel's efficacy is itself
falsifiable.

**Trigger.** Before the next claim that episteme *works*. Right now
the claim is coherence-based; telemetry would make it outcome-based.

**Pointer.** `kernel/KERNEL_LIMITS.md` section "A. Calibration
telemetry."

### 2. Attribution regression check

**What.** A doctor check (`episteme doctor --kernel`) that scans
kernel files for named concepts and flags any that do not appear in
REFERENCES.md's primary section. Prevents the attribution audit from
decaying to a point-in-time property.

**Trigger.** Next time a new concept is introduced into kernel wording.
Or: whenever `HOOKS_MAP.md` is next revised.

### 3. Profile staleness mechanism

**What.** `last_elicited` timestamp on each operator profile file, with
a soft prompt when the threshold (90 days default) is exceeded.

**Trigger.** Next operator-profile revision. The author's own profile is
at `core/memory/global/` — that is the first test site.

**Pointer.** `kernel/KERNEL_LIMITS.md` section "B. Profile staleness."

### 4. Multi-operator mode

**What.** An explicit contract for loops with two or more operators
whose cognitive profiles materially differ. First-class dissent (cf.
Edmondson); named authority per decision class; reconciliation as a
constraint-regime negotiation rather than averaging.

**Trigger.** First real collaborative use of episteme with a second
person. Not before — the design should be driven by real friction, not
speculative symmetry.

**Pointer.** `kernel/KERNEL_LIMITS.md` section "C. Team and pair
workflows."

### 5. Tacit-call decision mode

**What.** An explicit marker on decision records (`tacit-call: true`)
for decisions governed by craft judgment. Skip the fabricated-Knowns
failure; track tacit→explicit migration over time.

**Trigger.** First time a decision is recorded where the real driver is
taste or craft, not evidence. Likely comes up in the next design-heavy
session.

**Pointer.** `kernel/KERNEL_LIMITS.md` section "D. Tacit/explicit
trade-off unmodeled."

---

## The next concrete action

The next session should restructure `README.md` and
`docs/assets/system-overview.svg` so that the repository reads
*demo-first* (like medsci-skills) — a new user should see `demos/` early,
understand what episteme *does* via this audit artifact, and only
then encounter the philosophical kernel.

That action is reversible, produces immediate feedback (any new visitor
to the repo is the verifier), and depends on nothing external. Exactly
the shape of "next reversible action" the workflow contract asks for.

---

## Carried-forward assumptions

- **The operator will audit this handoff.** If they do not, the handoff
  has not completed. Handoff is not a write; it is a transfer with
  receipt.
- **The audit's claim that "no load-bearing concept remains
  unattributed" is bounded by current visibility.** A future reader may
  find one. Expected. That reader triggering an update is the
  regression check working the way it should.
- **This demo is the first, not the canonical.** Future demos (a real
  engineering decision audited the same way; a research-planning loop;
  a hiring call) will stress-test the four-file pattern further. If the
  pattern survives three real uses, it earns the right to be a template.
