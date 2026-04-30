import { Sectioned } from "@/components/ui/Sectioned";

const pillars = [
  {
    n: "01",
    name: "Cognitive Blueprints",
    promise: "Forcing functions, not policies.",
    body: "Four named blueprints (Fence, Consequence-Chain, Axiomatic Judgment, Architectural-Cascade) intercept writes at the exact point where patterns of confident-wrongness historically emerge. Each blueprint has a validator, a fallback, and a dogfood test — the kernel runs against itself before it runs against you.",
  },
  {
    n: "02",
    name: "Append-Only Hash Chain",
    promise: "Tamper-evident memory, not a log.",
    body: "Every Reasoning Surface seal, protocol synthesis, and deferred discovery writes one line to a SHA-256-linked JSONL chain. A corrupted past is not just noticed — it is unprovable to replay. Session boot walks the chain and fails closed on mismatch.",
  },
  {
    n: "03",
    name: "Framework Synthesis & Active Guidance",
    promise: "Protocols from practice, not from doctrine.",
    body: "The kernel observes decisions, extracts context-fit protocols, and injects them back into the next cycle through session digests and guide CLIs. The framework gets sharper every time you use it — not because you trained it, but because the chain made the lessons auditable.",
  },
];

export function PillarsGrid() {
  return (
    <Sectioned
      id="framework"
      index="01"
      label="three pillars"
      kicker="not a library, a substrate"
    >
      <div className="mb-12 grid grid-cols-1 gap-8 md:grid-cols-12">
        <h2 className="font-display text-[2rem] leading-[1.1] text-bone md:col-span-7 md:text-[2.75rem]">
          The kernel is small on purpose.
          <br />
          <span className="text-ash">
            Three pillars. Everything else is scaffolding.
          </span>
        </h2>
        <p className="font-sans text-[0.9375rem] leading-relaxed text-ash md:col-span-5">
          Agents fail confidently when they confuse fluent pattern-match with
          reasoning. episteme does not block that failure mode — it makes the
          mode structurally unavailable. Pillars below.
        </p>
      </div>

      <ol className="grid grid-cols-1 gap-0 border border-hairline md:grid-cols-3">
        {pillars.map((p, i) => (
          <li
            key={p.n}
            className={
              "flex flex-col gap-5 bg-surface/20 p-6 md:p-8 " +
              (i > 0 ? "border-t border-hairline md:border-l md:border-t-0" : "")
            }
          >
            <header className="flex items-baseline justify-between">
              <span className="font-mono text-[0.6875rem] uppercase tracking-[0.2em] text-muted">
                pillar {p.n}
              </span>
              <span className="font-display text-[2.5rem] leading-none text-whisper">
                {p.n}
              </span>
            </header>
            <h3 className="font-display text-[1.5rem] leading-tight text-bone">
              {p.name}
            </h3>
            <p className="font-mono text-[0.75rem] uppercase tracking-[0.08em] text-chain">
              {p.promise}
            </p>
            <p className="font-sans text-[0.9375rem] leading-relaxed text-ash">
              {p.body}
            </p>
          </li>
        ))}
      </ol>
    </Sectioned>
  );
}
