# Falsifiability Conditions

**Operational summary** (load first if you have a token budget):

- Every load-bearing kernel claim is enumerated here with a concrete observable that would prove it wrong.
- A claim that cannot be falsified is not episteme — it is doxa wearing episteme's vocabulary.
- 14 load-bearing claims grouped into 7 sections. Each row: claim → falsification condition → measurement method → status → action on disconfirmation.
- Status taxonomy: **RUNNING** (test exists, evidence collected), **PARTIAL** (test exists, evidence partial), **SCHEDULED** (test designed, not yet run), **ASPIRATIONAL** (no test infrastructure yet — flag honestly).
- Authority: the kernel must meet its own thesis or its thesis is decorative. This file is the self-applied Popperian gate.
- See [REFERENCES.md § Popper](./REFERENCES.md#philosophy-of-science--falsifiability) for the source attribution; this file is the operationalization.

---

## What this is

Popper's demarcation criterion: a claim about the world must name, in advance, the observable outcome that would prove it wrong. Without that condition, the claim is unfalsifiable — it cannot be distinguished from a post-hoc rationalization that fits any evidence.

The kernel applies this to itself. Every claim about the kernel's value-proposition has a falsifiability condition. Where the condition is concretely measurable today, the test is named and the evidence is cited. Where the condition is currently aspirational, that is named honestly — confirmation theater (only enumerating claims we already know pass) is itself a Doxa-shape and would defeat the discipline.

The kernel's central thesis is that confident wrongness is the dominant failure mode of fluent agents. The kernel must not, in claiming to counter that failure, exemplify it. This file is the structural counter.

---

## How to read this file

Each entry has five fields:

1. **Claim** — the assertion the kernel makes about its own value or correctness, paraphrased from kernel docs (CONSTITUTION / FAILURE_MODES / REASONING_SURFACE / README) with cross-reference.
2. **Falsification condition** — a concrete observable event whose occurrence would falsify the claim. Specific enough to be reproducible. "Vague risk surfaces" is not sufficient.
3. **Measurement method** — how the observable is detected: an existing test, a manual procedure, a planned benchmark, etc.
4. **Status** — whether the test is currently *running* (with evidence to date), *partial* (test exists but evidence incomplete), *scheduled* (test designed, not run), or *aspirational* (no infrastructure yet — named for honesty, not as a claim of falsifiability).
5. **Action on disconfirmation** — what the kernel does when the falsification fires. *"Discuss it later"* is not an action. Concrete: a CP, a doc revision, a hook patch, a claim demotion.

A row whose action-on-disconfirmation is empty or generic is ceremonial. Either the action is concrete or the row should not exist.

---

## § A · Pillar mechanics

### A1 · Pillar 2 hash chain is tamper-evident

- **Claim.** Every reasoning surface, blueprint firing, protocol synthesis, and deferred-discovery is anchored in a cryptographically hash-chained record; tampering is mechanically detectable. ([README § Active Guidance](../README.md); [FAILURE_MODES § Knowledge Sanctuaries](./FAILURE_MODES.md))
- **Falsification condition.** A record in any chained stream (`~/.episteme/memory/episodic/*.jsonl`, `~/.episteme/framework/protocols.jsonl`, `~/.episteme/framework/deferred_discoveries.jsonl`, `~/.episteme/memory/reflective/profile_audit.jsonl`) is modified or inserted post-write without `episteme chain verify` detecting the discrepancy.
- **Measurement method.** Unit tests at `tests/test_chain_*.py`; manual procedure: edit a chained record, run `episteme chain verify`, expect non-zero exit.
- **Status.** **RUNNING.** Chain-verify implemented; baseline tests passing. Real-world tampering test would require an external red-team exercise.
- **Action on disconfirmation.** Treat as critical regression. Audit hash construction in `core/hooks/_chain.py`; immediate kernel patch; investigate whether prior records can be retroactively re-hashed under a recovery-attestation envelope (cross-references CP-CHAIN-RECOVERY-PROTOCOL-01 in `~/episteme-private/docs/cp-v1.1-architectural.md`).

### A2 · Reasoning Surface validator rejects lazy-token disconfirmation

- **Claim.** Strict Mode rejects conditional-but-observable-less disconfirmation phrasing (`"n/a"`, `"if issues arise"`, `"none"`, `"tbd"`, `"해당 없음"`); admits only specific falsification conditions. ([README § The solution](../README.md); [REASONING_SURFACE.md](./REASONING_SURFACE.md))
- **Falsification condition.** A surface with disconfirmation field set to a lazy token (any item from the rejection list) passes the validator and the op proceeds.
- **Measurement method.** Unit tests in `tests/test_*surface*.py`; manual: submit lazy disconfirmation under strict mode, expect refusal.
- **Status.** **RUNNING.** Validator implemented; tests cover the canonical lazy-token list across English + Korean. Bypass-vector expansion would require fuzzing.
- **Action on disconfirmation.** Expand the lazy-token list + tighten regex in `core/hooks/_reasoning_surface_validator.py`; lock down the lazy-list as a versioned artifact; add fuzz tests.

### A3 · PreToolUse hook refuses ops when surface is missing/invalid

- **Claim.** Under strict mode, a high-impact op (cascade:architectural, fence:constraint-removal, irreversible-tier ops) cannot proceed without a valid, TTL-fresh Reasoning Surface declared. Hook exits non-zero. ([README § The solution](../README.md))
- **Falsification condition.** Operator runs a high-impact op (`git push` to main, irreversible DB migration, etc.) under strict mode in a project with NO `.episteme/reasoning-surface.json` (or a stale one past TTL), and the op proceeds without a refusal event in `~/.episteme/state/hooks.log`.
- **Measurement method.** Adversarial test in fresh repo; hook log inspection; Gate 28 dogfood (kernel-on-itself).
- **Status.** **RUNNING.** Verified extensively across Events 36-50 (soak window) + the current session. Gate 28 baseline shows 564 cascade:architectural firings with strict-mode enforcement; 3,675 blocked actions across audit stream.
- **Action on disconfirmation.** Audit `core/hooks/_reasoning_surface_validator.py` + `block_dangerous.py`; identify the bypass vector; emergency CP-FENCE-class patch; hard regression bar in CI.

### A4 · Stateful interceptor catches bypass shapes

- **Claim.** Bypass via `subprocess.run(['git','push'])`, `os.system('git push')`, or agent-written shell scripts (deep-scanned) is caught — the interceptor maintains cross-call stateful memory of agent-written files. ([README § The solution](../README.md))
- **Falsification condition.** Agent writes `attack.sh` containing `git push`, runs `bash attack.sh`, and the push succeeds with NO RS challenge or refusal event recorded.
- **Measurement method.** Adversarial test fixtures (need verification — list of bypass-vectors should live in `tests/test_bypass_*.py` if it doesn't already); systematic fuzzing across the bypass-vector taxonomy.
- **Status.** **PARTIAL.** Normalized-command scanner + state-tracker exist; coverage of known bypass shapes verified. Coverage of unknown / future bypass shapes is structurally limited (see Ashby variety-mismatch / FAILURE_MODE 9). The interceptor is escalate-by-default for shapes outside its declared coverage; that is the kernel's response to the variety gap, not a claim of complete coverage.
- **Action on disconfirmation.** When a new bypass surfaces, expand the bypass-vector taxonomy in `system_prompts_leaks` adopt-from-adjacent-ecosystems list (CP-NORM-EXPAND-01, post-soak); patch `core/hooks/_normalized_command_scanner.py`; add regression test; record the prior-undetected vector as a Phase-12 audit data point.

### A5 · Pillar 3 protocols are context-scoped (only fire on matching context_signature)

- **Claim.** Each synthesized protocol carries a `context_signature` so it only reactivates in matching situations; protocols never fire on non-matching contexts. ([README § Active Guidance](../README.md); [FAILURE_MODES § Knowledge Sanctuaries](./FAILURE_MODES.md))
- **Falsification condition.** Active-guidance surfaces a protocol on an op whose context_signature does NOT match the protocol's declared context_signature (a false-positive surface).
- **Measurement method.** Per-firing log lines with `context_signature_match: bool`; trace inspection on `episteme guide --inject` output. Synthetic test suite where protocol P has signature S1 and ops with signature S2 should NOT surface P.
- **Status.** **PARTIAL.** Schema field exists; comparison logic in `core/hooks/_guidance.py` exists; systematic synthetic test suite verifying "doesn't fire on non-match" is NOT yet built (this is genuinely partial — flagged honestly).
- **Action on disconfirmation.** Audit context_signature comparison logic; tighten matching predicate; this is a CP-ACTIVE-GUIDANCE-RANKING-AUDIT-01-class concern (see `~/episteme-private/docs/cp-v1.1-architectural.md`).

---

## § B · Reasoning Surface contract

### B1 · Surface declaration is precondition for execution

- **Claim.** Knowns / Unknowns / Assumptions / Disconfirmation must be declared *before* the Execute stage opens. The Surface is a feedforward gate, not a retrospective form. ([CONSTITUTION § Principle IV](./CONSTITUTION.md); [FAILURE_MODES § feedforward](./FAILURE_MODES.md))
- **Falsification condition.** A high-impact op proceeds to execution and only THEN is the Surface authored (post-hoc documentation pattern); audit log timestamps show RS write *after* op invocation.
- **Measurement method.** Timestamp comparison on `.episteme/reasoning-surface.json` mtime vs `~/.episteme/state/hooks.log` action-invocation timestamps; Phase 12 audit detection of post-hoc RS authoring patterns.
- **Status.** **RUNNING.** Hooks fire pre-tool-use, so the architecture is structurally feedforward. Operator-side discipline (filling the Surface honestly rather than performatively after the fact) is a separate dimension audited by Phase 12.
- **Action on disconfirmation.** If post-hoc-authoring pattern surfaces in audit, this is a governance event (operator is using the kernel as documentation rather than a gate). Response: hook-strictness recalibration (TTL tightening), or operator re-orientation (the kernel does not save time when used as documentation; it defers cost).

### B2 · Disconfirmation field operationalizes Robust Falsifiability (named-in-advance)

- **Claim.** The Disconfirmation field is committed *before* execution; it is not editable to fit observed outcomes after the fact. The chain catches post-hoc rewrites. ([README § The solution](../README.md); [REASONING_SURFACE.md](./REASONING_SURFACE.md))
- **Falsification condition.** A reasoning surface in the chained record stream contains a disconfirmation that was modified *after* its associated action completed (post-hoc rationalization), and the chain integrity check did NOT detect the modification.
- **Measurement method.** Chain-walk audit comparing chained-record disconfirmation field at write-time vs current state; chain-verify should detect any tampered records.
- **Status.** **PARTIAL.** Hash chain catches edit-after-write; surfaces themselves can be re-authored within a single cycle (operator can iterate on their RS pre-execution). The norm is enforcement at submit-time, not retroactive immutability.
- **Action on disconfirmation.** If post-hoc disconfirmation editing surfaces in audit, propose CP-RS-IMMUTABILITY-AFTER-EXECUTE — supersede-with-history pattern at the surface tier, not just the protocol tier. Cross-references CP-TEMPORAL-INTEGRITY-EXPANSION-01 (`~/episteme-private/docs/cp-v1.1-architectural.md`).

---

## § C · Failure-mode counters

### C1 · The 11 named failure modes cover the dominant cognitive failures of fluent reasoners

- **Claim.** The taxonomy in `FAILURE_MODES.md` (6 Kahneman-derived modes + 3 governance-layer modes + 2 v1.0 RC additions = 11 modes) is sufficient to classify the dominant confident-wrongness shapes encountered in real operator usage. ([FAILURE_MODES.md](./FAILURE_MODES.md))
- **Falsification condition.** A confident-wrongness episode in real operator usage maps cleanly to NONE of the 11 modes, *or* maps to one only with significant violence to the taxonomy's vocabulary.
- **Measurement method.** Retrospective review of episodic records and post-incident reports. Scan for episodes where the kernel's classification fails or requires "other" as a fallback at non-trivial frequency (>10% of incidents).
- **Status.** **PARTIAL.** Phase 2 triage (Event 47) classified 1,294 deferred-discovery records to flaw_classification distribution that maps reasonably to the 11 modes. Note: see [FAILURE_MODES § Two-vocabulary distinction](./FAILURE_MODES.md#two-vocabulary-distinction--failure_modes-vs-flaw_classification) — `flaw_classification` and `FAILURE_MODES` are *orthogonal* axes; reasoning failures (FAILURE_MODES) and artifact-state flaws (flaw_classification) load on different dimensions. Gate 27 historical reclassification is the load-bearing precedent for this triage discipline.
- **Action on disconfirmation.** If a class of confident-wrongness emerges that doesn't map, propose new FAILURE_MODE entry. Adding a mode is a governance event (kernel/CONSTITUTION-class change), not an implementation tweak — it requires Evolution Contract gate (propose → critique → gate → promote).

### C2 · Counter artifacts fire feedforward, not feedback

- **Claim.** Each counter fires *before* execution begins; the kernel is feedforward control, not feedback control. ([CONSTITUTION § Principle IV](./CONSTITUTION.md); [FAILURE_MODES § feedforward](./FAILURE_MODES.md))
- **Falsification condition.** A counter artifact (e.g., the Disconfirmation field) is filled out AFTER the action it was supposed to gate, and the chain shows no pre-action declaration.
- **Measurement method.** Same as B1 — timestamp comparison, Phase 12 detection.
- **Status.** **RUNNING.** Architecturally feedforward by hook ordering (PreToolUse). Operator-discipline dimension audited via Phase 12.
- **Action on disconfirmation.** Same as B1 — governance event response.

---

## § D · Operator-modeling

### D1 · Operator profile axes are control signals

- **Claim.** Profile axes (`risk_tolerance`, `testing_rigor`, `asymmetry_posture`, etc.) are not decorative — they are control signals that modulate enforcement thresholds and hook behavior. Changing an axis value changes derived knobs and therefore changes kernel behavior. ([README § Why this architecture](../README.md); [OPERATOR_PROFILE_SCHEMA.md](./OPERATOR_PROFILE_SCHEMA.md))
- **Falsification condition.** A profile axis's `value` field is changed (e.g., `risk_tolerance: low → high`); ZERO derived knobs change in response; ZERO hook behavior changes; ZERO enforcement thresholds change.
- **Measurement method.** Targeted test: snapshot derived-knob outputs in `core/hooks/_derived_knobs.py`, change axis value, re-snapshot, diff. Adversarial property test: any axis whose change produces no downstream diff is structurally orphan.
- **Status.** **PARTIAL.** Pre-Phase-A audit (2026-04-22) found 5 of 7 orphan derived knobs (only 2 of 7 consumed by hooks). Phase A + Phase A2 closed some (`noise_watch_set`, `preferred_lens_order`, `explanation_form` wired). Post-soak audit must re-verify which axes are now load-bearing vs which remain orphan; the 7-axis enumeration may have grown since.
- **Action on disconfirmation.** For each orphan axis: either wire it into a derived knob + hook consumer (Phase B-class work), OR demote the axis from "control signal" to "documentation" in OPERATOR_PROFILE_SCHEMA.md (and update README claim language). Cross-references CP-OPERATOR-COGNITIVE-BUDGET-01.

### D2 · Phase 12 audit detects measure-target drift on profile axes

- **Claim.** When an axis's claimed value diverges from the operator's observed behavior across episodic records, Phase 12 audit flags the axis for re-elicitation. The profile is a hypothesis, not a frozen self-portrait. ([CONSTITUTION § not a frozen measurement](./CONSTITUTION.md); [FAILURE_MODES § measure-as-target drift](./FAILURE_MODES.md))
- **Falsification condition.** An axis with claimed value X but observed behavior consistent with Y across N≥10 episodic records is NOT flagged for re-elicitation in any audit cycle within 30 days.
- **Measurement method.** Phase 12 audit runs (`episteme profile audit --write`); inspection of `~/.episteme/memory/reflective/profile_audit.jsonl`; spot-check for drift flags on axes with known divergence.
- **Status.** **RUNNING.** Phase 12 detected `asymmetry_posture` drift on 2026-04-23 (Event 48; Gate 25 PASS). Concrete falsification-survival evidence — the audit fired exactly when the kernel claimed it should.
- **Action on disconfirmation.** If audit silently accepts drift, calibrate the threshold in `_profile_audit.py`; CP-PHASE12-class refinement; potentially adjust the metric (stop-condition rate, rollback-mention rate, etc.) to be more sensitive.

---

## § E · Active guidance

### E1 · Synthesized protocols accumulate context-fit know-how durable across sessions

- **Claim.** Pillar 3 synthesis turns every resolved blueprint firing into a reusable, context-scoped protocol. The framework compounds: the agent gets sharper on a codebase every time it resolves a conflict. ([README § Protocol Synthesis](../README.md))
- **Falsification condition.** After 30 days of normal kernel use on an active project, ANY of the following: (a) `~/.episteme/framework/protocols.jsonl` contains < 3 protocols total; (b) protocols exist but their context_signatures are empty / single-token / unworkable for matching; (c) protocols never fire on subsequent matching contexts (zero `guidance_bind_rate`).
- **Measurement method.** 30-day window measurement: protocol count + per-protocol fire-count + context-signature entropy; tracked via `episteme guide --inject` traces and protocol-stream audits.
- **Status.** **SCHEDULED.** v1.0 RC verification gate proposed this as a 30-day measure (Gate 22 + 26 in `~/episteme-private/docs/POST_SOAK_TRIAGE.md`). At Day-2 baseline, 0 protocols had been synthesized — that was a known measurement-pipeline gap (Events 36-38 fixed it). Post-soak Day-7+ measurement gives the first real datapoint.
- **Action on disconfirmation.** Audit the synthesis emit path in `core/hooks/_fence_synthesis.py` + the trigger conditions; redesign the Pillar 3 invocation logic; if criterion (a) fails, the "active guidance" claim is currently aspirational rather than operational and the kernel must say so in README. Cross-references CP-FENCE-02 (Event 50) which closed the immediate emit-path bug.

### E2 · Protocol synthesis improves operator decision quality

- **Claim.** The kernel's value is not just auditability — it produces measurably better operator decisions in the contexts it covers, vs the same operator without the kernel. ([README § Protocol Synthesis](../README.md); implicit in the kernel's positioning)
- **Falsification condition.** A retrospective post-incident review across N≥10 incidents finds that operator decision quality was NOT measurably better when relevant synthesized protocols were available, vs comparator incidents where similar context arose but no protocol existed.
- **Measurement method.** Designed retrospective study with operator self-rating + (where available) outcome-quality measure; comparator: matched-context episodes pre- and post-synthesis. Requires episodic-outcome capture (CP-EPISODIC-OUTCOME-01, currently in Theme 1 of `~/episteme-private/docs/ROADMAP_POST_V1.md`).
- **Status.** **ASPIRATIONAL.** No current measurement infrastructure. This is the hardest claim to falsify cleanly because operator decision quality is multidimensional and post-hoc rating has bias. Flagged honestly: this is the load-bearing claim that is least currently testable.
- **Action on disconfirmation.** If the retrospective study finds no quality-delta, the kernel's value-proposition is at risk. Likely reframe: from *"improves decision quality"* to *"improves decision auditability + retrospective debugability"* (a weaker but more honest claim). Cross-references CP-MODEL-PROGRESS-OBSOLESCENCE-01 (the strategic threat-model CP); a value-prop pivot would land here.

---

## § F · Cross-tool / strategic

### F1 · Kernel travels across substrates without modification (BYOS)

- **Claim.** The kernel is pure markdown; it injects into any runtime that accepts system-level context. Adapter layer is pluggable. The framework outlives the tool. ([README § Why this architecture](../README.md); [README § Works with any stack](../README.md))
- **Falsification condition.** Adding a new substrate adapter (Codex, opencode, hermes, or future) requires modifications to `kernel/*.md` content (not just adapter shim code) to function correctly.
- **Measurement method.** Adapter-development experience; new-adapter onboarding cost; `kernel/*` diff before/after adapter addition. The audit is: does the new adapter work with the kernel as-is, or does the kernel need to bend?
- **Status.** **PARTIAL.** Claude Code adapter is the primary; Hermes + opencode + codex have been mentioned but not all are at parity. Need to verify the "modifications-required" claim for each. The kernel-as-markdown discipline is preserved (ZERO code in `kernel/*.md`), but practical adapter-onboarding may surface friction.
- **Action on disconfirmation.** If kernel/* modifications ARE required for new adapters, demote the BYOS thesis from "kernel travels unmodified" to "kernel travels with adapter shims" in README; revise [README § Works with any stack](../README.md) language. Alternatively: refactor the kernel to factor out adapter-specific assumptions, but this is non-trivial and would itself require a CP.

### F2 · Kernel value persists despite model-capability progress

- **Claim.** The kernel's value-proposition is not eroded by improvements in underlying model capability. Confident-wrongness as a failure mode persists at the operator-AI-joint-system level even as model reasoning improves. ([CONSTITUTION § The distinction that matters](./CONSTITUTION.md); implicit in the kernel's strategic positioning)
- **Falsification condition.** A future model (Claude 5+, GPT-6+, or successor) reliably produces context-fit answers without scaffolding at parity with kernel-disciplined operator workflow on a representative benchmark. Specifically: differential demo (`demos/03_differential/`) shows no measurable quality gap between kernel-OFF and kernel-ON conditions.
- **Measurement method.** Periodic comparative benchmark: model-without-kernel vs model-with-kernel on representative ops drawn from operator's actual usage. Cadence: each major model release.
- **Status.** **ASPIRATIONAL.** No benchmark infrastructure for cross-model comparison. The differential demo is the proto-version; needs structured measurement framework to be falsifiability-grade. Cross-references CP-MODEL-PROGRESS-OBSOLESCENCE-01 (strategic threat-model CP, `~/episteme-private/docs/cp-v1.1-architectural.md`).
- **Action on disconfirmation.** If gap closes, the kernel pivots positioning per CP-MODEL-PROGRESS-OBSOLESCENCE-01: from *model-correction* (substrate-facing) to *workflow-discipline* (operator-facing). The discipline value to the OPERATOR persists even if the model-correction value erodes — the operator still benefits from the explicit-thinking gate even when the model itself is more capable.

---

## § G · Reflexive falsifiability — what would falsify this matrix itself

The matrix above is itself a kernel claim ("we have enumerated the load-bearing claims and named falsification conditions"). It must meet its own thesis.

- **Claim.** This file enumerates the load-bearing claims; named falsifications are concrete + observable + actionable.
- **Falsification conditions.**
  1. **Decorative matrix.** After 6 months of kernel use, NO claim in the matrix has had its falsification condition tested in any session — neither RUNNING claims producing fresh evidence, nor PARTIAL claims having their gaps closed, nor ASPIRATIONAL claims being converted to SCHEDULED. The matrix is shelfware.
  2. **Confirmation theater.** Tested falsifications all confirm the claims AND none were "unexpected" — meaning we only tested what we were sure of. The matrix only enumerates safe claims, not real ones.
  3. **Ceremonial action column.** A falsification fires AND no doc revision OR no kernel patch follows. The "action on disconfirmation" column was never load-bearing.
  4. **Coverage gap.** A confident-wrongness episode in operator usage does NOT map to any failure-mode the matrix names a falsifiability test for — meaning the matrix's coverage of the kernel's claim surface is incomplete, and the missing claim is itself unfalsified.
- **Measurement method.** Quarterly review (recommended cadence): walk the matrix; for each row, has the test been run? What was the result? Was the action-on-disconfirmation column's commitment honored when it fired?
- **Status.** **SCHEDULED.** First quarterly review at v1.1 cycle close (~3 months post-v1.0 GA, late 2026 / early 2027).
- **Action on disconfirmation.** If reflexive falsifiability fires on this matrix, treat it as a kernel-credibility regression. Either tighten the matrix (concrete test conditions, real evidence), demote claims that cannot be falsified ("decorative" → "demoted-from-load-bearing"), or expand coverage. The kernel does not get to claim self-applied falsifiability discipline if the discipline is itself unfalsified.

---

## Action-on-disconfirmation policy

When a falsifiability condition fires:

1. **Do not silently revise the claim.** Per Pillar 2 ethos (nothing changes silently), claim revisions are governance events, not edits. Mark the row with the falsification event + date + evidence-ref; preserve the prior claim language under supersede-with-history (cross-references CP-TEMPORAL-INTEGRITY-EXPANSION-01).
2. **Investigate before demoting.** Gate 27's historical reclassification ("decorative taxonomy" → "measurement dimension mismatch") is the load-bearing precedent. A falsification may be a real falsification (claim was wrong), OR it may be a measurement-dimension mismatch (the test was measuring a different dimension than the claim). The kernel should run the investigation before reaching for the demote button.
3. **Demote, don't delete.** A falsified claim becomes a demoted claim (e.g., "load-bearing" → "documentation-only" → "removed at next major version"). Delete-on-falsification is a Doxa-shape — it makes the kernel look like it never claimed the thing.
4. **Update README + CONSTITUTION + REFERENCES** when the falsification meaningfully changes the kernel's value-proposition. Public claims must match operational reality.
5. **Open a CP** when the falsification surfaces a fixable mechanism gap. The CP (in `~/episteme-private/docs/cp-v1.1-architectural.md` or sibling) carries the work; this matrix carries the audit trail.

---

## Cross-references

- [CONSTITUTION.md](./CONSTITUTION.md) — the four principles whose load-bearing claims are tested here.
- [FAILURE_MODES.md](./FAILURE_MODES.md) — the 11-mode taxonomy whose coverage is tested in § C1.
- [REASONING_SURFACE.md](./REASONING_SURFACE.md) — the 5-field protocol whose mechanics are tested in § A2 + § B1 + § B2.
- [REFERENCES.md § Popper](./REFERENCES.md#philosophy-of-science--falsifiability) — the source attribution; this file is the operationalization.
- [KERNEL_LIMITS.md](./KERNEL_LIMITS.md) — declared boundaries; the matrix is bounded by these limits (claims about behavior outside the kernel's declared boundary are not in scope).
- `~/episteme-private/docs/cp-v1.1-architectural.md` — § Section B includes CP-MODEL-PROGRESS-OBSOLESCENCE-01 (the strategic falsification axis cross-referenced in F2) and CP-DESIGN-BEHAVIOR-VERIFICATION-01 (which complements this matrix at the runtime-conformance layer).
- `~/episteme-private/docs/POST_SOAK_TRIAGE.md` — Gate 27 historical reclassification; the load-bearing precedent for the "investigate before demoting" policy.

---

## Maintenance

This file is part of the kernel's self-audit. It is correct when:

- Every load-bearing claim in CONSTITUTION + README + FAILURE_MODES + REFERENCES traces to a row here.
- Every row's falsification condition is concrete enough to be reproducible.
- Every status field is honest (RUNNING / PARTIAL / SCHEDULED / ASPIRATIONAL is named without rounding up).
- Every action-on-disconfirmation column commits to a specific response, not "we'll think about it."
- The reflexive falsifiability section (§ G) is reviewed quarterly + on each major-version cycle close.

Version: v1.0 (Event 73, 2026-04-29). First slice covers the doc + per-claim matrix. Components 3 (`benchmarks/falsifiability/`) and 5 (`episteme falsifiability check` CLI) are deferred — both require this doc as their spec input.

If a reader can identify a load-bearing claim that is *not* in the matrix, the matrix has a coverage gap. Open an issue or PR. The kernel's commitment to its own thesis depends on this file being honestly comprehensive.
