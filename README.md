# episteme

> **episteme installs an epistemic posture.** The artifacts are how the posture becomes enforceable. Markdown. Vendor-neutral. The kernel outlives the tooling.

A *posture* is how a reasoner holds themselves before a decision: which questions get asked, which unknowns get named, which options are pre-rejected, and which conditions force a pivot. Tools and memory stores cycle every 18–36 months — the posture does not. `episteme` is the layer that installs the posture once and delivers it into every runtime and substrate you use.

**What `episteme` installs is a *way of thinking* the agent cannot skip — not a list of tools it can call.** Before any high-impact decision, the agent must project its reasoning onto a four-field surface: what it *knows*, what it *doesn't know*, what it is *assuming*, and what observable outcome would *prove it wrong* — with a Core Question above them. Those five fields are the structural counter to the six Kahneman-derived failure modes LLMs inherit from their training (WYSIATI, question substitution, anchoring, narrative fallacy, planning fallacy, overconfidence), plus three governance failure modes (constraint removal without understanding, measure-as-target drift, controller-variety mismatch — see [`kernel/FAILURE_MODES.md`](./kernel/FAILURE_MODES.md)). The framework separates facts from inferences from preferences, demands falsifiable hypotheses, keeps hypothesis → test → update visible across sessions, and audits the operator's own cognitive profile against the episodic record of what was actually done. **Thinking this way — deliberately, auditably, under named failure modes — is the product.** The rest is how we keep the framework from being skipped under pressure.

**Enforcement — the file-system is the kernel's prefrontal cortex.** Prompt-only reminders get skipped the moment a deadline arrives; reminders embedded in system prompts lose against a sufficiently confident LLM. So the framework is enforced at the file-system boundary instead of the prompt boundary. By default, `episteme` *blocks* (exit 2) any high-impact op — `git push`, `npm publish`, `terraform apply`, DB migrations, lockfile edits — until a valid Reasoning Surface is on disk. Validity is structural: Core Question, Knowns, Unknowns, Assumptions, Disconfirmation must be filled with concrete, measurable content (≥ 15 chars, no `none` / `n/a` / `tbd` / `해당 없음` placeholders). Command text is normalized before matching, so `subprocess.run(['git','push'])` and `os.system('git push')` bypass shapes are caught. Agent-written shell scripts executed across calls are deep-scanned via a stateful interceptor. This is the uncompromising enforcer of the cognitive discipline above — not a security product pretending to be a thinking framework.

