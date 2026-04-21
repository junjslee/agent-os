"""CP6 tests — Layer 4 verification_trace schema in the hot path.

At CP6 the generic blueprint declares ``verification_trace_required:
true``. For any high-impact Bash op matched by HIGH_IMPACT_BASH, the
guard's Layer 4 composition now requires the surface to carry a
parseable ``verification_trace`` with at least one of
``command`` / ``or_dashboard`` / ``or_test`` — AND a strict
``threshold_observable`` when ``command`` is set.

For Fence Reconstruction the blueprint declares
``verification_trace_maps_to: rollback_path`` — the existing
``rollback_path`` surface field is wrapped as a Layer 4 command slot
and smoke-tested (shlex-parse + prod-marker absence +
path-existence against the project tree).

Four other blueprint stubs ship at CP6 — axiomatic_judgment /
consequence_chain / architectural_cascade — each as
``verification_trace_required: false`` with empty selector_triggers.
The hot path does NOT run their field-level validation at RC; the
schema-only shape is registered so the registry + future selectors
can consume it.

Spec: docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md § Layer 4 ·
falsification-trace requirement (blueprint-shaped).
"""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from core.hooks import reasoning_surface_guard as guard
from core.hooks import _verification_trace as vt  # pyright: ignore[reportAttributeAccessIssue]
from core.hooks import _grounding  # pyright: ignore[reportAttributeAccessIssue]
from core.hooks._blueprint_registry import (  # pyright: ignore[reportMissingImports]
    load_registry,
)


# ---------- Helpers ------------------------------------------------------


def _base_surface(
    disconfirmation: str = "CI fails on main after push or tag verification rejects",
    verification_trace: dict | None = None,
) -> dict:
    surface = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "core_question": "Does this change preserve the kernel contract?",
        "knowns": ["tests pass locally"],
        "unknowns": [
            "if CI returns non-zero exit code on the push branch, "
            "local parity was false"
        ],
        "assumptions": ["cwd is repo root"],
        "disconfirmation": disconfirmation,
    }
    if verification_trace is not None:
        surface["verification_trace"] = verification_trace
    return surface


def _write_and_run(
    surface: dict, cwd: Path, command: str
) -> tuple[int, str, str]:
    (cwd / ".episteme").mkdir(exist_ok=True)
    (cwd / ".episteme" / "reasoning-surface.json").write_text(
        json.dumps(surface), encoding="utf-8"
    )
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "cwd": str(cwd),
    }
    raw = json.dumps(payload)
    with patch("sys.stdin", new=io.StringIO(raw)), \
         patch("sys.stdout", new=io.StringIO()) as fake_out, \
         patch("sys.stderr", new=io.StringIO()) as fake_err:
        rc = guard.main()
    return rc, fake_out.getvalue(), fake_err.getvalue()


def _fence_surface(
    rollback: str,
    constraint: str = "core/hooks/_grounding.py:32",
) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "core_question": "Is removing this constraint safe in this context?",
        "knowns": ["CP4 green at 361 tests"],
        "unknowns": [
            "if CI returns non-zero exit code on the push branch, "
            "local parity was false"
        ],
        "assumptions": ["hook runner is Claude Code"],
        "disconfirmation": "CI fails on main after push or tag verification rejects",
        "constraint_identified": constraint,
        "origin_evidence": "Commit e1f49c9 added this to close CP3 gap #9.",
        "removal_consequence_prediction": (
            "if the deep-scan returns non-zero exit code after removal, "
            "ungrounded entities slip past Layer 3"
        ),
        "reversibility_classification": "reversible",
        "rollback_path": rollback,
    }


# ---------- Validator pure function --------------------------------------


