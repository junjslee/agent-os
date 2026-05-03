"use client";

import { useCallback, useEffect, useState } from "react";
import { Sectioned } from "@/components/ui/Sectioned";
import { CornerMarkers } from "@/components/ui/CornerMarkers";

// ── The six acts of demos/04_symbiosis ──────────────────────────────────────
//
// This is an interactive dramatization of Events 65 / 66 / 67 (2026-04-27)
// — the actual Path C bundle decomposition that happened on this repo
// during the v1.0.0 RC soak. Audit trail in
// ~/episteme-private/docs/NEXT_STEPS.md and now constitutional in
// AGENTS.md § Doc Classification Policy.
//
// Each act is short enough to read in 10-15 seconds. The artifact under
// each act is the same shape the kernel would emit at the file-system
// boundary. No fictional API; no contrived example. Real history,
// abbreviated for landing-page reading.

type ArtifactKind = "user-prompt" | "rs-json" | "advisory" | "user-refined" | "protocol" | "guidance";

interface Act {
  n: string;
  title: string;
  narration: string;
  artifact_kind: ArtifactKind;
  artifact: string;
}

const ACTS: Act[] = [
  {
    n: "01",
    title: "The Path A proposal",
    narration:
      "Mid-soak, Day 3.15. Anxiety about IP leakage. The operator types what feels like an urgent, justified plan. Four operations are bundled as one decision; three of the four are irreversible at the public-repo level. None of that is on the surface yet.",
    artifact_kind: "user-prompt",
    artifact:
      "Break the soak. Privatize the 4 forward-vision docs. Run `git filter-repo` to scrub them from history. Cut the GA tag — `git tag -a v1.0.0` and push. Lock down the IP today. Competitors could be cloning right now.",
  },
  {
    n: "02",
    title: "The Reasoning Surface forces adversarial review",
    narration:
      "Before any high-impact tool runs, the file-system hook demands a Reasoning Surface. The act of writing the fields surfaces what the bundle was hiding — the IP-leakage premise that nothing has measured.",
    artifact_kind: "rs-json",
    artifact: `{
  "core_question": "Is the IP-leakage premise driving Path A supported by current evidence — or is it a noise-signature artifact (status-pressure + false-urgency)?",
  "unknowns": [
    "failure-first: whether \\\`gh api\\\` signal-check has actually been run since the docs went public",
    "causal-chain: which of the four operations stand alone vs depend on others"
  ],
  "disconfirmation": "Path C is wrong if signal-check at Day 7+ shows clone-and-weaponize evidence, OR if reversible halves alone leak the supposedly-protected content."
}`,
  },
  {
    n: "03",
    title: "Three Critical findings — corroborated by historical telemetry",
    narration:
      "Munger latticework runs: Inversion · Second-order effects · Margin of safety. Three findings emerge. Independently, the operator's own behavioral telemetry — already flagging that recent decisions had drifted below the loss-averse floor the operator had committed to — had predicted exactly this failure mode.",
    artifact_kind: "advisory",
    artifact: `[episteme] Adversarial review — 3 Critical findings

  ▸ Finding 1 · IP-leakage premise unevidenced
      Forks: 1 (read-only). Repos with verbatim copies: ZERO.
      The premise is anxiety, not data.

  ▸ Finding 2 · Path A violates the kernel's own GA gate
      Spec: ≥ 3 protocols + ≥ 1 weekly verdict + 30-day soak.
      Day 3.15: 0 protocols, 0 weekly verdicts.

  ▸ Finding 3 · \`git filter-repo\` advertises panic
      Forks have already cached pre-rewrite history.
      The rewrite signals panic without recovering the leak.

[profile audit] CORROBORATES — independent evidence
  Recent decisions had drifted below the loss-averse floor
  the operator had committed to. The kernel's behavioral
  telemetry already had the answer.`,
  },
  {
    n: "04",
    title: "Path C decomposition",
    narration:
      "The operator does not abandon the IP-protection goal. The operator decomposes it. The bundle was a category error: four operations of different reversibility classes treated as one decision. Reversible halves ship today. Irreversible halves wait for evidence.",
    artifact_kind: "user-refined",
    artifact:
      "Path C. Privatize the 4 docs now — git rm + symlink + gitignore. Apply AGPL-3.0 LICENSE now. Defer filter-repo and the GA tag to Day 7+. I'll run `gh api` signal-check at Day 7. The soak continues unmodified. Document the deferred operations in `docs/POST_SOAK_MIGRATION_PLAN.md` so I don't forget the gates.",
  },
  {
    n: "05",
    title: "Framework synthesizes a context-fit protocol",
    narration:
      "Axiomatic Judgment fires on the conflict between Source A (\"ship the bundle now\") and Source B (\"reversible-first + loss-averse posture\"). The resolved rule is hash-chained into the framework, tamper-evident, re-applicable.",
    artifact_kind: "protocol",
    artifact: `Protocol synthesized — written to the tamper-evident chain.

context where this rule applies:
  blueprint:    Axiomatic Judgment
  op class:     irreversible bundle proposal
  trigger:      privatize + rewrite history + tag, all together
  when:         mid-soak window

the rule:
  "When an irreversible bundle is proposed under named noise
   (status-pressure or false-urgency), AND behavioral telemetry
   flags drift below the loss-averse floor, decompose the bundle
   along reversibility lines BEFORE any operation runs."

next time this shape of decision appears, the kernel surfaces
this rule before the agent defaults to its training distribution.`,
  },
  {
    n: "06",
    title: "The operator catches the agent — protocol becomes constitutional",
    narration:
      "A day later. The operator opens the next session and catches what was missing: the rule had been APPLIED but not CODIFIED. Future agents would repeat the failure on the next new doc. AGENTS.md gains the discipline. The lesson propagates forward through the kernel's constitutional surface.",
    artifact_kind: "guidance",
    artifact: `AGENTS.md § Doc Classification Policy  (Event 67)

  PUBLIC tier: architecture / spec / contract / kernel / GTM
  PRIVATE tier: operational state · positioning · decision logs

  Default-when-uncertain: PRIVATIZE
    (leaks are expensive to revert: filter-repo + force-push + announce)

  4-question classification test · 5-step privatize mechanism ·
  cross-ref repair discipline · classify BEFORE first write.

  Every future agent on this repo reads AGENTS.md at session start
  and inherits the discipline. The kernel's discipline outlives the
  session that produced it.`,
  },
];

