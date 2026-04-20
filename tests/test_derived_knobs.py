"""Tests for derived-behavior-knobs bridge from operator profile to hooks.

Kernel reference: `kernel/OPERATOR_PROFILE_SCHEMA.md` section 5
(Derived behavior knobs). The knob file is written by the adapter at
`episteme sync` time from the profile's scored axes; hooks read it at
invocation time.

These tests verify:
1. The compute function derives knobs correctly from a v2 profile.
2. load_knob returns the declared default when the file is missing / empty /
   malformed / has a type mismatch (hook must never block on a bad knob file).
3. reasoning_surface_guard's min-length functions pick up the derived value.
4. A knob file with a higher min actually tightens the guard's validation
   (end-to-end: profile → knob file → hook behavior).
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.hooks import _derived_knobs as dk
from core.hooks import reasoning_surface_guard as guard


class ComputeKnobsFromProfileTests(unittest.TestCase):
    """The derivation rules in kernel/OPERATOR_PROFILE_SCHEMA.md section 5."""

    def test_default_profile_yields_default_min(self):
        knobs = dk.compute_knobs_from_scores(
            process={"testing_rigor": 2},
            cognitive={"uncertainty_tolerance": 2},
        )
        # uncertainty_tolerance 2 + testing_rigor 2 = no bump above base 15
        self.assertEqual(knobs["disconfirmation_specificity_min"], 15)
        self.assertEqual(knobs["unknown_specificity_min"], 15)

    def test_high_rigor_profile_raises_min(self):
        # uncertainty 4, testing 4 → 15 + 3*2 + 3*2 = 27
        knobs = dk.compute_knobs_from_scores(
            process={"testing_rigor": 4},
            cognitive={"uncertainty_tolerance": 4},
        )
        self.assertEqual(knobs["disconfirmation_specificity_min"], 27)
        self.assertEqual(knobs["unknown_specificity_min"], 27)

    def test_loss_averse_forces_confirm_irreversible(self):
        knobs = dk.compute_knobs_from_scores(
            process={"risk_tolerance": 5},  # high
            cognitive={"asymmetry_posture": "loss-averse"},
        )
        # loss-averse overrides high risk_tolerance
        self.assertEqual(knobs["default_autonomy_class"], "confirm-irreversible")

    def test_convexity_seeking_plus_high_risk_permits_reversible(self):
        knobs = dk.compute_knobs_from_scores(
            process={"risk_tolerance": 4},
            cognitive={"asymmetry_posture": "convexity-seeking"},
        )
        self.assertEqual(knobs["default_autonomy_class"], "permit-reversible")

    def test_dominant_lens_round_trips_as_preferred_lens_order(self):
        knobs = dk.compute_knobs_from_scores(
            process={},
            cognitive={"dominant_lens": ["failure-first", "causal-chain"]},
        )
        self.assertEqual(
            knobs["preferred_lens_order"], ["failure-first", "causal-chain"]
        )

    def test_noise_signature_flattens_to_watch_set(self):
        knobs = dk.compute_knobs_from_scores(
            process={},
            cognitive={"noise_signature": {
                "primary": "status-pressure",
                "secondary": "false-urgency",
            }},
        )
        self.assertEqual(
            knobs["noise_watch_set"], ["status-pressure", "false-urgency"]
        )

    def test_malformed_cognitive_values_fall_back_to_defaults(self):
        # Adapter should survive a profile with malformed entries.
        knobs = dk.compute_knobs_from_scores(
            process={},
            cognitive={
                "uncertainty_tolerance": "four",  # bad type
                "dominant_lens": "not-a-list",    # bad type
                "noise_signature": "nope",        # bad type
                "fence_discipline": None,
            },
        )
        # Falls back to base 15; no crash; suspicious entries absent.
        self.assertEqual(knobs["disconfirmation_specificity_min"], 15)
        self.assertNotIn("preferred_lens_order", knobs)
        self.assertNotIn("noise_watch_set", knobs)
        self.assertNotIn("fence_check_strictness", knobs)


class LoadKnobTests(unittest.TestCase):
    """load_knob must never block; a bad file returns the default."""

    def _with_knobs_file(self, contents: str | None):
        """Context-manager-like helper: point _KNOBS_PATH at a tmp file."""
        class _Ctx:
            def __enter__(self_inner):
                self_inner.tmp = tempfile.TemporaryDirectory()
                path = Path(self_inner.tmp.name) / "derived_knobs.json"
                if contents is not None:
                    path.write_text(contents)
                self_inner.patch = patch.object(dk, "_KNOBS_PATH", path)
                self_inner.patch.start()
                return path

            def __exit__(self_inner, *a):
                self_inner.patch.stop()
                self_inner.tmp.cleanup()
        return _Ctx()

    def test_missing_file_returns_default(self):
        with self._with_knobs_file(None):
            self.assertEqual(dk.load_knob("disconfirmation_specificity_min", 15), 15)

    def test_malformed_json_returns_default(self):
        with self._with_knobs_file("{ not json"):
            self.assertEqual(dk.load_knob("disconfirmation_specificity_min", 15), 15)

    def test_missing_key_returns_default(self):
        with self._with_knobs_file(json.dumps({"other_knob": 99})):
            self.assertEqual(dk.load_knob("disconfirmation_specificity_min", 15), 15)

    def test_type_mismatch_returns_default(self):
        with self._with_knobs_file(json.dumps({"disconfirmation_specificity_min": "27"})):
            # String where int expected → default
            self.assertEqual(dk.load_knob("disconfirmation_specificity_min", 15), 15)

    def test_valid_value_returned(self):
        with self._with_knobs_file(json.dumps({"disconfirmation_specificity_min": 27})):
            self.assertEqual(dk.load_knob("disconfirmation_specificity_min", 15), 27)

    def test_empty_file_returns_default(self):
        with self._with_knobs_file(""):
            self.assertEqual(dk.load_knob("disconfirmation_specificity_min", 15), 15)


class GuardConsumesDerivedKnobsTests(unittest.TestCase):
    """End-to-end: a knob override actually tightens the guard's validation."""

    def _with_guard_knobs(self, disc_min: int, unknown_min: int):
        class _Ctx:
            def __enter__(self_inner):
                self_inner.tmp = tempfile.TemporaryDirectory()
                path = Path(self_inner.tmp.name) / "derived_knobs.json"
                path.write_text(json.dumps({
                    "disconfirmation_specificity_min": disc_min,
                    "unknown_specificity_min": unknown_min,
                }))
                self_inner.patch = patch.object(guard, "_DERIVED_KNOBS_PATH", path)
                self_inner.patch.start()
                return path

            def __exit__(self_inner, *a):
                self_inner.patch.stop()
                self_inner.tmp.cleanup()
        return _Ctx()

    def test_default_min_passes_a_15_char_disconfirmation(self):
        # No knob file → default 15; 15-char disc passes.
        with self._with_guard_knobs(15, 15):
            missing = guard._surface_missing_fields({
                "core_question": "Will migration hold under production load?",
                "unknowns": ["Does caller hold a lock on the target table here?"],
                "assumptions": [],
                "disconfirmation": "row_count > 50000",  # 16 chars
            })
            self.assertNotIn("disconfirmation", missing)

    def test_raised_min_rejects_same_disconfirmation(self):
        # operator profile → knob 27; 16-char disc now fails.
        with self._with_guard_knobs(27, 27):
            missing = guard._surface_missing_fields({
                "core_question": "Will migration hold under production load?",
                "unknowns": ["Does caller hold a lock on the target table here?"],
                "assumptions": [],
                "disconfirmation": "row_count > 50000",  # 16 chars
            })
            self.assertIn("disconfirmation", missing)

    def test_raised_min_accepts_longer_disconfirmation(self):
        with self._with_guard_knobs(27, 27):
            missing = guard._surface_missing_fields({
                "core_question": "Will migration hold under production load?",
                "unknowns": ["Does caller hold a lock on the target table here?"],
                "assumptions": [],
                # 35 chars, concrete + measurable
                "disconfirmation": "job fails within 2m when rows > 50k",
            })
            self.assertNotIn("disconfirmation", missing)

    def test_raised_unknown_min_tightens_unknown_validation(self):
        with self._with_guard_knobs(27, 27):
            missing = guard._surface_missing_fields({
                "core_question": "Will migration hold?",
                # 21 chars — passes at 15, fails at 27
                "unknowns": ["does caller hold lock"],
                "assumptions": [],
                "disconfirmation": "job fails within 2m when rows > 50k",
            })
            self.assertIn("unknowns", missing)


if __name__ == "__main__":
    unittest.main()
