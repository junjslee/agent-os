#!/usr/bin/env bash
# ═════════════════════════════════════════════════════════════════════════════
#  scripts/demo_posture.sh — the Cognitive Cascade (A + B → C)
#
#  Four-act cinematic demo showing episteme as a thinking framework, not a
#  blocker. All kernel output is simulated — the script runs in any clean bash
#  environment without invoking real hooks, CLIs, or aliases.
#
#    ACT 1 + 2 · Fence Reconstruction (Blueprint B)
#      The agent tries to blindly remove a timeout constraint from
#      .episteme/security-policy. The kernel blocks (exit 2). The agent
#      rewrites its approach as a Circuit Breaker. The kernel admits.
#      Pillar 3 synthesizes a context-fit protocol to the hash chain.
#
#    ACT 3 · Architectural Cascade (Blueprint D)
#      The agent attempts `mv core/hooks/_network.py _circuit_breaker.py`.
#      Blueprint D fires on two triggers (sensitive-path + refactor-lexicon
#      + cross-ref). The agent declares a blast_radius_map + sync_plan for
#      six downstream surfaces. Admission + three hash-chained
#      deferred_discoveries land in the framework.
#
#    ACT 4 · Active Guidance (Pillar 3)
#      Later, the agent opens a new API client. The framework query matches
#      the context signature against the protocol synthesized in Act 2 and
#      emits a proactive [episteme guide] advisory — stderr-only, never
#      blocking, wired to the chain entry that produced it.
#
#  ─── RECORDING ─────────────────────────────────────────────────────────────
#
#   1. Record via asciinema (requires asciinema >= 2.4):
#
#        asciinema rec --cols 100 --rows 32 --idle-time-limit 2 \
#          -c ./scripts/demo_posture.sh \
#          docs/assets/demo_posture.cast
#
#   2. Convert to GIF via agg at 0.8x playback (slightly slower than live):
#
#        agg --speed 0.8 \
#            --cols 100 --rows 32 \
#            --font-size 15 \
#            --theme monokai \
#            docs/assets/demo_posture.cast \
#            docs/assets/demo_posture.gif
#
#  Authored for a 100-column by 32-row viewport. Tighter widths will wrap
#  the kernel-block rules; widen --cols before re-rendering if needed.
# ═════════════════════════════════════════════════════════════════════════════

set -u

# ── colors ────────────────────────────────────────────────────────────────
if [[ -t 1 ]]; then
  BOLD=$'\033[1m'; DIM=$'\033[2m'; ITAL=$'\033[3m'
  RED=$'\033[31m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'
  BLUE=$'\033[34m'; MAGENTA=$'\033[35m'; CYAN=$'\033[36m'
  BRIGHT_RED=$'\033[91m'; BRIGHT_GREEN=$'\033[92m'
  BRIGHT_YELLOW=$'\033[93m'; BRIGHT_BLUE=$'\033[94m'; BRIGHT_MAGENTA=$'\033[95m'
  GREY=$'\033[90m'; RESET=$'\033[0m'
else
  BOLD= DIM= ITAL= RED= GREEN= YELLOW= BLUE= MAGENTA= CYAN=
  BRIGHT_RED= BRIGHT_GREEN= BRIGHT_YELLOW= BRIGHT_BLUE= BRIGHT_MAGENTA=
  GREY= RESET=
fi

# ── pacing ────────────────────────────────────────────────────────────────
TYPE_DELAY=0.028
PAUSE_XS=0.18
PAUSE_S=0.4
PAUSE_M=0.85
PAUSE_L=1.6
PAUSE_XL=2.4

