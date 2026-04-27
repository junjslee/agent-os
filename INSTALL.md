# Install episteme

Three paths, cheapest first. All three install *the same* posture — the kernel is a contract, not a fork.

---

## 1. One-line Claude Code install (recommended)

This repo is a self-contained Claude Code **plugin marketplace**. Add it, install the plugin:

```
/plugin marketplace add junjslee/episteme
/plugin install episteme@episteme
```

What lands in your Claude Code session:

- **Skills** — every reusable skill under [`skills/custom/`](./skills/custom/) and [`skills/vendor/`](./skills/vendor/).
- **Agents** — every operator persona from [`core/agents/`](./core/agents/) (`planner`, `researcher`, `implementer`, `reviewer`, `test-runner`, `docs-handoff`, `domain-architect`, `reasoning-auditor`, `governance-safety`, `orchestrator`, `domain-owner`).
- **Safety + workflow hooks** — `block_dangerous`, `reasoning_surface_guard`, `workflow_guard`, `format`, `precompact_backup`, `quality_gate`, `session_context`. Hook paths use `${CLAUDE_PLUGIN_ROOT}` so they work from any install location.

Plugin manifest: [`.claude-plugin/plugin.json`](./.claude-plugin/plugin.json). Marketplace manifest: [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json).

Uninstall:

```
/plugin uninstall episteme
/plugin marketplace remove episteme
```

Your authoritative files (`core/memory/global/*.md`, project `docs/*.md`) are untouched by uninstall.

---

## 2. Full clone + CLI install (for operators who want to edit the kernel)

```bash
git clone https://github.com/junjslee/episteme ~/episteme
cd ~/episteme
pip install -e .

episteme init                          # bootstrap memory files from templates
episteme setup . --interactive         # score working style + cognitive posture
episteme sync                          # deliver identity to every adapter
episteme doctor                        # verify wiring
```

What this gets you beyond path (1):

- The `episteme` CLI (`sync`, `doctor`, `setup`, `capture`, `viewer`, `bridge substrate`, `harness`, `evolve`).
- Editable kernel (`kernel/*.md`, `core/memory/global/*.md`) — you become the author, not just the consumer.
- The local viewer (`episteme viewer`) for browsing the posture's produced artifacts.

---

## 3. Dev install against a local clone

For contributors testing changes to the plugin without publishing:

```bash
git clone https://github.com/junjslee/episteme ~/episteme
claude --plugin-dir ~/episteme
```

Equivalent to path (1) but bypasses the marketplace fetch — useful when you are modifying the skills/agents/hooks in place.

---

## 4. First run on your repo

Install puts the kernel into your Claude Code session. It does *not* put anything into the repo you happen to be working on — that part happens the first time the session touches a high-impact op (`git push`, `npm publish`, `terraform apply`, DB migration, lockfile edit, kernel-adjacent edit) inside that repo.

Here is what to expect on a fresh repo, the first time:

1. Open Claude Code in the project directory you actually want governed.
2. Ask the agent to do a high-impact op — for example, *"push this branch to the remote."* (Do not approve any action the kernel has not yet authorized.)
3. The hook fires. Claude Code's tool execution stops with a non-zero exit. The error names the missing precondition — typically:

   ```
   REASONING SURFACE MISSING: high-impact op `git:push` requires
   .episteme/reasoning-surface.json
   Write the surface with: { core_question, knowns, unknowns,
                              assumptions, disconfirmation }
   ```

That is the kernel attaching to your project. The hook walked up from the agent's working directory looking for `.git/` or `.episteme/`, found your repo root, and refused the op because the precondition (a Reasoning Surface) was not in place.

You now have three valid responses, and the choice is per-repo.

### Strict (the production posture)

Have the agent author a Reasoning Surface — `.episteme/reasoning-surface.json` containing `core_question`, `knowns`, `unknowns`, `assumptions`, `disconfirmation`. Once it exists and validates, the next attempt at the op proceeds. The kernel stamps a `correlation_id` at PASS, the op runs, and a hash-chained record lands under `~/.episteme/framework/`. This is the default.

### Advisory (recommended for the first day on a new repo)

Opt the repo into warn-don't-block mode:

```bash
mkdir -p .episteme && touch .episteme/advisory-surface
```

The hook still fires, still emits the same diagnostic, but exits zero — the op proceeds. You watch the kernel reason out loud without it stopping you. Useful while you decide whether the discipline fits this project's cadence. Switch back to strict by removing the file: `rm .episteme/advisory-surface`.

### Off (per repo)

If you do not want governance on a particular project, simply do not create `.episteme/` in that repo. The hook will continue to refuse high-impact ops there until you choose strict or advisory; nothing else changes. The kernel does not touch repos it has not been activated against.

### What the kernel does not need from you

No per-repo `episteme init`. No `git config` change. No daemon. The plugin install is the only registration step; the per-repo signal is whatever you put (or do not put) in `.episteme/`.

After the first block (or first advisory warning), check:

```bash
ls .episteme/                  # advisory-surface OR reasoning-surface.json
ls ~/.episteme/framework/      # global hash chain — protocols.jsonl + audit/*
```

Hook exit traces appear in your Claude Code session output, not in a separate log file — the visible-evidence channel is the session itself.

For the runtime architecture — see [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md). For the differential demo (same prompt, framework off vs on) — see [`demos/03_differential/`](./demos/03_differential/).

---

## Verify

After any of the three paths:

```bash
episteme doctor                 # runtime wiring
episteme kernel verify          # manifest integrity
episteme bridge substrate verify noop  # substrate bridge contract
```

All three should exit 0.

---

## What episteme actually installs

Not a tool. A posture. The four artifacts that make the posture enforceable:

| Artifact                           | What it enforces                                             |
|------------------------------------|--------------------------------------------------------------|
| `reasoning-surface.json`           | Core Question + Knowns/Unknowns/Assumptions/Disconfirmation |
| `decision-trace.md`                | Options considered, because-chain, rejection conditions     |
| `verification.md`                  | Evidence per assumption + per disconfirmation condition     |
| `handoff.md`                       | What shipped, what was pre-rejected and why                 |

Differential proof: [`demos/03_differential/`](./demos/03_differential/).
