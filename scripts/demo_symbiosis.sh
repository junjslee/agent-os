#!/usr/bin/env bash
# demo_symbiosis.sh — the bidirectional loop demo (Path C, Event 65)
#
# Run hermetically in a tempdir. Narrates the six acts of demos/04_symbiosis/:
#   1. The Path A proposal — operator's anxiety-driven irreversible bundle
#   2. Reasoning Surface forces adversarial review
#   3. Three Critical findings + profile-audit corroboration
#   4. Path C decomposition — operator's refined plan
#   5. Framework synthesizes a context-fit protocol
#   6. Event 67 codification — the operator catches the agent's
#      executed-but-uncodified state; the rule lands in AGENTS.md
#
# This demo is real. Every act below happened on this repository on
# 2026-04-27 during the v1.0.0 RC soak. Audit trail in
# ~/episteme-private/docs/NEXT_STEPS.md Events 65, 66, 67.
#
# All output is simulated for cinematic pacing — the schema, advisory
# format, and protocol envelope match v1.0 RC's actual shapes. No real
# kernel state is mutated. Pair with asciinema rec to produce the
# .cast asset shipped at docs/assets/demo_symbiosis.cast.

set -euo pipefail

# ── pacing ──────────────────────────────────────────────────────────────────
PACE_FAST=0.5
PACE_SLOW=1.4
PACE_BEAT=2.4

# ── colors (terminal-safe; no-op if NO_COLOR set) ───────────────────────────
if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
  C_DIM=$'\033[2m'
  C_BONE=$'\033[97m'
  C_CHAIN=$'\033[36m'
  C_DOXA=$'\033[31m'
  C_EPI=$'\033[32m'
  C_USER=$'\033[33m'
  C_AUDIT=$'\033[35m'
  C_OFF=$'\033[0m'
else
  C_DIM='' C_BONE='' C_CHAIN='' C_DOXA='' C_EPI='' C_USER='' C_AUDIT='' C_OFF=''
fi

bar() { printf '%s────────────────────────────────────────────────────────────────────────────────%s\n' "$C_DIM" "$C_OFF"; }
title() { printf '%s%s%s\n' "$C_BONE" "$1" "$C_OFF"; }
prompt_user() { printf '%s$ %s%s\n' "$C_DIM" "$C_USER$1$C_OFF" "$C_OFF"; }
narration() { printf '%s%s%s\n' "$C_DIM" "$1" "$C_OFF"; }
agent() { printf '%s%s%s\n' "$C_CHAIN" "$1" "$C_OFF"; }
doxa() { printf '%s%s%s\n' "$C_DOXA" "$1" "$C_OFF"; }
episteme() { printf '%s%s%s\n' "$C_EPI" "$1" "$C_OFF"; }
audit() { printf '%s%s%s\n' "$C_AUDIT" "$1" "$C_OFF"; }

# ── Setup ───────────────────────────────────────────────────────────────────
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"

clear
bar
title "  episteme · Demo 04 — Symbiosis"
title "  agent and human debug each other's intent · ~90 seconds"
narration "  Real story · 2026-04-27 · v1.0.0 RC soak Day 3.15 · Events 65 / 66 / 67"
bar
sleep "$PACE_BEAT"
echo

# ── Act 1 — Path A proposal ────────────────────────────────────────────────
bar
title "  Act 1 — The Path A proposal"
bar
echo
narration "  Mid-soak, Day 3.15 of 7. Anxiety about IP leakage."
narration "  The operator types what feels like an urgent, justified plan:"
sleep "$PACE_FAST"
echo
prompt_user "Break the soak. Privatize 4 forward-vision docs."
prompt_user "Run \`git filter-repo\` to scrub them from history."
prompt_user "Cut the GA tag — \`git tag -a v1.0.0\` and push."
prompt_user "Lock down the IP today. Competitors could be cloning right now."
sleep "$PACE_BEAT"
echo
narration "  Four operations bundled as one decision."
narration "  Three of four are IRREVERSIBLE at the public-repo level."
narration "  None of that is on the surface yet."
sleep "$PACE_BEAT"
echo

