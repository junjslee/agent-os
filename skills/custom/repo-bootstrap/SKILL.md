---
name: repo-bootstrap
description: Bootstrap a repository with the standard episteme scaffold and verify the core memory files exist.
---
Use this skill when a repository is missing the standard operating scaffold.

Steps:
1. Inspect whether `AGENTS.md`, `CLAUDE.md`, and `docs/*.md` already exist.
2. If the scaffold is missing, run `episteme bootstrap` from the repo root.
3. Confirm the required memory files now exist.
4. Summarize what was created and what was preserved.

Do not overwrite substantive existing project docs unless explicitly asked.
