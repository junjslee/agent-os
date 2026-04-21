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


# ---------------------------------------------------------------------------
# Axis C · fence_discipline (checkpoint 2)
# ---------------------------------------------------------------------------
#
# These tests exercise:
#   - _is_constraint_removal glob + verb co-occurrence
#   - _has_reconstruction / _has_counterfactual text probes
#   - insufficient_evidence below the 5-record minimum
#   - aligned when both S1 and S2 clear thresholds
#   - drift on S1-only catastrophic miss (named D1 exception)
#   - drift on S2-only catastrophic miss (named D1 exception)
#   - evidence_refs capture + 20-item cap
#   - signature_predictions shape per claim level
#   - end-to-end via run_audit against the fence_discipline axis

def _make_removal_record(
    command: str,
    *,
    correlation_id: str,
    knowns: list[str] | None = None,
    assumptions: list[str] | None = None,
    unknowns: list[str] | None = None,
    disconfirmation: str | None = None,
) -> dict:
    """Build an episodic record shaped like core/hooks/episodic_writer.py's
    output, with a reasoning-surface snapshot attached."""
    surface: dict = {}
    if knowns is not None:
        surface["knowns"] = knowns
    if assumptions is not None:
        surface["assumptions"] = assumptions
    if unknowns is not None:
        surface["unknowns"] = unknowns
    if disconfirmation is not None:
        surface["disconfirmation"] = disconfirmation

    details: dict = {
        "tool": "Bash",
        "command": command,
        "cwd": "/tmp/fixture",
        "exit_code": 0,
        "status": "success",
        "high_impact_patterns_matched": [],
    }
    if surface:
        details["reasoning_surface"] = surface

    return {
        "id": f"fixture-{correlation_id}",
        "memory_class": "episodic",
        "summary": "fixture: constraint removal",
        "details": details,
        "provenance": {
            "source_type": "agent",
            "source_ref": "tests/test_profile_audit.py",
            "captured_at": "2026-04-20T00:00:00+00:00",
            "captured_by": "fixture",
            "confidence": "high",
            "evidence_refs": [f"correlation_id:{correlation_id}"],
        },
        "status": "active",
        "version": "memory-contract-v1",
        "tags": ["high-impact", "bash"],
        "session_id": "fixture-session",
        "event_type": "action",
    }


class FenceDisciplineConstraintDetectionTests(unittest.TestCase):
    """_is_constraint_removal: path-glob AND removal-verb co-occurrence."""

    def test_rm_on_episteme_policy_is_removal(self):
        rec = _make_removal_record("rm .episteme/policy.md", correlation_id="r1")
        self.assertTrue(pa._is_constraint_removal(rec))

    def test_git_rm_on_core_hooks_is_removal(self):
        rec = _make_removal_record(
            "git rm core/hooks/reasoning_surface_guard.py", correlation_id="r2"
        )
        self.assertTrue(pa._is_constraint_removal(rec))

    def test_sed_inplace_on_constitution_is_removal(self):
        rec = _make_removal_record(
            "sed -i 's/must/may/' kernel/CONSTITUTION.md", correlation_id="r3"
        )
        self.assertTrue(pa._is_constraint_removal(rec))

    def test_lockfile_overwrite_is_removal(self):
        rec = _make_removal_record(
            "echo '{}' > package-lock.json", correlation_id="r4"
        )
        self.assertTrue(pa._is_constraint_removal(rec))

    def test_removal_verb_without_constraint_path_does_not_match(self):
        rec = _make_removal_record("rm /tmp/garbage.txt", correlation_id="r5")
        self.assertFalse(pa._is_constraint_removal(rec))

    def test_constraint_path_without_removal_verb_does_not_match(self):
        # Reading / greping a constraint file is not a removal.
        rec = _make_removal_record(
            "grep -n 'must' kernel/CONSTITUTION.md", correlation_id="r6"
        )
        self.assertFalse(pa._is_constraint_removal(rec))

    def test_append_redirect_is_not_removal(self):
        # `>>` append must not trip the `>` overwrite regex.
        rec = _make_removal_record(
            "echo 'note' >> .episteme/notes.md", correlation_id="r7"
        )
        self.assertFalse(pa._is_constraint_removal(rec))

    def test_non_bash_record_is_not_removal(self):
        rec = {"details": {"tool": "Read", "path": ".episteme/policy.md"}}
        self.assertFalse(pa._is_constraint_removal(rec))

    def test_malformed_record_does_not_crash(self):
        self.assertFalse(pa._is_constraint_removal({}))
        self.assertFalse(pa._is_constraint_removal({"details": "nope"}))
        self.assertFalse(pa._is_constraint_removal({"details": {}}))


