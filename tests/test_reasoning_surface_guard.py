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
        "unknowns": ["whether CI matches the local result on the push branch"],
        "assumptions": ["cwd is repo root"],
        "disconfirmation": "CI fails on main after push or tag verification rejects",
    }


def _stale_surface_payload() -> dict:
    return {
        "timestamp": (time.time() - (guard.SURFACE_TTL_SECONDS + 120)),
        "core_question": "Old work",
        "unknowns": ["x"],
        "disconfirmation": "y",
    }


def _advisory(cwd: Path) -> None:
    (cwd / ".episteme").mkdir(exist_ok=True)
    (cwd / ".episteme" / "advisory-surface").write_text("", encoding="utf-8")


class ReasoningSurfaceGuardTests(unittest.TestCase):
    def _run(self, payload: dict, cwd: Path) -> tuple[int, str, str]:
        payload = {**payload, "cwd": str(cwd)}
        raw = json.dumps(payload)
        with patch("sys.stdin", new=io.StringIO(raw)), \
             patch("sys.stdout", new=io.StringIO()) as fake_out, \
             patch("sys.stderr", new=io.StringIO()) as fake_err:
            rc = guard.main()
        return rc, fake_out.getvalue(), fake_err.getvalue()

    # ----- baseline pass-through -----

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

    def test_non_lockfile_edit_passes(self):
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = self._run(
                {"tool_name": "Edit", "tool_input": {"file_path": "src/foo.py"}},
                Path(td),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    # ----- strict mode is default -----

    def test_high_impact_bash_without_surface_blocks_by_default(self):
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "git push origin main"}},
                Path(td),
            )
        self.assertEqual(rc, 2)
        self.assertEqual(out, "")
        self.assertIn("Episteme Strict Mode", err)
        self.assertIn("REASONING SURFACE MISSING", err)

    def test_stale_surface_blocks_by_default(self):
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
        self.assertEqual(rc, 2)
        self.assertIn("STALE", err)

    def test_incomplete_surface_blocks_by_default(self):
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
        self.assertEqual(rc, 2)
        self.assertIn("INCOMPLETE", err)
        self.assertIn("disconfirmation", err)

    def test_lockfile_edit_blocks_by_default(self):
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = self._run(
                {
                    "tool_name": "Edit",
                    "tool_input": {"file_path": "/repo/package-lock.json"},
                },
                Path(td),
            )
        self.assertEqual(rc, 2)
        self.assertIn("package-lock.json", err)

    # ----- valid surface passes strict mode -----

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
        self.assertEqual(err, "")

    # ----- advisory opt-out -----

    def test_advisory_marker_downgrades_block_to_advisory(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            _advisory(cwd)
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "git push origin main"}},
                cwd,
            )
        self.assertEqual(rc, 0)
        self.assertEqual(err, "")
        payload = json.loads(out)
        ctx = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("REASONING SURFACE MISSING", ctx)
        self.assertIn("Advisory mode is active", ctx)

    def test_legacy_strict_surface_marker_is_noop(self):
        # strict is default — the legacy marker neither helps nor hurts.
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / ".episteme").mkdir()
            (cwd / ".episteme" / "strict-surface").write_text("", encoding="utf-8")
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "git push --force origin main"}},
                cwd,
            )
        self.assertEqual(rc, 2)
        self.assertIn("Episteme Strict Mode", err)

    # ----- lazy-agent rejection -----

    def test_lazy_disconfirmation_is_rejected(self):
        for lazy in ("none", "N/A", "TBD", "해당 없음", "없음", "null", "-", "nothing"):
            with self.subTest(lazy=lazy):
                with tempfile.TemporaryDirectory() as td:
                    cwd = Path(td)
                    (cwd / ".episteme").mkdir()
                    payload = _fresh_surface_payload()
                    payload["disconfirmation"] = lazy
                    (cwd / ".episteme" / "reasoning-surface.json").write_text(
                        json.dumps(payload), encoding="utf-8"
                    )
                    rc, out, err = self._run(
                        {"tool_name": "Bash", "tool_input": {"command": "git push origin main"}},
                        cwd,
                    )
                self.assertEqual(rc, 2)
                self.assertIn("disconfirmation", err)

    def test_short_disconfirmation_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / ".episteme").mkdir()
            payload = _fresh_surface_payload()
            payload["disconfirmation"] = "CI fails"  # 8 chars, below MIN
            (cwd / ".episteme" / "reasoning-surface.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "git push origin main"}},
                cwd,
            )
        self.assertEqual(rc, 2)
        self.assertIn("disconfirmation", err)

    def test_lazy_unknowns_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / ".episteme").mkdir()
            payload = _fresh_surface_payload()
            payload["unknowns"] = ["none", "N/A", "TBD"]
            (cwd / ".episteme" / "reasoning-surface.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "git push origin main"}},
                cwd,
            )
        self.assertEqual(rc, 2)
        self.assertIn("unknowns", err)

    def test_short_unknowns_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / ".episteme").mkdir()
            payload = _fresh_surface_payload()
            payload["unknowns"] = ["x", "y", "maybe z"]  # all under MIN_UNKNOWN_LEN
            (cwd / ".episteme" / "reasoning-surface.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "git push origin main"}},
                cwd,
            )
        self.assertEqual(rc, 2)
        self.assertIn("unknowns", err)

    # ----- bypass vectors -----

    def test_subprocess_run_list_form_is_caught(self):
        # Agent tries: python -c "import subprocess; subprocess.run(['git', 'push'])"
        with tempfile.TemporaryDirectory() as td:
            cmd = "python -c \"import subprocess; subprocess.run(['git', 'push'])\""
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": cmd}},
                Path(td),
            )
        self.assertEqual(rc, 2)
        self.assertIn("git push", err)

    def test_os_system_form_is_caught(self):
        with tempfile.TemporaryDirectory() as td:
            cmd = "python -c \"import os; os.system('git push origin main')\""
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": cmd}},
                Path(td),
            )
        self.assertEqual(rc, 2)
        self.assertIn("git push", err)

    def test_sh_c_wrapped_publish_is_caught(self):
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "sh -c 'npm publish'"}},
                Path(td),
            )
        self.assertEqual(rc, 2)
        self.assertIn("npm publish", err)

    def test_backtick_wrapped_git_push_is_caught(self):
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "echo `git push`"}},
                Path(td),
            )
        self.assertEqual(rc, 2)
        self.assertIn("git push", err)

    # ----- indirection heuristics (Phase 4) -----

    def test_eval_of_variable_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": 'eval "$CMD"'}},
                Path(td),
            )
        self.assertEqual(rc, 2)
        self.assertIn("eval", err)

    def test_eval_bare_variable_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "eval $CMD"}},
                Path(td),
            )
        self.assertEqual(rc, 2)
        self.assertIn("eval", err)

    def test_eval_literal_string_passes(self):
        # `eval "echo hi"` has no variable indirection — should not trip.
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": 'eval "echo hi"'}},
                Path(td),
            )
        self.assertEqual(rc, 0)

    # ----- script-execution interception (Phase 4) -----

    def test_bash_script_containing_git_push_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / "deploy.sh").write_text("#!/bin/bash\ngit push origin main\n", encoding="utf-8")
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "bash deploy.sh"}},
                cwd,
            )
        self.assertEqual(rc, 2)
        self.assertIn("git push", err)
        self.assertIn("deploy.sh", err)

    def test_relative_dot_slash_script_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / "release.sh").write_text("#!/usr/bin/env bash\nnpm publish\n", encoding="utf-8")
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "./release.sh"}},
                cwd,
            )
        self.assertEqual(rc, 2)
        self.assertIn("npm publish", err)

    def test_sourced_script_is_scanned(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / "env.sh").write_text("export X=1\nterraform apply\n", encoding="utf-8")
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "source env.sh"}},
                cwd,
            )
        self.assertEqual(rc, 2)
        self.assertIn("terraform apply", err)

    def test_benign_script_passes(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / "hello.sh").write_text("#!/bin/bash\necho hello world\n", encoding="utf-8")
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "bash hello.sh"}},
                cwd,
            )
        self.assertEqual(rc, 0)

    def test_missing_script_passes_silently(self):
        # Best-effort: if the referenced script isn't there, don't block.
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = self._run(
                {"tool_name": "Bash", "tool_input": {"command": "bash /nonexistent-script.sh"}},
                Path(td),
            )
        self.assertEqual(rc, 0)

    # ----- calibration telemetry (Phase 2) -----

    def test_allowed_bash_writes_prediction_telemetry(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / ".episteme").mkdir()
            (cwd / ".episteme" / "reasoning-surface.json").write_text(
                json.dumps(_fresh_surface_payload()), encoding="utf-8"
            )
            telemetry_root = cwd / "telemetry_home"
            with patch.object(guard.Path, "home", return_value=telemetry_root):
                rc, _, _ = self._run(
                    {
                        "tool_name": "Bash",
                        "tool_input": {"command": "git push origin main"},
                        "tool_use_id": "tu_abc123",
                    },
                    cwd,
                )
            self.assertEqual(rc, 0)
            day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            tpath = telemetry_root / ".episteme" / "telemetry" / f"{day}-audit.jsonl"
            self.assertTrue(tpath.exists(), f"expected telemetry file at {tpath}")
            lines = [ln for ln in tpath.read_text(encoding="utf-8").splitlines() if ln.strip()]
            self.assertEqual(len(lines), 1)
            rec = json.loads(lines[0])
            self.assertEqual(rec["event"], "prediction")
            self.assertEqual(rec["correlation_id"], "tu_abc123")
            self.assertEqual(rec["command_executed"], "git push origin main")
            self.assertEqual(rec["op"], "git push")
            self.assertIsNone(rec["exit_code"])
            pred = rec["epistemic_prediction"]
            self.assertEqual(
                pred["disconfirmation"],
                "CI fails on main after push or tag verification rejects",
            )
            self.assertTrue(pred["unknowns"])

    def test_blocked_bash_writes_no_telemetry(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            telemetry_root = cwd / "telemetry_home"
            with patch.object(guard.Path, "home", return_value=telemetry_root):
                rc, _, _ = self._run(
                    {"tool_name": "Bash", "tool_input": {"command": "git push origin main"}},
                    cwd,
                )
            self.assertEqual(rc, 2)
            # Telemetry is prediction+outcome only — blocked calls stay in
            # the audit log, not the telemetry stream.
            tpath = telemetry_root / ".episteme" / "telemetry"
            self.assertFalse(tpath.exists())


if __name__ == "__main__":
    unittest.main()
