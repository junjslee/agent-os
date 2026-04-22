"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { cn, shortHash } from "@/lib/utils";
import type { Protocol } from "@/lib/types/episteme";
import { SignalBadge } from "@/components/ui/SignalBadge";

interface ProtocolNodeProps {
  protocol: Protocol;
  className?: string;
}

export function ProtocolNode({ protocol, className }: ProtocolNodeProps) {
  const [open, setOpen] = useState(false);
  const confPct = Math.round(protocol.confidence * 100);

  return (
    <article
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      className={cn(
        "group relative flex cursor-pointer flex-col gap-4 panel-gradient p-5 transition-[background-image]",
        "hover:[background-image:linear-gradient(color-mix(in_oklab,var(--color-surface)_96%,transparent),color-mix(in_oklab,var(--color-surface)_96%,transparent)),linear-gradient(180deg,rgba(125,224,176,0.35)_0%,rgba(125,224,176,0.05)_100%)]",
        className,
      )}
    >
      <header className="flex items-start justify-between gap-3">
        <div className="flex flex-col gap-1">
          <span className="font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-muted">
            {protocol.id}
          </span>
          <h3 className="font-display text-[1.125rem] leading-tight text-bone">
            {protocol.name}
          </h3>
        </div>
        <SignalBadge signal="verified">
          {confPct.toString().padStart(2, "0")}%
        </SignalBadge>
      </header>

      <p className="font-mono text-[0.8125rem] leading-relaxed text-ash">
        {protocol.summary}
      </p>

      <div className="flex flex-wrap gap-1.5">
        {protocol.triggers.slice(0, 3).map((t) => (
          <span
            key={t}
            className="border border-hairline px-2 py-1 font-mono text-[0.625rem] uppercase tracking-wide text-muted"
          >
            {t}
          </span>
        ))}
      </div>

      <footer className="flex items-center justify-between border-t border-hairline pt-3 font-mono text-[0.6875rem] text-muted">
        <span>invocations · {protocol.invocations}</span>
        {protocol.last_chain_hash && (
          <span className="text-chain">
            ↳ {shortHash(protocol.last_chain_hash, 6)}
          </span>
        )}
      </footer>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 4 }}
            transition={{ duration: 0.18, ease: [0, 0, 0.2, 1] }}
            className="absolute left-full top-0 z-10 ml-3 hidden w-80 border border-line bg-elevated/95 p-5 shadow-2xl backdrop-blur-sm md:block"
          >
            <p className="font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-muted">
              because-chain
            </p>
            <dl className="mt-3 flex flex-col gap-3 font-mono text-[0.75rem] leading-relaxed text-ash">
              <div>
                <dt className="text-muted">observed signal</dt>
                <dd className="text-bone">{protocol.because.observed_signal}</dd>
              </div>
              <div>
                <dt className="text-muted">inferred cause</dt>
                <dd className="text-bone">{protocol.because.inferred_cause}</dd>
              </div>
              <div>
                <dt className="text-muted">decision</dt>
                <dd className="text-bone">{protocol.because.decision}</dd>
              </div>
            </dl>
          </motion.div>
        )}
      </AnimatePresence>
    </article>
  );
}
