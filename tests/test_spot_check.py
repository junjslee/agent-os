"""CP8 tests — Layer 8 spot-check sampling + review verdicts.

Covers:

- Rate computation (cold/warm decay, project override, max-not-sum
  multipliers, cap at 1.0).
- Sampling determinism (seeded RNG, empirical rate ≈ target ±1%,
  rate_zero short-circuit).
- Queue I/O (chained entries, idempotent re-sample, surface_snapshot
  preservation).
- Verdict writes (required-dimension validation, revision semantics,
  skip-with-TTL re-presentation).
- Phase 12 precondition (chain_integrity gains spot_check_queue
  stream; per-stream isolation).

All file-touching tests use ``EphemeralHome`` to redirect
``EPISTEME_HOME`` at a tempdir for the duration of the test.
"""
from __future__ import annotations

import json
import os
import random
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from core.hooks import _spot_check  # pyright: ignore[reportAttributeAccessIssue]


# ---------- Helpers ------------------------------------------------------


class EphemeralHome:
    """Redirect EPISTEME_HOME for the duration of the test."""
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


def _sample_inputs(**overrides) -> dict:
    """Default kwargs for maybe_sample; overridden per test."""
    base = {
        "correlation_id": "abc123",
        "op_label": "git push",
        "blueprint": "generic",
        "context_signature": {
            "project_name": "example",
            "project_tier": "python",
            "blueprint": "generic",
            "op_class": "git push",
            "constraint_head": None,
            "runtime_marker": "governed",
        },
        "surface_snapshot": {
            "core_question": "q",
            "disconfirmation": "d",
            "unknowns": [],
            "hypothesis": "",
        },
    }
    base.update(overrides)
    return base


# ---------- Rate computation --------------------------------------------


class RateComputation(unittest.TestCase):
    def test_cold_window_returns_10_percent(self):
        with EphemeralHome():
            anchor = datetime(2026, 4, 21, tzinfo=timezone.utc)
            now = anchor + timedelta(days=5)
            self.assertAlmostEqual(
                _spot_check.base_rate(now=now, anchor=anchor), 0.10
            )

    def test_warm_window_returns_5_percent(self):
        with EphemeralHome():
            anchor = datetime(2026, 4, 21, tzinfo=timezone.utc)
            now = anchor + timedelta(days=31)
            self.assertAlmostEqual(
                _spot_check.base_rate(now=now, anchor=anchor), 0.05
            )

    def test_project_override_wins(self):
        with EphemeralHome():
            with tempfile.TemporaryDirectory() as cwd:
                (Path(cwd) / ".episteme").mkdir()
                (Path(cwd) / ".episteme" / "spot_check_rate").write_text("0.25\n")
                rate = _spot_check.base_rate(cwd=Path(cwd))
                self.assertAlmostEqual(rate, 0.25)

    def test_project_override_clamped_to_unit_interval(self):
        with EphemeralHome():
            with tempfile.TemporaryDirectory() as cwd:
                (Path(cwd) / ".episteme").mkdir()
                (Path(cwd) / ".episteme" / "spot_check_rate").write_text("1.5\n")
                self.assertEqual(_spot_check.base_rate(cwd=Path(cwd)), 1.0)
                (Path(cwd) / ".episteme" / "spot_check_rate").write_text("-0.2\n")
                self.assertEqual(_spot_check.base_rate(cwd=Path(cwd)), 0.0)

    def test_malformed_override_falls_back_to_schedule(self):
        with EphemeralHome():
            with tempfile.TemporaryDirectory() as cwd:
                (Path(cwd) / ".episteme").mkdir()
                (Path(cwd) / ".episteme" / "spot_check_rate").write_text("not-a-number\n")
                anchor = datetime(2026, 4, 21, tzinfo=timezone.utc)
                now = anchor + timedelta(days=5)
                rate = _spot_check.base_rate(
                    now=now, cwd=Path(cwd), anchor=anchor
                )
                self.assertAlmostEqual(rate, 0.10)

    def test_effective_rate_max_not_sum(self):
        # 10% base × 2× (blueprint_fired) + 2× (synthesis_produced)
        # = max(2, 2) × 0.10 = 0.20, NOT 0.40.
        rate = _spot_check.effective_rate(
            0.10, {"blueprint_fired", "synthesis_produced"}
        )
        self.assertAlmostEqual(rate, 0.20)

    def test_effective_rate_capped_at_unity(self):
        # base 0.80 × 2 = 1.60 → clamped to 1.0.
        rate = _spot_check.effective_rate(0.80, {"blueprint_fired"})
        self.assertEqual(rate, 1.0)

    def test_effective_rate_no_multipliers(self):
        self.assertAlmostEqual(
            _spot_check.effective_rate(0.10, set()), 0.10
        )


