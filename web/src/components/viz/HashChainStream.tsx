"use client";

import { motion } from "motion/react";
import { cn, shortHash, formatTime } from "@/lib/utils";
import type { ChainEntry } from "@/lib/types/episteme";

interface HashChainStreamProps {
  entries: ChainEntry[];
  className?: string;
  /** Max entries shown at once; oldest are dropped from view */
  cap?: number;
}

const kindLabel: Record<ChainEntry["kind"], string> = {
  genesis: "GEN",
  surface_sealed: "RS.SEAL",
  protocol_synthesized: "PR.SYN",
  protocol_applied: "PR.APP",
  deferred_discovery: "DD.LOG",
  cascade_detected: "CD.FIRE",
  verification_trace: "VT.PASS",
};

const kindTone: Record<ChainEntry["kind"], string> = {
  genesis: "text-muted",
  surface_sealed: "text-bone",
  protocol_synthesized: "text-verified",
  protocol_applied: "text-ash",
  deferred_discovery: "text-unknown",
  cascade_detected: "text-disconfirm",
  verification_trace: "text-chain",
};

export function HashChainStream({
  entries,
  className,
  cap = 12,
}: HashChainStreamProps) {
  const sorted = [...entries].sort((a, b) => b.seq - a.seq).slice(0, cap);

  return (
    <div
      className={cn(
        "relative flex h-full flex-col panel-gradient",
        className,
      )}
    >
      <header className="flex items-center justify-between border-b border-hairline px-4 py-3">
        <span className="font-mono text-[0.6875rem] uppercase tracking-[0.2em] text-muted">
          hash chain
        </span>
        <span className="font-mono text-[0.6875rem] text-chain">
          seq {sorted[0]?.seq ?? 0}
        </span>
      </header>

      <ol className="flex flex-1 flex-col divide-y divide-hairline overflow-hidden">
        {sorted.map((e, i) => {
          const isHead = i === 0;
          const broken = e.tamper_suspected === true;
          return (
            <motion.li
              key={e.seq}
              layout
              initial={isHead ? { opacity: 0, y: -6 } : false}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.24, ease: [0, 0, 0.2, 1] }}
              className={cn(
                "relative flex flex-col gap-1 px-4 py-2.5 transition-colors",
                isHead && "flash-chain",
                broken && "flash-break",
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={cn(
                      "font-mono text-[0.6875rem] uppercase tracking-wide",
                      kindTone[e.kind],
                    )}
                  >
                    {kindLabel[e.kind]}
                  </span>
                  <span className="font-mono text-[0.6875rem] text-muted">
                    {e.seq.toString().padStart(4, "0")}
                  </span>
                </div>
                <span className="font-mono text-[0.625rem] text-muted">
                  {formatTime(e.ts)}
                </span>
              </div>

              <p className="truncate font-mono text-[0.75rem] text-ash">
                {e.label}
              </p>

              <div className="flex items-center gap-2 pt-0.5">
                <span className="font-mono text-[0.625rem] text-muted">
                  {shortHash(e.prev_hash, 6)}
                </span>
                <span className="font-mono text-[0.625rem] text-muted">→</span>
                <span
                  className={cn(
                    "font-mono text-[0.625rem]",
                    broken ? "text-disconfirm" : "text-chain",
                  )}
                >
                  {shortHash(e.this_hash, 6)}
                </span>
                {broken && (
                  <span className="ml-auto font-mono text-[0.625rem] uppercase tracking-wider text-disconfirm">
                    TAMPER
                  </span>
                )}
              </div>
            </motion.li>
          );
        })}
      </ol>

      <footer className="border-t border-hairline px-4 py-2">
        <span className="font-mono text-[0.625rem] text-muted">
          append-only · prev.this_hash → next.prev_hash
        </span>
      </footer>
    </div>
  );
}
