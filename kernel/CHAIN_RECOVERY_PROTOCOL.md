# Chain Recovery Protocol

**Operational summary** (load first if you have a token budget):

- Pillar 2 (append-only hash chain) is tamper-evident; this document is the recovery contract for the cases where the chain breaks legitimately.
- Three recovery modes: **reset** (full rewind with attestation), **selective** (partial-corruption windowed-rebuild), **migrate** (forward-walk across schema versions).
- Every recovery is itself a chain-anchored event. The recovery-attestation envelope is the genesis record of the rewound / migrated chain; provenance is preserved across the discontinuity.
- CLI: `episteme chain recover --mode={reset,selective,migrate} --stream <name> --reason "..." --confirm "..."`.
- v1.1 first slice (Event 80 / CP-CHAIN-RECOVERY-PROTOCOL-01): **reset mode is functional**; selective + migrate are documented + reserved-via-stub. Selective requires CP-CHAIN-RECOVERY-PROTOCOL component 5; migrate requires CP-TEMPORAL-INTEGRITY-EXPANSION-01 first.

---

## What this is

[Pillar 2](./CONSTITUTION.md) makes the kernel's audit substrate tamper-evident: every reasoning surface, blueprint firing, protocol synthesis, and deferred discovery is anchored in a SHA-256 hash-chained record (envelope schema in [`core/hooks/_chain.py`](../core/hooks/_chain.py)). The chain is closed-by-design against mid-chain mutation — `verify_chain` reports the first break-index; downstream readers stop trusting at-or-after a break.

But chains break legitimately. Disk corruption. Schema migration. `rm -rf ~/.episteme/`. Multi-machine forks. Adversarial tampering caught after the fact. The kernel must survive these without losing the discipline that made the chain credible in the first place.

This document is the recovery contract. It enumerates the legitimate break scenarios, names the recovery mode for each, defines the attestation envelope schema, and bounds what recovery does and does not preserve.

---

## Critical-gap scenarios

The kernel's value-proposition assumes operators can recover from chain breakage without abandoning the audit trail. The five scenarios below are the load-bearing cases.

### Scenario 1 · Disk corruption breaks chain integrity mid-stream

A bit-flip, partial write, or ENOSPC truncation produces a chain where some prefix verifies but a mid-stream record fails the `prev_hash`-or-`entry_hash` check. **Selective mode** rewinds the chain to the last verifiably-good record + archives the corrupted suffix + writes an attestation linking them.

### Scenario 2 · Schema migration (v1.0 → v1.1)

The envelope schema or a payload's `type`-specific shape evolves across kernel versions. **Migrate mode** forward-walks v1.0 entries, transforms each to v1.1 shape under operator-authorized rules, and writes a `schema_migration_attestation` genesis on the new chain. Pre-migration entries are archived intact for forensic comparison.

### Scenario 3 · Operator runs `rm -rf ~/.episteme/` (accidental or intentional fresh-start)

