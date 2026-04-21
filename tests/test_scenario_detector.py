"""CP2 tests — scenario detector + blueprint registry substrate.

At CP2 the hot path does NOT yet consult the detector or registry
(`reasoning_surface_guard.py` is untouched). These tests cover the
contracts CP3+ will depend on:

- Registry loads the generic_fallback blueprint from
  `core/blueprints/` and exposes it by name.
- The generic blueprint carries exactly the historic four fields
  (knowns / unknowns / assumptions / disconfirmation) in that order —
  this is the guarantee that pre-v1.0-RC surfaces validate unchanged.
- The detector stub returns the string `"generic"` for every input
  shape the hot path is expected to pass in (empty, plausible, with or
  without surface text and project context).
- The detector signature is frozen — CP3 will call with the exact
  parameter names asserted below. Any rename is a governance event.
- Load is lazy + cached so CP3's hot-path call cost is a dict lookup,
  not a directory scan.
- Malformed blueprint files are rejected with a named exception, not
  silently skipped.
"""
from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path

from core.hooks._blueprint_registry import (
    BLUEPRINTS_DIR,
    BlueprintParseError,
    BlueprintValidationError,
    Registry,
    load_registry,
)
from core.hooks._scenario_detector import GENERIC_FALLBACK, detect_scenario


class GenericFallbackLoad(unittest.TestCase):
    """The source-of-truth blueprint for CP2."""

    def test_generic_is_known(self):
        reg = load_registry()
        self.assertIn("generic", reg.known_names())

    def test_generic_has_exactly_the_historic_four_fields(self):
        reg = load_registry()
        generic = reg.get("generic")
        # Order matters — kernel/REASONING_SURFACE.md documents this
        # ordering as the "grain" of epistemic discipline (settled →
        # open → provisional → falsification-condition).
        self.assertEqual(
            generic.required_fields,
            ("knowns", "unknowns", "assumptions", "disconfirmation"),
        )

    def test_generic_has_no_synthesis_arm(self):
        reg = load_registry()
        generic = reg.get("generic")
        # The generic fallback does NOT emit framework protocols —
        # only named blueprints (A / B / D) with synthesis arms do.
        self.assertFalse(generic.synthesis_arm)

    def test_generic_has_no_selector_triggers_at_cp2(self):
        reg = load_registry()
        generic = reg.get("generic")
        self.assertEqual(generic.selector_triggers, ())

    def test_generic_version_is_1(self):
        reg = load_registry()
        self.assertEqual(reg.get("generic").version, 1)

    def test_generic_source_path_points_at_repo_blueprint(self):
        reg = load_registry()
        generic = reg.get("generic")
        self.assertEqual(generic.source_path, BLUEPRINTS_DIR / "generic_fallback.yaml")


class DetectorStub(unittest.TestCase):
    """CP2 detector always returns 'generic'. Real selectors at CP5 / CP10."""

    def test_returns_generic_for_empty_op(self):
        self.assertEqual(detect_scenario({}), GENERIC_FALLBACK)

    def test_returns_generic_for_plausible_constraint_removal_input(self):
        # CP5 will route this to "fence_reconstruction" when the real
        # selector lands. At CP2 the stub ignores content.
        result = detect_scenario(
            {"tool_name": "Bash", "command": "rm config/legacy-policy.yaml"},
            surface_text="Removing legacy constraint because ...",
            project_context={"cwd": "/some/project"},
        )
        self.assertEqual(result, GENERIC_FALLBACK)

    def test_returns_generic_for_plausible_cascade_input(self):
        # CP10 will route this to "architectural_cascade" when the real
        # selector lands.
        result = detect_scenario(
            {"tool_name": "Edit", "file_path": "core/schemas/foo.json"},
            surface_text='{"flaw_classification": "schema-implementation-drift"}',
            project_context={"diff": "core/schemas/foo.json + CLI changes"},
        )
        self.assertEqual(result, GENERIC_FALLBACK)

    def test_signature_is_stable(self):
        # CP3 commits to this exact signature. Any rename or reorder is
        # a governance event; this test locks it in.
        sig = inspect.signature(detect_scenario)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ["pending_op", "surface_text", "project_context"])

    def test_generic_fallback_constant_matches_blueprint_name(self):
        reg = load_registry()
        self.assertEqual(GENERIC_FALLBACK, reg.get(GENERIC_FALLBACK).name)


