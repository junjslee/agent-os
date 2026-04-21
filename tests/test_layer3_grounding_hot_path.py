"""CP4 tests — Layer 3 contextual grounding wired into the hot path.

At CP4 `reasoning_surface_guard.py` runs Layer 3 after Layer 2 (both
wired in the same `if status == "ok"` block). Layer 3 consults:
  - `_scenario_detector.detect_scenario(...)` (returns "generic" at CP4)
  - `_grounding.ground_blueprint_fields(...)` per blueprint-declared
    grounded field (generic: `disconfirmation` + `unknowns`)

Behavior change vs CP3: surfaces that pass Layer 1 (length + lazy-token)
AND Layer 2 (trigger + observable classifier) but reference
entity-shaped tokens (snake_case / SCREAMING_CASE / path+ext / hex SHA)
that do NOT grep to the project tree are rejected with a
"Layer 3 grounding ... rejected" verdict, FP-averse-gated per
docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md § Layer 3 (grounded >= 2 AND
(not_found / named) > 0.5).

Honest CP4 limit: the three spec fluent-vacuous examples that CP3 could
not catch (`the migration may produce unexpected behavior...`,
`if the build process exhibits anomalous behavior...`,
`if results diverge from expectations...`) contain NO entity-shaped
tokens — pure English prose. Layer 3 is NOT the layer that catches
them; the composition-cost argument (spec § Layer 2 Composition cost)
says surfaces that evade Layer 2 must get MORE specific, which raises
Layer 3 surface area. Surfaces with no extractable entities have no
Layer 3 surface area, so CP4 passes them honestly. They are caught at
Layer 4 (CP6 `verification_trace`). This limit is tested explicitly
below so future readers understand the compose-across-layers discipline.
"""
from __future__ import annotations

import io
import json
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from core.hooks import reasoning_surface_guard as guard
from core.hooks import _grounding  # pyright: ignore[reportAttributeAccessIssue]


_SENTINEL = object()


def _surface_with(
    disconfirmation: str,
    unknowns: list[str] | None = None,
    knowns: list[str] | None = None,
    assumptions: list[str] | None = None,
    verification_trace: object = _SENTINEL,
) -> dict:
    """Build a Layer-1-and-Layer-2-passing surface whose Layer-3
    grounding characteristics are what the test exercises.

    CP6: generic blueprint declares ``verification_trace_required:
    true``. Helper defaults to a valid trace so Layer-3-focused tests
    continue passing; tests exercising Layer 4 pass ``None`` or an
    explicit dict.
    """
    surface = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "core_question": "Does this pass the Layer 3 grounding gate?",
        "knowns": knowns or ["repo at tip of master"],
        "unknowns": unknowns or [
            "if CI returns non-zero exit code on the push branch, "
            "local parity was false"
        ],
        "assumptions": assumptions or ["hook runner is Claude Code"],
        "disconfirmation": disconfirmation,
    }
    if verification_trace is _SENTINEL:
        surface["verification_trace"] = {
            "or_test": "tests/test_layer3_grounding_hot_path.py::test_smoke",
        }
    elif verification_trace is not None:
        surface["verification_trace"] = verification_trace
    return surface


def _seed_project(cwd: Path, files: dict[str, str]) -> None:
    """Write a minimal fixture project at `cwd`. Keys are relative
    paths; values are file contents."""
    for rel, content in files.items():
        target = cwd / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def _write_and_run(surface: dict, cwd: Path, command: str) -> tuple[int, str, str]:
    """Persist the surface and run the guard. Returns (rc, stdout, stderr)."""
    (cwd / ".episteme").mkdir(exist_ok=True)
    (cwd / ".episteme" / "reasoning-surface.json").write_text(
        json.dumps(surface), encoding="utf-8"
    )
    payload = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(cwd)}
    raw = json.dumps(payload)
    with patch("sys.stdin", new=io.StringIO(raw)), \
         patch("sys.stdout", new=io.StringIO()) as fake_out, \
         patch("sys.stderr", new=io.StringIO()) as fake_err:
        rc = guard.main()
    return rc, fake_out.getvalue(), fake_err.getvalue()


