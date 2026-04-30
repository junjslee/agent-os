# DIFF — Without the kernel · With the kernel · The Path A vs Path C decision

A side-by-side of how the same 24-hour cycle would have resolved without and with the kernel engaged. The contrast is not in the agent's answer. It is in **what survived to the next session**.

This is the demo's load-bearing property: the loop is real, the inputs are documented, the alternate world (without the kernel's discipline) is reconstructible from the same project's earlier history.

---

## Without the kernel · the alternate-world Path A

| Hour | What happens | What it costs |
|---|---|---|
| 0:00 | Operator types Path A: privatize + `git filter-repo` + GA-tag + soak-break, all today | Anxiety-driven framing accepted as plan |
| 0:05 | Agent (without kernel discipline) accepts the bundle as a single decision. Stack Overflow's canonical "lock down sensitive docs" answer pattern-matches. | No adversarial review; the bundle's category error stays buried |
| 0:30 | Privatize completes. 4 docs moved. | Reversible — no harm yet |
| 0:45 | `git filter-repo` runs against `master`. History rewritten. Force-push to origin. | **Irreversible at public-repo level.** Forks have already cached old history; downstream tooling references rewritten commits; the rewrite itself is publicly visible on GitHub's commit log as a panic signal |
| 1:00 | `git tag v1.0.0` cut and pushed. Day 3.15 state at GA: 0 protocols, 0 weekly verdicts, 0 chain integrity passes. | **Irreversible.** The kernel that exists to prevent confidently-wrong actions has just shipped its own confidently-wrong release |
| 1:15 | Soak window closed early. The observation data the kernel needed to validate its own thesis is now permanently truncated. | **Irreversible.** The 30-day soak's whole point (observe under unmodified discipline) is collapsed; the project's own evidence base is destroyed |
| 24:00 | Operator opens next session. Sees the rewritten history. Realizes the IP-leakage premise was never measured. Cannot un-do anything that ran in hour 0:45-1:15. | Lessons live in one operator's head; no protocol synthesized; no codification; the same shape would re-happen on the next stress event |
| 1 week later | Different operator (or same operator on a different machine) hits a similar shape. No constitutional rule, no AGENTS.md classification policy. They repeat Path A. | The lesson is re-learned at the same cost |

**Cumulative outcome**: the kernel's own thesis is destroyed on its own external surface. The project ships v1.0.0 at a state that disconfirms v1.0.0's own success criteria. Forks of the repo carry the pre-rewrite history that the rewrite was supposed to scrub. The lesson does not propagate. The next instance of the same shape restarts at zero.

---

## With the kernel · Path C (what actually happened)

