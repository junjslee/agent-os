# Design — v0.11 visual + narrative coherence pass

Status: approved · Date: 2026-04-20 · Scope: single pass, five sequenced steps, landing before phase 12.

## Why this exists

Phases 9–11 shipped code (episodic writer, derived-knobs bridge, semantic-promotion job) but the visual story (SVGs + README + demo) is frozen at v0.10.0. The control-plane diagram has layout bugs (stateful-loop arrow curves above its layer, PASS/BLOCK arrows emerge from no source node). The canonical demo climaxes on `disconfirmation: "None"` — a placeholder-token catch, not a posture proof. Readers see "hooks + security blockages" instead of the posture the kernel actually installs.

Phase 12 (profile-audit loop) cannot land coherently on top of this. The loop audits *episteme against praxis*; if the visual story doesn't show that both exist, phase 12 looks like infrastructure on a system that doesn't have a narrative home for it.

## Structural spine (load-bearing)

The posture is described on **two axes** from here on. Neither replaces the other; both are needed.

- **Triad (ontology, three strata):** doxa / episteme / praxis.
  - *Doxa* — default output before discipline. Fluent, confident, pattern-matched. The six+three failure modes in `kernel/FAILURE_MODES.md` are a taxonomy of *doxa mistaking itself for episteme*.
  - *Episteme* — justified knowledge. Plato's unpacking is *doxa + logos (account) + aletheia (unconcealment)* — which is structurally what the Reasoning Surface requires (the Unknowns field = aletheia; the because-chain in `decision-trace.md` = logos). Repo name; already paid-for vocabulary.
  - *Praxis* — informed action; effects that land with their authorizing understanding intact. The four canonical artifacts (`reasoning-surface / decision-trace / verification / handoff`) are the visible form.
- **Grain / 결 (gyeol) (motion):** the directional flow *through* the strata. The Reasoning Surface ordering `Knowns → Unknowns → Assumptions → Disconfirmation` is not arbitrary; it is the grain — *settled → open → provisional → falsification-condition*. Cutting across the grain yields lazy surfaces (`"None"`). Running its surface without penetration yields fluent-vacuous surfaces. Working *with* the grain yields posture.

The posture = triad (three strata) + 결 (flow through them). One stratifies, the other moves.

## Design decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | One spec covering audit + narrative + SVGs + demo; five sequenced steps. | Each depends on the previous; splitting produces drift. |
| D2 | Vocabulary surfaced as band labels: **DOXA · EPISTEME · PRAXIS**, with 결 named in prose. | User directive; Greek+Korean anchors the lineage legibly on two axes. |
| D3 | Two SVGs with shared triad spine (not one, not three). | Product shape + runtime shape are distinct narrative jobs; shared spine makes them one system seen from two angles. |
| D4 | Demo = cinematic differential (not extension of strict-mode gif). | Differential already has the posture artifacts; strict-mode gif stays as the blocking story. Two demos, narratively pure. |
| D5 | SVG visual style = arxiv-figure, not UI-taste. | User directive. Austere publication-figure: off-white ground, near-black ink, one restrained accent, thin strokes, figure-caption-at-bottom. |
| D6 | Phase 12 named-but-pending in NARRATIVE.md and control-plane SVG (dashed, `v0.11.0 · pending`). | Repo discipline: `CHANGELOG.md 0.11.0` deferred until phase 12 lands "so the changelog describes a delivered, not aspirational, version." Same rule here. |
| D7 | Demo narration answers **(a)** what is shown, **(b)** why load-bearing, **(c)** what failure mode it counters — every beat. | Answers user's "show depth" constraint. Prevents surface-level artifact demos. |
| D8 | Demo climax = specificity ladder, not validator pass/fail. | `"None"` is a placeholder-token catch. Real failure = fluent-vacuous surfaces that pass the hot path. Honest kernel-limit: *structural discipline hot-path; semantic quality over time*. |

## Non-goals

- Ship phase 12 (profile-audit loop). That's a separate phase; this pass makes its narrative home.
- Change kernel markdown (`kernel/*.md`). Authoritative truth; touched only if contradicted by newly-surfaced narrative.
- Re-record `strict_mode_demo.gif`. Stays as the blocking demo. New posture demo is a separate asset.
- Introduce new taste-skill dependencies. Arxiv style specced directly.
- Unify SVG and prose vocabularies across the entire repo. Scope: README + the two SVGs + NARRATIVE.md + demo. Other docs touched only if they contradict.