# ---------- Entity extractor (pure unit tests) ----------------------------

class TestEntityExtraction(unittest.TestCase):
    """Regex extractors must be FP-averse against natural English prose.

    Each test names the class under examination in its docstring so a
    future tuning pass can read failures as the specific extractor they
    implicate.
    """

    def test_snake_case_requires_underscore(self):
        ents = _grounding.extract_entities(
            "user_id and reasoning_surface_guard fire when classify_disconfirmation runs"
        )
        self.assertIn("user_id", ents)
        self.assertIn("reasoning_surface_guard", ents)
        self.assertIn("classify_disconfirmation", ents)

    def test_english_prose_does_not_extract(self):
        # These are all spec fluent-vacuous examples — none contain
        # entity-shaped tokens, so the extractor must return empty.
        samples = [
            "the migration may produce unexpected behavior if edge cases are encountered",
            "if the build process exhibits anomalous behavior we should investigate before proceeding",
            "if results diverge from expectations we will return to first principles",
            "the team will reassess our approach once new data arrives",
            "velocity baseline migration build process results expectations behavior",
        ]
        for s in samples:
            with self.subTest(sample=s):
                self.assertEqual(
                    _grounding.extract_entities(s), set(),
                    f"Expected zero entities from English prose: {s!r}"
                )

    def test_path_with_known_extension_extracts(self):
        # The extractor greedy-matches full paths when a `/` precedes
        # the extension; bare filenames match on their own line too.
        ents = _grounding.extract_entities(
            "edit core/hooks/_grounding.py and update docs/PLAN.md before tag"
        )
        # Full path with slashes.
        self.assertTrue(
            any(e.endswith("_grounding.py") for e in ents),
            f"expected a *_grounding.py match in {ents}"
        )
        self.assertTrue(
            any(e.endswith("PLAN.md") for e in ents),
            f"expected a *PLAN.md match in {ents}"
        )
        # Bare filename variant.
        ents2 = _grounding.extract_entities("see README.md and config.yaml")
        self.assertIn("README.md", ents2)
        self.assertIn("config.yaml", ents2)

    def test_screaming_case_requires_underscore(self):
        # Acronyms (CI, API, AWS, URL) must NOT extract. SCREAMING_CASE
        # with `_` MUST extract.
        ents = _grounding.extract_entities(
            "set NODE_ENV and AWS_REGION; CI and API stay as prose"
        )
        self.assertIn("NODE_ENV", ents)
        self.assertIn("AWS_REGION", ents)
        self.assertNotIn("CI", ents)
        self.assertNotIn("API", ents)
        self.assertNotIn("AWS", ents)

    def test_hex_sha_requires_digit_and_letter(self):
        # A real short-SHA must extract; a 7-char all-letter English
        # word ("acceded" has digits-free hex letters) must NOT extract
        # because the dual-lookahead requires at least one digit.
        ents = _grounding.extract_entities(
            "reverted to e1f49c9 after issue; the cat acceded to the tuna"
        )
        self.assertIn("e1f49c9", ents)
        self.assertNotIn("acceded", ents)

    def test_all_digit_hex_does_not_extract(self):
        # "1234567" is valid hex but has no letters; should NOT extract
        # (filters page numbers / line numbers from the entity set).
        ents = _grounding.extract_entities("page 1234567 of the report")
        self.assertNotIn("1234567", ents)


# ---------- Gate logic (pure unit tests) ----------------------------------