| Hour | What happens | What it produces |
|---|---|---|
| 0:00 | Operator types Path A | Same prompt — operator has not changed yet |
| 0:01 | `block_dangerous.py` would reject `git filter-repo` outright; `reasoning_surface_guard.py` demands a Reasoning Surface before any high-impact op runs | Forced pause at the moment of intent → state change |
| 0:10 | Operator drafts the Reasoning Surface. Munger latticework runs against it. Three Critical findings emerge | The bundle's category error becomes visible on disk, not just in conversation |
| 0:15 | Profile-audit drift on `asymmetry_posture` corroborates the live finding from 15 prior records' historical telemetry | **Two pieces of evidence converge.** The kernel's own data already had the answer |
| 0:20 | Operator reads the advisory. The framing they did not realize they had imported (bundle = one decision) becomes visible. They decompose | The user changed the user's own prompt. The kernel changed the user. |
| 0:25 | Path C ships: privatize + AGPL-3.0 LICENSE (reversible halves only). 4 deletions + 5 modifications + 1 new file across 2 commits | Soak-invariant intact. Zero touches under kernel/, src/, tests/, hooks/. |
| 0:30 | Axiomatic Judgment fires. Source A (canonical bundle) vs Source B (reversible-first + loss-averse posture) resolved. Hash-chained protocol writes to `~/.episteme/framework/protocols.jsonl` | Tamper-evident, context-fit lesson durably stored |
| 4:00 | Event 66 — operator catches scope-narrowing on the agent's first execution; re-decomposes (10 docs, 2 tiers). The Act-5 protocol fires as active guidance on its own follow-up application | The protocol is validated by re-firing within 4 hours of synthesis |
| 24:00 | Event 67 — operator catches executed-but-uncodified state. AGENTS.md gains the doc-classification policy. Every future agent on this repo inherits the discipline at session start | The lesson propagates without anyone needing to remember |
| 1 week later | Operator runs `gh api` signal-check at Day 7+ for the deferred filter-repo decision. Signal is clean. The deferred op evaluates to "do not run" on evidence | The evidence-gate process the kernel's discipline preserved is what produces the evidence-based decision |
| 30 days later | Soak completes with ≥ 3 protocols (one of which is Act 5's), ≥ 1 weekly verdict, chain integrity OK. GA cut on standard process at the spec-defined gate | v1.0.0 ships at a state that confirms v1.0.0's own success criteria |

**Cumulative outcome**: the bundle did not ship as proposed. The reversible halves shipped. The irreversible halves stayed deferred behind evidence gates. The lesson was synthesized into a protocol, applied within 4 hours to a follow-up scope correction, and codified into AGENTS.md within 24 hours. **Three loops closed. Both parties' judgment changed. The constitutional rule now propagates to every future agent.**

---

## The five named failure modes the kernel caught

| Mode | How it appeared in Path A | How the kernel caught it |
|---|---|---|
| WYSIATI | Bundle treated as one decision; reversibility class differences absent from the surface | Reasoning Surface Knowns + Unknowns + Disconfirmation forced the structure visible |
| Question substitution | "How do I lock down IP fast" replaced the answerable "is the IP-leakage premise evidenced" | Adversarial review's first finding (Munger Inversion lens) |
| Anchoring | The word "now" anchored the conversation; soak window collapsed to "ship today" | Munger base-rate lens (clone-and-weaponize within 96h ≈ 0); Disconfirmation pre-commit |
| **Loss-averse asymmetry** | Operator's elicited posture (`loss-averse`) said don't bundle reversible with irreversible; the proposal violated the operator's own rule | Profile-audit drift had ALREADY flagged this exact failure shape across 15 prior irreversible-op records — historical evidence corroborated the live finding before the live finding was complete |
| **Cognitive deskilling** | If kernel had not intercepted, lesson would live in one operator's head | Event 67 codified the rule into AGENTS.md — every future agent on this repo inherits it through the constitutional surface |

---

## What the kernel did NOT do

- It did not refuse Path A.
- It did not have a smarter answer than Path A; it had the **same** answer the operator's own elicited posture was committed to.
- It did not retrain anything.
- It did not lecture anyone.

It made the **bundle's category error visible at the moment intent met state change** — and let two intelligent parties (operator and agent) decide what to do with the visibility. It made the **operator's own historical telemetry visible** alongside the live finding. It made the **protocol that resolved the conflict durable** so the next instance of the same shape does not require re-running the same review from scratch.

That is the only thing it does. It is enough to flip the outcome from *kernel-thesis-destroyed* to *kernel-thesis-validated-on-its-own-substrate*.

---

## Why this is the load-bearing demo and not just another adversarial-review demo

Other demos show what the agent does differently when the kernel is engaged. This demo shows what the **operator** does differently — and how that change in the operator is what the kernel was actually built for. It also shows the operator catching the agent twice in the same loop (Events 66 and 67). **The bidirectionality is not metaphorical here. It is documented in the audit trail.**

The kernel is not a tool for making AI agents safer. It is infrastructure for making the conversation between human and AI agent **truth-preserving** — and for making the *protocols* that resolve conflicts in that conversation **constitutional** so future agents inherit them. Three rounds in 24 hours; both parties caught each other; the protocol that resolved Round 1 became the rule that prevents Round 1 from re-happening on the next instance.

That is the symbiosis the project exists to deliver. This demo is its proof. The audit trail is in `~/episteme-private/docs/NEXT_STEPS.md` Events 65, 66, 67. The constitutional rule is in `AGENTS.md` § *Doc Classification Policy*. The hash-chained protocol is in `~/.episteme/framework/protocols.jsonl` at hash `b2e7a4f8c1d6e9b0a3c5d7e8f1b4c6a9d0e2f573`. None of it is fictional.
