# Roadmap — Post v1.0.0 (Branched by Day-7 Outcome)

Goal-backward roadmap for episteme beyond the v1.0.0 soak close. Three
execution branches anchored to Day-7 gate-grading outcomes + five
milestone themes + explicit non-goals per milestone + dependency graph
+ lessons-from-adjacent-ecosystems (Hermes v2026.4.23) appendix.

Drafted Event 51 (2026-04-24) while all 6 pre-soak infrastructure CPs
landed (Events 47-50) and soak clock runs toward ~2026-04-30 close.

---

## 0. Governing intent — the anchor everything traces back to

Restated from the operator's own words (Event 6 third-pass reframe;
also in `kernel/CONSTITUTION.md` and
`docs/COGNITIVE_SYSTEM_PLAYBOOK.md` § 1):

> There is so much information in the world. When I search the
> internet or look at docs, how do I distinguish what is actually
> correct or what specifically fits MY context? Source A says "do
> it this way", Source B says "do it that way". There is an
> underlying know-how or protocol hidden in these multiple cases.
> I want a system that systematically breaks this chaos down,
> understands WHY the sources conflict, creates a thinking
> framework that can continuously update itself, and then uses
> the insights generated from this framework to actively GUIDE me
> in the right direction.

Four jobs the kernel must do to satisfy this:
1. **Per-action causal decomposition** — Pillar 1 Cognitive Blueprints
2. **Per-case protocol synthesis** — Pillar 3 synthesis arm on
   Axiomatic Judgment + Fence Reconstruction + Blueprint D
3. **Proactive guidance at future decisions** — Pillar 3 advisory
   stream at PreToolUse
4. **Continuous self-maintenance** — Blueprint D architectural cascade
   + deferred-discovery logging + retrospective sync-plan verification

Every milestone below must explicitly map to ≥1 of these four jobs.
Items that don't map are scope creep.

---

## 1. Current state (pre-soak-close) — what's in the box

| Capability | Status |
|---|---|
| Pillar 1 · Four named blueprints (A·B·C·D) + generic fallback | ✓ shipped |
| Pillar 2 · Hash-chained episodic + pending-contracts + framework streams | ✓ shipped |
| Pillar 3 · Framework synthesis arm on Fence Reconstruction | ✓ shipped |
| Pillar 3 · Advisory guidance at PreToolUse | ✓ shipped |
| Phase 12 · Profile-audit loop (4 axes deeply-worked, 11 stubbed) | ✓ shipped; drift detection verified Event 48 |
| Exit-code extraction (CP-TEL-01) | ✓ Event 49 |
| Framework dedup-on-log (CP-DEDUP-01) | ✓ Event 49 |
| Correlation-id mismatch (CP-FENCE-02) | ✓ Event 50 |
| Discriminator calibration (CP-DISC-01) | ✓ Event 47 |
| Gate-grading tools (`tools/grade_gates.py` etc.) | ✓ Events 47-50 |
| v1.0.0 governance docs (rubric, triage, prepared patches) | ✓ Events 46-50 |

Current grader baseline (subject to Day-7 fresh-evidence collection):
**3 PASS · 4 MANUAL · 1 FAIL · weighted 3.0/4.0**. Gate 26 FAIL will
likely flip on the first soak-window fence_reconstruction op now that
CP-FENCE-02 has landed.

---

## 2. Day-7 branched paths

Three branches per `docs/POST_SOAK_TRIAGE.md` §4 decision rule.

### 2.A — GA path (≥ 4/8 clear-pass, Gate 28 ≥ PARTIAL)

v1.0.0 GA released. release-please PR #2 merges with operator's
post-soak version-bump decision. Next milestone opens immediately as
**v1.0.1 · Evidence Pipeline Hardening** (§3.1 below). Remaining
MANUAL/FAIL gates named as v1.0.1 scope in release notes per the
honest-disclosure requirement (§4.4 POST_SOAK_TRIAGE).

Estimated calendar: 1 week from GA to v1.0.1-rc1 soak open.

### 2.B — v1.0.1-rc path (2-3 clear-pass)

No GA. v1.0.1-rc1 cycle opens with the top-priority CPs from §3.1
folded in before re-soak. This is the most realistic outcome given
current baseline and remaining MANUAL gates.