class VerificationTraceValidator(unittest.TestCase):
    """Unit tests for the pure validate_trace function."""

    def test_valid_command_with_observable_passes(self):
        trace = vt.VerificationTrace(
            command="curl -s https://api.example.com/health",
            threshold_observable="http_code == 200",
        )
        verdict, _detail = vt.validate_trace(trace)
        self.assertEqual(verdict, "valid")

    def test_bare_single_word_command_rejects(self):
        trace = vt.VerificationTrace(
            command="verify",
            threshold_observable="exit_code == 0",
        )
        verdict, detail = vt.validate_trace(trace)
        self.assertEqual(verdict, "unparseable_command")
        self.assertIn(">= 2 tokens", detail)

    def test_unclosed_quote_command_rejects(self):
        trace = vt.VerificationTrace(command='echo "unclosed')
        verdict, detail = vt.validate_trace(trace)
        self.assertEqual(verdict, "unparseable_command")
        self.assertIn("shell-parseable", detail)

    def test_valid_http_dashboard_passes(self):
        trace = vt.VerificationTrace(
            or_dashboard="https://grafana.internal/d/api-latency"
        )
        verdict, _detail = vt.validate_trace(trace)
        self.assertEqual(verdict, "valid")

    def test_bare_string_dashboard_rejects(self):
        trace = vt.VerificationTrace(or_dashboard="grafana dashboard")
        verdict, detail = vt.validate_trace(trace)
        self.assertEqual(verdict, "shape_invalid")
        self.assertIn("or_dashboard", detail)

    def test_ftp_scheme_dashboard_rejects(self):
        trace = vt.VerificationTrace(or_dashboard="ftp://example.com/dash")
        verdict, detail = vt.validate_trace(trace)
        self.assertEqual(verdict, "shape_invalid")

    def test_pytest_id_passes(self):
        trace = vt.VerificationTrace(
            or_test="tests/test_foo.py::test_bar"
        )
        verdict, _detail = vt.validate_trace(trace)
        self.assertEqual(verdict, "valid")

    def test_unittest_id_passes(self):
        trace = vt.VerificationTrace(
            or_test="package.module.TestClass.test_method"
        )
        verdict, _detail = vt.validate_trace(trace)
        self.assertEqual(verdict, "valid")

    def test_makefile_target_in_or_test_rejects(self):
        trace = vt.VerificationTrace(or_test="make test")
        verdict, detail = vt.validate_trace(trace)
        self.assertEqual(verdict, "shape_invalid")
        self.assertIn("pytest", detail)  # message names the accepted shape

    def test_all_slots_empty_rejects(self):
        trace = vt.VerificationTrace()
        verdict, detail = vt.validate_trace(trace)
        self.assertEqual(verdict, "shape_invalid")
        self.assertIn("command", detail)

    def test_absent_trace_returns_absent(self):
        verdict, detail = vt.validate_trace(None)
        self.assertEqual(verdict, "absent")
        self.assertIn("not present", detail)

    def test_command_without_observable_rejects(self):
        trace = vt.VerificationTrace(
            command="grep -n error /tmp/log.txt"
        )
        verdict, detail = vt.validate_trace(trace)
        self.assertEqual(verdict, "no_observable")
        self.assertIn("threshold_observable", detail)

    def test_qualitative_observable_rejects_strict_grammar(self):
        trace = vt.VerificationTrace(
            command="curl -s https://x/health",
            threshold_observable="response looks healthy",
        )
        verdict, detail = vt.validate_trace(trace)
        self.assertEqual(verdict, "no_observable")
        self.assertIn("comparison operator", detail)

    def test_threshold_digit_without_operator_rejects(self):
        trace = vt.VerificationTrace(
            command="curl -s https://x/health",
            threshold_observable="response time 400ms",
        )
        verdict, _detail = vt.validate_trace(trace)
        self.assertEqual(verdict, "no_observable")

    def test_threshold_operator_without_digit_rejects(self):
        trace = vt.VerificationTrace(
            command="curl -s https://x/health",
            threshold_observable="result != healthy",
        )
        verdict, _detail = vt.validate_trace(trace)
        self.assertEqual(verdict, "no_observable")

    def test_from_surface_field_non_dict_returns_none(self):
        self.assertIsNone(vt.VerificationTrace.from_surface_field("string"))
        self.assertIsNone(vt.VerificationTrace.from_surface_field(None))
        self.assertIsNone(vt.VerificationTrace.from_surface_field(123))

    def test_from_surface_field_rejects_bool_as_window(self):
        # bool is a subclass of int in Python — must be rejected
        # explicitly so `"window_seconds": true` doesn't silently
        # become `1` second.
        trace = vt.VerificationTrace.from_surface_field(
            {"or_test": "tests/foo.py::test_bar", "window_seconds": True}
        )
        assert trace is not None
        self.assertIsNone(trace.window_seconds)


# ---------- Hot-path integration (generic blueprint) --------------------


