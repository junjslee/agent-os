import { Header } from "@/components/site/Header";
import { Footer } from "@/components/site/Footer";
import { LiveReasoningMatrix } from "@/components/viz/LiveReasoningMatrix";
import { LiveHashChainStream } from "@/components/viz/LiveHashChainStream";
import { LiveProtocolGrid } from "@/components/viz/LiveProtocolGrid";
import { TelemetryTicker } from "@/components/viz/TelemetryTicker";
import { CascadeDetector } from "@/components/viz/CascadeDetector";
import { SignalBadge } from "@/components/ui/SignalBadge";
import { CornerMarkers } from "@/components/ui/CornerMarkers";
import { fixtureTelemetry } from "@/lib/fixtures/chain";
import { fixtureCascadeSignals } from "@/lib/fixtures/cascade";

export default function DashboardPage() {
  return (
    <>
      <Header />
      <main className="min-h-screen">
        <section className="border-b border-hairline">
          <div className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-12 md:px-12 md:py-16">
            <div className="flex items-center gap-3">
              <SignalBadge signal="chain">live kernel</SignalBadge>
              <span className="font-mono text-[0.6875rem] uppercase tracking-[0.12em] text-muted">
                .episteme / dashboard · polling 10s
              </span>
            </div>
            <h1 className="font-display text-[2rem] leading-[1.05] text-bone md:text-[3rem]">
              Kernel telemetry · operator console
            </h1>
            <p className="max-w-2xl font-mono text-[0.8125rem] leading-relaxed text-ash">
              Live reads from{" "}
              <code className="text-bone">$EPISTEME_HOME/framework/*.jsonl</code>{" "}
              and{" "}
              <code className="text-bone">
                $EPISTEME_PROJECT/.episteme/reasoning-surface.json
              </code>
              . Production builds default to fixture mode; set{" "}
              <code className="text-bone">EPISTEME_MODE=live</code> and point{" "}
              <code className="text-bone">EPISTEME_HOME</code> at your local
              kernel state to swap in real telemetry.
            </p>
          </div>
        </section>

        <section className="border-b border-hairline">
          <div className="mx-auto max-w-7xl px-6 py-10 md:px-12 md:py-14">
            <CascadeDetector signals={fixtureCascadeSignals} />
          </div>
        </section>

        <section className="border-b border-hairline">
          <div className="mx-auto max-w-7xl px-6 py-10 md:px-12 md:py-14">
            <div className="relative">
              <CornerMarkers />
              <div className="grid grid-cols-1 gap-5 p-3 md:grid-cols-12">
                <div className="md:col-span-8">
                  <LiveReasoningMatrix intervalMs={10_000} />
                </div>
                <div className="md:col-span-4">
                  <LiveHashChainStream
                    intervalMs={10_000}
                    limit={50}
                    className="h-full min-h-[620px]"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="border-b border-hairline">
          <div className="mx-auto max-w-7xl px-6 py-10 md:px-12 md:py-14">
            <div className="mb-6 flex items-baseline justify-between">
              <h2 className="font-mono text-[0.6875rem] uppercase tracking-[0.2em] text-muted">
                active protocols
              </h2>
              <span className="font-mono text-[0.6875rem] text-muted">
                hover a node to see its because-chain
              </span>
            </div>
            <LiveProtocolGrid intervalMs={10_000} />
          </div>
        </section>

        <section>
          <div className="mx-auto max-w-7xl px-6 py-10 md:px-12 md:py-14">
            <TelemetryTicker events={fixtureTelemetry} />
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
