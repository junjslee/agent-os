# Post-Soak Triage — v1.0 GA Decision Protocol

Governance document. Converts 7 days of v1.0.0-rc1 soak telemetry into a defensible
v1.0 GA / no-GA / scope-retreat verdict. Replaces ad-hoc "does it feel ready" judgment
with a four-phase rubric that an outside reviewer can audit without asking the operator
what they were thinking.

Created Event 46 (2026-04-24). Target execution window: soak close ~2026-04-30 (±7 days
per operator-availability extension window).

---

## 0. Core principle — measurement IS the gradient

The kernel's product thesis is that autonomous agents fail by form-filling: producing
fluent-looking structure that passes eyeball checks while carrying no real reasoning.
The post-soak triage is dogfood. If we judge v1.0 readiness by eyeballing the dashboard
(**"gates look good, ship it"**), we have already lost to the failure mode the product
exists to detect.

Therefore:

1. Every gate below has a named **data source**, a **measurement procedure**, and
   **PASS / PARTIAL / FAIL bands** — not "looks good."
2. Every gate has a **counter-example question**: "what record in this data source
   would force a FAIL grade?" If the operator cannot name one in 30 seconds, the
   rubric is decorative, not load-bearing.
3. The **form-filling discriminator** (§1.9) applies on top of Gate 21/23/24 because
   those gates measure the reasoning-surface corpus, and the reasoning-surface is where
   form-filling hides first.

The decision rule is deliberately conservative (§4): **GA requires ≥ 4 of 8 clear-pass**,
and any Gate 28 (kernel-on-kernel dogfood) failure is a hard block regardless of the
other seven. This is the kernel's own "buffer" mental model (Munger latticework,
margin-of-safety) applied to its own release decision.

---

## 1. Phase 1 — Gate grading at Day 7

Gates 21-28 were defined during v1.0.0-rc1 planning as the *cognitive-adoption* gates
(Gates 1-20 are infrastructure). Each gate below is a direct grading procedure, not a
restatement of the original definition.

### 1.1 Gate 21 — Reasoning-Surface snapshot quality

- **Origin claim**: "Sample 20 random episodic records. Target: zero lazy placeholders
  and zero disconfirmations without observable outcomes."
- **Data source**: `~/.episteme/memory/episodic/*.jsonl` **after** Event 38 fresh-soak
  start (2026-04-23T21:23:36Z). Records before that timestamp are from the broken
  pipeline era and do not count.
- **Sample procedure**: `shuf -n 20 ~/.episteme/memory/episodic/*.jsonl` — if post-soak
  corpus < 20 records, grade on whatever exists and mark sample-size caveat in the
  grading report.
- **Scoring** (per record): (+1) for each of the 4 reasoning-surface fields (knowns,
  unknowns, assumptions, disconfirmation) that satisfies ALL of:
  - ≥ 15 chars non-whitespace content
  - Zero lazy tokens (see §1.9 form-filling discriminator)
  - Mentions at least one **proper noun** (file path, command name, gate number, error
    code, SHA, ticket id) — this is the anti-abstraction anchor
  - For `disconfirmation`: contains an **observable verb phrase** (see §1.9)
- **Bands**:
  - **PASS**: ≥ 3.2/4 average across the sample (80% field-richness)
  - **PARTIAL**: 2.4 – 3.1 (60-79%) — typically means disconfirmations lack observable
    verbs or unknowns default to abstract phrasing
  - **FAIL**: < 2.4 (< 60%) — indicates form-filling pattern dominating
- **Counter-example question**: "Show me one record where `unknowns` is 15+ chars but
  doesn't name a file/command/gate." If such records dominate → FAIL.

### 1.2 Gate 22 — Disconfirmation actually fires

- **Origin claim**: "On ≥ 1 recorded decision, the disconfirmation triggered a
  downstream action change."
- **Data source**: `~/.episteme/memory/episodic/` cross-referenced with git log.
- **Measurement procedure**: Grep episodic records for pattern "disconfirmation
  triggered" or "disconfirmation fired" or "invalidated by" in session-summary fields.
  Then verify the next episodic record from the same session shows a deviation from
  the original hypothesis (different command sequence, different branch strategy,
  different fix approach).