class RegistryErrorCases(unittest.TestCase):
    def test_unknown_blueprint_raises_keyerror_with_known_list(self):
        reg = load_registry()
        with self.assertRaises(KeyError) as ctx:
            # At CP5 fence_reconstruction is realized. axiomatic_judgment
            # lands at CP6 as schema-only; use it as the "not yet
            # realized" probe. When CP6 ships, migrate to another
            # not-yet-realized name (consequence_chain or
            # architectural_cascade).
            reg.get("axiomatic_judgment")
        message = str(ctx.exception)
        self.assertIn("axiomatic_judgment", message)
        # The error lists what IS known — so the operator can see the gap.
        self.assertIn("generic", message)
        self.assertIn("fence_reconstruction", message)  # CP5 now realized

    def test_malformed_yaml_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.yaml"
            # Indented line with no top-level key — the parser's expected
            # rejection shape.
            bad.write_text("  this is not a top-level key: value\n")
            reg = Registry(Path(tmp))
            with self.assertRaises(BlueprintParseError):
                reg.known_names()

    def test_missing_name_key_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "no_name.yaml"
            missing.write_text("required_fields: []\nversion: 1\n")
            reg = Registry(Path(tmp))
            with self.assertRaises(BlueprintValidationError):
                reg.known_names()

    def test_duplicate_blueprint_name_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.yaml"
            b = Path(tmp) / "b.yaml"
            shared = (
                "name: shared\n"
                "version: 1\n"
                "required_fields: []\n"
                "optional_fields: []\n"
                "synthesis_arm: false\n"
                "selector_triggers: []\n"
            )
            a.write_text(shared)
            b.write_text(shared)
            reg = Registry(Path(tmp))
            with self.assertRaises(BlueprintValidationError) as ctx:
                reg.known_names()
            self.assertIn("duplicate", str(ctx.exception).lower())

    def test_non_list_required_fields_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad_shape.yaml"
            bad.write_text("name: foo\nrequired_fields: not_a_list\n")
            reg = Registry(Path(tmp))
            with self.assertRaises(BlueprintValidationError):
                reg.known_names()


class RegistryBehavior(unittest.TestCase):
    def test_empty_directory_yields_empty_registry(self):
        # Supports downstream forks installing without core/blueprints/ —
        # the kernel falls back to generic validation via other paths.
        with tempfile.TemporaryDirectory() as tmp:
            reg = Registry(Path(tmp))
            self.assertEqual(reg.known_names(), ())

    def test_nonexistent_directory_yields_empty_registry(self):
        reg = Registry(Path("/definitely/does/not/exist/here"))
        self.assertEqual(reg.known_names(), ())

    def test_load_is_cached(self):
        reg = load_registry()
        first = reg.get("generic")
        second = reg.get("generic")
        # Same frozen-dataclass instance — CP3 cost budget depends on
        # the cache hit, not a re-read.
        self.assertIs(first, second)

    def test_reload_invalidates_cache(self):
        reg = load_registry()
        first = reg.get("generic")
        reg.reload()
        second = reg.get("generic")
        # Different instance after reload — confirms cache was actually
        # refreshed (for tests that modify blueprints on disk).
        self.assertIsNot(first, second)
        self.assertEqual(first, second)  # but structurally equal

    def test_parser_handles_folded_block_scalar(self):
        with tempfile.TemporaryDirectory() as tmp:
            bp = Path(tmp) / "folded.yaml"
            bp.write_text(
                "name: folded_test\n"
                "description: >\n"
                "  line one\n"
                "  line two\n"
                "  line three\n"
                "required_fields: []\n"
            )
            reg = Registry(Path(tmp))
            folded = reg.get("folded_test")
            self.assertEqual(folded.description, "line one line two line three")


class BlueprintDataclass(unittest.TestCase):
    def test_blueprint_is_frozen(self):
        reg = load_registry()
        generic = reg.get("generic")
        # Frozen dataclass — mutation attempts raise. Guarantees the
        # cached instance can be shared across hot-path calls safely.
        with self.assertRaises(Exception):
            generic.name = "not_generic"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
