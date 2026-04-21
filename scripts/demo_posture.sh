#!/usr/bin/env bash
# demo_posture.sh — posture as thinking (not just blocking).
#
# Cinematic differential. Same PM prompt as demos/03_differential/, walked
# through in four narrated beats so the viewer sees the posture in motion
# rather than reading markdown artifacts in a folder.
#
#   Beat 1  The prompt — a real ask, posed by a PM to an engineer.
#   Beat 2  Doxa vs episteme — fluent default vs the Reasoning Surface
#           authored field-by-field, each field answering (a) what is
#           shown, (b) why load-bearing, (c) what failure mode it counters.
#   Beat 3  The specificity ladder — three disconfirmations validated
#           live against the real Reasoning-Surface Guard: the shallowest
#           blocks; the fluent-vacuous one passes the hot path (honest
#           kernel limit); the concrete falsifiable one is the posture.
#   Beat 4  The memory loop closes it — what phase 11 promotion emits,
#           and what phase 12 (pending) audits.
#
# Runs hermetically in a tempdir. Sets HOME to the tempdir so the real
# ~/.episteme/state/ and ~/.episteme/telemetry/ are untouched.
#
# Recording:
#   asciinema rec -c ./scripts/demo_posture.sh docs/assets/posture_demo.cast
#   agg docs/assets/posture_demo.cast docs/assets/posture_demo.gif \
#     --cols 100 --rows 36 --font-size 15 --theme monokai

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GUARD="$REPO_ROOT/core/hooks/reasoning_surface_guard.py"

if [[ ! -f "$GUARD" ]]; then
  printf 'fatal: guard hook not found at %s\n' "$GUARD" >&2
  exit 1
fi

# Colors degrade gracefully if output isn't a tty.
#
# DIM_RED is the visual demote on Beat 3's BLOCK rung — the script's
# narration calls BLOCK "the shallowest thing the kernel does", so the
# color must match the philosophical hierarchy. Bright red on an exit-2
# was the visual climax of the GIF, which inverted the intended
# climax (the Reasoning Surface itself). BRIGHT_GREEN is the climax
# color for the falsifiable PASS rung — the actual posture.
if [[ -t 1 ]]; then
  BOLD=$'\033[1m'; DIM=$'\033[2m'
  RED=$'\033[31m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'
  BLUE=$'\033[34m'; MAGENTA=$'\033[35m'; CYAN=$'\033[36m'
  GREY=$'\033[90m'; RESET=$'\033[0m'
  DIM_RED=$'\033[2;31m'; BRIGHT_GREEN=$'\033[1;92m'
else
  BOLD=""; DIM=""; RED=""; GREEN=""; YELLOW=""; BLUE=""; MAGENTA=""; CYAN=""; GREY=""; RESET=""
  DIM_RED=""; BRIGHT_GREEN=""
fi

pause()   { sleep "${DEMO_PAUSE:-0.8}"; }
hold()    { sleep "${DEMO_HOLD:-1.6}"; }
narrate() { printf '%s\n' "$1"; pause; }

# Hermetic runtime: fake HOME so the real state/telemetry stay clean.
TMPDIR_DEMO="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_DEMO"' EXIT
export HOME="$TMPDIR_DEMO"
PROJECT="$TMPDIR_DEMO/proj"
mkdir -p "$PROJECT/.episteme"

NOW_ISO="$(python3 -c 'from datetime import datetime, timezone; print(datetime.now(timezone.utc).isoformat())')"

