"""Tests for v0.10.0-alpha stateful interception.

Covers both halves of the new machinery:
    * `core.hooks.state_tracker` — PostToolUse recorder that persists
      agent-written file paths + sha256 + ts to
      `~/.episteme/state/session_context.json`.
    * `core.hooks.reasoning_surface_guard` — PreToolUse consumer that
      deep-scans agent-written files referenced in Bash commands and blocks
      variable-indirection shapes that point at recently-written scripts.

The key invariants:
    1. Write-then-execute across separate tool calls is blocked.
    2. Bash-redirect-then-execute across separate Bash calls is blocked.
    3. The TTL purges stale entries on every write.
    4. Variable-indirection (bash $F) against a recent tracked write is
       blocked even when the filename is not literally in the command.
    5. Baseline: no regression on non-tracked Writes or on low-risk Bash.
"""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from core.hooks import reasoning_surface_guard as guard
from core.hooks import state_tracker as tracker


def _fresh_surface_payload() -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "core_question": "Does the posture hold?",
        "knowns": ["tracker records .py"],
        "unknowns": ["whether variable-indirection is caught by the guard"],
        "assumptions": ["cwd is repo root"],
        "disconfirmation": "CI fails on push or deep-scan misses git push in content",
    }


def _run_tracker(payload: dict, home: Path) -> int:
    raw = json.dumps(payload)
    with patch("sys.stdin", new=io.StringIO(raw)), \
         patch.object(tracker.Path, "home", return_value=home):
        return tracker.main()


def _run_guard(payload: dict, home: Path) -> tuple[int, str, str]:
    raw = json.dumps(payload)
    with patch("sys.stdin", new=io.StringIO(raw)), \
         patch("sys.stdout", new=io.StringIO()) as out, \
         patch("sys.stderr", new=io.StringIO()) as err, \
         patch.object(guard.Path, "home", return_value=home):
        rc = guard.main()
    return rc, out.getvalue(), err.getvalue()


