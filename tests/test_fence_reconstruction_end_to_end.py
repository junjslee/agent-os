"""CP5 tests — Blueprint B (Fence Reconstruction) end-to-end.

Covers:

- YAML parser list-of-dicts extension (one class, targeted unit tests).
- Blueprint registry loads `fence_reconstruction` cleanly.
- Scenario detector compound-AND gate: fires only when removal lexicon
  AND constraint-bearing path both present in a Bash command.
- `_classify_origin_evidence` verdict classes.
- Layer · Fence validation: presence + non-lazy + origin-evidence
  classification + reversibility enum check.
- Irreversible-classification branch: advisory-only + no synthesis.
- End-to-end Pillar 3 synthesis: PreToolUse Fence fire → pending
  marker written → PostToolUse exit 0 → protocol appended to
  ~/.episteme/framework/protocols.jsonl with format_version
  `cp5-pre-chain`. exit != 0 writes nothing; marker is cleaned up.
- Graceful degrade on corrupt marker.

Honest CP5 limit: the write-time gate is `exit_code == 0`. The proper
"rollback-path not triggered within the window" retrospective check
lands at CP7 with `_pending_contracts.py` + Layer 6 TTL audit. CP5's
tests verify the MVP contract; CP7's tests will extend it.
"""
from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from core.hooks import reasoning_surface_guard as guard
from core.hooks import _blueprint_registry as registry  # pyright: ignore[reportAttributeAccessIssue]
from core.hooks import _scenario_detector as detector  # pyright: ignore[reportAttributeAccessIssue]
from core.hooks import _specificity as specificity  # pyright: ignore[reportAttributeAccessIssue]
from core.hooks import _fence_synthesis as fence_synth  # pyright: ignore[reportAttributeAccessIssue]
from core.hooks import fence_synthesis as fence_post_hook  # pyright: ignore[reportAttributeAccessIssue]


# ---------- Fixtures -----------------------------------------------------

def _valid_fence_surface(
    constraint: str = "core/hooks/_grounding.py:32",
    origin: str = "Commit e1f49c9 added this constraint to close CP3 gap #9.",
    consequence: str = (
        "if the deep-scan returns non-zero exit code after removal, "
        "ungrounded entities slip past Layer 3"
    ),
    reversibility: str = "reversible",
    rollback: str = "git revert HEAD and rerun PYTHONPATH=. pytest -q tests/",
) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "core_question": "Is removing this constraint safe in this context?",
        "knowns": ["CP3 landed 2026-04-21 with 340 tests green"],
        "unknowns": [
            "if CI returns non-zero exit code on the push branch, "
            "local parity was false"
        ],
        "assumptions": ["hook runner is Claude Code"],
        "disconfirmation": (
            "CI fails on main after push or tag verification rejects"
        ),
        # Fence-specific fields:
        "constraint_identified": constraint,
        "origin_evidence": origin,
        "removal_consequence_prediction": consequence,
        "reversibility_classification": reversibility,
        "rollback_path": rollback,
    }


def _run_guard(surface: dict, cwd: Path, command: str) -> tuple[int, str, str]:
    (cwd / ".episteme").mkdir(exist_ok=True)
    (cwd / ".episteme" / "reasoning-surface.json").write_text(
        json.dumps(surface), encoding="utf-8"
    )
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "cwd": str(cwd),
        "tool_use_id": "test-use-id-fence-cp5",
    }
    raw = json.dumps(payload)
    with patch("sys.stdin", new=io.StringIO(raw)), \
         patch("sys.stdout", new=io.StringIO()) as fake_out, \
         patch("sys.stderr", new=io.StringIO()) as fake_err:
        rc = guard.main()
    return rc, fake_out.getvalue(), fake_err.getvalue()


def _run_post_hook(
    command: str, exit_code: int, cwd: Path
) -> tuple[int, str, str]:
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "cwd": str(cwd),
        "tool_use_id": "test-use-id-fence-cp5",
        "tool_response": {"exit_code": exit_code},
    }
    raw = json.dumps(payload)
    with patch("sys.stdin", new=io.StringIO(raw)), \
         patch("sys.stdout", new=io.StringIO()) as fake_out, \
         patch("sys.stderr", new=io.StringIO()) as fake_err:
        rc = fence_post_hook.main()
    return rc, fake_out.getvalue(), fake_err.getvalue()


