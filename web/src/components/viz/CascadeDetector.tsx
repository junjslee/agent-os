import { cn } from "@/lib/utils";
import { CornerMarkers } from "@/components/ui/CornerMarkers";
import type { CascadeSignal } from "@/lib/types/episteme";

interface CascadeDetectorProps {
  signals: CascadeSignal[];
  className?: string;
}

const stateStyles: Record<CascadeSignal["state"], string> = {
  dormant: "bg-verified/15 border-verified/30 text-verified",
  armed: "bg-unknown/20 border-unknown/40 text-unknown",
  firing: "bg-disconfirm/25 border-disconfirm/50 text-disconfirm",
};

export function CascadeDetector({ signals, className }: CascadeDetectorProps) {
  return (
    <div className={cn("relative panel-gradient", className)}>
      <CornerMarkers topOnly />
      <header className="flex items-center justify-between border-b border-hairline px-4 py-3">
        <span className="font-mono text-[0.6875rem] uppercase tracking-[0.2em] text-muted">
          blueprint d · cascade detector
        </span>
        <span className="font-mono text-[0.6875rem] text-muted">
          four triggers
        </span>
      </header>
      <ol className="grid grid-cols-1 md:grid-cols-4">
        {signals.map((s, i) => (
          <li
            key={s.trigger_id}
            className={cn(
              "relative flex flex-col gap-3 border-hairline p-5",
              i > 0 && "border-t md:border-t-0 md:border-l",
            )}
          >
            <div className="flex items-center justify-between">
              <span className="font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-muted">
                {s.trigger_id}
              </span>
              <span
                className={cn(
                  "inline-flex size-2.5 rounded-full border",
                  stateStyles[s.state],
                )}
                aria-label={s.state}
              />
            </div>
            <p className="font-display text-[1rem] leading-tight text-bone">
              {s.label}
            </p>
            <p className="font-mono text-[0.6875rem] leading-relaxed text-ash">
              {s.describes}
            </p>
            <span className="mt-auto font-mono text-[0.625rem] uppercase tracking-wider text-muted">
              state · {s.state}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}
