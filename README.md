<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg?v=2">
    <img alt="episteme" src="docs/assets/logo-light.svg?v=2" width="456">
  </picture>
</h1>

<p align="center">
  <a href="https://github.com/junjslee/episteme/releases"><img alt="Latest Release" src="https://img.shields.io/github/v/release/junjslee/episteme?include_prereleases&label=release&logo=github"></a>
  <a href="https://github.com/junjslee/episteme/blob/master/LICENSE"><img alt="License: AGPL-3.0-or-later" src="https://img.shields.io/badge/license-AGPL--3.0--or--later-blue"></a>
  <a href="https://github.com/junjslee/episteme"><img alt="Unique Clones" src="https://img.shields.io/badge/dynamic/json?color=success&label=Unique%20Clones&query=uniques&url=https://gist.githubusercontent.com/junjslee/0a171c9a54b11948bbd1562f4f040465/raw/clone.json&logo=github"></a>
</p>

<p align="center">
  <a href="README.md"><b>English</b></a> &bull;
  <a href="README.ko.md">한국어</a> &bull;
  <a href="README.es.md">Español</a> &bull;
  <a href="README.zh.md">中文</a>
</p>

<p align="center"><a href="https://epistemekernel.com"><b>epistemekernel.com</b></a></p>

> **A thinking framework for the AI coding agent you already ship.** Before any high-impact move — the task, not just the shell command — the agent has to state its reasoning on disk: core question, knowns, unknowns, what would prove the plan wrong. A file-system hook refuses to proceed if that surface is missing or vapor, even when the operator is the one who asked for the move. Every resolved conflict becomes a reusable protocol, chained tamper-evidently and surfaced back at the next matching decision. Built as a **Sovereign Cognitive Kernel** — **생각의 틀**, posture over prompt.