- **Bands**:
  - **PASS**: ≥ 2 cases with named disconfirmation → named action change, both
    within the Event-38 soak window
  - **PARTIAL**: 1 case, or ≥ 2 cases where only the operator retrospectively
    labels the change as disconfirmation-triggered (weaker evidence)
  - **FAIL**: 0 cases — disconfirmation field is decorative
- **Counter-example question**: "Show me the git commit where we abandoned the
  original approach because the disconfirmation fired." If the operator cannot point
  to a specific SHA → FAIL.
- **Caveat**: Gate 22 is the **hardest gate to pass honestly**. Most soak weeks don't
  produce real disconfirmation events. PARTIAL is the realistic target.

### 1.3 Gate 23 — Facts / inferences / preferences stay separated

- **Origin claim**: "< 10% cross-labeling across sampled records."
- **Data source**: Same 20 records as Gate 21.
- **Measurement procedure**: For each record's `knowns` field, classify each entry as
  (a) **fact** (verifiable by running a command / reading a file), (b) **inference**
  (derived from facts + reasoning), or (c) **preference** (operator or agent
  judgment). Cross-label rate = (inferences mislabeled as knowns + preferences
  mislabeled as knowns) / total-knowns-entries.
- **Bands**:
  - **PASS**: < 10% cross-labeling (original criterion)
  - **PARTIAL**: 10-25% — usually inferences being claimed as facts
  - **FAIL**: ≥ 25% — knowns field is acting as a general "stuff I think" dumping
    ground
- **Counter-example question**: "Show me one `knowns` entry that would not survive
  `grep` or a `git log` check." Every record should have at least one such failure
  mode already avoided — if 5+/20 have them → FAIL.

### 1.4 Gate 24 — Hypothesis → test → update cycle observable

- **Origin claim**: "Observable on ≥ 3 of 5 sampled surfaces."
- **Data source**: Sample 5 reasoning-surface records (`hypothesis` field must be
  non-empty); cross-reference with same-session episodic records to see whether the
  hypothesis was validated, refined, or invalidated.
- **Measurement procedure**: Per surface, look for a closing record (end-of-session
  or mid-session checkpoint) that names the hypothesis outcome. Accepts any of:
  - **validated** — hypothesis held; cite evidence
  - **refined** — hypothesis partially held, narrowed scope with new data
  - **invalidated** — hypothesis wrong; cite the contradicting observation
- **Bands**:
  - **PASS**: ≥ 3/5 surfaces show a closed hypothesis loop
  - **PARTIAL**: 2/5
  - **FAIL**: ≤ 1/5 — hypotheses are write-only; agent is not updating its model on
    results
- **Counter-example question**: "Which hypothesis this week was honestly invalidated?"
  If the answer is "none, they all worked," either the soak had no real contested
  work OR Gate 24 is silently failing (overclaim). Either way, not PASS.

### 1.5 Gate 25 — Phase 12 profile-audit surfaces real drift

- **Origin claim**: "≥ 1 real drift detection against the operator's own profile."
- **Data source**: Phase 12 profile-audit output. **Unknown as of Event 46**: exact
  file path for Phase 12 audit emissions. Pre-grading task: confirm path (candidates:
  `~/.episteme/audit.jsonl`, `~/.episteme/state/profile_audit.log`, or per-session
  stdout). Grading blocked until path is verified.
- **Measurement procedure** (once path is verified): For each `inferred` axis in
  `core/memory/global/operator_profile.md`, check whether the audit produced a
  promotion recommendation (`inferred → elicited`) OR a drift flag (elicited value
  no longer matching recent behavior). Either counts as "real drift detection."
- **Bands**:
  - **PASS**: ≥ 1 named axis with audit-surfaced evidence AND the operator acted on
    it (either promoted the axis or corrected the value)
  - **PARTIAL**: ≥ 1 audit emission exists but operator has not reviewed it
  - **FAIL**: audit produced zero emissions across the soak window
- **Counter-example question**: "Name one axis this soak should have flagged based
  on observed behavior." If the operator can name one the audit missed → FAIL
  (false negative). If the operator cannot name one → sample size too small, mark
  insufficient-evidence-to-grade.

### 1.6 Gate 26 — Semantic-tier promotion emits reasoning-shape regularity

