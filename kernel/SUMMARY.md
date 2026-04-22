# Kernel Summary

A 30-line distillation of the entire episteme kernel. Load this first.

---

**Root claim.** The danger is not incompetence. It is *confident wrongness* — fluent answers indistinguishable from examined ones.

**Four principles.**
- **I. Explicit > implicit.** Hidden assumptions are objectives in disguise. Expose the model, including the parts that are wrong.
- **II. Orientation precedes observation.** You do not see reality; you see your model of it. The kernel is orientation infrastructure.
- **III. No model is sufficient alone.** Every lens has a structural blind spot. Convergence across lenses confirms; conflict informs.
- **IV. The loop is the unit of progress.** Frame → Decompose → Execute → Verify → Handoff. A skipped stage defers its cost, not removes it.

**Six reasoner failure modes ↔ counter artifacts. Plus five governance-layer modes (three at v0.11, two added at v1.0 RC).**

| Mode                              | Counter                                    |
|-----------------------------------|--------------------------------------------|
| WYSIATI (reasoning from presence) | Unknowns field (Reasoning Surface)         |
| Question substitution             | Core Question (required in Frame)          |
| Anchoring / first-framing         | Disconfirmation field                      |
| Narrative fallacy                 | Facts / inferences / preferences split     |
| Planning fallacy                  | Failure-first + buffer (high-impact)       |
| Overconfidence                    | Assumptions field + weight-by-track-record |
| Constraint removal w/o understanding | Fence-Check before removing any rule    |
| Measure-as-target drift           | Periodic scorecard audit vs outcome record |
| Controller-variety mismatch       | Escalate-by-default on out-of-coverage ops |
| Framework-as-Doxa (v1.0 RC)       | Layer 3 grounding + Layer 8 protocol-quality verdicts + Phase 12 synthesis-distribution audit |
| Cascade-theater (v1.0 RC)         | Layer 3 entity grounding on `blast_radius_map[]` + Layer 8 "cascade-theater vs real sync" verdict |

**v1.0 RC pillars.** Three additions the substrate cannot perform natively: **(1) Cognitive Blueprints** — four named scaffolds for high-impact decision shapes: **Axiomatic Judgment** (per-decision source-conflict synthesis), **Fence Reconstruction** (constraint-removal safety + rollback smoke test), **Consequence Chain** (irreversible-op decomposition), **Blueprint D · Architectural Cascade & Escalation** (patch-vs-refactor evaluation + symmetric cascade synchronization + deferred-discovery logging — the emergent-flaw counter to cascade-theater) — plus a generic maximum-rigor fallback. **(2) Append-Only Hash Chain** — SHA-256-linked stream across episodic tier + pending contracts + framework protocols. **(3) Framework Synthesis & Active Guidance** — context-indexed protocols surfaced advisory-only at PreToolUse; never blocking.

**Reasoning Surface.** Four fields + two markers, filled in before any consequential action: Knowns, Unknowns, Assumptions, Disconfirmation — plus a **domain** marker (Clear/Complicated/Complex/Chaotic — posture changes accordingly) and a **tacit_call** marker (when the decision rests on calibrated expert intuition). Blank Unknowns = refusal signal. This is a feedforward gate — run before Execute, not as retrospective audit. Evidence updates plausibility; it does not flip booleans. In DbC terms: Preconditions (Knowns + Assumptions), Postconditions (Verify/Handoff), Invariants (this kernel).

**Operator profile (v2).** Two scorecards: **process** axes (how work proceeds, 0–5) and **cognitive-style** axes (how the operator reasons — dominant lens, noise signature, abstraction entry, decision cadence, explanation depth, feedback mode, uncertainty tolerance, asymmetry posture, fence discipline). Per-axis metadata (confidence, last_observed, evidence_refs) + an `expertise_map` + a declared set of **derived behavior knobs** adapters compute from the axes (default autonomy, disconfirmation specificity minimum, preferred lens order, noise-watch set). The profile is a control signal, not documentation.

**Memory architecture.** Five tiers — working (session scratchpad) · episodic (per-decision records) · semantic (cross-session patterns) · procedural (operator-specific action templates) · reflective (memory about memory). Retrieval is query-by-situation, not query-by-key. Promotion is gated: episodic → semantic (pattern + outcome validation) → profile-drift proposal (operator-reviewed, never auto-merged). Forgetting is declared per tier.

**Authority hierarchy.** Project docs > operator profile > kernel defaults > runtime defaults. Most specific explicit truth wins.

**Scope boundary.** See [KERNEL_LIMITS.md](./KERNEL_LIMITS.md) — the kernel is wrong tool for: trivial-cost decisions, disconfirmation paralysis, tacit-dominated work, multi-operator loops, unvalidated calibration claims, rule-based governance against general-capability agents, scorecard-as-target drift.

**Attribution.** Every borrowed concept traced in [REFERENCES.md](./REFERENCES.md).

---

*Next load, in priority order:* [CONSTITUTION.md](./CONSTITUTION.md) · [REASONING_SURFACE.md](./REASONING_SURFACE.md) · [FAILURE_MODES.md](./FAILURE_MODES.md) · [KERNEL_LIMITS.md](./KERNEL_LIMITS.md) · [OPERATOR_PROFILE_SCHEMA.md](./OPERATOR_PROFILE_SCHEMA.md) · [MEMORY_ARCHITECTURE.md](./MEMORY_ARCHITECTURE.md) · [REFERENCES.md](./REFERENCES.md).