class TestLayer3GateLogic(unittest.TestCase):
    """Per spec § Layer 3 — reject only when grounded >= 2 AND
    (not_found / named) > 0.5."""

    def test_no_entities_named_passes(self):
        self.assertEqual(_grounding.layer3_verdict_from_counts(0, 0), "pass")

    def test_all_grounded_passes(self):
        self.assertEqual(_grounding.layer3_verdict_from_counts(5, 5), "pass")

    def test_fresh_repo_sparse_grounding_advisory_not_reject(self):
        # 3 named, 1 grounded → grounded < 2 clause prevents reject.
        # Some ungrounded → advisory (per verdict function).
        self.assertEqual(_grounding.layer3_verdict_from_counts(3, 1), "advisory")

    def test_gate_fires_at_high_miss_ratio(self):
        # 4 named, 2 grounded → not_found / named = 0.5, boundary.
        # Must be strictly > 50% to reject; 0.5 exactly is advisory.
        self.assertEqual(_grounding.layer3_verdict_from_counts(4, 2), "advisory")
        # 5 named, 2 grounded → 0.6 > 0.5 → reject
        self.assertEqual(_grounding.layer3_verdict_from_counts(5, 2), "reject")


# ---------- Grounding against a real project fixture ----------------------

class TestGroundingAgainstProjectFixture(unittest.TestCase):
    """Seeds a tmp_path project with known files and verifies the
    grounding behavior end-to-end through `ground_blueprint_fields`."""

    def setUp(self):
        _grounding._clear_cache_for_tests()
        self._tmpdir = __import__("tempfile").TemporaryDirectory()
        self.cwd = Path(self._tmpdir.name)
        _seed_project(self.cwd, {
            "core/hooks/_grounding.py": "# grounding module\n",
            "docs/PLAN.md": "# Plan\n\nuser_id fields and NODE_ENV vars\n",
            "README.md": "# Project\n\nShort commit sha e1f49c9 landed.\n",
        })

    def tearDown(self):
        self._tmpdir.cleanup()
        _grounding._clear_cache_for_tests()

    def test_named_entities_all_ground_passes(self):
        surface = _surface_with(
            disconfirmation=(
                "if _grounding.py fails to ground user_id against NODE_ENV "
                "and PLAN.md references become stale we rollback"
            ),
        )
        verdict, _detail = _grounding.ground_blueprint_fields(
            surface, "generic", self.cwd
        )
        self.assertEqual(verdict, "pass")

    def test_fake_entities_exceed_gate_reject(self):
        # 4 fake snake_case tokens + 2 fake SCREAMING_CASE + 0 grounded
        # → grounded < 2 clause keeps this advisory, not reject. Add 2
        # grounded (user_id, NODE_ENV exist) + 4 fake → grounded=2,
        # not_found/named = 4/6 = 0.67 > 0.5 → reject.
        surface = _surface_with(
            disconfirmation=(
                "if user_id and NODE_ENV drift from phantom_metric_a and "
                "phantom_metric_b while FAKE_KNOB_X and FAKE_KNOB_Y misfire, rollback"
            ),
        )
        verdict, detail = _grounding.ground_blueprint_fields(
            surface, "generic", self.cwd
        )
        self.assertEqual(verdict, "reject")
        self.assertIn("Layer 3 grounding", detail)
        self.assertIn("phantom_metric_a", detail)

    def test_unknowns_entries_also_grounded(self):
        # Fake entities in unknowns[] must trigger the same gate.
        surface = _surface_with(
            disconfirmation="if user_id drifts and NODE_ENV misfires rollback",
            unknowns=[
                "phantom_service_alpha and phantom_service_beta "
                "and phantom_service_gamma may diverge"
            ],
        )
        verdict, _detail = _grounding.ground_blueprint_fields(
            surface, "generic", self.cwd
        )
        # 2 grounded (user_id, NODE_ENV) + 3 phantom → 3/5 miss = 0.6 > 0.5
        self.assertEqual(verdict, "reject")

    def test_knowns_and_assumptions_not_grounded(self):
        # Even if knowns/assumptions name fake entities, Layer 3 must
        # not reject — those fields are category-outside the generic
        # blueprint's grounded-field set.
        surface = _surface_with(
            disconfirmation="CI fails on main after push",  # no entities
            knowns=[
                "phantom_a phantom_b phantom_c FAKE_X FAKE_Y FAKE_Z "
                "are all expected project entities"
            ],
            assumptions=[
                "phantom_d phantom_e phantom_f FAKE_P FAKE_Q FAKE_R hold"
            ],
        )
        verdict, _detail = _grounding.ground_blueprint_fields(
            surface, "generic", self.cwd
        )
        self.assertEqual(verdict, "pass")


