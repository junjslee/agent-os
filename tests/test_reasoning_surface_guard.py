import io
import json
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from core.hooks import reasoning_surface_guard as guard


def _fresh_surface_payload() -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "core_question": "Does this change preserve the kernel contract?",
        "knowns": ["tests pass locally"],
        "unknowns": ["whether CI matches"],
        "assumptions": ["cwd is repo root"],
        "disconfirmation": "CI fails on main after push",
    }


def _stale_surface_payload() -> dict:
    return {
        "timestamp": (time.time() - (guard.SURFACE_TTL_SECONDS + 120)),
        "core_question": "Old work",
        "unknowns": ["x"],
        "disconfirmation": "y",
    }


class ReasoningSurfaceGuardTests(unittest.TestCase):
    def _run(self, payload: dict, cwd: Path) -> tuple[int, str, str]:
        payload = {**payload, "cwd": str(cwd)}
        raw = json.dumps(payload)
        with patch("sys.stdin", new=io.StringIO(raw)), \
             patch("sys.stdout", new=io.StringIO()) as fake_out, \
             patch("sys.stderr", new=io.StringIO()) as fake_err:
            rc = guard.main()
        return rc, fake_out.getvalue(), fake_err.getvalue()

    def test_non_matching_tool_passes_silently(self):
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = self._run(
                {"tool_name": "Read", "tool_input": {"file_path": "README.md"}},
                Path(td),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")
        self.assertEqual(err, "")

    def test_low_risk_bash_passes_silently(self):
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "ls -la"}},
                Path(td),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_high_impact_bash_without_surface_emits_advisory(self):
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "git push origin main"}},
                Path(td),
            )
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertIn("REASONING SURFACE", payload["hookSpecificOutput"]["additionalContext"])
        self.assertIn("git push", payload["hookSpecificOutput"]["additionalContext"])

    def test_high_impact_bash_with_fresh_surface_passes(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / ".episteme").mkdir()
            (cwd / ".episteme" / "reasoning-surface.json").write_text(
                json.dumps(_fresh_surface_payload()), encoding="utf-8"
            )
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "git push origin main"}},
                cwd,
            )
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_stale_surface_emits_advisory(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / ".episteme").mkdir()
            (cwd / ".episteme" / "reasoning-surface.json").write_text(
                json.dumps(_stale_surface_payload()), encoding="utf-8"
            )
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "terraform apply"}},
                cwd,
            )
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertIn("STALE", payload["hookSpecificOutput"]["additionalContext"])

    def test_incomplete_surface_emits_advisory(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / ".episteme").mkdir()
            bad = _fresh_surface_payload()
            bad.pop("disconfirmation")
            (cwd / ".episteme" / "reasoning-surface.json").write_text(
                json.dumps(bad), encoding="utf-8"
            )
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "npm publish"}},
                cwd,
            )
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        ctx = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("INCOMPLETE", ctx)
        self.assertIn("disconfirmation", ctx)

    def test_strict_mode_blocks_without_surface(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / ".episteme").mkdir()
            (cwd / ".episteme" / "strict-surface").write_text("", encoding="utf-8")
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "git push --force origin main"}},
                cwd,
            )
        self.assertEqual(rc, 2)
        self.assertEqual(out, "")
        self.assertIn("REASONING SURFACE", err)

    def test_lockfile_edit_triggers_advisory(self):
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = self._run(
                {
                    "tool_name": "Edit",
                    "tool_input": {"file_path": "/repo/package-lock.json"},
                },
                Path(td),
            )
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertIn("package-lock.json", payload["hookSpecificOutput"]["additionalContext"])

    def test_non_lockfile_edit_passes(self):
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = self._run(
                {"tool_name": "Edit", "tool_input": {"file_path": "src/foo.py"}},
                Path(td),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
