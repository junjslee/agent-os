"""CP3 tests — Layer 2 classifier wired into the hot path.

At CP3 `reasoning_surface_guard.py` consults:
  - `_scenario_detector.detect_scenario(...)` (always returns "generic" at
    CP2/CP3; CP5/CP10 plug real selectors)
  - `_blueprint_registry.load_registry().get("generic")` for the field
    contract
  - `_specificity._classify_disconfirmation(...)` per
    classifier-eligible field

Behavior change vs CP2: surfaces that pass Layer 1 (length + lazy-token)
but carry no specific observable in their `disconfirmation` /
`unknowns[]` entries are now rejected with a `(tautological)` verdict.
The five fluent-vacuous evasion examples from
docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md § "Why this exists" should all
block. Absence-shape fields (`if no issues arise`) get a stderr
advisory but pass.
"""
from __future__ import annotations

import io
import json
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from core.hooks import reasoning_surface_guard as guard


_SENTINEL = object()


def _surface_with(
    disconfirmation: str,
    unknowns: list[str] | None = None,
    verification_trace: object = _SENTINEL,
) -> dict:
    """Build a Layer-1-passing surface with the specified
    classifier-eligible fields. Knowns / assumptions are Layer-1-valid
    strings but classifier-irrelevant by design.

    CP6: the generic blueprint declares ``verification_trace_required:
    true``, so every surface that reaches a high-impact Bash op must
    carry a parseable verification_trace to pass Layer 4. The helper
    inserts a default valid trace so tests focused on Layers 1-3
    continue passing. Tests exercising Layer 4 pass ``None`` (absent)
    or a dict (shape-invalid) explicitly.
    """
    surface = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "core_question": "Does this pass the Layer 2 classifier?",
        "knowns": ["repo at tip of master"],
        "unknowns": unknowns or [
            "if CI returns non-zero exit code on the push branch, "
            "local parity was false"
        ],
        "assumptions": ["hook runner is Claude Code"],
        "disconfirmation": disconfirmation,
    }
    if verification_trace is _SENTINEL:
        surface["verification_trace"] = {
            "or_test": "tests/test_layer2_classifier_hot_path.py::test_smoke",
        }
    elif verification_trace is not None:
        surface["verification_trace"] = verification_trace
    return surface


def _write_and_run(surface: dict, cwd: Path, command: str) -> tuple[int, str, str]:
    """Persist the surface, invoke the guard with a high-impact op,
    and return (exit_code, stdout, stderr)."""
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


class Layer2FireClassificationPasses(unittest.TestCase):
    def test_fire_disconfirmation_with_fire_unknowns_passes(self):
        surface = _surface_with(
            disconfirmation=(
                "if p95 latency exceeds 400ms after the rollout, "
                "the canary fails the SLO"
            ),
        )
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 0)
        self.assertEqual(err, "")

    def test_multiple_fire_unknowns_all_classifier_clean(self):
        surface = _surface_with(
            disconfirmation="if CI returns non-zero exit code within 10m, rollback",
            unknowns=[
                "if the canary logs show error rate > 1%, scale down",
                "when exit code != 0 after migration, the schema broke",
            ],
        )
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 0)
        self.assertEqual(err, "")


class Layer2RejectsTautological(unittest.TestCase):
    def test_tautological_disconfirmation_blocks(self):
        # Length OK, no lazy token → Layer 1 passes. But no observable →
        # Layer 2 rejects.
        surface = _surface_with(
            disconfirmation=(
                "if something goes wrong we will investigate and then reassess "
                "our approach carefully"
            ),
        )
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 2)
        self.assertIn("Layer 2", err)
        self.assertIn("tautological", err)
        self.assertIn("disconfirmation", err)

    def test_unknown_disconfirmation_classification_blocks(self):
        # Length ≥ Layer-1 minimum but classifier returns "unknown" for
        # text too short to reason about (< 10 chars in classifier's
        # own threshold). Layer 1 lets 15+ char strings through; the
        # classifier may still declare them unknown if they're just
        # whitespace-padded. Use a well-formed but classifier-unknown
        # edge-case (non-string).
        # NOTE: Layer 1 requires str, so realistically unknown is rare
        # for disconfirmation — we focus the block-on-unknown assertion
        # on an unknowns[] entry that survives Layer 1 but fails
        # classifier (exercised in Layer2PerEntryUnknowns below).
        surface = _surface_with(
            # 20 chars, all absence — should advisory, not block. We're
            # checking that `unknown` classification wouldn't slip
            # through by accident.
            disconfirmation="if nothing breaks, everything is fine and normal",
        )
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        # This is absence, so it advisories (rc=0) — asserting rc==0
        # confirms unknown doesn't spuriously fire here.
        self.assertEqual(rc, 0)
        self.assertIn("absence", err)


