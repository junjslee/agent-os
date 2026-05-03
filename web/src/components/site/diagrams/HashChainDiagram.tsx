// Hash-chain envelope visualization.
// Universal example readers recognize: git's commit ancestry.
// Each commit references the previous commit's SHA — same shape as
// EPISTEME's protocol chain. The fourth envelope shows what tamper-
// evidence catches: someone rewriting commit 002's tree silently
// breaks the parent_sha reference from commit 003 — `git fsck` and
// `verify_chain` both refuse to trust the chain past the break.

const CHAIN = [
  {
    seq: "commit 001",
    label: "initial commit",
    prev: "—",
    payload: "feat: scaffold project",
    hash: "a83cf12",
  },
  {
    seq: "commit 002",
    label: "feature ships",
    prev: "a83cf12",
    payload: "feat: add user login",
    hash: "d471e8b",
  },
  {
    seq: "commit 003",
    label: "fix lands",
    prev: "d471e8b",
    payload: "fix: rate-limit edge case",
    hash: "9b2a3c0",
  },
];

export function HashChainDiagram() {
  return (
    <figure className="relative mx-auto w-full max-w-5xl">
      <svg
        viewBox="0 0 900 320"
        role="img"
        aria-label="Append-only hash chain — three envelopes with prev_hash, payload, hash; a fourth envelope shows tamper detection"
        className="h-auto w-full text-line"
      >
        <defs>
          <marker
            id="hc-arrow"
            viewBox="0 0 10 10"
            refX={9}
            refY={5}
            markerWidth={6}
            markerHeight={6}
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--color-chain)" />
          </marker>
          <marker
            id="hc-arrow-break"
            viewBox="0 0 10 10"
            refX={9}
            refY={5}
            markerWidth={6}
            markerHeight={6}
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--color-disconfirm)" />
          </marker>
        </defs>

        {/* Three sealed envelopes (chain head) */}
        {CHAIN.map((env, i) => {
          const x = 40 + i * 200;
          return (
            <g key={env.seq}>
              <rect
                x={x}
                y={70}
                width={170}
                height={170}
                fill="var(--color-elevated)"
                stroke="var(--color-chain)"
                strokeWidth={1.2}
                strokeOpacity={0.75}
              />
              <text
                x={x + 12}
                y={92}
                className="fill-chain font-mono"
                fontSize={11}
                letterSpacing={1.2}
              >
                envelope · {env.seq}
              </text>
              <text
                x={x + 12}
                y={106}
                className="fill-muted font-mono"
                fontSize={9}
                letterSpacing={1}
              >
                {env.label}
              </text>

              {/* prev_hash field */}
              <line
                x1={x + 12}
                y1={120}
                x2={x + 158}
                y2={120}
                stroke="currentColor"
                strokeOpacity={0.3}
                strokeWidth={1}
              />
              <text
                x={x + 12}
                y={138}
                className="fill-ash font-mono"
                fontSize={9}
                letterSpacing={1.4}
              >
                PREV_HASH
              </text>
              <text
                x={x + 12}
                y={152}
                className="fill-bone font-mono"
                fontSize={10}
              >
                {env.prev}
              </text>

              {/* payload field */}
              <line
                x1={x + 12}
                y1={162}
                x2={x + 158}
                y2={162}
                stroke="currentColor"
                strokeOpacity={0.3}
                strokeWidth={1}
              />
              <text
                x={x + 12}
                y={178}
                className="fill-ash font-mono"
                fontSize={9}
                letterSpacing={1.4}
              >
                PAYLOAD
              </text>
              <text
                x={x + 12}
                y={192}
                className="fill-bone font-mono"
                fontSize={9}
              >
                {env.payload}
              </text>

              {/* hash field */}
              <line
                x1={x + 12}
                y1={202}
                x2={x + 158}
                y2={202}
                stroke="currentColor"
                strokeOpacity={0.3}
                strokeWidth={1}
              />
              <text
                x={x + 12}
                y={218}
                className="fill-ash font-mono"
                fontSize={9}
                letterSpacing={1.4}
              >
                HASH
              </text>
              <text
                x={x + 12}
                y={232}
                className="fill-bone font-mono"
                fontSize={10}
              >
                {env.hash}
              </text>

              {/* Chain-link arrow to next envelope */}
              {i < CHAIN.length - 1 && (
                <g>
                  <line
                    x1={x + 170}
                    y1={155}
                    x2={x + 200}
                    y2={155}
                    stroke="var(--color-chain)"
                    strokeWidth={1.4}
                    strokeOpacity={0.85}
                    markerEnd="url(#hc-arrow)"
                  />
                  <text
                    x={x + 185}
                    y={148}
                    textAnchor="middle"
                    className="fill-chain font-mono"
                    fontSize={9}
                    letterSpacing={1.2}
                  >
                    seal
                  </text>
                </g>
              )}
            </g>
          );
        })}

        {/* Tamper-evidence callout — fourth envelope dashed in disconfirm tone */}
        <g>
          <line
            x1={640}
            y1={155}
            x2={680}
            y2={155}
            stroke="var(--color-disconfirm)"
            strokeWidth={1.4}
            strokeOpacity={0.85}
            strokeDasharray="3 3"
            markerEnd="url(#hc-arrow-break)"
          />
          <rect
            x={690}
            y={70}
            width={170}
            height={170}
            fill="none"
            stroke="var(--color-disconfirm)"
            strokeWidth={1.2}
            strokeOpacity={0.85}
            strokeDasharray="3 3"
          />
          <text
            x={702}
            y={92}
            className="fill-disconfirm font-mono"
            fontSize={11}
            letterSpacing={1.2}
          >
            commit 002 · rewritten
          </text>
          <text
            x={702}
            y={106}
            className="fill-muted font-mono"
            fontSize={9}
            letterSpacing={1}
          >
            tree silently changed
          </text>
          <text
            x={702}
            y={138}
            className="fill-ash font-mono"
            fontSize={9}
            letterSpacing={1.4}
          >
            EXPECTED PARENT
          </text>
          <text
            x={702}
            y={152}
            className="fill-bone font-mono"
            fontSize={10}
          >
            d471e8b
          </text>
          <text
            x={702}
            y={178}
            className="fill-ash font-mono"
            fontSize={9}
            letterSpacing={1.4}
          >
            COMPUTED PARENT
          </text>
          <text
            x={702}
            y={192}
            className="fill-disconfirm font-mono"
            fontSize={10}
          >
            f02ad81
          </text>
          <text
            x={702}
            y={218}
            className="fill-disconfirm font-mono"
            fontSize={9}
            letterSpacing={1.4}
          >
            VERIFY · FAIL
          </text>
          <text
            x={702}
            y={232}
            className="fill-muted font-mono"
            fontSize={9}
          >
            history breaks · chain refuses
          </text>
        </g>

        {/* Header */}
        <g>
          <text
            x={40}
            y={36}
            className="fill-muted font-mono"
            fontSize={10}
            letterSpacing={2}
          >
            APPEND-ONLY · PARENT-LINKED · LIKE GIT
          </text>
          <text
            x={40}
            y={56}
            className="fill-bone font-display"
            fontSize={20}
          >
            Tamper-evident memory, not a log.
          </text>
        </g>

        {/* Footer note */}
        <text
          x={40}
          y={300}
          className="fill-ash font-mono"
          fontSize={10}
          letterSpacing={1.2}
        >
          every commit names its parent. break one, break the rest.
        </text>
      </svg>
      <figcaption className="mt-3 text-center font-mono text-[0.6875rem] uppercase tracking-[0.16em] text-muted">
        figure 3 · the chain · GENESIS → seal → seal · tamper → fail-closed
      </figcaption>
    </figure>
  );
}