class FenceDisciplineTextProbeTests(unittest.TestCase):
    """_has_reconstruction + _has_counterfactual on reasoning-surface fields."""

    def test_reconstruction_phrase_in_knowns_detected(self):
        rec = _make_removal_record(
            "rm .episteme/forbidden.txt",
            correlation_id="t1",
            knowns=[
                "This constraint exists because we had a leaked-token "
                "incident on 2026-02-03 (see audit entry)."
            ],
        )
        self.assertTrue(pa._has_reconstruction(rec))

    def test_commit_sha_in_knowns_detected_as_reconstruction(self):
        rec = _make_removal_record(
            "rm .episteme/legacy.md",
            correlation_id="t2",
            knowns=["Added in commit 9c26201 per review discussion."],
        )
        self.assertTrue(pa._has_reconstruction(rec))

    def test_bare_knowns_without_reconstruction_fails(self):
        rec = _make_removal_record(
            "rm .episteme/legacy.md",
            correlation_id="t3",
            knowns=["we no longer need this file"],
        )
        self.assertFalse(pa._has_reconstruction(rec))

    def test_missing_surface_fails_reconstruction_and_counterfactual(self):
        rec = _make_removal_record("rm .episteme/x", correlation_id="t4")
        self.assertFalse(pa._has_reconstruction(rec))
        self.assertFalse(pa._has_counterfactual(rec))

    def test_counterfactual_in_assumptions_detected(self):
        rec = _make_removal_record(
            "rm .episteme/guard.md",
            correlation_id="t5",
            assumptions=["If we remove this, the pre-commit check no longer fires."],
        )
        self.assertTrue(pa._has_counterfactual(rec))

    def test_counterfactual_in_unknowns_detected(self):
        rec = _make_removal_record(
            "rm .episteme/guard.md",
            correlation_id="t6",
            unknowns=["What would break if removed: the telemetry stops capturing exit codes."],
        )
        self.assertTrue(pa._has_counterfactual(rec))

    def test_counterfactual_blast_radius_phrase(self):
        rec = _make_removal_record(
            "rm core/hooks/legacy.py",
            correlation_id="t7",
            assumptions=["blast radius: downstream hook x, y, z"],
        )
        self.assertTrue(pa._has_counterfactual(rec))


