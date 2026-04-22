import { cn, formatTime } from "@/lib/utils";
import type { TelemetryEvent } from "@/lib/types/episteme";

const levelTone: Record<TelemetryEvent["level"], string> = {
  info: "text-muted",
  signal: "text-verified",
  warn: "text-unknown",
  error: "text-disconfirm",
};

interface TelemetryTickerProps {
  events: TelemetryEvent[];
  className?: string;
}

export function TelemetryTicker({ events, className }: TelemetryTickerProps) {
  const recent = [...events].sort(
    (a, b) => new Date(b.ts).getTime() - new Date(a.ts).getTime(),
  );

  return (
    <div
      className={cn("panel-gradient font-mono text-[0.75rem]", className)}
    >
      <header className="flex items-center justify-between border-b border-hairline px-4 py-2">
        <span className="text-[0.6875rem] uppercase tracking-[0.2em] text-muted">
          kernel telemetry
        </span>
        <span className="text-[0.625rem] text-muted">
          {recent.length} events
        </span>
      </header>
      <ol className="flex max-h-60 flex-col divide-y divide-hairline overflow-y-auto">
        {recent.map((e) => (
          <li
            key={e.id}
            className="flex items-center gap-3 px-4 py-1.5 leading-tight"
          >
            <span className="text-[0.6875rem] text-muted">
              {formatTime(e.ts)}
            </span>
            <span
              className={cn(
                "w-20 shrink-0 text-[0.6875rem] uppercase tracking-wide",
                levelTone[e.level],
              )}
            >
              {e.code}
            </span>
            <span className="truncate text-ash">{e.message}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}