# ---------- End-to-end through the guard ---------------------------------

class TestLayer3HotPathIntegration(unittest.TestCase):
    """Drives the full hot-path chain via `guard.main()`. Verifies
    Layer 3 rejections block the op and Layer 3 passes do not."""

    def setUp(self):
        _grounding._clear_cache_for_tests()
        self._tmpdir = __import__("tempfile").TemporaryDirectory()
        self.cwd = Path(self._tmpdir.name)
        _seed_project(self.cwd, {
            "core/hooks/_grounding.py": "# real project module\n",
            "docs/PLAN.md": "# Plan with user_id and NODE_ENV references\n",
            "src/main.py": "# placeholder\n",
        })

    def tearDown(self):
        self._tmpdir.cleanup()
        _grounding._clear_cache_for_tests()

    def test_fake_entities_block_op(self):
        # Crafted to pass Layer 2 (trigger `if` + observables `fail`,
        # `rejects`) while stuffing fake entity tokens that don't ground.
        # 2 grounded (user_id, NODE_ENV) + 4 phantom → 4/6 = 0.67 > 0.5 → reject.
        surface = _surface_with(
            disconfirmation=(
                "if user_id and NODE_ENV fail after phantom_alpha_one, "
                "phantom_alpha_two, FAKE_KNOB_P, and FAKE_KNOB_Q reject "
                "the deployment"
            ),
        )
        rc, _out, err = _write_and_run(surface, self.cwd, "git push origin master")
        self.assertEqual(rc, 2, f"stderr: {err}")
        self.assertIn("Layer 3 grounding", err)
        self.assertIn("rejected", err)

    def test_real_entities_pass(self):
        surface = _surface_with(
            disconfirmation=(
                "if _grounding.py and PLAN.md diverge after push, rollback "
                "because user_id tests fail"
            ),
        )
        rc, _out, err = _write_and_run(surface, self.cwd, "git push origin master")
        # Pass means rc 0 and no Layer 3 rejection message.
        self.assertEqual(rc, 0, f"stderr: {err}")
        self.assertNotIn("Layer 3 grounding", err)

    def test_no_entities_passes_as_pure_english(self):
        # CP4's honest limit: pure-English fluent prose passes Layer 3
        # because there are no entity-shaped tokens to ground. Layer 2
        # must have already classified this as fire or tautological; we
        # use a surface Layer 2 passes for this test.
        surface = _surface_with(
            disconfirmation=(
                "CI fails on main after push or tag verification rejects "
                "once the artifact lands"
            ),
        )
        rc, _out, err = _write_and_run(surface, self.cwd, "git push origin master")
        self.assertEqual(rc, 0, f"stderr: {err}")
        self.assertNotIn("Layer 3 grounding", err)


# ---------- Spec fluent-vacuous examples — documented CP4 limits ---------