# -----------------------------------------------------------------------------
# BEAT 0 — TITLE CARD  (the cognitive thesis, frozen for the GIF thumbnail)
# -----------------------------------------------------------------------------
#
# Anchors the GIF's first-frame impression on the Reasoning Surface
# formulation. The auto-playing thumbnail used to land on Beat 3's
# bright-red BLOCK; now it lands here. The card holds for ~2.2 seconds —
# long enough to read, short enough not to feel like marketing.
printf '\n'
printf '%s┌──────────────────────────────────────────────────────────────────────────────┐%s\n' "$BOLD$CYAN" "$RESET"
printf '%s│%s                                                                              %s│%s\n' "$BOLD$CYAN" "$RESET" "$BOLD$CYAN" "$RESET"
printf '%s│%s    %sepisteme%s — the rigorous formulation of a Reasoning Surface              %s│%s\n' "$BOLD$CYAN" "$RESET" "$BOLD" "$RESET" "$BOLD$CYAN" "$RESET"
printf '%s│%s                                                                              %s│%s\n' "$BOLD$CYAN" "$RESET" "$BOLD$CYAN" "$RESET"
printf '%s│%s    %sCore Question%s · what is this work actually trying to answer            %s│%s\n' "$BOLD$CYAN" "$RESET" "$DIM" "$RESET" "$BOLD$CYAN" "$RESET"
printf '%s│%s    %sUnknowns%s      · classifiable failure modes, named before the work       %s│%s\n' "$BOLD$CYAN" "$RESET" "$DIM" "$RESET" "$BOLD$CYAN" "$RESET"
printf '%s│%s    %sDisconfirmation%s · the falsifiable pivot, pre-committed                 %s│%s\n' "$BOLD$CYAN" "$RESET" "$DIM" "$RESET" "$BOLD$CYAN" "$RESET"
printf '%s│%s                                                                              %s│%s\n' "$BOLD$CYAN" "$RESET" "$BOLD$CYAN" "$RESET"
printf '%s└──────────────────────────────────────────────────────────────────────────────┘%s\n\n' "$BOLD$CYAN" "$RESET"
sleep "${DEMO_TITLE_HOLD:-2.2}"

# -----------------------------------------------------------------------------
# OPEN
# -----------------------------------------------------------------------------
printf '%s════════  episteme  —  posture as thinking  ════════%s\n' "$BOLD$CYAN" "$RESET"
printf '%sFour beats: the prompt · doxa vs episteme · the specificity ladder · the memory loop.%s\n\n' "$DIM" "$RESET"
sleep 1

# =============================================================================
# BEAT 1 — THE PROMPT
# =============================================================================
printf '%s───  BEAT 1  ·  THE PROMPT  ───%s\n\n' "$BOLD$BLUE" "$RESET"
narrate "${DIM}A real PM ask, posed to a product engineer (demos/03_differential/prompt.md):${RESET}"
printf '\n'
printf '  %s┌──────────────────────────────────────────────────────────────────────────────┐%s\n' "$GREY" "$RESET"
printf '  %s│%s  %sFrom:%s Priya (PM)   %sTo:%s Jun (Eng)                                              %s│%s\n' "$GREY" "$RESET" "$BOLD" "$RESET" "$BOLD" "$RESET" "$GREY" "$RESET"
printf '  %s│%s  %sSubject:%s Semantic search on the KB — can we scope?                         %s│%s\n' "$GREY" "$RESET" "$BOLD" "$RESET" "$GREY" "$RESET"
printf '  %s├──────────────────────────────────────────────────────────────────────────────┤%s\n' "$GREY" "$RESET"
printf '  %s│%s  Customers cannot find stuff. I think semantic search is the answer — we   %s│%s\n' "$GREY" "$RESET" "$GREY" "$RESET"
printf '  %s│%s  should embed the KB and use vector similarity. Can you scope a 2-sprint    %s│%s\n' "$GREY" "$RESET" "$GREY" "$RESET"
printf '  %s│%s  build for Q3? Ship before the trade show (~6 weeks out). What do you       %s│%s\n' "$GREY" "$RESET" "$GREY" "$RESET"
printf '  %s│%s  need from me?                                                              %s│%s\n' "$GREY" "$RESET" "$GREY" "$RESET"
printf '  %s└──────────────────────────────────────────────────────────────────────────────┘%s\n\n' "$GREY" "$RESET"
hold

# =============================================================================
# BEAT 2 — DOXA vs EPISTEME
# =============================================================================
printf '%s───  BEAT 2  ·  DOXA  vs  EPISTEME  ───%s\n\n' "$BOLD$MAGENTA" "$RESET"

