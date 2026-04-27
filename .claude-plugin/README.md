# episteme — Claude Code plugin

Installs the episteme **epistemic posture** — the Reasoning Surface protocol, named failure-mode counters, operator profile schema, and workflow loop — into Claude Code as skills, agents, and hooks.

Not a fork of the kernel. A distribution wrapper over the same markdown this repo ships.

## Install (marketplace)

```
/plugin marketplace add junjslee/episteme
/plugin install episteme@episteme
```

The marketplace manifest lives at [`./marketplace.json`](./marketplace.json); the plugin manifest at [`./plugin.json`](./plugin.json).

## Install (local / development)

```bash
claude --plugin-dir /path/to/episteme
```

## What lands in the session

- **Skills** — everything under [`skills/custom/`](../skills/custom/) and [`skills/vendor/`](../skills/vendor/), namespaced as `/episteme:<skill-name>`.
- **Agents** — personas from [`core/agents/`](../core/agents/) (`planner`, `researcher`, `implementer`, `reviewer`, `test-runner`, `docs-handoff`, `domain-architect`, `reasoning-auditor`, `governance-safety`, `orchestrator`, `domain-owner`).
- **Hooks** — safety + workflow hooks declared in [`../hooks/hooks.json`](../hooks/hooks.json); hook commands use `${CLAUDE_PLUGIN_ROOT}` so they work from any install location.

## Authority

The plugin is a delivery mechanism, not an authority. Kernel truth lives in `kernel/*.md`; operator truth lives in `core/memory/global/*.md`; project truth lives in each project's `docs/*.md`. Plugin-native memory is acceleration only.

## Verify

After install:

```bash
episteme doctor
episteme kernel verify
episteme bridge substrate verify noop
```

## Uninstall

```
/plugin uninstall episteme
```

Uninstall removes plugin-managed surfaces. Your authoritative files (`core/memory/global/*.md`, project `docs/*.md`) are untouched.

## See also

- [`../INSTALL.md`](../INSTALL.md) — the three install paths compared.
- [`../demos/03_differential/`](../demos/03_differential/) — same scenario with the posture off vs. on.
