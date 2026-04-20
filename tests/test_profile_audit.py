"""Tests for phase 12 profile-audit loop — checkpoint 1 (scaffolding).

Verifies the foundation behaves correctly BEFORE any real axis signature
lands:

- run_audit() returns a well-formed profile-audit-v1 record even when
  every input is missing (empty episodic dir, no profile, no lexicon).
- All 15 axes appear in the output with explicit names matching the
  spec's axis inventory.
- Every axis at checkpoint 1 is `insufficient_evidence` with a reason
  pointing to the spec's sketch table (readable audit log per approved
  decision #2 on open questions).
- JSON-serializable output (matches the profile-audit-v1 JSON schema).
- Profile-claim parser handles the real operator_profile.md shape:
  scalar values, list values (dominant_lens), and dict values
  (noise_signature primary/secondary, decision_cadence tempo/commit_after).
- Lexicon loader reads `## <name>` sections with bullet-list terms.
- Fingerprint is deterministic over identical lexicon contents.
- Record writer is append-only.
- Drift-surfacing helper produces the correct one-line string shape
  per session-context contract, and returns None on missing /
  acknowledged / no-drift records.

Synthetic fixtures per approved tactical lean #1: mechanical correctness
of scaffolding is exercised with fabricated inputs; cognitive-drift
signatures will be exercised against real-tier dogfood in checkpoint 5.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from episteme import _profile_audit as pa


class RunAuditScaffoldingTests(unittest.TestCase):
    """All-empty-inputs path: proves the scaffolding never crashes."""

    def test_run_audit_with_everything_missing_returns_well_formed_record(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = pa.run_audit(
                episodic_dir=root / "episodic",          # does not exist
                reflective_dir=root / "reflective",
                profile_path=root / "no_profile.md",      # does not exist
                lexicon_path=root / "no_lexicon.md",      # does not exist
                since_days=30,
            )

        # Envelope fields
        self.assertEqual(result["version"], "profile-audit-v1")
        self.assertRegex(result["run_id"], r"^audit-\d{8}-\d{6}-[0-9a-f]{4}$")
        self.assertIn("run_ts", result)
        self.assertEqual(result["episodic_window"], "30d")
        self.assertRegex(result["lexicon_fingerprint"], r"^[0-9a-f]{16}$")
        self.assertFalse(result["acknowledged"])

        # Exactly 15 axes, names match the spec's axis inventory
        axes = result["axes"]
        self.assertEqual(len(axes), 15)
        names = [a["axis_name"] for a in axes]
        self.assertEqual(names, list(pa.ALL_AXES))
        self.assertEqual(set(names), set(pa.PROCESS_AXES) | set(pa.COGNITIVE_AXES))

        # Every axis is insufficient_evidence at checkpoint 1 and
        # points back to the spec's sketch table (per approved decision
        # #2: per-axis explicit stubs, not a generic fallback).
        for a in axes:
            self.assertEqual(a["verdict"], "insufficient_evidence")
            self.assertEqual(a["evidence_count"], 0)
            self.assertEqual(a["signatures"], {})
            self.assertEqual(a["signature_predictions"], {})
            self.assertEqual(a["evidence_refs"], [])
            self.assertIsNone(a["suggested_reelicitation"])
            self.assertIn("DESIGN_V0_11_PHASE_12", a["reason"])

    def test_run_audit_output_is_json_serializable(self):
        """Scaffolding must emit profile-audit-v1 records that serialize
        cleanly — otherwise `--json` output and `--write` persistence break."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = pa.run_audit(
                episodic_dir=root / "e",
                profile_path=root / "p.md",
                lexicon_path=root / "l.md",
                since_days=7,
            )
            raw = json.dumps(result, ensure_ascii=False)
            roundtrip = json.loads(raw)
            self.assertEqual(roundtrip["version"], "profile-audit-v1")
            self.assertEqual(len(roundtrip["axes"]), 15)