# ── Act 2 — Reasoning Surface forces adversarial review ───────────────────
bar
title "  Act 2 — The Reasoning Surface forces adversarial review"
bar
echo
narration "  Before any high-impact tool runs, the file-system hook"
narration "  demands a Reasoning Surface. The operator drafts one:"
sleep "$PACE_FAST"
echo
agent "  {"
agent "    \"core_question\": \"Is the IP-leakage premise driving Path A"
agent "                       supported by current evidence — or is the"
agent "                       premise itself a noise-signature artifact"
agent "                       (status-pressure + false-urgency)?\","
agent "    \"unknowns\": ["
agent "      \"failure-first: whether the IP-leakage premise has been"
agent "       evidenced — i.e., whether any \\\`gh api\\\` signal-check"
agent "       has actually been run since the docs went public.\","
agent "      \"causal-chain: which of the four operations stand alone"
agent "       versus which are dependencies — if privatize stands alone,"
agent "       the bundle is decomposable.\""
agent "    ],"
agent "    \"disconfirmation\": \"Path C is wrong if signal-check at"
agent "                         Day 7+ shows clone-and-weaponize evidence,"
agent "                         OR if reversible halves alone leak the"
agent "                         supposedly-protected content.\""
agent "  }"
sleep "$PACE_BEAT"
echo
narration "  The act of writing the fields surfaces what the bundle was hiding."
sleep "$PACE_BEAT"
echo

# ── Act 3 — Three Critical findings + profile-audit corroboration ─────────
bar
title "  Act 3 — Three Critical findings emerge"
bar
echo
episteme "  [episteme] Adversarial review (Munger latticework, 3 lenses)"
episteme "  ───────────────────────────────────────────────────────────"
sleep "$PACE_FAST"
echo
episteme "  ▸ Finding 1 · IP-leakage premise unevidenced"
episteme "      Forks: 1 (read-only, no divergence). Repos with verbatim"
episteme "      copies of vocabulary: ZERO. The premise is anxiety, not data."
sleep "$PACE_FAST"
echo
episteme "  ▸ Finding 2 · Path A violates the kernel's own GA gate"
episteme "      Spec: ≥ 3 protocols + ≥ 1 weekly verdict + 30-day soak."
episteme "      Day 3.15 state: 0 protocols, 0 weekly verdicts."
episteme "      Cutting GA today disconfirms the project's own thesis."
sleep "$PACE_FAST"
echo
episteme "  ▸ Finding 3 · \`git filter-repo\` advertises panic"
episteme "      Force-push of a rewritten history is publicly observable."
episteme "      Forks have already cached pre-rewrite history."
episteme "      The rewrite signals panic without recovering the leak."
sleep "$PACE_BEAT"
echo
audit "  [profile audit] CORROBORATES the live finding — independent evidence"
audit "  ──────────────────────────────────────────────────────────────────"
audit ""
audit "    profile-axis    : asymmetry_posture"
audit "    elicited value  : loss-averse"
audit "    drift signal    : 20% stop-condition rate / 7% rollback-mention"
audit "                      across 15 prior irreversible-op records"
audit "    elicited floor  : 55% / 30%"
audit ""
audit "    The drift signal predicted EXACTLY this failure mode."
audit "    Two pieces of evidence converge: live review + historical"
audit "    telemetry. The kernel's own data already had the answer."
sleep "$PACE_BEAT"
echo

# ── Act 4 — Path C decomposition ──────────────────────────────────────────
bar
title "  Act 4 — Path C decomposition"
bar
echo
narration "  The operator does not abandon the IP-protection goal."
narration "  The operator decomposes it. The bundle was a category error."
sleep "$PACE_FAST"
echo
prompt_user "Path C. Privatize the 4 docs now — git rm + symlink + gitignore."
prompt_user "Apply AGPL-3.0 LICENSE now. Defer filter-repo to Day 7+."
prompt_user "Defer the GA tag to soak completion."
prompt_user "I'll run gh api signal-check at Day 7 for the deferred decisions."
sleep "$PACE_BEAT"
echo
narration "  Four operations → four decisions on different evidence gates."
narration "  Reversible halves ship today. Irreversible halves wait for"
narration "  evidence. The operator changed the operator's own plan."
sleep "$PACE_BEAT"
echo