- **Origin claim**: "≥ 1 reasoning-shape regularity emitted, not just outcome
  regularity."
- **Data source**: `~/.episteme/framework/protocols.jsonl` (canonical path for
  framework synthesis output per `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`).
- **Distinction that matters**: An **outcome regularity** is "command X tends to
  succeed/fail under condition Y." A **reasoning-shape regularity** is "when the
  agent faces decision-type Z, it tends to consider option A before option B" or
  "disconfirmation fields under cascade:architectural posture tend to enumerate
  three failure paths." Outcome regularities are pattern-matching; reasoning-shape
  regularities are cognitive-process pattern-matching — harder to produce, more
  load-bearing.
- **Measurement procedure**: Read all protocols emitted during the Event-38 soak
  window. Classify each as outcome-shape or reasoning-shape. Reasoning-shape
  requires the protocol's condition OR action to reference a reasoning-surface
  field (knowns/unknowns/assumptions/disconfirmation/hypothesis/posture).
- **Bands**:
  - **PASS**: ≥ 1 reasoning-shape regularity emitted; matches a real pattern the
    operator can confirm from memory
  - **PARTIAL**: protocols emitted but all are outcome-shape
  - **FAIL**: zero protocols emitted during the soak window (synthesis pipeline is
    silent)
- **Counter-example question**: "Which of the emitted protocols would change the
  agent's next reasoning-surface if fired?" If answer is "none, they're all about
  command exit codes" → PARTIAL, not PASS.

### 1.7 Gate 27 — Failure-mode taxonomy citation (revised per Event 37)

- **Revised claim** (original grading was measurement-dimension mismatch — see
  `kernel/FAILURE_MODES.md` "Two-vocabulary distinction"): FAILURE_MODES.md ids
  appear in kernel prose (CONSTITUTION.md, REFERENCES.md, design docs, blueprint
  descriptions) with ≥ 3 distinct ids cited load-bearingly.
- **Data source**: `kernel/` + `docs/DESIGN_*.md` prose grep.
- **Measurement procedure**: Grep for the 9 canonical FAILURE_MODES ids (WYSIATI,
  question-substitution, anchoring, narrative-fallacy, planning-fallacy,
  overconfidence, fence-check, context-poisoning, others per current taxonomy).
  "Load-bearing" means the citation explains WHY a feature exists, not just
  mentions the id in a reference list.
- **Bands**:
  - **PASS**: ≥ 3 distinct ids cited in ≥ 2 files each, where removing the citation
    would leave a "why does this feature exist" gap
  - **PARTIAL**: 2 ids cited, or citations present but all in one file
  - **FAIL**: taxonomy still decorative in kernel prose
- **Counter-example question**: "If we removed FAILURE_MODES.md right now, would any
  feature's motivation become unexplained?" If answer is "no, just a few footnotes"
  → FAIL regardless of grep count.
- **Orthogonal ungraded dimension**: The original Gate 27 "FAILURE_MODES cited in
  episodic records" remains ungradeable until Path 4B adds a
  `reasoning_failure_mode` surface field. Do not re-grade against that dimension
  without the schema change.

### 1.8 Gate 28 — Kernel-on-kernel dogfood

- **Origin claim**: "Kernel edits on episteme itself show the same discipline
  demanded of downstream users."
- **Data source**: Episode records + reasoning-surfaces for all soak-window commits
  that touched `core/hooks/`, `src/episteme/`, or `kernel/`.
- **Measurement procedure**: For every such commit during the Event-38 soak window,
  verify: (a) a reasoning-surface existed and was non-stale (≤ 30 min before the
  commit), (b) the surface named the change's blast radius, (c) at least one
  episodic record cross-references the commit SHA.
- **Bands**:
  - **PASS**: 100% of kernel-touching commits have all three evidence items
  - **PARTIAL**: ≥ 80% have all three, remainder have at least (a)
  - **FAIL**: any kernel-touching commit with no reasoning-surface at all → **hard
    FAIL regardless of other evidence**. The product's core claim is "the kernel
    enforces its own discipline"; a single surface-less kernel commit breaks that
    claim on the kernel's own repo.
- **Special weight**: Gate 28 failure is a **hard GA block** (§4). Other gates can
  fail and still allow GA with named scope retreat; Gate 28 cannot.