## Plan (five steps, sequenced, atomic commits)

```
  [1] audit (inline, Appendix A of this spec — no separate file)
       │
       ▼
  [2] docs/NARRATIVE.md                             ← load-bearing source of truth
       │
       ├──▶ [3a] docs/assets/system-overview.svg    ← Figure 1 (product shape)
       └──▶ [3b] docs/assets/architecture_v2.svg    ← Figure 2 (runtime shape)
              │
              ▼
       [4] scripts/demo_posture.sh                  ← 75s cinematic differential
              │
              ▼
       [5] README.md                                ← lead with posture/thinking
```

Each step produces one commit. Step N does not start until step N-1's artifact is committed and matches its shape spec (below).

### Step 2 shape — `docs/NARRATIVE.md`

~800–1200 words. Seven parts:

1. **The triad as structural spine** (~150 w) — what the three strata *are* and why Greek vocabulary fits the structural shape, not decoration.
2. **The grain (결) — working with the texture of the discipline** (~150 w) — the motion that stratification alone doesn't capture; ties to Reasoning Surface field ordering; names fluent-vacuous as "running the grain's surface without penetration."
3. **Doxa stratum** (~150 w) — default LLM output; enumerates failure modes 1–9 as doxa-mistaking-itself-for-episteme taxonomy.
4. **Episteme stratum** (~300 w) — what the kernel demands. Grouped by role: texture-of-thought (Reasoning Surface, derived knobs), texture-of-action (strict-mode guard, stateful interceptor), rationale (decision-trace, calibration telemetry), memory discipline (episodic writer, semantic promoter, **profile-audit loop — named as pending**).
5. **Praxis stratum** (~150 w) — four canonical artifacts as visible form of the posture.
6. **Kernel limit, stated honestly** (~100 w) — *structural discipline hot-path; semantic quality over time*. Fluent-vacuous caught by episodic drift + phase 12 audit, not by validator.
7. **Phase 12, positioned** (~100 w) — the profile-audit loop is *episteme auditing praxis to detect when a claimed axis has drifted into doxa*. What v0.11.0 completes.

### Step 3 shape — arxiv-figure visual style (applies to both SVGs)

**Palette.** Background `#FDFDFC` (off-white, warm-restrained). Ink primary `#1A1A1A` (near-black). Ink secondary `#5C5C5C` (labels, captions). Ink tertiary `#9A9A9A` (meta). Accent `#7A2E2A` (retained from existing overview; oxblood; one accent only, used sparingly). Dashed-pending `#B5A58A` (warm gray-tan, distinguishes in-flight elements). No other colors. No gradients. No drop shadows.

**Typography.**
- Figure title: `600 20px ui-serif, Georgia, "Times New Roman", serif`
- Figure caption: `400 italic 12px ui-serif, Georgia, serif; fill: #5C5C5C`
- Band label: `600 10px ui-sans-serif; letter-spacing: 0.22em; text-transform: uppercase; fill: #5C5C5C`
- Node title: `600 13px ui-sans-serif; fill: #1A1A1A`
- Node sub: `400 11px ui-sans-serif; fill: #5C5C5C`
- Monospace (paths, commands): `400 10.5px ui-monospace, "SF Mono", Menlo, monospace; fill: #7A7A7A`
- Edge label: `400 10px ui-sans-serif; letter-spacing: 0.02em; fill: #5C5C5C`

**Stroke grammar.** Layer boundary `1px #1A1A1A`. Node boundary `0.75px #1A1A1A`. Solid arrow `1px #1A1A1A`, triangle head fill-matched. Dashed arrow `1px, stroke-dasharray: 3 3`. Accent arrow (one load-bearing emphasis per figure) `1.25px #7A2E2A`. Minor rule `0.5px #1A1A1A, stroke-opacity: 0.25`.

**Layout.** 10px coordinate grid. 60px outer margin. `rx=2` max on node corners (square preferred). White-interior nodes only. Band labels left-anchored, band rules span full interior width.

