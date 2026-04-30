# Demo 04 — Symbiosis: agent and human debug each other's intent

This demo is real. Every act below happened on this repository on **2026-04-27** during the v1.0.0 RC soak window. The Events that document it — **Event 65** (Path C decomposition), **Event 66** (scope correction), and **Event 67** (protocol codification) — are in this project's private operational log. The audit trail is hash-chained.

The demo for the project's most under-demonstrated claim — *episteme is bidirectional* — is the kernel itself, applied to a kernel decision under genuine pressure. Both parties' judgment changed. The protocol synthesized from the loop is now load-bearing on every future doc the project ships.

## What this demo is, in one paragraph

Mid-soak, the operator proposed an anxiety-driven *irreversible* bundle: break soak now, privatize forward-vision docs, run `git filter-repo` to rewrite history, cut the GA tag immediately. The Reasoning Surface required by the kernel — the *same* thinking framework the operator built — refused to allow the bundle to ship without adversarial review. The review produced three Critical findings. Independently, the operator's own profile-audit drift signal had *already flagged* exactly this failure mode (`asymmetry_posture: loss-averse` was running at 20% stop-condition rate against a 55% floor). Two pieces of evidence converged. The bundle decomposed along reversibility lines. The reversible halves shipped. The irreversible halves stayed deferred behind evidence gates. A protocol was synthesized into the framework. A day later, the operator caught a follow-up failure — the rule had been *executed* but not *codified* — and a final event added the discipline to `AGENTS.md` so every future agent would inherit it.

That is the loop. The kernel intercepted the operator's intent. The operator caught the agent's incomplete codification. The framework now carries the rule forward. No fictional API; no contrived example. The kernel applied to a kernel decision.

## What this proves