class AnchorSeeding(unittest.TestCase):
    def test_anchor_seeded_on_first_call(self):
        with EphemeralHome() as home:
            self.assertFalse((home / "sample_schedule_anchor.json").exists())
            now = datetime(2026, 4, 21, tzinfo=timezone.utc)
            read = _spot_check.read_or_seed_anchor(now=now)
            self.assertEqual(read, now)
            self.assertTrue((home / "sample_schedule_anchor.json").exists())

    def test_anchor_read_preserves_across_calls(self):
        with EphemeralHome():
            first = datetime(2026, 4, 21, tzinfo=timezone.utc)
            _spot_check.read_or_seed_anchor(now=first)
            later = datetime(2026, 6, 1, tzinfo=timezone.utc)
            read = _spot_check.read_or_seed_anchor(now=later)
            self.assertEqual(read, first)  # first write wins


# ---------- Sampling determinism ----------------------------------------


class SamplingDeterminism(unittest.TestCase):
    def test_decide_sample_rate_zero_short_circuits(self):
        self.assertFalse(_spot_check.decide_sample(0.0))

    def test_decide_sample_rate_one_always_true(self):
        self.assertTrue(_spot_check.decide_sample(1.0))

    def test_seeded_rng_is_deterministic(self):
        rng_a = random.Random(42)
        rng_b = random.Random(42)
        choices_a = [
            _spot_check.decide_sample(0.5, rng=rng_a) for _ in range(100)
        ]
        choices_b = [
            _spot_check.decide_sample(0.5, rng=rng_b) for _ in range(100)
        ]
        self.assertEqual(choices_a, choices_b)

    def test_empirical_rate_approximates_target(self):
        rng = random.Random(1234)
        n = 20000
        target = 0.20
        hits = sum(
            _spot_check.decide_sample(target, rng=rng) for _ in range(n)
        )
        # Within ±1% of target.
        self.assertAlmostEqual(hits / n, target, delta=0.01)


# ---------- Queue I/O ---------------------------------------------------