class FenceDisciplineHandlerTests(unittest.TestCase):
    """End-to-end on _axis_fence_discipline dispatched via _AXIS_HANDLERS."""

    @staticmethod
    def _aligned_record(correlation_id: str) -> dict:
        return _make_removal_record(
            f"rm .episteme/rule_{correlation_id}.md",
            correlation_id=correlation_id,
            knowns=[
                f"this constraint exists because of incident {correlation_id} "
                f"(see audit entry)"
            ],
            assumptions=[
                "if we remove this, the ingest pipeline no longer fails closed"
            ],
        )

    @staticmethod
    def _s1_missing_record(correlation_id: str) -> dict:
        # No reconstruction, but has counterfactual — S1 catastrophic miss.
        return _make_removal_record(
            f"rm .episteme/rule_{correlation_id}.md",
            correlation_id=correlation_id,
            knowns=["no longer needed"],
            assumptions=["removing this would impact the ingest pipeline"],
        )

    @staticmethod
    def _s2_missing_record(correlation_id: str) -> dict:
        # Reconstruction present, no counterfactual — S2 catastrophic miss.
        return _make_removal_record(
            f"rm .episteme/rule_{correlation_id}.md",
            correlation_id=correlation_id,
            knowns=[
                f"this constraint exists because of incident {correlation_id}"
            ],
            assumptions=["housekeeping"],
        )

    def test_insufficient_evidence_below_minimum(self):
        records = [self._aligned_record(f"r{i}") for i in range(4)]
        out = pa._axis_fence_discipline("fence_discipline", 4, records, {})
        self.assertEqual(out["verdict"], "insufficient_evidence")
        self.assertEqual(out["evidence_count"], 4)
        self.assertEqual(out["signatures"], {})
        self.assertIn("Only 4 constraint-removal", out["reason"])
        self.assertIn("DESIGN_V0_11_PHASE_12", out["reason"])
        # Claim-dependent predictions are still populated so the record is
        # readable even when verdict is insufficient_evidence. For claim 4
        # the S1 band is [0.70, 1.00] — low bound doubles as drift floor.
        self.assertIn("S1_reconstruction_rate", out["signature_predictions"])
        self.assertEqual(
            out["signature_predictions"]["S1_reconstruction_rate"], [0.70, 1.00]
        )

    def test_non_removal_records_do_not_count_toward_minimum(self):
        # Seven records, but none are constraint-removals → evidence_count=0.
        records = [
            _make_removal_record("git push origin main", correlation_id=f"r{i}")
            for i in range(7)
        ]
        out = pa._axis_fence_discipline("fence_discipline", 4, records, {})
        self.assertEqual(out["verdict"], "insufficient_evidence")
        self.assertEqual(out["evidence_count"], 0)

    def test_aligned_when_both_signatures_above_threshold(self):
        records = [self._aligned_record(f"r{i}") for i in range(8)]
        out = pa._axis_fence_discipline("fence_discipline", 4, records, {})
        self.assertEqual(out["verdict"], "aligned")
        self.assertEqual(out["evidence_count"], 8)
        self.assertEqual(out["signatures"]["S1_reconstruction_rate"], 1.0)
        self.assertEqual(out["signatures"]["S2_review_trace_rate"], 1.0)
        self.assertIsNone(out["suggested_reelicitation"])
        # Confidence rises with evidence: medium below 10, high at/above 10.
        self.assertEqual(out["confidence"], "medium")

    def test_confidence_is_high_at_or_above_ten_records(self):
        records = [self._aligned_record(f"r{i}") for i in range(12)]
        out = pa._axis_fence_discipline("fence_discipline", 4, records, {})
        self.assertEqual(out["confidence"], "high")

    def test_drift_on_s1_only_miss_catastrophic_exception(self):
        # All 6 records carry counterfactual (S2 passes) but none carry
        # reconstruction (S1 = 0% < 70%). Spec §Axis C explicitly permits
        # single-signature flagging on this axis.
        records = [self._s1_missing_record(f"r{i}") for i in range(6)]
        out = pa._axis_fence_discipline("fence_discipline", 4, records, {})
        self.assertEqual(out["verdict"], "drift")
        self.assertEqual(out["signatures"]["S1_reconstruction_rate"], 0.0)
        self.assertEqual(out["signatures"]["S2_review_trace_rate"], 1.0)
        self.assertIn("reconstruction rate", out["reason"])
        self.assertIn("single-signature flagging", out["reason"])
        self.assertIsNotNone(out["suggested_reelicitation"])

    def test_drift_on_s2_only_miss_catastrophic_exception(self):
        # All 6 records carry reconstruction (S1 passes) but none carry
        # counterfactual (S2 = 0% < 50%).
        records = [self._s2_missing_record(f"r{i}") for i in range(6)]
        out = pa._axis_fence_discipline("fence_discipline", 4, records, {})
        self.assertEqual(out["verdict"], "drift")
        self.assertEqual(out["signatures"]["S1_reconstruction_rate"], 1.0)
        self.assertEqual(out["signatures"]["S2_review_trace_rate"], 0.0)
        self.assertIn("review-trace rate", out["reason"])

    def test_s1_at_exactly_threshold_does_not_drift(self):
        # 7/10 = 70% — at the boundary; < means drift, so equal is aligned.
        records: list[dict] = []
        for i in range(7):
            records.append(self._aligned_record(f"pass-{i}"))
        for i in range(3):
            records.append(self._s1_missing_record(f"fail-{i}"))
        out = pa._axis_fence_discipline("fence_discipline", 4, records, {})
        self.assertEqual(out["signatures"]["S1_reconstruction_rate"], 0.7)
        # S2 is 10/10 here (all records carry assumptions — the s1_missing
        # records carry a counterfactual phrase). Boundary on S1 → aligned.
        self.assertEqual(out["verdict"], "aligned")

    def test_evidence_refs_capped_at_twenty(self):
        # Build 25 removal records; only 20 refs should make it into the output.
        records = [self._aligned_record(f"r{i:03d}") for i in range(25)]
        out = pa._axis_fence_discipline("fence_discipline", 4, records, {})
        self.assertEqual(out["evidence_count"], 25)
        self.assertEqual(len(out["evidence_refs"]), 20)
        # First 20 in insertion order (fixture is deterministic).
        self.assertEqual(out["evidence_refs"][0], "r000")
        self.assertEqual(out["evidence_refs"][19], "r019")


