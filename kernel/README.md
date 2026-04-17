# The Cognitive Kernel

The canonical specification of cognitive-os.

Pure markdown. No code. No tooling. Nothing vendor-specific.

The kernel defines **how an agent should think** — before any platform,
framework, or adapter gets involved. Everything else in this repository
(the CLI, the hooks, the adapters, the skills) exists to deliver this
kernel into a specific runtime.

If the kernel is sound, the adapters are small. If an adapter starts
growing, the fix is in the kernel's portability, not in more adapter code.

---

## Files

- **[CONSTITUTION.md](./CONSTITUTION.md)** — the north-star document.
  Root claim, failure modes being addressed, the four principles, and what
  follows from them.

- **[REASONING_SURFACE.md](./REASONING_SURFACE.md)** — the operational
  protocol that operationalizes Principle I (Explicit > Implicit). The
  minimum viable explicitness required before any consequential action.

- **[FAILURE_MODES.md](./FAILURE_MODES.md)** — the six failure modes the
  kernel is built against, mapped to the specific artifact that counters
  each one.

- **[OPERATOR_PROFILE_SCHEMA.md](./OPERATOR_PROFILE_SCHEMA.md)** — the
  schema for encoding an operator's cognitive preferences so they travel
  with the agent across tools and sessions.

- **[REFERENCES.md](./REFERENCES.md)** — external sources that informed
  the kernel's contents. The kernel body does not import jargon from these
  sources; concepts are described in the kernel's own vocabulary. This
  file is the attribution trail for readers who want to go deeper.

---

## How the kernel is delivered

An adapter is a thin shim that injects kernel files into a runtime's
native context-loading mechanism:

- Claude Code: concatenated into `CLAUDE.md` or referenced from global
  memory.
- Hermes: mounted as `OPERATOR.md`.
- Any future runtime: same files, different destination.

The kernel does not care which runtime loads it. The runtime does not
know what the kernel contains. That decoupling is the point.

---

## What lives here vs. elsewhere

- **kernel/** — portable spec. Markdown only. Vendor-neutral.
- **adapters/** — per-runtime delivery. Should be tiny (<100 LOC each).
- **core/memory/global/** — the *author's* personal instance of the
  operator profile, using the schema defined here.
- **docs/** — project-level documentation about the system itself
  (architecture notes, contract docs, PRDs). Not kernel.
