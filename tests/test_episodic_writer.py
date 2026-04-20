"""Tests for the episodic-tier writer (core/hooks/episodic_writer.py).

Kernel reference: kernel/MEMORY_ARCHITECTURE.md — episodic tier.

These tests verify:
1. Trigger logic fires on high-impact Bash and only there.
2. Records conform to the episodic_record.json schema (required fields).
3. Reasoning-surface snapshot is attached when the surface exists in cwd.
4. Redaction catches obvious secret shapes before write.
5. Hook never blocks: empty stdin, malformed JSON, unknown payload shapes
   all return 0 and produce no crash.
6. Confidence field on provenance reflects what signal was available.
"""
from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.hooks import episodic_writer as ew


def _payload(tool: str, cmd: str, *, cwd: str, exit_code: int = 0,
             session_id: str = "sess-abc", tool_use_id: str = "tuid-1",
             extra: dict | None = None) -> dict:
    p: dict = {
        "tool_name": tool,
        "tool_input": {"command": cmd},
        "tool_response": {"exit_code": exit_code, "status": "success"},
        "cwd": cwd,
        "session_id": session_id,
        "tool_use_id": tool_use_id,
    }
    if extra:
        p.update(extra)
    return p


class TriggerLogicTests(unittest.TestCase):
    """Only Bash + matched high-impact pattern produces a record."""

    def test_non_bash_tool_skips(self):
        record_it, _, _ = ew._should_record(_payload("Write", "anything", cwd="/tmp"))
        self.assertFalse(record_it)

    def test_bash_empty_cmd_skips(self):
        record_it, _, _ = ew._should_record(_payload("Bash", "", cwd="/tmp"))
        self.assertFalse(record_it)

    def test_bash_non_high_impact_skips(self):
        record_it, _, hits = ew._should_record(_payload("Bash", "ls -la", cwd="/tmp"))
        self.assertFalse(record_it)
        self.assertEqual(hits, [])

    def test_bash_high_impact_triggers(self):
        record_it, cmd, hits = ew._should_record(
            _payload("Bash", "git push origin master", cwd="/tmp"))
        self.assertTrue(record_it)
        self.assertIn("git push", hits)

    def test_bash_quoted_indirection_still_matches(self):
        # Quoted/bracketed invocations should trip the normalized pattern
        # set, matching the guard's own bypass-hardening posture.
        record_it, _, hits = ew._should_record(_payload(
            "Bash", "python -c \"import subprocess; subprocess.run(['git','push'])\"",
            cwd="/tmp",
        ))
        self.assertTrue(record_it)
        self.assertIn("git push", hits)


class RecordShapeTests(unittest.TestCase):
    """Records must satisfy the common.json + episodic_record.json schema."""

    def _write_and_read(self, payload: dict) -> dict:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            with patch.dict(os.environ, {"HOME": str(home)}):
                # Force Path.home() to honor patched HOME.
                with patch("core.hooks.episodic_writer.Path.home",
                           return_value=home):
                    rc = ew._should_record(payload)
                    self.assertTrue(rc[0])
                    record = ew._build_record(payload, rc[1], rc[2])
                    ew._append_record(record)
                    # Locate the jsonl file (one date bucket expected).
                    episodic_dir = home / ".episteme" / "memory" / "episodic"
                    files = list(episodic_dir.glob("*.jsonl"))
                    self.assertEqual(len(files), 1, "expected one date file")
                    with open(files[0]) as f:
                        lines = [json.loads(ln) for ln in f if ln.strip()]
                    self.assertEqual(len(lines), 1)
                    return lines[0]

    def test_required_common_fields_present(self):
        record = self._write_and_read(_payload("Bash", "git push", cwd="/tmp"))
        for field in ("id", "memory_class", "summary", "details",
                      "provenance", "status", "version"):
            self.assertIn(field, record, f"missing {field}")
        self.assertEqual(record["memory_class"], "episodic")
        self.assertEqual(record["version"], "memory-contract-v1")
        self.assertEqual(record["status"], "active")

    def test_required_episodic_fields_present(self):
        record = self._write_and_read(_payload("Bash", "git push", cwd="/tmp"))
        self.assertIn("session_id", record)
        self.assertIn("event_type", record)
        self.assertEqual(record["event_type"], "action")

    def test_provenance_has_all_required_fields(self):
        record = self._write_and_read(_payload("Bash", "git push", cwd="/tmp"))
        prov = record["provenance"]
        for field in ("source_type", "source_ref", "captured_at",
                      "captured_by", "confidence"):
            self.assertIn(field, prov)
        self.assertEqual(prov["source_type"], "agent")
        self.assertIn(prov["confidence"], ("low", "medium", "high"))

    def test_summary_under_500_chars(self):
        record = self._write_and_read(_payload("Bash", "git push", cwd="/tmp"))
        self.assertLessEqual(len(record["summary"]), 500)

    def test_details_carry_cmd_and_exit(self):
        record = self._write_and_read(
            _payload("Bash", "git push origin master", cwd="/tmp", exit_code=0))
        d = record["details"]
        self.assertEqual(d["tool"], "Bash")
        self.assertIn("git push", d["command"])
        self.assertEqual(d["exit_code"], 0)
        self.assertIn("git push", d["high_impact_patterns_matched"])


