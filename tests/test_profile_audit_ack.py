"""Tests for CP-AUDIT-ACK-01 (Event 78) — `episteme profile audit ack` CLI
+ hash-chained ack-store at ~/.episteme/state/profile_audit_acks.jsonl.

Coverage:

- Validation (lazy-token rejection, min-char floor, both English + Korean tokens).
- Write path (ack + revoke produce valid cp7-chained-v1 envelopes).
- Read path (is_acked / acked_ids reflect latest-state-per-id).
- Revoke preserves audit trail (revoke is a new entry, not a delete; chain stays intact).
- list_outstanding_audits filters out acked records correctly.
- Chain integrity (`verify_chain` returns intact after writes).
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from episteme import _profile_audit_ack as ack


class ValidateRationaleTests(unittest.TestCase):
    """Lazy-token + min-char discipline mirrors Reasoning Surface validator."""

    def test_rationale_too_short_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            ack.validate_rationale("too short")
        self.assertIn("at least", str(ctx.exception))

    def test_rationale_lazy_token_n_a_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            ack.validate_rationale("n/a" + " " * 20)  # padded to pass min-char
        self.assertIn("lazy-token", str(ctx.exception))

    def test_rationale_lazy_token_tbd_rejected(self):
        # exact match "tbd" stripped+lowered should reject regardless of length
        # (after stripping). With trailing spaces but lazy match.
        # Note: we strip+lower then compare to lazy set; trailing spaces
        # don't help. We need the stripped form to NOT match the lazy set.
        with self.assertRaises(ValueError):
            ack.validate_rationale("   tbd   ")  # padded fails min-char

    def test_rationale_lazy_token_korean_rejected(self):
        with self.assertRaises(ValueError):
            ack.validate_rationale("해당 없음")

    def test_rationale_lazy_token_ack_rejected(self):
        with self.assertRaises(ValueError):
            ack.validate_rationale("ack")

    def test_rationale_lazy_token_ok_rejected(self):
        with self.assertRaises(ValueError):
            ack.validate_rationale("ok")

    def test_rationale_substantive_accepted(self):
        # 15+ chars, not in lazy set
        ack.validate_rationale("Re-elicited asymmetry_posture in Event 68; closed gap.")
        # Should NOT raise

    def test_rationale_non_string_rejected(self):
        with self.assertRaises(ValueError):
            ack.validate_rationale(None)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            ack.validate_rationale(123)  # type: ignore[arg-type]


class AckStoreWriteTests(unittest.TestCase):
    """Write paths produce valid cp7-chained-v1 envelopes."""

    def test_write_ack_creates_chain_entry_with_correct_payload(self):
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td)
            envelope = ack.write_ack(
                "audit-20260427-063251-9131",
                "Re-elicited asymmetry_posture in Event 68; closed the gap.",
                evidence_refs=["Event 65", "Event 66", "Event 67"],
                acker="testuser",
                state_dir=state_dir,
            )
            self.assertEqual(envelope["schema_version"], "cp7-chained-v1")
            self.assertEqual(envelope["payload"]["type"], "profile_audit_ack")
            self.assertEqual(envelope["payload"]["audit_id"], "audit-20260427-063251-9131")
            self.assertEqual(envelope["payload"]["acker"], "testuser")
            self.assertEqual(envelope["payload"]["evidence_refs"], ["Event 65", "Event 66", "Event 67"])
            self.assertTrue(envelope["entry_hash"].startswith("sha256:"))

    def test_write_revoke_creates_revoke_entry(self):
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td)
            ack.write_ack(
                "audit-20260427-070000-aaaa",
                "Substantive ack rationale here.",
                state_dir=state_dir,
                acker="testuser",
            )
            revoke = ack.write_revoke(
                "audit-20260427-070000-aaaa",
                "Reverting because new evidence shows drift continues.",
                state_dir=state_dir,
                acker="testuser",
            )
            self.assertEqual(revoke["payload"]["type"], "profile_audit_ack_revoke")
            self.assertEqual(revoke["payload"]["audit_id"], "audit-20260427-070000-aaaa")

    def test_write_ack_invalid_audit_id_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td)
            with self.assertRaises(ValueError):
                ack.write_ack("", "Substantive rationale here.", state_dir=state_dir)
            with self.assertRaises(ValueError):
                ack.write_ack(None, "Substantive rationale here.", state_dir=state_dir)  # type: ignore[arg-type]


class NormalizeAuditIdTests(unittest.TestCase):
    """Event 79 — auto-prefix + regex validation on audit_id."""

    def test_already_prefixed_audit_id_returned_unchanged(self):
        result = ack.normalize_audit_id("audit-20260427-063251-9131")
        self.assertEqual(result, "audit-20260427-063251-9131")

    def test_bare_stem_gets_audit_prefix_auto_prepended(self):
        result = ack.normalize_audit_id("20260427-063251-9131")
        self.assertEqual(result, "audit-20260427-063251-9131")

    def test_malformed_format_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            ack.normalize_audit_id("blarg")
        self.assertIn("expected format", str(ctx.exception))

    def test_uppercase_hex_in_suffix_rejected(self):
        # NNNN must be lowercase hex per uuid4().hex[:4] convention
        with self.assertRaises(ValueError):
            ack.normalize_audit_id("audit-20260427-063251-91FF")

    def test_wrong_date_length_rejected(self):
        with self.assertRaises(ValueError):
            ack.normalize_audit_id("audit-2026-04-27-063251-9131")

    def test_empty_audit_id_rejected(self):
        with self.assertRaises(ValueError):
            ack.normalize_audit_id("")
        with self.assertRaises(ValueError):
            ack.normalize_audit_id("   ")

    def test_non_string_rejected(self):
        with self.assertRaises(ValueError):
            ack.normalize_audit_id(None)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            ack.normalize_audit_id(123)  # type: ignore[arg-type]

    def test_write_ack_with_bare_stem_normalizes_in_chain(self):
        """Functional test: write_ack with bare stem ends up storing the full id."""
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td)
            envelope = ack.write_ack(
                "20260427-063251-9131",  # NO prefix
                "Substantive rationale of sufficient length here.",
                state_dir=state_dir,
            )
            # The chain entry carries the normalized (prefixed) id
            self.assertEqual(envelope["payload"]["audit_id"], "audit-20260427-063251-9131")
            # And is_acked of the FULL id returns True
            self.assertTrue(ack.is_acked("audit-20260427-063251-9131", state_dir=state_dir))

    def test_write_ack_with_malformed_id_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td)
            with self.assertRaises(ValueError):
                ack.write_ack(
                    "abracadabra",
                    "Substantive rationale of sufficient length here.",
                    state_dir=state_dir,
                )


class IsAckedReadPathTests(unittest.TestCase):
    """is_acked + acked_ids reflect the latest-state-per-id walk."""

    def test_is_acked_returns_false_when_no_store(self):
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td)
            self.assertFalse(ack.is_acked("audit-20260427-060001-0000", state_dir=state_dir))

    def test_is_acked_returns_true_after_ack(self):
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td)
            ack.write_ack(
                "audit-20260427-070001-aaaa",
                "Rationale that is sufficiently long.",
                state_dir=state_dir,
            )
            self.assertTrue(ack.is_acked("audit-20260427-070001-aaaa", state_dir=state_dir))
            self.assertFalse(ack.is_acked("audit-20260427-070002-bbbb", state_dir=state_dir))

    def test_revoke_after_ack_returns_false(self):
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td)
            ack.write_ack(
                "audit-20260427-080001-aaaa",
                "First ack rationale that is substantive.",
                state_dir=state_dir,
            )
            self.assertTrue(ack.is_acked("audit-20260427-080001-aaaa", state_dir=state_dir))
            ack.write_revoke(
                "audit-20260427-080001-aaaa",
                "Reverting on new evidence of continued drift.",
                state_dir=state_dir,
            )
            self.assertFalse(ack.is_acked("audit-20260427-080001-aaaa", state_dir=state_dir))

    def test_re_ack_after_revoke_returns_true(self):
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td)
            aid = "audit-20260427-090001-aaaa"
            ack.write_ack(
                aid,
                "First ack with substantive rationale text.",
                state_dir=state_dir,
            )
            ack.write_revoke(
                aid,
                "Initial revoke with substantive reason text.",
                state_dir=state_dir,
            )
            ack.write_ack(
                aid,
                "Second ack with substantive rationale text.",
                state_dir=state_dir,
            )
            # Latest is ack again
            self.assertTrue(ack.is_acked(aid, state_dir=state_dir))

    def test_acked_ids_returns_set_of_currently_acked(self):
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td)
            aid_a = "audit-20260427-100001-aaaa"
            aid_b = "audit-20260427-100002-bbbb"
            aid_c = "audit-20260427-100003-cccc"
            ack.write_ack(aid_a, "Substantive ack rationale here.", state_dir=state_dir)
            ack.write_ack(aid_b, "Substantive ack rationale here.", state_dir=state_dir)
            ack.write_ack(aid_c, "Substantive ack rationale here.", state_dir=state_dir)
            ack.write_revoke(aid_b, "Substantive revoke rationale here.", state_dir=state_dir)
            self.assertEqual(
                ack.acked_ids(state_dir=state_dir),
                {aid_a, aid_c},  # b revoked
            )


class ChainIntegrityTests(unittest.TestCase):
    """Chain stays intact across multiple writes (ack + revoke + re-ack)."""

    def test_chain_intact_after_multiple_writes(self):
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td)
            aid_1 = "audit-20260427-110001-1111"
            aid_2 = "audit-20260427-110002-2222"
            ack.write_ack(aid_1, "First substantive ack rationale.", state_dir=state_dir)
            ack.write_ack(aid_2, "Second substantive ack rationale.", state_dir=state_dir)
            ack.write_revoke(aid_1, "Revoke rationale that is substantive.", state_dir=state_dir)
            ack.write_ack(aid_1, "Re-ack rationale that is substantive.", state_dir=state_dir)

            verdict = ack.verify_chain(state_dir=state_dir)
            self.assertTrue(verdict.intact)
            self.assertEqual(verdict.total_entries, 4)


class ListOutstandingAuditsTests(unittest.TestCase):
    """list_outstanding_audits filters acked records and returns drift-axis info."""

    def _write_audit_record(self, reflective_dir: Path, run_id: str, drift_axes: list[str]):
        reflective_dir.mkdir(parents=True, exist_ok=True)
        path = reflective_dir / "profile_audit.jsonl"
        rec = {
            "version": "profile-audit-v1",
            "run_id": run_id,
            "run_ts": "2026-04-29T00:00:00+00:00",
            "axes": [
                {"axis_name": name, "verdict": "drift", "reason": "test"}
                for name in drift_axes
            ],
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def test_outstanding_excludes_acked_records(self):
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td) / "state"
            reflective_dir = Path(td) / "reflective"
            aid_old = "audit-20260427-120001-aaaa"
            aid_new = "audit-20260427-120002-bbbb"
            self._write_audit_record(reflective_dir, aid_old, ["asymmetry_posture"])
            self._write_audit_record(reflective_dir, aid_new, ["fence_discipline"])
            ack.write_ack(
                aid_old,
                "Acked because re-elicited in Event 68.",
                state_dir=state_dir,
            )

            outstanding = ack.list_outstanding_audits(
                reflective_dir=reflective_dir,
                state_dir=state_dir,
            )
            self.assertEqual(len(outstanding), 1)
            self.assertEqual(outstanding[0]["run_id"], aid_new)
            self.assertEqual(outstanding[0]["drift_axes"], ["fence_discipline"])

    def test_outstanding_excludes_no_drift_records(self):
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td) / "state"
            reflective_dir = Path(td) / "reflective"
            # Record with NO drift axes
            self._write_audit_record(reflective_dir, "audit-20260427-130001-cccc", [])

            outstanding = ack.list_outstanding_audits(
                reflective_dir=reflective_dir,
                state_dir=state_dir,
            )
            self.assertEqual(len(outstanding), 0)

    def test_outstanding_empty_when_no_records(self):
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td) / "state"
            reflective_dir = Path(td) / "reflective"  # does not exist
            outstanding = ack.list_outstanding_audits(
                reflective_dir=reflective_dir,
                state_dir=state_dir,
            )
            self.assertEqual(outstanding, [])


if __name__ == "__main__":
    unittest.main()