class TestLayer3OnSpecFluentVacuousExamples(unittest.TestCase):
    """The three fluent-vacuous examples that CP3 cannot catch contain
    NO entity-shaped tokens. CP4's Layer 3 cannot catch them either —
    this is correct per spec § Layer 2 Composition cost (evading
    Layer 2 forces specificity, which raises Layer 3 surface area; an
    agent that produces NO specificity has no Layer 3 surface area but
    also cannot produce a Layer 4 `verification_trace`, which CP6
    will require).

    Tested explicitly so future tuning passes understand the
    compose-across-layers discipline.
    """

    def setUp(self):
        _grounding._clear_cache_for_tests()

    def tearDown(self):
        _grounding._clear_cache_for_tests()

    def test_cp4_honestly_passes_pure_english_fluent_vacuous(self):
        spec_examples_without_entities = [
            "the migration may produce unexpected behavior if edge cases are encountered",
            "if the build process exhibits anomalous behavior we should investigate before proceeding",
            "if results diverge from expectations we will return to first principles",
        ]
        for ex in spec_examples_without_entities:
            with self.subTest(example=ex):
                self.assertEqual(
                    _grounding.extract_entities(ex), set(),
                    "Layer 3 honest limit: these examples have no "
                    "extractable entities; they are closed at Layer 4/CP6, "
                    "not CP4. If this test starts FAILING by finding "
                    "entities, the extractor widened and the FP-averse "
                    "discipline needs a re-audit before CP5."
                )

    def test_fluent_vacuous_with_added_fake_entities_blocks(self):
        # Composition cost in action: an agent that evades Layer 2 by
        # adding specificity MUST name entities; fake entities trigger
        # Layer 3 rejection. This is the "evading Layer 2 helps Layer 3
        # catch you" property.
        tmp = __import__("tempfile").TemporaryDirectory()
        try:
            cwd = Path(tmp.name)
            _seed_project(cwd, {
                "core/real_thing.py": "# real module\n",
                "docs/PLAN.md": "# plan with user_id\n",
            })
            surface = _surface_with(
                disconfirmation=(
                    "if real_thing.py and user_id diverge from phantom_a, "
                    "phantom_b, phantom_c, and phantom_d while FAKE_X_Y "
                    "and FAKE_Z_W drift, we rollback after deployment"
                ),
            )
            verdict, detail = _grounding.ground_blueprint_fields(
                surface, "generic", cwd
            )
            self.assertEqual(verdict, "reject")
            self.assertIn("phantom_", detail)
        finally:
            tmp.cleanup()


# ---------- Graceful degrade ---------------------------------------------

class TestLayer3GracefulDegrade(unittest.TestCase):
    """Layer 3 MUST never crash the hot path. Any IO exception yields
    a 'pass' verdict so Layers 1 & 2 stay the ultimate enforcer."""

    def test_nonexistent_cwd_does_not_crash(self):
        _grounding._clear_cache_for_tests()
        nonexistent = Path("/tmp/definitely-not-a-real-path-for-episteme-cp4-test-xyzzy")
        surface = _surface_with(
            disconfirmation="if user_id and NODE_ENV diverge from phantom_a rollback",
        )
        verdict, _detail = _grounding.ground_blueprint_fields(
            surface, "generic", nonexistent
        )
        # With no project, no filenames, no content — all entities
        # ungrounded. Gate: grounded=0 < 2 → advisory (some ungrounded)
        # or pass if the function treats empty fingerprint specially.
        # Either is acceptable; crash is not.
        self.assertIn(verdict, ("pass", "advisory"))


# ---------- Latency ------------------------------------------------------

class TestLayer3Latency(unittest.TestCase):
    """Warm-cache grounding must stay within the spec's ~5 ms / call
    target on small projects. We assert a generous p100 of 100 ms per
    call averaged over 20 calls — anything slower is a regression."""

    def test_warm_cache_is_bounded(self):
        _grounding._clear_cache_for_tests()
        tmp = __import__("tempfile").TemporaryDirectory()
        try:
            cwd = Path(tmp.name)
            # Seed enough files to make content-scan non-trivial but
            # bounded by the 500-file cap.
            seed = {
                f"mod_{i}.py": f"# module {i}\nuser_id = {i}\n"
                for i in range(50)
            }
            seed["README.md"] = "user_id NODE_ENV PLAN.md baseline\n"
            _seed_project(cwd, seed)

            surface = _surface_with(
                disconfirmation=(
                    "if user_id drifts from NODE_ENV in README.md we rollback"
                ),
            )
            # Warm the cache once.
            _grounding.ground_blueprint_fields(surface, "generic", cwd)
            # Measure 20 warm calls.
            start = time.perf_counter()
            for _ in range(20):
                _grounding.ground_blueprint_fields(surface, "generic", cwd)
            total_ms = (time.perf_counter() - start) * 1000
            avg_ms = total_ms / 20
            self.assertLess(
                avg_ms, 100,
                f"Warm-cache average {avg_ms:.2f}ms exceeds 100ms budget"
            )
        finally:
            tmp.cleanup()
            _grounding._clear_cache_for_tests()


if __name__ == "__main__":
    unittest.main()