# --- DOXA -------------------------------------------------------------------
printf '%s▐ DOXA · posture off · fluent default%s\n\n' "$BOLD$RED" "$RESET"
narrate "${DIM}The engineer answers the question as asked. Specific. Actionable. Wrong.${RESET}"
printf '\n'
printf '  %s> pgvector on Postgres; embed with text-embedding-3-small.%s\n' "$GREY" "$RESET"
printf '  %s> Backfill ~4,200 articles. Wire /search with cosine top-10.%s\n' "$GREY" "$RESET"
printf '  %s> 50/50 A/B, feature flag ramp. CTR as primary metric.%s\n' "$GREY" "$RESET"
printf '  %s> Should work before the trade show. Kicking off Monday.%s\n\n' "$GREY" "$RESET"

printf '  %sFailure modes exhibited (five of nine, from kernel/FAILURE_MODES.md):%s\n' "$BOLD" "$RESET"
printf '   %s02%s %sQuestion substitution%s  %s(a)%s scope produced   %s(b)%s real q: "should we build"   %s(c)%s needs Core Question\n' "$RED" "$RESET" "$BOLD" "$RESET" "$YELLOW" "$RESET" "$YELLOW" "$RESET" "$YELLOW" "$RESET"
printf '   %s01%s %sWYSIATI%s                %s(a)%s accepts "cannot find" as diagnosis   %s(c)%s needs Unknowns field\n' "$RED" "$RESET" "$BOLD" "$RESET" "$YELLOW" "$RESET" "$YELLOW" "$RESET"
printf '   %s03%s %sAnchoring%s              %s(a)%s "semantic" in prompt anchored plan   %s(c)%s needs Disconfirmation\n' "$RED" "$RESET" "$BOLD" "$RESET" "$YELLOW" "$RESET" "$YELLOW" "$RESET"
printf '   %s05%s %sPlanning fallacy%s       %s(a)%s no eval, no rollback cost, no ops   %s(c)%s inversion + margin of safety\n' "$RED" "$RESET" "$BOLD" "$RESET" "$YELLOW" "$RESET" "$YELLOW" "$RESET"
printf '   %s06%s %sOverconfidence%s         %s(a)%s no pre-stated pivot condition       %s(c)%s Disconfirmation field\n\n' "$RED" "$RESET" "$BOLD" "$RESET" "$YELLOW" "$RESET" "$YELLOW" "$RESET"
hold

# --- EPISTEME ---------------------------------------------------------------
printf '%s▐ EPISTEME · posture on · Reasoning Surface authored field-by-field%s\n\n' "$BOLD$CYAN" "$RESET"

narrate "${DIM}Same prompt. The posture refuses to answer the asked question until it reframes it.${RESET}"
printf '\n'

printf '  %sCore Question (reframed — not the PM question):%s\n' "$BOLD" "$RESET"
printf '  %s"Do we have evidence that keyword search is the load-bearing failure,%s\n' "$CYAN" "$RESET"
printf '  %s before committing 2 sprints to semantic search?"%s\n' "$CYAN" "$RESET"
printf '   %s(a)%s reframes the question            %s(b)%s fluent answer answered the wrong one\n' "$YELLOW" "$RESET" "$YELLOW" "$RESET"
printf '   %s(c)%s counters 02 Question substitution\n\n' "$YELLOW" "$RESET"
pause

printf '  %sUnknowns (classifiable, not hand-wavy):%s\n' "$BOLD" "$RESET"
printf '  %s · What %% of failed searches are typos vs stop-word vs content-missing%s\n' "$CYAN" "$RESET"
printf '  %s   vs discoverability-external vs genuine semantic gap?%s\n' "$CYAN" "$RESET"
printf '  %s · Base rate: does BM25 actually lose to vectors at this scale/domain?%s\n' "$CYAN" "$RESET"
printf '  %s · Current false-negative rate on a labelled gold set? (no gold set exists)%s\n' "$CYAN" "$RESET"
printf '   %s(a)%s five distinct failure modes       %s(b)%s the fluent response lumped them as one\n' "$YELLOW" "$RESET" "$YELLOW" "$RESET"
printf '   %s(c)%s counters 01 WYSIATI\n\n' "$YELLOW" "$RESET"
pause

