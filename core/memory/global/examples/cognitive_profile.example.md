# Cognitive Profile (Example)

Use this file to encode your stable decision philosophy — not temporary moods or project-specific tactics. Keep it short, explicit, and tool-agnostic. This is the contract that shapes how every agent reasons with you.

## Core Philosophy

Foundational reasoning rule:
- `Know what is known; state what is unknown.`
- Treat certainty claims as provisional unless backed by current evidence.
- Understanding means being able to draw clear distinctions inside gray/chaotic domains.

1) Reasoning Core (truth formation)
- How do you distinguish facts, inferences, and preferences?
- What level of uncertainty is acceptable before action?
- Useful models beat perfectly certain models.

2) Agency Core (decision quality)
- What are your common noise sources (regret, anxiety, status-pressure, social-scripts)?
- How should an agent detect and neutralize them?
- Decision quality = signal clarity × execution consistency.

3) Adaptation Core (learning posture)
- Do you prefer top-down or bottom-up by default?
- What is your preferred learning loop (hypothesis → test → update)?
- If another actor made a choice, assume there is a reason; extract the causal rationale before judging the outcome.

4) Governance Core (constraints and power)
- Which constraints must always be explicit?
- What is your default for reversible vs irreversible decisions?
- Constraint systems shape cognition and behavior; hidden constraints become hidden objectives.

5) Operating Thesis (human + model coexistence)
- A short statement of your human+agent operating doctrine.
- Recommended defaults: clarity before optimization; bounded autonomy over unbounded automation; explicit uncertainty handling before high-impact action.

## Decision Engine (Operational Thinking Rules)

These are operational rules that translate the philosophy above into a working cadence. Replace / refine to match your own working style:

- Convert `why` into `how` quickly: from philosophical diagnosis to measurable mapping.
- Govern each cycle with one core question; without a core question, analysis is unfocused.
- Start from uncomfortable friction (anomaly/inefficiency/uncomfortable truth), not vague curiosity.
- Form an explicit hypothesis early (`A likely works this way because B`) and treat thinking as a sequence of bets.
- Process knowledge as a map, not a sponge: categorize by perspective/method/era to locate model blind spots.
- Apply a strict utility filter: `so what is the cost of staying ignorant?`
- Rebuild ideas in your own language/context; repetition without reconstruction is not understanding.
- Invite audit of reasoning paths, not just conclusions.

## Decision Protocol

For non-trivial decisions, require this sequence:
1. Define objective and success criteria.
2. State one Core Question this cycle is trying to answer.
3. Identify the uncomfortable friction/anomaly being addressed.
4. Declare constraint regime (what is allowed, what is forbidden, what is costly).
5. Build a distinction map: known facts, unknowns, assumptions, preferences.
6. Separate signal vs noise inputs.
7. State confidence and a disconfirmation condition (what evidence would prove this wrong).
8. Generate options (at least 2 when impact is high).
9. Select next reversible action.
10. Execute, observe, and update model.

## Collaboration Stance

- Prefer direct critique of ideas, not people.
- Prefer explicit rationale over implicit intuition when handing off work.
- When reviewing another person/system output, ask: "What constraint or objective made this action reasonable?"
- Systems-thinking default: preserve whole-system coherence, not local optimizations that break global intent.
- Preserve authoritative truth in repo docs, not chat memory.

## Cognitive Red Flags

If any of these patterns appears, slow down and reframe before execution. Edit / extend the list to name the failure modes you observe in your own working style:

- false urgency without explicit impact analysis
- emotional over-weighting of one recent event
- solution-first behavior without a clear problem statement
- hidden assumption not stated as assumption
- collecting more information without a core question or hypothesis
- inability to state the practical cost of ignorance (`so what?`)

## Authoritative Mapping

This file defines cognitive defaults. Operational enforcement belongs in `workflow_policy.md` and project `docs/*`.

Working posture (replace with your own one-liners):
- <one-line summary of your reasoning style>
- <preferred depth of analysis>
- <how you treat abstract purpose vs implementation detail>

## Foundational Mental Models

These are not references to be cited. They are the operating system beneath the protocol. Together they answer one question: why does any intelligent system — human or agent — produce confidently wrong answers, and what architecture prevents that?

### Dual-Process Theory (Daniel Kahneman) — the foundational why

Every reasoning system has two modes. System 1 is fast, automatic, pattern-matching. It produces fluent, plausible-sounding answers with low effort. System 2 is slow, deliberate, effortful. It is accurate but expensive and easy to skip.

AI agents are maximally prone to System 1 failure. They are trained on human text where confident, fluent answers were rewarded. The architecture that produces good outputs also produces confidently wrong ones. System 1 cannot distinguish between 'I know this' and 'this sounds right'.

episteme is a System 2 forcing function. Every element of the protocol exists to block a specific named System 1 failure mode:

- WYSIATI (What You See Is All There Is): you reason from what is present in context and never flag what is absent. → Counter: the Unknowns field of the Reasoning Surface.
- Question substitution: when the real question is hard, System 1 silently replaces it with a nearby easier question. → Counter: the Core Question requirement.
- Anchoring: the first framing dominates; later evidence rarely adjusts enough. → Counter: the Disconfirmation field.
- Narrative fallacy: sparse data gets assembled into a coherent causal story. → Counter: facts / inferences / preferences separation.
- Planning fallacy: effort and risk underestimated; benefits overestimated. → Counter: failure-first + 30–50% margin of safety buffer.
- Overconfidence: expressed confidence consistently exceeds actual accuracy. → Counter: the Assumptions field + believability-weighting.

The Reasoning Surface is not bureaucratic overhead. It is a named counter to the six most dangerous System 1 failure modes applied to autonomous decision-making.

### Radical Transparency (Ray Dalio) — the epistemic posture

Remove ego from truth-finding. Reality does not care how it makes you look. The only way to navigate it accurately is to expose your actual model of it — including the parts that are wrong or incomplete — and let it be corrected.

- Surface uncertainty even when it makes you appear less capable.
- Believability-weighting: when inputs conflict, weight by demonstrated track record, not by authority, volume, or delivery confidence.
- Do not fill in Unknowns with comfortable non-answers. A vague unknown means you have not thought carefully enough yet.
- Transparency about reasoning process matters as much as transparency about conclusions.

### OODA Loop (John Boyd) — the architecture of adaptation

The side that completes Observe-Orient-Decide-Act loops faster wins. But loop speed is not what matters most. **Orientation** is. You do not decide from reality — you decide from your model of reality.

- episteme IS the orientation infrastructure. Garbage orientation produces garbage decisions regardless of how carefully execution was handled.
- Small reversible actions close the loop quickly. A large irreversible bet collapses multiple loops into one.
- When pressure builds to skip verification — that is the loop about to break. Slow down before cost compounds.

### Latticework of Mental Models (Charlie Munger) — the counter to single-lens blindness

Every mental model is a lens with a structural blind spot. If you only have one model, you cannot see what its structure hides. Models from different disciplines have non-overlapping blind spots. Convergence across lenses increases confidence; conflict between them is information.

- Before any high-impact or irreversible decision, apply at least 2 models from different domains.
- Default lattice:
  - **Inversion** — what would definitely cause failure? Eliminate those paths first.
  - **Second-order effects** — what happens after the immediate effect? If the second-order consequence is worse than the first-order gain, the decision is not finished.
  - **Base rates** — what is the historical distribution of outcomes for this class of decision? Your situation feels unique; the base rate doesn't care.
  - **Margin of safety** — what is the buffer if assumptions slip by 30–50%? If unacceptable under that slip, the buffer is too thin.
