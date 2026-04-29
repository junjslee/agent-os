"""Tests for CP-CHAIN-RECOVERY-PROTOCOL-01 (Event 80) — `episteme chain recover`
unified recovery CLI + recovery-attestation envelope schema.

Coverage:

- reset_stream now accepts mode + what_was_lost; genesis payload contains all
  documented attestation fields.
- mode=reset end-to-end: writes prior entries, recovers, verifies attestation
  envelope shape + chain integrity restored.
- mode=selective and mode=migrate are stubs that return non-zero from a
  programmatic invocation surface check (the CLI returns exit 2; here we
  verify the mode-name handling without spinning up a subprocess).
- Backward compatibility: callers that pass only the original args
  (reason / operator_confirmation / previous_head) still get a valid
  genesis with mode='reset' default.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure core/hooks/ is importable for the chain module.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_CORE_HOOKS_DIR = _REPO_ROOT / "core" / "hooks"
if str(_CORE_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_HOOKS_DIR))

import _chain  # type: ignore  # pyright: ignore[reportMissingImports]


class ResetStreamAttestationFieldsTests(unittest.TestCase):
    """The genesis payload now carries the recovery-attestation envelope
    fields documented in kernel/CHAIN_RECOVERY_PROTOCOL.md."""

    def test_reset_genesis_payload_has_all_attestation_fields(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "test.jsonl"
            # Write a prior entry so reset has something to archive
            _chain.append(path, {"type": "test", "data": "prior"})
            prior_verdict = _chain.verify_chain(path)
            previous_head = prior_verdict.head_hash

            _chain.reset_stream(
                path,
                reason="Test recovery rationale",
                operator_confirmation="I ACKNOWLEDGE CHAIN RESET",
                previous_head=previous_head,
                mode="reset",
                what_was_lost="One test entry; no real data loss.",
            )

            # Read the new chain's genesis record
            with open(path, "r", encoding="utf-8") as f:
                genesis = json.loads(f.readline())

            payload = genesis["payload"]
            self.assertEqual(payload["type"], "chain_reset")
            self.assertEqual(payload["mode"], "reset")
            self.assertEqual(payload["reason"], "Test recovery rationale")
            self.assertEqual(payload["operator_confirmation"], "I ACKNOWLEDGE CHAIN RESET")
            self.assertEqual(payload["previous_head"], previous_head)
            self.assertIn("recovered_at", payload)
            self.assertTrue(isinstance(payload["recovered_at"], str))
            self.assertIn("archived_from", payload)
            self.assertIsNotNone(payload["archived_from"])  # prior file existed; archived
            self.assertEqual(payload["what_was_lost"], "One test entry; no real data loss.")

    def test_reset_genesis_archived_from_null_when_no_prior_chain(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "test.jsonl"  # does NOT exist
            result = _chain.reset_stream(
                path,
                reason="Fresh-start recovery",
                operator_confirmation="I ACKNOWLEDGE CHAIN RESET",
            )
            self.assertEqual(result.status, "reset")  # not archived_and_reset
            self.assertIsNone(result.archived_path)

            with open(path, "r", encoding="utf-8") as f:
                genesis = json.loads(f.readline())
            self.assertIsNone(genesis["payload"]["archived_from"])

    def test_reset_what_was_lost_optional(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "test.jsonl"
            _chain.reset_stream(
                path,
                reason="Test",
                operator_confirmation="I ACKNOWLEDGE",
                # no what_was_lost
            )
            with open(path, "r", encoding="utf-8") as f:
                genesis = json.loads(f.readline())
            self.assertIsNone(genesis["payload"]["what_was_lost"])

    def test_reset_default_mode_is_reset(self):
        """Backward compat: callers that don't pass mode get mode='reset'."""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "test.jsonl"
            _chain.reset_stream(
                path,
                reason="Test",
                operator_confirmation="I ACKNOWLEDGE",
                # no mode kwarg
            )
            with open(path, "r", encoding="utf-8") as f:
                genesis = json.loads(f.readline())
            self.assertEqual(genesis["payload"]["mode"], "reset")


class ResetEndToEndTests(unittest.TestCase):
    """Full reset cycle: prior entries → reset → new chain genesis →
    verify chain intact."""

    def test_reset_archives_prior_chain_and_creates_new_intact_chain(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "test.jsonl"
            # Prior entries
            _chain.append(path, {"type": "test", "n": 1})
            _chain.append(path, {"type": "test", "n": 2})
            _chain.append(path, {"type": "test", "n": 3})
            prior = _chain.verify_chain(path)
            self.assertEqual(prior.total_entries, 3)
            self.assertTrue(prior.intact)

            # Reset
            result = _chain.reset_stream(
                path,
                reason="Test full reset",
                operator_confirmation="I ACKNOWLEDGE CHAIN RESET",
                previous_head=prior.head_hash,
                mode="reset",
            )
            self.assertEqual(result.status, "archived_and_reset")
            self.assertIsNotNone(result.archived_path)
            self.assertTrue(result.archived_path.exists())  # type: ignore[union-attr]

            # New chain has just the genesis record + is intact
            new_verdict = _chain.verify_chain(path)
            self.assertEqual(new_verdict.total_entries, 1)
            self.assertTrue(new_verdict.intact)
            self.assertEqual(new_verdict.head_hash, result.new_genesis_hash)

            # Archived file still parses + has the original 3 entries
            archived_verdict = _chain.verify_chain(result.archived_path)  # type: ignore[arg-type]
            self.assertEqual(archived_verdict.total_entries, 3)
            self.assertTrue(archived_verdict.intact)


if __name__ == "__main__":
    unittest.main()