class _EphemeralEpistemeHome:
    """Context manager that points EPISTEME_HOME at a temp dir and
    resets it on exit. Also clears the scenario-detector trigger cache
    in case a prior test mutated blueprint state."""

    def __enter__(self):
        self._home = tempfile.TemporaryDirectory()
        self._prev = os.environ.get("EPISTEME_HOME")
        os.environ["EPISTEME_HOME"] = self._home.name
        detector._reset_trigger_cache_for_tests()
        return Path(self._home.name)

    def __exit__(self, *a):
        if self._prev is None:
            os.environ.pop("EPISTEME_HOME", None)
        else:
            os.environ["EPISTEME_HOME"] = self._prev
        self._home.cleanup()
        detector._reset_trigger_cache_for_tests()


# ---------- YAML parser list-of-dicts extension -------------------------

class TestYAMLListOfDictsExtension(unittest.TestCase):
    """CP5 extended the CP2 zero-dependency YAML parser. Target
    coverage is the exact shape the Fence blueprint uses."""

    def test_parses_list_of_flat_dicts(self):
        data = registry._parse_yaml_subset(
            """
name: test
selector_triggers:
  - a: "alpha"
    b: "beta"
  - a: "gamma"
    b: "delta"
""",
            source=Path("inline"),
        )
        self.assertEqual(data["name"], "test")
        triggers = data["selector_triggers"]
        self.assertEqual(len(triggers), 2)
        self.assertEqual(triggers[0], {"a": "alpha", "b": "beta"})
        self.assertEqual(triggers[1], {"a": "gamma", "b": "delta"})

    def test_scalar_list_still_works(self):
        data = registry._parse_yaml_subset(
            """
required_fields:
  - one
  - two
""",
            source=Path("inline"),
        )
        self.assertEqual(data["required_fields"], ["one", "two"])

    def test_empty_list_shortcut_still_works(self):
        data = registry._parse_yaml_subset(
            "optional_fields: []\n",
            source=Path("inline"),
        )
        self.assertEqual(data["optional_fields"], [])

    def test_nested_list_inside_dict_rejected(self):
        with self.assertRaises(registry.BlueprintParseError):
            registry._parse_yaml_subset(
                """
selector_triggers:
  - key: value
    nested:
      - one
      - two
""",
                source=Path("inline"),
            )


# ---------- Blueprint registry loads fence_reconstruction ---------------

class TestFenceBlueprintLoads(unittest.TestCase):
    def test_fence_blueprint_in_registry(self):
        reg = registry.load_registry()
        bp = reg.get("fence_reconstruction")
        self.assertEqual(bp.name, "fence_reconstruction")
        self.assertEqual(
            bp.required_fields,
            (
                "constraint_identified",
                "origin_evidence",
                "removal_consequence_prediction",
                "reversibility_classification",
                "rollback_path",
            ),
        )
        self.assertTrue(bp.synthesis_arm)
        self.assertGreaterEqual(len(bp.selector_triggers), 1)
        first = bp.selector_triggers[0]
        self.assertIsInstance(first, dict)
        self.assertIn("removal_lexicon_pattern", first)
        self.assertIn("constraint_path_pattern", first)


# ---------- Scenario detector: compound AND gate ------------------------

