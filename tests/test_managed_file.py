"""Tests for the managed-region contract in cli._write_managed_file / _compose_managed_file.

Contract under test:
- Fresh file: the managed block is written between begin/end markers.
- User content outside the markers is preserved verbatim across syncs.
- User edits *inside* the markers are overwritten on the next sync.
- First-run migration (file exists without markers): managed block is inserted
  at the top and the pre-existing content is kept below, never silently destroyed.
"""
import tempfile
import unittest
from pathlib import Path

from cognitive_os.cli import (
    MANAGED_MARKER,
    _compose_managed_file,
    _extract_managed_block,
    _write_managed_file,
)


class ManagedFileContractTests(unittest.TestCase):
    def test_fresh_file_gets_managed_block_only(self):
        result = _compose_managed_file(None, "hello world")
        self.assertIn(f"<!-- {MANAGED_MARKER}:begin -->", result)
        self.assertIn(f"<!-- {MANAGED_MARKER}:end -->", result)
        self.assertIn("hello world", result)
        # Managed block ends with a trailing newline
        self.assertTrue(result.endswith("\n"))

    def test_user_content_outside_markers_preserved_on_update(self):
        begin = f"<!-- {MANAGED_MARKER}:begin -->"
        end = f"<!-- {MANAGED_MARKER}:end -->"
        existing = (
            f"{begin}\n"
            "OLD MANAGED\n"
            f"{end}\n"
            "\n"
            "# My personal notes\n"
            "- remember to do X\n"
        )
        result = _compose_managed_file(existing, "NEW MANAGED")
        self.assertIn("NEW MANAGED", result)
        self.assertNotIn("OLD MANAGED", result)
        self.assertIn("# My personal notes", result)
        self.assertIn("remember to do X", result)

    def test_user_content_before_markers_preserved(self):
        begin = f"<!-- {MANAGED_MARKER}:begin -->"
        end = f"<!-- {MANAGED_MARKER}:end -->"
        existing = (
            "# Personal header\n"
            "some prefix prose\n"
            f"{begin}\n"
            "OLD\n"
            f"{end}\n"
        )
        result = _compose_managed_file(existing, "NEW")
        self.assertTrue(result.startswith("# Personal header\n"))
        self.assertIn("NEW", result)
        self.assertNotIn("OLD", result)

    def test_first_run_migration_preserves_existing_content_below(self):
        existing = "# User wrote this by hand\nline two\n"
        result = _compose_managed_file(existing, "MANAGED")
        # Managed block at top, user content kept below
        self.assertTrue(result.lstrip().startswith(f"<!-- {MANAGED_MARKER}:begin -->"))
        self.assertIn("# User wrote this by hand", result)
        self.assertIn("line two", result)
        self.assertIn("MANAGED", result)

    def test_prior_signature_enables_clean_replace(self):
        # Simulates a file authored by a pre-marker sync: matches signature,
        # so we overwrite cleanly instead of duplicating content.
        existing = "# cognitive-os Global Memory\n\n@some/path\n"
        result = _compose_managed_file(
            existing, "NEW", prior_signature="# cognitive-os Global Memory"
        )
        self.assertIn("NEW", result)
        self.assertNotIn("@some/path", result)
        # Result should be exactly the managed block — no pre-marker header
        # content left as a duplicate trailer.
        self.assertTrue(result.lstrip().startswith(f"<!-- {MANAGED_MARKER}:begin -->"))
        self.assertTrue(result.rstrip().endswith(f"<!-- {MANAGED_MARKER}:end -->"))

    def test_prior_signature_mismatch_falls_back_to_preservation(self):
        existing = "# Totally unrelated content\n"
        result = _compose_managed_file(
            existing, "MANAGED", prior_signature="# cognitive-os Global Memory"
        )
        self.assertIn("# Totally unrelated content", result)
        self.assertIn("MANAGED", result)

    def test_idempotent_when_managed_content_unchanged(self):
        first = _compose_managed_file(None, "STABLE")
        second = _compose_managed_file(first, "STABLE")
        self.assertEqual(first, second)

    def test_extract_managed_block_roundtrips(self):
        composed = _compose_managed_file(None, "payload body\nline two")
        self.assertEqual(_extract_managed_block(composed), "payload body\nline two")

    def test_extract_managed_block_returns_none_when_no_markers(self):
        self.assertIsNone(_extract_managed_block("no markers here at all"))

    def test_write_managed_file_creates_and_updates_on_disk(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "nested" / "OPERATOR.md"
            _write_managed_file(target, "v1")
            self.assertTrue(target.exists())
            self.assertIn("v1", target.read_text())

            # Simulate user adding notes below the managed region
            with target.open("a", encoding="utf-8") as fh:
                fh.write("\n# USER NOTE\n")

            _write_managed_file(target, "v2")
            text = target.read_text()
            self.assertIn("v2", text)
            self.assertNotIn("v1", text)
            self.assertIn("# USER NOTE", text)


if __name__ == "__main__":
    unittest.main()