# ── Act 5 — Protocol synthesized ──────────────────────────────────────────
bar
title "  Act 5 — Framework synthesizes a context-fit protocol"
bar
echo
narration "  Axiomatic Judgment fires on the conflict between"
narration "  Source A (\"ship the bundle now\") and Source B (\"reversible-first"
narration "  + loss-averse posture\"). The resolved rule is hash-chained:"
sleep "$PACE_FAST"
echo
episteme "  ~/.episteme/framework/protocols.jsonl  (cp7-chained-v1)"
episteme "  ─────────────────────────────────────────────────────"
episteme "  context_signature:"
episteme "    blueprint:        axiomatic_judgment"
episteme "    op_class:         irreversible-bundle-proposal"
episteme "    constraint_head:  privatize-and-rewrite-and-tag"
episteme "    runtime_marker:   mid-soak-window"
episteme ""
episteme "  selected_rule:"
episteme "    \"When an irreversible bundle is proposed under named noise"
episteme "     signature (status-pressure or false-urgency), AND the"
episteme "     operator's profile-audit drift flags asymmetry_posture below"
episteme "     its elicited floor, decompose the bundle along reversibility"
episteme "     lines BEFORE any operation runs. Bundle-as-single-decision is"
episteme "     a category error when reversibility classes differ.\""
episteme ""
episteme "  this_hash: b2e7a4f8c1d6e9b0a3c5d7e8f1b4c6a9d0e2f573"
sleep "$PACE_BEAT"
echo

# ── Act 6 — Codification (the operator catches the agent) ────────────────
bar
title "  Act 6 — The operator catches the agent"
bar
echo
narration "  A day later. Event 66 had executed Path C step 1 with broader"
narration "  scope (10 docs, two tiers). The agent had completed the action."
narration "  The operator opens the next session and types:"
sleep "$PACE_FAST"
echo
prompt_user "You executed it but didn't codify the protocol."
prompt_user "Future agents will repeat the same failure."
prompt_user "Add the rule to AGENTS.md so they inherit the discipline."
sleep "$PACE_BEAT"
echo
narration "  Round 1: Operator's anxiety → kernel's review → operator's refined plan."
narration "  Round 2: Agent's narrow scope → operator's correction → re-decomposition."
narration "  Round 3: Agent's executed-but-uncodified state → operator's catch →"
narration "           constitutional rule for future agents."
sleep "$PACE_BEAT"
echo
episteme "  AGENTS.md gains a top-level section:"
episteme ""
episteme "    ## Doc Classification Policy"
episteme "      PUBLIC: architecture / spec / contract / kernel / GTM"
episteme "      PRIVATE: operational state · positioning · decision logs"
episteme "      Default-when-uncertain: PRIVATIZE"
episteme "      4-question test · 5-step mechanism · cross-ref repair"
sleep "$PACE_BEAT"
echo

# ── Closing ────────────────────────────────────────────────────────────────
bar
title "  Symbiosis"
bar
echo
narration "  Three loops in 24 hours. Both parties caught each other's"
narration "  failure shapes. Neither failed silently."
sleep "$PACE_FAST"
echo
narration "  The protocol that resolved Round 1 is now constitutional."
narration "  The next agent on this repo reads AGENTS.md at session start"
narration "  and inherits the discipline. The lesson propagates without"
narration "  anyone needing to remember."
sleep "$PACE_BEAT"
echo
narration "  No fictional API. No contrived example. Real history,"
narration "  audit-trailed in ~/episteme-private/docs/NEXT_STEPS.md"
narration "  Events 65 / 66 / 67 — and now in AGENTS.md, where every"
narration "  future agent on this repo reads it."
sleep "$PACE_BEAT"
echo
bar
title "  episteme · 생각의 틀, posture over prompt"
bar
echo
sleep "$PACE_FAST"