class TestScenarioDetectorFence(unittest.TestCase):
    def setUp(self):
        detector._reset_trigger_cache_for_tests()

    def tearDown(self):
        detector._reset_trigger_cache_for_tests()

    def test_fence_fires_on_rm_of_episteme_file(self):
        op = {
            "tool_name": "Bash",
            "tool_input": {"command": "rm .episteme/advisory-surface"},
        }
        self.assertEqual(
            detector.detect_scenario(op), "fence_reconstruction"
        )

    def test_fence_fires_on_rm_of_kernel_md(self):
        op = {
            "tool_name": "Bash",
            "tool_input": {"command": "rm kernel/FAILURE_MODES.md"},
        }
        self.assertEqual(
            detector.detect_scenario(op), "fence_reconstruction"
        )

    def test_fence_fires_on_delete_of_ci_workflow(self):
        op = {
            "tool_name": "Bash",
            "tool_input": {"command": "git rm .github/workflows/ci.yml"},
        }
        self.assertEqual(
            detector.detect_scenario(op), "fence_reconstruction"
        )

    def test_routine_rm_without_constraint_path_falls_back(self):
        # rm but no constraint-bearing path → generic.
        op = {
            "tool_name": "Bash",
            "tool_input": {"command": "rm /tmp/scratch_build_output.log"},
        }
        self.assertEqual(detector.detect_scenario(op), "generic")

    def test_routine_episteme_edit_without_removal_verb_falls_back(self):
        # .episteme/ path but no removal verb → generic.
        op = {
            "tool_name": "Bash",
            "tool_input": {"command": "cat .episteme/advisory-surface"},
        }
        self.assertEqual(detector.detect_scenario(op), "generic")

    def test_echo_append_to_episteme_file_falls_back(self):
        # Appending (no removal verb in the command) must NOT fire.
        op = {
            "tool_name": "Bash",
            "tool_input": {
                "command": "echo 'added' >> .episteme/advisory-surface"
            },
        }
        self.assertEqual(detector.detect_scenario(op), "generic")

    def test_non_bash_tool_falls_back(self):
        op = {
            "tool_name": "Edit",
            "tool_input": {"file_path": "rm .episteme/foo"},
        }
        # Non-Bash never fires Fence even if path / lexicon appear.
        self.assertEqual(detector.detect_scenario(op), "generic")


# ---------- origin_evidence classifier ----------------------------------

class TestClassifyOriginEvidence(unittest.TestCase):
    def test_commit_sha_classifies_as_evidence(self):
        self.assertEqual(
            specificity._classify_origin_evidence(
                "See commit e1f49c9 landing CP3 Layer 2 classifier."
            ),
            "evidence",
        )

    def test_path_line_anchor_classifies_as_evidence(self):
        self.assertEqual(
            specificity._classify_origin_evidence(
                "Origin: core/hooks/_grounding.py:32 sets the cache TTL."
            ),
            "evidence",
        )

    def test_incident_id_classifies_as_evidence(self):
        self.assertEqual(
            specificity._classify_origin_evidence(
                "Relates to INC42 — post-mortem logged on 2026-04-15."
            ),
            "evidence",
        )

    def test_url_classifies_as_evidence(self):
        self.assertEqual(
            specificity._classify_origin_evidence(
                "See https://github.com/junjslee/episteme/pull/12 for reasoning."
            ),
            "evidence",
        )

    def test_probably_legacy_classifies_as_legacy(self):
        self.assertEqual(
            specificity._classify_origin_evidence(
                "Unclear — probably legacy from the 0.8 cycle."
            ),
            "legacy",
        )

    def test_dont_remember_classifies_as_legacy(self):
        self.assertEqual(
            specificity._classify_origin_evidence(
                "We don't remember why this was added — just there."
            ),
            "legacy",
        )

    def test_short_classifies_as_unknown(self):
        self.assertEqual(specificity._classify_origin_evidence("x"), "unknown")
        self.assertEqual(specificity._classify_origin_evidence(""), "unknown")

    def test_legacy_beats_evidence_priority(self):
        # A surface that cites a SHA but still hedges "probably legacy"
        # routes to legacy — the hedge is the epistemic claim.
        self.assertEqual(
            specificity._classify_origin_evidence(
                "Commit e1f49c9 added it but unclear — probably legacy reasons"
            ),
            "legacy",
        )


# ---------- Layer · Fence validation ------------------------------------

class TestLayerFenceValidate(unittest.TestCase):
    def test_all_fields_present_reversible_passes(self):
        verdict, _detail = guard._layer_fence_validate(_valid_fence_surface())
        self.assertEqual(verdict, "pass")

    def test_missing_field_rejects(self):
        surface = _valid_fence_surface()
        del surface["rollback_path"]
        verdict, detail = guard._layer_fence_validate(surface)
        self.assertEqual(verdict, "reject")
        self.assertIn("rollback_path", detail)

    def test_lazy_origin_evidence_rejects(self):
        surface = _valid_fence_surface(
            origin="unclear — probably legacy from the 0.8 cycle"
        )
        verdict, detail = guard._layer_fence_validate(surface)
        self.assertEqual(verdict, "reject")
        self.assertIn("origin_evidence", detail)
        self.assertIn("legacy", detail)

    def test_bad_reversibility_enum_rejects(self):
        surface = _valid_fence_surface(reversibility="maybe")
        verdict, detail = guard._layer_fence_validate(surface)
        self.assertEqual(verdict, "reject")
        self.assertIn("reversibility_classification", detail)

    def test_irreversible_advisory_not_reject(self):
        surface = _valid_fence_surface(reversibility="irreversible")
        verdict, detail = guard._layer_fence_validate(surface)
        self.assertEqual(verdict, "advisory-irreversible")
        self.assertIn("Axiomatic Judgment", detail)


