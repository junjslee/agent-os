"""Tests for CP-TEMPORAL-INTEGRITY-EXPANSION-01 Item 2 (Event 83) —
policy_history.jsonl for cognitive_profile / workflow_policy / agent_feedback.

Mirrors test_profile_history.py structure + coverage.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from episteme import _policy_history as ph


class ValidateFileNameTests(unittest.TestCase):
    def test_valid_files_accepted(self):
        ph.validate_file_name("cognitive_profile")
        ph.validate_file_name("workflow_policy")
        ph.validate_file_name("agent_feedback")

    def test_unknown_file_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            ph.validate_file_name("operator_profile")  # excluded; covered by Item 1
        self.assertIn("unknown file_name", str(ctx.exception))

    def test_empty_file_rejected(self):
        with self.assertRaises(ValueError):
            ph.validate_file_name("")

    def test_non_string_file_rejected(self):
        with self.assertRaises(ValueError):
            ph.validate_file_name(None)  # type: ignore[arg-type]


class ValidateSectionTests(unittest.TestCase):
    def test_valid_section_accepted(self):
        ph.validate_section("Decision Engine")
        ph.validate_section("Universal rules")

    def test_empty_section_rejected(self):
        with self.assertRaises(ValueError):
            ph.validate_section("")

    def test_non_string_section_rejected(self):
        with self.assertRaises(ValueError):
            ph.validate_section(None)  # type: ignore[arg-type]


class ValidateReasonTests(unittest.TestCase):
    def test_lazy_token_rejected(self):
        with self.assertRaises(ValueError):
            ph.validate_reason("n/a")

    def test_korean_lazy_token_rejected(self):
        with self.assertRaises(ValueError):
            ph.validate_reason("해당 없음")

    def test_short_reason_rejected(self):
        with self.assertRaises(ValueError):
            ph.validate_reason("too short")

    def test_substantive_reason_accepted(self):
        ph.validate_reason("Adding new section after Event-N introduced new pattern.")


class RecordChangeTests(unittest.TestCase):
    def test_record_change_writes_valid_envelope(self):
        with tempfile.TemporaryDirectory() as td:
            envelope = ph.record_change(
                "cognitive_profile",
                section="Decision Engine",
                old_content="(no Decision Engine section in v1)",
                new_content="Decision Engine section with 8 operational thinking rules",
                reason="Added Decision Engine after Event-N introduced operational rules.",
                evidence_refs=["Event 56"],
                recorder="testuser",
                reflective_dir=Path(td),
            )
            payload = envelope["payload"]
            self.assertEqual(payload["type"], "policy_change")
            self.assertEqual(payload["file_name"], "cognitive_profile")
            self.assertEqual(payload["section"], "Decision Engine")
            self.assertEqual(payload["recorder"], "testuser")
            self.assertEqual(payload["evidence_refs"], ["Event 56"])

    def test_record_change_invalid_file_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                ph.record_change(
                    "fake_file", "section", "old", "new",
                    "Substantive reason text here.",
                    reflective_dir=Path(td),
                )

    def test_record_change_empty_section_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                ph.record_change(
                    "cognitive_profile", "", "old", "new",
                    "Substantive reason text here.",
                    reflective_dir=Path(td),
                )

    def test_record_change_empty_content_allowed(self):
        """Empty old_content represents 'section did not exist before' (new section)."""
        with tempfile.TemporaryDirectory() as td:
            envelope = ph.record_change(
                "cognitive_profile",
                section="New Section",
                old_content="",  # represents new-section creation
                new_content="content",
                reason="Created new section as part of schema evolution.",
                reflective_dir=Path(td),
            )
            self.assertEqual(envelope["payload"]["old_content"], "")


class WalkFileHistoryTests(unittest.TestCase):
    def test_walk_returns_chronological_for_file(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            ph.record_change(
                "cognitive_profile", "Decision Engine",
                "v1", "v2",
                "First substantive revision.",
                reflective_dir=d,
            )
            ph.record_change(
                "cognitive_profile", "Decision Engine",
                "v2", "v3",
                "Second substantive revision.",
                reflective_dir=d,
            )
            history = ph.walk_file_history("cognitive_profile", reflective_dir=d)
            self.assertEqual(len(history), 2)

    def test_walk_filters_by_section(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            ph.record_change(
                "cognitive_profile", "Decision Engine",
                "v1", "v2",
                "Decision Engine revision text.",
                reflective_dir=d,
            )
            ph.record_change(
                "cognitive_profile", "Cognitive Red Flags",
                "v1", "v2",
                "Red flags revision substantive text.",
                reflective_dir=d,
            )
            engine_history = ph.walk_file_history(
                "cognitive_profile",
                section="Decision Engine",
                reflective_dir=d,
            )
            self.assertEqual(len(engine_history), 1)
            self.assertEqual(engine_history[0]["payload"]["section"], "Decision Engine")

    def test_walk_filters_other_files(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            ph.record_change(
                "cognitive_profile", "Section A",
                "v1", "v2", "Substantive reason text here.",
                reflective_dir=d,
            )
            ph.record_change(
                "workflow_policy", "Section B",
                "v1", "v2", "Substantive reason text here.",
                reflective_dir=d,
            )
            cog_history = ph.walk_file_history("cognitive_profile", reflective_dir=d)
            self.assertEqual(len(cog_history), 1)
            self.assertEqual(cog_history[0]["payload"]["file_name"], "cognitive_profile")


class ListFilesWithHistoryTests(unittest.TestCase):
    def test_list_returns_distinct_files(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            ph.record_change("cognitive_profile", "S", "a", "b", "Substantive reason text here.", reflective_dir=d)
            ph.record_change("workflow_policy", "S", "a", "b", "Substantive reason text here.", reflective_dir=d)
            ph.record_change("cognitive_profile", "S", "b", "c", "Substantive reason text here.", reflective_dir=d)
            files = ph.list_files_with_history(reflective_dir=d)
            self.assertEqual(files, {"cognitive_profile", "workflow_policy"})


class ChainIntegrityTests(unittest.TestCase):
    def test_chain_intact_after_writes(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            ph.record_change("cognitive_profile", "S1", "a", "b", "Substantive reason text.", reflective_dir=d)
            ph.record_change("workflow_policy", "S2", "a", "b", "Substantive reason text.", reflective_dir=d)
            ph.record_change("agent_feedback", "S3", "a", "b", "Substantive reason text.", reflective_dir=d)
            verdict = ph.verify_chain(reflective_dir=d)
            self.assertTrue(verdict.intact)
            self.assertEqual(verdict.total_entries, 3)


if __name__ == "__main__":
    unittest.main()