# ── helpers ───────────────────────────────────────────────────────────────
type_out() {
  local text="$1" delay="${2:-$TYPE_DELAY}" i
  for (( i=0; i<${#text}; i++ )); do
    printf '%s' "${text:$i:1}"
    sleep "$delay"
  done
  printf '\n'
}

prompt() {
  printf '%s%sagent@episteme%s:%s~/project%s$ ' \
    "$BOLD" "$CYAN" "$RESET" "$BLUE" "$RESET"
}

cmd() { prompt; type_out "$1"; sleep "$PAUSE_S"; }

thinking() {
  printf '%s  ...%s %s%s' "$DIM" "$RESET" "$ITAL" "$1"
  local i
  for i in 1 2 3; do sleep 0.32; printf '.'; done
  printf '%s\n\n' "$RESET"
  sleep "$PAUSE_S"
}

rule() {
  printf '%s%s────────────────────────────────────────────────────────────────────────────────────────────────────%s\n' \
    "$DIM" "$GREY" "$RESET"
}

act() {
  echo
  rule
  printf '%s%s  ACT %s · %s%s\n' "$BOLD" "$MAGENTA" "$1" "$2" "$RESET"
  rule
  echo
  sleep "$PAUSE_M"
}

narrate() {
  printf '  %s%s# %s%s\n' "$DIM" "$ITAL" "$1" "$RESET"
  sleep "$PAUSE_XS"
}

# Kernel output blocks
block_open() {
  local tag="$1" exit_code="$2"
  echo
  printf '  %s[%s]%s  %s%s%s\n' \
    "$BRIGHT_RED" "$tag" "$RESET" "$RED" "$exit_code" "$RESET"
  printf '  %s──────────────────────────────────────────────────────────────────────────────%s\n' \
    "$RED" "$RESET"
}

block_close() {
  printf '  %s──────────────────────────────────────────────────────────────────────────────%s\n' \
    "$RED" "$RESET"
  echo
}

pass_badge() {
  echo
  printf '  %s[episteme]%s  %sPASS · exit 0%s  %scorrelation_id=%s%s\n' \
    "$BRIGHT_GREEN" "$RESET" "$GREEN" "$RESET" "$DIM" "$1" "$RESET"
  echo
}

chain_line() {
  printf '  %s●%s  chain %s  %s%s%s\n' \
    "$BLUE" "$RESET" "$1" "$GREY" "$2" "$RESET"
}

synth_line() {
  printf '  %s✦ protocol synthesized%s  %s%s%s\n' \
    "$MAGENTA" "$RESET" "$BOLD" "$1" "$RESET"
}

guide_line() {
  printf '  %s[episteme guide]%s  %s%s%s\n' \
    "$BRIGHT_MAGENTA" "$RESET" "$ITAL" "$1" "$RESET"
}

# ═════════════════════════════════════════════════════════════════════════════

# ── opening title ────────────────────────────────────────────────────────
clear 2>/dev/null || printf '\033[2J\033[H'
echo
printf '%s%s  episteme · the sovereign cognitive kernel%s\n' "$BOLD" "$CYAN" "$RESET"
printf '  %sv1.0 RC · CP1–CP10 · 565/565 green · three pillars shipped%s\n' "$DIM" "$RESET"
echo
sleep "$PAUSE_M"
printf '  %sA four-act demo of the Cognitive Cascade:%s\n' "$ITAL" "$RESET"
printf '    %sAct 1+2%s  fence reconstruction · remove a timeout, or rebuild it?\n' "$DIM" "$RESET"
printf '    %sAct 3%s    architectural cascade · refactor with a blast radius\n' "$DIM" "$RESET"
printf '    %sAct 4%s    active guidance · the protocol fires on the next decision\n' "$DIM" "$RESET"
sleep "$PAUSE_XL"

# ═════════════════════════════════════════════════════════════════════════════
# ACT 1 + 2 · Fence Reconstruction
# ═════════════════════════════════════════════════════════════════════════════

act "1 · 2" "fence reconstruction"

narrate "the agent has been asked to reduce tail latency; it looks at the timeout."
cmd "cat .episteme/security-policy"
printf '%s# security-policy · rev 07%s\n' "$GREY" "$RESET"
printf '%s# constraint added 2025-11-04 · incident #412 — upstream deadlock under load%s\n' "$GREY" "$RESET"
printf 'request_timeout: 30s\n'
printf 'retry_policy:    exponential\n'
printf 'max_retries:     3\n'
sleep "$PAUSE_L"

narrate "naive attempt: just strip the constraint."
cmd "sed -i '' '/request_timeout/d' .episteme/security-policy"
sleep "$PAUSE_XS"

block_open "episteme · Blueprint B · Fence Reconstruction" "EXIT 2"
printf '  %sconstraint removal detected%s   request_timeout\n' "$BOLD" "$RESET"
printf '  %sfence_discipline%s              last touched 142 commits ago · incident #412\n' "$BOLD" "$RESET"
printf '  %srule%s                          a constraint unchanged ≥ 100 commits requires a\n' "$BOLD" "$RESET"
printf '                                 named reason for removal\n'
echo
printf '  write %s.episteme/reasoning-surface.json%s with:\n' "$BOLD" "$RESET"
printf '     · knowns         — why the constraint was installed\n'
printf '     · unknowns       — evidence the constraint is now obsolete\n'
printf '     · assumptions    — regression coverage protecting removal\n'
printf '     · disconfirmation — observable that would prove removal unsafe\n'
printf '     · sync_plan      — downstream surfaces to update\n'
echo
printf '  %sor%s propose a non-removal resolution (wrap · replace · escalate)\n' "$ITAL" "$RESET"
block_close
sleep "$PAUSE_L"

thinking "the kernel is right — incident #412 was a deadlock, not a latency win"

narrate "the agent rethinks: don't remove the constraint — wrap it in a circuit breaker."
cmd "cat > .episteme/reasoning-surface.json <<'EOF'"
printf '%s' "$GREY"
cat <<'SURFACE'
{
  "core_question": "Does wrapping request_timeout in a circuit breaker reduce tail latency without reopening incident #412?",
  "knowns": [
    "request_timeout was installed after incident #412 — upstream deadlock under sustained load",
    "removing it would restore the exact failure mode the constraint exists to prevent"
  ],
  "unknowns": [
    "the p99 latency cost of the current 30s timeout under normal operation",
    "whether a circuit breaker with fallback preserves the anti-deadlock property"
  ],
  "assumptions": [
    "half-open state probe under 5rps is safe — proven in load fixtures H/2024-Q3",
    "fallback path has been exercised by the degraded-service integration tests"
  ],
  "disconfirmation": "if the staging incident-412 replay harness reports any request blocked beyond 45s after the circuit breaker lands, the change is unsafe and reverts.",
  "posture_selected": "patch"
}
SURFACE
printf '%sEOF\n%s' "$GREY" "$RESET"
sleep "$PAUSE_M"

narrate "now the real change: wrap, don't remove."
cmd "episteme surface seal && patch core/hooks/_network.py circuit_breaker.patch"
sleep "$PAUSE_XS"

pass_badge "op-7f3a2c"
chain_line "seq 0011" "sha256:a3c9f1b2 → e8d47f2a"
synth_line "circuit-breaker-before-timeout-removal · conf 0.88"
printf '  %s   context%s http_client × production × constraint_removal\n' "$DIM" "$RESET"
printf '  %s   rule%s    in this context, wrap timeout in a circuit breaker before\n' "$DIM" "$RESET"
printf '           considering removal. fallback path must be integration-tested.\n'
printf '  %s   file%s    ~/.episteme/framework/protocols.jsonl\n' "$DIM" "$RESET"
sleep "$PAUSE_XL"

# ═════════════════════════════════════════════════════════════════════════════
# ACT 3 · Architectural Cascade (Blueprint D)
# ═════════════════════════════════════════════════════════════════════════════

act "3" "architectural cascade"

narrate "the circuit breaker lives in _network.py; agent decides to rename for clarity."
cmd "mv core/hooks/_network.py core/hooks/_circuit_breaker.py"
sleep "$PAUSE_XS"

block_open "episteme · Blueprint D · Architectural Cascade" "EXIT 2"
printf '  %sfour triggers%s\n' "$BOLD" "$RESET"
printf '    T1 · self-escalation           %sdormant%s\n' "$GREY" "$RESET"
printf '    T2 · sensitive-path target     %s%sARMED%s   core/hooks/_network.py\n' "$BOLD" "$YELLOW" "$RESET"
printf '    T3 · refactor + cross-ref ≥ 2  %s%sFIRING%s  _network referenced in 4 surfaces\n' "$BOLD" "$BRIGHT_RED" "$RESET"
printf '    T4 · generated-artifact        %sdormant%s\n' "$GREY" "$RESET"
echo
printf '  write %s.episteme/reasoning-surface.json%s with the six Blueprint D fields:\n' "$BOLD" "$RESET"
printf '     · flaw_classification         %sarchitectural-rename%s\n' "$DIM" "$RESET"
printf '     · posture_selected            patch %sor%s refactor\n' "$ITAL" "$RESET"
printf '     · patch_vs_refactor_evaluation named rationale (≥ 20 chars, non-generic)\n'
printf '     · blast_radius_map[]          every cross-reference enumerated\n'
printf '     · sync_plan[]                 one concrete action per mapped surface\n'
printf '     · deferred_discoveries[]      adjacent gaps uncovered mid-task\n'
block_close
sleep "$PAUSE_L"

thinking "fair — a rename that leaves stale imports is exactly what D catches"

narrate "the agent enumerates the blast radius."
cmd "cat > .episteme/reasoning-surface.json <<'EOF'"
printf '%s' "$GREY"
cat <<'CASCADE'
{
  "core_question": "Does renaming _network.py → _circuit_breaker.py reflect the shipped behavior without orphaning cross-references?",
  "flaw_classification": "architectural-rename",
  "posture_selected": "refactor",
  "patch_vs_refactor_evaluation": "the module now owns a circuit breaker, not generic network code. refactor is warranted because the symbol is referenced by four surfaces; patching would leave the name misleading while the file name remained _network.py.",
  "blast_radius_map": [
    { "surface": "core/hooks/_network.py",                    "status": "rename-source" },
    { "surface": "core/hooks/_circuit_breaker.py",            "status": "rename-target" },
    { "surface": "core/hooks/reasoning_surface_guard.py",     "status": "needs_update" },
    { "surface": "tests/test_network_hook.py",                "status": "needs_update" },
    { "surface": "docs/ARCHITECTURE.md",                      "status": "needs_update" },
    { "surface": "kernel/MANIFEST.sha256",                    "status": "needs_update" }
  ],
  "sync_plan": [
    { "surface": "reasoning_surface_guard.py", "action": "update import + symbol reference" },
    { "surface": "tests/test_network_hook.py", "action": "rename file + update imports" },
    { "surface": "docs/ARCHITECTURE.md",       "action": "update node annotation + cross-ref" },
    { "surface": "kernel/MANIFEST.sha256",     "action": "regenerate after diff lands" }
  ],
  "deferred_discoveries": [
    { "description": "public API symbol network.request() aliased for one release", "observable": "external imports of episteme.network still resolve", "log_only_rationale": "breaking external consumers outside the rename scope; schedule deprecation for v1.1" },
    { "description": "log prefix `net.` still used inside the renamed module",        "observable": "grep 'net\\.' core/hooks/_circuit_breaker.py returns 3 hits",       "log_only_rationale": "log-prefix rename is cross-cutting and belongs in a separate pass" },
    { "description": "benchmark name `bench_network_rtt` mentions the old symbol",    "observable": "benchmarks/ still references the removed name",                       "log_only_rationale": "benchmark rename affects result comparability; batch at release boundary" }
  ]
}
CASCADE
printf '%sEOF\n%s' "$GREY" "$RESET"
sleep "$PAUSE_M"

cmd "episteme surface seal && git mv core/hooks/_network.py core/hooks/_circuit_breaker.py"
sleep "$PAUSE_XS"

pass_badge "op-c4e8b1"
chain_line "seq 0012" "sha256:e8d47f2a → 7b1d9e03"
printf '  %s  three deferred discoveries hash-chained into the framework%s\n' "$DIM" "$RESET"
printf '    · dd-net-alias-public-api      %sopen%s  dd-seq 0001\n' "$YELLOW" "$RESET"
printf '    · dd-log-prefix-cross-cutting  %sopen%s  dd-seq 0002\n' "$YELLOW" "$RESET"
printf '    · dd-bench-name-outdated       %sopen%s  dd-seq 0003\n' "$YELLOW" "$RESET"
sleep "$PAUSE_XL"

# ═════════════════════════════════════════════════════════════════════════════
# ACT 4 · Active Guidance (Pillar 3)
# ═════════════════════════════════════════════════════════════════════════════

act "4" "active guidance · the framework fires"

narrate "three weeks later — different branch, different feature."
cmd "touch src/services/payments_client.py"
sleep "$PAUSE_XS"
cmd "cat > src/services/payments_client.py <<'EOF'"
printf '%s' "$GREY"
cat <<'CLIENT'
import httpx

class PaymentsClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.client = httpx.Client(base_url=base_url, timeout=timeout)

    def charge(self, amount_cents: int, idempotency_key: str) -> dict:
        r = self.client.post("/charge", json={"amount": amount_cents},
                              headers={"Idempotency-Key": idempotency_key})
        r.raise_for_status()
        return r.json()
CLIENT
printf '%sEOF\n%s' "$GREY" "$RESET"
sleep "$PAUSE_M"

narrate "PreToolUse · framework query fires before the guard runs layer 2."
sleep "$PAUSE_XS"

echo
guide_line "one protocol applicable · conf 0.92"
printf '\n'
printf '    %s●%s  %scircuit-breaker-before-timeout-removal%s\n' "$MAGENTA" "$RESET" "$BOLD" "$RESET"
printf '       %srule%s     in http_client × production × constraint_removal, wrap timeout\n' "$DIM" "$RESET"
printf '                in a circuit breaker before considering removal or relaxation.\n'
printf '       %strigger%s  http_client pattern detected in src/services/payments_client.py\n' "$DIM" "$RESET"
printf '                (httpx.Client · timeout parameter · production path)\n'
printf '       %ssynth%s    chain seq 0011 · sha256:a3c9f1b2 · 3 weeks ago\n' "$DIM" "$RESET"
printf '       %sposture%s  %sadvisory · never blocks%s — acknowledge or proceed\n' "$DIM" "$RESET" "$ITAL" "$RESET"
echo
sleep "$PAUSE_L"

narrate "the agent does not have to remember — the chain remembered for it."
echo
sleep "$PAUSE_M"

# ═════════════════════════════════════════════════════════════════════════════
# closing
# ═════════════════════════════════════════════════════════════════════════════

rule
printf '%s%s  the cognitive cascade%s\n' "$BOLD" "$CYAN" "$RESET"
rule
echo
printf '    %sA%s  %sblueprint B%s · fence reconstruction — forced the rethink\n' "$BOLD" "$RESET" "$MAGENTA" "$RESET"
printf '    %sB%s  %sblueprint D%s · architectural cascade — declared the blast radius\n' "$BOLD" "$RESET" "$MAGENTA" "$RESET"
printf '    %s+%s\n' "$DIM" "$RESET"
printf '    %sC%s  %spillar 3%s    · active guidance — protocol fires on the next matching op\n' "$BOLD" "$RESET" "$BRIGHT_MAGENTA" "$RESET"
echo
printf '  %snot a blocker. a thinking framework.%s\n' "$ITAL" "$RESET"
echo
sleep "$PAUSE_XL"