**[See it in 60 seconds ↓](#see-it-in-60-seconds)** · **[Install ↓](#quick-start)** · **[Why the file-system, not the prompt ↓](#the-problem--the-solution)** · **[Architecture & philosophy ↓](#architecture--philosophy)**

 ![Episteme — the Thinking Framework in motion](docs/assets/demo_posture.gif)

---

## TL;DR

Modern AI agents are **incredibly capable** — they write production code, navigate entire repos, plan multi-step workflows. What they lack is **context-awareness** and a defensive mechanism for **drift from user's intent**.

When two credible sources disagree — *Source A says do it this way, Source B says do it that way* — an auto-regressive engine cannot tell which answer fits **your** project, **your** team's constraints, **your** op-class's history. So it defaults to the statistically average answer: fluent, confident, and fit for no specific context.

Recent academic work calls this phenomenon **Epistemic Drift** — the cumulative divergence between (a) what the agent actually knows in context, (b) what the operator actually intends, and (c) what the artifact-level state of the system is, produced by repeated human-AI interaction without a verification layer. Drift is not a single error but a thousand small misalignments, each too small to detect alone, that together push the joint human-AI cognitive system off its target without anyone noticing the moment it happened.

`episteme` closes that gap. It is not a memory tool and not a prompt wrapper; it is a **socio-epistemic infrastructure** between you and your AI coding agent. Before any high-impact command runs, the agent is forced onto a four-field **Thinking Framework** on disk — **Knowns · Unknowns · Assumptions · Disconfirmation** — under a **Core Question**. Every conflict the framework resolves is extracted as a reusable protocol, committed to a tamper-evident knowledge base — a **technical provenance system** for agentic reasoning — and surfaced proactively at the next matching decision.

Enforcement is **structural**, not advisory. Prompts can be skipped; a file-system hook that exits non-zero cannot.

---

## The ABCD architecture — four blueprints, one cortex

`episteme` acts as a **prefrontal cortex for AI agents**: it sits between intent and action, and it refuses to let an action proceed until the reasoning behind it is explicit. Four **Cognitive Blueprints** — each keyed to a specific failure class — decide what "explicit enough" means for a given op:

- **A · Axiomatic Judgment** — resolves conflicts between credible but incompatible sources. Forces the agent to name *why* they disagree and *which feature of the current context* selects between them.
- **B · Fence Reconstruction** — protects inherited constraints. Before a constraint can be removed, its original purpose must be reconstructed — Chesterton's fence enforced by the file system.
- **C · Consequence Chain** — decomposes irreversible ops (first-order effect, second-order effect, failure-mode inversion, base-rate reference, margin of safety).
- **D · Architectural Cascade** — catches refactors and renames that would leave stale references behind. Makes the agent enumerate the full blast radius before it edits.

Every blueprint firing — and every decision it validates — is committed to a **tamper-evident hash chain**. That chain is not a log; it is how the kernel gives you **Active Guidance** later: at the next matching decision, the relevant synthesized protocol is surfaced proactively, before the agent defaults to its training distribution.

The result is a **project-specific thinking framework that compounds**. The agent gets sharper on your codebase every time it resolves a conflict, not because you trained it — because the chain did the remembering.

---

## The problem · the solution

### The problem — conflicting sources, averaged answers, no durable know-how

The internet is full of contradictory how-to. Docs say one thing; a senior engineer says another. Two libraries recommend opposite patterns for the same bug. Modern agents, being auto-regressive pattern engines, cannot tell which answer *fits this specific context* — because fit is a causal-world-model judgment, not a pattern match over token frequency. So they average. The output sounds authoritative, fits no specific context, and misleads by omission.

Prompts cannot fix this:

- A system-prompt reminder lives for one call.
- A `CLAUDE.md` nudge gets skipped the moment a deadline arrives.
- **Know-how** — the irreducibly context-specific rule of *"in this shape of problem, do this"* — cannot be taught through better wording. It has to be extracted, stored, and re-surfaced.

### The solution — a Thinking Framework at the file-system level

`episteme` intercepts the moment **intent meets state change**. Before any high-impact op (`git push`, `npm publish`, `terraform apply`, DB migrations, lockfile edits), the agent must project its reasoning onto a structured surface on disk:

| Field | What the agent must commit to |
|---|---|
| **Core Question** | The one question this action is actually trying to answer (counters question substitution). |
| **Knowns** | Verified facts, citations, measurements — not plausible-sounding guesses. |
| **Unknowns** | Named, classifiable gaps — not vague "there might be risks." |
| **Assumptions** | Load-bearing beliefs, flagged so they can be falsified. |
| **Disconfirmation** | The observable event that would prove this plan wrong — pre-committed before action. |

Validity is checked **structurally**: minimum content length, no lazy-token placeholders (`none`, `n/a`, `tbd`, `해당 없음`), normalized command scanning so bypass shapes like `subprocess.run(['git','push'])` and `os.system('git push')` are caught. Agent-written shell scripts are deep-scanned via a stateful interceptor across calls. If the surface is absent or invalid, the op is refused (`exit 2`). Default is strict; advisory mode (warn-don't-block) is opt-in per-project: `touch .episteme/advisory-surface`.

The Disconfirmation field in particular is not a risk checklist — it is the mechanical enforcement of **Robust Falsifiability**: the requirement that a plan commit, *in advance*, to a concrete observable event that would prove it wrong. Strict Mode rejects conditional-but-observable-less phrasing (*"if issues arise"*) and admits only specific falsification conditions (*"p95 latency > 500ms for 5 consecutive minutes, Grafana dashboard api-latency"*). A plan that cannot be falsified is not episteme; it is doxa wearing episteme's vocabulary.

This is the difference between a prompt reminder and a compiler: one asks nicely, the other refuses to proceed.

---

## Protocol Synthesis & Active Guidance — the ultimate vision

`episteme` is **not just a blocker**. The framework's real job is to turn every conflict it resolves into durable know-how that the agent re-applies automatically at the next matching decision.

Here is the loop (v1.0.0 GA shipped · CP1–CP10 · 565 / 565 green; **v1.1.0-rc1 cut 2026-04-29** · 766 / 766 + 21 subtests green — see [`docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`](./docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md)):

1. **Detect conflict.** The agent encounters two valid-looking but incompatible approaches for a context it hasn't fully resolved before.
2. **Decompose, don't average.** The Thinking Framework refuses the "average" answer. It forces the agent to extract *why* the sources conflict and which feature of the context tips the decision.
3. **Synthesize a context-fit protocol.** The resolved *"in context X, do Y"* rule is committed to an append-only, hash-chained knowledge base — tamper-evident, so the agent cannot silently rewrite the lesson.
4. **Guide actively.** At the next matching decision — even weeks later, even across sessions or tools — the kernel surfaces the protocol **proactively**. You don't have to remember to ask.
5. **Self-maintain.** When the agent discovers drift (stale config, deprecated API, core-logic mismatch), it is forced to evaluate *patch vs. refactor* honestly and synchronize the cascade across the full blast radius — CLI, config, schemas, docs, tests, external surfaces — before moving on.

The knowledge base is not a vector store pretending to be memory. It is a **structural, human-readable, version-controlled artifact** you can read, edit, fork, and migrate between adapters (Claude Code, Cursor, Hermes, future tools).

Synthesized protocols are not cache entries — they are **Knowledge Sanctuaries**: tamper-evident (Pillar 2 hash-chained), context-scoped (each protocol carries a context signature so it only reactivates in matching situations), and supersession-respecting (a newer chain entry can override an older one, but cannot silently rewrite it). "Sanctuary" because the space is protected from the entropic LLM-average that surrounds it: only rules locally validated against *this project's* evidence occupy the space. The kernel outlives the tooling; the sanctuaries are how it carries know-how forward.

This architecture also counters **Cognitive Deskilling** — the erosion of the human operator's own reasoning capacity that follows from uncritical reliance on AI output. Because the Reasoning Surface forces declaration of Unknowns and Disconfirmation on *every* high-impact move, the operator cannot outsource thinking without the gaps being surfaced. See [Human prompt debugging](#human-prompt-debugging) below for the specific mechanism.

---

## I want to… → do this

| Goal                                                | Command / pointer                                                   |
|-----------------------------------------------------|---------------------------------------------------------------------|
| See the Thinking Framework *off vs on* on the same prompt      | [`demos/03_differential/`](./demos/03_differential/) · [`scripts/demo_posture.sh`](./scripts/demo_posture.sh) |
| See what the framework produces end-to-end                     | [`demos/01_attribution-audit/`](./demos/01_attribution-audit/) · [`demos/02_debug_slow_endpoint/`](./demos/02_debug_slow_endpoint/) |
| Install as a Claude Code plugin (one line)          | `/plugin marketplace add junjslee/episteme`                     |
| Install on my machine (CLI + editable kernel)       | `pip install -e . && episteme init` — see [`INSTALL.md`](./INSTALL.md) |
| Understand what this installs in 3 minutes          | [`kernel/SUMMARY.md`](./kernel/SUMMARY.md)                          |
| Draft a reasoning surface from a Slack thread       | `episteme capture --input thread.txt --output surface.json`    |
| Sync identity to every AI tool I use                | `episteme sync`                                                 |
| Encode working style + reasoning posture            | `episteme setup . --interactive`                                |
| Apply the right harness for my project type         | `episteme detect . && episteme harness apply <type> .`      |
| Know when *not* to use this kernel                  | [`kernel/KERNEL_LIMITS.md`](./kernel/KERNEL_LIMITS.md)              |
| Find attribution for any borrowed concept           | [`kernel/REFERENCES.md`](./kernel/REFERENCES.md)                    |
| Audit my setup                                      | `episteme doctor`                                               |

---

## See it in 60 seconds

Live site + visual dashboard — both rendered against the kernel's own `cp7-chained-v1` hash chain. See [`web/README.md`](./web/README.md) for the Vercel deploy guide.

Three demos, increasing in what they prove:

- **[`demos/03_differential/`](./demos/03_differential/) — the demo that converts skeptics.** *Exact same prompt, Thinking Framework OFF vs. ON.* A PM asks for a 2-sprint semantic-search scope; off answers *how*; on answers *whether*. [`DIFF.md`](./demos/03_differential/DIFF.md) shows which named failure modes the framework caught.
- [`demos/02_debug_slow_endpoint/`](./demos/02_debug_slow_endpoint/) — framework applied to a realistic p95 regression. The fluent-wrong *"add a cache"* answer is rejected at the Core Question gate; a schema-level root cause is produced instead.
- [`demos/01_attribution-audit/`](./demos/01_attribution-audit/) — canonical four-artifact shape (reasoning-surface → decision-trace → verification → handoff). The kernel applied to itself, auditing whether every borrowed concept is traceable to a primary source.

Open any of the three. You will know what `episteme` produces before reading any philosophy.

---

## Quick start

### Option A — install via Claude Code plugin marketplace

The fastest path if you use Claude Code. This repo ships a marketplace manifest (`.claude-plugin/marketplace.json`), so you can add it as a marketplace and install the plugin in two commands.

Inside Claude Code:

```
/plugin marketplace add junjslee/episteme
/plugin install episteme@episteme
```

Then from any shell:

```bash
episteme init     # one-shot: seed personal memory files from examples
episteme setup    # score workstyle + cognition profile
episteme sync     # propagate into Claude Code and Hermes
episteme doctor   # verify wiring
```

For authoritative command syntax and update semantics, see [Claude Code's plugin marketplace documentation](https://docs.anthropic.com/en/docs/claude-code/plugins).

### Option B — clone the kernel directly

For contributors, forkers, or if you want the full source tree locally:

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
Full command reference: **[`docs/COMMANDS.md`](./docs/COMMANDS.md)**.

---

## How episteme compares

Most tools in this space either build agent runtimes or provide memory APIs for applications. `episteme` augments the developer tools you already use.

| Axis                  | episteme                                          | Memory APIs (mem0, OpenMemory)  | Agent runtimes (Agno, opencode, omo) |
|-----------------------|---------------------------------------------------|---------------------------------|--------------------------------------|
| **What it is**        | Identity + governance layer across dev tools      | Memory API embedded in an app   | A runtime that executes agents       |
| **Where identity lives** | Governed markdown + JSON, cross-tool, versioned | Vector/graph store, per app     | System prompt per session            |
| **Sync**              | One command, all tools                            | N/A                             | N/A (per-project config)             |
| **Know-how extraction** | Enforced at file-system boundary; hash-chained | Opaque retrieval                | Prompt-tuned, per session            |

The gap `episteme` fills: no other project syncs a *governed cognitive contract* across multiple developer AI tools in one command, and no other project forces context-fit protocol extraction at the point of state mutation. Runtimes and memory APIs own different lanes; `episteme` sits above them and makes them aware of *who you are*, *how you think*, and *what your project has already learned*.

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

`episteme` doesn't just govern the agent — it **debugs the human's intent**. When the agent maps Knowns vs. Unknowns against a user request, it exposes logical gaps in the *original prompt* before executing flawed assumptions. The Unknowns field is often where the human realizes their question was underspecified. The Disconfirmation field is often where they realize they haven't thought about falsification at all.

This is not a side effect. It is a design property: a system that forces the agent to declare what it does not know forces the human to confront what they did not specify.

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

The product is a Thinking Framework; the rest of this list is what falls out when that framework is taken seriously.

- **Feedforward cognitive control, not reactive correction.** Most agent-safety systems observe an error and correct after the fact. `episteme` names the failure modes *before* execution and refuses to proceed until they are countered. Knowns, Unknowns, Assumptions, Disconfirmation are declared *first*, action *second*.
- **Cognitive contract (Design by Contract).** The Thinking Framework is Bertrand Meyer's *Design by Contract* applied to reasoning itself: **preconditions** (Knowns + validated Assumptions that must hold before execution), **postconditions** (Verification: what must be true at handoff), **invariants** (kernel principles that cannot be suspended). Breach a precondition and the agent does not proceed.
- **Hypothesis → test → update, observable across sessions.** Each Reasoning Surface carries a hypothesis; each execution carries an outcome; the episodic tier records both; the semantic-promotion job surfaces patterns where hypotheses *never* fire their declared disconfirmation (calibration debt). Thinking-quality drift is detectable over time.
- **Cognitive profile is hypothesis, not documentation.** The operator profile's nine cognitive-style axes (`dominant_lens`, `noise_signature`, `explanation_depth`, etc.) are control signals that modulate enforcement thresholds — and are themselves audited against the episodic record of actual behavior. Claimed posture vs. lived posture, with drift surfaced as re-elicitation.
- **Declared limits.** [`KERNEL_LIMITS.md`](./kernel/KERNEL_LIMITS.md) names when the kernel is the wrong tool. *A discipline without a boundary is a creed.*
- **Hard authority boundary.** Repo docs + global memory are the source of truth; tool-native memories are acceleration, not authority.
- **Cross-tool consistency.** One governed cognitive contract across Claude Code, Hermes, and future adapters. The framework outlives the tool.
- **Policy engine for agent cognition.** `episteme` plays the role OPA (Open Policy Agent) plays for cloud infrastructure: an independent layer that evaluates whether a proposed *reasoning state* meets declared policy before the action it authorizes is allowed. The LLM is the runtime; `episteme` is the policy engine.
- **AI-safety by construction, not by bolt-on.** The same structural gates that counter reasoning failure modes also close the OWASP Agentic risks. Security falls out of the framework.

Memory model, Memory Contract v1, Evolution Contract v1, and managed-runtime coexistence: **[`docs/SYNC_AND_MEMORY.md`](./docs/SYNC_AND_MEMORY.md)**.

---

## Architecture & philosophy

> Full diagram with node annotations and cross-references: [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md).

The Thinking Framework above is the *product surface*. Beneath it sits a structural vocabulary borrowed from ancient Greek epistemology and Korean aesthetics — a spine that every diagram, demo, and artifact in this repository renders onto.

### The triad — doxa · episteme · praxis

- **Doxa** (δόξα) — common opinion, fluent output produced by default. The nine named failure modes in [`kernel/FAILURE_MODES.md`](./kernel/FAILURE_MODES.md) are a taxonomy of *doxa mistaking itself for episteme*.
- **Episteme** (ἐπιστήμη) — justified knowledge: concrete Knowns, named Unknowns, falsifiable Disconfirmation. The precondition for execution. The repo's namesake.
- **Praxis** (πρᾶξις) — informed action: effects that land with their authorizing discipline intact. The four canonical artifacts (reasoning-surface / decision-trace / verification / handoff) are its visible form.

### The grain — 결 · gyeol

The Korean word **결** (*gyeol*) names the grain of wood or stone: the latent pattern-structure inside matter that, when followed, yields coherent form; when cut against, fractures. The Reasoning Surface's field ordering — Knowns → Unknowns → Assumptions → Disconfirmation — is the 결 of epistemic discipline: *settled → open → provisional → falsification-condition*. The calibration loop (prediction + outcome joined by `correlation_id`, analyzed by `episteme evolve friction`) is the grain refining itself across cycles.

### Lifecycle

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

### Four strata, one loop

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

Four subgraphs, one lifecycle. **Doxa** (red) — fluent-but-unvalidated output or a hard block — is the failure state the kernel exists to prevent. **Episteme** (green) — a validated Reasoning Surface — is the precondition for execution. **Praxis** (light green) — the admitted tool execution and its observed outcome. **결 · Gyeol** (blue) — the calibration loop that refines the framework across cycles, feeding back into the operator profile and the kernel constitution.

**Works with any stack.** `episteme` operates independently of the LLM runtime — LangChain, CrewAI, Claude Code, Cursor, MCP. Kernel is pure markdown; operator profile is plain JSON; workflow loop is vendor-neutral. Adapter layer (Claude Code, Hermes, OMO/OMX) is pluggable.

### Cognitive Arms — v1.1+

The four blueprints (above) and three pillars — Cognitive Blueprints · Append-Only Hash Chain · Framework Synthesis & Active Guidance — are the v1.0 *unchanging structural foundation*. Pillars do not move. v1.1 adds **3 Cognitive Arms** operating on top: fluid active engines that refactor the kernel's own knowledge over time.

- **Arm A · Temporal Integrity** — protocols decay. Operator-confirmed retirement supersedes a stale rule rather than silently overwriting it. Verification window: 30 days post-CP-DECAY-03.
- **Arm B · Causal Synthesis** — zero-LLM entity extraction over the deferred-discovery stream produces cluster proposals the framework can act on. Verification window: 60 days.
- **Arm C · Self-Consistency Convergence** — protocols promote to models that derive disconfirmations structurally. Verification window: 90 days.

The distinction is load-bearing — pillars are settled vocabulary; arms are how the system audits and refines its own outputs across time. Status: **v1.1.0-rc1 cut 2026-04-29** with Arm A substrate shipped (supersede-with-history infrastructure + auto-instrumentation hooks that record operator profile + policy edits to chain streams). Arm A decay-verification mechanism, Arm B, and Arm C are scoped for v1.1.0 GA → v1.2.

---

### The kernel files

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

## Read next

| Topic                                      | Where                                                            |
|--------------------------------------------|------------------------------------------------------------------|
| The v1.0 RC direction                      | [`docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`](./docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md) |
| Kernel distillation (30 lines)             | [`kernel/SUMMARY.md`](./kernel/SUMMARY.md)                       |
| What the kernel produces                   | [`demos/01_attribution-audit/`](./demos/01_attribution-audit/) · [`demos/02_debug_slow_endpoint/`](./demos/02_debug_slow_endpoint/) |
| Same prompt, framework off vs. on            | [`demos/03_differential/`](./demos/03_differential/)             |
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
| Layer model + adapter matrix               | [`docs/LAYER_MODEL.md`](./docs/LAYER_MODEL.md)                   |

---

## Push-readiness checklist

```bash
PYTHONPATH=. pytest -q tests/test_profile_cognition.py
python3 -m py_compile src/episteme/cli.py
episteme doctor
git status && git rev-list --left-right --count @{u}...HEAD
```

---

## Commercial licensing

For commercial licensing or consulting, [contact me](mailto:junseong.lee652@gmail.com).