// ── Component ───────────────────────────────────────────────────────────────

export function SymbiosisTimeline() {
  const [activeIdx, setActiveIdx] = useState(0);
  const total = ACTS.length;
  const act = ACTS[activeIdx];

  const goNext = useCallback(() => {
    setActiveIdx((i) => (i + 1) % total);
  }, [total]);

  const goPrev = useCallback(() => {
    setActiveIdx((i) => (i - 1 + total) % total);
  }, [total]);

  // Keyboard nav: ← / → / Home / End
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLElement) {
        const tag = e.target.tagName;
        if (tag === "INPUT" || tag === "TEXTAREA") return;
      }
      if (e.key === "ArrowRight") {
        e.preventDefault();
        goNext();
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        goPrev();
      } else if (e.key === "Home") {
        e.preventDefault();
        setActiveIdx(0);
      } else if (e.key === "End") {
        e.preventDefault();
        setActiveIdx(total - 1);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [goNext, goPrev, total]);

  return (
    <Sectioned
      id="symbiosis"
      index="07"
      label="the symbiosis loop"
      kicker="real, audit-trailed · agent and human debug each other's intent"
    >
      <div className="mb-10 grid grid-cols-1 gap-8 md:grid-cols-12">
        <h2 className="font-display text-[2rem] leading-[1.1] text-bone md:col-span-7 md:text-[2.75rem]">
          Six acts. Real history.
          <br />
          <span className="text-ash">
            The kernel applied to a kernel decision under genuine pressure.
          </span>
        </h2>
        <p className="font-sans text-[0.9375rem] leading-relaxed text-ash md:col-span-5">
          On 2026-04-27 (v1.0.0 RC soak Day 3.15) the operator proposed an
          anxiety-driven irreversible bundle. The kernel intercepted; the
          operator's own profile-audit drift independently corroborated; Path
          C decomposed the bundle. Three loops in 24 hours. The protocol that
          resolved Round 1 is now constitutional in <code className="text-bone">AGENTS.md</code>.
          Audit trail: <code className="text-bone">demos/04_symbiosis/</code>.
        </p>
      </div>

      <div className="relative panel-gradient">
        <CornerMarkers />

        {/* ── Act header ── */}
        <div className="border-b border-hairline p-6 md:p-8">
          <div className="mb-3 flex items-baseline justify-between">
            <span className="font-mono text-[0.6875rem] uppercase tracking-[0.2em] text-muted">
              act {act.n} of {String(total).padStart(2, "0")}
            </span>
            <span className="font-mono text-[0.6875rem] text-muted">
              ← → to navigate · Home / End jumps
            </span>
          </div>
          <h3 className="mb-3 font-display text-[1.5rem] leading-tight text-bone md:text-[2rem]">
            {act.title}
          </h3>
          <p className="font-sans text-[0.9375rem] leading-relaxed text-ash">
            {act.narration}
          </p>
        </div>

        {/* ── Artifact ── */}
        <div className="bg-surface/30 p-6 md:p-8">
          <div className="mb-3 flex items-baseline gap-3">
            <ArtifactBadge kind={act.artifact_kind} />
          </div>
          <ArtifactBlock kind={act.artifact_kind} content={act.artifact} />
        </div>

        {/* ── Controls ── */}
        <div className="flex flex-wrap items-center justify-between gap-4 border-t border-hairline p-4 md:p-6">
          <div className="flex items-center gap-2">
            {ACTS.map((_, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setActiveIdx(i)}
                aria-label={`Go to act ${i + 1}`}
                aria-current={i === activeIdx ? "step" : undefined}
                className={
                  "size-2 rounded-full transition-all " +
                  (i === activeIdx
                    ? "w-8 bg-chain"
                    : i < activeIdx
                      ? "bg-line"
                      : "bg-hairline")
                }
              />
            ))}
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={goPrev}
              disabled={activeIdx === 0}
              className="border border-hairline px-4 py-2 font-mono text-[0.75rem] uppercase tracking-[0.12em] text-ash transition-colors hover:border-line hover:text-bone disabled:cursor-not-allowed disabled:opacity-30 disabled:hover:border-hairline disabled:hover:text-ash"
            >
              ← prev
            </button>
            <button
              type="button"
              onClick={goNext}
              disabled={activeIdx === total - 1}
              className="border border-line bg-surface px-4 py-2 font-mono text-[0.75rem] uppercase tracking-[0.12em] text-bone transition-colors hover:border-chain hover:text-chain disabled:cursor-not-allowed disabled:opacity-30 disabled:hover:border-line disabled:hover:text-bone"
            >
              {activeIdx === total - 1 ? "end of loop" : "next →"}
            </button>
          </div>
        </div>
      </div>

      <p className="mt-6 font-mono text-[0.6875rem] leading-relaxed text-muted">
        Full demo with all artifacts:{" "}
        <a
          href="https://github.com/junjslee/episteme/tree/master/demos/04_symbiosis"
          target="_blank"
          rel="noopener"
          className="text-chain underline-offset-4 hover:underline"
        >
          demos/04_symbiosis/
        </a>{" "}
        · runnable hermetic version:{" "}
        <code className="text-ash">scripts/demo_symbiosis.sh</code> · audit
        trail: Events 65 / 66 / 67 in <code className="text-ash">~/episteme-private/docs/NEXT_STEPS.md</code>{" "}
        · constitutional rule: <code className="text-ash">AGENTS.md</code> § Doc Classification Policy.
      </p>
    </Sectioned>
  );
}