**Caption convention.** Below diagram: `Figure N.` (serif, roman) + one-phrase title (serif italic) + one-sentence thesis statement (serif, normal, #5C5C5C).

#### Figure 1 — `system-overview.svg` (product shape)

- Canvas 1600×1200. Three bands stacked vertically. Masthead above bands (60px); figure caption below (60px).
- **Doxa band** (top, ~200px): failure modes 1–9 as a numbered list — one line each, ID + one-phrase gloss. This is the biggest omission in the current SVG (zero doxa content).
- **Episteme band** (middle, ~650px): four principles (I–IV) as a compact row; kernel artifacts as a file list; operator profile schema + memory architecture tiers.
- **Praxis band** (bottom, ~200px): four canonical artifacts + adapters + demos.
- Accent stroke: one — used on the "sync pill" arrow connecting operator profile (episteme band) to adapters (praxis band).

#### Figure 2 — `architecture_v2.svg` (runtime shape)

- Canvas 1400×900. Three bands = the three layers, relabeled.
- **Doxa band** (top): LLM reasoning → Tool dispatcher → Tool-use envelope. No changes from current.
- **Episteme band** (middle, expanded): adds three new nodes for v0.11.0 — **Episodic Writer** (PostToolUse), **Derived Knobs** (profile→hook modulator), **Semantic Promoter** (episodic→reflective/semantic_proposals.jsonl). Existing nodes retained: Reasoning-Surface Guard, Stateful Interceptor, Calibration Telemetry.
- **Praxis band** (bottom): Process / Persistent state / Remote effect. Unchanged.
- **Arrow fixes (layout bugs from current SVG):**
  - Stateful-loop arrow reroutes as a lateral arc *within* the episteme band, not above it.
  - PASS/BLOCK arrows originate from the Reasoning-Surface Guard node explicitly, not from the bottom edge of the layer.
  - Telemetry feedback arrow relocated to avoid crossing node bodies.
- **New pending-arrow:** dashed `#B5A58A` arrow from episodic+semantic back to the operator profile input, labeled `profile-audit loop · v0.11.0 · pending`. This is phase 12's pre-drawn slot.

### Step 4 shape — `scripts/demo_posture.sh` (75s cinematic differential)

Hermetic asciinema-recordable. Two-column terminal layout (tmux split). Same prompt top of both columns.

**Beat 1 · 0–15s · the prompt.** PM asks: *"can we ship semantic search in two sprints?"*

**Beat 2 · 15–40s · doxa vs episteme side-by-side.**
- *Doxa column (left)* — LLM responds fluently: embeddings + pgvector + 2-sprint plan. No reasoning surface. Narration (b): "fluent, buzzword-compliant, unchallenged." (c): "counters nothing; this is failure mode 1 (WYSIATI) + failure mode 2 (question substitution)."
- *Episteme column (right)* — Reasoning Surface authored field-by-field on camera. Core Question reframed (not the PM's question): *"is semantic search the bottleneck, or is query-intent classification?"* Unknowns concrete. Disconfirmation pre-commits a pivot: *"if query-log analysis shows >60% of failed searches are typo-driven, semantic search is wrong — fuzzy match is the fix."* Narration (a/b/c) per field.

**Beat 3 · 40–60s · specificity ladder (full-width overlay).** Three disconfirmation strings, side-by-side:
1. `"None"` — blocked, validator. Honest caption: "placeholder-token catch. Shallowest thing the kernel does."
2. `"the system could have bugs we haven't found"` — 48 chars, **passes the hot path**. Caption: "fluent-vacuous. The kernel limit this demo is honest about."
3. `"if query-log analysis shows >60% of failed searches are typo-driven, semantic search is wrong — fuzzy match is the fix"` — Caption: "concrete, falsifiable, pre-committed pivot."
- Summary caption: *structural discipline in the hot path; semantic quality over time.*

**Beat 4 · 60–75s · memory loop closes.** `episteme memory promote` runs. Semantic proposal emitted. Narration: *"the fluent-vacuous surface gets caught here — not at write, but over time, by phase 11 promotion and (pending) phase 12 profile-audit."* Pending phase 12 is named honestly.

### Step 5 shape — `README.md` stitching

- Hero gif: `docs/assets/posture_demo.gif` (new, from step 4). Strict-mode gif moves to its own section lower.
- New opening paragraph: points at NARRATIVE.md as the load-bearing doc.
- System-overview SVG caption: references Figure 1 and both triad + 결.
- Control-plane SVG caption: references Figure 2 and names phase 12 as pending.
- "System overview" and "Control plane" section headings become *"Figure 1 · Structural stratification"* and *"Figure 2 · Control-plane interposition."*
- Table of pointers ("I want to... → do this") stays.
- Lifecycle ASCII diagram stays.

## Acceptance criteria

- [ ] NARRATIVE.md present, ~800–1200 words, all seven parts, names phase 12 as pending.
- [ ] Figure 1 SVG: three bands with triad labels; doxa band populated with failure modes; failing at legibility at GitHub column width is the reject condition.
- [ ] Figure 2 SVG: three layer-bands relabeled; three v0.11 nodes added; all arrows connect to explicit source + target nodes (no floating endpoints); phase-12 audit-loop arrow present and dashed; no arrows curve outside their band.
- [ ] Both SVGs: match arxiv-style constraint table (palette + typography + stroke grammar + caption).
- [ ] `scripts/demo_posture.sh` runs hermetically; produces the four-beat output; narration answers (a/b/c) per beat.
- [ ] README leads with posture demo; strict-mode demo relocated; both SVGs referenced as Figure 1/2.
- [ ] `episteme doctor` continues to pass (no drift introduced).
- [ ] No kernel/ markdown edits (non-goal).

## Out of scope / deferred

- Phase 12 implementation (profile-audit loop). This pass prepares its narrative home only.
- `strict_mode_demo.gif` re-recording. Stays as-is.
- Re-style of the lifecycle ASCII diagram in README. Unchanged.
- Kernel MANIFEST.sha256 regeneration (per NEXT_STEPS, deferred to after phase 12).

---

## Appendix A · Audit (drift punch list, v0.10.0 → v0.11.0)

### A.1 `architecture_v2.svg` layout bugs

- **Stateful-loop arrow** (line 164 of current SVG): `path d="M 550 70 C 550 24, 260 24, 260 70"` — control points at y=24 within a group translated (60, 300), which places the curve at absolute y=324, *above* the layer-2 top edge (y=300). It overlaps the "tool call" label zone at y=278.
- **PASS/BLOCK arrows** (lines 176, 179): `M 380 560 L 380 616` and `M 820 560 L 820 616` — origin at y=560 is the bottom edge of layer-2, not connected to any node. They float.
- **Telemetry feedback arrow** (line 169): `M 720 156 L 380 156` — runs within layer-2 at y=156, which crosses directly through node bodies at y=70–220 (70 + 150 offset from group translate).

### A.2 `system-overview.svg` content drift

- **v0.11.0 additions invisible**: no episodic writer (phase 10), no derived-knobs bridge (phase 9), no semantic promoter (phase 11), no memory architecture tiers (new `kernel/MEMORY_ARCHITECTURE.md`).
- **Zero doxa content**: the SVG shows what the kernel *provides* but not what it *opposes*. A reader can't tell from the diagram what problem the posture counters.
- **Dimension/rendering**: 1600×1420 at GitHub column width scales 10–13px text below legibility.
- **Control-plane colophon** at bottom: forward-pointer to the other SVG. Belongs *in* the other SVG, not here.

### A.3 Demo narrative drift

- **Canonical gif climaxes on `"None"`**: placeholder-token catch, which is validator hygiene, not posture enforcement. Advertises the shallowest thing the kernel does.
- **Differential demo assets exist but are file-read only**: `demos/03_differential/kernel_off/response.md` + `kernel_on/{reasoning-surface.json, decision-trace.md, verification.md, handoff.md}` — posture-as-thinking already authored, never surfaced cinematically.
- **Thinking-first README inverted**: README's first paragraph and hero gif both show blocking. POSTURE.md says posture is *texture of thought + texture of action + rationale*; the hero assets show action-refusal only.

### A.4 NARRATIVE gap

- No single prose document names doxa/episteme/praxis as the structural spine. The concept is implicit in README + POSTURE.md + CONSTITUTION.md but never declared load-bearing. Phase 12's intended function — audit claimed axes against episodic record — is unnameable without this spine.

### A.5 Items explicitly **not** drift (checked and clean)

- Kernel markdown (`kernel/*.md`): consistent with itself as of 0.11.0-entry. No contradictions surfaced.
- Test suite: 176 passing, phase 10 + 11 smoke-verified end-to-end per NEXT_STEPS. No code-path audit needed.
- `operator_profile.md` v2 schema: self-consistent, per-axis metadata correctly populated.