# ---------- End-to-end Pillar 3 synthesis -------------------------------

class TestPillar3SynthesisEndToEnd(unittest.TestCase):
    """The load-bearing CP5 verification gate: a reversible Fence fire
    through PreToolUse + PostToolUse must produce exactly one protocol
    entry in ~/.episteme/framework/protocols.jsonl with
    format_version `cp5-pre-chain`."""

    def test_reversible_fence_writes_protocol_on_exit_zero(self):
        with _EphemeralEpistemeHome() as home:
            with tempfile.TemporaryDirectory() as td:
                cwd = Path(td)
                # Seed the project tree so Layer 3 can ground
                # constraint_identified.
                (cwd / "core" / "hooks").mkdir(parents=True, exist_ok=True)
                (cwd / "core" / "hooks" / "_grounding.py").write_text(
                    "# grounding\n", encoding="utf-8"
                )
                (cwd / "docs").mkdir(exist_ok=True)
                (cwd / "docs" / "PLAN.md").write_text("# plan\n")
                surface = _valid_fence_surface(
                    constraint="core/hooks/_grounding.py:32",
                )
                # Pre: fence fires, pending marker written.
                rc, _out, _err = _run_guard(
                    surface, cwd, "rm .episteme/advisory-surface"
                )
                self.assertEqual(rc, 0, f"PreToolUse should admit: {_err}")
                pending_dir = home / "state" / "fence_pending"
                pending_files = list(pending_dir.glob("*.json")) if pending_dir.is_dir() else []
                self.assertEqual(
                    len(pending_files), 1,
                    f"expected 1 pending marker, got {len(pending_files)}"
                )

                # Post: exit 0 → protocol written.
                rc_post, _out_p, _err_p = _run_post_hook(
                    "rm .episteme/advisory-surface", exit_code=0, cwd=cwd
                )
                self.assertEqual(rc_post, 0)
                framework = home / "framework" / "protocols.jsonl"
                self.assertTrue(
                    framework.is_file(),
                    "framework protocols.jsonl was not created"
                )
                lines = [
                    ln for ln in framework.read_text(
                        encoding="utf-8"
                    ).splitlines()
                    if ln.strip()
                ]
                self.assertEqual(len(lines), 1)
                protocol = json.loads(lines[0])
                self.assertEqual(
                    protocol["format_version"], "cp5-pre-chain"
                )
                self.assertEqual(protocol["blueprint"], "fence_reconstruction")
                self.assertIsNone(protocol["chain"]["prev_hash"])
                self.assertIsNone(protocol["chain"]["entry_hash"])
                self.assertTrue(protocol["synthesized_protocol"])
                self.assertTrue(protocol["context_signature"])
                self.assertEqual(
                    protocol["source_fields"]["reversibility_classification"],
                    "reversible",
                )
                # Marker cleaned up.
                self.assertEqual(
                    len(list(pending_dir.glob("*.json"))), 0,
                    "pending marker should be deleted after PostToolUse"
                )

    def test_exit_nonzero_writes_no_protocol_and_cleans_marker(self):
        with _EphemeralEpistemeHome() as home:
            with tempfile.TemporaryDirectory() as td:
                cwd = Path(td)
                (cwd / "core" / "hooks").mkdir(parents=True, exist_ok=True)
                (cwd / "core" / "hooks" / "_grounding.py").write_text("# g\n")
                (cwd / "docs").mkdir(exist_ok=True)
                (cwd / "docs" / "PLAN.md").write_text("# p\n")
                surface = _valid_fence_surface()
                rc, _out, _err = _run_guard(
                    surface, cwd, "rm .episteme/advisory-surface"
                )
                self.assertEqual(rc, 0)

                rc_post, _out_p, _err_p = _run_post_hook(
                    "rm .episteme/advisory-surface", exit_code=1, cwd=cwd
                )
                self.assertEqual(rc_post, 0)
                framework = home / "framework" / "protocols.jsonl"
                self.assertFalse(
                    framework.exists(),
                    "no protocol should be written when exit != 0"
                )
                pending_dir = home / "state" / "fence_pending"
                self.assertEqual(
                    len(list(pending_dir.glob("*.json")) if pending_dir.is_dir() else []),
                    0,
                    "pending marker must be cleaned up on exit != 0"
                )

    def test_irreversible_writes_no_pending_marker(self):
        with _EphemeralEpistemeHome() as home:
            with tempfile.TemporaryDirectory() as td:
                cwd = Path(td)
                (cwd / "core" / "hooks").mkdir(parents=True, exist_ok=True)
                (cwd / "core" / "hooks" / "_grounding.py").write_text("# g\n")
                (cwd / "docs").mkdir(exist_ok=True)
                (cwd / "docs" / "PLAN.md").write_text("# p\n")
                surface = _valid_fence_surface(reversibility="irreversible")
                rc, _out, err = _run_guard(
                    surface, cwd, "rm .episteme/advisory-surface"
                )
                self.assertEqual(rc, 0)
                self.assertIn("Axiomatic Judgment", err)
                pending_dir = home / "state" / "fence_pending"
                self.assertEqual(
                    len(list(pending_dir.glob("*.json")) if pending_dir.is_dir() else []),
                    0,
                    "irreversible fence must NOT write a pending marker"
                )

    def test_generic_op_does_not_trigger_fence_synthesis(self):
        with _EphemeralEpistemeHome() as home:
            with tempfile.TemporaryDirectory() as td:
                cwd = Path(td)
                surface = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "core_question": "Is the push ready?",
                    "knowns": ["baseline green"],
                    "unknowns": [
                        "if CI returns non-zero exit code on the push branch, "
                        "local parity was false"
                    ],
                    "assumptions": ["hook runner is Claude Code"],
                    "disconfirmation": (
                        "CI fails on main after push or tag verification rejects"
                    ),
                    # CP6 — generic blueprint requires verification_trace
                    # for high-impact Bash ops. Minimal or_test slot
                    # keeps the focus on "generic op does not write a
                    # Fence marker," not on Layer 4 grammar itself.
                    "verification_trace": {
                        "or_test": (
                            "tests/test_fence_reconstruction_end_to_end.py"
                            "::test_generic_op_does_not_trigger_fence_synthesis"
                        ),
                    },
                }
                rc, _out, _err = _run_guard(
                    surface, cwd, "git push origin master"
                )
                self.assertEqual(rc, 0)
                pending_dir = home / "state" / "fence_pending"
                self.assertEqual(
                    len(list(pending_dir.glob("*.json")) if pending_dir.is_dir() else []),
                    0,
                    "non-Fence op must never write a Fence pending marker"
                )