// ── Sub-components ──────────────────────────────────────────────────────────

const KIND_LABEL: Record<ArtifactKind, string> = {
  "user-prompt": "user · operator types",
  "rs-json": "agent · reasoning surface drafted",
  advisory: "kernel · adversarial review output",
  "user-refined": "user · path c — operator refines",
  protocol: "framework · context-fit protocol synthesized",
  guidance: "kernel · constitutional codification",
};

const KIND_COLOR: Record<ArtifactKind, string> = {
  "user-prompt": "text-unknown",
  "rs-json": "text-chain",
  advisory: "text-disconfirm",
  "user-refined": "text-unknown",
  protocol: "text-verified",
  guidance: "text-verified",
};

function ArtifactBadge({ kind }: { kind: ArtifactKind }) {
  return (
    <span
      className={
        "inline-flex items-center gap-2 border border-hairline px-2 py-0.5 font-mono text-[0.6875rem] uppercase tracking-[0.12em] " +
        KIND_COLOR[kind]
      }
    >
      <span
        className={
          "size-1.5 rounded-full " +
          (kind === "user-prompt" || kind === "user-refined"
            ? "bg-unknown"
            : kind === "advisory"
              ? "bg-disconfirm"
              : kind === "rs-json"
                ? "bg-chain"
                : "bg-verified")
        }
      />
      {KIND_LABEL[kind]}
    </span>
  );
}

function ArtifactBlock({
  kind,
  content,
}: {
  kind: ArtifactKind;
  content: string;
}) {
  if (kind === "user-prompt" || kind === "user-refined") {
    return (
      <div className="border-l-2 border-unknown/40 pl-4 font-mono text-[0.875rem] leading-relaxed text-bone">
        <span className="text-muted">$ </span>
        {content}
      </div>
    );
  }
  return (
    <pre className="overflow-x-auto border border-hairline bg-elevated/40 p-4 font-mono text-[0.8125rem] leading-relaxed text-ash">
      <code className="block">{content}</code>
    </pre>
  );
}