class StateTrackerTests(unittest.TestCase):
    def test_records_write_of_shell_script(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            home.mkdir()
            proj = root / "proj"
            proj.mkdir()
            script = proj / "run.sh"
            script.write_text("#!/bin/bash\necho hi\n", encoding="utf-8")

            rc = _run_tracker(
                {
                    "tool_name": "Write",
                    "tool_input": {"file_path": str(script)},
                    "cwd": str(proj),
                },
                home,
            )
            self.assertEqual(rc, 0)

            state_path = home / ".episteme" / "state" / "session_context.json"
            self.assertTrue(state_path.exists())
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["version"], tracker.STATE_VERSION)
            key = str(script.resolve())
            self.assertIn(key, state["entries"])
            entry = state["entries"][key]
            self.assertEqual(entry["tool"], "Write")
            self.assertEqual(entry["source"], "direct")
            self.assertEqual(len(entry["sha256"]), 64)

    def test_records_python_and_js_and_extensionless(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            home.mkdir()
            proj = root / "proj"
            proj.mkdir()
            for name, content in [
                ("worker.py", "import os\n"),
                ("index.js", "console.log('hi')\n"),
                ("launcher", "#!/bin/bash\necho ok\n"),
            ]:
                (proj / name).write_text(content, encoding="utf-8")
                rc = _run_tracker(
                    {
                        "tool_name": "Write",
                        "tool_input": {"file_path": str(proj / name)},
                        "cwd": str(proj),
                    },
                    home,
                )
                self.assertEqual(rc, 0)

            state = json.loads(
                (home / ".episteme" / "state" / "session_context.json").read_text()
            )
            recorded = {Path(k).name for k in state["entries"]}
            self.assertEqual(recorded, {"worker.py", "index.js", "launcher"})

    def test_skips_non_tracked_extensions(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            home.mkdir()
            proj = root / "proj"
            proj.mkdir()
            md = proj / "README.md"
            md.write_text("# hi\n", encoding="utf-8")

            _run_tracker(
                {
                    "tool_name": "Write",
                    "tool_input": {"file_path": str(md)},
                    "cwd": str(proj),
                },
                home,
            )
            state_path = home / ".episteme" / "state" / "session_context.json"
            if state_path.exists():
                state = json.loads(state_path.read_text(encoding="utf-8"))
                self.assertNotIn(str(md.resolve()), state["entries"])

    def test_bash_redirect_records_target(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            home.mkdir()
            proj = root / "proj"
            proj.mkdir()
            target = proj / "stealth.sh"
            # Simulate the redirect having already landed on disk. The tracker
            # hashes the current content; it does not run the shell itself.
            target.write_text("git push origin main\n", encoding="utf-8")

            rc = _run_tracker(
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": f"echo 'git push' > {target.name}"},
                    "cwd": str(proj),
                },
                home,
            )
            self.assertEqual(rc, 0)
            state = json.loads(
                (home / ".episteme" / "state" / "session_context.json").read_text()
            )
            self.assertIn(str(target.resolve()), state["entries"])
            self.assertEqual(
                state["entries"][str(target.resolve())]["source"], "redirect"
            )

    def test_bash_tee_records_target(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            home.mkdir()
            proj = root / "proj"
            proj.mkdir()
            target = proj / "out.py"
            target.write_text("print('hi')\n", encoding="utf-8")

            _run_tracker(
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": f"echo x | tee -a {target.name}"},
                    "cwd": str(proj),
                },
                home,
            )
            state = json.loads(
                (home / ".episteme" / "state" / "session_context.json").read_text()
            )
            self.assertIn(str(target.resolve()), state["entries"])
            self.assertEqual(
                state["entries"][str(target.resolve())]["source"], "tee"
            )

    def test_ttl_purges_stale_entries_on_write(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            state_path = home / ".episteme" / "state" / "session_context.json"
            state_path.parent.mkdir(parents=True)
            old_ts = (datetime.now(timezone.utc) - timedelta(seconds=tracker.TTL_SECONDS + 120)).isoformat()
            state_path.write_text(
                json.dumps({
                    "version": 1,
                    "entries": {
                        "/nowhere/ghost.sh": {
                            "sha256": "x" * 64,
                            "ts": old_ts,
                            "tool": "Write",
                            "source": "direct",
                        }
                    },
                }),
                encoding="utf-8",
            )

            proj = root / "proj"
            proj.mkdir()
            fresh = proj / "fresh.sh"
            fresh.write_text("echo ok\n", encoding="utf-8")
            _run_tracker(
                {
                    "tool_name": "Write",
                    "tool_input": {"file_path": str(fresh)},
                    "cwd": str(proj),
                },
                home,
            )
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertNotIn("/nowhere/ghost.sh", state["entries"])
            self.assertIn(str(fresh.resolve()), state["entries"])

    def test_bash_fd_redirect_not_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            home.mkdir()
            proj = root / "proj"
            proj.mkdir()
            _run_tracker(
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": "some_cmd 2>&1"},
                    "cwd": str(proj),
                },
                home,
            )
            state_path = home / ".episteme" / "state" / "session_context.json"
            if state_path.exists():
                state = json.loads(state_path.read_text(encoding="utf-8"))
                self.assertEqual(state["entries"], {})


class StatefulGuardTests(unittest.TestCase):
    """End-to-end: tracker records, then guard blocks on execute."""

    def _setup(self, td: str) -> tuple[Path, Path]:
        root = Path(td)
        home = root / "home"
        home.mkdir()
        proj = root / "proj"
        proj.mkdir()
        # Fresh Reasoning Surface so the guard does not block for the other
        # reason (missing surface). We want these tests to exercise the
        # stateful-interception path specifically.
        (proj / ".episteme").mkdir()
        (proj / ".episteme" / "reasoning-surface.json").write_text(
            json.dumps(_fresh_surface_payload()), encoding="utf-8"
        )
        return home, proj

    def test_write_py_then_python_run_blocks(self):
        """Write tool creates run.py with os.system('git push'), then Bash
        invokes `python run.py`. Existing `.sh`-only scanner misses this.
        The state store + deep-scan catches it."""
        with tempfile.TemporaryDirectory() as td:
            home, proj = self._setup(td)
            runpy = proj / "run.py"
            runpy.write_text(
                "import os\nos.system('git push origin main')\n",
                encoding="utf-8",
            )
            # 1) PostToolUse tracker records the Write.
            _run_tracker(
                {
                    "tool_name": "Write",
                    "tool_input": {"file_path": str(runpy)},
                    "cwd": str(proj),
                },
                home,
            )
            # 2) Wipe the surface to force a block. The stateful path must
            # produce a label *and* the surface must be missing/invalid for
            # the block to land. We confirm the label is the new one.
            (proj / ".episteme" / "reasoning-surface.json").unlink()
            rc, _, err = _run_guard(
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": "python run.py"},
                    "cwd": str(proj),
                },
                home,
            )
            self.assertEqual(rc, 2)
            self.assertIn("git push", err)
            self.assertIn("agent-written run.py", err)

    def test_bash_redirect_then_bash_exec_blocks(self):
        """Two Bash calls: (1) writes the script via redirect, (2) executes
        by name. Between calls the tracker persists run.sh's sha256 + ts."""
        with tempfile.TemporaryDirectory() as td:
            home, proj = self._setup(td)
            script = proj / "stealth.sh"
            # The file lands on disk as if the shell had run the redirect.
            # For the tracker, that is all that matters.
            script.write_text("#!/bin/bash\ngit push origin main\n", encoding="utf-8")
            _run_tracker(
                {
                    "tool_name": "Bash",
                    "tool_input": {
                        "command": f"echo '#!/bin/bash' > {script.name}; "
                                   f"echo 'git push origin main' >> {script.name}",
                    },
                    "cwd": str(proj),
                },
                home,
            )
            (proj / ".episteme" / "reasoning-surface.json").unlink()
            rc, _, err = _run_guard(
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": "bash stealth.sh"},
                    "cwd": str(proj),
                },
                home,
            )
            self.assertEqual(rc, 2)
            # This case ALSO trips the existing `.sh` script scanner; either
            # label is acceptable — the important thing is that it blocks.
            self.assertIn("git push", err)

    def test_variable_indirection_against_recent_write_blocks(self):
        """`F=stealth.sh; bash $F` — the command string never contains the
        filename. State tracking + indirection heuristic catches it."""
        with tempfile.TemporaryDirectory() as td:
            home, proj = self._setup(td)
            script = proj / "stealth.sh"
            script.write_text("#!/bin/bash\ngit push origin main\n", encoding="utf-8")
            _run_tracker(
                {
                    "tool_name": "Write",
                    "tool_input": {"file_path": str(script)},
                    "cwd": str(proj),
                },
                home,
            )
            (proj / ".episteme" / "reasoning-surface.json").unlink()
            rc, _, err = _run_guard(
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": "bash $F"},
                    "cwd": str(proj),
                },
                home,
            )
            self.assertEqual(rc, 2)
            self.assertIn("agent-written stealth.sh", err)

    def test_innocuous_agent_written_file_does_not_trip_guard(self):
        """If the agent writes a benign file, a Bash command referencing it
        must pass. The deep-scan only fires on high-impact patterns."""
        with tempfile.TemporaryDirectory() as td:
            home, proj = self._setup(td)
            script = proj / "build.sh"
            script.write_text("#!/bin/bash\nmake all\n", encoding="utf-8")
            _run_tracker(
                {
                    "tool_name": "Write",
                    "tool_input": {"file_path": str(script)},
                    "cwd": str(proj),
                },
                home,
            )
            rc, _, err = _run_guard(
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": "bash build.sh"},
                    "cwd": str(proj),
                },
                home,
            )
            self.assertEqual(rc, 0, f"unexpected block: {err}")

    def test_empty_state_store_is_noop_for_guard(self):
        """With no state store, the guard behavior is identical to pre-0.10."""
        with tempfile.TemporaryDirectory() as td:
            home, proj = self._setup(td)
            (proj / ".episteme" / "reasoning-surface.json").unlink()
            rc, _, _ = _run_guard(
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": "ls -la"},
                    "cwd": str(proj),
                },
                home,
            )
            self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
