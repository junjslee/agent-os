#!/usr/bin/env bash
# demo_strict_mode.sh — "show, don't tell" episteme Strict Mode demo.
#
# Simulates a lazy agent who writes an invalid Reasoning Surface (disconfirmation: "None")
# and then attempts a `git push`. The Episteme PreToolUse guard blocks with exit 2.
# The agent then rewrites a valid surface — execution is allowed through.
#
# Runs hermetically in a tempdir, never touches the real git remote. Designed
# to be recorded with asciinema; keep the printf cadence narrative.
#
# Usage:
#   ./scripts/demo_strict_mode.sh
#   asciinema rec -c ./scripts/demo_strict_mode.sh docs/assets/strict_mode_demo.cast

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOK="$REPO_ROOT/core/hooks/reasoning_surface_guard.py"

if [[ ! -f "$HOOK" ]]; then
  echo "fatal: hook not found at $HOOK" >&2
  exit 1
fi

# Colors degrade gracefully if output isn't a tty.
if [[ -t 1 ]]; then
  BOLD=$'\033[1m'; DIM=$'\033[2m'; RED=$'\033[31m'; GREEN=$'\033[32m'
  YELLOW=$'\033[33m'; CYAN=$'\033[36m'; RESET=$'\033[0m'
else
  BOLD=""; DIM=""; RED=""; GREEN=""; YELLOW=""; CYAN=""; RESET=""
fi

narrate() { printf '%s\n' "$1"; sleep "${DEMO_PAUSE:-1.0}"; }

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT
mkdir -p "$TMPDIR/.episteme"

printf '\n'
printf '%s===== episteme Strict Mode — live block demo =====%s\n' "$BOLD$CYAN" "$RESET"
printf '%sScenario: a lazy agent tries to `git push` with an invalid Reasoning Surface.%s\n\n' "$DIM" "$RESET"
sleep 1

# ─── Act 1: lazy surface ─────────────────────────────────────────────────────
narrate "${YELLOW}[1/3]${RESET} Agent writes reasoning-surface.json with ${RED}disconfirmation: \"None\"${RESET}"

cat > "$TMPDIR/.episteme/reasoning-surface.json" <<'JSON'
{
  "timestamp": "__TIMESTAMP__",
  "core_question": "Ship it?",
  "knowns": ["code compiles"],
  "unknowns": ["n/a"],
  "assumptions": [],
  "disconfirmation": "None"
}
JSON
# Patch in a fresh timestamp so staleness isn't the reason for the block.
NOW_ISO="$(python3 -c 'from datetime import datetime, timezone; print(datetime.now(timezone.utc).isoformat())')"
python3 -c "
import pathlib, json
p = pathlib.Path('$TMPDIR/.episteme/reasoning-surface.json')
d = json.loads(p.read_text())
d['timestamp'] = '$NOW_ISO'
p.write_text(json.dumps(d, indent=2))
"

printf '%s' "$DIM"
cat "$TMPDIR/.episteme/reasoning-surface.json"
printf '%s\n\n' "$RESET"
sleep 1

# ─── Act 2: attempt git push → block ─────────────────────────────────────────
narrate "${YELLOW}[2/3]${RESET} Agent attempts ${BOLD}\`git push origin main\`${RESET}"

PAYLOAD="$(python3 -c "
import json, sys
print(json.dumps({
  'tool_name': 'Bash',
  'tool_input': {'command': 'git push origin main'},
  'cwd': '$TMPDIR',
}))
")"

set +e
RESPONSE="$(printf '%s' "$PAYLOAD" | python3 "$HOOK" 2>&1 >/dev/null)"
EXIT_CODE=$?
set -e

if [[ "$EXIT_CODE" -eq 2 ]]; then
  printf '%s✗ BLOCKED (exit %d)%s\n' "$RED$BOLD" "$EXIT_CODE" "$RESET"
  printf '%s%s%s\n' "$DIM" "$RESPONSE" "$RESET"
else
  printf '%sunexpected exit code: %d — the guard should have blocked.%s\n' "$RED" "$EXIT_CODE" "$RESET"
  exit 1
fi
sleep 2

# ─── Act 3: fix the surface → pass ───────────────────────────────────────────
printf '\n'
narrate "${YELLOW}[3/3]${RESET} Agent rewrites a ${GREEN}valid${RESET} surface (concrete disconfirmation, substantive unknowns)"

cat > "$TMPDIR/.episteme/reasoning-surface.json" <<JSON
{
  "timestamp": "$NOW_ISO",
  "core_question": "Does the deploy preserve existing contract semantics?",
  "knowns": ["local tests pass", "staging green"],
  "unknowns": ["how the canary behaves under live-traffic shape shift"],
  "assumptions": ["feature flag is off by default"],
  "disconfirmation": "p95 latency on checkout exceeds 400ms within 10 minutes of deploy"
}
JSON

printf '%s' "$DIM"
cat "$TMPDIR/.episteme/reasoning-surface.json"
printf '%s\n\n' "$RESET"
sleep 1

narrate "Agent retries ${BOLD}\`git push origin main\`${RESET}"

set +e
printf '%s' "$PAYLOAD" | python3 "$HOOK" 2>&1 >/dev/null
EXIT_CODE=$?
set -e

if [[ "$EXIT_CODE" -eq 0 ]]; then
  printf '%s✓ ALLOWED (exit 0) — Reasoning Surface is valid%s\n' "$GREEN$BOLD" "$RESET"
else
  printf '%sunexpected exit code: %d — expected 0.%s\n' "$RED" "$EXIT_CODE" "$RESET"
  exit 1
fi

printf '\n'
printf '%s===== demo complete =====%s\n' "$BOLD$CYAN" "$RESET"
printf '%sStrict Mode blocks lazy surfaces. Valid surfaces pass through. No config needed.%s\n\n' "$DIM" "$RESET"
