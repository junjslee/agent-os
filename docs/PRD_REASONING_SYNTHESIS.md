# PRD: Reasoning Synthesis & Cognitive Alignment (v2.0)

## 1. Vision
Transform `cognitive-os` from a memory storage layer into a **Reasoning Synchronization Engine**. The system must capture not just *what* was done, but the *reasoning landscape* (assumptions, confidence, and disconfirmation criteria) of the operator.

## 2. Core Principles (The "How You Think" Integration)
- **Top-Down Priority**: Abstract architecture and "First Principles" must govern concrete implementation.
- **Reasoning Humility**: Every session must explicitly separate "Knowns" from "Unknowns."
- **Skepticism as a Service**: Agents must attempt to falsify their own plans before execution.
- **Low-Entropy Communication**: Concise, bullet-heavy handoffs to minimize cognitive load.

## 3. Key Features
### F1: The Reasoning Surface
Update `docs/PROGRESS.md` and `docs/DECISION_STORY.md` templates to include an "Reasoning Surface" block:
- **Knowns**: Verified facts.
- **Unknowns**: Identified gaps/risks.
- **Assumptions**: Critical beliefs requiring validation.
- **Disconfirmation**: "What would prove us wrong?"

### F2: Reflexive Prompting (The "Check-in")
Modify the `workflow_policy.md` to mandate a "Cognitive Pause" at Step 2 (Plan):
- Agent must present a "Devil's Advocate" view of its own plan.
- Agent must verify plan against the `cognitive_profile.md` (e.g., speed vs. rigor).

### F3: Handoff Synthesis (TL;DR-first)
Standardize `docs/NEXT_STEPS.md` to use a "So-What Now?" summary format to eliminate context-switching lag.

## 4. Implementation Plan
- [ ] Update `src/cognitive_os/cli.py` to include Reasoning dimensions in compiled policies.
- [ ] Update `templates/project/AGENTS.md` with the new workflow.
- [ ] Update `templates/project/docs/` templates with Reasoning blocks.
- [ ] Add `cognitive-os audit` (reasoning check) to verify if the current session has addressed its unknowns.

---

# Implementation: Reasoning Upgrades
