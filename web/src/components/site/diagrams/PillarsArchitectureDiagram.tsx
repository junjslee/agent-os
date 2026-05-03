// Three-pillar architecture diagram.
// Left column: Pillar 1 — four named blueprints (A · B · C · D).
// Center column: Pillar 2 — three chained envelopes (append-only hash chain).
// Right column: Pillar 3 — three advisory query nodes (active guidance).
// Horizontal arrows show the data flow: every blueprint write seals into
// the chain; the chain feeds the guidance query at the next decision.
// A return arrow at the bottom closes the loop — guidance modifies the
// next blueprint firing.

const BLUEPRINTS = [
  { tag: "A", name: "Axiomatic Judgment" },
  { tag: "B", name: "Fence Reconstruction" },
  { tag: "C", name: "Consequence Chain" },
  { tag: "D", name: "Architectural Cascade" },
];

const ENVELOPES = [
  { seq: "GENESIS", payload: "ø" },
  { seq: "#001", payload: "blueprint-B-fired" },
  { seq: "#002", payload: "cascade-resolved" },
];

const GUIDANCE = [
  { kind: "query", label: "match by context signature" },
  { kind: "advise", label: "one advisory per high-impact op" },
  { kind: "digest", label: "session-start synthesis digest" },
];

export function PillarsArchitectureDiagram() {
  return (
    <figure className="relative mx-auto w-full max-w-5xl">
      <svg
        viewBox="0 0 900 480"
        role="img"
        aria-label="Three-pillar architecture: Cognitive Blueprints, Append-Only Hash Chain, Active Guidance"
        className="h-auto w-full text-line"
      >
        <defs>
          <marker
            id="pa-arrow"
            viewBox="0 0 10 10"
            refX={9}
            refY={5}
            markerWidth={6}
            markerHeight={6}
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" />
          </marker>
          <marker
            id="pa-arrow-chain"
            viewBox="0 0 10 10"
            refX={9}
            refY={5}
            markerWidth={6}
            markerHeight={6}
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--color-chain)" />
          </marker>
        </defs>

        {/* Pillar headings */}
        <g textAnchor="middle">
          <text
            x={150}
            y={30}
            className="fill-muted font-mono"
            fontSize={10}
            letterSpacing={2}
          >
            PILLAR 01
          </text>
          <text
            x={150}
            y={48}
            className="fill-bone font-display"
            fontSize={18}
          >
            Cognitive Blueprints
          </text>

          <text
            x={450}
            y={30}
            className="fill-muted font-mono"
            fontSize={10}
            letterSpacing={2}
          >
            PILLAR 02
          </text>
          <text
            x={450}
            y={48}
            className="fill-bone font-display"
            fontSize={18}
          >
            Append-Only Hash Chain
          </text>

          <text
            x={750}
            y={30}
            className="fill-muted font-mono"
            fontSize={10}
            letterSpacing={2}
          >
            PILLAR 03
          </text>
          <text
            x={750}
            y={48}
            className="fill-bone font-display"
            fontSize={18}
          >
            Active Guidance
          </text>
        </g>

        {/* Pillar 1 — Blueprint stack */}
        {BLUEPRINTS.map((b, i) => {
          const y = 90 + i * 60;
          return (
            <g key={b.tag}>
              <rect
                x={40}
                y={y}
                width={220}
                height={44}
                fill="var(--color-elevated)"
                stroke="currentColor"
                strokeWidth={1}
                strokeOpacity={0.7}
              />
              <text
                x={56}
                y={y + 28}
                className="fill-chain font-mono"
                fontSize={13}
                letterSpacing={1.2}
              >
                {b.tag}
              </text>
              <text
                x={78}
                y={y + 28}
                className="fill-bone font-display"
                fontSize={13}
              >
                {b.name}
              </text>
            </g>
          );
        })}

        {/* Pillar 2 — Chained envelopes */}
        {ENVELOPES.map((env, i) => {
          const y = 100 + i * 100;
          return (
            <g key={env.seq}>
              <rect
                x={360}
                y={y}
                width={180}
                height={76}
                fill="var(--color-elevated)"
                stroke="var(--color-chain)"
                strokeWidth={1.2}
                strokeOpacity={0.75}
              />
              <text
                x={376}
                y={y + 20}
                className="fill-chain font-mono"
                fontSize={10}
                letterSpacing={1.2}
              >
                envelope · {env.seq}
              </text>
              <text
                x={376}
                y={y + 38}
                className="fill-ash font-mono"
                fontSize={9}
                letterSpacing={1.2}
              >
                PREV_HASH
              </text>
              <text
                x={376}
                y={y + 54}
                className="fill-bone font-mono"
                fontSize={9}
              >
                payload · {env.payload}
              </text>
              <text
                x={376}
                y={y + 70}
                className="fill-ash font-mono"
                fontSize={9}
                letterSpacing={1.2}
              >
                HASH
              </text>
              {/* Inter-envelope chain link */}
              {i < ENVELOPES.length - 1 && (
                <line
                  x1={450}
                  y1={y + 76}
                  x2={450}
                  y2={y + 100}
                  stroke="var(--color-chain)"
                  strokeWidth={1.2}
                  strokeOpacity={0.55}
                  markerEnd="url(#pa-arrow-chain)"
                />
              )}
            </g>
          );
        })}

        {/* Pillar 3 — Guidance nodes */}
        {GUIDANCE.map((g, i) => {
          const y = 100 + i * 100;
          return (
            <g key={g.kind}>
              <rect
                x={640}
                y={y}
                width={220}
                height={76}
                fill="var(--color-elevated)"
                stroke="currentColor"
                strokeWidth={1}
                strokeOpacity={0.7}
              />
              <text
                x={656}
                y={y + 26}
                className="fill-verified font-mono"
                fontSize={10}
                letterSpacing={1.2}
              >
                {g.kind}
              </text>
              <text
                x={656}
                y={y + 50}
                className="fill-bone font-mono"
                fontSize={10}
              >
                {g.label}
              </text>
            </g>
          );
        })}

        {/* Flow arrows: Pillar 1 → Pillar 2 (every fire seals to chain) */}
        <line
          x1={250}
          y1={170}
          x2={370}
          y2={140}
          stroke="currentColor"
          strokeWidth={1}
          strokeOpacity={0.55}
          markerEnd="url(#pa-arrow)"
        />
        <text
          x={310}
          y={146}
          className="fill-muted font-mono"
          fontSize={9}
          letterSpacing={1}
        >
          seal
        </text>

        {/* Flow arrows: Pillar 2 → Pillar 3 (chain query feeds guidance) */}
        <line
          x1={530}
          y1={228}
          x2={650}
          y2={228}
          stroke="currentColor"
          strokeWidth={1}
          strokeOpacity={0.55}
          markerEnd="url(#pa-arrow)"
        />
        <text
          x={590}
          y={222}
          className="fill-muted font-mono"
          fontSize={9}
          letterSpacing={1}
          textAnchor="middle"
        >
          query
        </text>

        {/* Return loop: Pillar 3 → Pillar 1 (guidance shapes next firing) */}
        <path
          d="M 750 410 Q 450 460 150 410"
          fill="none"
          stroke="currentColor"
          strokeWidth={1}
          strokeOpacity={0.4}
          strokeDasharray="4 4"
          markerEnd="url(#pa-arrow)"
        />
        <text
          x={450}
          y={455}
          className="fill-muted font-mono"
          fontSize={10}
          letterSpacing={1.2}
          textAnchor="middle"
        >
          guidance shapes the next blueprint firing — the loop is bidirectional
        </text>
      </svg>
      <figcaption className="mt-3 text-center font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-muted">
        figure 2 · three pillars · seal · query · guide · the loop closes on itself
      </figcaption>
    </figure>
  );
}