class FenceDisciplinePredictionsTests(unittest.TestCase):
    """Claim-dependent prediction bands. The [low, high] shape now means
    [drift_floor, ideal_ceiling] — observed < low ⇒ drift, within ⇒
    aligned. This frames the threshold as claim-relative, matching
    spec's 'drift is the delta between claim and reality' principle."""

    def test_claim_4_matches_spec_axis_c_absolute_threshold(self):
        # Spec §Axis C names absolute thresholds 0.70 / 0.50 for claim 4.
        # The predictions band anchors here, so claim 4 reproduces the
        # spec's exact threshold as its drift floor.
        p = pa._fence_discipline_predictions(4)
        self.assertEqual(p["S1_reconstruction_rate"], [0.70, 1.00])
        self.assertEqual(p["S2_review_trace_rate"], [0.50, 1.00])

    def test_claim_5_is_tightest(self):
        p = pa._fence_discipline_predictions(5)
        self.assertEqual(p["S1_reconstruction_rate"], [0.90, 1.00])
        self.assertEqual(p["S2_review_trace_rate"], [0.90, 1.00])

    def test_claim_0_has_zero_floor_cannot_drift(self):
        # User-specified semantic: claim 0 + 10% observed = aligned.
        # Floor at 0.0 makes drift mathematically impossible for claim 0 —
        # the operator's own declaration already names near-absent practice.
        p = pa._fence_discipline_predictions(0)
        self.assertEqual(p["S1_reconstruction_rate"], [0.00, 0.30])
        self.assertEqual(p["S2_review_trace_rate"], [0.00, 0.15])

    def test_claim_3_has_intermediate_floor(self):
        p = pa._fence_discipline_predictions(3)
        self.assertEqual(p["S1_reconstruction_rate"], [0.50, 0.80])

    def test_out_of_range_claim_clamps(self):
        # Defensive: a malformed profile claiming fence_discipline: 99
        # still yields a usable band rather than a KeyError.
        p_high = pa._fence_discipline_predictions(99)
        self.assertEqual(p_high["S1_reconstruction_rate"], [0.90, 1.00])
        p_low = pa._fence_discipline_predictions(-3)
        self.assertEqual(p_low["S1_reconstruction_rate"], [0.00, 0.30])

    def test_no_claim_returns_empty_predictions(self):
        self.assertEqual(pa._fence_discipline_predictions(None), {})
        self.assertEqual(pa._fence_discipline_predictions("4"), {})


