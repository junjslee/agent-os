"""Tests for `episteme evolve friction` (v0.10.0-alpha heuristic analyzer).

The analyzer pairs prediction ↔ outcome records by `correlation_id`,
flags cases where exit_code ≠ 0 despite a positive prediction, and ranks
the unknowns that appeared most often in failing runs.
"""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from episteme import cli


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _pred(cid: str, *, op: str, cmd: str, unknowns: list[str], disc: str, ts: str) -> dict:
    return {
        "ts": ts,
        "event": "prediction",
        "correlation_id": cid,
        "tool": "Bash",
        "op": op,
        "cwd": "/tmp/proj",
        "command_executed": cmd,
        "epistemic_prediction": {
            "core_question": "test",
            "disconfirmation": disc,
            "unknowns": unknowns,
            "hypothesis": "should pass",
        },
        "exit_code": None,
    }


def _out(cid: str, *, exit_code: int, ts: str, cmd: str = "") -> dict:
    return {
        "ts": ts,
        "event": "outcome",
        "correlation_id": cid,
        "tool": "Bash",
        "cwd": "/tmp/proj",
        "command_executed": cmd,
        "exit_code": exit_code,
        "status": "error" if exit_code != 0 else "success",
    }


class FrictionAnalyzerTests(unittest.TestCase):
    def test_empty_telemetry_dir_emits_no_friction_message(self):
        with tempfile.TemporaryDirectory() as td:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli._evolve_friction(telemetry_dir=Path(td) / "empty")
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertIn("Episteme Friction Report", out)
            self.assertIn("No friction detected yet", out)

    def test_ranks_most_violated_unknowns(self):
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            _write_jsonl(
                tdir / "2026-04-20-audit.jsonl",
                [
                    _pred(
                        "c1",
                        op="git push",
                        cmd="git push origin main",
                        unknowns=["remote diverged since last pull"],
                        disc="push rejected by remote or CI fails on main",
                        ts="2026-04-20T10:00:00+00:00",
                    ),
                    _out("c1", exit_code=1, ts="2026-04-20T10:00:05+00:00"),
                    _pred(
                        "c2",
                        op="git push",
                        cmd="git push origin feature",
                        unknowns=["remote diverged since last pull"],
                        disc="non-fast-forward rejection",
                        ts="2026-04-20T11:00:00+00:00",
                    ),
                    _out("c2", exit_code=1, ts="2026-04-20T11:00:02+00:00"),
                    _pred(
                        "c3",
                        op="npm publish",
                        cmd="npm publish",
                        unknowns=["authenticated session for registry"],
                        disc="npm ERR! 401 unauthorized",
                        ts="2026-04-20T12:00:00+00:00",
                    ),
                    _out("c3", exit_code=1, ts="2026-04-20T12:00:03+00:00"),
                    _pred(
                        "c4",
                        op="terraform apply",
                        cmd="terraform apply -auto-approve",
                        unknowns=["state lock held by another run"],
                        disc="terraform errors with state lock timeout",
                        ts="2026-04-20T13:00:00+00:00",
                    ),
                    _out("c4", exit_code=0, ts="2026-04-20T13:00:10+00:00"),
                ],
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli._evolve_friction(telemetry_dir=tdir)
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertIn("Friction events (exit_code ≠ 0", out)
            self.assertIn("Paired predictions / outcomes: **4**", out)
            # 3 failures (c1,c2,c3) — c4 succeeded.
            self.assertIn("Friction events (exit_code ≠ 0 despite positive prediction): **3**", out)
            # `remote diverged since last pull` appeared twice — top of the list.
            # `authenticated session for registry` once.
            lines = out.splitlines()
            top_section = "\n".join(lines)
            self.assertIn("×2", top_section)
            self.assertIn("remote diverged since last pull", top_section)
            self.assertIn("authenticated session for registry", top_section)
            # git push appears 2x in failing ops, npm publish 1x.
            self.assertIn("`git push` — 2 failing run(s)", out)
            self.assertIn("`npm publish` — 1 failing run(s)", out)

    def test_empty_prediction_envelope_is_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            _write_jsonl(
                tdir / "2026-04-20-audit.jsonl",
                [
                    {
                        "ts": "2026-04-20T10:00:00+00:00",
                        "event": "prediction",
                        "correlation_id": "c-empty",
                        "tool": "Bash",
                        "op": "git push",
                        "epistemic_prediction": {
                            "core_question": "",
                            "disconfirmation": "",
                            "unknowns": [],
                            "hypothesis": "",
                        },
                    },
                    _out("c-empty", exit_code=1, ts="2026-04-20T10:00:05+00:00"),
                ],
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli._evolve_friction(telemetry_dir=tdir)
            self.assertEqual(rc, 0)
            # No positive prediction → not a calibration signal.
            self.assertIn("No friction detected yet", buf.getvalue())

    def test_missing_outcome_is_ignored(self):
        """Unpaired predictions (no outcome) are not friction; they may just be in-flight."""
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            _write_jsonl(
                tdir / "2026-04-20-audit.jsonl",
                [
                    _pred(
                        "c-orphan",
                        op="git push",
                        cmd="git push",
                        unknowns=["x" * 20],
                        disc="y" * 20,
                        ts="2026-04-20T10:00:00+00:00",
                    ),
                ],
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli._evolve_friction(telemetry_dir=tdir)
            self.assertEqual(rc, 0)
            self.assertIn("No friction detected yet", buf.getvalue())

    def test_malformed_line_does_not_crash(self):
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            path = tdir / "2026-04-20-audit.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write("this is not json\n")
                f.write(json.dumps(_pred(
                    "c1", op="git push", cmd="git push",
                    unknowns=["a real unknown about remote state"],
                    disc="push rejected by remote protections",
                    ts="2026-04-20T10:00:00+00:00",
                )) + "\n")
                f.write(json.dumps(_out("c1", exit_code=1, ts="2026-04-20T10:00:05+00:00")) + "\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli._evolve_friction(telemetry_dir=tdir)
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertIn("Friction events", out)
            self.assertIn("a real unknown about remote state", out)

    def test_output_flag_writes_file(self):
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            _write_jsonl(
                tdir / "2026-04-20-audit.jsonl",
                [
                    _pred(
                        "c1", op="git push", cmd="git push",
                        unknowns=["unknown about registry auth state"],
                        disc="disc about auth failure mode",
                        ts="2026-04-20T10:00:00+00:00",
                    ),
                    _out("c1", exit_code=1, ts="2026-04-20T10:00:05+00:00"),
                ],
            )
            out_path = tdir / "out" / "friction.md"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli._evolve_friction(telemetry_dir=tdir, output_path=out_path)
            self.assertEqual(rc, 0)
            self.assertTrue(out_path.exists())
            body = out_path.read_text(encoding="utf-8")
            self.assertIn("Episteme Friction Report", body)
            self.assertIn("unknown about registry auth state", body)

    def test_top_n_limits_ranking(self):
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            records: list[dict] = []
            for i in range(8):
                cid = f"c{i}"
                records.append(
                    _pred(
                        cid, op=f"op-{i}", cmd=f"cmd-{i}",
                        unknowns=[f"unknown number {i} with enough length"],
                        disc=f"disconfirm number {i} with enough length",
                        ts=f"2026-04-20T{10 + i:02d}:00:00+00:00",
                    )
                )
                records.append(_out(cid, exit_code=1, ts=f"2026-04-20T{10 + i:02d}:00:05+00:00"))
            _write_jsonl(tdir / "2026-04-20-audit.jsonl", records)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli._evolve_friction(telemetry_dir=tdir, top_n=3)
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            # Each unknown appears once; top_n=3 → only three numbered entries.
            unknowns_section = out.split("## Operations with most friction")[0]
            ranked_lines = [ln for ln in unknowns_section.splitlines() if ln.startswith(("1.", "2.", "3.", "4."))]
            numbered = [ln for ln in ranked_lines if ln[0].isdigit()]
            self.assertLessEqual(len(numbered), 3)

    def test_negative_top_n_clamps_to_empty_ranked_sections(self):
        """top_n = -1 previously sliced from the tail (ranked[:-1]) and
        produced garbage output. Now clamps to 0 → no ranked entries but
        the report still renders and exits 0."""
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            _write_jsonl(
                tdir / "2026-04-20-audit.jsonl",
                [
                    _pred(
                        "c1",
                        op="git push",
                        cmd="git push origin main",
                        unknowns=["remote diverged since last pull sync"],
                        disc="push rejected by remote protections or CI red",
                        ts="2026-04-20T10:00:00+00:00",
                    ),
                    _out("c1", exit_code=1, ts="2026-04-20T10:00:05+00:00"),
                ],
            )
            buf_neg = io.StringIO()
            with redirect_stdout(buf_neg):
                rc_neg = cli._evolve_friction(telemetry_dir=tdir, top_n=-1)
            buf_zero = io.StringIO()
            with redirect_stdout(buf_zero):
                rc_zero = cli._evolve_friction(telemetry_dir=tdir, top_n=0)
            self.assertEqual(rc_neg, 0)
            self.assertEqual(rc_zero, 0)
            # Both runs detect the friction event; neither produces a ranked list.
            for out in (buf_neg.getvalue(), buf_zero.getvalue()):
                self.assertIn("Friction events (exit_code ≠ 0 despite positive prediction): **1**", out)
                self.assertIn("_(no unknowns recorded in failing runs)_", out)
                self.assertIn("_(no op labels recorded)_", out)
            # The unknown must not leak into output under negative top_n
            # (which previously produced tail-sliced garbage).
            self.assertNotIn("remote diverged since last pull sync", buf_neg.getvalue())


class GrepLikeNoMatchFilterTests(unittest.TestCase):
    """Event 103 — `_is_grep_like_no_match` filters benign exit=1 from
    grep / diff / test / find / cmp out of the friction stream while
    keeping (a) real failures from those tools at exit ≥ 2, and (b) any
    non-zero exit from non-grep-class commands."""

    def test_grep_no_match_exit_1_is_filtered_out(self):
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            _write_jsonl(
                tdir / "2026-04-20-audit.jsonl",
                [
                    _pred(
                        "g1", op="grep", cmd="grep needle haystack.txt",
                        unknowns=["whether the pattern matches the file at all"],
                        disc="pattern not present in file (exit code 1)",
                        ts="2026-04-20T10:00:00+00:00",
                    ),
                    _out(
                        "g1", exit_code=1,
                        ts="2026-04-20T10:00:05+00:00",
                        cmd="grep needle haystack.txt",
                    ),
                ],
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli._evolve_friction(telemetry_dir=tdir)
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertIn(
                "Friction events (exit_code ≠ 0 despite positive prediction): **0**",
                out,
            )
            self.assertIn("No friction detected yet", out)

    def test_grep_no_match_after_pipe_is_filtered(self):
        """Most real-world friction was on `cmd1 && cmd2 | grep foo` shapes;
        the terminal grep dictates the exit semantics."""
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            _write_jsonl(
                tdir / "2026-04-20-audit.jsonl",
                [
                    _pred(
                        "p1", op="status+grep",
                        cmd='git status --short && git log --oneline | grep "foo"',
                        unknowns=["whether the log mentions the foo token"],
                        disc="log does not contain the token (grep exit 1)",
                        ts="2026-04-20T10:00:00+00:00",
                    ),
                    _out(
                        "p1", exit_code=1,
                        ts="2026-04-20T10:00:05+00:00",
                        cmd='git status --short && git log --oneline | grep "foo"',
                    ),
                ],
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli._evolve_friction(telemetry_dir=tdir)
            self.assertEqual(rc, 0)
            self.assertIn(
                "Friction events (exit_code ≠ 0 despite positive prediction): **0**",
                buf.getvalue(),
            )

    def test_real_failure_exit_1_from_non_grep_stays_in_friction(self):
        """`cargo publish` returning 1 is a real auth/registry failure —
        the filter must NOT swallow it just because exit_code happens to be 1."""
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            _write_jsonl(
                tdir / "2026-04-20-audit.jsonl",
                [
                    _pred(
                        "r1", op="cargo publish", cmd="cargo publish --token X",
                        unknowns=["whether the registry token is valid for this crate"],
                        disc="cargo errors with 401 unauthorized or 403 forbidden",
                        ts="2026-04-20T10:00:00+00:00",
                    ),
                    _out(
                        "r1", exit_code=1,
                        ts="2026-04-20T10:00:05+00:00",
                        cmd="cargo publish --token X",
                    ),
                ],
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli._evolve_friction(telemetry_dir=tdir)
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertIn(
                "Friction events (exit_code ≠ 0 despite positive prediction): **1**",
                out,
            )
            self.assertIn("cargo publish", out)

    def test_grep_real_error_exit_2_stays_in_friction(self):
        """`grep --invalid-flag` exits 2 — that IS an operational failure
        and must be preserved (only literal exit==1 is treated as no-match)."""
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            _write_jsonl(
                tdir / "2026-04-20-audit.jsonl",
                [
                    _pred(
                        "e1", op="grep", cmd="grep --bogus-flag pattern file.txt",
                        unknowns=["whether the flag is recognized by this grep build"],
                        disc="grep rejects flag with usage error (exit 2)",
                        ts="2026-04-20T10:00:00+00:00",
                    ),
                    _out(
                        "e1", exit_code=2,
                        ts="2026-04-20T10:00:05+00:00",
                        cmd="grep --bogus-flag pattern file.txt",
                    ),
                ],
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli._evolve_friction(telemetry_dir=tdir)
            self.assertEqual(rc, 0)
            self.assertIn(
                "Friction events (exit_code ≠ 0 despite positive prediction): **1**",
                buf.getvalue(),
            )

    def test_absolute_path_grep_is_recognized(self):
        """`/usr/bin/grep` should resolve to `grep` after basename strip."""
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            _write_jsonl(
                tdir / "2026-04-20-audit.jsonl",
                [
                    _pred(
                        "a1", op="grep", cmd="/usr/bin/grep pat file.txt",
                        unknowns=["whether the absolute-path invocation is filtered too"],
                        disc="filter must recognize basename across path prefixes",
                        ts="2026-04-20T10:00:00+00:00",
                    ),
                    _out(
                        "a1", exit_code=1,
                        ts="2026-04-20T10:00:05+00:00",
                        cmd="/usr/bin/grep pat file.txt",
                    ),
                ],
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli._evolve_friction(telemetry_dir=tdir)
            self.assertEqual(rc, 0)
            self.assertIn(
                "Friction events (exit_code ≠ 0 despite positive prediction): **0**",
                buf.getvalue(),
            )

    def test_helper_function_unit_cases(self):
        """Direct unit tests on `_is_grep_like_no_match` to nail the contract:
        exit_code == 1 + grep-class terminal command → True; everything
        else → False (conservative: keeps records when in doubt)."""
        # Positive cases: exit=1 + grep-class terminal command.
        self.assertTrue(cli._is_grep_like_no_match("grep foo bar", 1))
        self.assertTrue(cli._is_grep_like_no_match("egrep -i foo bar", 1))
        self.assertTrue(cli._is_grep_like_no_match("rg foo", 1))
        self.assertTrue(cli._is_grep_like_no_match("diff a b", 1))
        self.assertTrue(cli._is_grep_like_no_match("find . -name x", 1))
        self.assertTrue(cli._is_grep_like_no_match("ls && grep foo bar.txt", 1))
        self.assertTrue(cli._is_grep_like_no_match("a | b | grep z", 1))
        self.assertTrue(cli._is_grep_like_no_match("/usr/local/bin/rg foo", 1))
        # Negative cases: wrong exit code.
        self.assertFalse(cli._is_grep_like_no_match("grep foo bar", 0))
        self.assertFalse(cli._is_grep_like_no_match("grep foo bar", 2))
        self.assertFalse(cli._is_grep_like_no_match("grep foo bar", 130))
        # Negative cases: wrong terminal command.
        self.assertFalse(cli._is_grep_like_no_match("git push", 1))
        self.assertFalse(cli._is_grep_like_no_match("npm publish", 1))
        self.assertFalse(cli._is_grep_like_no_match("cargo publish --token X", 1))
        # Negative cases: empty / parse-ambiguous.
        self.assertFalse(cli._is_grep_like_no_match("", 1))
        self.assertFalse(cli._is_grep_like_no_match("   ", 1))


if __name__ == "__main__":
    unittest.main()