class QueueWrite(unittest.TestCase):
    def test_rate_one_queues_entry(self):
        with EphemeralHome():
            # Anchor to today — cold window — AND override to 1.0 at
            # the multiplier path (blueprint_fired on fence).
            rng = random.Random(0)  # not used since rate=1.0
            with tempfile.TemporaryDirectory() as cwd:
                (Path(cwd) / ".episteme").mkdir()
                (Path(cwd) / ".episteme" / "spot_check_rate").write_text("1.0\n")
                result = _spot_check.maybe_sample(
                    **_sample_inputs(),
                    cwd=Path(cwd),
                    rng=rng,
                )
            self.assertTrue(result.queued)
            self.assertEqual(result.reason, "queued")
            # The entry is in the queue.
            entries = _spot_check.list_entries()
            self.assertEqual(len(entries), 1)
            self.assertEqual(
                entries[0].payload["correlation_id"], "abc123"
            )

    def test_rate_zero_does_not_queue(self):
        with EphemeralHome():
            with tempfile.TemporaryDirectory() as cwd:
                (Path(cwd) / ".episteme").mkdir()
                (Path(cwd) / ".episteme" / "spot_check_rate").write_text("0.0\n")
                result = _spot_check.maybe_sample(
                    **_sample_inputs(),
                    cwd=Path(cwd),
                )
            self.assertFalse(result.queued)
            self.assertEqual(result.reason, "rate_zero")
            self.assertEqual(len(_spot_check.list_entries()), 0)

    def test_idempotent_by_correlation_id(self):
        with EphemeralHome():
            with tempfile.TemporaryDirectory() as cwd:
                (Path(cwd) / ".episteme").mkdir()
                (Path(cwd) / ".episteme" / "spot_check_rate").write_text("1.0\n")
                r1 = _spot_check.maybe_sample(
                    **_sample_inputs(), cwd=Path(cwd)
                )
                r2 = _spot_check.maybe_sample(
                    **_sample_inputs(), cwd=Path(cwd)
                )
            self.assertTrue(r1.queued)
            self.assertFalse(r2.queued)
            self.assertEqual(r2.reason, "already_queued")
            self.assertEqual(len(_spot_check.list_entries()), 1)

    def test_blueprint_fired_multiplier_applied(self):
        with EphemeralHome():
            with tempfile.TemporaryDirectory() as cwd:
                (Path(cwd) / ".episteme").mkdir()
                (Path(cwd) / ".episteme" / "spot_check_rate").write_text("1.0\n")
                result = _spot_check.maybe_sample(
                    **_sample_inputs(blueprint="fence_reconstruction"),
                    cwd=Path(cwd),
                )
            self.assertTrue(result.queued)
            self.assertIn("blueprint_fired", result.multipliers)

    def test_synthesis_produced_multiplier_applied(self):
        with EphemeralHome():
            with tempfile.TemporaryDirectory() as cwd:
                (Path(cwd) / ".episteme").mkdir()
                (Path(cwd) / ".episteme" / "spot_check_rate").write_text("1.0\n")
                result = _spot_check.maybe_sample(
                    **_sample_inputs(blueprint="fence_reconstruction"),
                    synthesis_produced=True,
                    cwd=Path(cwd),
                )
            self.assertTrue(result.queued)
            self.assertIn("synthesis_produced", result.multipliers)
            self.assertIn("blueprint_fired", result.multipliers)

    def test_chain_is_intact_after_writes(self):
        from core.hooks import _chain  # pyright: ignore[reportAttributeAccessIssue]
        with EphemeralHome():
            with tempfile.TemporaryDirectory() as cwd:
                (Path(cwd) / ".episteme").mkdir()
                (Path(cwd) / ".episteme" / "spot_check_rate").write_text("1.0\n")
                for i in range(3):
                    _spot_check.maybe_sample(
                        **_sample_inputs(correlation_id=f"cid-{i}"),
                        cwd=Path(cwd),
                    )
                verdict = _spot_check.verify_chain()
            self.assertTrue(verdict.intact)
            self.assertEqual(verdict.total_entries, 3)


# ---------- Verdict writes ----------------------------------------------


def _seed_entry(correlation_id: str = "abc123", **overrides):
    """Helper — force-queue a single entry under EphemeralHome for
    verdict tests. Assumes caller is already inside EphemeralHome."""
    with tempfile.TemporaryDirectory() as cwd:
        (Path(cwd) / ".episteme").mkdir()
        (Path(cwd) / ".episteme" / "spot_check_rate").write_text("1.0\n")
        return _spot_check.maybe_sample(
            **_sample_inputs(correlation_id=correlation_id, **overrides),
            cwd=Path(cwd),
        )