class FenceDisciplineClaimRelativeDriftTests(unittest.TestCase):
    """Drift is the delta between claim and lived record — it MUST scale
    with the declared score. An operator who claims poor fence discipline
    and exhibits poor practice is aligned; an operator who claims strong
    practice and exhibits poor practice drifts. These tests pin that
    semantic so absolute-threshold drift cannot sneak back in."""

    def test_claim_0_with_low_reconstruction_is_aligned(self):
        # 10% reconstruction rate against claim=0 (band floor 0.0) is
        # aligned — the operator's claim already names this behavior.
        # Under the old absolute-threshold code this would have drifted.
        records: list[dict] = []
        for i in range(9):
            records.append(FenceDisciplineHandlerTests._s1_missing_record(f"m{i}"))
        records.append(FenceDisciplineHandlerTests._aligned_record("a0"))
        out = pa._axis_fence_discipline("fence_discipline", 0, records, {})
        self.assertEqual(out["signatures"]["S1_reconstruction_rate"], 0.1)
        self.assertEqual(out["verdict"], "aligned")

    def test_claim_4_with_same_low_reconstruction_is_drift(self):
        # Same behavior (10% reconstruction), different claim (4). The
        # band floor for claim=4 is 0.70, so 10% is catastrophic drift.
        # This is the point of claim-relative thresholds.
        records: list[dict] = []
        for i in range(9):
            records.append(FenceDisciplineHandlerTests._s1_missing_record(f"m{i}"))
        records.append(FenceDisciplineHandlerTests._aligned_record("a0"))
        out = pa._axis_fence_discipline("fence_discipline", 4, records, {})
        self.assertEqual(out["signatures"]["S1_reconstruction_rate"], 0.1)
        self.assertEqual(out["verdict"], "drift")
        self.assertIn("claim=4", out["reason"])
        self.assertIn("70% floor", out["reason"])

    def test_claim_3_intermediate_behavior_aligned(self):
        # 60% reconstruction against claim=3 (floor 0.50) is aligned.
        records: list[dict] = []
        for i in range(6):
            records.append(FenceDisciplineHandlerTests._aligned_record(f"a{i}"))
        for i in range(4):
            records.append(FenceDisciplineHandlerTests._s1_missing_record(f"m{i}"))
        out = pa._axis_fence_discipline("fence_discipline", 3, records, {})
        self.assertEqual(out["signatures"]["S1_reconstruction_rate"], 0.6)
        self.assertEqual(out["verdict"], "aligned")

    def test_null_claim_never_drifts_but_surfaces_observations(self):
        # Profile with no declared fence_discipline value — the audit
        # cannot compute a delta, so it does not flag. It still reports
        # the observed rates so the operator can decide whether to
        # elicit a value.
        records = [FenceDisciplineHandlerTests._s1_missing_record(f"m{i}") for i in range(6)]
        out = pa._axis_fence_discipline("fence_discipline", None, records, {})
        self.assertEqual(out["verdict"], "aligned")
        self.assertIn("No numeric fence_discipline claim", out["reason"])
        self.assertEqual(out["signature_predictions"], {})
        # Signatures are still computed — the record is informational.
        self.assertEqual(out["signatures"]["S1_reconstruction_rate"], 0.0)


class FenceDisciplineEndToEndTests(unittest.TestCase):
    """run_audit surfaces Axis C correctly alongside the 14 stubbed axes."""

    def test_run_audit_routes_fence_discipline_to_real_handler(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            # Seed episodic dir with 6 aligned removal records.
            epi = root / "episodic"
            epi.mkdir()
            lines = [
                json.dumps(FenceDisciplineHandlerTests._aligned_record(f"r{i}"))
                for i in range(6)
            ]
            (epi / "2026-04-20.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")

            # Minimal profile declaring fence_discipline: 4.
            prof = root / "profile.md"
            prof.write_text(
                "```\nfence_discipline:\n  value: 4\n  confidence: inferred\n```\n",
                encoding="utf-8",
            )
            result = pa.run_audit(
                episodic_dir=epi,
                reflective_dir=root / "reflective",
                profile_path=prof,
                lexicon_path=root / "lex.md",  # missing → empty lexicon, fine for Axis C
                since_days=3650,  # large window so the fixture passes any ts filter
            )

        axes_by_name = {a["axis_name"]: a for a in result["axes"]}
        fd = axes_by_name["fence_discipline"]
        self.assertEqual(fd["verdict"], "aligned")
        self.assertEqual(fd["claim"], 4)
        self.assertEqual(fd["evidence_count"], 6)
        # The other 14 axes are still stubbed.
        stubbed = [a for name, a in axes_by_name.items() if name != "fence_discipline"]
        self.assertEqual(len(stubbed), 14)
        for a in stubbed:
            self.assertEqual(a["verdict"], "insufficient_evidence")


if __name__ == "__main__":
    unittest.main()