- **Counter-example question**: "Is there a commit this soak I would not want an
  external reviewer to audit?" Name it now — if yes → FAIL.

### 1.9 Form-filling discriminator (applies atop Gates 21, 23, 24)

The gap Event 46's Phase 1 evaluation identified as sharpest. Without this, Gate 21
degenerates into "does the JSON have 4 fields populated with ≥ 15 chars" — exactly
the failure mode the kernel exists to detect.

Three sub-metrics, each computable via a small Python/awk script over
`~/.episteme/memory/episodic/*.jsonl`:

**(a) Lazy-token regex screen**
  - Regex (case-insensitive, word-boundary): `\b(none|n/a|tbd|todo|later|somehow|maybe|perhaps|various|misc|etc\.?|placeholder|generic)\b`
  - Also Korean: `\b(해당\s*없음|없음|나중에|어떻게든)\b`
  - Failure condition: any match in the reasoning-surface fields

**(b) Proper-noun density**
  - Count: file paths (contain `/` or `.md` or `.py`), SHA-like tokens (≥ 6 hex
    chars), gate numbers (`Gate \d+` or `G\d+`), error codes, command names
    (`git`, `gh`, `pnpm`, etc. — known tool-name list), ticket references
    (`#\d+`, `PR #\d+`, `Event \d+`)
  - Per reasoning-surface field, target ≥ 1 proper-noun token per 80 characters of
    content
  - Threshold rationale: a surface saying "the workflow may fail" has zero
    proper nouns; a surface saying "`.github/workflows/clone.yml` cron `0 */24 *
    * *` lands on contended 00:00 UTC slot" has three (file, field, value)

**(c) Observable-verb density (disconfirmation field only)**
  - Required verbs (at least one per disconfirmation): `fires`, `fails`,
    `returns`, `exits`, `blocks`, `resolves`, `matches`, `emits`, `produces`,
    `logs`, `writes`, `reads`, `passes`, `hangs`, `times out`, `throws`
  - Korean equivalents: `실패`, `반환`, `차단`, `해결`, `일치`, `발생`
  - A disconfirmation that says "the approach might not work well" has no
    observable verb; "`pnpm build` exits with code 1" has one
  - Threshold: 100% of non-empty disconfirmation fields must contain at least one

**Grading integration**:
  - A reasoning-surface that fails (a) or fails (b) on ≥ 2 of 4 fields or fails
    (c) — **drop one point from its Gate 21 score**.
  - Aggregate form-filling rate across the 20-record sample. If > 40% of records
    fail the discriminator on any sub-metric → **Gate 21 downgrades one band**
    regardless of nominal field-richness (PASS → PARTIAL, PARTIAL → FAIL).
  - Discriminator thresholds are **calibrated at first use on the current corpus**
    (see Phase 3 CP-DISC-01). If every historical surface fails the proper-noun
    density screen, threshold is too strict; if none fail, threshold is too loose.

---

## 2. Phase 2 — Deferred-discovery triage

1,294 records currently sit in `~/.episteme/framework/deferred_discoveries.jsonl`.
At the current rate these accumulate faster than any human can individually review.
Phase 2 converts that pile into an ordered list of real debt.

### 2.1 Classification procedure

For each of the 1,294 records, assign one of three labels:

- **REAL-DEBT** — describes a kernel/code issue that still exists in current master
  and would change agent behavior if fixed. Example: "fence_synthesis.py produces
  empty output for cascade:architectural posture."
- **RESOLVED** — the described issue no longer applies; a subsequent commit fixed
  the underlying condition. Requires naming the commit SHA.
- **NOISE** — described a transient state, a decorative observation, or a
  non-actionable musing. Example: "commit took longer than expected."

### 2.2 Scaling approach

Full human review of 1,294 records is not the plan. Instead:

1. **Structural pre-classification** (script-driven): sort records by
   `flaw_classification` enum value. The 666 `schema-implementation-drift` records
   are the largest bucket and are candidates for batch-resolve (one schema fix
   often retires dozens of records).
2. **Recency filter**: records from the broken-pipeline era (before Event 38) are
   deprioritized — the pipeline itself was in an inconsistent state, so the signal
   quality is lower.
3. **Sample-and-extrapolate**: manually classify 50 post-Event-38 records.
   Extrapolate rates (% REAL-DEBT, % RESOLVED, % NOISE) to estimate total REAL-DEBT
   count within ±20%. Full manual review is deferred to v1.0.2 or later.

### 2.3 Output

`docs/DEFERRED_DISCOVERIES_TRIAGE.md` (to be created post-soak) listing:
- The ~20-50 REAL-DEBT items identified in the sample
- Estimated total REAL-DEBT count (sample × 1,294 / 50)
- Top-3 structural patterns driving the pile (which inform CP priorities)

---

## 3. Phase 3 — v1.0.1 CP (correction protocol) derivation

Seed candidates identified during Event 46 drafting. Full list derives from Phase 1
failures + Phase 2 REAL-DEBT items.

### 3.1 Pre-seeded candidates

**CP-TEL-01 — Calibration telemetry asymmetry**
  - **Observation**: 3,357 `prediction` events vs 80 `outcome` events across 5
    days of telemetry; 100% of the 80 outcomes captured have `exit_code: null`.
  - **Two failure layers**: (1) outcome events are not being written proportionally
    to predictions (42× gap); (2) even the outcomes we do capture have null exit
    codes, making calibration mathematically impossible.
  - **Consequence**: Gate 22 grading has no objective substrate. Disconfirmation
    "firing" cannot be verified against predicted outcomes.
  - **Priority**: HIGH — blocks Gate 22 + Gate 24 rigor; v1.0.1 scope.
  - **Likely root cause (unverified)**: `calibration_telemetry.py` hook either not
    receiving exit_code from the Bash tool protocol, or not writing the outcome
    event pair for short-lived commands.

**CP-FENCE-01 — Fence synthesis empty-emit**
  - **Observation**: fence_synthesis.py fires on most PostToolUse invocations but
    produces zero fences in its output file on the majority of runs.
  - **Consequence**: Gate 26 (semantic-tier promotion) has nothing to grade.
  - **Priority**: MEDIUM — Gate 26 is not a hard GA block but fence pipeline is
    load-bearing for Pillar 3.
  - **Likely root cause (unverified)**: fence detection threshold too strict, or
    fence state reading from pre-Event-38 cwd.

**CP-DISC-01 — Form-filling discriminator calibration**
  - **Observation**: The discriminator thresholds in §1.9 are operator judgment,
    not empirically calibrated.
  - **Measurement**: Run the discriminator against all post-Event-38 episodic
    records. If false-positive rate on manually-confirmed-good records > 20% →
    thresholds too strict. If false-negative rate on manually-confirmed-lazy
    records > 20% → too loose.
  - **Priority**: HIGH — without calibration, §1.9 is vapor, and Gate 21/23/24
    degrade back to structural checks.

**CP-PHASE12-01 — Phase 12 audit path verification**
  - **Observation**: Gate 25 data source path is not confirmed (§1.5).
  - **Priority**: MEDIUM — affects Gate 25 gradeability only.
  - **Resolution**: ~30 min of grep + one hook-run verification.

### 3.2 Priority formula

For each CP candidate, compute:

```
priority_score = gate_impact × (1 / effort_days)
```

Where `gate_impact` = number of Phase-1 gates a CP unblocks or materially improves,
and `effort_days` = rough dev time (≥ 0.5).

Sort descending. The top-4 seed v1.0.1. Below a threshold (≤ 0.5) → v1.0.2 or
deferred.

---

## 4. Phase 4 — v1.0 GA decision rule

### 4.1 Hard block

Gate 28 (kernel-on-kernel dogfood) at **anything worse than PARTIAL** → no GA.
Rationale: the product's thesis is that the kernel enforces discipline on itself.
A kernel commit with no reasoning-surface on the kernel's own repo is a credibility
failure that no amount of other-gate green can repair.

### 4.2 Primary rule

Of the other 7 gates (21-27):

- **≥ 4 clear-PASS** → **v1.0.0 GA**, with remaining 3 or fewer gates named as
  v1.0.1 scope in the release notes
- **2-3 clear-PASS** → **v1.0.1 release candidate cycle**. Run the top-priority
  CPs (§3), then re-grade. Do not ship GA.
- **≤ 1 clear-PASS** → **scope retreat**. The cognitive-adoption claim is not
  holding up under measurement. Options: (a) demote the cognitive-adoption thesis
  from v1.0 headline to v1.1 roadmap item and ship v1.0 on the engineering claim
  only, or (b) defer v1.0 entirely.

### 4.3 PARTIAL handling

PARTIAL counts as 0.5 of a PASS for the threshold check. Example: 3 PASS + 3 PARTIAL
= 4.5 → meets threshold → GA. But PARTIAL does NOT count toward the Gate 28 hard
block.

### 4.4 Honest-disclosure requirement

The release notes for v1.0.0 GA must include, per-gate:

```
Gate 21 (reasoning-surface quality): PASS — 3.4/4 richness, 18% form-filling rate
Gate 22 (disconfirmation fires): PARTIAL — 1 confirmed case, not 2
Gate 23 (fact/inference/preference separation): PASS — 6% cross-labeling
...
```

This is the dogfood: if the grading report itself reads like form-filling, the
product has failed the post-soak triage by its own criterion.

### 4.5 Decision authority

The operator is the final decision-maker. This rubric makes the decision auditable;
it does not make it automatic. Edge cases (e.g., a novel Gate 28 near-miss that
doesn't cleanly map to PASS/PARTIAL/FAIL) are escalated to the operator with the
evidence that made the grading non-obvious.

---

## 5. Execution timeline

- **~2026-04-30 (Day 7 of Event-38 soak)**: run Phase 1 grading script against the
  soak-window corpus. Produce `docs/GATE_GRADING_2026-04-30.md` with per-gate bands
  + evidence citations.
- **Day 7 + 1**: run Phase 2 sample-and-extrapolate. Produce
  `docs/DEFERRED_DISCOVERIES_TRIAGE.md`.
- **Day 7 + 2**: Phase 3 CP priority list. Update `docs/NEXT_STEPS.md` with v1.0.1
  scope.
- **Day 7 + 3**: Phase 4 decision. Either cut v1.0.0 GA (release-please PR #2
  merges) or cut v1.0.1-rc1 with named CPs.

Extension to ±14 days is acceptable per operator-availability window — the 7-day
minimum is statistical-validity, not calendar-deadline.

---

## 6. What this document is NOT

- It is **not** a fixed spec. Sub-metric thresholds in §1.9 and §3.1 are calibrated
  on first use against the actual corpus. If a threshold is wrong, the rubric gets
  updated — but the update is itself a reasoning-surface-gated change, not a
  drive-by edit.
- It is **not** automation. A grading script can compute field-richness and
  discriminator scores; the "counter-example question" for each gate is an operator
  judgment call against current-state evidence. That's intentional — full
  automation would re-introduce the form-filling failure mode (plausible-looking
  numbers with no semantic check).
- It is **not** forever. At v1.0 GA, the rubric migrates to a slimmer v1.1 version
  with lessons learned. CP-DISC-01's calibration data becomes the v1.1 default.

---

## Appendix A — Data source cheat sheet

| What | Path |
|---|---|
| Episodic records (post-fix) | `~/.episteme/memory/episodic/*.jsonl` |
| Deferred discoveries | `~/.episteme/framework/deferred_discoveries.jsonl` |
| Framework protocols | `~/.episteme/framework/protocols.jsonl` |
| Telemetry audit | `~/.episteme/telemetry/YYYY-MM-DD-audit.jsonl` |
| Hook log | `~/.episteme/state/hooks.log` |
| Operator profile | `core/memory/global/operator_profile.md` |
| Phase 12 audit emissions | **UNVERIFIED** — pre-grading CP-PHASE12-01 |
| Current reasoning surface | `.episteme/reasoning-surface.json` |

---

## Appendix B — Known evidence gaps at draft time

- Phase 12 audit path: see CP-PHASE12-01.
- Gate 22 baseline: no known disconfirmation-fired-and-changed-action commit in the
  soak window yet. Realistic target at Day 7 is PARTIAL.
- Gate 26 baseline: fence pipeline empty-emit pattern (CP-FENCE-01) will likely
  produce an empty protocols.jsonl → FAIL unless the pipeline is fixed pre-soak
  close.
- Form-filling discriminator: not yet implemented (script); CP-DISC-01.

These gaps are named now so the Day-7 grading session does not discover them
mid-execution.