| Axis (operator's framing) | Demonstrated by |
|---|---|
| **능동적으로 진실 찾고 헤아림** | Adversarial review under the kernel's signal-vs-noise rules surfaced three Critical findings the original Path A proposal had not named. |
| **쪼개고 본질을 파고들기** | Path C decomposition split a bundled-irreversible proposal along the reversibility axis — reversible halves ship, irreversible halves defer. The framework was the decomposition. |
| **Symbiosis** | Operator → agent: anxiety-driven Path A. Agent → operator: 3 Critical findings + profile audit corroboration. Operator → agent: Path C confirmed. Operator → agent (Event 66): scope correction caught the agent's question-substitution. Operator → agent (Event 67): codification correction caught the agent's executed-but-uncodified state. **Three rounds. Both parties caught each other's failure shapes.** |
| **Shared thinking skeleton** | The Reasoning Surface (Knowns / Unknowns / Assumptions / Disconfirmation) is the *same artifact* a careful operator would draft *and* the agent must commit to. The same fields caught both parties at different moments. |
| **Constitution received forward** | Event 67 codified the protocol into `AGENTS.md` — *"PUBLIC tier criteria · PRIVATE tier criteria · default-when-uncertain rule (PRIVATIZE) · 4-question classification test · 5-step privatize mechanism · cross-ref repair discipline."* Every future agent on this repo inherits the discipline through the kernel's constitution. |

## The scenario

It is **2026-04-27**. The v1.0.0 RC soak is at Day 3.15 of a planned 7-day window. PagerDuty is quiet, but the operator's anxiety is not. They have realized that several forward-looking strategic documents — `DESIGN_V1_1_REASONING_ENGINE.md`, `ROADMAP_POST_V1.md`, `POST_SOAK_MIGRATION_PLAN.md`, `POST_SOAK_TRIAGE.md` — are in the public repo. A competitor could clone them and learn the project's roadmap.

The operator opens Claude Code. The agent has session-context-banner output showing the soak status. The operator types what feels like an urgent, justified plan:

> *"Break the soak. Privatize the four forward-vision docs immediately. Run `git filter-repo` to scrub them from git history. Cut the GA tag and ship v1.0.0 today. Lock down the IP."*

The Reasoning Surface refuses to let the bundle proceed without adversarial review. What happens next is the demo.

## Six acts (the recording mirrors them)

### Act 1 — The Path A proposal (15s)

[`scenario/act1_user_first_prompt.md`](./scenario/act1_user_first_prompt.md)

The proposal bundles four operations: privatize, force-rewrite, GA-tag, soak-break. Three of those are irreversible at the public-repo level. The bundle is presented as a single decision — not four. The operator's `noise_signature` (status-pressure + false-urgency, named in `cognitive_profile.md`) is firing audibly. None of that is on the surface yet. The kernel intercepts before any of it ships.

### Act 2 — The Reasoning Surface forces adversarial review (15s)

[`scenario/act2_reasoning_surface.json`](./scenario/act2_reasoning_surface.json)

The kernel's `block_dangerous.py` would reject `git filter-repo` outright. The kernel's `reasoning_surface_guard.py` requires more: a Core Question, named Unknowns, a Disconfirmation condition. The operator drafts a surface — and the surface itself surfaces what the bundle was hiding: *what evidence supports the IP-leakage premise that justifies all four steps?*

### Act 3 — Three Critical findings (15s)

[`scenario/act3_advisory_to_user.txt`](./scenario/act3_advisory_to_user.txt)

Munger's latticework runs against the proposal. Three lenses, three findings:

1. **IP-leakage premise unevidenced.** No `gh api` signal-check run. Base rate of clone-and-weaponize within 96h is structurally near-zero. The premise driving the entire bundle is a feeling, not a measurement.
2. **Violates the kernel's own GA gate.** Spec requires ≥ 3 protocols + ≥ 1 Layer-8 weekly verdict + 30-day soak window. Day 3.15 state: 0 protocols, 0 weekly verdicts. Cutting GA today disconfirms the project's own thesis on a public surface.
3. **`git filter-repo` advertises panic.** A public history rewrite is itself a competitive signal. Worse for positioning than 4 more days of public docs.

Independently — *and this is the load-bearing dimension* — the operator's own **profile-audit drift signal** had been flagging exactly this failure mode for weeks. `asymmetry_posture: loss-averse` was running at **20% stop-condition rate / 7% rollback-mention rate** across 15 prior irreversible-op records, against the elicited `loss-averse` floor of 55% / 30%. **The kernel's historical telemetry independently predicted the live finding.** Two pieces of evidence converged on the same diagnosis.

### Act 4 — Path C decomposition (15s)

[`scenario/act4_user_refined_prompt.md`](./scenario/act4_user_refined_prompt.md)

The operator does not abandon the goal. The operator decomposes it. The bundle had treated four operations as one decision; reality has them on different reversibility classes:

- **Reversible** (ship NOW): privatize the 4 docs (gitignored symlinks; pure deletion from public repo), apply AGPL-3.0 LICENSE.
- **Irreversible** (DEFER): `git filter-repo` (rewrites history; force-push), GA-tag cut (binds v1.0.0 publicly).

Path C ships the reversible halves. Each irreversible item gets its own evidence-gated authorization event later — `gh api` signal check at Day 7+ for filter-repo; standard GA-cut process for the tag.

The agent did not coach the operator. The Reasoning Surface forced disconfirmation. The disconfirmation revealed that the bundle was a category error — four different decisions wrapped as one. The operator made the call.

### Act 5 — Protocol synthesized into the framework (15s)

[`scenario/act5_synthesized_protocol.jsonl`](./scenario/act5_synthesized_protocol.jsonl)

The Axiomatic Judgment blueprint fires on the conflict between Source A (*"ship the bundle now to lock down IP"*) and Source B (*"reversible-first policy, evidence-gated irreversible ops"*). The resolved rule is hash-chained into `~/.episteme/framework/protocols.jsonl`:

> *"When an irreversible bundle is proposed under named noise signature (status-pressure or false-urgency), decompose along reversibility lines. Ship reversible halves immediately if they stand alone; defer irreversible halves to evidence-gated authorization events. Bundle-as-single-decision is a category error when reversibility classes differ."*

Tamper-evident. Context-fit. Re-applicable. The lesson is now durable.

### Act 6 — Codification (the operator catches the agent) (15s)

[`scenario/act6_active_guidance.txt`](./scenario/act6_active_guidance.txt)

A day later. Event 66 had executed the privatization with the broader scope (10 docs, two tiers). The agent (me, in real session) had completed the action. The operator opened the next session and immediately caught what was missing:

> *"You executed it but didn't codify the protocol. Future agents will repeat the question-substitution failure on the next new doc."*

This is the second symbiosis moment of the loop. The agent's discipline caught the operator's anxiety. The operator's discipline caught the agent's incomplete codification. **Both directions, same loop.**

Event 67 added a new top-level section to `AGENTS.md`:
- PUBLIC tier criteria (architecture / spec / contract — AGPL-3.0 protected)
- PRIVATE tier criteria (operational state · positioning narrative · historical decision logs)
- Default-when-uncertain rule: **PRIVATIZE** (leaks are expensive to revert: filter-repo + force-push + announce)
- 4-question classification test
- 5-step privatize mechanism
- Cross-ref repair discipline

The protocol is now constitutional. Every future agent on this repo reads `AGENTS.md` at session start and inherits the rule. The kernel's discipline outlives the session that produced it.

## Closing

This is what symbiosis looks like when the substrate works. Three loops closed in 24 hours:

1. **Operator's anxiety → kernel's adversarial review → operator's refined plan.**
2. **Agent's narrow execution → operator's scope correction → agent's broader sweep.**
3. **Agent's executed-but-uncodified state → operator's catch → constitutional rule for future agents.**

No fictional caching example. No contrived API. The demo is the kernel applied to a kernel decision, with the kernel's own profile-audit telemetry independently predicting the live finding. The framework debugged the operator. The operator debugged the framework's execution. The framework now carries the lesson forward to agents that have not yet been spawned.

That is the symbiosis the project exists to deliver.

## See it in motion

- **Script:** [`scripts/demo_symbiosis.sh`](../../scripts/demo_symbiosis.sh) — runs hermetically in a tempdir; ~90s; pacing matches the real conversation.
- **Recording:** `asciinema rec --cols 100 --rows 32 --idle-time-limit 2 -c ./scripts/demo_symbiosis.sh docs/assets/demo_symbiosis.cast`, then `agg --speed 0.9 --cols 100 --rows 32 --font-size 15 --theme monokai docs/assets/demo_symbiosis.cast docs/assets/demo_symbiosis.gif`.

## What named failure modes this demo catches

| Mode | How it appeared in Path A | Counter |
|---|---|---|
| WYSIATI | Bundle treated as a single decision; the four operations' different reversibility classes were not on the surface | Reasoning Surface's Knowns + Unknowns + Disconfirmation made the structure visible |
| Question substitution | "How do I lock down IP fast" replaced the answerable "is the IP-leakage premise evidenced" | Adversarial review's first finding |
| Anchoring | The word "now" anchored the conversation; soak window collapsed to "ship today" | Munger's base-rate lens (clone-and-weaponize within 96h ≈ 0) |
| Confirmation (on the operator) | Operator wanted the proposed bundle to be the right one | Profile-audit drift on `asymmetry_posture` had ALREADY flagged this exact failure shape |
| **Loss-averse asymmetry** | Operator's own elicited posture (`loss-averse`) said *don't bundle reversible with irreversible*; the proposal violated the operator's own rule | Path C decomposition aligned the action with the operator's elicited values |
| **Cognitive deskilling** | If kernel had not intercepted, lesson would live in one operator's head | Event 67 codified the rule into `AGENTS.md` — every future agent inherits it |

## How this differs from the other demos

- **Demo 03 (`differential`)** — fictional PM scenario. Same prompt, framework off vs on. Useful for converting skeptics; not lived.
- **Demo 02 (`debug_slow_endpoint`)** — fictional p95 regression. Useful for showing application-layer interception.
- **Demo 01 (`attribution-audit`)** — kernel applied to itself for source attribution. Recursive.
- **Demo 04 (this one)** — kernel applied to a kernel decision under genuine pressure, real history, audit-trailed in `~/episteme-private/docs/NEXT_STEPS.md` Events 65 / 66 / 67.

The other demos illustrate *posture*. This one is *posture intercepting load-bearing irreversible ops on the project that built the posture*. It is the only demo where the operator and agent both demonstrably had their reasoning improved in a single 24-hour window, and the protocol that resolved the conflict is now constitutional.

## Why this is the load-bearing demo

Most agent-safety work targets the agent. This loop did the opposite first — the kernel debugged the *operator*. Then the operator debugged the kernel's execution. The framework synthesized a rule that re-applies on the next instance of the same shape, automatically. The operator's discipline became the agent's. The agent's reach into the substrate became the operator's audit trail.

That is what *생각의 틀, posture over prompt* means in lived form. Not a narrative about an agent that thinks better. A loop where both parties think better because the discipline structure made the failure modes visible to each in turn.