class Layer4HotPathGeneric(unittest.TestCase):
    """Generic blueprint + HIGH_IMPACT_BASH composition."""

    def test_high_impact_without_trace_blocks(self):
        surface = _base_surface()
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 2)
        self.assertIn("Layer 4", err)
        self.assertIn("verification_trace", err)

    def test_high_impact_with_valid_trace_passes(self):
        surface = _base_surface(
            verification_trace={
                "or_test": "tests/test_layer4.py::test_push_smoke",
            }
        )
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 0, f"stderr: {err}")

    def test_non_high_impact_without_trace_passes(self):
        # Layer 4 only kicks in for high-impact ops. Low-impact Bash
        # (ls, cat, grep) bypasses the guard entirely at
        # _match_high_impact. This test asserts that the layered
        # architecture does NOT escalate advisory ops to blocked.
        surface = _base_surface()
        with tempfile.TemporaryDirectory() as td:
            rc, out, err = _write_and_run(
                surface, Path(td), "ls -la"
            )
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")
        self.assertEqual(err, "")

    def test_high_impact_with_shape_invalid_trace_blocks(self):
        surface = _base_surface(
            verification_trace={"or_dashboard": "not-a-url"}
        )
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 2)
        self.assertIn("Layer 4", err)
        self.assertIn("or_dashboard", err)

    def test_high_impact_with_unparseable_command_blocks(self):
        surface = _base_surface(
            verification_trace={
                "command": "bad 'quote",
                "threshold_observable": "exit_code == 0",
            }
        )
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 2)
        self.assertIn("Layer 4", err)

    def test_command_without_observable_blocks(self):
        surface = _base_surface(
            verification_trace={"command": "grep -n error /tmp/log.txt"}
        )
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 2)
        self.assertIn("Layer 4", err)
        self.assertIn("threshold_observable", err)

    def test_command_with_valid_observable_passes(self):
        surface = _base_surface(
            verification_trace={
                "command": "curl -s https://health.example.com",
                "threshold_observable": "http_code == 200",
            }
        )
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 0, f"stderr: {err}")


# ---------- Fence rollback smoke test ------------------------------------


