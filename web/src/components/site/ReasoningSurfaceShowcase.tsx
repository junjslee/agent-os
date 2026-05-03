"use client";

import { useState } from "react";
import { Sectioned } from "@/components/ui/Sectioned";

// ── Three Reasoning Surfaces — one real, two pattern templates ──────────────
//
// Card 1 happened on this repository on a named date and is audit-trailed.
// Cards 2 and 3 are pattern templates of the failure shapes episteme catches
// in any production codebase — concrete numbers, version strings, named call
// sites, falsifiable Disconfirmations. No fictional API; no contrived metric.
// Each card carries a `provenance.type` so the visitor can read which is which.
//
// Each card carries a naive-vs-structural contrast block: the literal
// instruction-style prompt a developer would type, why that prompt fails as
// cognitive guidance, and what the kernel's blueprint structurally forces in
// its place. The contrast is the load-bearing teaching moment — without it the
// example is indistinguishable from a tone-of-voice prompt.

interface Sample {
  id: string;
  tab: string;
  provenance: { type: "real" | "pattern"; label: string };
  blueprint: string;
  headline: string;
  scenario: string;
  naive: { prompt: string; fails_because: string };
  structural: { forces: string };
  rs: {
    core_question: string;
    key_unknown: string;
    disconfirmation: string;
  };
  outcome: string;
}

