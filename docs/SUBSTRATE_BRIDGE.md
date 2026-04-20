# Substrate Bridge — A Generalizable Contract for External Memory Systems

The kernel speaks exactly one format: `memory-contract-v1` envelopes. Every external memory system — mem0, Memori, MemOS, claude-mem, a vector DB, a filesystem tree, an MCP server, a future substrate we haven't heard of yet — integrates through the same adapter protocol. No substrate becomes authoritative; they are caches with **declared capabilities** and **declared lossy fields**.

This doc defines the contract. Adapter implementations live in `src/episteme/bridges/substrate/adapters/` — drop one file to add a new substrate.

---

## Operational summary

```
memory-contract-v1 envelope
        │
        ▼
   SubstrateAdapter.push(envelope, scope)   ──►  external system (mem0/Memori/…)
   SubstrateAdapter.pull(query)             ◄──  external system
        │
        ▼
memory-contract-v1 envelope
```

Every adapter declares: (1) `name`, (2) `capabilities` (push/pull/delete/search/…), (3) `scope_keys` it honors natively, (4) `lossy_fields` it cannot preserve. Records the adapter cannot honor must appear in `PushResult.skipped` with a reason. **Silent drops are a contract violation.**

---

## CLI surface

```bash
episteme bridge substrate list-adapters
episteme bridge substrate describe <adapter>
episteme bridge substrate verify <adapter>

episteme bridge substrate push <adapter> \
  --input <envelope.json> \
  [--user-id … --project-id … --agent-id … --session-id …] \
  [--config <adapter-config.json>] \
  [--output <push-result.json>]

episteme bridge substrate pull <adapter> \
  [--query "free-text"] [--limit 50] [--since 2026-01-01T00:00:00Z] \
  [--user-id … --project-id …] \
  [--config <adapter-config.json>] \
  [--output <envelope.json>]
```

Every command emits schema-validated JSON. `push` exits non-zero if any record fails; `skipped` does not fail the command (skipped is a contractual outcome).

---

## The adapter protocol

```python
class SubstrateAdapter(ABC):
    name: str                                 # unique id, e.g. "mem0", "memori", "noop"

    def describe(self) -> AdapterDescriptor:
        """Self-description validated against substrate-v1/adapter_descriptor schema."""

    def push(self, envelope, scope) -> PushResult:
        """Push a memory-contract-v1 envelope. Records the substrate cannot honor
        land in PushResult.skipped with a reason — never silently dropped."""

    def pull(self, query) -> dict:
        """Pull from substrate, emit a memory-contract-v1 envelope. Default: unsupported."""

    def delete(self, substrate_id) -> bool:
        """Delete one record by substrate-native id. Default: unsupported."""
```

`ScopeMap` is a neutral set of optional keys: `user_id`, `project_id`, `agent_id`, `session_id`, `run_id`, `app_id`, `org_id`. Adapters declare which they honor natively; keys they don't honor are stored in substrate-side metadata (when possible), not used for filtering.

---

## Schemas (the stable surface)

| File                                                      | Defines                                          |
|-----------------------------------------------------------|--------------------------------------------------|
| `core/schemas/substrate/adapter_descriptor.schema.json`   | What every adapter must declare about itself    |
| `core/schemas/substrate/pull_query.schema.json`           | Pull query shape                                |
| `core/schemas/substrate/push_result.schema.json`          | Push result shape                               |
| `core/schemas/memory-contract/memory_envelope.json`       | The envelope format every adapter speaks        |

`contract_version` is pinned to `"substrate-v1"`. Breaking changes bump the major number and require a new schema file.

---

## Bundled adapters

| Adapter   | Substrate          | Transport   | Push | Pull | Search | Notes                                                                    |
|-----------|--------------------|-------------|------|------|--------|--------------------------------------------------------------------------|
| `noop`    | local filesystem   | filesystem  | ✅   | ✅   | ❌     | Zero deps. Reference implementation. Preserves full record losslessly.   |
| `mem0`    | mem0 cloud         | REST        | ✅   | ✅   | ✅     | Requires `MEM0_API_KEY`. Requires `scope.user_id`. Lossy on provenance.   |
| `memori`  | Memori SDK         | SDK         | ✅   | ❌   | ✅     | Requires `pip install memori`. Maps user→entity, agent→process.           |

### What "lossy" means

An adapter is lossy on a field if the substrate cannot store it losslessly. The mem0 adapter, for example, declares `provenance.captured_by`, `provenance.confidence`, `provenance.evidence_refs`, and `status` as lossy — these are sent in `metadata` but mem0 doesn't use them for ranking or retrieval. The operator sees this in the descriptor *before* pushing, not after facts are lost.

---

## Invariants (the kernel rules that bridges must preserve)

1. **Authority stays in the kernel.** No substrate becomes authoritative. Promotion from runtime/substrate to authoritative lives in Evolution Contract v1, not in the bridge.
2. **`global` memory is never routed to substrates.** Global memory is stable operator identity; replicating it into a cloud substrate creates a drift surface. Adapters must `skip` records with `memory_class == "global"` and report the reason.
3. **Provenance is sacred when the substrate supports it.** An adapter that lies about `preserve_provenance: true` while dropping fields fails `verify`.
4. **Skipped ≠ failed.** Skipped is a contractual outcome (substrate cannot honor this record). Failed is an error (the operation broke). They are reported separately.
5. **Scope is declarative.** Adapters must not synthesize missing scope keys. If `mem0` requires `user_id` and it's missing, `push` returns failed with an explicit message — it does not invent `"anonymous"`.

---

## Writing a new adapter

1. Create `src/episteme/bridges/substrate/adapters/<name>.py`.
2. Subclass `SubstrateAdapter`. Implement `describe`, `push`, and (optionally) `pull`/`delete`.
3. Export `ADAPTER = YourAdapter` at module level.
4. `episteme bridge substrate list-adapters` should now show `<name>`.
5. Run `episteme bridge substrate verify <name>` to validate the descriptor.

The `noop` adapter in the same directory is the canonical minimal example.

---

## Why this shape

Every memory-system repo in 2026 (mem0, Memori, MemOS, claude-mem) has converged on roughly the same primitives: `add(content, scope, metadata)` → `search(query, filters)` → `list` → `delete`. The differences are in ranking quality, storage backend, and dashboard UX — not in the API surface. The adapter protocol is the **least common multiple** of those substrates, expressed as a self-describing plugin so the kernel doesn't need to care which substrate is on the other side.

This is the same move the kernel makes elsewhere: declare the contract, let capability-declarations route around substrate gaps. The bridge does not pretend every substrate is equivalent — it makes the differences visible.

---

## See also

- `docs/MEMORY_CONTRACT.md` — the envelope format substrates receive and emit.
- `docs/SYNC_AND_MEMORY.md` — where substrates fit in the coexistence model.
- `kernel/KERNEL_LIMITS.md` — why no substrate can replace authoritative project docs.
