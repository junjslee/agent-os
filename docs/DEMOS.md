# Demos

Two demos. The first is the homepage hero; the second is here because the
homepage should not lead with enforcement.

---

## ① Posture as thinking — homepage hero

`scripts/demo_posture.sh` · ~75 s · cinematic differential.

Same PM prompt walked twice. Fluent default (*doxa*) versus the
Reasoning Surface authored field-by-field (*episteme*). The climax is
the Reasoning Surface itself — Core Question reframed, Unknowns
enumerated as classifiable failure modes, Disconfirmation pre-committed
as a falsifiable pivot.

Beat 3 then runs the surface against the real Reasoning-Surface Guard
in three rungs:

1. `"None"` blocks. The shallowest thing the kernel does.
2. A 43-char fluent-vacuous disconfirmation passes the hot path. The
   honest kernel limit — structural pass, semantic emptiness.
3. A concrete falsifiable pivot passes for the right reason. The
   posture.

Beat 4 closes the circuit: phase 11 promotion catches over time what
the hot path missed at write; phase 12 (profile-audit) is the loop
that audits *the operator's claimed cognitive profile* against the
lived episodic record.

GIF: [`docs/assets/posture_demo.gif`](./assets/posture_demo.gif).

## ② Posture as enforcement of the surface

`scripts/demo_strict_mode.sh` · three acts.

This demo shows what the kernel does to *protect* a Reasoning Surface
from being treated as decoration. It is intentionally not the
homepage hero — leading with enforcement reads as "linter," and the
product is a Cognitive OS, not a wrist-slapper. Watch this after the
first demo, with the first demo's framing already in your head.

Three acts:

1. **The lazy surface is caught.** A surface with `"disconfirmation":
   "None"` (or `"해당 없음"`, or any other lazy placeholder) is rejected
   by the semantic validator. The block is the shallowest layer of
   defense; the surface itself is the load-bearing layer.
2. **Cross-call indirection is caught.** The agent writes a script
   that runs an irreversible op, then executes the script in a later
   tool call. The stateful interceptor (v0.10) reads the script's
   contents at execute-time via sha256 + deep-scan and blocks. The
   block protects the surface contract from agent-side workarounds.
3. **The kernel learns from the praxis.** `episteme evolve friction`
   pairs prediction-with-outcome telemetry, ranks the unknowns the
   operator keeps under-naming, and emits a Friction Report that
   feeds the calibration loop.

GIF: [`docs/assets/strict_mode_demo.gif`](./assets/strict_mode_demo.gif).

## Why two demos, in this order

The first demo answers *what should the agent be doing differently?*
The second answers *what does the kernel do when the agent doesn't do
it?* The order matters: the kernel exists to protect the surface, not
the other way around. A reader who only watches one should watch the
first.

## Recording

Both scripts run hermetically against a tempdir HOME so re-recording
does not touch real `~/.episteme/` state.

```bash
asciinema rec -c ./scripts/demo_posture.sh \
  docs/assets/posture_demo.cast
agg docs/assets/posture_demo.cast docs/assets/posture_demo.gif \
  --cols 100 --rows 36 --font-size 15 --theme monokai

asciinema rec -c ./scripts/demo_strict_mode.sh \
  docs/assets/strict_mode_demo.cast
agg docs/assets/strict_mode_demo.cast docs/assets/strict_mode_demo.gif \
  --cols 100 --rows 34 --font-size 15 --theme monokai
```

See [`docs/CONTRIBUTING.md`](./CONTRIBUTING.md#recording-the-strict-mode-demo)
for the full recording workflow.
