import { ImageResponse } from "next/og";

// OpenGraph / Twitter social-share card for episteme.
//
// Next.js 16 app-router convention: this file is served at `/opengraph-image`
// and automatically referenced by the generated <meta property="og:image">
// tag for every page under the app root, overriding the bundled default.
//
// Design discipline: dark operator-console palette matching the Hero
// (bone/ash/chain/hairline on near-black substrate), no custom fonts (system
// sans only — Satoshi/Fraunces loading in the build-time image pipeline adds
// complexity disproportionate to the marginal legibility gain at 1200×630).
// Iterate on this after v1.0 GA if the card's visual identity becomes a
// measurable brand-recall signal.

export const alt = "episteme — Semantic Governance for Agentic Memory";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          background: "#0a0a0b",
          padding: "80px 96px",
          position: "relative",
          fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif",
        }}
      >
        {/* Ambient corner atmosphere — matches Hero panel-gradient */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "40%",
            height: "60%",
            background:
              "radial-gradient(circle at 0% 0%, rgba(78, 166, 255, 0.14) 0%, transparent 70%)",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: 0,
            right: 0,
            width: "45%",
            height: "55%",
            background:
              "radial-gradient(circle at 100% 100%, rgba(255, 128, 120, 0.08) 0%, transparent 70%)",
          }}
        />

        {/* Top meta row — substrate pill + version */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
            fontSize: 18,
            letterSpacing: "0.18em",
            textTransform: "uppercase",
            color: "#6a7080",
          }}
        >
          <span
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              border: "1px solid #4ea6ff",
              padding: "6px 14px",
              color: "#9dc7ff",
              fontSize: 15,
            }}
          >
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: "#4ea6ff",
              }}
            />
            substrate · v1.0 rc
          </span>
          <span>causal-consequence scaffolding</span>
        </div>

        {/* Spacer */}
        <div style={{ flex: 1 }} />

        {/* Primary wordmark + tagline */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "28px",
          }}
        >
          <div
            style={{
              fontSize: 128,
              fontWeight: 300,
              letterSpacing: "-0.04em",
              color: "#f2efe8",
              lineHeight: 1,
            }}
          >
            episteme
          </div>

          <div
            style={{
              fontSize: 42,
              fontWeight: 400,
              letterSpacing: "-0.01em",
              color: "#c9c5ba",
              lineHeight: 1.25,
              maxWidth: "85%",
            }}
          >
            Semantic Governance for Agentic Memory
          </div>
        </div>

        {/* Spacer */}
        <div style={{ flex: 1 }} />

        {/* Bottom signature row */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontSize: 20,
            letterSpacing: "0.1em",
            color: "#6a7080",
            borderTop: "1px solid #2a2d36",
            paddingTop: "24px",
          }}
        >
          <span>Sovereign Cognitive Kernel · 생각의 틀</span>
          <span style={{ color: "#9dc7ff" }}>epistemekernel.com</span>
        </div>
      </div>
    ),
    { ...size },
  );
}
