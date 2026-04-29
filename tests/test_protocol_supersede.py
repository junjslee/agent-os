"""Tests for CP-TEMPORAL-INTEGRITY-EXPANSION-01 Item 4 (Event 84) —
synthesized protocols supersede-with-history.

Coverage:
- Auto-supersede detection on write_protocol when context_signature matches
- list_protocols filters superseded entries by default
- list_protocols(include_superseded=True) returns full chain
- walk_supersede_chains groups by context_signature; returns only chains > 1
- Chain integrity preserved across multiple supersedes
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

# Locate core/hooks/_framework + _chain
_REPO_ROOT = Path(__file__).resolve().parent.parent
_CORE_HOOKS_DIR = _REPO_ROOT / "core" / "hooks"
if str(_CORE_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_HOOKS_DIR))

import _framework  # type: ignore  # pyright: ignore[reportMissingImports]
import _chain  # type: ignore  # pyright: ignore[reportMissingImports]


def _make_payload(project: str = "p", blueprint: str = "fence", **extra) -> dict:
    return {
        "blueprint": blueprint,
        "context_signature": {
            "project_name": project,
            "blueprint": blueprint,
            "op_class": "test",
        },
        "synthesized_protocol": "test rule",
        "correlation_id": "cid-test",
        **extra,
    }


class AutoSupersedeOnWriteTests(unittest.TestCase):
    def test_first_protocol_has_no_supersedes(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "protocols.jsonl"
            envelope = _framework.write_protocol(_make_payload(), path=path)
            self.assertNotIn("supersedes", envelope["payload"])

    def test_second_protocol_with_same_context_sig_supersedes_first(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "protocols.jsonl"
            first = _framework.write_protocol(_make_payload(), path=path)
            second = _framework.write_protocol(
                _make_payload(synthesized_protocol="updated rule"),
                path=path,
            )
            self.assertEqual(second["payload"]["supersedes"], first["entry_hash"])

    def test_different_context_sig_does_not_supersede(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "protocols.jsonl"
            _framework.write_protocol(_make_payload(project="p1"), path=path)
            second = _framework.write_protocol(_make_payload(project="p2"), path=path)
            self.assertNotIn("supersedes", second["payload"])

    def test_explicit_supersedes_not_overwritten(self):
        """Caller can explicitly set supersedes; auto-detection must not
        overwrite it."""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "protocols.jsonl"
            _framework.write_protocol(_make_payload(), path=path)
            second = _framework.write_protocol(
                _make_payload(supersedes="sha256:explicit"),
                path=path,
            )
            self.assertEqual(second["payload"]["supersedes"], "sha256:explicit")


class ListProtocolsFilterTests(unittest.TestCase):
    def test_default_filters_superseded(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "protocols.jsonl"
            _framework.write_protocol(_make_payload(synthesized_protocol="v1"), path=path)
            _framework.write_protocol(_make_payload(synthesized_protocol="v2"), path=path)
            active = _framework.list_protocols(path=path)
            self.assertEqual(len(active), 1)
            self.assertEqual(active[0]["payload"]["synthesized_protocol"], "v2")

    def test_include_superseded_returns_all(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "protocols.jsonl"
            _framework.write_protocol(_make_payload(synthesized_protocol="v1"), path=path)
            _framework.write_protocol(_make_payload(synthesized_protocol="v2"), path=path)
            full = _framework.list_protocols(path=path, include_superseded=True)
            self.assertEqual(len(full), 2)

    def test_three_protocols_only_latest_active(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "protocols.jsonl"
            _framework.write_protocol(_make_payload(synthesized_protocol="v1"), path=path)
            _framework.write_protocol(_make_payload(synthesized_protocol="v2"), path=path)
            _framework.write_protocol(_make_payload(synthesized_protocol="v3"), path=path)
            active = _framework.list_protocols(path=path)
            self.assertEqual(len(active), 1)
            self.assertEqual(active[0]["payload"]["synthesized_protocol"], "v3")
            full = _framework.list_protocols(path=path, include_superseded=True)
            self.assertEqual(len(full), 3)


class WalkSupersedeChainsTests(unittest.TestCase):
    def test_no_chains_returned_for_unique_context_sigs(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "protocols.jsonl"
            _framework.write_protocol(_make_payload(project="p1"), path=path)
            _framework.write_protocol(_make_payload(project="p2"), path=path)
            chains = _framework.walk_supersede_chains(path=path)
            self.assertEqual(chains, [])

    def test_chain_returned_for_multiple_entries_same_sig(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "protocols.jsonl"
            _framework.write_protocol(_make_payload(synthesized_protocol="v1"), path=path)
            _framework.write_protocol(_make_payload(synthesized_protocol="v2"), path=path)
            chains = _framework.walk_supersede_chains(path=path)
            self.assertEqual(len(chains), 1)
            self.assertEqual(len(chains[0]), 2)


class ChainIntegrityTests(unittest.TestCase):
    def test_chain_intact_after_supersede_writes(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "protocols.jsonl"
            _framework.write_protocol(_make_payload(synthesized_protocol="v1"), path=path)
            _framework.write_protocol(_make_payload(synthesized_protocol="v2"), path=path)
            _framework.write_protocol(_make_payload(project="p2"), path=path)
            _framework.write_protocol(_make_payload(synthesized_protocol="v3"), path=path)
            verdict = _chain.verify_chain(path)
            self.assertTrue(verdict.intact)
            self.assertEqual(verdict.total_entries, 4)


if __name__ == "__main__":
    unittest.main()