const SAMPLES: Sample[] = [
  {
    id: "bundle",
    tab: "Anxiety bundled four ops as one",
    provenance: { type: "real", label: "Event 65 · 2026-04-27 · this repository" },
    blueprint: "Axiomatic Judgment",
    headline:
      "Four operations proposed as one decision — three of them irreversible. The kernel split the bundle before any history was rewritten.",
    scenario:
      "Day 3 of a planned 7-day soak. The operator typed: privatize four forward-vision docs, run `git filter-repo` to scrub them from history, cut the GA tag, end the soak — all today. Three of those operations cannot be undone once they reach a public repo with 18 unique clones in the prior 90 days.",
    naive: {
      prompt:
        "Be thorough — lock down our IP fast. Privatize the docs, rewrite git history, ship GA, end the soak.",
      fails_because:
        "An LLM satisfies ‘be thorough’ by sounding careful. Tone-of-voice instructions are unfalsifiable — the agent passes by writing ‘I have carefully considered…’ and proceeds. The bundle stays one decision. Reversibility class never gets named because the prompt provides no structural reason to name it.",
    },
    structural: {
      forces:
        "In the kernel, thorough means *separately falsifiable*. The Reasoning Surface requires one pre-committed observable per discrete action — the specific event that would prove *that* op wrong, not the bundle as a whole. ‘If issues arise’ is rejected as a placeholder. Four ops cannot share one observable, so the bundle decomposes by force: irreversible ops separate from reversible, each earns its own evidence gate, and the reversible halves ship before the irreversible halves can be authorized.",
    },
    rs: {
      core_question:
        "Is the IP-leakage premise driving the bundle actually evidenced — or is it stress-state pattern-matching to a panic shape?",
      key_unknown:
        "Whether `gh api repos/junjslee/episteme/traffic/clones` has been queried since the four docs went public five days ago. The premise driving urgency is unmeasured.",
      disconfirmation:
        "Decomposition is wrong if Day 7 `gh api` traffic-clones returns ≥ 3 unique cloners within 96h of the doc-publication window, OR if any privatized doc remains reachable via `git reflog` 24h after the symlink swap.",
    },
    outcome:
      "Day 7 signal-check: 0 unique cloners since publication. The two reversible operations (privatize via gitignored symlinks; AGPL-3.0 LICENSE) shipped that day. The two irreversible operations were never run. Avoided a public history rewrite that would have advertised exactly the panic the operator was trying to hide.",
  },
  {
    id: "migration",
    tab: "Vestigial-looking constraint, hidden consumer",
    provenance: { type: "pattern", label: "Pattern · production schema migrations" },
    blueprint: "Fence Reconstruction",
    headline:
      "The CHECK constraint looks vestigial. The migration looks safe. The fulfillment service that depends on the constraint lives in a different repo.",
    scenario:
      "A senior engineer reviews a 14-month-old `CHECK (status IN ('pending','paid','shipped','cancelled'))` on the `orders` table. Product needs three new states for a return-flow feature. The migration’s author left the company. There is no doc explaining which downstream systems read `orders.status`.",
    naive: {
      prompt:
        "Make no mistakes here, this is production. Drop the orders.status CHECK constraint and add the wider one. Be careful not to introduce regressions.",
      fails_because:
        "‘Don’t introduce regressions’ is unfalsifiable as written. The agent passes by tone-matching (‘I have carefully reviewed the migration…’) without surfacing the question that actually determines safety: which production reader of `orders.status` has a switch/match without a default branch and will fault on a state value the constraint historically excluded?",
    },
    structural: {
      forces:
        "Fence Reconstruction blueprint refuses to drop a constraint until five fields are populated — `original_purpose`, `original_author`, `last_validated`, `removal_safety_evidence`, `rollback_path`. `original_purpose: 'unknown'` is a lazy-token rejection, so reconstruction is forced to walk the actual call graph before the migration is allowed to run.",
    },
    rs: {
      core_question:
        "Which production services read `orders.status`, exhaustively match the four legacy values without a fallback branch, and will fault on the new state values the constraint widening admits?",
      key_unknown:
        "Whether `fulfillment-svc` (last touched 14 months ago, off the main team’s radar) reads `orders.status` and exhaustively matches the four legacy states — `grep -rn 'order\\.status' services/fulfillment` not yet run.",
      disconfirmation:
        "Reconstruction passes only if a 30-min staging soak with one synthetic order in each new state shows zero `panic: invalid status transition` log lines across the 7 services that import the orders schema, AND production p99 fulfillment success rate stays ≥ 99.5% over the 15-min post-deploy window.",
    },
    outcome:
      "Reconstruction surfaced an exhaustive match at `fulfillment-svc/dispatcher.go:142`. Migration revised: keep the original CHECK; add the three new states via a separate `order_lifecycle` table referenced by FK; deprecate the CHECK only after `fulfillment-svc` ships its v2 dispatcher. Zero production incidents on rollout.",
  },
  {
    id: "cascade",
    tab: "Two files in the diff, eleven in the blast radius",
    provenance: { type: "pattern", label: "Pattern · major dependency upgrades" },
    blueprint: "Architectural Cascade",
    headline:
      "The PR diff shows two files. The actual blast radius shows eleven, and two of them are config the developer never opened.",
    scenario:
      "A team upgrades `@tanstack/react-query` v3 → v5. The codemod handles the `useQuery` rename. The PR diff looks clean — two files, all green locally. The agent’s instinct: ‘this is just a version bump.’",
    naive: {
      prompt:
        "Bump react-query from v3 to v5. Don’t break anything — make sure the tests pass.",
      fails_because:
        "‘Don’t break anything’ is satisfied locally before the change reaches the surfaces it will actually break. The MSW handlers, the SSR streaming adapter, the deploy-time type augmentation, the public CHANGELOG, and the downstream package consumer all live outside the diff the LLM saw — the prompt provides no structural reason for the agent to enumerate them.",
    },
    structural: {
      forces:
        "Architectural Cascade blueprint refuses to ship until `blast_radius_map[]` lists every affected surface, each with status `needs_update` or `not-applicable` (no `unknown`), AND `sync_plan[]` carries one concrete action per affected surface. A `not-applicable` entry requires a one-line rationale that survives Layer 8 spot-check — empty rationale = cascade-theater verdict.",
    },
    rs: {
      core_question:
        "Which non-source surfaces (CI workflows, MSW handlers, SSR adapter, type augmentation, public CHANGELOG, downstream package consumers) carry assumptions about react-query v3’s API that v5 silently invalidates?",
      key_unknown:
        "Whether `tests/setup/msw-handlers.ts` references the v3 `new QueryClient(positional)` signature that v5 changed to object-arg — `grep -rn 'new QueryClient' tests/` not yet run; expected to surface 4 call sites the codemod did not touch.",
      disconfirmation:
        "Cascade is theater if any `sync_plan[]` entry’s status is `not-applicable` without a rationale naming the specific reason; OR if the post-deploy 7-day soak emits a single `TypeError: Cannot read properties of undefined` originating from a react-query call site; OR if any downstream package consumer reports a build break within 14 days of the npm publish.",
    },
    outcome:
      "Cascade flagged 11 surfaces; 2 (the SSR streaming adapter, the deploy-time type augmentation) were not in the developer’s mental model. `sync_plan[]` ran one PR per surface. Deploy clean. One downstream consumer was contacted via a coordination issue 4 days before publish; their migration shipped in parallel.",
  },
];

