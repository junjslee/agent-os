import { Sectioned } from "@/components/ui/Sectioned";

const lines = [
  { t: "prompt", v: "$ episteme guide" },
  { t: "out-header", v: "EPISTEME · active guidance" },
  { t: "out", v: "" },
  { t: "sig", v: "▶ surface: fresh · domain=complicated" },
  { t: "out", v: "" },
  { t: "mut", v: "core question" },
  { t: "out", v: "  Does this migration preserve the CHECK constraint a downstream" },
  { t: "out", v: "  service depends on for exhaustive enum match?" },
  { t: "out", v: "" },
  { t: "warn", v: "▲ unknowns — proceed blocked until cleared:" },
  { t: "out", v: "  1. who reads orders.shipping_status without a default branch?" },
  { t: "out", v: "  2. is the constraint's original purpose recorded anywhere?" },
  { t: "out", v: "  3. what would prove this migration unsafe — pre-committed?" },
  { t: "out", v: "" },
  { t: "ok", v: "✓ disconfirmation declared" },
  { t: "ok", v: "✓ hypothesis stated" },
  { t: "out", v: "" },
  { t: "mut", v: "matching protocols from prior decisions" },
  { t: "out", v: "  · drop-check-without-call-graph-walk → block" },
  { t: "out", v: "  · widen-enum-without-downstream-audit → escalate" },
  { t: "out", v: "  · adding NULL to a constrained column → reconstruct the fence first" },
  { t: "out", v: "" },
  { t: "chain", v: "↳ surface committed · linked to prior decisions" },
];

const toneMap: Record<string, string> = {
  prompt: "text-ash",
  "out-header": "text-bone",
  out: "text-ash",
  sig: "text-chain",
  mut: "text-bone",
  warn: "text-unknown",
  ok: "text-verified",
  chain: "text-chain",
};

export function CodeSample() {
  return (
    <Sectioned
      index="06"
      label="active guidance"
      kicker="the kernel speaks"
    >
      <div className="mb-10 grid grid-cols-1 gap-8 md:grid-cols-12">
        <h2 className="font-display text-[2rem] leading-[1.1] text-bone md:col-span-7 md:text-[2.75rem]">
          <code className="font-display">episteme guide</code>
          <br />
          <span className="text-ash">
            reads your surface and tells you what&apos;s missing.
          </span>
        </h2>
        <p className="font-sans text-[0.9375rem] leading-relaxed text-ash md:col-span-5">
          One CLI. No config. Reads <code className="text-bone">reasoning-surface.json</code>,
          walks the hash chain, surfaces active protocols, and names the
          unknowns that are blocking the next step.
        </p>
      </div>

      <pre className="overflow-x-auto border border-hairline bg-surface/30 p-6 font-mono text-[0.8125rem] leading-relaxed">
        <code className="block">
          {lines.map((l, i) => (
            <div key={i} className={toneMap[l.t] ?? "text-ash"}>
              {l.v || "\u00A0"}
            </div>
          ))}
        </code>
      </pre>
    </Sectioned>
  );
}