class Layer4FenceSmokeTest(unittest.TestCase):
    """Fence blueprint wraps rollback_path as the Layer 4 command
    slot. Smoke test is syntactic + prod-marker absence +
    file-extension-path existence."""

    def setUp(self):
        _grounding._clear_cache_for_tests()

    def tearDown(self):
        _grounding._clear_cache_for_tests()

    def _run_fence(
        self, rollback: str, cwd: Path, constraint: str
    ) -> tuple[int, str, str]:
        # Seed a minimal project tree so Layer 3 (grounds
        # constraint_identified) and Layer 4 (path-existence on
        # rollback path args) have something to check.
        (cwd / "core" / "hooks").mkdir(parents=True, exist_ok=True)
        (cwd / "core" / "hooks" / "_grounding.py").write_text(
            "# grounding\n", encoding="utf-8"
        )
        (cwd / "docs").mkdir(exist_ok=True)
        (cwd / "docs" / "PLAN.md").write_text("# plan\n")
        surface = _fence_surface(rollback, constraint=constraint)
        return _write_and_run(surface, cwd, "rm .episteme/advisory-surface")

    def test_valid_rollback_passes_smoke(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            rc, _out, err = self._run_fence(
                "git revert HEAD and rerun PYTHONPATH=. pytest -q tests/",
                cwd,
                "core/hooks/_grounding.py:32",
            )
        self.assertEqual(rc, 0, f"stderr: {err}")

    def test_rollback_single_token_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            rc, _out, err = self._run_fence(
                "rollback",  # single token, also < 15 chars
                cwd,
                "core/hooks/_grounding.py:32",
            )
        self.assertEqual(rc, 2)
        # Fence structural check runs before Layer 4 smoke test —
        # length minimum fires first. The assertion is simply that
        # the op is refused.
        self.assertIn("rollback_path", err)

    def test_rollback_referencing_prod_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            rc, _out, err = self._run_fence(
                "kubectl rollout undo deployment/api --namespace prod",
                cwd,
                "core/hooks/_grounding.py:32",
            )
        self.assertEqual(rc, 2)
        self.assertIn("Layer 4", err)
        self.assertIn("production marker", err)

    def test_rollback_referencing_nonexistent_file_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            rc, _out, err = self._run_fence(
                "git checkout HEAD -- docs/GONE.md",
                cwd,
                "core/hooks/_grounding.py:32",
            )
        self.assertEqual(rc, 2)
        self.assertIn("Layer 4", err)
        self.assertIn("absent from the project tree", err)

    def test_rollback_bare_directory_passes(self):
        # CP6 path-existence only flags file-extension-shaped tokens;
        # bare directories (`tests/`) and git refs (`HEAD`, `main`)
        # pass. Without this narrow shape rule, rollback commands
        # that legitimately operate on directories would always fail
        # path-existence.
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            rc, _out, err = self._run_fence(
                "git reset --hard HEAD~1 and rm -rf tests/",
                cwd,
                "core/hooks/_grounding.py:32",
            )
        self.assertEqual(rc, 0, f"stderr: {err}")


# ---------- Blueprint stubs structural ------------------------------------


class BlueprintStubsStructural(unittest.TestCase):
    """Registry must load all 5 RC blueprints cleanly; the 3 CP6
    stubs must declare empty selector_triggers (don't fire at RC)
    and carry the required-fields list the spec names."""

    def test_all_five_blueprints_load(self):
        reg = load_registry()
        names = set(reg.known_names())
        self.assertIn("generic", names)
        self.assertIn("fence_reconstruction", names)
        self.assertIn("axiomatic_judgment", names)
        self.assertIn("consequence_chain", names)
        self.assertIn("architectural_cascade", names)

    def test_axiomatic_judgment_schema(self):
        bp = load_registry().get("axiomatic_judgment")
        # Decision arm + synthesis arm, per spec § Blueprint A.
        for f in (
            "sources",
            "conflict_axis",
            "decision_rule",
            "fail_condition_per_source",
            "fallback_if_both_wrong",
            "conflict_cause",
            "context_signature",
            "synthesized_protocol",
            "framework_entry_ref",
            "guidance_trigger",
        ):
            self.assertIn(f, bp.required_fields)
        self.assertTrue(bp.synthesis_arm)
        self.assertEqual(bp.selector_triggers, ())  # doesn't fire at RC
        self.assertFalse(bp.verification_trace_required)

    def test_consequence_chain_schema(self):
        bp = load_registry().get("consequence_chain")
        for f in (
            "first_order_effect",
            "second_order_effect",
            "failure_mode_inversion",
            "base_rate_reference",
            "margin_of_safety",
        ):
            self.assertIn(f, bp.required_fields)
        self.assertFalse(bp.synthesis_arm)
        self.assertEqual(bp.selector_triggers, ())

    def test_architectural_cascade_schema(self):
        bp = load_registry().get("architectural_cascade")
        for f in (
            "flaw_classification",
            "posture_selected",
            "patch_vs_refactor_evaluation",
            "blast_radius_map",
            "sync_plan",
            "deferred_discoveries",
        ):
            self.assertIn(f, bp.required_fields)
        self.assertTrue(bp.synthesis_arm)
        self.assertEqual(bp.selector_triggers, ())  # CP10 populates

    def test_generic_blueprint_requires_verification_trace(self):
        bp = load_registry().get("generic")
        self.assertTrue(bp.verification_trace_required)
        self.assertIsNone(bp.verification_trace_maps_to)

    def test_fence_blueprint_maps_trace_to_rollback_path(self):
        bp = load_registry().get("fence_reconstruction")
        self.assertTrue(bp.verification_trace_required)
        self.assertEqual(bp.verification_trace_maps_to, "rollback_path")


# ---------- Back-compat -------------------------------------------------


class Layer4BackCompat(unittest.TestCase):
    """v0.11.0-shaped surfaces (no verification_trace) pass on
    non-high-impact tool calls and on Write/Edit of non-lockfile
    paths — only high-impact Bash promotes Layer 4 to blocking."""

    def test_write_non_lockfile_with_no_trace_passes(self):
        surface = _base_surface()  # no trace
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / ".episteme").mkdir()
            (cwd / ".episteme" / "reasoning-surface.json").write_text(
                json.dumps(surface), encoding="utf-8"
            )
            payload = {
                "tool_name": "Edit",
                "tool_input": {"file_path": "src/foo.py"},
                "cwd": str(cwd),
            }
            raw = json.dumps(payload)
            with patch("sys.stdin", new=io.StringIO(raw)), \
                 patch("sys.stdout", new=io.StringIO()), \
                 patch("sys.stderr", new=io.StringIO()) as fake_err:
                rc = guard.main()
            self.assertEqual(rc, 0, f"stderr: {fake_err.getvalue()}")

    def test_read_tool_does_not_invoke_layer4(self):
        payload = {
            "tool_name": "Read",
            "tool_input": {"file_path": "README.md"},
            "cwd": "/tmp",
        }
        raw = json.dumps(payload)
        with patch("sys.stdin", new=io.StringIO(raw)), \
             patch("sys.stdout", new=io.StringIO()) as fake_out, \
             patch("sys.stderr", new=io.StringIO()) as fake_err:
            rc = guard.main()
        self.assertEqual(rc, 0)
        self.assertEqual(fake_out.getvalue(), "")
        self.assertEqual(fake_err.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