class VerdictWrite(unittest.TestCase):
    def test_verdict_round_trip(self):
        with EphemeralHome():
            _seed_entry()
            _spot_check.write_verdict(
                correlation_id="abc123",
                verdicts={"surface_validity": "real"},
            )
            entry = _spot_check.get_entry("abc123")
            self.assertIsNotNone(entry)
            assert entry is not None
            self.assertIsNotNone(entry.verdict)
            assert entry.verdict is not None
            self.assertEqual(
                entry.verdict["verdicts"]["surface_validity"], "real"
            )

    def test_missing_entry_raises(self):
        with EphemeralHome():
            with self.assertRaises(_spot_check.ChainError):
                _spot_check.write_verdict(
                    correlation_id="does-not-exist",
                    verdicts={"surface_validity": "real"},
                )

    def test_surface_validity_required(self):
        with EphemeralHome():
            _seed_entry()
            with self.assertRaises(_spot_check.ChainError):
                _spot_check.write_verdict(
                    correlation_id="abc123",
                    verdicts={"note": "missing dimension"},
                )

    def test_protocol_quality_required_when_synthesis_produced(self):
        with EphemeralHome():
            _seed_entry(blueprint="fence_reconstruction")
            # The seed_entry above doesn't set synthesis_produced, so
            # force that multiplier directly. Re-seed with it:
            import shutil
            # Re-run seed with synthesis.
            with tempfile.TemporaryDirectory() as cwd:
                (Path(cwd) / ".episteme").mkdir()
                (Path(cwd) / ".episteme" / "spot_check_rate").write_text("1.0\n")
                _spot_check.maybe_sample(
                    **_sample_inputs(
                        correlation_id="synth1",
                        blueprint="fence_reconstruction",
                    ),
                    synthesis_produced=True,
                    cwd=Path(cwd),
                )
            with self.assertRaises(_spot_check.ChainError):
                _spot_check.write_verdict(
                    correlation_id="synth1",
                    verdicts={"surface_validity": "real"},  # missing protocol_quality
                )
            # Now with the required dimension:
            _spot_check.write_verdict(
                correlation_id="synth1",
                verdicts={
                    "surface_validity": "real",
                    "protocol_quality": "useful",
                },
            )

    def test_duplicate_verdict_requires_revise_flag(self):
        with EphemeralHome():
            _seed_entry()
            _spot_check.write_verdict(
                correlation_id="abc123",
                verdicts={"surface_validity": "real"},
            )
            with self.assertRaises(_spot_check.ChainError):
                _spot_check.write_verdict(
                    correlation_id="abc123",
                    verdicts={"surface_validity": "vapor"},
                )
            # Revision succeeds.
            _spot_check.write_verdict(
                correlation_id="abc123",
                verdicts={"surface_validity": "vapor"},
                is_revision=True,
            )
            entry = _spot_check.get_entry("abc123")
            assert entry is not None and entry.verdict is not None
            # Latest-wins semantics.
            self.assertEqual(
                entry.verdict["verdicts"]["surface_validity"], "vapor"
            )


class SkipTTL(unittest.TestCase):
    def test_skip_hides_entry_from_pending_until_ttl_expires(self):
        with EphemeralHome():
            _seed_entry(correlation_id="skip1")
            # Pending before skip.
            self.assertEqual(len(_spot_check.list_pending()), 1)
            # Write a skip at t=0.
            t0 = datetime(2026, 5, 1, tzinfo=timezone.utc)
            _spot_check.write_skip(
                "skip1", now=t0, ttl_seconds=60,
            )
            # Hidden while skip is active.
            within_ttl = t0 + timedelta(seconds=30)
            self.assertEqual(
                len(_spot_check.list_pending(now=within_ttl)), 0
            )
            # Re-presents after TTL.
            past_ttl = t0 + timedelta(seconds=120)
            self.assertEqual(
                len(_spot_check.list_pending(now=past_ttl)), 1
            )

    def test_skip_missing_entry_raises(self):
        with EphemeralHome():
            with self.assertRaises(_spot_check.ChainError):
                _spot_check.write_skip("does-not-exist")


