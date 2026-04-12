import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.agent_os import cli


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


if __name__ == "__main__":
    unittest.main()