class EpisodicLoaderTests(unittest.TestCase):
    """Input loader for phase 10 episodic records."""

    def test_loader_handles_absent_directory(self):
        with tempfile.TemporaryDirectory() as td:
            records = pa._load_episodic_records(
                Path(td) / "missing",
                since_days=30,
                now=datetime.now(timezone.utc),
            )
            self.assertEqual(records, [])

    def test_loader_skips_malformed_lines_silently(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            p = d / "2026-04-20.jsonl"
            p.write_text(
                '{"ts":"2026-04-20T10:00:00+00:00","event":"ok"}\n'
                'this is not json\n'
                '{"ts":"2026-04-20T10:00:01+00:00","event":"ok2"}\n'
                '\n'  # blank
                '"a string, not an object"\n',
                encoding="utf-8",
            )
            records = pa._load_episodic_records(
                d, since_days=365, now=datetime(2026, 4, 20, 11, tzinfo=timezone.utc)
            )
            # Only the two valid dict-shaped records survive.
            self.assertEqual(len(records), 2)
            self.assertEqual({r["event"] for r in records}, {"ok", "ok2"})

    def test_loader_applies_since_days_window(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            p = d / "records.jsonl"
            p.write_text(
                '{"ts":"2026-01-01T00:00:00+00:00","event":"old"}\n'
                '{"ts":"2026-04-19T00:00:00+00:00","event":"new"}\n',
                encoding="utf-8",
            )
            records = pa._load_episodic_records(
                d, since_days=30, now=datetime(2026, 4, 20, tzinfo=timezone.utc)
            )
            self.assertEqual([r["event"] for r in records], ["new"])


class ProfileClaimParserTests(unittest.TestCase):
    """Parses the operator_profile.md YAML-ish shape without pyyaml dep."""

    PROFILE_SAMPLE = """
# Operator Profile

Some prose.

```
planning_strictness:
  value: 4
  confidence: elicited

risk_tolerance:
  value: 2
  confidence: elicited

dominant_lens:
  value: [failure-first, causal-chain, first-principles]
  confidence: inferred

noise_signature:
  primary: status-pressure
  secondary: false-urgency
  confidence: inferred

decision_cadence:
  tempo: medium
  commit_after: evidence
  confidence: inferred

abstraction_entry:
  value: purpose-first
  confidence: elicited
```
"""

    def test_parses_all_known_axis_shapes(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "profile.md"
            p.write_text(self.PROFILE_SAMPLE, encoding="utf-8")
            claims = pa._load_profile_claims(p)

        # Integer scalar
        self.assertEqual(claims["planning_strictness"], 4)
        self.assertEqual(claims["risk_tolerance"], 2)
        # List (dominant_lens)
        self.assertEqual(
            claims["dominant_lens"],
            ["failure-first", "causal-chain", "first-principles"],
        )
        # Dict with primary/secondary
        self.assertEqual(
            claims["noise_signature"],
            {"primary": "status-pressure", "secondary": "false-urgency"},
        )
        # Dict with tempo/commit_after
        self.assertEqual(
            claims["decision_cadence"],
            {"tempo": "medium", "commit_after": "evidence"},
        )
        # String value
        self.assertEqual(claims["abstraction_entry"], "purpose-first")
        # Axis not in the sample → None
        self.assertIsNone(claims["fence_discipline"])

    def test_absent_profile_returns_all_none(self):
        claims = pa._load_profile_claims(Path("/nonexistent/profile.md"))
        self.assertEqual(set(claims.keys()), set(pa.ALL_AXES))
        for v in claims.values():
            self.assertIsNone(v)


class LexiconLoaderTests(unittest.TestCase):
    def test_loads_valid_sections_skips_prose_h2s(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "lex.md"
            p.write_text(
                "# Top heading — ignored\n"
                "\n"
                "Prose prose prose.\n"
                "\n"
                "## failure_frame\n"
                "\n"
                "- fails\n"
                "- breaks\n"
                "- TIMEOUT\n"  # case-insensitized
                "\n"
                "## not_a_real_lexicon\n"
                "\n"
                "- should-be-skipped\n"
                "\n"
                "## buzzword\n"
                "\n"
                "- robust\n"
                "- seamless\n",
                encoding="utf-8",
            )
            lex = pa._load_lexicon(p)

        self.assertIn("failure_frame", lex)
        self.assertIn("buzzword", lex)
        self.assertNotIn("not_a_real_lexicon", lex)
        self.assertEqual(lex["failure_frame"], frozenset({"fails", "breaks", "timeout"}))
        self.assertEqual(lex["buzzword"], frozenset({"robust", "seamless"}))

    def test_fingerprint_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            a = Path(td) / "a.md"
            b = Path(td) / "b.md"
            content = "## failure_frame\n- fails\n- breaks\n"
            a.write_text(content, encoding="utf-8")
            b.write_text(content, encoding="utf-8")
            fp_a = pa._lexicon_fingerprint(pa._load_lexicon(a))
            fp_b = pa._lexicon_fingerprint(pa._load_lexicon(b))
            self.assertEqual(fp_a, fp_b)
            self.assertEqual(len(fp_a), 16)

    def test_fingerprint_changes_on_content_change(self):
        with tempfile.TemporaryDirectory() as td:
            a = Path(td) / "a.md"
            b = Path(td) / "b.md"
            a.write_text("## failure_frame\n- fails\n", encoding="utf-8")
            b.write_text("## failure_frame\n- fails\n- breaks\n", encoding="utf-8")
            fp_a = pa._lexicon_fingerprint(pa._load_lexicon(a))
            fp_b = pa._lexicon_fingerprint(pa._load_lexicon(b))
            self.assertNotEqual(fp_a, fp_b)


class OutputPersistenceTests(unittest.TestCase):
    def test_write_audit_record_is_append_only(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            rec_a = {"version": "profile-audit-v1", "run_id": "audit-20260420-100000-aaaa", "axes": []}
            rec_b = {"version": "profile-audit-v1", "run_id": "audit-20260420-100001-bbbb", "axes": []}
            path = pa.write_audit_record(rec_a, reflective_dir=d)
            pa.write_audit_record(rec_b, reflective_dir=d)
            self.assertTrue(path.exists())
            lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln]
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[0])["run_id"], rec_a["run_id"])
            self.assertEqual(json.loads(lines[1])["run_id"], rec_b["run_id"])

    def test_read_latest_audit_returns_last_line(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            pa.write_audit_record({"run_id": "first", "axes": []}, reflective_dir=d)
            pa.write_audit_record({"run_id": "second", "axes": []}, reflective_dir=d)
            pa.write_audit_record({"run_id": "third", "axes": []}, reflective_dir=d)
            rec = pa.read_latest_audit(reflective_dir=d)
            self.assertIsNotNone(rec)
            self.assertEqual(rec["run_id"], "third")

    def test_read_latest_audit_returns_none_when_absent(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(pa.read_latest_audit(reflective_dir=Path(td)))


class DriftSurfacingTests(unittest.TestCase):
    """Contract between run_audit output and session_context.py surfacing."""

    def test_surface_line_is_none_when_no_record(self):
        self.assertIsNone(pa.surface_drift_line(None))
        self.assertIsNone(pa.surface_drift_line({}))

    def test_surface_line_is_none_when_acknowledged(self):
        rec = {
            "run_id": "audit-x",
            "acknowledged": True,
            "axes": [{"axis_name": "fence_discipline", "verdict": "drift", "reason": "r"}],
        }
        self.assertIsNone(pa.surface_drift_line(rec))

    def test_surface_line_is_none_when_no_drift(self):
        rec = {
            "run_id": "audit-x",
            "acknowledged": False,
            "axes": [
                {"axis_name": "fence_discipline", "verdict": "aligned"},
                {"axis_name": "dominant_lens", "verdict": "insufficient_evidence"},
            ],
        }
        self.assertIsNone(pa.surface_drift_line(rec))

    def test_single_drift_produces_axis_named_line(self):
        rec = {
            "run_id": "audit-20260420-100000-aaaa",
            "acknowledged": False,
            "axes": [{
                "axis_name": "fence_discipline",
                "verdict": "drift",
                "reason": "constraint-removal records missing reconstruction",
            }],
        }
        line = pa.surface_drift_line(rec)
        self.assertIsNotNone(line)
        self.assertIn("profile-audit: drift on fence_discipline", line)
        self.assertIn("audit-20260420-100000-aaaa", line)

    def test_many_drifts_collapse_to_count(self):
        axes = [
            {"axis_name": f"axis_{i}", "verdict": "drift", "reason": "r"}
            for i in range(7)
        ]
        rec = {"run_id": "audit-x", "acknowledged": False, "axes": axes}
        line = pa.surface_drift_line(rec)
        self.assertIsNotNone(line)
        self.assertIn("drift on 7 axes", line)


class SessionContextIntegrationTests(unittest.TestCase):
    """End-to-end: profile_audit.jsonl on disk → session_context hook
    emits a one-line drift signal. Exercises the actual hook function,
    not the library's surface_drift_line helper (they are structurally
    twins; both must agree)."""

    def test_hook_surfaces_drift_from_real_jsonl(self):
        import os
        import sys
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            reflective = home / ".episteme" / "memory" / "reflective"
            reflective.mkdir(parents=True)
            record = {
                "version": "profile-audit-v1",
                "run_id": "audit-20260420-123000-cafe",
                "run_ts": "2026-04-20T12:30:00+00:00",
                "episodic_window": "30d",
                "lexicon_fingerprint": "0123456789abcdef",
                "acknowledged": False,
                "axes": [{
                    "axis_name": "fence_discipline",
                    "verdict": "drift",
                    "reason": "constraint-removals lacking reconstruction",
                }],
            }
            (reflective / "profile_audit.jsonl").write_text(
                json.dumps(record) + "\n", encoding="utf-8"
            )

            # Import the hook module fresh with a mocked HOME.
            hook_path = Path(__file__).resolve().parents[1] / "core" / "hooks"
            sys.path.insert(0, str(hook_path))
            try:
                if "session_context" in sys.modules:
                    del sys.modules["session_context"]
                with patch.dict(os.environ, {"HOME": str(home)}), \
                     patch("pathlib.Path.home", return_value=home):
                    import session_context
                    line = session_context._profile_audit_line()
            finally:
                sys.path.remove(str(hook_path))
                sys.modules.pop("session_context", None)

            self.assertIsNotNone(line)
            self.assertIn("profile-audit: drift on fence_discipline", line)
            self.assertIn("audit-20260420-123000-cafe", line)

    def test_hook_silent_on_acknowledged_record(self):
        import sys
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            reflective = home / ".episteme" / "memory" / "reflective"
            reflective.mkdir(parents=True)
            record = {
                "run_id": "audit-x",
                "acknowledged": True,
                "axes": [{"axis_name": "fence_discipline", "verdict": "drift", "reason": "r"}],
            }
            (reflective / "profile_audit.jsonl").write_text(
                json.dumps(record) + "\n", encoding="utf-8"
            )

            hook_path = Path(__file__).resolve().parents[1] / "core" / "hooks"
            sys.path.insert(0, str(hook_path))
            try:
                if "session_context" in sys.modules:
                    del sys.modules["session_context"]
                with patch("pathlib.Path.home", return_value=home):
                    import session_context
                    line = session_context._profile_audit_line()
            finally:
                sys.path.remove(str(hook_path))
                sys.modules.pop("session_context", None)

            self.assertIsNone(line)


class TextReportRendererTests(unittest.TestCase):
    def test_empty_record_renders_without_crashing(self):
        text = pa.render_text_report({
            "run_id": "audit-x",
            "run_ts": "2026-04-20T00:00:00+00:00",
            "episodic_window": "30d",
            "lexicon_fingerprint": "0123456789abcdef",
            "axes": [],
        })
        self.assertIn("Profile Audit", text)
        self.assertIn("audit-x", text)

    def test_checkpoint_1_shape_renders_all_15_as_insufficient(self):
        """Checkpoint 1's default output: every axis under the
        'Insufficient evidence' header."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = pa.run_audit(
                episodic_dir=root / "e",
                profile_path=root / "p.md",
                lexicon_path=root / "l.md",
            )
        text = pa.render_text_report(result)
        self.assertIn("## Insufficient evidence", text)
        self.assertIn("**0** in drift", text)
        self.assertIn("**15** insufficient_evidence", text)
        # No drift or aligned sections when empty
        self.assertNotIn("## Drift", text)
        self.assertNotIn("## Aligned", text)


if __name__ == "__main__":
    unittest.main()
