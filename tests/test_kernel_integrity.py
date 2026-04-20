import tempfile
import unittest
from pathlib import Path

from episteme import kernel_integrity as ki


def _write_kernel(root: Path) -> None:
    (root / "kernel").mkdir(parents=True, exist_ok=True)
    for rel in ki.MANAGED_KERNEL_FILES:
        p = root / rel
        p.write_text(f"# {Path(rel).stem}\ncontent\n", encoding="utf-8")


class KernelIntegrityTests(unittest.TestCase):
    def test_compute_and_render_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_kernel(root)
            manifest = ki.compute_manifest(root)
            self.assertEqual(set(manifest), set(ki.MANAGED_KERNEL_FILES))
            text = ki.render_manifest(manifest)
            parsed = ki.parse_manifest(text)
            self.assertEqual(parsed, manifest)

    def test_write_then_verify_ok(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_kernel(root)
            ki.write_manifest(root)
            ok, diffs = ki.verify(root)
            self.assertTrue(ok, diffs)
            self.assertEqual(diffs, [])

    def test_verify_detects_content_drift(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_kernel(root)
            ki.write_manifest(root)
            (root / ki.MANAGED_KERNEL_FILES[0]).write_text("# tampered\n", encoding="utf-8")
            ok, diffs = ki.verify(root)
            self.assertFalse(ok)
            self.assertTrue(any("drift:" in d for d in diffs))

    def test_verify_detects_missing_file(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_kernel(root)
            ki.write_manifest(root)
            (root / ki.MANAGED_KERNEL_FILES[1]).unlink()
            ok, diffs = ki.verify(root)
            self.assertFalse(ok)
            self.assertTrue(any("missing" in d for d in diffs))

    def test_verify_missing_manifest_returns_false(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_kernel(root)
            ok, diffs = ki.verify(root)
            self.assertFalse(ok)
            self.assertTrue(any("manifest not found" in d for d in diffs))

    def test_parse_ignores_comments_and_blanks(self):
        text = (
            "# comment line\n"
            "\n"
            "deadbeef  kernel/x.md\n"
            "  \n"
            "abc123  kernel/y.md\n"
        )
        parsed = ki.parse_manifest(text)
        self.assertEqual(parsed, {"kernel/x.md": "deadbeef", "kernel/y.md": "abc123"})


if __name__ == "__main__":
    unittest.main()