# ---------- Graceful degrade -------------------------------------------

class TestFenceGracefulDegrade(unittest.TestCase):
    def test_corrupt_pending_marker_does_not_crash_posthook(self):
        with _EphemeralEpistemeHome() as home:
            pending_dir = home / "state" / "fence_pending"
            pending_dir.mkdir(parents=True, exist_ok=True)
            # Write a correlation-ID file that is not valid JSON.
            (pending_dir / "test-use-id-fence-cp5.json").write_text(
                "{ not valid json",
                encoding="utf-8",
            )
            with tempfile.TemporaryDirectory() as td:
                cwd = Path(td)
                rc, _out, _err = _run_post_hook(
                    "rm .episteme/advisory-surface", exit_code=0, cwd=cwd
                )
            self.assertEqual(rc, 0)
            framework = home / "framework" / "protocols.jsonl"
            self.assertFalse(
                framework.exists(),
                "corrupt marker must not yield a synthesized protocol"
            )

    def test_build_protocol_short_truncates_long_fields(self):
        marker = {
            "correlation_id": "abc",
            "cwd": "/tmp/test",
            "command_redacted": "rm foo",
            "surface": {
                "constraint_identified": "x" * 500,
                "origin_evidence": "y" * 500,
                "removal_consequence_prediction": "z" * 500,
                "reversibility_classification": "reversible",
                "rollback_path": "w" * 500,
            },
        }
        protocol = fence_synth.build_protocol_for_tests(marker, 0)
        self.assertLess(
            len(protocol["synthesized_protocol"]), 2000,
            "protocol text should be bounded even with oversize inputs"
        )


if __name__ == "__main__":
    unittest.main()
