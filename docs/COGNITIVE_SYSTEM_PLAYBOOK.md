# 📒 Cognitive System Playbook

## 🏛️ Operating Thesis: The Mind-Vessel Duality

`episteme` runs on a dual-system architecture:
- **Cognitive System (The Soul)**: Governs *how to think*. Improves decision quality and reasoning integrity through formal protocols.
- **Execution System (The Vessel)**: Governs *how to act*. Improves delivery reliability and verification discipline through deterministic workflows.

**Design Rule**:
> Cognition without Execution is abstract theory.
> Execution without Cognition is a brittle machine.

## 2) Memory architecture (authority boundaries)

Three memory classes with strict authority:

1. Project memory (highest day-to-day authority)
- where: `docs/*`, `AGENTS.md`, `HARNESS.md`
- content: requirements, constraints, milestones, decisions
- role: source of truth for what must be delivered now

2. Global memory
- where: `core/memory/global/*`
- content: stable operator defaults, cognitive posture, workflow policy
- role: source of truth for how work is generally done

3. Episodic memory
- where: session traces / evolution episodes
- content: observations, outcomes, experiments, run artifacts
- role: evidence for learning and promotion, not direct authority

Conflict precedence:
- project > global > episodic
- explicit human correction overrides inferred memory

## 🧠 3) Cognitive Reasoning Protocol (Mandatory)

Before committing to any major path, project your reasoning onto the **Reasoning Surface**:

- **Knowns**: Verified, non-negotiable facts.
- **Unknowns**: Risks, missing data, or "black boxes."
- **Assumptions**: The logical leaps we are currently making.
- **Disconfirmation**: One specific piece of evidence that would prove our reasoning is wrong.

**Why this protocol exists -- Kahneman's Dual-Process Theory**: AI agents run almost entirely on
System 1: fast, automatic, pattern-matching reasoning that produces fluent, plausible-sounding
answers whether or not they are correct. The training signal that makes agents useful -- rewarding
confident, coherent responses -- also makes them systematically prone to specific failure modes.

The Reasoning Surface is a System 2 forcing function. Each field blocks a named System 1 failure:
- **Unknowns field** blocks WYSIATI (What You See Is All There Is): reasoning only from what is
  present in context, never flagging what is missing. A blank Unknowns section means the agent
  has not looked for what it does not know.
- **Core Question** blocks question substitution: silently replacing the hard real question with
  a nearby easier one and answering that instead. Name the actual question.
- **Disconfirmation** blocks anchoring: the first framing encountered dominates and later
  information adjusts insufficiently. Force an active falsification attempt before committing.
- **Facts / Inferences / Preferences separation** blocks narrative fallacy: sparse data assembled
  into a coherent causal story that feels discovered but was constructed.

**Radical Transparency (Dalio)**: Surface uncertainty even when it makes the agent appear less
capable. Believability-weighting applies when inputs conflict: weight by demonstrated track record,
not authority, fluency, or volume. The most confident voice is often the most dangerous to follow
uncritically.

**Mental Model Lattice (Munger)**: Every model is a lens with a built-in blind spot. For high-impact
or irreversible decisions, apply at least 2 models from different domains. Convergence = proceed.
Conflict = mandatory investigation, not a tiebreaker. Default lattice: inversion (what would make
this fail?), second-order effects (what happens downstream?), base rates (what does the historical
distribution say?), margin of safety (what buffer if assumptions slip?).

## 🎭 4) Manifestation Loop (Workflow)

**This loop is an OODA loop (Boyd)**: Observe -> Orient -> Decide -> Act. episteme is the
**Orientation infrastructure** -- the system that shapes the agent's worldview before observation
even begins. Orientation (mental models, memory, reasoning protocols) is the most critical step
because it filters what gets observed and how decisions are framed. Faster loop iterations beat
stronger single iterations: prefer reversible, small actions that close the loop quickly over
large, confident, slow bets.

1. **Awareness** [Observe]: Ingest the **Cognitive Harness** (`HARNESS.md`) and state of the world (`PROGRESS.md`).
2. **Projection** [Orient]: Map the logic into `docs/PLAN.md` with explicit verification checkpoints.
3. **Manifestation** [Decide + Act]: Implement the smallest reversible increment.
4. **Verification** [Observe again]: Execute deterministic quality checks (tests, lint, audit).
5. **Synchronization** [Orient again]: Update memory and hand off with a "So-What Now?" summary.

Output rule:
- every stage must produce an artifact (plan update, test output, decision note, handoff note)

## 5) Self-evolution protocol (accountable improvement)

Use evolution only as a gated system:
1. propose bounded mutation
2. critique/falsify the proposal
3. replay/evaluate on known suite
4. gate decision
5. promote or rollback with references

Promotion requirements:
- no safety regression
- measurable improvement or justified neutral impact
- replay evidence stored
- rollback path confirmed

Do not allow direct ungated self-modification.

## 6) Hermes coexistence model

Treat Hermes as adaptive runtime, episteme as authoritative governance.

Pattern:
- Hermes memory/skills = fast adaptation lane
- episteme memory/contracts = authoritative lane
- sync + promotion = bridge lane

Rule:
- learn locally fast
- promote durable lessons slowly and explicitly

## 7) Adapter conformance checklist

For each runtime adapter (Claude/Codex/opencode/Hermes), verify:
- authoritative files are readable from the runtime
- runtime does not override authority boundaries
- required safety behavior is active
- handoff docs are honored
- sync reproduces deterministic state

If any fail, the adapter is non-conformant and must be fixed before trusting automation.

## 8) Practical anti-drift controls

- Keep generated artifacts in `.generated/` and mark them non-authoritative until compiled
- Use deterministic commands for bootstrap/setup
- Keep command surface single-name (`episteme`)
- Run CI on every PR/push
- Record high-impact decisions in `docs/DECISION_STORY.md`

## 9) Success metrics

Track these over time:
- delivery reliability: completed planned tasks / committed tasks
- verification quality: regression count, escaped defect count
- cognitive quality: % of major decisions with known/unknown/assumptions/disconfirmation
- adaptation quality: promoted evolution episodes with sustained improvement
- cross-runtime parity: same task outcome consistency across adapters

## 10) 30-day maturity roadmap

Week 1:
- stabilize naming/contracts/CI
- enforce decision protocol in templates

Week 2:
- add adapter conformance smoke checks
- add replay harness for evolution evaluation

Week 3:
- collect and promote repeated winning patterns into authoritative memory/skills

Week 4:
- publish conformance report + evolution outcomes
- tighten gates based on observed regressions

---

This playbook is intentionally opinionated.
If a future change weakens authority boundaries, auditability, or rollback safety, reject it.
