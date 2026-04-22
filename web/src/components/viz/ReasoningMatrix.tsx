"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { cn } from "@/lib/utils";
import type { ReasoningSurface, Assumption } from "@/lib/types/episteme";

interface ReasoningMatrixProps {
  surface: ReasoningSurface;
  className?: string;
}

type Quadrant = "knowns" | "unknowns" | "assumptions" | "disconfirmation";

const meta: Record<
  Quadrant,
  { title: string; code: string; tone: string; rule: string }
> = {
  knowns: {
    title: "Knowns",
    code: "K",
    tone: "verified",
    rule: "Facts with current evidence. Distinct from inference.",
  },
  unknowns: {
    title: "Unknowns",
    code: "U",
    tone: "unknown",
    rule: "Cannot proceed to execute while this is empty.",
  },
  assumptions: {
    title: "Assumptions",
    code: "A",
    tone: "muted",
    rule: "Stated as assumption, not smuggled as fact.",
  },
  disconfirmation: {
    title: "Disconfirmation",
    code: "D",
    tone: "disconfirm",
    rule: "What evidence would prove this wrong?",
  },
};

function assumptionText(a: Assumption): string {
  return typeof a === "string" ? a : a.claim;
}

function disconfirmationItems(
  d: string | string[],
): string[] {
  if (Array.isArray(d)) return d;
  return d.split(/(?<=[.?!])\s+(?=[A-Z0-9(])/g).filter(Boolean);
}

function Quad({
  q,
  items,
  isOpen,
  onOpen,
  onClose,
}: {
  q: Quadrant;
  items: string[];
  isOpen: boolean;
  onOpen: () => void;
  onClose: () => void;
}) {
  const { title, code, tone, rule } = meta[q];
  const count = items.length;
  const previewCount = 3;
  const preview = items.slice(0, previewCount);
  const hidden = Math.max(0, count - previewCount);

  return (
    <button
      type="button"
      onClick={isOpen ? onClose : onOpen}
      className={cn(
        "group relative flex w-full flex-col items-start gap-4 border p-6 text-left transition-colors",
        "bg-surface/40 hover:bg-surface/70 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-line-strong",
        tone === "verified" && "border-verified/15 hover:border-verified/40",
        tone === "unknown" && "border-unknown/20 hover:border-unknown/50 pulse-unknown",
        tone === "muted" && "border-hairline hover:border-line",
        tone === "disconfirm" && "border-disconfirm/15 hover:border-disconfirm/40",
      )}
    >
      <div className="flex w-full items-baseline justify-between">
        <div className="flex items-baseline gap-3">
          <span
            className={cn(
              "font-mono text-[0.6875rem] uppercase tracking-[0.2em]",
              tone === "verified" && "text-verified",
              tone === "unknown" && "text-unknown",
              tone === "muted" && "text-ash",
              tone === "disconfirm" && "text-disconfirm",
            )}
          >
            {code} / {title}
          </span>
        </div>
        <span
          className={cn(
            "font-display text-[2rem] leading-none",
            tone === "verified" && "text-verified",
            tone === "unknown" && "text-unknown",
            tone === "muted" && "text-bone",
            tone === "disconfirm" && "text-disconfirm",
          )}
        >
          {count.toString().padStart(2, "0")}
        </span>
      </div>

      <p className="font-mono text-[0.6875rem] leading-relaxed tracking-wide text-muted">
        {rule}
      </p>

      <ul className="flex w-full flex-col gap-2 font-mono text-[0.8125rem] leading-snug text-ash">
        {preview.map((item, i) => (
          <li
            key={i}
            className="line-clamp-2 border-l border-hairline pl-3"
            title={item}
          >
            {item}
          </li>
        ))}
        {hidden > 0 && (
          <li className="text-muted">+ {hidden} more</li>
        )}
      </ul>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.24, ease: [0.4, 0, 0.2, 1] }}
            className="w-full overflow-hidden"
          >
            <div className="mt-2 border-t border-hairline pt-4">
              <ul className="flex flex-col gap-2 font-mono text-[0.8125rem] leading-snug text-bone">
                {items.map((item, i) => (
                  <li
                    key={i}
                    className="border-l border-hairline pl-3 text-ash"
                  >
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </button>
  );
}

export function ReasoningMatrix({ surface, className }: ReasoningMatrixProps) {
  const [openQuad, setOpenQuad] = useState<Quadrant | null>(null);

  const data: Record<Quadrant, string[]> = {
    knowns: surface.knowns,
    unknowns: surface.unknowns,
    assumptions: surface.assumptions.map(assumptionText),
    disconfirmation: disconfirmationItems(surface.disconfirmation),
  };

  return (
    <div className={cn("flex flex-col gap-5", className)}>
      <header className="flex items-baseline justify-between border-b border-hairline pb-4">
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-[0.6875rem] uppercase tracking-[0.2em] text-muted">
            reasoning surface
          </span>
          <span className="font-mono text-[0.6875rem] text-muted">
            {surface.schema}
          </span>
        </div>
        <span className="font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-ash">
          domain: {surface.domain}
        </span>
      </header>

      <div className="panel-gradient p-5">
        <p className="font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-muted">
          core question
        </p>
        <p className="mt-2 font-display text-[1.0625rem] leading-relaxed text-bone">
          {surface.core_question}
        </p>
      </div>

      <div className="panel-gradient grid grid-cols-1 gap-0 md:grid-cols-2">
        {(["knowns", "unknowns", "assumptions", "disconfirmation"] as Quadrant[]).map(
          (q, i) => (
            <div
              key={q}
              className={cn(
                "border-hairline",
                i === 0 && "md:border-r md:border-b",
                i === 1 && "border-t md:border-t-0 md:border-b",
                i === 2 && "border-t md:border-r",
                i === 3 && "border-t",
              )}
            >
              <Quad
                q={q}
                items={data[q]}
                isOpen={openQuad === q}
                onOpen={() => setOpenQuad(q)}
                onClose={() => setOpenQuad(null)}
              />
            </div>
          ),
        )}
      </div>

      {surface.hypothesis && (
        <div className="panel-gradient p-5">
          <p className="font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-muted">
            hypothesis · thinking as a bet
          </p>
          <p className="mt-2 font-mono text-[0.875rem] leading-relaxed text-ash">
            {surface.hypothesis}
          </p>
        </div>
      )}
    </div>
  );
}
