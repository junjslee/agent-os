---
name: worktree-split
description: Decompose parallelizable work into bounded branches and create safe git worktrees.
---
Use this skill when a task naturally splits into independent tracks.

Steps:
1. Identify bounded subtasks with low file overlap.
2. Propose one worktree per subtask.
3. Use `episteme worktree <type> <task>` for approved branches.
4. Keep review and merge separate from implementation.

Avoid parallel worktrees when the changes are tightly coupled.