printf '  %sDisconfirmation (pre-committed pivot condition):%s\n' "$BOLD" "$RESET"
printf '  %s"If query-log analysis shows over 50%% of failed searches are true%s\n' "$CYAN" "$RESET"
printf '  %s semantic gaps, the semantic hypothesis survives and we build.%s\n' "$CYAN" "$RESET"
printf '  %s If under 30%%, we do not."%s\n' "$CYAN" "$RESET"
printf '   %s(a)%s pivot named before the work      %s(b)%s makes the plan falsifiable\n' "$YELLOW" "$RESET" "$YELLOW" "$RESET"
printf '   %s(c)%s counters 03 Anchoring + 06 Overconfidence\n\n' "$YELLOW" "$RESET"
hold

# =============================================================================
# BEAT 3 — THE SPECIFICITY LADDER
# =============================================================================
printf '%s───  BEAT 3  ·  THE SPECIFICITY LADDER  ───%s\n\n' "$BOLD$YELLOW" "$RESET"
narrate "${DIM}Three disconfirmations, validated live against the Reasoning-Surface Guard.${RESET}"
narrate "${DIM}The kernel catches the first. It does not catch the second. This is the kernel limit.${RESET}"
printf '\n'

PAYLOAD_PUSH="$(python3 -c "
import json
print(json.dumps({
  'tool_name': 'Bash',
  'tool_input': {'command': 'git push origin main'},
  'cwd': '$PROJECT',
}))
")"

_rung () {
  local disco="$1"
  local label="$2"
  local expect="$3"   # 'block' | 'pass'
  local color="$4"
  local note="$5"

  python3 - "$PROJECT" "$NOW_ISO" "$disco" <<'PY'
import json, sys, pathlib
project, now_iso, disco = sys.argv[1], sys.argv[2], sys.argv[3]
surface = {
    "timestamp": now_iso,
    "core_question": "Should we push this change to main?",
    "knowns": ["tests pass on the feature branch", "one reviewer approved"],
    "unknowns": ["whether any regressions exist in rarely-hit code paths"],
    "assumptions": ["the review caught the load-bearing risks"],
    "disconfirmation": disco,
}
pathlib.Path(project, ".episteme", "reasoning-surface.json").write_text(json.dumps(surface, indent=2))
PY

  set +e
  local response
  response="$(printf '%s' "$PAYLOAD_PUSH" | python3 "$GUARD" 2>&1 >/dev/null)"
  local rc=$?
  set -e

  printf '  %s┌─ %s%s%s\n' "$GREY" "$BOLD" "$label" "$RESET"
  printf '  %s│%s  disconfirmation: %s"%s"%s\n' "$GREY" "$RESET" "$color" "$disco" "$RESET"
  if [[ $rc -eq 0 ]]; then
    # Visual hierarchy matches the philosophical hierarchy: a falsifiable
    # PASS is the climax (BRIGHT_GREEN); the fluent-vacuous PASS is the
    # honest kernel limit (yellow note, no special pass color); a BLOCK
    # is the shallowest thing the kernel does (DIM_RED, demoted from
    # the previous bright-red exit-code climax).
    if [[ "$color" == "$GREEN" ]]; then
      printf '  %s│%s  result:          %sPASS%s (exit 0)   %s%s%s\n' "$GREY" "$RESET" "$BRIGHT_GREEN" "$RESET" "$DIM" "$note" "$RESET"
    else
      printf '  %s│%s  result:          %sPASS%s (exit 0)   %s%s%s\n' "$GREY" "$RESET" "$GREEN" "$RESET" "$DIM" "$note" "$RESET"
    fi
  else
    printf '  %s│%s  result:          %sBLOCK%s (exit %d)   %s%s%s\n' "$GREY" "$RESET" "$DIM_RED" "$RESET" "$rc" "$DIM" "$note" "$RESET"
    if [[ -n "$response" ]]; then
      printf '  %s│%s  %s%s%s\n' "$GREY" "$RESET" "$DIM" "$(printf '%s' "$response" | head -n 1)" "$RESET"
    fi
  fi
  printf '  %s└─%s\n\n' "$GREY" "$RESET"

  if [[ "$expect" == "block" && $rc -eq 0 ]]; then
    printf '  %sFAIL: expected BLOCK, got PASS%s\n' "$RED" "$RESET"
    exit 1
  fi
  if [[ "$expect" == "pass" && $rc -ne 0 ]]; then
    printf '  %sFAIL: expected PASS, got BLOCK (exit %d)%s\n' "$RED" "$rc" "$RESET"
    exit 1
  fi
  pause
}

