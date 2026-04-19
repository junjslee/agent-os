# Install cognitive-os

Three paths, cheapest first. All three install *the same* posture — the kernel is a contract, not a fork.

---

## 1. One-line Claude Code install (recommended)

This repo is a self-contained Claude Code **plugin marketplace**. Add it, install the plugin:

```
/plugin marketplace add junjslee/cognitive-os
/plugin install cognitive-os@cognitive-os
```

What lands in your Claude Code session:

- **Skills** — every reusable skill under [`skills/custom/`](./skills/custom/) and [`skills/vendor/`](./skills/vendor/).
- **Agents** — every operator persona from [`core/agents/`](./core/agents/) (`planner`, `researcher`, `implementer`, `reviewer`, `test-runner`, `docs-handoff`, `domain-architect`, `reasoning-auditor`, `governance-safety`, `orchestrator`, `domain-owner`).
- **Safety + workflow hooks** — `block_dangerous`, `reasoning_surface_guard`, `workflow_guard`, `format`, `precompact_backup`, `quality_gate`, `session_context`. Hook paths use `${CLAUDE_PLUGIN_ROOT}` so they work from any install location.

Plugin manifest: [`.claude-plugin/plugin.json`](./.claude-plugin/plugin.json). Marketplace manifest: [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json).

Uninstall:

```
/plugin uninstall cognitive-os
/plugin marketplace remove cognitive-os
```

Your authoritative files (`core/memory/global/*.md`, project `docs/*.md`) are untouched by uninstall.

---

## 2. Full clone + CLI install (for operators who want to edit the kernel)

```bash
git clone https://github.com/junjslee/cognitive-os ~/cognitive-os
cd ~/cognitive-os
pip install -e .

cognitive-os init                          # bootstrap memory files from templates
cognitive-os setup . --interactive         # score working style + cognitive posture
cognitive-os sync                          # deliver identity to every adapter
cognitive-os doctor                        # verify wiring
```

What this gets you beyond path (1):

- The `cognitive-os` CLI (`sync`, `doctor`, `setup`, `capture`, `viewer`, `bridge substrate`, `harness`, `evolve`).
- Editable kernel (`kernel/*.md`, `core/memory/global/*.md`) — you become the author, not just the consumer.
- The local viewer (`cognitive-os viewer`) for browsing the posture's produced artifacts.

---

## 3. Dev install against a local clone

For contributors testing changes to the plugin without publishing:

```bash
git clone https://github.com/junjslee/cognitive-os ~/cognitive-os
claude --plugin-dir ~/cognitive-os
```

Equivalent to path (1) but bypasses the marketplace fetch — useful when you are modifying the skills/agents/hooks in place.

---

## Verify

After any of the three paths:

```bash
cognitive-os doctor                 # runtime wiring
cognitive-os kernel verify          # manifest integrity
cognitive-os bridge substrate verify noop  # substrate bridge contract
```

All three should exit 0.

---

## What cognitive-os actually installs

Not a tool. A posture. The four artifacts that make the posture enforceable:

| Artifact                           | What it enforces                                             |
|------------------------------------|--------------------------------------------------------------|
| `reasoning-surface.json`           | Core Question + Knowns/Unknowns/Assumptions/Disconfirmation |
| `decision-trace.md`                | Options considered, because-chain, rejection conditions     |
| `verification.md`                  | Evidence per assumption + per disconfirmation condition     |
| `handoff.md`                       | What shipped, what was pre-rejected and why                 |

Full framing: [`docs/POSTURE.md`](./docs/POSTURE.md). Differential proof: [`demos/03_differential/`](./demos/03_differential/).
