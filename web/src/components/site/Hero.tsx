import Link from "next/link";
import { SignalBadge } from "@/components/ui/SignalBadge";
import { CornerMarkers } from "@/components/ui/CornerMarkers";

const HERO_WORDS = [
  "A",
  "thinking",
  "framework",
  "for",
  "the",
  "agents",
  "you",
  "already",
  "ship.",
];

export function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-hairline">
      <div className="relative mx-auto max-w-7xl px-6 pt-20 pb-16 md:px-12 md:pt-32 md:pb-24">
        <div className="relative panel-gradient">
          <CornerMarkers />

          {/* Inner atmosphere for the hero panel only */}
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 overflow-hidden"
          >
            <div className="absolute left-1/2 top-1/2 h-[70%] w-[60%] -translate-x-1/2 -translate-y-1/2 rounded-full bg-chain/[0.06] blur-[110px]" />
            <div className="absolute right-[-15%] bottom-[-20%] h-[55%] w-[50%] rounded-full bg-disconfirm/[0.04] blur-[100px]" />
          </div>

          <div className="relative flex flex-col gap-10 p-8 md:gap-14 md:p-14 lg:p-20">
            <div className="flex flex-wrap items-center gap-3">
              <SignalBadge signal="chain">
                <span className="relative inline-flex size-1.5">
                  <span className="absolute inline-flex h-full w-full rounded-full bg-chain opacity-75 status-pulse" />
                  <span className="relative inline-flex size-1.5 rounded-full bg-chain" />
                </span>
                substrate · v1.0 rc
              </SignalBadge>
              <span className="font-mono text-[0.6875rem] uppercase tracking-[0.12em] text-muted">
                causal-consequence scaffolding & protocol synthesis
              </span>
            </div>

            <h1 className="max-w-5xl font-display text-[2.75rem] leading-[1.05] tracking-tight text-bone md:text-[4.5rem]">
              {HERO_WORDS.map((word, i) => (
                <span key={`${word}-${i}`} className="mask-word mr-[0.22em]">
                  <span
                    className="mask-word-inner"
                    style={{ animationDelay: `${i * 70}ms` }}
                  >
                    {word}
                  </span>
                </span>
              ))}
            </h1>

            <p
              className="max-w-2xl font-sans text-[1.0625rem] leading-relaxed text-ash md:text-[1.1875rem] opacity-0"
              style={{
                animation: "mask-word-rise 900ms var(--ease-enter) 700ms forwards",
              }}
            >
              <span className="text-bone">episteme</span> is a sovereign cognitive kernel that
              extracts context-fit protocols from conflicting information, records every
              decision on a tamper-evident hash chain, and actively guides execution when
              the reasoning surface goes thin.
            </p>

            <div
              className="flex flex-wrap items-center gap-4 opacity-0"
              style={{
                animation: "mask-word-rise 900ms var(--ease-enter) 900ms forwards",
              }}
            >
              <Link
                href="#framework"
                className="group inline-flex items-center gap-2 border border-line bg-surface px-5 py-3 font-mono text-[0.8125rem] uppercase tracking-[0.12em] text-bone transition-colors hover:border-chain hover:text-chain"
              >
                see the framework
                <span
                  aria-hidden
                  className="transition-transform group-hover:translate-x-0.5"
                >
                  →
                </span>
              </Link>
              <Link
                href="https://github.com/junjslee/episteme"
                target="_blank"
                rel="noopener"
                className="inline-flex items-center gap-2 border border-hairline px-5 py-3 font-mono text-[0.8125rem] uppercase tracking-[0.12em] text-ash transition-colors hover:border-line hover:text-bone"
              >
                read the kernel
              </Link>
            </div>

            <div
              className="mt-4 grid grid-cols-2 gap-6 border-t border-hairline/70 pt-8 md:grid-cols-4 opacity-0"
              style={{
                animation: "mask-word-rise 900ms var(--ease-enter) 1100ms forwards",
              }}
            >
              {[
                { k: "pillars", v: "03" },
                { k: "blueprints", v: "04" },
                { k: "tests green", v: "565 / 565" },
                { k: "protocols synthesized", v: "live" },
              ].map((m) => (
                <div key={m.k} className="flex flex-col gap-1">
                  <span className="font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-muted">
                    {m.k}
                  </span>
                  <span className="font-display text-[1.75rem] leading-none text-bone">
                    {m.v}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