_rung 'None' \
      '1. Placeholder token  (shallowest thing the kernel does)' \
      'block' \
      "$RED" \
      '— validator catches the lazy token'

_rung 'the system could have bugs we did not find' \
      '2. Fluent-vacuous     (43 chars, passes the hot path)' \
      'pass' \
      "$YELLOW" \
      '— the honest kernel limit: structural pass, semantic emptiness'

_rung 'if canary p95 latency on checkout exceeds 400ms within 10 minutes of deploy, roll back' \
      '3. Concrete, falsifiable, pre-committed pivot   (what the posture is)' \
      'pass' \
      "$GREEN" \
      '— passes because it names the condition under which it abandons itself'

printf '  %sStructural discipline in the hot path;  semantic quality over time.%s\n\n' "$BOLD$CYAN" "$RESET"
hold

# =============================================================================
# BEAT 4 — THE MEMORY LOOP CLOSES IT
# =============================================================================
printf '%s───  BEAT 4  ·  THE MEMORY LOOP CLOSES IT  ───%s\n\n' "$BOLD$GREEN" "$RESET"
narrate "${DIM}The fluent-vacuous surface (#2) is not caught at write. It is caught over time.${RESET}"
narrate "${DIM}Phase 10 logs every high-impact action paired with its surface. Phase 11 promotes.${RESET}"
printf '\n'

printf '  %s$ episteme memory promote --dry-run%s\n' "$DIM" "$RESET"
printf '  %s────────────────────────────────────────────────────────────%s\n' "$GREY" "$RESET"
printf '  %sproposal_id%s    : %sbc4f2e71%s   (deterministic · hash of signature + evidence refs)\n' "$BOLD" "$RESET" "$CYAN" "$RESET"
printf '  %scluster%s        : (git-push, invariant-disconfirmation)\n' "$BOLD" "$RESET"
printf '  %sevidence%s       : 14 episodic records across 6 days\n' "$BOLD" "$RESET"
printf '  %sfire rate%s      : %s0 / 14%s  (disconfirmation condition never observed)\n' "$BOLD" "$RESET" "$YELLOW" "$RESET"
printf '  %ssignal%s         : %sclaim fluent, outcome invariant%s  — measure-as-target drift\n' "$BOLD" "$RESET" "$YELLOW" "$RESET"
printf '  %srecommendation%s : re-elicit disconfirmation specificity for this command class\n' "$BOLD" "$RESET"
printf '  %sstatus%s         : proposal  (human review required before acceptance)\n' "$BOLD" "$RESET"
printf '  %s────────────────────────────────────────────────────────────%s\n\n' "$GREY" "$RESET"
hold

printf '  %sPhase 11 ships this promotion job.%s\n' "$DIM" "$RESET"
printf '  %sPhase 12 (pending) closes the loop:%s\n' "$DIM" "$RESET"
printf '  %s   compares claimed profile axes  ⇄  episodic praxis;%s\n' "$DIM" "$RESET"
printf '  %s   flags drift as re-elicitation at SessionStart;%s\n' "$DIM" "$RESET"
printf '  %s   episteme auditing praxis to detect axes that have drifted into doxa.%s\n\n' "$DIM" "$RESET"
hold

# =============================================================================
# CLOSE
# =============================================================================
printf '%s════════  end of demo  ════════%s\n' "$BOLD$CYAN" "$RESET"
printf '%sProse counterpart: docs/NARRATIVE.md%s\n' "$DIM" "$RESET"
printf '%sEnforcement-of-the-surface demo: scripts/demo_strict_mode.sh  (see docs/DEMOS.md)%s\n' "$DIM" "$RESET"
printf '%sFull differential artifacts: demos/03_differential/%s\n\n' "$DIM" "$RESET"
