import { cn } from "@/lib/utils";

interface CornerMarkersProps {
  /** When true, only top corners render (for panels that sit flush with below content). */
  topOnly?: boolean;
  className?: string;
}

const Plus = () => (
  <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path d="M12 4v16m8-8H4" strokeLinecap="round" />
  </svg>
);

export function CornerMarkers({ topOnly, className }: CornerMarkersProps) {
  return (
    <>
      <span className={cn("corner-marker tl", className)} aria-hidden>
        <Plus />
      </span>
      <span className={cn("corner-marker tr", className)} aria-hidden>
        <Plus />
      </span>
      {!topOnly && (
        <>
          <span className={cn("corner-marker bl", className)} aria-hidden>
            <Plus />
          </span>
          <span className={cn("corner-marker br", className)} aria-hidden>
            <Plus />
          </span>
        </>
      )}
    </>
  );
}
