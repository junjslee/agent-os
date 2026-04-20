import json
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from episteme import cli
from episteme.adapters import claude as claude_adapter


class ProfileCognitionTests(unittest.TestCase):
    def test_normalize_answers_accepts_both_ranges(self):
        raw = {
            "a": 1,
            "b": 4,
            "c": 0,
            "d": 3,
            "bad": 99,
            "text": "x",
        }
        got = cli._normalize_answers(raw)
        self.assertEqual(got["a"], 2)
        self.assertEqual(got["c"], 1)  # presence of 0 => zero-based mode
        self.assertEqual(got["d"], 4)
        self.assertNotIn("b", got)
        self.assertNotIn("bad", got)
        self.assertNotIn("text", got)

    def test_normalize_answers_one_based_mode_keeps_1_to_4(self):
        got = cli._normalize_answers({"a": 1, "b": 3, "c": 4})
        self.assertEqual(got, {"a": 1, "b": 3, "c": 4})

    def test_load_answers_file_supports_top_level_and_nested(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            top = base / "top.json"
            nested = base / "nested.json"

            top.write_text(json.dumps({"planning_strictness": 4}), encoding="utf-8")
            nested.write_text(json.dumps({"answers": {"testing_rigor": 2}}), encoding="utf-8")

            a = cli._load_answers_file(top)
            b = cli._load_answers_file(nested)

            self.assertEqual(a["planning_strictness"], 4)
            self.assertEqual(b["testing_rigor"], 2)

    def test_load_answers_file_raises_for_invalid_json(self):
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.json"
            bad.write_text("{not-json}", encoding="utf-8")
            with self.assertRaises(ValueError):
                cli._load_answers_file(bad)

    def test_profile_hybrid_blending_is_deterministic(self):
        survey_payload = {
            "scores": {dim: 3 for dim in cli.PROFILE_DIMENSIONS},
            "evidence": {dim: ["survey"] for dim in cli.PROFILE_DIMENSIONS},
        }
        infer_payload = {
            "scores": {dim: 0 for dim in cli.PROFILE_DIMENSIONS},
            "evidence": {dim: ["infer"] for dim in cli.PROFILE_DIMENSIONS},
        }
        with patch.object(cli, "_profile_survey", return_value=survey_payload), patch.object(
            cli, "_profile_infer", return_value=infer_payload
        ):
            out = cli._profile_hybrid(Path("."), answers={"planning_strictness": 4})

        for dim in cli.PROFILE_DIMENSIONS:
            self.assertEqual(out["scores"][dim], 2)  # round(0.6*3 + 0.4*0)
            self.assertTrue(out["evidence"][dim][0].startswith("hybrid blend:"))

    def test_cognition_hybrid_blending_is_deterministic(self):
        survey_payload = {
            "scores": {dim: 3 for dim in cli.COGNITIVE_DIMENSIONS},
            "evidence": {dim: ["survey"] for dim in cli.COGNITIVE_DIMENSIONS},
        }
        infer_payload = {
            "scores": {dim: 1 for dim in cli.COGNITIVE_DIMENSIONS},
            "evidence": {dim: ["infer"] for dim in cli.COGNITIVE_DIMENSIONS},
        }
        with patch.object(cli, "_cognition_survey", return_value=survey_payload), patch.object(
            cli, "_cognition_infer", return_value=infer_payload
        ):
            out = cli._cognition_hybrid(Path("."), answers={"first_principles_depth": 4})

        for dim in cli.COGNITIVE_DIMENSIONS:
            self.assertEqual(out["scores"][dim], 2)  # round(0.6*3 + 0.4*1)
            self.assertTrue(out["evidence"][dim][0].startswith("hybrid blend:"))

    def test_cognition_infer_scores_are_bounded(self):
        with patch.object(cli, "_git_text", return_value=""), patch.object(cli, "_safe_read_text", return_value=""), patch.object(
            cli, "_project_has_ci", return_value=False
        ):
            out = cli._cognition_infer(Path("."))

        self.assertEqual(set(out["scores"].keys()), set(cli.COGNITIVE_DIMENSIONS))
        for value in out["scores"].values():
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 3)

    def test_setup_command_runs_selected_modes_and_post_steps(self):
        with patch.object(cli, "_resolve_bootstrap_target", return_value=Path(".")), patch.object(
            cli, "_profile_command", return_value=0
        ) as profile_cmd, patch.object(cli, "_cognition_command", return_value=0) as cognition_cmd, patch.object(
            cli, "_write_personalization_blueprint"
        ) as blueprint_cmd, patch.object(cli, "_sync_user_runtime") as sync_cmd, patch.object(
            cli, "_doctor", return_value=0
        ) as doctor_cmd:
            rc = cli._setup_command(
                path_arg=".",
                profile_mode="hybrid",
                cognition_mode="infer",
                governance_mode="balanced",
                write=True,
                overwrite=False,
                do_sync=True,
                do_doctor=True,
                profile_answers={dim: 4 for dim in cli.PROFILE_DIMENSIONS},
                cognition_answers={"first_principles_depth": 3},
                interactive=False,
            )

        self.assertEqual(rc, 0)
        profile_cmd.assert_called_once_with(
            "hybrid",
            ".",
            write=True,
            overwrite=False,
            answers={dim: 4 for dim in cli.PROFILE_DIMENSIONS},
        )
        cognition_cmd.assert_called_once_with(
            "infer",
            ".",
            write=True,
            overwrite=False,
            answers={"first_principles_depth": 3},
        )
        blueprint_cmd.assert_called_once()
        sync_cmd.assert_called_once_with("balanced")
        doctor_cmd.assert_called_once()

    def test_setup_command_rejects_invalid_mode(self):
        with patch("sys.stderr", new_callable=io.StringIO):
            rc = cli._setup_command(
                path_arg=".",
                profile_mode="bad",
                cognition_mode="skip",
                governance_mode="balanced",
                write=False,
                overwrite=False,
                do_sync=False,
                do_doctor=False,
                profile_answers=None,
                cognition_answers=None,
                interactive=False,
            )
        self.assertEqual(rc, 1)

    def test_setup_answers_file_override_resolution(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fallback = root / "fallback.json"
            profile = root / "profile.json"
            cognition = root / "cognition.json"
            fallback.write_text(json.dumps({"answers": {"planning_strictness": 2, "first_principles_depth": 2}}), encoding="utf-8")
            profile.write_text(json.dumps({"planning_strictness": 4}), encoding="utf-8")
            cognition.write_text(json.dumps({"first_principles_depth": 3}), encoding="utf-8")

            parser = cli.build_parser()
            args = parser.parse_args(
                [
                    "setup",
                    ".",
                    "--profile-mode",
                    "survey",
                    "--cognition-mode",
                    "survey",
                    "--answers-file",
                    str(fallback),
                    "--profile-answers-file",
                    str(profile),
                    "--cognition-answers-file",
                    str(cognition),
                ]
            )

            fallback_answers = cli._load_answers_file(Path(args.answers_file).expanduser())
            profile_answers = fallback_answers
            if args.profile_answers_file:
                profile_answers = cli._load_answers_file(Path(args.profile_answers_file).expanduser())
            cognition_answers = fallback_answers
            if args.cognition_answers_file:
                cognition_answers = cli._load_answers_file(Path(args.cognition_answers_file).expanduser())

            self.assertEqual(profile_answers["planning_strictness"], 4)
            self.assertEqual(cognition_answers["first_principles_depth"], 3)

    def test_setup_parser_defaults_to_noninteractive_safe_modes(self):
        parser = cli.build_parser()
        args = parser.parse_args(["setup"])
        self.assertIsNone(args.profile_mode)
        self.assertIsNone(args.cognition_mode)
        self.assertEqual(args.governance_pack, "balanced")

    def test_setup_command_rejects_invalid_governance_pack(self):
        with patch("sys.stderr", new_callable=io.StringIO) as fake_stderr:
            rc = cli._setup_command(
                path_arg=".",
                profile_mode="skip",
                cognition_mode="skip",
                governance_mode="bad-pack",
                write=False,
                overwrite=False,
                do_sync=False,
                do_doctor=False,
                profile_answers=None,
                cognition_answers=None,
                interactive=False,
            )
        self.assertEqual(rc, 1)
        self.assertIn("Unsupported governance pack", fake_stderr.getvalue())

    def test_strict_governance_removes_permission_request_after_merge(self):
        existing = {
            "hooks": {
                "PermissionRequest": [
                    {
                        "matcher": "Read|Glob|Grep",
                        "hooks": [{"type": "command", "command": "echo '{\"decision\":\"allow\"}'"}],
                    }
                ]
            }
        }
        merged = claude_adapter.merge_settings(existing, claude_adapter.build_settings("strict"))
        merged = claude_adapter.enforce_governance_overrides(merged, "strict")
        hooks = merged.get("hooks", {})
        self.assertNotIn("PermissionRequest", hooks)

    def test_balanced_governance_keeps_permission_request(self):
        existing = {
            "hooks": {
                "PermissionRequest": [
                    {
                        "matcher": "Read|Glob|Grep",
                        "hooks": [{"type": "command", "command": "echo '{\"decision\":\"allow\"}'"}],
                    }
                ]
            }
        }
        merged = claude_adapter.merge_settings(existing, claude_adapter.build_settings("balanced"))
        merged = claude_adapter.enforce_governance_overrides(merged, "balanced")
        hooks = merged.get("hooks", {})
        self.assertIn("PermissionRequest", hooks)

    def test_dedupe_preserves_non_command_hook_entries(self):
        hooks = {
            "PostToolUse": [
                {
                    "matcher": "Write",
                    "hooks": [
                        {"type": "webhook", "url": "https://example.invalid/hook"},
                        {"type": "webhook", "url": "https://example.invalid/hook"},
                    ],
                }
            ]
        }
        deduped = claude_adapter.dedupe_hooks_map(hooks)
        self.assertIn("PostToolUse", deduped)
        self.assertEqual(len(deduped["PostToolUse"]), 1)
        out_hooks = deduped["PostToolUse"][0].get("hooks", [])
        self.assertEqual(len(out_hooks), 2)
        self.assertEqual(out_hooks[0].get("type"), "webhook")

    def test_strict_governance_preserves_custom_permission_request_hooks(self):
        existing = {
            "hooks": {
                "PermissionRequest": [
                    {
                        "matcher": "Read|Glob|Grep",
                        "hooks": [{"type": "command", "command": "echo '{\"decision\":\"allow\"}'"}],
                    },
                    {
                        "matcher": "Read",
                        "hooks": [{"type": "command", "command": "python /tmp/custom_permission.py"}],
                    },
                ]
            }
        }
        merged = claude_adapter.merge_settings(existing, claude_adapter.build_settings("strict"))
        merged = claude_adapter.enforce_governance_overrides(merged, "strict")
        hooks = merged.get("hooks", {})
        self.assertIn("PermissionRequest", hooks)
        entries = hooks.get("PermissionRequest", [])
        self.assertTrue(any(isinstance(e, dict) and e.get("matcher") == "Read" for e in entries))

    def test_prune_managed_hooks_for_minimal_pack(self):
        merged = claude_adapter.build_settings("balanced")
        merged.setdefault("hooks", {}).setdefault("PreToolUse", []).append(
            {
                "matcher": "Write",
                "hooks": [{"type": "command", "command": "python /tmp/external_guard.py"}],
            }
        )

        out = claude_adapter.prune_managed_hook_entries(merged, "minimal")
        hooks = out.get("hooks", {})
        pre = hooks.get("PreToolUse", [])
        post = hooks.get("PostToolUse", [])
        pre_cmds = [h.get("command", "") for e in pre if isinstance(e, dict) for h in e.get("hooks", []) if isinstance(h, dict)]
        post_cmds = [h.get("command", "") for e in post if isinstance(e, dict) for h in e.get("hooks", []) if isinstance(h, dict)]
        self.assertFalse(any("workflow_guard.py" in c for c in pre_cmds))
        self.assertFalse(any("prompt_guard.py" in c for c in pre_cmds))
        self.assertFalse(any("context_guard.py" in c for c in post_cmds))
        self.assertTrue(any("test_runner.py" in c for c in post_cmds))
        self.assertTrue(any("external_guard.py" in c for c in pre_cmds))

    def test_setup_noninteractive_defaults_infer_when_modes_omitted(self):
        with patch.object(cli, "_resolve_bootstrap_target", return_value=Path(".")), patch.object(
            cli, "_profile_command", return_value=0
        ) as profile_cmd, patch.object(cli, "_cognition_command", return_value=0) as cognition_cmd, patch.object(
            cli, "_write_personalization_blueprint"
        ) as blueprint_cmd:
            rc = cli._setup_command(
                path_arg=".",
                profile_mode=None,
                cognition_mode=None,
                governance_mode="balanced",
                write=False,
                overwrite=False,
                do_sync=False,
                do_doctor=False,
                profile_answers=None,
                cognition_answers=None,
                interactive=False,
            )
        self.assertEqual(rc, 0)
        profile_cmd.assert_called_once_with("infer", ".", write=False, overwrite=False, answers=None)
        cognition_cmd.assert_called_once_with("infer", ".", write=False, overwrite=False, answers=None)
        blueprint_cmd.assert_called_once()

    def test_setup_noninteractive_rejects_survey_without_answers(self):
        with patch("sys.stderr", new_callable=io.StringIO) as fake_stderr:
            rc = cli._setup_command(
                path_arg=".",
                profile_mode="survey",
                cognition_mode="skip",
                governance_mode="balanced",
                write=False,
                overwrite=False,
                do_sync=False,
                do_doctor=False,
                profile_answers=None,
                cognition_answers=None,
                interactive=False,
            )
        self.assertEqual(rc, 1)
        self.assertIn("requires complete answers", fake_stderr.getvalue())
    def test_setup_interactive_defaults_to_questionnaire_first(self):
        with patch.object(cli, "_prompt_yes_no", side_effect=[True, False, False, False]), patch.object(
            cli, "_resolve_bootstrap_target", return_value=Path(".")
        ), patch.object(cli, "_profile_command", return_value=0) as profile_cmd, patch.object(
            cli, "_cognition_command", return_value=0
        ) as cognition_cmd, patch.object(cli, "_write_personalization_blueprint") as blueprint_cmd:
            rc = cli._setup_command(
                path_arg=".",
                profile_mode=None,
                cognition_mode=None,
                governance_mode="balanced",
                write=False,
                overwrite=False,
                do_sync=False,
                do_doctor=False,
                profile_answers={dim: 2 for dim in cli.PROFILE_DIMENSIONS},
                cognition_answers={dim: 2 for dim in cli.COGNITIVE_DIMENSIONS},
                interactive=True,
            )
        self.assertEqual(rc, 0)
        profile_cmd.assert_called_once_with("survey", ".", write=False, overwrite=False, answers={dim: 2 for dim in cli.PROFILE_DIMENSIONS})
        cognition_cmd.assert_called_once_with("survey", ".", write=False, overwrite=False, answers={dim: 2 for dim in cli.COGNITIVE_DIMENSIONS})
        blueprint_cmd.assert_called_once()

    def test_setup_interactive_prompt_mentions_questionnaire_onboarding(self):
        with patch.object(cli, "_prompt_yes_no", side_effect=[True, False, False, False]) as prompt_yes_no, patch.object(
            cli, "_resolve_bootstrap_target", return_value=Path(".")
        ), patch("sys.stdout", new_callable=io.StringIO) as fake_stdout, patch.object(cli, "_profile_command", return_value=0), patch.object(cli, "_cognition_command", return_value=0), patch.object(
            cli, "_write_personalization_blueprint"
        ) as blueprint_cmd:
            rc = cli._setup_command(
                path_arg=".",
                profile_mode=None,
                cognition_mode=None,
                governance_mode="balanced",
                write=False,
                overwrite=False,
                do_sync=False,
                do_doctor=False,
                profile_answers={dim: 2 for dim in cli.PROFILE_DIMENSIONS},
                cognition_answers={dim: 2 for dim in cli.COGNITIVE_DIMENSIONS},
                interactive=True,
            )
        self.assertEqual(rc, 0)
        prompt_yes_no.assert_any_call("Use questionnaire onboarding now?", default=True)
        self.assertIn("agent's soul", fake_stdout.getvalue())
        blueprint_cmd.assert_called_once()
    def test_setup_writes_personalization_blueprint_when_scores_available(self):
        with tempfile.TemporaryDirectory() as td:
            project_root = Path(td)
            generated_dir = project_root / "core" / "memory" / "global" / ".generated"
            generated_dir.mkdir(parents=True)

            (generated_dir / "workstyle_scores.json").write_text(
                json.dumps(
                    {
                        "mode": "survey",
                        "scores": {
                            "planning_strictness": 3,
                            "risk_tolerance": 2,
                            "testing_rigor": 1,
                            "parallelism_preference": 0,
                            "documentation_rigor": 2,
                            "automation_level": 1,
                        },
                    }
                ),
                encoding="utf-8",
            )
            (generated_dir / "cognitive_profile.json").write_text(
                json.dumps(
                    {
                        "mode": "survey",
                        "scores": {
                            "first_principles_depth": 3,
                            "exploration_breadth": 2,
                            "speed_vs_rigor_balance": 1,
                            "challenge_orientation": 2,
                            "uncertainty_tolerance": 1,
                            "autonomy_preference": 2,
                        },
                    }
                ),
                encoding="utf-8",
            )

            cli._write_personalization_blueprint(project_root)
            out_path = generated_dir / "personalization_blueprint.md"
            self.assertTrue(out_path.exists())
            text = out_path.read_text(encoding="utf-8")
            self.assertIn("Personalization Blueprint", text)
            self.assertIn("🧭 Execution Profile (Workstyle)", text)
            self.assertIn("🧠 Thinking Profile (Cognition)", text)
            self.assertIn("🔒 Operating Contract", text)

    def test_evolve_parser_has_run_report_promote_rollback(self):
        parser = cli.build_parser()
        args = parser.parse_args([
            "evolve",
            "run",
            "--hypothesis",
            "improve handoff consistency",
            "--mutation-type",
            "handoff_format_tweak",
            "--target",
            "core/agents/docs-handoff.md",
            "--expected-effect",
            "higher style_fit_score",
        ])
        self.assertEqual(args.command, "evolve")
        self.assertEqual(args.evolve_action, "run")

    def test_evolve_run_creates_episode_file(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(cli, "EVOLUTION_EPISODES_DIR", Path(td) / "episodes"):
                rc = cli._evolve_run(
                    hypothesis="improve planning depth",
                    mutation_type="planning_depth_tweak",
                    target="core/agents/planner.md",
                    expected_effect="increase task_success_rate",
                    diff_text="increase decomposition checklist",
                    risk_level="low",
                    suite_ref="smoke-suite",
                    seed=7,
                    captured_by="test",
                )
                self.assertEqual(rc, 0)
                files = list((Path(td) / "episodes").glob("*.json"))
                self.assertEqual(len(files), 1)
                payload = json.loads(files[0].read_text(encoding="utf-8"))
                self.assertEqual(payload["decision"], "candidate")
                self.assertEqual(payload["mutation"]["type"], "planning_depth_tweak")

    def test_evolve_promote_and_rollback(self):
        with tempfile.TemporaryDirectory() as td:
            episodes_dir = Path(td) / "episodes"
            episodes_dir.mkdir(parents=True)
            episode = {
                "episode_id": "ep-test",
                "hypothesis": "h",
                "mutation": {
                    "type": "planning_depth_tweak",
                    "target": "core/agents/planner.md",
                    "diff": "x",
                    "expected_effect": "y",
                    "risk_level": "low",
                },
                "suite_ref": "smoke",
                "metrics_before": {
                    "task_success_rate": 0.5,
                    "safety_violation_count": 0,
                    "latency_ms_p50": 100,
                    "token_cost": 1000,
                    "style_fit_score": 0.7,
                },
                "metrics_after": {
                    "task_success_rate": 0.6,
                    "safety_violation_count": 0,
                    "latency_ms_p50": 105,
                    "token_cost": 1100,
                    "style_fit_score": 0.75,
                },
                "gate_result": {"passed": True, "reasons": ["all gates passed"]},
                "decision": "candidate",
                "provenance": {
                    "captured_at": "2026-01-01T00:00:00+00:00",
                    "captured_by": "test",
                    "confidence": "medium",
                },
                "version": "evolution-contract-v1",
            }
            (episodes_dir / "ep-test.json").write_text(json.dumps(episode), encoding="utf-8")

            with patch.object(cli, "EVOLUTION_EPISODES_DIR", episodes_dir):
                self.assertEqual(cli._evolve_promote("ep-test", force=False), 0)
                promoted = json.loads((episodes_dir / "ep-test.json").read_text(encoding="utf-8"))
                self.assertEqual(promoted["decision"], "promoted")

                self.assertEqual(cli._evolve_rollback("ep-test", rollback_ref="manual-test"), 0)
                rolled = json.loads((episodes_dir / "ep-test.json").read_text(encoding="utf-8"))
                self.assertEqual(rolled["decision"], "rolled_back")
                self.assertEqual(rolled["rollback_ref"], "manual-test")

    def test_evolve_promote_fails_when_gate_not_passed_without_force(self):
        with tempfile.TemporaryDirectory() as td:
            episodes_dir = Path(td) / "episodes"
            episodes_dir.mkdir(parents=True)
            episode = {
                "episode_id": "ep-gate-fail",
                "hypothesis": "h",
                "mutation": {
                    "type": "planning_depth_tweak",
                    "target": "core/agents/planner.md",
                    "diff": "x",
                    "expected_effect": "y",
                    "risk_level": "low",
                },
                "suite_ref": "smoke",
                "metrics_before": {},
                "metrics_after": {},
                "gate_result": {"passed": False, "reasons": ["evaluation not run yet"]},
                "decision": "candidate",
                "provenance": {
                    "captured_at": "2026-01-01T00:00:00+00:00",
                    "captured_by": "test",
                    "confidence": "medium",
                },
                "version": "evolution-contract-v1",
            }
            (episodes_dir / "ep-gate-fail.json").write_text(json.dumps(episode), encoding="utf-8")

            with patch.object(cli, "EVOLUTION_EPISODES_DIR", episodes_dir), patch("sys.stderr", new_callable=io.StringIO) as fake_stderr:
                rc = cli._evolve_promote("ep-gate-fail", force=False)
                self.assertEqual(rc, 1)
                self.assertIn("gate_result.passed is false", fake_stderr.getvalue())

    def test_evolve_promote_force_allows_failed_gate(self):
        with tempfile.TemporaryDirectory() as td:
            episodes_dir = Path(td) / "episodes"
            episodes_dir.mkdir(parents=True)
            episode = {
                "episode_id": "ep-force",
                "hypothesis": "h",
                "mutation": {
                    "type": "planning_depth_tweak",
                    "target": "core/agents/planner.md",
                    "diff": "x",
                    "expected_effect": "y",
                    "risk_level": "low",
                },
                "suite_ref": "smoke",
                "metrics_before": {},
                "metrics_after": {},
                "gate_result": {"passed": False, "reasons": ["evaluation not run yet"]},
                "decision": "candidate",
                "provenance": {
                    "captured_at": "2026-01-01T00:00:00+00:00",
                    "captured_by": "test",
                    "confidence": "medium",
                },
                "version": "evolution-contract-v1",
            }
            (episodes_dir / "ep-force.json").write_text(json.dumps(episode), encoding="utf-8")

            with patch.object(cli, "EVOLUTION_EPISODES_DIR", episodes_dir):
                rc = cli._evolve_promote("ep-force", force=True)
                self.assertEqual(rc, 0)
                promoted = json.loads((episodes_dir / "ep-force.json").read_text(encoding="utf-8"))
                self.assertEqual(promoted["decision"], "promoted")

    def test_evolve_report_missing_episode_returns_error(self):
        with tempfile.TemporaryDirectory() as td:
            episodes_dir = Path(td) / "episodes"
            episodes_dir.mkdir(parents=True)
            with patch.object(cli, "EVOLUTION_EPISODES_DIR", episodes_dir), patch("sys.stderr", new_callable=io.StringIO) as fake_stderr:
                rc = cli._evolve_report("does-not-exist")
                self.assertEqual(rc, 1)
                self.assertIn("episode not found", fake_stderr.getvalue())

    def test_bridge_parser_has_anthropic_managed_subcommand(self):
        parser = cli.build_parser()
        args = parser.parse_args([
            "bridge",
            "anthropic-managed",
            "--input",
            "events.json",
        ])
        self.assertEqual(args.command, "bridge")
        self.assertEqual(args.bridge_action, "anthropic-managed")
        self.assertEqual(args.input, "events.json")

    def test_bridge_anthropic_managed_writes_memory_envelope(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            payload = {
                "session_id": "sess-123",
                "events": [
                    {"type": "tool_call", "tool": "bash", "input": {"cmd": "echo hi"}},
                    {"type": "error", "message": "boom"},
                ],
            }
            input_path = root / "managed-events.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")

            with patch.object(cli, "REPO_ROOT", root):
                rc = cli._bridge_anthropic_managed(
                    input_path=input_path,
                    output_path=None,
                    session_id=None,
                    project_id="proj-1",
                    source_ref=None,
                    captured_by="test-bridge",
                    confidence="high",
                    dry_run=False,
                )

            self.assertEqual(rc, 0)
            out_path = root / "core" / "memory" / "bridges" / "anthropic-managed" / "sess-123.memory-envelope.json"
            self.assertTrue(out_path.exists())
            out = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(out["contract_version"], "memory-contract-v1")
            self.assertEqual(len(out["records"]), 2)
            self.assertEqual(out["records"][0]["memory_class"], "episodic")
            self.assertEqual(out["records"][0]["event_type"], "action")
            self.assertEqual(out["records"][0]["session_id"], "sess-123")
            self.assertEqual(out["records"][0]["related_project_id"], "proj-1")
            self.assertEqual(out["records"][0]["provenance"]["source_type"], "imported")


if __name__ == "__main__":
    unittest.main()