Estimated calendar: 2-3 weeks of CP execution + fresh 7-day soak.

### 2.C — scope-retreat path (≤ 1 clear-pass)

Cognitive-adoption thesis not holding up under measurement. Two
options:
- **2.C.i** — demote cognitive-adoption from v1.0 headline; ship v1.0
  on engineering-gates only; cognitive-adoption becomes v1.1 roadmap
  item. Release notes are honest about the retreat.
- **2.C.ii** — defer v1.0 entirely; fold cognitive-adoption and
  engineering completeness into v1.1.

Should not be reached given current baseline (3 PASS already), but
named explicitly so the decision-making is always branch-aware.

---

## 3. Milestone themes — organized by dependency order

Five themes cluster the remaining scope. Each theme has a dedicated
milestone section below.

```
  ┌─────────────────────────────────────────┐
  │ Theme 1: Evidence Pipeline Hardening    │
  │         (v1.0.1 — highest priority)     │
  └───────────────┬─────────────────────────┘
                  │
     ┌────────────┴────────────┐
     ▼                         ▼
  ┌─────────────────┐    ┌──────────────────────┐
  │ Theme 2:        │    │ Theme 3:             │
  │ Schema Evolution│    │ Behavior Knobs       │
  │ (v1.0.1-v1.1)   │    │ (v1.0.1-v1.1)        │
  └────────┬────────┘    └──────────┬───────────┘
           └────────────┬───────────┘
                        ▼
          ┌─────────────────────────────┐
          │ Theme 4: Framework          │
          │         Consolidation (v1.1)│
          └──────────────┬──────────────┘
                         ▼
          ┌─────────────────────────────┐
          │ Theme 5: Cognitive-Adoption │
          │ Gates Raising (v1.2)        │
          └─────────────────────────────┘

  Cross-cutting (any milestone):
  - TUI + observability surface (§3.6)
  - Multi-project framework consolidation (§3.7, v2.0 candidate)
```

### 3.1 Theme 1 — Evidence Pipeline Hardening (v1.0.1)

**Maps to Jobs 1 + 2 + 4.** Ensures the kernel's own evidence-
collection machinery is honest before we raise gates or add features.

CPs in execution-priority order:

| CP | Scope | Effort | Counters FAILURE_MODE |
|---|---|---:|---|
| CP-FENCE-02 | correlation-id mismatch | ✓ applied Event 50 | narrative-fallacy (broken-pairing-masquerading-as-no-evidence) |
| CP-TEL-01 | exit_code extraction | ✓ applied Event 49 | WYSIATI (null-extraction feels complete) |
| CP-DEDUP-01 | framework dedup-on-log | ✓ applied Event 49 | narrative-fallacy (1,294 records feels like 1,294 findings) |
| CP-DEDUP-02 | retroactive dedup of existing 1,294 records | 1 day | same |
| CP-CROSSREF-01 | unique-file-count cross-ref proxy (deferred #2) | 0.5 day | overconfidence |
| CP-CASCADE-01 | exempt kernel state files + read-only ops from cascade (deferred #1 + #26) | 1 day | fence-check (detector firing on own state) |
| CP-CHKPT-01 | auto-checkpoint re-fires fix (deferred #27) | 1 day | planning-fallacy (premature-chkpt commits) |
| CP-SMOKE-01 | installable-plugin smoke test in RC engineering gate (deferred #20) | 1 day | WYSIATI (gate didn't see what was actually broken) |

**Non-goals for v1.0.1**:
- Do NOT add new cognitive-adoption gates (Theme 5 territory).
- Do NOT add new blueprints (Theme 4 territory; current A/B/C/D is
  load-bearing and proven).
- Do NOT introduce new CLI UX features (Theme 6 territory).

**Acceptance criteria for v1.0.1**:
- All CPs above applied + tested.
- Grader weighted-pass reaches ≥ 5.5/4.0 (Gate 22/26 PASS; Gate 25 +
  21 + 27 remain PASS; Gate 28 PASS via pre-audit upgrade; Gates 23 +
  24 PARTIAL at minimum).
- `~/.episteme/framework/protocols.jsonl` contains ≥ 5 real protocol
  entries from soak-window fence_reconstruction ops.
- `framework/deferred_discoveries.jsonl` growth rate drops to < 10
  records/day (from current ~67/day) via CP-DEDUP-01 + -02.

### 3.2 Theme 2 — Schema Evolution (v1.0.1 → v1.1)

**Maps to Job 1 (blueprint field fidelity) + Job 4 (self-maintenance
schema drift detection).** Closes the 4+ schema gaps logged in
deferred discovery #37 + makes schemas reflect what the kernel
actually needs.

| CP | Scope | Effort | Milestone |
|---|---|---:|---|
| CP-SCHEMA-01a | `flaw_classification` enum gains `doc-positioning-drift` + `scope-creep` | 0.25 day | v1.0.1 |
| CP-SCHEMA-01b | `posture_selected` enum gains `audit-pass` (non-patch/non-refactor review state) | 0.25 day | v1.0.1 |
| CP-SCHEMA-02 | add `reasoning_failure_mode` surface field for FAILURE_MODES.md citations (Path 4B — referenced in Gate 27 resolution, deferred #37) | 2 days | v1.1 |
| CP-SCHEMA-03 | migration tooling: episteme kernel evolve — auto-upgrade in-flight surfaces when schema changes | 3 days | v1.1 |

**Non-goals**:
- Do NOT extend blueprint field counts beyond what's proven necessary.
  Adding fields is easy; retiring them breaks past records. Every
  addition requires a counter-factual ("what failure mode does this
  field counter that no existing field captures?").

**Acceptance criteria**:
- Post-schema-02, Gate 27 migrates from kernel-prose-only grading to
  dual-axis (prose + episodic-field) grading.
- No silent schema breaks — all evolution paths have test coverage.

### 3.3 Theme 3 — Behavior Knobs (v1.0.1 → v1.1)

**Maps to Job 3 (active guidance).** Operationalizes the orphan knobs
+ adds the Ashby escalate-by-default mechanism.

| CP | Scope | Effort | Milestone |
|---|---|---:|---|
| CP-KNOBS-01 | `default_autonomy_class` wired to reasoning-surface-guard admit/defer/reject decision (deferred #5) | 2 days | v1.0.1 |
| CP-KNOBS-02 | `fence_check_strictness` wired to Blueprint B strictness threshold (deferred #5) | 2 days | v1.0.1 |
| CP-ASHBY-01 | escalate-by-default for out-of-coverage action shapes (FAILURE_MODE 9 counter; deferred #6) | 3 days | v1.1 |
| CP-JAYNES-01 | evidence-weighted assumption update — posterior plausibility on reasoning_surface.assumptions[] entries; epistemic decay schedule (deferred #7) | 5 days | v1.1 |

**Non-goals**:
- Do NOT make knobs runtime-mutable from agent-side code. Operator-
  only config surface (`core/memory/global/operator_profile.md` +
  `episteme sync`). The kernel controls the knobs; the agent
  doesn't.
- Do NOT add global knobs that don't have a failure-mode counter.

**Acceptance criteria**:
- Post-KNOBS-01+02, session-level behavior visibly different between
  `default_autonomy_class: reversible-auto` vs
  `default_autonomy_class: irreversible-only-gate`.
- Post-ASHBY-01, ≥1 real out-of-coverage action during v1.1 soak is
  caught + escalated (spot-check verdict records this).

### 3.4 Theme 4 — Framework Consolidation (v1.1)

**Maps to Jobs 2 + 3 + 4.** Turns the protocols.jsonl stream from a
flat log into a queryable graph that the advisory system actually
uses with high recall.

| CP | Scope | Effort | Milestone |
|---|---|---:|---|
| CP-GRAPH-01 | Stop-hook async maintenance worker (consolidates protocols into context-signature graph) | 5 days | v1.1 |
| CP-GRAPH-02 | zero-LLM entity extractor on every reasoning-surface write (regex + heuristic cascade, pattern from gbrain) | 3 days | v1.1 |
| CP-GRAPH-03 | `episteme guide --context=<signature>` Recall@5 benchmarking (synthetic corpus target per NEXT_STEPS entry) | 2 days | v1.1 |
| CP-GUIDE-01 | cross-session guidance replay — last-session context-signature + advisory continuation at SessionStart | 2 days | v1.1 |
| CP-RETRO-01 | retrospective sync-plan completeness verification (cross-surface orphan-reference detection; spec-deferred since CP10 — deferred #4) | 4 days | v1.1 |

**Non-goals**:
- Do NOT invoke LLMs on the write path. Entity extraction stays
  regex+heuristic per gbrain discipline; Recall@5 quality is the
  metric, not semantic depth.
- Do NOT produce advisory blocks. Guidance is always advisory per
  Pillar 3 design — collapsing to enforcement creates a feedback
  loop where the kernel enforces its own synthesis against the
  operator.

**Acceptance criteria**:
- Framework graph emits ≥ 10 non-trivial protocols after 30-day soak.
- `episteme guide` query returns context-matched protocols at
  Recall@5 ≥ 0.7 on synthetic test corpus.
- ≥ 1 operator spot-check verdict confirms advisory guidance was
  helpful (not just technically correct but operator-valuable).

### 3.5 Theme 5 — Cognitive-Adoption Gates Raising (v1.2)

**Maps to all four Jobs via measurement.** Strengthens the Day-7
rubric so v1.2+ releases have higher bar than v1.0.

| CP | Scope | Effort | Milestone |
|---|---|---:|---|
| CP-GATE-01 | raise Gate 21 form-filling rate threshold from > 40% band-downgrade to > 25% (after 50+ record corpus calibration per CP-DISC-02) | 1 day | v1.2 |
| CP-GATE-02 | add Gate 29 — `synthesized_protocol` refs trace to ≥2 distinct reasoning-surface fields per emission | 2 days | v1.2 |
| CP-GATE-03 | add Gate 30 — cascade-theater audit: sampled Blueprint-D firings show ≥ 60% "real sync" verdict (Layer 8 discipline) | 2 days | v1.2 |
| CP-GATE-04 | add Gate 31 — guidance-acted-on rate: advisory emissions with operator spot-check "used" verdict / total emissions ≥ 10% | 2 days | v1.2 |
| CP-DISC-02 | discriminator threshold re-calibration against 50+ record post-v1.0 corpus | 1 day | v1.1 prereq |

**Non-goals**:
- Do NOT raise gates before v1.0.1 evidence pipeline hardening
  completes. Raising gates on broken infrastructure produces noise.
- Do NOT add gates that only one kind of work triggers. Every new
  gate must match ≥ 3 distinct op classes to avoid gate-gaming.

**Acceptance criteria**:
- v1.2 baseline ≥ 6/11 clear-pass on raised bar.
- v1.2 honest-disclosure release notes show which gates tightened
  and why.

### 3.6 Cross-cutting — TUI + observability (v1.1 candidate)

**Maps to Job 3 (guidance visibility).** Inspired by Hermes
v2026.4.23's Ink-based TUI (see §5). episteme benefits from
visualizing the reasoning-surface + framework protocol emissions +
Phase 12 drift + gate-grading state in real-time.

| CP | Scope | Effort | Milestone |
|---|---|---:|---|
| CP-TUI-01 | `episteme tui` — Textual-based (Python-native; avoid Node/Ink dep) dashboard showing current reasoning-surface status, episodic-record stream, recent framework protocols, Gate 21-28 live grading | 5-7 days | v1.1 |
| CP-TUI-02 | subagent-spawn observability overlay (map Task-tool invocations to surface + outcome per spawn) | 3 days | v1.1 |
| CP-WEB-01 | web dashboard parity — `/dashboard` route showing Hermes-style observability but web-native | 4 days | v1.1 |

**Non-goals**:
- Do NOT build a TUI that tries to REPLACE the Claude Code / Hermes
  agent surface. episteme is a governance layer; the TUI is
  observability into our layer, not an agent chat UI.
- Do NOT introduce a Node/Ink dependency for core CLI. TUI is
  optional, Python-native (Textual library), installable as extra.

**Acceptance criteria**:
- TUI runs against live `~/.episteme/*.jsonl` streams without
  read-lock contention.
- Operator can derive Day-7 grading state in 30 seconds via TUI
  without running `grade_gates.py` manually.

### 3.7 Cross-project vision (v2.0 candidate)

**Maps to Job 2 + 3 at cross-project scale.** The operator's governing
intent includes "continuously update the framework" — today that's
per-project. v2.0 would consolidate protocol streams across multiple
projects so a protocol synthesized in project A surfaces as advisory
in project B when context-signature matches.

Scoped as v2.0 candidate because:
- Requires stable per-project framework format (v1.1 consolidation
  first).
- Raises privacy + trust questions not load-bearing in single-project
  v1.0 (cross-project context may leak local details).
- Needs cross-project hash-chain continuity — non-trivial.

Not executing this in v1.x explicitly — keeping it named so the
governing intent stays visible, but committing to the single-project
scope for v1.0 → v1.2.

---

## 4. Dependency graph — what blocks what

```
v1.0.0 GA (Day-7 branch 2.A)
    │
    ├─→ v1.0.1 Evidence Pipeline Hardening (§3.1)
    │      │
    │      ├─→ CP-FENCE-02 ✓ (Event 50)
    │      ├─→ CP-TEL-01 ✓ (Event 49)
    │      ├─→ CP-DEDUP-01 ✓ (Event 49) ──→ CP-DEDUP-02 retro cleanup
    │      ├─→ CP-CASCADE-01 (exempt state files) ──→ reduces own-noise
    │      ├─→ CP-CHKPT-01 (auto-checkpoint fix)
    │      └─→ CP-SMOKE-01 (plugin-install smoke test)
    │
    ├─→ v1.0.1 Schema Evolution (partial) (§3.2)
    │      ├─→ CP-SCHEMA-01a/b (enum additions)
    │      └─(CP-SCHEMA-02 + 03 defer to v1.1)
    │
    ├─→ v1.0.1 Behavior Knobs (partial) (§3.3)
    │      ├─→ CP-KNOBS-01 (autonomy_class wired)
    │      └─→ CP-KNOBS-02 (fence_check_strictness wired)
    │                │
    │                └─→ v1.1 Ashby + Jaynes build on these
    │
    └─→ v1.1 Framework Consolidation (§3.4)
           │
           ├─→ CP-SCHEMA-02 + 03 (from §3.2 deferred)
           ├─→ CP-DISC-02 (threshold re-calibration) ──→ unlocks Theme 5
           ├─→ CP-GRAPH-01 + 02 ──→ CP-GRAPH-03 (Recall@5)
           ├─→ CP-GUIDE-01 (cross-session guidance)
           ├─→ CP-RETRO-01 (retrospective sync-plan verification)
           │
           └─→ v1.2 Cognitive-Adoption Gates Raising (§3.5)
                  ├─→ CP-GATE-01..04 (raised bar + new gates)
                  │
                  └─→ v2.0 candidate: cross-project consolidation (§3.7)
```

Estimated execution calendar (assuming v1.0.0 GA Day-7 branch):

- v1.0.1-rc1 soak open: +10 days from GA
- v1.0.1 GA: +24 days from v1.0.0 GA (3-week sprint + 1-week soak)
- v1.1-rc1 soak open: +45 days from v1.0.0 GA
- v1.1 GA: +60 days
- v1.2-rc1: +90 days

Subject to operator-availability windows; calendar is best-case, not
commitment.

---

## 5. Appendix — Lessons from Hermes v2026.4.23 (Nous Research)

Hermes Agent v0.11.0 (2026-04-23) — published same day as our Event 38
soak anchor — shipped a major release with an Ink-based TUI, pluggable
transport layer, 5 new inference paths, expanded plugin surface, and
the `/steer` mid-run nudge command. Episteme uses Hermes as one of its
adapter targets (`src/episteme/adapters/hermes.py`), so their release
patterns are directly relevant to our v1.1 roadmap.

### 5.1 Adopt

- **Textual-based TUI (Hermes uses React/Ink)** — our equivalent
  stays Python-native (Textual library) to avoid a Node runtime
  dependency in core CLI. Scoped as CP-TUI-01 (§3.6). Features to
  mirror: status bar with stopwatch + git branch + session state;
  subagent spawn observability overlay (Task-tool integration);
  stable picker keys for reproducible flows.

- **`/steer`-style mid-run nudge** — Hermes `/steer <prompt>`
  injects a note the running agent sees after next tool call
  without breaking prompt cache. episteme equivalent:
  `episteme guide --inject <protocol-id>` operator command that
  appends a framework-protocol advisory to the agent's next
  PreToolUse payload. Aligns with Pillar 3 active guidance; maps
  to Job 3 (proactive guidance). Candidate v1.1 addition under
  Theme 4 as CP-GUIDE-02 (not yet in §3.4 — to be added if
  roadmap progresses past v1.0.1).

- **Plugin surface patterns (`transform_tool_result`,
  `dispatch_tool`, hook-veto)** — our hooks already do veto
  (block_dangerous.py) and transform (episodic_writer.py captures
  outcomes). Hermes's more general `transform_tool_result` +
  `dispatch_tool` APIs could inform how we expose Pillar 3
  advisory-injection to future adapters. v1.1 scope consideration;
  don't force premature abstraction.

- **Observability overlay — subagent spawn tracing** — tracing
  Task-tool invocations as their own mini-sessions with surface
  + outcome per spawn is a natural fit for the Blueprint-D
  cascade detector. CP-TUI-02 in §3.6.

### 5.2 Consciously NOT adopt

- **Multi-provider LLM transport abstraction** — Hermes extracted
  `AnthropicTransport`, `BedrockTransport`, etc. into
  `agent/transports/`. Tempting to mirror, but episteme is a
  governance layer NOT a runtime; adding a transport abstraction
  is scope creep. Stay one layer up.

- **Messaging-platform expansion (QQBot, Telegram, Feishu, etc.)**
  — Hermes is a multi-platform agent gateway; episteme is not.
  Explicit non-goal.

- **Shell-script hooks generalization** — Hermes lets any shell
  script be a hook. We deliberately chose typed Python hooks
  with strict schemas for kernel discipline (see
  `kernel/CONSTITUTION.md`). Flexibility ≠ discipline; we chose
  discipline.

- **Provider-catalog live-discovery (GPT-5.5 via Codex OAuth)**
  — episteme doesn't maintain a model catalog; adapters cover
  the tool-ecosystem, not the provider ecosystem.

- **Plugin-packaged image_gen / TTS / STT backends** — out of
  product scope. episteme ≠ multi-modal orchestration layer.

### 5.3 Adoption matrix summary

| Hermes v0.11 feature | episteme decision | Milestone |
|---|---|---|
| Ink TUI | Adopt (Textual, Python-native) | v1.1 CP-TUI-01 |
| Subagent spawn overlay | Adopt | v1.1 CP-TUI-02 |
| `/steer` mid-run nudge | Adopt (as `episteme guide --inject`) | v1.1 candidate |
| Plugin: `transform_tool_result`, `dispatch_tool` | Study for Pillar 3 advisory API; defer commitment | v1.1 review |
| Transport ABC (multi-provider) | Explicit non-goal | — |
| Messaging platform expansion | Explicit non-goal | — |
| Shell-script hooks | Explicit non-goal | — |
| Provider-catalog live discovery | Explicit non-goal | — |
| Bundled image_gen / TTS plugins | Explicit non-goal | — |

### 5.4 Counter-positioning observation

Hermes v0.11's release narrative centers on *surface expansion* —
more transports, more platforms, more plugin capabilities. episteme's
v1.0 → v1.2 narrative should center on *depth of epistemic
correctness* — more evidence pipeline hardening, more schema
fidelity, more gate-grading rigor. These are complementary products:
Hermes grows the surface; episteme grows the governance
underneath. The roadmap above should not chase Hermes's surface-
expansion tempo; stay true to the governance mandate.

### 5.5 Langfuse v3.170.0 — context

Langfuse (`langfuse/langfuse` · YC W23 · ~26k stars · TypeScript ·
self-hostable) describes itself as *"Open source LLM engineering
platform: LLM Observability, metrics, evals, prompt management,
playground, datasets."* v3.170.0 shipped 2026-04-23 (same day as
the Hermes release and our Event 38 soak anchor — which is
coincidental, but convenient: one clean reference date for all
three adjacent-ecosystem scans).

Langfuse's primary loop: app-developer instruments their LLM
integration → traces flow into Langfuse → scoring (manual or
programmatic LLM-as-judge) attaches to traces → datasets get
built from high-signal traces → prompt templates get versioned
against dataset benchmarks → playground lets operators compare
side-by-side.

Episteme's primary loop is **one layer up the stack**: an agent
(not a single LLM call) runs under governance; reasoning-surfaces
+ episodic records capture the decision substrate, not just the
prompt-completion pair; gate-grading is cognitive-adoption
measurement, not response-quality eval.

So the overlap is at **evidence-shape**, not at product category.
That shapes every adopt/decline call below.

### 5.6 Adopt (from Langfuse)

- **OpenTelemetry-compatible export for the evidence stream** —
  Langfuse integrates natively with OpenTelemetry's LLM semantic
  conventions. Episteme's episodic + framework + telemetry streams
  could emit OTel-compatible spans as an optional export format.
  Value: portability + interop with any OTel-compatible tool
  (Grafana, Jaeger, Datadog, Langfuse itself) without becoming an
  observability product ourselves. Maps to Job 4 (continuous
  self-maintenance: the ecosystem's tooling audits the kernel's
  own records). Candidate **v1.2 scope as CP-OTEL-01** (effort
  ~3 days; standardization not feature-expansion).

- **Dataset-from-traces primitive** — Langfuse lets an operator
  promote selected traces into a dataset used for regression
  testing prompts. Episteme's analog: an `episteme dataset build`
  subcommand that promotes selected episodic records (operator
  spot-check "used" verdicts, or gate-grading PASS records, or
  specific context-signature clusters) into a versioned corpus
  for discriminator calibration + gate-grading regression. Maps
  directly to CP-DISC-02 (discriminator threshold re-calibration
  against larger corpus — §3.5 prerequisite). Candidate **v1.1
  scope as CP-DATASET-01** (effort ~2 days; operator-triggered
  workflow, not automatic).

- **LLM-as-judge scoring pattern (study, not adopt wholesale)** —
  Langfuse's programmatic eval framework uses an LLM to score
  trace quality against a rubric. For episteme: the form-filling
  discriminator (§1.9 POST_SOAK_TRIAGE) is deliberately
  deterministic (regex + density). LLM-as-judge is NOT a
  replacement because it reintroduces the exact failure mode
  (confidently-fluent-output) the kernel exists to detect.
  BUT: LLM-as-judge could be a **secondary cross-check** on a
  small sample — if the regex discriminator and an LLM judge
  disagree on the same record, that's a threshold-calibration
  signal. Candidate **v1.2 as CP-DISC-03 — LLM-cross-check
  audit** (effort ~2 days; advisory-only, never replaces the
  deterministic path).

- **Self-hostable + sovereignty stance** — Langfuse's self-host-
  first model aligns with episteme's Pillar 2 tamper-evident
  local-only semantics. No adopt needed — we already ship this.
  Noting as **parallel design philosophy** that validates our
  posture for external observers (reviewers, adopters) who
  understand Langfuse's positioning.

### 5.7 Consciously NOT adopt (from Langfuse)

- **Prompt management as a product feature** — Langfuse stores
  prompt templates, versions them, A/B-tests variants. Episteme
  is not a prompt-ops product. Our analog — the reasoning-surface
  schema — is load-bearing structure, not user-editable templates.
  Making reasoning-surfaces user-editable would collapse the
  governance contract. **Explicit non-goal.**

- **Playground / interactive exploration UI** — Langfuse's
  playground lets operators iterate prompts against live models.
  Episteme's analog would be "iterate on reasoning-surface fields
  against live agent runs" — but that's the agent itself doing
  the iteration, not a separate UI. Also the Textual TUI (§3.6
  CP-TUI-01) covers the observability side, not the interactive-
  exploration side. **Explicit non-goal.**

- **Multi-LLM-provider SDK abstractions** — Langfuse supports
  OpenAI SDK, Langchain, LlamaIndex, LiteLLM. Same rationale as
  the Hermes transport-ABC non-adopt (§5.2): we're governance,
  not runtime. Every SDK abstraction we add is scope creep away
  from the kernel mandate. **Explicit non-goal.**

- **Analytics-dashboard-as-primary-surface** — Langfuse's UI is a
  web dashboard for observability-first workflows. Episteme has
  a web/ surface today, but it's marketing-facing + a small
  fixtures visualization — not a general-purpose observability
  dashboard. The TUI (CP-TUI-01) + web dashboard parity
  (CP-WEB-01) stay **scoped to the kernel's own evidence
  streams**, not a general LLM observability product. The
  governance mandate would be diluted if we tried to become a
  Langfuse competitor. **Explicit non-goal at the product
  positioning level.**

### 5.8 Adoption matrix summary

| Langfuse v3.170 feature | episteme decision | Milestone |
|---|---|---|
| OpenTelemetry export | Adopt (portability, standardization) | v1.2 CP-OTEL-01 |
| Dataset-from-traces | Adopt (operator-triggered) | v1.1 CP-DATASET-01 |
| LLM-as-judge eval | Adopt as secondary cross-check, not replacement | v1.2 CP-DISC-03 |
| Self-host-first sovereignty | Parallel design — already shipped | — |
| Prompt management | Explicit non-goal (would break governance contract) | — |
| Playground UI | Explicit non-goal | — |
| Multi-LLM SDK abstractions | Explicit non-goal (governance, not runtime) | — |
| Analytics-dashboard-as-product | Explicit non-goal (stay kernel-scoped) | — |

### 5.9 Counter-positioning observation (Langfuse)

Langfuse and episteme occupy **different layers of the agent
stack**, not different segments of the same layer:

- **Langfuse**: LLM-call observability + prompt-ops for app
  developers. "Is my LLM integration producing the right output?"
- **episteme**: Agent-reasoning governance for kernel architects.
  "Is the agent thinking in a way that would survive external
  audit?"

A team could (and should) use both simultaneously. Langfuse sees
the LLM call shape; episteme sees the reasoning shape around the
call. OpenTelemetry export from episteme → Langfuse could
literally federate the two: LLM-call observability in Langfuse,
cognitive-adoption governance in episteme, same underlying trace
standard.

This is the cleanest counter-positioning the roadmap has
surfaced so far: **Langfuse and episteme are vertically composable,
not horizontally competitive.** A v1.2 `CP-OTEL-01` makes this
composition explicit.

### 5.10 Cross-ecosystem pattern emerging

Two ecosystem scans in (Hermes §5.1-§5.4, Langfuse §5.5-§5.9) reveal
the same pattern repeating:

| Ecosystem | Their move | Our non-adopt rationale |
|---|---|---|
| Hermes | Multi-provider LLM transports | We're governance, not runtime |
| Langfuse | Multi-LLM SDK abstractions | Same |
| Hermes | Messaging platform expansion | Not our scope |
| Langfuse | Prompt management | Would break governance contract |
| Hermes | Shell-script hook flexibility | We chose typed Python for kernel discipline |
| Langfuse | Playground interactive UI | Not our product |

**Pattern**: every adjacent ecosystem expands its surface (providers,
platforms, modalities, UI richness). Episteme's opposite move —
deepening the governance underneath — is what makes the two
composable rather than competitive. This is not a reason to dismiss
ecosystem scans; it's a reason to keep doing them, because the
named non-adopts reinforce the governance mandate better than any
abstract statement would.

If a third ecosystem scan (e.g., next cadence) produces net-zero
adopt items, that's a signal: either the scan methodology is
over-fitting to our existing plans, or the ecosystem has genuinely
converged. In either case, re-evaluate whether quarterly cadence is
the right cadence.

---

## 6. How this doc stays current

- **Every Event that adds a CP** updates §3.1-§3.5 status columns.
- **Every v1.x GA** triggers a post-GA review: did the milestone
  theme acceptance criteria actually hold? Adjust next milestone
  accordingly.
- **Day-7 grading outcome** selects the executing branch (§2.A/B/C)
  and tightens §3 milestone effort estimates based on real
  evidence.
- **Quarterly** (≈ every v1.x GA): revisit §5 adjacent-ecosystem
  lessons — has Hermes / Claude Code / Codex shipped patterns
  worth adopting or explicitly declining?

If the operator intent (§0) shifts, this whole doc is deprecated and
rewritten goal-backward. The governing intent is the anchor; the
milestones are the implementation.