// ── Component ───────────────────────────────────────────────────────────────

export function ReasoningSurfaceShowcase() {
  const [activeId, setActiveId] = useState(SAMPLES[0].id);
  const sample = SAMPLES.find((s) => s.id === activeId) ?? SAMPLES[0];

  return (
    <Sectioned
      id="what-it-produces"
      index="01"
      label="what episteme produces"
      kicker="three reasoning surfaces · one real, two pattern · naive prompt vs structural counter, side by side"
    >
      <div className="mb-10 grid grid-cols-1 gap-8 md:grid-cols-12">
        <h2 className="font-display text-[2rem] leading-[1.1] text-bone md:col-span-7 md:text-[2.75rem]">
          ‘Be thorough’ is unfalsifiable.
          <br />
          <span className="text-ash">
            The kernel makes thoroughness measurable.
          </span>
        </h2>
        <p className="font-sans text-[0.9375rem] leading-relaxed text-ash md:col-span-5">
          Tone-of-voice instructions — <em>be thorough</em>, <em>make no mistakes</em>, <em>don&apos;t break anything</em> — pass by sounding careful. The kernel replaces them with a structural test: each action must commit, in advance, to the specific observable that would prove it wrong. Four operations need four observables; one observable for four ops fails the contract before any of them runs.
        </p>
      </div>

      {/* ── Tabs ── */}
      <div className="mb-6 grid grid-cols-1 gap-2 md:grid-cols-3">
        {SAMPLES.map((s) => (
          <button
            key={s.id}
            type="button"
            onClick={() => setActiveId(s.id)}
            aria-pressed={s.id === activeId}
            className={
              "border px-5 py-4 text-left transition-colors " +
              (s.id === activeId
                ? "border-line bg-elevated/60"
                : "border-hairline bg-surface/30 hover:border-line/60 hover:bg-surface/50")
            }
          >
            <div
              className={
                "mb-1 flex items-center gap-2 font-mono text-[0.6875rem] uppercase tracking-[0.16em] " +
                (s.id === activeId ? "text-chain" : "text-muted")
              }
            >
              <span
                className={
                  "inline-block size-1.5 rounded-full " +
                  (s.provenance.type === "real" ? "bg-verified" : "bg-chain/70")
                }
                aria-hidden
              />
              {s.provenance.type === "real" ? "real · audited" : "pattern · template"}
            </div>
            <div
              className={
                "font-sans text-[0.9375rem] leading-snug " +
                (s.id === activeId ? "text-bone" : "text-ash")
              }
            >
              {s.tab}
            </div>
          </button>
        ))}
      </div>

      {/* ── Sample card ── */}
      <article className="border border-hairline bg-elevated/40">
        <div className="border-b border-hairline p-6 md:p-10">
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <span
              className={
                "inline-flex items-center gap-2 border px-2 py-0.5 font-mono text-[0.6875rem] uppercase tracking-[0.12em] " +
                (sample.provenance.type === "real"
                  ? "border-verified/40 text-verified"
                  : "border-chain/40 text-chain")
              }
            >
              <span
                className={
                  "size-1.5 rounded-full " +
                  (sample.provenance.type === "real" ? "bg-verified" : "bg-chain/70")
                }
              />
              {sample.provenance.label}
            </span>
            <span className="font-mono text-[0.6875rem] uppercase tracking-[0.12em] text-muted">
              blueprint · {sample.blueprint}
            </span>
          </div>
          <h3 className="font-display text-[1.375rem] leading-tight text-bone md:text-[1.75rem]">
            {sample.headline}
          </h3>
          <p className="mt-4 font-sans text-[0.9375rem] leading-relaxed text-ash">
            {sample.scenario}
          </p>
        </div>

        {/* ── Naive vs Structural contrast block ── */}
        <div className="grid grid-cols-1 divide-y divide-hairline md:grid-cols-2 md:divide-x md:divide-y-0">
          <div className="p-6 md:p-10">
            <div className="mb-3 flex items-center gap-2 font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-disconfirm">
              <span aria-hidden>×</span>
              naive prompt · gameable
            </div>
            <blockquote className="border-l-2 border-disconfirm/50 pl-4 font-sans text-[0.9375rem] italic leading-relaxed text-bone">
              “{sample.naive.prompt}”
            </blockquote>
            <p className="mt-4 font-sans text-[0.875rem] leading-relaxed text-ash">
              <span className="font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-muted">
                why it fails ·{" "}
              </span>
              {sample.naive.fails_because}
            </p>
          </div>
          <div className="bg-surface/20 p-6 md:p-10">
            <div className="mb-3 flex items-center gap-2 font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-verified">
              <span aria-hidden>✓</span>
              structural counter · {sample.blueprint}
            </div>
            <p className="font-sans text-[0.9375rem] leading-relaxed text-bone">
              {sample.structural.forces}
            </p>
          </div>
        </div>

        {/* ── Reasoning Surface produced ── */}
        <div className="border-t border-hairline">
          <div className="px-6 pb-2 pt-6 font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-muted md:px-10 md:pt-8">
            the reasoning surface that resulted (committed to disk before the op ran)
          </div>
          <div className="divide-y divide-hairline">
            <Field label="Core question" value={sample.rs.core_question} />
            <Field label="Key unknown" value={sample.rs.key_unknown} />
            <Field
              label="Disconfirmation pre-commit"
              value={sample.rs.disconfirmation}
            />
          </div>
        </div>

        <div className="border-t border-hairline bg-surface/30 p-6 md:p-10">
          <div className="mb-2 font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-muted">
            What happened next
          </div>
          <p className="font-sans text-[0.9375rem] leading-relaxed text-bone">
            {sample.outcome}
          </p>
        </div>
      </article>

      <p className="mt-6 font-sans text-[0.875rem] leading-relaxed text-ash">
        Card 1 happened on this repository on a named date — audit-trailed in
        the project&apos;s operational log, hash-chained to the framework
        synthesizing protocols. Cards 2 and 3 are pattern templates of failure
        shapes the kernel catches in any codebase: real version strings, named
        call sites, falsifiable thresholds. The structural counter in each card
        requires evidence the naive prompt cannot produce — that is the
        difference between a tone-of-voice instruction and a kernel that
        refuses to proceed.
      </p>
    </Sectioned>
  );
}

// ── Sub-components ──────────────────────────────────────────────────────────

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid grid-cols-1 gap-2 p-6 md:grid-cols-12 md:gap-8 md:p-10">
      <div className="md:col-span-3">
        <div className="font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-muted">
          {label}
        </div>
      </div>
      <p className="font-sans text-[0.9375rem] leading-relaxed text-bone md:col-span-9">
        {value}
      </p>
    </div>
  );
}