# ---------- List / stats -------------------------------------------------


class ListAndStats(unittest.TestCase):
    def test_stats_counts_pending_and_verdicted(self):
        with EphemeralHome():
            _seed_entry(correlation_id="a")
            _seed_entry(correlation_id="b")
            _spot_check.write_verdict(
                correlation_id="a",
                verdicts={"surface_validity": "real"},
            )
            stats = _spot_check.stats()
            self.assertEqual(stats["total"], 2)
            self.assertEqual(stats["verdicted"], 1)
            self.assertEqual(stats["pending"], 1)
            self.assertEqual(
                stats["surface_validity_distribution"]["real"], 1
            )

    def test_list_pending_is_oldest_first(self):
        with EphemeralHome():
            _seed_entry(correlation_id="first")
            _seed_entry(correlation_id="second")
            pending = _spot_check.list_pending()
            self.assertEqual(len(pending), 2)
            self.assertEqual(pending[0].payload["correlation_id"], "first")


# ---------- Phase 12 precondition ---------------------------------------


class Phase12SpotCheckIntegration(unittest.TestCase):
    def test_audit_chain_integrity_includes_spot_check(self):
        from episteme._profile_audit import run_audit  # pyright: ignore[reportMissingImports]
        with EphemeralHome():
            result = run_audit(since_days=1)
        self.assertIn("chain_integrity", result)
        self.assertIn("spot_check_queue", result["chain_integrity"])
        # Empty queue is intact by definition.
        self.assertTrue(result["chain_integrity"]["spot_check_queue"]["intact"])

    def test_audit_reports_break_when_spot_check_tampered(self):
        from episteme._profile_audit import run_audit  # pyright: ignore[reportMissingImports]
        with EphemeralHome() as home:
            _seed_entry(correlation_id="a")
            _seed_entry(correlation_id="b")
            # Tamper.
            queue_path = home / "state" / "spot_check_queue.jsonl"
            text = queue_path.read_text()
            queue_path.write_text(text.replace('"a"', '"AA"'))
            result = run_audit(since_days=1)
        self.assertFalse(result["chain_integrity"]["spot_check_queue"]["intact"])
        # Per-stream isolation preserved.
        self.assertTrue(result["chain_integrity"]["protocols"]["intact"])


# ---------- Integration via PostToolUse build_post_context --------------


class BuildPostContext(unittest.TestCase):
    def test_build_context_from_prediction_record(self):
        with EphemeralHome() as home:
            # Write a synthetic prediction record matching what
            # reasoning_surface_guard._write_prediction produces.
            tel_dir = home / "telemetry"
            tel_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now(timezone.utc).isoformat()
            tel_path = tel_dir / f"{ts[:10]}-audit.jsonl"
            record = {
                "ts": ts,
                "event": "prediction",
                "correlation_id": "post1",
                "tool": "Bash",
                "op": "git push",
                "cwd": str(home),
                "command_executed": "git push origin main",
                "epistemic_prediction": {
                    "core_question": "Q",
                    "disconfirmation": "D",
                    "unknowns": ["u1"],
                    "hypothesis": "",
                },
                "blueprint_name": "generic",
                "exit_code": None,
            }
            tel_path.write_text(json.dumps(record) + "\n")

            ctx = _spot_check.build_post_context("post1")
            self.assertIsNotNone(ctx)
            assert ctx is not None
            self.assertEqual(ctx["op_label"], "git push")
            self.assertEqual(ctx["blueprint"], "generic")
            self.assertEqual(ctx["surface_snapshot"]["disconfirmation"], "D")

    def test_build_context_returns_none_when_prediction_missing(self):
        with EphemeralHome():
            ctx = _spot_check.build_post_context("nonexistent")
            self.assertIsNone(ctx)


if __name__ == "__main__":
    unittest.main()
