// 5-stage framework loop — Frame → Decompose → Execute → Verify → Handoff.
// Pentagon layout with directional arrows; consumes theme tokens via Tailwind
// classes (currentColor on stroke / class-based on fill) so the diagram
// inherits substrate-flip cleanly.

const STAGES = [
  { id: "frame", n: "01", label: "Frame", note: "name the question" },
  { id: "decompose", n: "02", label: "Decompose", note: "split, weigh options" },
  { id: "execute", n: "03", label: "Execute", note: "reversible first" },
  { id: "verify", n: "04", label: "Verify", note: "against metric" },
  { id: "handoff", n: "05", label: "Handoff", note: "what's still open" },
];

// Pentagon vertex positions (cx=300 cy=240 r=180; first vertex at top, then clockwise).
function vertex(i: number): { x: number; y: number } {
  const angle = (Math.PI * 2 * i) / STAGES.length - Math.PI / 2;
  return {
    x: 360 + 180 * Math.cos(angle),
    y: 270 + 180 * Math.sin(angle),
  };
}

export function FrameworkLoopDiagram() {
  const points = STAGES.map((_, i) => vertex(i));

  return (
    <figure className="relative mx-auto w-full max-w-4xl">
      <svg
        viewBox="0 0 720 540"
        role="img"
        aria-label="Five-stage framework loop: Frame, Decompose, Execute, Verify, Handoff — closing the OODA tempo"
        className="h-auto w-full text-line"
      >
        {/* Pentagon arcs (open arrows from i → i+1) */}
        {points.map((p, i) => {
          const next = points[(i + 1) % points.length];
          const mx = (p.x + next.x) / 2;
          const my = (p.y + next.y) / 2;
          // Push midpoint slightly outward from center to create gentle outward arc.
          const dx = mx - 360;
          const dy = my - 270;
          const dist = Math.hypot(dx, dy);
          const ox = mx + (dx / dist) * 24;
          const oy = my + (dy / dist) * 24;
          return (
            <g key={`arc-${i}`}>
              <path
                d={`M ${p.x} ${p.y} Q ${ox} ${oy} ${next.x} ${next.y}`}
                fill="none"
                stroke="currentColor"
                strokeWidth={1}
                strokeOpacity={0.5}
                markerEnd="url(#fl-arrow)"
              />
            </g>
          );
        })}

        {/* Center caption */}
        <g transform="translate(360 262)" textAnchor="middle">
          <text
            className="fill-bone font-display"
            fontSize={18}
            letterSpacing={0.4}
          >
            the loop
          </text>
          <text
            y={22}
            className="fill-muted font-mono"
            fontSize={9}
            letterSpacing={2}
          >
            OBSERVE · ORIENT · DECIDE · ACT
          </text>
          <text
            y={40}
            className="fill-ash font-mono"
            fontSize={9}
            letterSpacing={1.4}
          >
            speed comes from completion, not from skipping
          </text>
        </g>

        {/* Stage nodes */}
        {STAGES.map((s, i) => {
          const { x, y } = points[i];
          // Node label position offset radially outward from center.
          const dx = x - 360;
          const dy = y - 270;
          const dist = Math.hypot(dx, dy);
          // Label sits closer to the node; note sits further out.
          // Both offsets are PURELY radial — no axis-aligned offset that
          // could collide with the label for top/bottom-positioned vertices.
          const lx = x + (dx / dist) * 32;
          const ly = y + (dy / dist) * 32;
          const nx = x + (dx / dist) * 64;
          const ny = y + (dy / dist) * 64;
          // Anchor based on quadrant.
          const anchor =
            Math.abs(dx) < 30 ? "middle" : dx > 0 ? "start" : "end";

          return (
            <g key={s.id}>
              {/* Outer pulse ring on hover (decorative). */}
              <circle
                cx={x}
                cy={y}
                r={26}
                fill="var(--color-elevated)"
                stroke="currentColor"
                strokeWidth={1}
                strokeOpacity={0.85}
              />
              <circle
                cx={x}
                cy={y}
                r={26}
                fill="none"
                stroke="var(--color-chain)"
                strokeWidth={1}
                strokeOpacity={0.18}
              />
              {/* Stage number */}
              <text
                x={x}
                y={y + 5}
                textAnchor="middle"
                className="fill-bone font-display"
                fontSize={16}
              >
                {s.n}
              </text>
              {/* Stage label */}
              <text
                x={lx}
                y={ly}
                textAnchor={anchor}
                className="fill-bone font-display"
                fontSize={15}
                dominantBaseline="middle"
              >
                {s.label}
              </text>
              {/* Stage note */}
              <text
                x={nx}
                y={ny}
                textAnchor={anchor}
                className="fill-muted font-mono"
                fontSize={9}
                letterSpacing={1.1}
                dominantBaseline="middle"
              >
                {s.note}
              </text>
            </g>
          );
        })}

        {/* Arrow head marker */}
        <defs>
          <marker
            id="fl-arrow"
            viewBox="0 0 10 10"
            refX={9}
            refY={5}
            markerWidth={6}
            markerHeight={6}
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" />
          </marker>
        </defs>
      </svg>
      <figcaption className="mt-3 text-center font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-muted">
        figure 1 · the five-stage loop · the kernel refuses to skip ahead
      </figcaption>
    </figure>
  );
}