class ReasoningSurfaceAttachmentTests(unittest.TestCase):
    """When a surface exists in cwd, its snapshot is attached."""

    def test_surface_snapshot_attached_when_present(self):
        with tempfile.TemporaryDirectory() as project_dir, \
             tempfile.TemporaryDirectory() as home_dir:
            surface_dir = Path(project_dir) / ".episteme"
            surface_dir.mkdir(parents=True)
            surface = {
                "timestamp": "2026-04-20T12:00:00Z",
                "core_question": "Will this push break the build?",
                "unknowns": ["does CI run tests on this branch?"],
                "assumptions": ["green suite locally"],
                "disconfirmation": "pipeline fails within 3m of push",
                "domain": "Complicated",
                "tacit_call": False,
            }
            (surface_dir / "reasoning-surface.json").write_text(
                json.dumps(surface))
            payload = _payload("Bash", "git push", cwd=project_dir)
            home = Path(home_dir)
            with patch("core.hooks.episodic_writer.Path.home", return_value=home):
                rc = ew._should_record(payload)
                record = ew._build_record(payload, rc[1], rc[2])
            rs = record["details"]["reasoning_surface"]
            self.assertEqual(rs["core_question"], surface["core_question"])
            self.assertEqual(rs["domain"], "Complicated")
            self.assertEqual(rs["tacit_call"], False)
            self.assertEqual(record["provenance"]["confidence"], "high",
                             "high confidence when surface + exit present")

    def test_no_surface_lowers_confidence(self):
        with tempfile.TemporaryDirectory() as project_dir, \
             tempfile.TemporaryDirectory() as home_dir:
            payload = _payload("Bash", "git push", cwd=project_dir)
            home = Path(home_dir)
            with patch("core.hooks.episodic_writer.Path.home", return_value=home):
                rc = ew._should_record(payload)
                record = ew._build_record(payload, rc[1], rc[2])
            self.assertNotIn("reasoning_surface", record["details"])
            self.assertEqual(record["provenance"]["confidence"], "medium",
                             "medium confidence when surface missing but exit present")


class RedactionTests(unittest.TestCase):
    """Commands carrying secrets must be redacted before write."""

    def test_aws_key_redacted(self):
        redacted = ew._redact("aws configure set access_key AKIAIOSFODNN7EXAMPLE")
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", redacted)
        self.assertIn("<REDACTED-AWS-KEY>", redacted)

    def test_github_token_redacted(self):
        redacted = ew._redact(
            "git push https://ghp_abcdefghijklmnopqrstuvwxyz123456@github.com/x/y.git")
        self.assertNotIn("ghp_abcdefghijklmnopqrstuvwxyz123456", redacted)

    def test_benign_command_unchanged(self):
        cmd = "git push origin master"
        self.assertEqual(ew._redact(cmd), cmd)


class NeverBlockTests(unittest.TestCase):
    """Any unexpected input must return 0 and write nothing."""

    def _run_with_stdin(self, text: str) -> int:
        with patch("sys.stdin", io.StringIO(text)):
            return ew.main()

    def test_empty_stdin_returns_zero(self):
        self.assertEqual(self._run_with_stdin(""), 0)

    def test_malformed_json_returns_zero(self):
        self.assertEqual(self._run_with_stdin("{ not json"), 0)

    def test_unknown_payload_shape_returns_zero(self):
        self.assertEqual(self._run_with_stdin(json.dumps({"foo": "bar"})), 0)

    def test_bash_no_cmd_returns_zero(self):
        self.assertEqual(self._run_with_stdin(
            json.dumps({"tool_name": "Bash", "tool_input": {}})), 0)


if __name__ == "__main__":
    unittest.main()
