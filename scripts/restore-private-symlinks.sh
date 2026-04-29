#!/usr/bin/env bash
# scripts/restore-private-symlinks.sh
#
# Restore the gitignored canonical-path symlinks that point to
# ~/episteme-private/. After a branch switch or fresh clone, these
# symlinks get wiped because they live at gitignored paths and aren't
# part of git history. Run this script to recreate them from the
# privatize-list embedded below.
#
# Idempotent: skips symlinks that already point at the correct target.
# Reports: restored / already-correct / missing-private counts.
# Exit codes:
#   0 - all 18 symlinks restored or already correct
#   1 - $HOME/episteme-private/ does not exist (cannot restore anything)
#   2 - some private targets are missing (partial success)
#
# CP-SYMLINK-RESTORE-01 Part A (Event 76, v1.0.1 polish).
# Part B — SessionStart hook integration in core/hooks/session_context.py
# that auto-detects + auto-runs this script — is deferred to a later Event.
#
# Sources of truth for the path list:
#   .gitignore § "Privatized strategic forward-vision docs (Event 65)"
#   .gitignore § "Privatized Tier 1 + Tier 2 docs (Event 66)"
#   .gitignore § "Privatized operator-profile canonicals (Event 71)"
# If any future Event privatizes more files, append them below in the
# matching section.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PRIVATE_ROOT="$HOME/episteme-private"
cd "$REPO_ROOT"

if [[ ! -d "$PRIVATE_ROOT" ]]; then
  echo "Error: $PRIVATE_ROOT does not exist." >&2
  echo "       Symlinks cannot be restored without the private staging directory." >&2
  echo "       This script is intended for the maintainer's machine; fork users" >&2
  echo "       seed clean templates from core/memory/global/examples/ via 'episteme init'." >&2
  exit 1
fi

# Canonical paths from .gitignore privatize sections. Mirror the privatize
# list — keep in sync if a future Event privatizes more files.
PATHS=(
  # Event 65 — forward-vision strategic docs (4)
  docs/DESIGN_V1_1_REASONING_ENGINE.md
  docs/ROADMAP_POST_V1.md
  docs/POST_SOAK_MIGRATION_PLAN.md
  docs/POST_SOAK_TRIAGE.md
  # Event 66 — Tier 1 + Tier 2 docs (10)
  docs/NEXT_STEPS.md
  docs/PLAN.md
  docs/PROGRESS.md
  docs/DEFERRED_DISCOVERIES_TRIAGE.md
  docs/DISCRIMINATOR_CALIBRATION.md
  docs/PREPARED_PATCHES.md
  docs/POSTURE.md
  docs/NARRATIVE.md
  docs/COGNITIVE_SYSTEM_PLAYBOOK.md
  docs/DECISION_STORY.md
  # Event 71 — operator-profile canonicals (4)
  core/memory/global/operator_profile.md
  core/memory/global/cognitive_profile.md
  core/memory/global/workflow_policy.md
  core/memory/global/agent_feedback.md
)

restored=0
already=0
missing=0

for canonical in "${PATHS[@]}"; do
  private_path="$PRIVATE_ROOT/$canonical"

  # Verify private target exists; skip cleanly if missing
  if [[ ! -f "$private_path" ]]; then
    echo "[MISS] private target absent: $private_path" >&2
    missing=$((missing + 1))
    continue
  fi

  # Compute the relative-target prefix based on canonical's depth from
  # $HOME. We need to step out of the canonical's parent directory all
  # the way up to $HOME, then descend into ~/episteme-private/. Pattern:
  #   docs/<file>               (depth 2 from $HOME) -> ../../episteme-private/docs/<file>
  #   core/memory/global/<file> (depth 4 from $HOME) -> ../../../../episteme-private/core/memory/global/<file>
  case "$canonical" in
    docs/*)               prefix="../.." ;;
    core/memory/global/*) prefix="../../../.." ;;
    *)
      echo "[SKIP] unknown canonical path prefix: $canonical (script needs an update)" >&2
      continue
      ;;
  esac
  relative_target="$prefix/episteme-private/$canonical"

  # If symlink already points at the correct target, skip
  if [[ -L "$canonical" ]]; then
    current="$(readlink "$canonical")"
    if [[ "$current" == "$relative_target" ]]; then
      already=$((already + 1))
      continue
    fi
  fi

  # Defensive: ensure parent dir exists (should always be true post-clone)
  mkdir -p "$(dirname "$canonical")"

  # Create or refresh the symlink
  ln -sf "$relative_target" "$canonical"
  echo "[OK]   $canonical -> $relative_target"
  restored=$((restored + 1))
done

total=${#PATHS[@]}
echo ""
echo "Summary: restored=$restored, already-correct=$already, missing-private=$missing (of $total)"

if [[ $missing -gt 0 ]]; then
  exit 2
fi
exit 0
