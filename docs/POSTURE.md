# What cognitive-os installs: an epistemic posture

One-line answer to *what is this*:

> **cognitive-os installs an epistemic posture. The artifacts are how the posture becomes enforceable.**

Every other framing (memory layer, agent runtime, prompt library, plugin kit) is
a downstream description of the delivery surface, not the thing being delivered.

---

## What a posture is

A *posture* is an actively maintained stance — how a reasoner holds themselves
before, during, and after a decision. It has three observable dimensions:

| Dimension              | What it governs                                                      |
|------------------------|----------------------------------------------------------------------|
| **Texture of thought** | Which questions get asked, which unknowns get named, which assumptions get flagged as load-bearing. |
| **Texture of action**  | Which options are admitted to the decision space, which are pre-rejected, and under what conditions the plan must pivot. |
| **Rationale**          | The because-chain from signal → inferred cause → chosen path. The audit trail, not the conclusion. |

A posture is not a mood, not a checklist, and not a personality. It is a
structured way of showing up — and the structure is what makes it coachable,
auditable, and transferable across operators and runtimes.

## Why *posture*, not *disposition* / *framework* / *prompt*

- **Not disposition.** "Disposition" skews toward innate temperament. cognitive-os
  is not something you *have* — it is something you *practice*, maintained
  against specific, named failure modes.
- **Not framework.** A framework is inert until someone wields it. A posture is
  already-wielded: the reasoner is in-stance or out-of-stance at every moment.
- **Not prompt.** A prompt is a per-call nudge. A posture survives across
  sessions, tools, and operator changes — it lives in markdown that outlives
  the runtime.

The word *posture* appears across the kernel's own memory files
(`cognitive_profile.md` → "Working posture"; `operator_profile.md` → "Risk
posture", "Testing posture", "Documentation posture") because that is the
category of thing being configured.

## How the posture becomes enforceable

The posture would be aspirational without artifacts that *make it visible*.
Each canonical artifact enforces one dimension:

| Artifact                                              | What it enforces                                                                 |
|-------------------------------------------------------|---------------------------------------------------------------------------------|
| [`reasoning-surface.json`](../kernel/REASONING_SURFACE.md) | Texture of thought: Core Question + Knowns / Unknowns / Assumptions / Disconfirmation before action. |
| [`decision-trace.md`](../demos/01_attribution-audit/decision-trace.md) | Texture of action: options considered, because-chain, rejection conditions, load-bearing concepts. |
| [`verification.md`](../demos/01_attribution-audit/verification.md)     | Rationale-under-audit: each assumption graded, each disconfirmation condition checked, residual unknowns kept honest. |
| [`handoff.md`](../demos/01_attribution-audit/handoff.md)               | Posture persistence: what shipped, what was pre-rejected and why, what the next session must not re-litigate. |

These four files are the *visible form* of the posture. An agent operating in
the posture emits them; an agent operating outside the posture does not. This
is the testable property.

## How to tell the posture is working

Two signals:

1. **Refusals that sound pedantic out-of-frame.** A posture-holding agent
   refuses to answer "add a cache?" before a diagnosis exists. Outside the
   posture, the refusal looks like friction. Inside, it looks like the first
   decision of the cycle.
2. **Pre-stated pivot conditions.** Before a hypothesis is tested, the agent
   has already written the condition under which it will be abandoned. If no
   such condition exists, the posture has lapsed into unfalsifiable advocacy.

The canonical 60-second demonstration is
[`demos/02_debug_slow_endpoint/`](../demos/02_debug_slow_endpoint/): same
scenario, same operator, same tools — the posture rejected the fluent-wrong
answer (*add a Redis cache*) at the Core Question gate and produced a
schema-level root cause instead. The differential version is
[`demos/03_differential/`](../demos/03_differential/): side-by-side output
with the posture *off* vs. *on* on the same prompt.

## Why this framing matters for delivery

If cognitive-os is pitched as a *memory system*, the reasonable buyer asks
"vs. mem0?" If pitched as a *framework*, the buyer asks "vs. LangChain?" Both
framings route the conversation into a category where cognitive-os is not the
best-in-class answer — and shouldn't be.

Pitched as **the posture layer** — installed beneath whichever memory
substrate and whichever runtime you use — the comparison collapses. mem0 and
Memori are substrates for the posture to write into. Claude Code and Hermes
are runtimes for the posture to execute in. The posture itself is the durable
thing.

```
                      ┌────────────────────────────────┐
                      │        epistemic posture       │   ← cognitive-os
                      │  (reasoning surface, failure   │     installs this
                      │   modes, decision trace,       │
                      │   verification, handoff)       │
                      └────────────────────────────────┘
                              │              │
                  writes into ▼              ▼ executes inside
          ┌────────────────────┐    ┌───────────────────────┐
          │   memory substrate │    │     agent runtime     │
          │  (mem0, memori,    │    │  (Claude Code, Hermes,│
          │   postgres, files) │    │   Codex, future)      │
          └────────────────────┘    └───────────────────────┘
```

## What stays constant, what is swappable

- **Constant:** the four artifacts, the six named failure modes, the
  Knowns/Unknowns/Assumptions/Disconfirmation structure, the authority
  hierarchy (project docs > operator profile > kernel defaults > runtime).
- **Swappable:** the memory substrate, the runtime, the specific LLM, the
  capture ergonomics, the viewer.

A successful posture installation survives every swap below it.

---

## Read next

- [`kernel/SUMMARY.md`](../kernel/SUMMARY.md) — the 30-line distillation this posture is built from.
- [`demos/02_debug_slow_endpoint/`](../demos/02_debug_slow_endpoint/) — the posture applied to a realistic incident.
- [`demos/03_differential/`](../demos/03_differential/) — same scenario with the posture off vs. on.
- [`.claude-plugin/README.md`](../.claude-plugin/README.md) — install the posture as a Claude Code plugin.
