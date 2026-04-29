"""Tests for CP-ACTIVE-GUIDANCE-RANKING-AUDIT-01 (Event 86) — anti-Doxa
discipline at the protocol-routing layer.

Critical falsifiability test: ranking by context-signature specificity
must beat popularity / use-count / frequency-of-fire. The kernel exists
to counter Doxa; the routing layer must not reinstall it.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

# Locate core/hooks/_guidance + _framework + _chain
_REPO_ROOT = Path(__file__).resolve().parent.parent
_CORE_HOOKS_DIR = _REPO_ROOT / "core" / "hooks"
if str(_CORE_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_HOOKS_DIR))

import _guidance  # type: ignore  # pyright: ignore[reportMissingImports]
import _framework  # type: ignore  # pyright: ignore[reportMissingImports]
from _context_signature import ContextSignature  # type: ignore  # pyright: ignore[reportMissingImports]


def _make_protocol_payload(
    project: str = "p",
    blueprint: str = "fence",
    op_class: str = "rm",
    constraint_head: str = "fileX",
    runtime_marker: str = "claude",
    project_tier: str = "personal",
    rule: str = "rule",
    cid: str = "cid",
) -> dict:
    return {
        "blueprint": blueprint,
        "context_signature": {
            "project_name": project,
            "project_tier": project_tier,
            "blueprint": blueprint,
            "op_class": op_class,
            "constraint_head": constraint_head,
            "runtime_marker": runtime_marker,
        },
        "synthesized_protocol": rule,
        "correlation_id": cid,
    }


class AntiDoxaSpecificityWinsTests(unittest.TestCase):
    """The load-bearing falsification check: ranking-by-specificity
    beats ranking-by-popularity. Adversarial fixture: 1 high-overlap
    protocol vs N low-overlap protocols. The high-overlap one MUST win
    regardless of how many low-overlap ones exist."""

    def setUp(self):
        # Clear the warm cache to ensure each test reads fresh state.
        _guidance._clear_cache_for_tests()

    def test_specificity_wins_over_popularity(self):
        """5-of-6 overlap protocol (fired ONCE) wins over 4-of-6
        overlap protocols (fired 100 times)."""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "protocols.jsonl"

            # 100 protocols matching 4 of 6 fields (low specificity, high popularity)
            for i in range(100):
                _framework.write_protocol(
                    _make_protocol_payload(
                        project="p", blueprint="fence", op_class="rm",
                        constraint_head="fileX",
                        runtime_marker=f"runtime_{i}",  # different runtime → won't match query
                        project_tier=f"tier_{i}",        # different tier → won't match query
                        rule=f"popular_rule_{i}",
                        cid=f"popular_{i}",
                    ),
                    path=path,
                )

            # 1 protocol matching 5 of 6 fields (high specificity, fired once)
            _framework.write_protocol(
                _make_protocol_payload(
                    project="p", blueprint="fence", op_class="rm",
                    constraint_head="fileX",
                    runtime_marker="claude",
                    project_tier="tier_OTHER",  # 1 field mismatch
                    rule="rare_specific_rule",
                    cid="rare_specific",
                ),
                path=path,
            )

            # Patch _protocols_path to point at our fixture
            original_path_fn = _framework._protocols_path
            _framework._protocols_path = lambda: path
            try:
                _guidance._clear_cache_for_tests()
                candidate = ContextSignature(
                    project_name="p",
                    project_tier="tier_TARGET",
                    blueprint="fence",
                    op_class="rm",
                    constraint_head="fileX",
                    runtime_marker="claude",
                )
                # min_overlap=4 so low-overlap protocols also pass threshold
                top_k = _guidance.query_top_k(
                    candidate,
                    k=5,
                    cwd=Path(td),
                    min_overlap=4,
                )
            finally:
                _framework._protocols_path = original_path_fn
                _guidance._clear_cache_for_tests()

            self.assertGreater(len(top_k), 0)
            # The TOP result must be the high-specificity one (overlap=5),
            # not any of the 100 popular but lower-specificity ones (overlap=4).
            top = top_k[0]
            self.assertEqual(top.overlap, 5)
            self.assertEqual(top.correlation_id, "rare_specific")
            self.assertIn("rare_specific_rule", top.protocol_payload.get("synthesized_protocol", ""))


class QueryTopKBasicTests(unittest.TestCase):
    """Basic mechanics of query_top_k."""

    def setUp(self):
        _guidance._clear_cache_for_tests()

    def test_query_top_k_empty_when_no_protocols(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "protocols.jsonl"
            original_path_fn = _framework._protocols_path
            _framework._protocols_path = lambda: path
            try:
                _guidance._clear_cache_for_tests()
                candidate = ContextSignature(
                    project_name="p", project_tier="t", blueprint="b",
                    op_class="o", constraint_head="c", runtime_marker="r",
                )
                top_k = _guidance.query_top_k(candidate, k=3, cwd=Path(td), min_overlap=1)
            finally:
                _framework._protocols_path = original_path_fn
                _guidance._clear_cache_for_tests()
            self.assertEqual(top_k, [])

    def test_query_top_k_returns_at_most_k(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "protocols.jsonl"
            for i in range(10):
                _framework.write_protocol(
                    _make_protocol_payload(
                        project="p",
                        runtime_marker=f"r_{i}",
                        cid=f"cid_{i}",
                        rule=f"rule_{i}",
                    ),
                    path=path,
                )
            original_path_fn = _framework._protocols_path
            _framework._protocols_path = lambda: path
            try:
                _guidance._clear_cache_for_tests()
                candidate = ContextSignature(
                    project_name="p", project_tier="personal", blueprint="fence",
                    op_class="rm", constraint_head="fileX", runtime_marker="r_5",
                )
                top_k = _guidance.query_top_k(candidate, k=3, cwd=Path(td), min_overlap=1)
            finally:
                _framework._protocols_path = original_path_fn
                _guidance._clear_cache_for_tests()
            self.assertLessEqual(len(top_k), 3)


if __name__ == "__main__":
    unittest.main()