Advisory mode (warn-don't-block) is opt-in per-project: `touch .episteme/advisory-surface`.

**[What this installs →](./docs/POSTURE.md)** · **[The narrative spine →](./docs/NARRATIVE.md)** · **[Differential demo (off vs on) →](./demos/03_differential/)** · **[Install as plugin →](./.claude-plugin/README.md)** · **[Quick start ↓](#quick-start)**

<!-- ![Episteme Strict Mode Block](docs/assets/strict_mode_demo.gif) -->
 ![Episteme — posture as thinking](docs/assets/posture_demo.gif)

> **Posture as thinking** — *(gif above)* — [`scripts/demo_posture.sh`](./scripts/demo_posture.sh) · ~75 s · cinematic differential. Same PM prompt, shown twice. Fluent default (*doxa*) vs. **the Reasoning Surface authored field-by-field** (*episteme*).
>
> **Climax: the Reasoning Surface itself** — Core Question reframed (the asked question wasn't the load-bearing one), Unknowns enumerated as classifiable failure modes (not hand-waved as "uncertainty"), Disconfirmation pre-committed as a falsifiable pivot. The specificity ladder that follows is the *test* of the surface — not the point of it: `"None"` blocks (the shallowest thing the kernel does), a fluent-vacuous disconfirmation passes the hot path (the honest kernel limit), a concrete falsifiable pivot passes for the right reason. The memory loop closes the circuit — phase 11 shipped; phase 12 (profile-audit) in flight.
>
> See also: [`docs/DEMOS.md`](./docs/DEMOS.md) for the second demo (posture as enforcement of the surface) and recording instructions.
>
> Prose spine: [`docs/NARRATIVE.md`](./docs/NARRATIVE.md) — *doxa / episteme / praxis*, traversed by the grain (**결 · gyeol**).

---

## I want to… → do this

| Goal                                                | Command / pointer                                                   |
|-----------------------------------------------------|---------------------------------------------------------------------|
| Understand what this is in 3 minutes                | [`docs/POSTURE.md`](./docs/POSTURE.md) · [`kernel/SUMMARY.md`](./kernel/SUMMARY.md) |
| Read the structural spine (doxa · episteme · praxis · 결)  | [`docs/NARRATIVE.md`](./docs/NARRATIVE.md)                     |
| See the posture *off vs on* on the same prompt      | [`demos/03_differential/`](./demos/03_differential/) · [`scripts/demo_posture.sh`](./scripts/demo_posture.sh) |
| See what it produces end-to-end                     | [`demos/01_attribution-audit/`](./demos/01_attribution-audit/) · [`demos/02_debug_slow_endpoint/`](./demos/02_debug_slow_endpoint/) |
| Install as a Claude Code plugin (one line)          | `/plugin marketplace add junjslee/episteme`                     |
| Install on my machine (CLI + editable kernel)       | `pip install -e . && episteme init` — see [`INSTALL.md`](./INSTALL.md) |
| Draft a reasoning surface from a Slack thread       | `episteme capture --input thread.txt --output surface.json`    |
| Sync identity to every AI tool I use                | `episteme sync`                                                 |
| Encode working style + reasoning posture            | `episteme setup . --interactive`                                |
| Apply the right harness for my project type         | `episteme detect . && episteme harness apply <type> .`      |
| Know when *not* to use this kernel                  | [`kernel/KERNEL_LIMITS.md`](./kernel/KERNEL_LIMITS.md)              |
| Find attribution for any borrowed concept           | [`kernel/REFERENCES.md`](./kernel/REFERENCES.md)                    |
| Audit my setup                                      | `episteme doctor`                                               |

---

## See it in 60 seconds

Three demos, increasing in what they prove:

- [`demos/01_attribution-audit/`](./demos/01_attribution-audit/) — canonical four-artifact shape (reasoning-surface → decision-trace → verification → handoff). The kernel applied to itself, auditing whether every borrowed concept is traceable to a primary source.
- [`demos/02_debug_slow_endpoint/`](./demos/02_debug_slow_endpoint/) — posture applied to a realistic p95 regression. The fluent-wrong "add a cache" answer rejected at the Core Question gate.
- [`demos/03_differential/`](./demos/03_differential/) — **same prompt, posture off vs. on**. The demo that converts skeptics: a PM asks for a 2-sprint semantic-search scope; off answers *how*, on answers *whether*. [`DIFF.md`](./demos/03_differential/DIFF.md) shows which failure modes the posture caught.

Open any of the three. You will know what episteme produces before reading any philosophy.

---

## The lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                         operator (you)                              │
│           ├── cognitive preferences   ├── working style             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                    episteme sync
                               │
      ┌────────────────────────┼────────────────────────┐
      ▼                        ▼                        ▼
 Claude Code             Hermes (OMO)            future adapter
 (CLAUDE.md)             (OPERATOR.md)           (same kernel)
      │                        │                        │
      └────────────────────────┼────────────────────────┘
                               │
                       per-session loop
                               │
      ┌────────┬────────┬──────┴─────┬────────┬────────┐
      ▼        ▼        ▼            ▼        ▼        ▼
    FRAME → DECOMPOSE → EXECUTE → VERIFY → HANDOFF → (next session)
      │                                        │
      │ Reasoning Surface                      │ docs/PROGRESS.md
      │ (Knowns / Unknowns /                   │ docs/NEXT_STEPS.md
      │  Assumptions / Disconfirmation)        │ decision artifact
      │                                        │
      └────────────── feedback ────────────────┘
```

Every element is the operational form of a kernel principle. The loop is the unit of progress (IV). Orientation precedes observation (II). Knowns/Unknowns/Assumptions/Disconfirmation are explicit before action (I). Multiple lenses are required at high-impact decisions (III).

---

## The kernel

Start at **[`kernel/`](./kernel/)**. Pure markdown. No code. No vendor lock-in.

| File                                                              | What it defines                                              |
|-------------------------------------------------------------------|--------------------------------------------------------------|
| [`SUMMARY.md`](./kernel/SUMMARY.md)                               | 30-line operational distillation                             |
| [`CONSTITUTION.md`](./kernel/CONSTITUTION.md)                     | Root claim, four principles, nine failure modes              |
| [`REASONING_SURFACE.md`](./kernel/REASONING_SURFACE.md)           | Knowns / Unknowns / Assumptions / Disconfirmation protocol   |
| [`FAILURE_MODES.md`](./kernel/FAILURE_MODES.md)                   | Nine fluent-agent failure modes ↔ counter artifacts (6 Kahneman · 3 governance) |
| [`OPERATOR_PROFILE_SCHEMA.md`](./kernel/OPERATOR_PROFILE_SCHEMA.md) | Schema for encoding an operator's cognitive preferences   |
| [`MEMORY_ARCHITECTURE.md`](./kernel/MEMORY_ARCHITECTURE.md)       | Five memory tiers (working / episodic / semantic / procedural / reflective) |
| [`KERNEL_LIMITS.md`](./kernel/KERNEL_LIMITS.md)                   | When the kernel is the wrong tool; declared gaps             |
| [`REFERENCES.md`](./kernel/REFERENCES.md)                         | Attribution for every load-bearing borrowed concept          |
| [`CHANGELOG.md`](./kernel/CHANGELOG.md)                           | Versioned kernel history                                     |

Authority hierarchy: **project docs > operator profile > kernel defaults > runtime defaults.** Specific beats general.

---

## Architecture · doxa → episteme → praxis → Gyeol

> Full diagram with node annotations and cross-references: [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md)

```mermaid
graph TD
    subgraph SG1["① The Agentic Mind — Intention"]
        A["Agent\nGenerating intent for a high-impact op"]
        B["Reasoning Surface\ncore_question · knowns · unknowns\nassumptions · disconfirmation"]
        D["Doxa\nFluent hallucination\nnone / n/a / tbd / 해당 없음\n< 15 chars · missing fields"]
        E["Episteme\nJustified true belief\nconcrete knowns · named unknowns\ndisconfirmation ≥ 15 chars · no placeholders"]
    end

    subgraph SG2["② The Sovereign Kernel — Interception"]
        F["Stateful Interceptor\ncore/hooks/reasoning_surface_guard.py\nnormalises cmd · deep-scans agent-written files\ncross-call stateful memory"]
        G["Hard Block · exit 2\nExecution denied\nAgent forced to re-author surface"]
        H["PASS · exit 0\nPrecondition satisfied\nExecution admitted to Praxis"]
    end

    subgraph SG3["③ Praxis & Reality — Execution"]
        I["Tool Execution\ngit push · bash script.sh · npm publish\nterraform apply · DB migrations · lockfile edits"]
        J["Observed Outcome\ncore/hooks/calibration_telemetry.py\nexit_code 0 or non-zero · stderr captured"]
    end

    subgraph SG4["④ 결 · Gyeol — Cognitive Texture & Evolution"]
        K["Prediction Record\ncorrelation_id stamped at PASS\n~/.episteme/telemetry/YYYY-MM-DD-audit.jsonl"]
        L["Outcome Record\ncorrelation_id · exit_code · stderr\n~/.episteme/telemetry/YYYY-MM-DD-audit.jsonl"]
        M["episteme evolve friction\nsrc/episteme/cli.py · _evolve_friction\npairs prediction ↔ outcome by correlation_id\nranks under-named unknowns · flags exit_code ≠ 0"]
        N["결 · Gyeol\nRefined cognitive grain\nfriction hotspots · calibrated profile axes"]
        O["Operator Profile\ncore/memory/global/operator_profile.md\nlast_elicited axes updated · confidence rescored"]
        P["kernel/CONSTITUTION.md\nFour principles recalibrated\nfailure-mode counters sharpened"]
    end

    A --> B
    B --> D
    B --> E
    D --> F
    E --> F
    F --> G
    F --> H
    G -.->|"cognitive retry"| A
    H --> I
    I --> J
    E -.->|"correlation_id stamped at PASS"| K
    J --> L
    K --> M
    L --> M
    M --> N
    N --> O
    N --> P
    O -.->|"posture loop closed"| A
    P -.->|"posture loop closed"| A

    classDef doxaStyle fill:#c0392b,stroke:#922b21,color:#fff
    classDef episteStyle fill:#1e8449,stroke:#145a32,color:#fff
    classDef passStyle fill:#27ae60,stroke:#1e8449,color:#fff
    classDef praxisStyle fill:#2ecc71,stroke:#27ae60,color:#000
    classDef gyeolStyle fill:#1a5276,stroke:#154360,color:#fff
    classDef kernelStyle fill:#6c3483,stroke:#512e5f,color:#fff
    classDef neutralStyle fill:#2c3e50,stroke:#1a252f,color:#fff

    class D,G doxaStyle
    class E episteStyle
    class H,I passStyle
    class J praxisStyle
    class K,L,M,N,O,P gyeolStyle
    class F kernelStyle
    class A,B neutralStyle
```

Four subgraphs, one lifecycle. **Doxa** (red) — fluent-but-unvalidated agent output or a hard block — is the failure state the kernel exists to prevent. **Episteme** (green) — a validated Reasoning Surface with concrete Knowns, named Unknowns, and a falsifiable Disconfirmation ≥ 15 chars — is the precondition for execution. **Praxis** (light green) — the admitted tool execution and its observed outcome. **결 · Gyeol** (blue, lit. *grain*) — the calibration loop: prediction and outcome records joined by `correlation_id` into daily JSONL, analyzed by `episteme evolve friction`, feeding friction signals back into the Operator Profile and `kernel/CONSTITUTION.md`. The posture loop is closed. Prose spine: [`docs/NARRATIVE.md`](./docs/NARRATIVE.md).

**Works with any stack.** Episteme is an agnostic layer that operates independently of the LLM runtime — LangChain, CrewAI, Claude Code, Cursor, MCP. Kernel is pure markdown; operator profile is plain JSON; workflow loop is vendor-neutral. Adapter layer (Claude Code, Hermes, OMO/OMX) is pluggable. The kernel outlives the tooling.

---

## Quick start

```bash
git clone https://github.com/junjslee/episteme ~/episteme
cd ~/episteme
pip install -e .

episteme init              # generate personal memory files from templates
episteme setup . --write   # score working style + reasoning posture
episteme sync              # push identity to every adapter
episteme doctor            # verify wiring
```

Project-type harness:

```bash
episteme detect .                         # analyze repo, recommend a harness
episteme harness apply ml-research .      # apply it
episteme new-project . --harness auto     # scaffold + auto-detect
```

Deep-dive onboarding modes, scored dimensions, and defaults: **[`docs/SETUP.md`](./docs/SETUP.md)**.

---

## How episteme compares

Most tools in this space either build agent runtimes or provide memory APIs for applications. `episteme` augments the developer tools you already use.

| Axis                  | episteme                                          | Memory APIs (mem0, OpenMemory)  | Agent runtimes (Agno, opencode, omo) |
|-----------------------|---------------------------------------------------|---------------------------------|--------------------------------------|
| **What it is**        | Identity + governance layer across dev tools      | Memory API embedded in an app   | A runtime that executes agents       |
| **Where identity lives** | Governed markdown + JSON, cross-tool, versioned | Vector/graph store, per app     | System prompt per session            |
| **Sync**              | One command, all tools                            | N/A                             | N/A (per-project config)             |

The gap episteme fills: no other project syncs a *governed identity + cognitive contract* across multiple developer AI tools in one command. Runtimes and memory APIs own different lanes; episteme sits above them and makes them aware of *who you are* and *how you think*.

---

## Repository layout

```
episteme/
├── kernel/                     philosophy (markdown; travels across runtimes)
├── demos/                      end-to-end reference deliverables
├── core/
│   ├── memory/global/          operator memory (gitignored; personal)
│   ├── hooks/                  deterministic safety + workflow hooks
│   ├── harnesses/              per-project-type operating environments
│   └── schemas/                memory + evolution contract schemas
├── adapters/                   kernel delivery layers (Claude Code, Hermes, …)
├── skills/                     reusable operator skills
├── templates/                  project scaffolds, example answer files
├── docs/                       runtime docs, architecture, contracts
├── src/episteme/               CLI + core library
└── tests/
```

Repo operating contract (for any agent working here): **[`AGENTS.md`](./AGENTS.md)**. LLM sitemap: **[`llms.txt`](./llms.txt)**.

---

## CLI surface

```bash
episteme init
episteme doctor
episteme sync [--governance-pack minimal|balanced|strict]
episteme new-project [path] --harness auto
episteme detect [path]
episteme harness apply <type> [path]
episteme profile [survey|infer|hybrid] [path] [--write]
episteme cognition [survey|infer|hybrid] [path] [--write]
episteme setup [path] [--interactive] [--write] [--sync] [--doctor]
episteme bridge anthropic-managed --input <events.json> [--dry-run]
episteme bridge substrate [list-adapters|describe|verify|push|pull] ...
episteme capture [--input <file>] [--output <file>] [--by <name>]
episteme viewer [--host 127.0.0.1] [--port 37776]
episteme evolve [run|report|promote|rollback] ...
```

Full reference: [`docs/README.md`](./docs/README.md).

---

## Why this architecture

The product is a thinking framework; the rest of this list is what falls out when that framework is taken seriously.

- **Feedforward cognitive control, not reactive correction.** Most agent-safety systems observe an error and correct after the fact. `episteme` names the failure modes *before* execution and refuses to proceed until they are countered. The Reasoning Surface is the feedforward gate — Knowns, Unknowns, Assumptions, Disconfirmation declared *first*, action *second*. WYSIATI cannot hide in a blank Unknowns field; question substitution cannot hide behind a missing Core Question; anchoring cannot hide from an explicit falsification condition.
- **Cognitive contract (Design by Contract).** The Reasoning Surface is Bertrand Meyer's *Design by Contract* applied to reasoning itself: **Preconditions** (Knowns + validated Assumptions that must hold before execution), **Postconditions** (Verification: what must be true at handoff), **Invariants** (the kernel's four principles, which cannot be suspended). Breach a precondition and the agent should not proceed. Enforcement is structural, not advisory.
- **Hypothesis → test → update, observable across sessions.** Each Reasoning Surface carries a hypothesis; each execution carries an outcome; the episodic tier records both; the semantic-promotion job surfaces patterns where hypotheses *never* fire their declared disconfirmation (calibration debt). The framework does not ask the agent to think once — it makes thinking-quality drift detectable over time.
- **Cognitive profile is hypothesis, not documentation.** The operator profile's nine cognitive-style axes (`dominant_lens`, `noise_signature`, `explanation_depth`, etc.) are control signals that modulate enforcement thresholds — and are themselves audited against the episodic record of actual behavior. Claimed posture vs. lived posture, with drift surfaced as re-elicitation. Prevents the profile from becoming a vanity mirror.
- **Declared limits.** [`KERNEL_LIMITS.md`](./kernel/KERNEL_LIMITS.md) names when the kernel is the wrong tool. *A discipline without a boundary is a creed.* The kernel enforces structural discipline in the hot path; semantic quality over time. Fluent-vacuous surfaces pass the hot-path validator by design — they are caught by the calibration loop, not the block.
- **Hard authority boundary.** Repo docs + global memory are the source of truth; tool-native memories are acceleration, not authority. The frame beats the framing.
- **Cross-tool consistency.** One governed cognitive contract across Claude Code, Hermes, and future adapters. The posture outlives the tool.
- **Deterministic setup.** Onboarding is explainable (`survey` / `infer` / `hybrid`) instead of implicit drift.
- **Coexistence, not replacement.** Self-evolving runtimes adapt fast locally; durable lessons get promoted into authoritative files, then re-synced. Managed runtimes (execution substrate) and `episteme` (cognitive control plane) are complementary.
- **Policy engine for agent cognition.** `episteme` plays the role OPA (Open Policy Agent) plays for cloud infrastructure: an independent layer that evaluates whether a proposed *reasoning state* meets declared epistemic policy before the action it authorizes is allowed. The LLM is the runtime; `episteme` is the policy engine.
- **AI-safety by construction, not by bolt-on.** The same structural gates that counter reasoning failure modes also close the OWASP Agentic risks (see *Zero-trust execution* below). Security falls out of the framework; it is not the framework.

Memory model, Memory Contract v1, Evolution Contract v1, and managed-runtime coexistence: **[`docs/SYNC_AND_MEMORY.md`](./docs/SYNC_AND_MEMORY.md)**.

---

## Zero-trust execution

The OWASP Agentic AI Top 10 identifies prompt injection, goal hijacking, overreach, and unbounded action as the primary risk classes for autonomous agents. The Knowns / Unknowns / Assumptions / Disconfirmation structure is a structural counter to each:

| OWASP Agentic Risk | episteme counter |
|--------------------|------------------|
| Prompt injection / goal hijacking | Core Question declared before execution begins; deviations surface as Unknowns |
| Overreach / unbounded action | Constraint regime declared in Frame; reversible-first policy enforced |
| Fluent hallucination | Unknowns field cannot be blank; assumptions must be named before acting on them |
| Infinite planning loops | Disconfirmation condition required; loop exits when evidence fires |

No assumption is trusted unless named. No action is taken unless the precondition (Knowns) and constraint regime are declared. The kernel is the verification layer between intent and execution.

---

## Human prompt debugging

Episteme doesn't just govern the AI—it debugs the human's intent. When an agent maps Knowns vs. Unknowns against a user request, it exposes logical gaps in the *original prompt* before executing flawed assumptions. The Unknowns field is often where the human realizes their question was underspecified. The Disconfirmation field is often where they realize they have not thought about falsification at all.

This is not a side effect. It is a design property. A system that forces the agent to declare what it does not know forces the human to confront what they did not specify.

---

## Read next

| Topic                                      | Where                                                            |
|--------------------------------------------|------------------------------------------------------------------|
| What episteme installs (posture framing) | [`docs/POSTURE.md`](./docs/POSTURE.md)                         |
| Kernel distillation (30 lines)             | [`kernel/SUMMARY.md`](./kernel/SUMMARY.md)                       |
| What the kernel produces                   | [`demos/01_attribution-audit/`](./demos/01_attribution-audit/) · [`demos/02_debug_slow_endpoint/`](./demos/02_debug_slow_endpoint/) |
| Same prompt, posture off vs. on            | [`demos/03_differential/`](./demos/03_differential/)             |
| Install paths (marketplace, CLI, dev)      | [`INSTALL.md`](./INSTALL.md)                                     |
| Benchmark with disconfirmation target      | [`benchmarks/kernel_v1/`](./benchmarks/kernel_v1/)               |
| Substrate bridge (mem0, memori, noop)      | [`docs/SUBSTRATE_BRIDGE.md`](./docs/SUBSTRATE_BRIDGE.md)         |
| Profile + cognition setup                  | [`docs/SETUP.md`](./docs/SETUP.md)                               |
| Sync matrix, memory model, contracts       | [`docs/SYNC_AND_MEMORY.md`](./docs/SYNC_AND_MEMORY.md)           |
| Harness system                             | [`docs/HARNESSES.md`](./docs/HARNESSES.md)                       |
| Hook reference + governance packs          | [`docs/HOOKS.md`](./docs/HOOKS.md)                               |
| Skills + agent personas + provenance       | [`docs/SKILLS_AND_PERSONAS.md`](./docs/SKILLS_AND_PERSONAS.md)   |
| Personal customization (memory/hooks/skills) | [`docs/CUSTOMIZATION.md`](./docs/CUSTOMIZATION.md)             |
| Agent repo operating contract              | [`AGENTS.md`](./AGENTS.md)                                       |
| Architecture deep-dive                     | [`docs/EPISTEME_ARCHITECTURE.md`](./docs/EPISTEME_ARCHITECTURE.md) |
| Cognitive system playbook                  | [`docs/COGNITIVE_SYSTEM_PLAYBOOK.md`](./docs/COGNITIVE_SYSTEM_PLAYBOOK.md) |

---

## Push-readiness checklist

```bash
PYTHONPATH=. pytest -q tests/test_profile_cognition.py
python3 -m py_compile src/episteme/cli.py
episteme doctor
git status && git rev-list --left-right --count @{u}...HEAD
```