Either `rm -rf` was an accident (recoverable from filesystem-level backup but the chain head hash on the prior recipient's machine no longer matches), OR the operator wants a clean slate and explicitly accepts the loss. **Reset mode** is the only correct response: write a `chain_reset` attestation with operator confirmation + reason + previous_head (if known) + what-was-lost description; start a new chain with that attestation as the genesis record.

### Scenario 4 · Multi-machine merge causes parallel-fork in the chain

Two operator machines wrote to the same logical stream concurrently and produced divergent chains; on merge, both chains are valid prefixes of nothing. **Selective mode** picks one chain as the surviving lineage + archives the other + writes an attestation enumerating which entries survived the cut. Multi-machine sync is a v1.2+ federation concern; selective is the local-recovery primitive that supports it.

### Scenario 5 · Adversarial tampering caught post-fact

`verify_chain` reports a break that is NOT explained by disk corruption or operator action — strongly suggests the chain file was edited by an adversarial process. **Reset mode** is the immediate response (preserve the attestation that the prior chain was tampered); the deeper investigation is forensic + out-of-scope for the recovery contract. Mitigation against future tampering is a v1.2+ federation concern (cryptographic chain rotations + external attestation).

---

## Recovery modes

Every mode emits a recovery-attestation envelope as the GENESIS record of the resulting chain. The attestation IS a chain entry — it carries the same `prev_hash`/`entry_hash` envelope shape as every other Pillar 2 record, with `prev_hash: "sha256:GENESIS"` (because it's the first record of the recovered chain).

### Mode `reset`

Full rewind. Archive the existing chain file (renamed to `<name>.broken-<ts>.jsonl` next to the original) + start a new chain with the recovery-attestation envelope as the genesis record.

**When to use:** Scenarios 3 + 5 (rm-rf or adversarial tampering caught post-fact).

**What's preserved:** the archived file is recoverable as forensic evidence. The new chain begins fresh; no entries from the prior chain are carried forward.

**What's lost:** all data in the prior chain — by design. The operator's `--reason` and `--what-was-lost` fields document the loss intent so future audit can distinguish reset-by-design from reset-by-accident.

**CLI:** `episteme chain recover --mode=reset --stream <name> --reason "..." --confirm "I ACKNOWLEDGE CHAIN RESET"`.

**Status:** **functional** as of Event 80 / CP-CHAIN-RECOVERY-PROTOCOL-01 first slice.

### Mode `selective`

Partial-corruption windowed-rebuild. Identify the last verifiably-good record (the `break_index - 1` from `verify_chain`); split the chain at that point; archive the corrupted suffix; write an attestation linking the surviving prefix to the new genesis.

**When to use:** Scenarios 1 + 4 (disk corruption + multi-machine fork).

**What's preserved:** every record before the break. Their entry_hashes remain valid because the chain prefix was untouched. The selective attestation lives at the boundary, naming the cut.

**What's lost:** every record at-or-after the break.

**CLI:** `episteme chain recover --mode=selective --stream <name> --reason "..." --confirm "..."`.

**Status:** **stub** as of Event 80. Returns exit code 2 with a not-implemented message naming Component 5 of CP-CHAIN-RECOVERY-PROTOCOL-01 as the dependency. Functional implementation is a follow-up Event.

### Mode `migrate`

Schema-migration forward-walk. Apply a documented v1.0 → v1.1 (or vN → vN+1) transformation rule across each entry; produce a new chain on the new schema; archive the prior chain intact.

**When to use:** Scenario 2 (kernel-version schema upgrade across a release boundary).

**What's preserved:** the archived prior-version chain stays intact and readable by the prior-version verifier. The migrated chain on the new schema covers the same logical content under the new envelope.

**What's lost:** nothing semantically; the migration is information-preserving by contract. (If it is not, it must be reset, not migrated.)

**CLI:** `episteme chain recover --mode=migrate --stream <name> --reason "..." --confirm "..." --from-version <vN> --to-version <vN+1>`.

**Status:** **stub** as of Event 80. Returns exit code 2 with a not-implemented message naming CP-TEMPORAL-INTEGRITY-EXPANSION-01 as the dependency (the migrate walker uses Arm A's supersede-with-history infrastructure). Functional implementation lands after both CPs are sequenced.

---

## Recovery-attestation envelope schema

Every recovery emits a chain-entry whose payload conforms to the recovery-attestation schema. The envelope wrapper is the standard `cp7-chained-v1` (see [`core/hooks/_chain.py`](../core/hooks/_chain.py)); the payload is the attestation.

### Common payload fields (all modes)

```json
{
  "type":                  "chain_reset" | "chain_recovery_selective" | "chain_recovery_migrate",
  "mode":                  "reset" | "selective" | "migrate",
  "reason":                "<operator-supplied free-text rationale>",
  "operator_confirmation": "<operator-supplied confirmation string>",
  "previous_head":         "sha256:<hex>" | null,
  "recovered_at":          "<ISO-8601 UTC, microseconds>",
  "archived_from":         "<absolute path to archived prior chain>" | null,
  "what_was_lost":         "<operator-supplied description of lost data>" | null
}
```

- `type` — payload-type discriminator. `chain_reset` is preserved for backward compatibility with v1.0 entries written by `reset_stream`. New types (`chain_recovery_selective`, `chain_recovery_migrate`) are reserved.
- `mode` — redundant with `type` but kept for forward-compat reasons (a future schema may consolidate types).
- `reason` — required. Free-text. Describes WHY the recovery is happening; the operator's stated rationale.
- `operator_confirmation` — required. Free-text. The operator's confirmation phrase (e.g., `"I ACKNOWLEDGE CHAIN RESET"`); audit-recordable evidence that the recovery was deliberate, not automated.
- `previous_head` — the entry_hash of the LAST record in the prior chain (the head before recovery). `null` only when no prior chain existed (recovery on a virgin stream).
- `recovered_at` — ISO-8601 UTC timestamp with microseconds. Matches the envelope-level `ts` but is also stored in the payload for read-side convenience.
- `archived_from` — absolute path to the archived prior chain file (e.g., `~/.episteme/framework/protocols.broken-2026-04-29T12:00:00Z.jsonl`). `null` only when the original file was absent at recovery time.
- `what_was_lost` — required when `mode=reset`; recommended otherwise. Operator-supplied description of what data was in the prior chain that won't be carried forward. The audit trail's honest accounting of the loss.

### Mode-specific extensions

**`chain_recovery_selective` adds:**
- `break_index` — the 0-based index of the first broken record in the prior chain.
- `entries_preserved` — count of entries before the break that were carried forward.
- `entries_archived` — count of entries at-or-after the break that were archived.

**`chain_recovery_migrate` adds:**
- `from_version` — prior schema version (e.g., `"cp7-chained-v1"`).
- `to_version` — new schema version.
- `migration_rules_ref` — pointer to the doc that names the transformation rules (e.g., `"docs/SCHEMA_MIGRATION_v1_0_to_v1_1.md"`).

---

## Threat model — what recovery covers / does not cover

**Closed:**
- Mid-chain mutation detection (existing `verify_chain` from Pillar 2).
- Operator-authorized reset with attestation-recordable rationale.
- Disk corruption recovery via selective mode (when implemented).
- Schema migration across kernel versions via migrate mode (when implemented).

**NOT closed by this protocol — out of scope:**
- **Tail truncation (erase-most-recent).** A coordinated attacker who erases the chain tail leaves the prefix verifiably intact; the kernel cannot detect this without external attestation (chain-head commitment to git, witness server, etc.). v1.2+ federation work.
- **Coordinated FS rewrite (attacker rewrites file + head atomically).** Requires cryptographic signing of chain rotations. Deferred past v1.0 RC; v1.2+ federation work.
- **Multi-machine merge with no agreed-upon truth.** Selective mode picks one lineage but the kernel does not adjudicate which fork "wins." Multi-machine merge protocol is a v1.2+ federation concern.

The recovery-attestation envelope is **operator-attestation grade**, not cryptographic-signature grade. The operator's `--confirm` string is auditable evidence of intent; it is not a tamper-proof signature. Mitigation against forged attestations is the same v1.2+ federation work named above.

---

## CLI usage

### Reset mode (functional)

```bash
# Reset the protocols stream after rm -rf or post-tamper recovery
episteme chain recover --mode=reset \
    --stream protocols \
    --reason "rm -rf ~/.episteme/ recovery; no backup available" \
    --confirm "I ACKNOWLEDGE CHAIN RESET" \
    --what-was-lost "all framework protocols synthesized 2026-04-22 through 2026-04-29; ~12 entries"
```

Behavior:

1. Reads the current chain head (if any) — captured as `previous_head` in the attestation.
2. Renames the existing chain file to `<name>.broken-<ts>.jsonl` (preserved as forensic evidence).
3. Writes the recovery-attestation envelope as the genesis record of a fresh chain at the original path.
4. Returns exit code 0 with the new genesis hash printed.

### Selective + migrate (stub)

```bash
episteme chain recover --mode=selective --stream protocols --reason "..." --confirm "..."
# Exit 2; prints: "selective recovery not yet implemented; depends on
# CP-CHAIN-RECOVERY-PROTOCOL-01 Component 5 (windowed-rebuild algorithm)"

episteme chain recover --mode=migrate --stream protocols --reason "..." --confirm "..." \
    --from-version cp7-chained-v1 --to-version cp7-chained-v2
# Exit 2; prints: "migrate recovery not yet implemented; depends on
# CP-TEMPORAL-INTEGRITY-EXPANSION-01 (Cognitive Arm A) — supersede-with-history
# infrastructure required by the schema-migration walker"
```

The stubs ship in Event 80 so the API surface is visible + stable; the operator sees the mode names + their dependencies before the implementations land.

---

## Verification (post-recovery)

After running `episteme chain recover --mode=reset`, verify:

```bash
# 1. The new chain is intact (single genesis record)
episteme chain verify
# Expect: <stream> INTACT entries=1

# 2. The attestation payload contains the documented fields
head -1 ~/.episteme/framework/protocols.jsonl | python3 -m json.tool
# Expect: payload.type == "chain_reset"
#         payload.mode == "reset"
#         payload.reason / operator_confirmation / previous_head / recovered_at /
#         archived_from / what_was_lost

# 3. The archived file is preserved
ls -la ~/.episteme/framework/protocols.broken-*.jsonl
# Expect: one file per recovery; chain_verify on it returns whatever
# state it was in at archive-time
```

---

## Cross-references

- [Pillar 2 spec](./CONSTITUTION.md) — append-only hash chain principles.
- [`core/hooks/_chain.py`](../core/hooks/_chain.py) — `cp7-chained-v1` envelope implementation; `reset_stream` reused under the hood by `--mode=reset`.
- [`kernel/FALSIFIABILITY_CONDITIONS.md`](./FALSIFIABILITY_CONDITIONS.md) § A1 — Pillar 2 hash chain tamper-evidence falsifiability claim. Recovery scenarios extend the action-on-disconfirmation discipline to legitimate-break cases.
- [`kernel/KERNEL_LIMITS.md`](./KERNEL_LIMITS.md) — kernel boundary doc; threat-model gaps named here cross-reference the v1.2+ federation work that closes them.
- `~/episteme-private/docs/cp-v1.1-architectural.md` — CP-CHAIN-RECOVERY-PROTOCOL-01 spec source; CP-TEMPORAL-INTEGRITY-EXPANSION-01 dependency for migrate mode.

---

## Maintenance

This file is part of the kernel's substrate contract. It is correct when:

- Every recovery mode named here has an implementation OR a documented stub with named dependency.
- Every documented attestation field is emitted by the corresponding mode's CLI path.
- Every threat-model gap names the v-cycle that closes it.
- Cross-references are reachable.

Version: v1.0 (Event 80, 2026-04-29). First slice covers the doc + reset mode functional + selective/migrate stubs. Components 4 (migrate functional) and 5 (selective functional) are deferred to follow-up Events with named dependencies.