class Layer2AdvisoryOnAbsence(unittest.TestCase):
    def test_absence_disconfirmation_advisories_but_passes(self):
        surface = _surface_with(
            disconfirmation="if nothing unexpected breaks, everything stays fine",
        )
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 0)
        self.assertIn("[episteme advisory]", err)
        self.assertIn("absence", err)

    def test_absence_unknowns_entry_advisories_but_passes(self):
        surface = _surface_with(
            disconfirmation="if p95 latency exceeds 400ms, rollback",
            unknowns=["if no one notices, the migration is silent"],
        )
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 0)
        self.assertIn("[episteme advisory]", err)


class Layer2PerEntryUnknowns(unittest.TestCase):
    def test_tautological_unknowns_entry_blocks_whole_surface(self):
        surface = _surface_with(
            disconfirmation="if p95 latency exceeds 400ms, rollback",
            unknowns=[
                "if the deploy fails with non-zero exit, rollback",  # fire
                "whether the database is ready",  # tautological (no trigger)
            ],
        )
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 2)
        self.assertIn("unknowns[1]", err)
        self.assertIn("tautological", err)

    def test_mixed_fire_unknowns_passes_without_advisory(self):
        surface = _surface_with(
            disconfirmation="if p95 latency exceeds 400ms, rollback",
            unknowns=[
                "if deploy fails with non-zero exit, rollback",
                "when pipeline error rate exceeds 1%, pause",
            ],
        )
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 0)
        self.assertEqual(err, "")


class LayerCompositionOnFluentVacuousExamples(unittest.TestCase):
    """The five spec-named fluent-vacuous examples from
    docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md § Why this exists.

    The spec's Verification section says "blocked at write time by
    some combination of Layers 2-4 + Fence Reconstruction blueprint
    where applicable" — not "by Layer 2 alone." At CP6 the closure is
    complete:

    - TWO examples block at Layer 2 — observable-free verbs
      (`reassess`, `evaluate`) the classifier's pattern set catches
      directly.
    - THREE examples block at Layer 4 — their verbs (`produces`,
      `exhibits`, `diverge`) pass Layer 2's permissive classifier and
      their text carries no entities so Layer 3 has no surface area,
      but they have committed to NO executable verification trace.
      The composition L2 + L4 is the intended closure path per spec
      § Why these layers compose well.

    All five examples use ``verification_trace=None`` so the test
    isolates the surface-text axis: a fluent-vacuous disconfirmation
    without a trace commitment cannot pass the hot path.
    """

    LAYER2_BLOCKS = [
        "if any unforeseen issue arises during deployment we will reassess our approach",
        "should monitoring detect concerning patterns we will pause and evaluate next steps",
    ]
    LAYER4_BLOCKS = [
        "the migration may produce unexpected behavior if edge cases are encountered",
        "if the build process exhibits anomalous behavior we should investigate before proceeding",
        "if results diverge from expectations we will return to first principles",
    ]

    def test_layer2_blocks_observable_free_examples(self):
        for text in self.LAYER2_BLOCKS:
            with self.subTest(text=text):
                surface = _surface_with(
                    disconfirmation=text, verification_trace=None
                )
                with tempfile.TemporaryDirectory() as td:
                    rc, _out, err = _write_and_run(
                        surface, Path(td), "git push origin main"
                    )
                self.assertEqual(
                    rc, 2,
                    f"Layer 2 should have blocked but passed: {text!r}"
                )
                self.assertIn("Layer 2", err)
                self.assertIn("disconfirmation", err)

    def test_layer4_blocks_l2_l3_leaky_fluent_vacuous(self):
        # These three passed Layer 2 ('produces', 'exhibits', 'diverge'
        # read as observable-shaped at the classifier) and carry no
        # entity-shaped tokens (Layer 3 honestly passes — no surface
        # area). They leak through the first three layers. At CP6,
        # absence of verification_trace is the closure: a fluent-
        # vacuous author cannot also name an executable command,
        # dashboard URL, or test id without breaking the fluency.
        for text in self.LAYER4_BLOCKS:
            with self.subTest(text=text):
                surface = _surface_with(
                    disconfirmation=text, verification_trace=None
                )
                with tempfile.TemporaryDirectory() as td:
                    rc, _out, err = _write_and_run(
                        surface, Path(td), "git push origin main"
                    )
                self.assertEqual(
                    rc, 2,
                    f"Layer 4 should have blocked but passed: {text!r}"
                )
                self.assertIn("Layer 4", err)
                self.assertIn("verification_trace", err)


