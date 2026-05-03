"""Phase A · v1.0.1 — SessionStart `_noise_watch_line()` producer tests.

Covers the new advisory producer that surfaces the operator profile's
`cognitive.noise_signature` axis at SessionStart by reading the
`noise_watch_set` derived knob.

Shape-for-shape analogue of the existing `_framework_digest_line` and
`_profile_audit_line` tests (see `tests/test_guidance.py` and
`tests/test_profile_audit.py`). Advisory-only — zero exit-code impact —
soak-safe.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.hooks import session_context as sc  # pyright: ignore[reportAttributeAccessIssue]
from core.hooks import _derived_knobs  # pyright: ignore[reportAttributeAccessIssue]  # noqa: F401  # re-exported so pyright resolves sys.path bare-name import below


class _TmpKnobs:
    """Point `_derived_knobs._KNOBS_PATH` at a tmp file for one test.

    `_derived_knobs` uses a module-level `_KNOBS_PATH = Path.home() /
    ".episteme" / "derived_knobs.json"` constant rather than reading
    `EPISTEME_HOME` at call time (orthogonal gap, NOT fixed in Phase A).

    Subtlety: `session_context._noise_watch_line` imports `_derived_knobs`
    via a `sys.path` injection pointing at `core/hooks/` — so at runtime
    Python loads the module under the BARE name `_derived_knobs` at
    `sys.modules["_derived_knobs"]`. The test file imports the same
    source under the dotted path `core.hooks._derived_knobs`, which
    registers at `sys.modules["core.hooks._derived_knobs"]` — a
    DIFFERENT module object.

    To make the monkey-patch visible to the production code path, patch
    `_KNOBS_PATH` on every module in sys.modules whose source resolves
    to the same file. This is the only reliable pattern when a hook
    intentionally uses bare-name sys.path imports for standalone-script
    independence.
    """
    def __init__(self, knobs: dict | None):
        self._tmp = tempfile.TemporaryDirectory()
        self._knobs = knobs
        self._orig_by_module: dict[str, object] = {}

    def __enter__(self) -> Path:
        path = Path(self._tmp.name) / "derived_knobs.json"
        if self._knobs is not None:
            path.write_text(json.dumps(self._knobs), encoding="utf-8")

        # Pre-trigger session_context's internal sys.path-injected import
        # so sys.modules["_derived_knobs"] is populated before we patch.
        _hooks_dir = Path(sc.__file__).resolve().parent
        if str(_hooks_dir) not in sys.path:
            sys.path.insert(0, str(_hooks_dir))
        try:
            import _derived_knobs as _dk_bare  # type: ignore  # pyright: ignore[reportMissingImports]  # noqa: F401
        except ImportError:
            pass

        # Patch every module instance whose source is core/hooks/_derived_knobs.py.
        for mod_name in list(sys.modules.keys()):
            mod = sys.modules.get(mod_name)
            if mod is None:
                continue
            if not hasattr(mod, "_KNOBS_PATH"):
                continue
            mod_file = getattr(mod, "__file__", "")
            if not mod_file or "_derived_knobs" not in str(mod_file):
                continue
            self._orig_by_module[mod_name] = mod._KNOBS_PATH  # type: ignore[attr-defined]
            mod._KNOBS_PATH = path  # type: ignore[attr-defined]
        return path

    def __exit__(self, *a):  # noqa: ARG002 (unittest API)
        for mod_name, orig in self._orig_by_module.items():
            mod = sys.modules.get(mod_name)
            if mod is not None:
                mod._KNOBS_PATH = orig  # type: ignore[attr-defined]
        self._tmp.cleanup()


class NoiseWatchLineProducer(unittest.TestCase):
    """Unit tests for `session_context._noise_watch_line()`."""

    def test_silent_when_knobs_file_absent(self):
        # No file written — producer returns None.
        with _TmpKnobs(knobs=None):
            self.assertIsNone(sc._noise_watch_line())

    def test_silent_when_knob_missing_from_file(self):
        # File exists, other knobs set, but noise_watch_set is absent.
        with _TmpKnobs(knobs={"disconfirmation_specificity_min": 27}):
            self.assertIsNone(sc._noise_watch_line())

    def test_silent_when_knob_empty_list(self):
        with _TmpKnobs(knobs={"noise_watch_set": []}):
            self.assertIsNone(sc._noise_watch_line())

    def test_silent_when_knob_wrong_type(self):
        # Adapter contract says list[str]; defensive rejection of scalar.
        # _derived_knobs.load_knob(name, None) returns whatever-is-there
        # when default is None (no type coercion). The producer must
        # reject non-list values itself.
        with _TmpKnobs(knobs={"noise_watch_set": "status-pressure"}):
            self.assertIsNone(sc._noise_watch_line())

    def test_silent_when_list_has_no_strings(self):
        # List of non-string entries — producer filters to strings and
        # finds nothing to surface.
        with _TmpKnobs(knobs={"noise_watch_set": [1, 2, {"a": 1}]}):
            self.assertIsNone(sc._noise_watch_line())

    def test_renders_single_axis(self):
        with _TmpKnobs(knobs={"noise_watch_set": ["status-pressure"]}):
            line = sc._noise_watch_line()
        self.assertEqual(line, "noise watch: status-pressure")

    def test_renders_primary_and_secondary(self):
        # Schema declares primary + secondary → adapter emits 2-element list.
        with _TmpKnobs(
            knobs={"noise_watch_set": ["status-pressure", "false-urgency"]}
        ):
            line = sc._noise_watch_line()
        self.assertEqual(line, "noise watch: status-pressure, false-urgency")

    def test_ignores_non_string_entries_in_mixed_list(self):
        # Partial filtering — emits only the valid string entries.
        with _TmpKnobs(
            knobs={"noise_watch_set": ["status-pressure", 42, "regret"]}
        ):
            line = sc._noise_watch_line()
        self.assertEqual(line, "noise watch: status-pressure, regret")

    def test_graceful_degrade_on_malformed_json(self):
        # Malformed JSON in the knobs file — load_knob catches the
        # JSONDecodeError and returns the default (None). Producer
        # returns None. Use _TmpKnobs so both module instances are
        # patched (see class docstring for why).
        with _TmpKnobs(knobs=None) as path:
            path.write_text("{ this is not json", encoding="utf-8")
            self.assertIsNone(sc._noise_watch_line())


class _IsolatedEpistemeHome:
    """Point `EPISTEME_HOME` at a tmp dir so session_context.main() does
    not read or write the operator's real `~/.episteme/state/`
    (last_session.json, framework files) during the test."""
    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._orig = None

    def __enter__(self) -> Path:
        self._orig = os.environ.get("EPISTEME_HOME")
        os.environ["EPISTEME_HOME"] = self._tmp.name
        return Path(self._tmp.name)

    def __exit__(self, *a):
        if self._orig is None:
            os.environ.pop("EPISTEME_HOME", None)
        else:
            os.environ["EPISTEME_HOME"] = self._orig
        self._tmp.cleanup()


class _TmpCwd:
    """Chdir into a tmp dir for the duration of the test.

    Event 104 — `sc.main()` reads cwd-relative paths (`docs/NEXT_STEPS.md`,
    `HARNESS.md`, `.episteme/reasoning-surface.json`). When the test runs in
    the operator's real repo cwd, those files exist and their contents are
    appended to the captured banner — so a substring like `"noise watch:"`
    appearing in `docs/NEXT_STEPS.md` prose (e.g. documenting the producer's
    own banner format) leaks into the test output and breaks `assertNotIn`.

    Chdir-isolation makes `Path('docs/NEXT_STEPS.md').exists()` return False
    for the duration of the test, so the banner producer alone determines
    whether the noise-watch line appears.
    """
    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._orig: str | None = None

    def __enter__(self) -> Path:
        self._orig = os.getcwd()
        os.chdir(self._tmp.name)
        return Path(self._tmp.name)

    def __exit__(self, *a):  # noqa: ARG002
        if self._orig is not None:
            try:
                os.chdir(self._orig)
            except OSError:
                pass
        self._tmp.cleanup()


class NoiseWatchMainIntegration(unittest.TestCase):
    """End-to-end: main() emits the noise-watch line when the knob is set.

    Event 104 — wrapped in `_TmpCwd` so cwd-relative file reads (especially
    `docs/NEXT_STEPS.md`) cannot pollute the captured banner with prose
    substrings that incidentally match the noise-watch line format."""

    def test_main_includes_noise_watch_when_knob_set(self):
        import io
        with _TmpCwd(), _IsolatedEpistemeHome(), _TmpKnobs(
            knobs={
                "noise_watch_set": ["status-pressure", "false-urgency"],
            }
        ):
            # `main()` writes the banner to sys.stdout. Capture it so
            # the test does not pollute the runner's output.
            buf = io.StringIO()
            with patch("sys.stdout", buf):
                rc = sc.main()
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertIn("noise watch: status-pressure, false-urgency", out)

    def test_main_silent_on_noise_watch_when_knob_absent(self):
        import io
        with _TmpCwd(), _IsolatedEpistemeHome(), _TmpKnobs(knobs=None):
            buf = io.StringIO()
            with patch("sys.stdout", buf):
                rc = sc.main()
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertNotIn("noise watch:", out)


if __name__ == "__main__":
    unittest.main()