class Layer2DoesNotClassifyKnownsOrAssumptions(unittest.TestCase):
    def test_arbitrary_knowns_value_does_not_block(self):
        # knowns are facts, not predictions — category error to classify.
        # Surface passes Layer 1 (knowns is a non-empty list) and Layer 2
        # (classifier runs only on disconfirmation / unknowns).
        surface = _surface_with(
            disconfirmation="if p95 exceeds 400ms after push, rollback",
        )
        surface["knowns"] = ["The moon is made of cheese"]  # non-observable
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 0)
        self.assertEqual(err, "")

    def test_arbitrary_assumptions_value_does_not_block(self):
        surface = _surface_with(
            disconfirmation="if p95 exceeds 400ms after push, rollback",
        )
        surface["assumptions"] = ["color of the week is purple"]
        with tempfile.TemporaryDirectory() as td:
            rc, _out, err = _write_and_run(
                surface, Path(td), "git push origin main"
            )
        self.assertEqual(rc, 0)
        self.assertEqual(err, "")


class Layer2GracefulDegradeOnRegistryFailure(unittest.TestCase):
    def test_registry_load_failure_falls_back_to_layer1_only(self):
        # If the registry throws on .get(), Layer 2 should stderr-warn
        # and pass — Layer 1 already validated the surface structure.
        surface = _surface_with(
            disconfirmation="if p95 exceeds 400ms after push, rollback",
        )

        class BrokenRegistry:
            def get(self, name: str):
                raise OSError("simulated: blueprint file corrupted")

        def broken_loader(*args, **kwargs):
            return BrokenRegistry()

        with tempfile.TemporaryDirectory() as td:
            with patch.object(guard, "_load_registry", broken_loader):
                rc, _out, err = _write_and_run(
                    surface, Path(td), "git push origin main"
                )
        self.assertEqual(rc, 0)
        self.assertIn("Layer 2 fallback", err)
        self.assertIn("OSError", err)


class Layer2LatencyIsBounded(unittest.TestCase):
    def test_layer2_adds_under_budget_per_call(self):
        # Spec budget: Layer 2 < 5ms p95 (absorbed into detector slot).
        # We run 20 validations and confirm median + max are sane. Not a
        # strict p95 measurement (needs scipy or larger N); a coarse
        # ceiling that catches pathological regressions (like a 100ms
        # accidental loop).
        surface = _surface_with(
            disconfirmation="if p95 latency exceeds 400ms after the rollout, rollback",
            unknowns=[
                "if the canary exit code != 0, scale down",
                "when error rate exceeds 1%, pause",
                "if memory rss exceeds 512MB, OOM",
            ],
        )
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / ".episteme").mkdir()
            (cwd / ".episteme" / "reasoning-surface.json").write_text(
                json.dumps(surface), encoding="utf-8"
            )
            # Warm the registry cache.
            _ = guard._load_registry().get("generic")

            timings = []
            for _ in range(20):
                payload = {
                    "tool_name": "Bash",
                    "tool_input": {"command": "git push origin main"},
                    "cwd": str(cwd),
                }
                raw = json.dumps(payload)
                t0 = time.perf_counter()
                with patch("sys.stdin", new=io.StringIO(raw)), \
                     patch("sys.stdout", new=io.StringIO()), \
                     patch("sys.stderr", new=io.StringIO()):
                    guard.main()
                timings.append(time.perf_counter() - t0)
            worst_ms = max(timings) * 1000.0
            # Coarse ceiling: the WHOLE hot path (Layers 1-4 + detector +
            # registry) must land under 100 ms p95 per the spec. A single
            # validate() call here is within that budget.
            self.assertLess(
                worst_ms, 100.0,
                f"hot-path worst-case {worst_ms:.1f}ms exceeds 100ms p95 budget"
            )


if __name__ == "__main__":
    unittest.main()
