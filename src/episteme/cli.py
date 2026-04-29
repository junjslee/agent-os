from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()


def _detect_python_prefix() -> Path:
    """Resolve the Python prefix the CLI should report and check against.

    Precedence: explicit override env → legacy conda env vars → running interpreter's prefix.
    No hardcoded default path — works for conda, venv, pyenv, system Python, or anything else.
    """
    for var in ("EPISTEME_PYTHON_PREFIX", "EPISTEME_CONDA_ROOT", "COGNITIVE_OS_CONDA_ROOT"):
        val = os.environ.get(var)
        if val:
            return Path(val)
    return Path(sys.prefix)


def _detect_runtime_kind(prefix: Path) -> str:
    """Classify a Python prefix as conda / venv / system for reporting purposes."""
    if (prefix / "conda-meta").is_dir():
        return "conda"
    if (prefix / "pyvenv.cfg").exists():
        return "venv"
    return "system"


PYTHON_PREFIX = _detect_python_prefix()
RUNTIME_KIND = _detect_runtime_kind(PYTHON_PREFIX)
REQUIRE_CONDA = os.environ.get("EPISTEME_REQUIRE_CONDA", "").lower() in {"1", "true", "yes"}

# Backward-compat aliases — older code paths still reference CONDA_ROOT.
CONDA_ROOT = PYTHON_PREFIX
EXPECTED_BASE_PREFIX = str(PYTHON_PREFIX)
RUNTIME_MANIFEST = json.loads((REPO_ROOT / "core" / "runtime_manifest.json").read_text(encoding="utf-8"))
HARNESSES_DIR = REPO_ROOT / "core" / "harnesses"
GLOBAL_MEMORY_DIR = REPO_ROOT / "core" / "memory" / "global"
GENERATED_PROFILE_DIR = GLOBAL_MEMORY_DIR / ".generated"
EVOLUTION_EPISODES_DIR = REPO_ROOT / "core" / "memory" / "evolution" / "episodes"
MEMORY_RECORDS_DIR = REPO_ROOT / "core" / "memory" / "records"
ALLOWED_EVOLUTION_MUTATIONS = {
    "prompt_policy_tweak",
    "retrieval_policy_tweak",
    "planning_depth_tweak",
    "tool_selection_rule_tweak",
    "handoff_format_tweak",
}


# ---------------------------------------------------------------------------
# Shell / process helpers
# ---------------------------------------------------------------------------

def _run(
    args: list[str],
    *,
    check: bool = True,
    capture_output: bool = True,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=check,
        text=True,
        capture_output=capture_output,
        cwd=str(cwd) if cwd else None,
    )


def _command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def _write_text(path: Path, content: str, *, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing == content:
            if executable:
                path.chmod(path.stat().st_mode | 0o111)
            return
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | 0o111)


# ---------------------------------------------------------------------------
# Managed-region contract
# ---------------------------------------------------------------------------
# episteme sync overwrites the block *between* the begin/end markers.
# Anything outside the markers is user-owned and preserved verbatim across
# syncs. Markers use HTML comment syntax so they render invisibly in Markdown.
#
# First-run migration: when a file exists but has no markers, the managed
# block is inserted at the top and the pre-existing content is kept verbatim
# below — so hand-edits are never silently destroyed.

MANAGED_MARKER = "cog-os:managed"


def _managed_markers(marker: str = MANAGED_MARKER) -> tuple[str, str]:
    return f"<!-- {marker}:begin -->", f"<!-- {marker}:end -->"


def _render_managed_block(content: str, marker: str = MANAGED_MARKER) -> str:
    begin, end = _managed_markers(marker)
    body = content.rstrip() + "\n"
    return f"{begin}\n{body}{end}\n"


def _compose_managed_file(
    existing: str | None,
    managed_content: str,
    marker: str = MANAGED_MARKER,
    *,
    prior_signature: str | None = None,
) -> str:
    """Return the full file contents that should be on disk.

    - If existing is None (file absent): just the managed block.
    - If existing already has markers: replace between them, preserve outside.
    - If existing has no markers AND starts with prior_signature: pure overwrite
      (the file is recognized as episteme-authored from before markers were
      introduced, so no hand-edits are at risk).
    - If existing has no markers and signature does not match: prepend managed
      block, preserve existing content below verbatim.
    """
    begin, end = _managed_markers(marker)
    managed_block = _render_managed_block(managed_content, marker)

    if existing is None:
        return managed_block

    if begin in existing and end in existing:
        pre, _, rest = existing.partition(begin)
        _, _, post = rest.partition(end)
        post = post.lstrip("\n")
        out = pre + managed_block + (post if post else "")
        if not out.endswith("\n"):
            out += "\n"
        return out

    # No markers yet. If the existing file matches a known episteme
    # signature, assume it was generated by an older sync and do a clean
    # replace (no duplication).
    if prior_signature and existing.lstrip().startswith(prior_signature):
        return managed_block

    # First-run migration with unknown content: preserve everything below the
    # managed block so hand-edits are never silently destroyed.
    trailing = existing.lstrip("\n")
    if not trailing:
        return managed_block
    return managed_block + "\n" + trailing


def _write_managed_file(
    path: Path,
    managed_content: str,
    *,
    marker: str = MANAGED_MARKER,
    prior_signature: str | None = None,
) -> None:
    """Write managed_content between begin/end markers in path.

    Content outside the markers is preserved across syncs. See the module
    docstring for the full contract. prior_signature lets callers opt into
    clean replacement of files authored by earlier, pre-marker syncs.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else None
    new_content = _compose_managed_file(
        existing, managed_content, marker, prior_signature=prior_signature
    )
    if existing is not None and existing == new_content:
        return
    path.write_text(new_content, encoding="utf-8")


def _extract_managed_block(existing: str, marker: str = MANAGED_MARKER) -> str | None:
    """Return the content currently inside the managed markers, or None if absent."""
    begin, end = _managed_markers(marker)
    if begin not in existing or end not in existing:
        return None
    _, _, rest = existing.partition(begin)
    inner, _, _ = rest.partition(end)
    return inner.strip("\n")


def _load_generated_scores(project_root: Path) -> tuple[dict[str, int] | None, dict[str, int] | None]:
    generated_dir = project_root / "core" / "memory" / "global" / ".generated"
    workstyle_path = generated_dir / "workstyle_scores.json"
    cognitive_path = generated_dir / "cognitive_profile.json"

    workstyle_scores = None
    cognitive_scores = None

    if workstyle_path.exists():
        try:
            workstyle_payload = json.loads(workstyle_path.read_text(encoding="utf-8"))
            raw = workstyle_payload.get("scores", {}) if isinstance(workstyle_payload, dict) else {}
            if isinstance(raw, dict):
                workstyle_scores = {k: int(v) for k, v in raw.items() if k in PROFILE_DIMENSIONS}
        except (json.JSONDecodeError, TypeError, ValueError):
            workstyle_scores = None

    if cognitive_path.exists():
        try:
            cognitive_payload = json.loads(cognitive_path.read_text(encoding="utf-8"))
            raw = cognitive_payload.get("scores", {}) if isinstance(cognitive_payload, dict) else {}
            if isinstance(raw, dict):
                cognitive_scores = {k: int(v) for k, v in raw.items() if k in COGNITIVE_DIMENSIONS}
        except (json.JSONDecodeError, TypeError, ValueError):
            cognitive_scores = None

    return workstyle_scores, cognitive_scores


def _render_identity_summary(workstyle_scores: dict, cognitive_scores: dict) -> str:
    """Produce a human-readable 2-3 paragraph summary of the operator's identity."""
    planning = workstyle_scores.get("planning_strictness", 0)
    risk = workstyle_scores.get("risk_tolerance", 0)
    testing = workstyle_scores.get("testing_rigor", 0)
    parallel = workstyle_scores.get("parallelism_preference", 0)
    docs = workstyle_scores.get("documentation_rigor", 0)
    automation = workstyle_scores.get("automation_level", 0)

    fpd = cognitive_scores.get("first_principles_depth", 0)
    exp = cognitive_scores.get("exploration_breadth", 0)
    svr = cognitive_scores.get("speed_vs_rigor_balance", 0)
    cho = cognitive_scores.get("challenge_orientation", 0)
    unt = cognitive_scores.get("uncertainty_tolerance", 0)
    aut = cognitive_scores.get("autonomy_preference", 0)

    # --- Workstyle paragraph ---
    if planning >= 2:
        plan_desc = "plans deliberately before touching code, preferring staged execution over emergent design"
    else:
        plan_desc = "moves quickly into implementation, letting structure emerge from the work itself"

    if risk >= 2:
        risk_desc = "with a conservative posture toward irreversible actions, requiring explicit gates before proceeding"
    else:
        risk_desc = "with a bias for speed and reversible progress over heavy approval overhead"

    if docs >= 2:
        docs_desc = "treats project documentation as an operating contract — decisions, trade-offs, and unknowns must be written down"
    else:
        docs_desc = "keeps docs lightweight, preferring code and commits as the primary record"

    if automation >= 2:
        auto_desc = "relies on strong deterministic automation for quality gates"
    else:
        auto_desc = "favors manual review over automated enforcement"

    para1 = (
        f"As an operator, this person {plan_desc}, {risk_desc}. "
        f"They {docs_desc}, and {auto_desc}. "
        f"Testing rigor sits at {'high' if testing >= 2 else 'moderate' if testing == 1 else 'low'} threshold "
        f"({'blocking on failures' if testing >= 3 else 'targeted tests for touched areas' if testing >= 1 else 'lightweight checks only'}), "
        f"and parallelism is {'actively structured via multi-lane execution' if parallel >= 2 else 'mostly sequential with occasional parallel tasks'}."
    )

    # --- Cognitive paragraph ---
    if fpd >= 2:
        fpd_desc = "thinks from the ground up — they decompose assumptions before accepting a framing"
    else:
        fpd_desc = "tends to reason from heuristics and pattern recognition rather than first principles"

    if exp >= 2:
        exp_desc = "systematically explores the option space before committing"
    else:
        exp_desc = "trusts strong intuitions and commits quickly once a path feels right"

    if cho >= 2:
        cho_desc = "actively courts adversarial critique of their own plans"
    else:
        cho_desc = "values momentum over devil's advocate pressure"

    if unt >= 2:
        unt_desc = "holds high epistemic standards — unknowns and assumptions must be named, not swept aside"
    else:
        unt_desc = "tolerates ambiguity and prefers to learn by doing rather than over-specifying upfront"

    para2 = (
        f"Cognitively, this operator {fpd_desc}. They {exp_desc} and {cho_desc}. "
        f"When facing uncertainty, they {unt_desc}. "
        f"Their speed-vs-rigor balance skews {'toward rigor' if svr >= 2 else 'toward speed'}, "
        f"and they prefer agents to operate with "
        f"{'high autonomy within strict boundaries' if aut >= 2 else 'frequent human checkpoints and confirmation loops'}."
    )

    # --- Contract paragraph ---
    if planning >= 2 and unt >= 2:
        contract_para = (
            "The resulting operating contract is one of structured deliberation: "
            "staged plans, explicit assumption surfaces, and review gates before irreversible moves. "
            "Agents should narrate their reasoning, not just their actions."
        )
    elif planning <= 1 and risk <= 1:
        contract_para = (
            "The resulting operating contract is one of adaptive momentum: "
            "bias for reversible progress, lightweight checkpoints, and fast feedback loops. "
            "Agents should prefer doing over deliberating, but checkpoint at natural seams."
        )
    else:
        contract_para = (
            "The resulting operating contract blends discipline with pragmatism: "
            "plans are staged but not over-specified, risks are flagged but not paralyzed by, "
            "and agents are trusted within their bounded scope while key decisions are surfaced for review."
        )

    return "\n\n".join([para1, para2, contract_para])


def _write_personalization_blueprint(project_root: Path) -> None:
    workstyle_scores, cognitive_scores = _load_generated_scores(project_root)
    if not workstyle_scores or not cognitive_scores:
        return

    planning = workstyle_scores.get("planning_strictness", 0)
    risk = workstyle_scores.get("risk_tolerance", 0)
    testing = workstyle_scores.get("testing_rigor", 0)
    parallel = workstyle_scores.get("parallelism_preference", 0)
    docs = workstyle_scores.get("documentation_rigor", 0)
    automation = workstyle_scores.get("automation_level", 0)

    fpd = cognitive_scores.get("first_principles_depth", 0)
    exp = cognitive_scores.get("exploration_breadth", 0)
    svr = cognitive_scores.get("speed_vs_rigor_balance", 0)
    cho = cognitive_scores.get("challenge_orientation", 0)
    unt = cognitive_scores.get("uncertainty_tolerance", 0)
    aut = cognitive_scores.get("autonomy_preference", 0)

    operator_type = (
        "Systems Architect" if planning >= 2 and docs >= 2 and automation >= 2 else
        "Rapid Builder" if planning <= 1 and risk <= 1 and testing <= 1 else
        "Balanced Operator"
    )

    cognitive_type = (
        "First-Principles Strategist" if fpd >= 2 and cho >= 2 else
        "Pragmatic Executor" if svr <= 1 and exp <= 1 else
        "Adaptive Analyst"
    )

    contract = (
        "Operate with staged plans, explicit assumptions, and review gates before irreversible changes."
        if planning >= 2 and unt >= 2 else
        "Bias for reversible progress with lightweight checks and explicit checkpointing."
    )

    identity_summary = _render_identity_summary(workstyle_scores, cognitive_scores)

    lines = [
        "# Personalization Blueprint",
        "",
        f"Generated on `{_today()}` from deterministic setup artifacts.",
        "This document captures your stable operating identity: how you execute and how you think.",
        "",
        "## 🪪 Operator Identity Summary",
        "",
        identity_summary,
        "",
        "## 🧭 Execution Profile (Workstyle)",
        f"- Type: {operator_type}",
        f"- planning_strictness: {planning}",
        f"- risk_tolerance: {risk}",
        f"- testing_rigor: {testing}",
        f"- parallelism_preference: {parallel}",
        f"- documentation_rigor: {docs}",
        f"- automation_level: {automation}",
        "",
        "## 🧠 Thinking Profile (Cognition)",
        f"- Type: {cognitive_type}",
        f"- first_principles_depth: {fpd}",
        f"- exploration_breadth: {exp}",
        f"- speed_vs_rigor_balance: {svr}",
        f"- challenge_orientation: {cho}",
        f"- uncertainty_tolerance: {unt}",
        f"- autonomy_preference: {aut}",
        "",
        "## 🔒 Operating Contract",
        f"- {contract}",
        "- Keep project truth in `docs/*` and narrate major choices in `docs/DECISION_STORY.md`.",
        "- Preserve your global build narrative in `core/memory/global/build_story.md`.",
        "",
        "## What / Why / How",
        "- What: Build a stable multi-agent operating contract adapted to your profile.",
        "- Why: Reduce cross-tool drift while preserving your decision style.",
        "- How: deterministic profile + cognition scorecards -> compiled policies -> synced adapters.",
        "",
    ]

    out_path = project_root / "core" / "memory" / "global" / ".generated" / "personalization_blueprint.md"
    _write_text(out_path, "\n".join(lines))
    print(f"✅ Wrote generated artifact:\n  - {out_path}")


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_tree(src: Path, dst: Path) -> None:
    for file_path in src.rglob("*"):
        if file_path.is_dir():
            continue
        rel = file_path.relative_to(src)
        _copy_file(file_path, dst / rel)


def _replace_tokens(content: str, mapping: dict[str, str]) -> str:
    rendered = content
    for key, value in mapping.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def _today() -> str:
    return date.today().isoformat()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_slug(raw: str) -> str:
    out = re.sub(r"[^a-z0-9._-]+", "-", raw.strip().lower())
    out = out.strip("-")
    return out or "episode"


def _episode_path(episode_id: str) -> Path:
    return EVOLUTION_EPISODES_DIR / f"{_safe_slug(episode_id)}.json"


def _write_episode(payload: dict) -> Path:
    episode_id = str(payload.get("episode_id", "")).strip()
    if not episode_id:
        raise ValueError("episode payload missing episode_id")
    target = _episode_path(episode_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return target


def _load_episode(episode_id: str) -> dict:
    target = _episode_path(episode_id)
    if not target.exists():
        raise FileNotFoundError(f"episode not found: {episode_id} ({target})")
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"episode file is not valid JSON: {target}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"episode payload must be an object: {target}")
    return payload


def _default_evaluation_report(seed: int, suite_ref: str) -> dict:
    return {
        "suite_ref": suite_ref,
        "seed": seed,
        "metrics": {
            "task_success_rate": 0.0,
            "safety_violation_count": 0,
            "latency_ms_p50": 0,
            "token_cost": 0,
            "style_fit_score": 0.0,
        },
        "safety_regression": False,
        "notes": "stub evaluation report (replace with real replay harness output)",
    }


def _evolve_run(
    *,
    hypothesis: str,
    mutation_type: str,
    target: str,
    expected_effect: str,
    diff_text: str,
    risk_level: str,
    suite_ref: str,
    seed: int,
    captured_by: str,
) -> int:
    if mutation_type not in ALLOWED_EVOLUTION_MUTATIONS:
        print(f"unsupported mutation type: {mutation_type}", file=sys.stderr)
        return 1
    if risk_level not in {"low", "medium", "high"}:
        print(f"unsupported risk level: {risk_level}", file=sys.stderr)
        return 1

    ts = datetime.now(timezone.utc)
    # 4-char uuid suffix avoids same-second collisions under fast loops
    # or mocked-time in tests. Prefix ep-YYYYMMDD-HHMMSS still sorts
    # lexicographically in wall-clock order for any reasonable reader.
    episode_id = f"ep-{ts.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"
    before = _default_evaluation_report(seed=seed, suite_ref=suite_ref)
    after = _default_evaluation_report(seed=seed, suite_ref=suite_ref)

    payload = {
        "episode_id": episode_id,
        "hypothesis": hypothesis,
        "mutation": {
            "type": mutation_type,
            "target": target,
            "diff": diff_text,
            "expected_effect": expected_effect,
            "risk_level": risk_level,
        },
        "suite_ref": suite_ref,
        "metrics_before": before["metrics"],
        "metrics_after": after["metrics"],
        "gate_result": {
            "passed": False,
            "reasons": ["evaluation not run yet"],
        },
        "decision": "candidate",
        "provenance": {
            "captured_at": _now_iso(),
            "captured_by": captured_by,
            "confidence": "medium",
            "evidence_refs": [],
        },
        "version": "evolution-contract-v1",
        "evaluation_report_before": before,
        "evaluation_report_after": after,
    }

    out = _write_episode(payload)
    print("Created evolution episode:")
    print(f"  - id: {episode_id}")
    print(f"  - file: {out}")
    print("Next steps:")
    print(f"  1) episteme evolve report {episode_id}")
    print(f"  2) episteme evolve promote {episode_id}")
    return 0


def _evolve_report(episode_id: str) -> int:
    try:
        ep = _load_episode(episode_id)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Evolution episode: {ep.get('episode_id', 'unknown')}")
    print(f"Decision: {ep.get('decision', 'unknown')}")
    mutation = ep.get("mutation", {}) if isinstance(ep.get("mutation"), dict) else {}
    print(f"Mutation: {mutation.get('type', 'unknown')} -> {mutation.get('target', 'unknown')}")
    print(f"Hypothesis: {ep.get('hypothesis', '')}")
    gate = ep.get("gate_result", {}) if isinstance(ep.get("gate_result"), dict) else {}
    print(f"Gate passed: {gate.get('passed', False)}")
    reasons = gate.get("reasons", []) if isinstance(gate.get("reasons"), list) else []
    if reasons:
        print("Gate reasons:")
        for reason in reasons:
            print(f"  - {reason}")
    return 0


def _evolve_promote(episode_id: str, *, force: bool = False) -> int:
    try:
        ep = _load_episode(episode_id)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    gate = ep.get("gate_result", {}) if isinstance(ep.get("gate_result"), dict) else {}
    if not force and not bool(gate.get("passed", False)):
        print("cannot promote: gate_result.passed is false (use --force to override)", file=sys.stderr)
        return 1

    ep["decision"] = "promoted"
    provenance = ep.get("provenance", {}) if isinstance(ep.get("provenance"), dict) else {}
    provenance["captured_at"] = _now_iso()
    ep["provenance"] = provenance
    path = _write_episode(ep)
    print(f"Promoted episode: {episode_id}")
    print(f"  - {path}")
    return 0


def _telemetry_dir() -> Path:
    return Path.home() / ".episteme" / "telemetry"


def _load_telemetry_pairs(
    telemetry_dir: Path,
) -> tuple[dict[str, dict], dict[str, dict]]:
    """Return (predictions_by_cid, outcomes_by_cid) across all day-scoped JSONL files.

    Malformed lines are skipped silently; the scanner is best-effort because
    telemetry is produced by never-blocking hooks that may truncate on
    crash.
    """
    predictions: dict[str, dict] = {}
    outcomes: dict[str, dict] = {}
    if not telemetry_dir.exists() or not telemetry_dir.is_dir():
        return predictions, outcomes
    for path in sorted(telemetry_dir.glob("*-audit.jsonl")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(rec, dict):
                        continue
                    cid = rec.get("correlation_id")
                    event = rec.get("event")
                    if not isinstance(cid, str) or not cid:
                        continue
                    if event == "prediction":
                        predictions[cid] = rec
                    elif event == "outcome":
                        outcomes[cid] = rec
        except OSError:
            continue
    return predictions, outcomes


def _render_friction_report(
    predictions: dict[str, dict],
    outcomes: dict[str, dict],
    top_n: int,
) -> str:
    """Render a Markdown Friction Report from paired telemetry.

    Heuristic:
        1. A "friction event" is any (prediction, outcome) pair where the
           observed `exit_code` is non-zero. The prediction implies the
           agent expected success — an LLM does not run a command it thinks
           will fail.
        2. Rank unknowns by frequency across friction events. The ones
           named most often in failing runs are the unknowns the operator
           is chronically under-elaborating at surface-time.
        3. Also surface the most-recurring failing `op` label (git push,
           terraform apply, …) so the operator sees *where* predictions
           diverge from reality.

    Non-positive-prediction filtering: if the prediction envelope is empty
    (no unknowns, no disconfirmation) we skip it — the agent declined to
    commit to a prediction, so the failure is not a calibration signal.
    """
    # Defensive clamp: argparse accepts negative ints without a min-value
    # check, and Python list slicing with a negative stop silently slices
    # from the tail. Treat any non-positive top_n as "no top-N section."
    top_n = max(0, top_n)
    friction: list[tuple[str, dict, dict]] = []
    for cid, pred in predictions.items():
        out = outcomes.get(cid)
        if not out:
            continue
        exit_code = out.get("exit_code")
        if not isinstance(exit_code, int) or exit_code == 0:
            continue
        pred_env = pred.get("epistemic_prediction") or {}
        unknowns = pred_env.get("unknowns") or []
        disc = (pred_env.get("disconfirmation") or "").strip()
        if not unknowns and not disc:
            continue  # agent didn't actually predict; skip
        friction.append((cid, pred, out))

    total_pairs = len(
        [cid for cid in predictions if cid in outcomes]
    )

    lines: list[str] = []
    lines.append("# Episteme Friction Report")
    lines.append("")
    lines.append(f"_Generated: {_now_iso()}_")
    lines.append("")
    lines.append(
        f"Paired predictions / outcomes: **{total_pairs}**  ·  "
        f"Friction events (exit_code ≠ 0 despite positive prediction): **{len(friction)}**"
    )
    lines.append("")

    if not friction:
        lines.append(
            "_No friction detected yet. Either the operator's predictions "
            "are well-calibrated, or telemetry has not accumulated enough "
            "paired records for an honest read._"
        )
        lines.append("")
        return "\n".join(lines)

    # Rank violated unknowns by frequency.
    unknowns_count: dict[str, int] = {}
    ops_count: dict[str, int] = {}
    no_disc_count = 0
    for _cid, pred, out in friction:
        env = pred.get("epistemic_prediction") or {}
        for u in env.get("unknowns") or []:
            key = str(u).strip()
            if not key:
                continue
            unknowns_count[key] = unknowns_count.get(key, 0) + 1
        op_label = str(pred.get("op") or "").strip()
        if op_label:
            ops_count[op_label] = ops_count.get(op_label, 0) + 1
        if not (env.get("disconfirmation") or "").strip():
            no_disc_count += 1

    ranked_unknowns = sorted(unknowns_count.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n]
    ranked_ops = sorted(ops_count.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n]

    lines.append("## Most-violated unknowns")
    lines.append("")
    lines.append("Unknowns named at prediction time that subsequently appeared in a failing run.")
    lines.append("High frequency = the operator is chronically under-elaborating this dimension.")
    lines.append("")
    if ranked_unknowns:
        for idx, (text, n) in enumerate(ranked_unknowns, start=1):
            preview = text if len(text) <= 140 else text[:137] + "..."
            lines.append(f"{idx}. **×{n}**  {preview}")
    else:
        lines.append("_(no unknowns recorded in failing runs)_")
    lines.append("")

    lines.append("## Operations with most friction")
    lines.append("")
    if ranked_ops:
        for idx, (op, n) in enumerate(ranked_ops, start=1):
            lines.append(f"{idx}. `{op}` — {n} failing run(s)")
    else:
        lines.append("_(no op labels recorded)_")
    lines.append("")

    lines.append("## Recent friction events")
    lines.append("")
    recent = sorted(
        friction,
        key=lambda triple: str(triple[2].get("ts") or ""),
        reverse=True,
    )[:5]
    for cid, pred, out in recent:
        cmd = str(pred.get("command_executed") or out.get("command_executed") or "")
        cmd_short = cmd if len(cmd) <= 120 else cmd[:117] + "..."
        ts = str(out.get("ts") or pred.get("ts") or "")
        exit_code = out.get("exit_code")
        env = pred.get("epistemic_prediction") or {}
        disc = (env.get("disconfirmation") or "").strip()
        lines.append(f"- `{ts}`  exit={exit_code}  cid=`{cid[:12]}`")
        lines.append(f"  - cmd: `{cmd_short}`")
        if disc:
            disc_short = disc if len(disc) <= 200 else disc[:197] + "..."
            lines.append(f"  - declared disconfirmation: _{disc_short}_")
    lines.append("")

    if no_disc_count:
        lines.append(
            f"> **{no_disc_count}** failing run(s) were declared with an empty "
            "disconfirmation — the agent predicted success without naming what "
            "would prove it wrong. Treat these as calibration debt."
        )
        lines.append("")

    lines.append("## Next")
    lines.append("")
    lines.append(
        "This report is the seed for automated `CONSTITUTION.md` refinement. "
        "For now: read the top-N unknowns above and consider whether they "
        "deserve to be promoted to mandatory Reasoning-Surface fields, or "
        "whether the disconfirmation threshold should be raised. See "
        "`docs/NEXT_STEPS.md` for the evolve-loop roadmap."
    )
    lines.append("")
    return "\n".join(lines)


def _evolve_friction(
    *,
    telemetry_dir: Path | None = None,
    output_path: Path | None = None,
    top_n: int = 5,
) -> int:
    """Scan telemetry and emit a Markdown Friction Report.

    Deterministic, no ML. Pairs prediction↔outcome JSONL records by
    `correlation_id`, flags exit_code ≠ 0 against positive predictions,
    ranks violated unknowns and friction-prone ops.
    """
    src = telemetry_dir or _telemetry_dir()
    predictions, outcomes = _load_telemetry_pairs(src)
    report = _render_friction_report(predictions, outcomes, top_n=top_n)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"Wrote friction report: {output_path}")
    else:
        print(report)
    return 0


def _evolve_rollback(episode_id: str, *, rollback_ref: str) -> int:
    try:
        ep = _load_episode(episode_id)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    ep["decision"] = "rolled_back"
    ep["rollback_ref"] = rollback_ref
    provenance = ep.get("provenance", {}) if isinstance(ep.get("provenance"), dict) else {}
    provenance["captured_at"] = _now_iso()
    ep["provenance"] = provenance
    path = _write_episode(ep)
    print(f"Rolled back episode: {episode_id}")
    print(f"  - rollback_ref: {rollback_ref}")
    print(f"  - {path}")
    return 0


def _event_type_from_payload(raw_type: str, event: dict) -> str:
    t = str(raw_type or "").strip().lower()
    if t in {"decision"}:
        return "decision"
    if t in {"error", "exception", "failure"}:
        return "error"
    if t in {"verification", "assertion", "check"}:
        return "verification"
    if t in {"handoff"}:
        return "handoff"
    if t in {"tool_call", "tool_result", "action", "execute", "command", "bash"}:
        return "action"

    payload = json.dumps(event, ensure_ascii=False).lower()
    if "error" in payload or "exception" in payload or "failed" in payload:
        return "error"
    return "observation"


def _load_bridge_events(input_path: Path) -> tuple[str | None, list[dict], dict]:
    try:
        raw = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FileNotFoundError(f"bridge input not found: {input_path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"bridge input is not valid JSON: {input_path}") from exc

    if isinstance(raw, list):
        return None, raw, {"root_type": "list"}

    if not isinstance(raw, dict):
        raise ValueError("bridge input must be a JSON object or array")

    events = raw.get("events")
    if not isinstance(events, list):
        raise ValueError("bridge input object must contain an array field `events`")

    return str(raw.get("session_id") or "").strip() or None, events, raw


def _bridge_record_from_event(
    *,
    session_id: str,
    project_id: str | None,
    idx: int,
    event: dict,
    source_ref: str,
    captured_by: str,
    confidence: str,
) -> dict:
    event_type = _event_type_from_payload(str(event.get("type", "")), event)
    summary = str(event.get("summary") or event.get("message") or event.get("type") or f"event-{idx}").strip()
    if not summary:
        summary = f"event-{idx}"

    record = {
        "id": str(uuid.uuid4()),
        "memory_class": "episodic",
        "summary": summary[:500],
        "details": {
            "event_index": idx,
            "event": event,
        },
        "provenance": {
            "source_type": "imported",
            "source_ref": source_ref,
            "captured_at": _now_iso(),
            "captured_by": captured_by,
            "confidence": confidence,
            "evidence_refs": [source_ref],
        },
        "status": "active",
        "version": "memory-contract-v1",
        "session_id": session_id,
        "event_type": event_type,
        "tags": ["bridge", "anthropic-managed"],
    }
    if project_id:
        record["related_project_id"] = project_id
    return record


def _bridge_anthropic_managed(
    *,
    input_path: Path,
    output_path: Path | None,
    session_id: str | None,
    project_id: str | None,
    source_ref: str | None,
    captured_by: str,
    confidence: str,
    dry_run: bool,
) -> int:
    if confidence not in {"low", "medium", "high"}:
        print(f"invalid confidence: {confidence} (expected low|medium|high)", file=sys.stderr)
        return 1

    try:
        detected_session_id, events, _ = _load_bridge_events(input_path)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    sid = (session_id or detected_session_id or input_path.stem).strip()
    if not sid:
        sid = f"managed-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    src_ref = source_ref or str(input_path)

    records: list[dict] = []
    for idx, raw_event in enumerate(events):
        if not isinstance(raw_event, dict):
            raw_event = {"value": raw_event, "type": "other"}
        records.append(
            _bridge_record_from_event(
                session_id=sid,
                project_id=project_id,
                idx=idx,
                event=raw_event,
                source_ref=src_ref,
                captured_by=captured_by,
                confidence=confidence,
            )
        )

    envelope = {
        "contract_version": "memory-contract-v1",
        "records": records,
    }

    if output_path is None:
        output_path = REPO_ROOT / "core" / "memory" / "bridges" / "anthropic-managed" / f"{_safe_slug(sid)}.memory-envelope.json"

    if dry_run:
        print("Bridge dry run complete.")
        print(f"  - input: {input_path}")
        print(f"  - session_id: {sid}")
        print(f"  - records: {len(records)}")
        print(f"  - would_write: {output_path}")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")

    print("Bridge import complete.")
    print(f"  - input: {input_path}")
    print(f"  - output: {output_path}")
    print(f"  - session_id: {sid}")
    print(f"  - records: {len(records)}")
    return 0


# ---------------------------------------------------------------------------
# Substrate bridge dispatch
# ---------------------------------------------------------------------------


def _build_scope_from_args(args: argparse.Namespace):
    from episteme.bridges.substrate import ScopeMap
    return ScopeMap(
        user_id=getattr(args, "user_id", None),
        project_id=getattr(args, "project_id", None),
        agent_id=getattr(args, "agent_id", None),
        session_id=getattr(args, "session_id", None),
        run_id=getattr(args, "run_id", None),
        app_id=getattr(args, "app_id", None),
        org_id=getattr(args, "org_id", None),
    )


def _load_adapter_config(path_str: str | None) -> dict:
    if not path_str:
        return {}
    path = Path(path_str).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"adapter config not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _bridge_substrate_dispatch(args: argparse.Namespace) -> int:
    from episteme.bridges.substrate import list_adapters, load_adapter
    from episteme.bridges.substrate.base import PullQuery

    action = args.substrate_action

    if action == "list-adapters":
        for name in list_adapters():
            print(name)
        return 0

    if action == "describe":
        adapter = load_adapter(args.adapter)
        print(json.dumps(adapter.describe().as_dict(), indent=2))
        return 0

    if action == "verify":
        adapter = load_adapter(args.adapter)
        desc = adapter.describe().as_dict()
        required = {"name", "version", "contract_version", "capabilities", "scope_keys"}
        missing = sorted(required - desc.keys())
        if missing:
            print(f"verify FAIL: missing fields {missing}", file=sys.stderr)
            return 1
        if desc["contract_version"] != "substrate-v1":
            print(f"verify FAIL: contract_version {desc['contract_version']!r} != 'substrate-v1'", file=sys.stderr)
            return 1
        if "push" not in desc["capabilities"]:
            print("verify FAIL: capabilities.push missing", file=sys.stderr)
            return 1
        print(f"verify OK: {desc['name']} v{desc['version']} ({desc.get('substrate', {}).get('transport', '?')})")
        return 0

    if action == "push":
        try:
            config = _load_adapter_config(args.config)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"config error: {exc}", file=sys.stderr)
            return 1
        adapter = load_adapter(args.adapter, config)
        input_path = Path(args.input).expanduser()
        if not input_path.exists():
            print(f"input envelope not found: {input_path}", file=sys.stderr)
            return 1
        envelope = json.loads(input_path.read_text(encoding="utf-8"))
        result = adapter.push(envelope, _build_scope_from_args(args))
        payload = json.dumps(result.as_dict(), indent=2) + "\n"
        if args.output:
            out = Path(args.output).expanduser()
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(payload, encoding="utf-8")
            print(f"pushed {len(result.pushed)} / skipped {len(result.skipped)} / failed {len(result.failed)} -> {out}")
        else:
            print(payload, end="")
        return 0 if not result.failed else 1

    if action == "pull":
        try:
            config = _load_adapter_config(args.config)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"config error: {exc}", file=sys.stderr)
            return 1
        adapter = load_adapter(args.adapter, config)
        query = PullQuery(
            query=args.query,
            scope=_build_scope_from_args(args),
            limit=args.limit,
            since=args.since,
        )
        envelope = adapter.pull(query)
        payload = json.dumps(envelope, indent=2) + "\n"
        if args.output:
            out = Path(args.output).expanduser()
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(payload, encoding="utf-8")
            print(f"pulled {len(envelope.get('records', []))} records -> {out}")
        else:
            print(payload, end="")
        return 0

    print(f"unknown substrate action: {action}", file=sys.stderr)
    return 2


# ---------------------------------------------------------------------------
# Machine context — cross-platform (macOS + Linux)
# ---------------------------------------------------------------------------

def _sysctl(name: str) -> str:
    try:
        return _run(["sysctl", "-n", name]).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sw_vers(flag: str) -> str:
    try:
        return _run(["sw_vers", flag]).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _linux_mem_gb() -> str:
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return str(kb // 1024 // 1024)
    except (OSError, ValueError, IndexError):
        pass
    return "unknown"


def _linux_cpu() -> str:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except (OSError, IndexError):
        pass
    try:
        out = _run(["lscpu"]).stdout
        for line in out.splitlines():
            if "model name" in line.lower():
                return line.split(":", 1)[1].strip()
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        pass
    return "unknown"


def _linux_os_version() -> str:
    try:
        with open("/etc/os-release", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except (OSError, IndexError):
        pass
    try:
        return _run(["uname", "-sr"]).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _tool_version(cmd: list[str], *, first_line: bool = False) -> str:
    try:
        output = _run(cmd).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "not installed"
    if first_line:
        return output.splitlines()[0] if output else "unknown"
    return output or "unknown"


def _machine_context() -> dict[str, str]:
    is_macos = platform.system() == "Darwin"
    if is_macos:
        mem_bytes = _sysctl("hw.memsize")
        mem_gb = str(int(mem_bytes) // 1024 // 1024 // 1024) if mem_bytes.isdigit() else "unknown"
        cpu = _sysctl("machdep.cpu.brand_string")
        os_version = _sw_vers("-productVersion")
        os_build = _sw_vers("-buildVersion")
    else:
        mem_gb = _linux_mem_gb()
        cpu = _linux_cpu()
        os_version = _linux_os_version()
        try:
            os_build = _run(["uname", "-r"]).stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            os_build = "unknown"
    return {
        "DATE": _today(),
        "HOME_PATH": str(HOME),
        "CONDA_ROOT": str(PYTHON_PREFIX),
        "PYTHON_PREFIX": str(PYTHON_PREFIX),
        "RUNTIME_KIND": RUNTIME_KIND,
        "OS_VERSION": os_version,
        "OS_BUILD": os_build,
        "CPU": cpu,
        "MEM_GB": mem_gb,
        "ARCH": platform.machine(),
        "SHELL": os.environ.get("SHELL", "unknown"),
        "CLAUDE_VERSION": _tool_version(["claude", "--version"]),
        "GIT_VERSION": _tool_version(["git", "--version"]),
        "NODE_VERSION": _tool_version(["node", "-v"]),
        "NPM_VERSION": _tool_version(["npm", "-v"]),
        "PYTHON_POLICY": (
            f"Local Python-backed episteme commands run in {RUNTIME_KIND} Python at {PYTHON_PREFIX}."
        ),
    }


# ---------------------------------------------------------------------------
# Asset helpers
# ---------------------------------------------------------------------------

def _load_template(rel_path: str) -> str:
    return (REPO_ROOT / "templates" / "project" / rel_path).read_text(encoding="utf-8")


def _managed_skills() -> list[Path]:
    selected = set(RUNTIME_MANIFEST["vendor_skills"] + RUNTIME_MANIFEST["custom_skills"])
    candidates = list((REPO_ROOT / "skills" / "vendor").glob("*/SKILL.md")) + list(
        (REPO_ROOT / "skills" / "custom").glob("*/SKILL.md")
    )
    skill_dirs: list[Path] = []
    for skill_file in candidates:
        skill_dir = skill_file.parent
        if skill_dir.name in selected:
            skill_dirs.append(skill_dir)
    return sorted(skill_dirs, key=lambda p: p.name)


def _resolve_memory_file(name: str) -> Path:
    """Return the personal file if it exists, else fall back to the example in examples/."""
    personal = GLOBAL_MEMORY_DIR / f"{name}.md"
    if personal.exists():
        return personal
    return GLOBAL_MEMORY_DIR / "examples" / f"{name}.example.md"


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

def _init_memory() -> int:
    """Bootstrap personal memory files from examples/*.example.md templates.

    Scope: this command seeds the kernel's own global memory at
    REPO_ROOT/core/memory/global/ from example templates. It is a one-shot
    setup step for a fresh clone of the episteme kernel repo; it does NOT
    scaffold the current working directory. For project scaffolding, use
    `episteme bootstrap`.

    If the personal files already exist (e.g. the repo ships with the author's
    real profiles), init skips them so forks start from those real profiles.
    """
    cwd = Path.cwd().resolve()
    memory_dir = REPO_ROOT / "core" / "memory" / "global"
    examples_dir = memory_dir / "examples"
    names = ["overview", "operator_profile", "workflow_policy", "python_runtime_policy", "cognitive_profile"]

    print(f"Seeding kernel global memory at {memory_dir}")
    print("(this command always targets the kernel install, not your current directory)")

    created: list[str] = []
    skipped: list[str] = []

    for name in names:
        personal = memory_dir / f"{name}.md"
        example = examples_dir / f"{name}.example.md"
        if personal.exists():
            skipped.append(f"{name}.md")
            continue
        if not example.exists():
            print(f"Warning: examples/{name}.example.md not found, skipping.", file=sys.stderr)
            continue
        shutil.copy2(example, personal)
        created.append(f"{name}.md")

    if created:
        print("\nCreated personal memory files:")
        for f in created:
            print(f"  core/memory/global/{f}")
        print("\nNext: edit these files with your personal context, then run `episteme sync`.")
    if skipped:
        print(f"\nAlready present (not overwritten): {', '.join(skipped)}")
        print("To re-seed an individual file, copy its .example.md template by hand —")
        print("this guard protects your real profile from accidental overwrite.")
    if not created and not skipped:
        print("\nNothing to do.")

    if cwd != REPO_ROOT:
        print(f"\nNote: you ran `episteme init` from {cwd}, which is not the kernel repo.")
        print("If you meant to scaffold this project, run `episteme bootstrap` instead.")

    return 0


# ---------------------------------------------------------------------------
# sync
# ---------------------------------------------------------------------------
# Runtime-specific sync logic lives in src/episteme/adapters/. This file
# holds only orchestration (_sync_user_runtime) and dry-run reporting
# (_sync_check). Adapters are imported lazily inside functions to avoid a
# circular import at module load time.



def _sync_check(governance_mode: str = "balanced") -> int:
    """Check what sync would write/update without making changes.

    Returns 0 if everything is in sync, 1 if changes would be made.
    """
    claude_root = HOME / ".claude"
    hermes_root = HOME / ".hermes"

    changes_needed: list[str] = []
    up_to_date: list[str] = []

    def _check_managed_target(path: Path, managed_content: str, label: str) -> None:
        """Compare only the managed region so user edits outside markers don't flag as drift."""
        if not path.exists():
            changes_needed.append(f"would create: {label}")
            return
        existing = path.read_text(encoding="utf-8")
        current_managed = _extract_managed_block(existing)
        expected = managed_content.rstrip()
        if current_managed is not None and current_managed == expected:
            up_to_date.append(label)
        elif current_managed is None:
            changes_needed.append(f"would migrate (insert managed markers): {label}")
        else:
            changes_needed.append(f"would update: {label}")

    from .adapters import claude as _claude
    from .adapters import hermes as _hermes

    # Claude CLAUDE.md
    _check_managed_target(claude_root / "CLAUDE.md", _claude.render_user_claude_md(), "~/.claude/CLAUDE.md")

    # Claude settings.json
    settings_path = claude_root / "settings.json"
    episteme = _claude.build_settings(governance_mode)
    if settings_path.exists():
        try:
            existing_settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing_settings = {}
    else:
        existing_settings = {}
    merged = _claude.merge_settings(existing_settings, episteme)
    merged = _claude.prune_managed_hook_entries(merged, governance_mode)
    merged = _claude.enforce_governance_overrides(merged, governance_mode)
    merged["hooks"] = _claude.dedupe_hooks_map(merged.get("hooks", {}))
    new_settings_content = json.dumps(merged, indent=2) + "\n"
    if settings_path.exists():
        existing_settings_content = settings_path.read_text(encoding="utf-8")
        if existing_settings_content == new_settings_content:
            up_to_date.append("~/.claude/settings.json")
        else:
            changes_needed.append("would update: ~/.claude/settings.json")
    else:
        changes_needed.append("would create: ~/.claude/settings.json")

    # Agent files
    for agent_file in sorted((REPO_ROOT / "core" / "agents").glob("*.md")):
        dst = claude_root / "agents" / agent_file.name
        src_content = agent_file.read_text(encoding="utf-8")
        if dst.exists() and dst.read_text(encoding="utf-8") == src_content:
            up_to_date.append(f"~/.claude/agents/{agent_file.name}")
        else:
            label = "update" if dst.exists() else "create"
            changes_needed.append(f"would {label}: ~/.claude/agents/{agent_file.name}")

    # Skills
    for skill_dir in _managed_skills():
        dst = claude_root / "skills" / skill_dir.name
        label = f"~/.claude/skills/{skill_dir.name}"
        if dst.exists():
            up_to_date.append(label)
        else:
            changes_needed.append(f"would create: {label}")

    # Hermes OPERATOR.md — managed region check (composed by the hermes adapter)
    if hermes_root.exists():
        _check_managed_target(
            hermes_root / "OPERATOR.md",
            _hermes._compose_operator_context(),
            "~/.hermes/OPERATOR.md",
        )

    print("sync --check: dry-run sync state report")
    print(f"  Governance pack: {governance_mode}")
    print()

    if up_to_date:
        print("Up to date:")
        for item in up_to_date:
            print(f"  [ok] {item}")
        print()

    if changes_needed:
        print("Would change:")
        for item in changes_needed:
            print(f"  [diff] {item}")
        print()
        print(f"  {len(changes_needed)} target(s) would be updated. Run `episteme sync` to apply.")
        return 1

    print("Everything is in sync. No changes needed.")
    return 0


def _sync_user_runtime(governance_mode: str = "balanced") -> None:
    from .adapters import claude as _claude
    from .adapters import hermes as _hermes
    from .adapters import omo as _omo
    from .adapters import omx as _omx

    _claude.sync(governance_mode)
    hermes_synced = _hermes.sync()
    omo_synced = _omo.sync(governance_mode)
    omx_synced = _omx.sync(governance_mode)

    print("Synced user runtime:")
    print(f"  - Claude: {HOME / '.claude'}")
    print(f"  - Governance pack: {governance_mode}")
    if hermes_synced:
        print(f"  - Hermes: {HOME / '.hermes'}")
    if omo_synced:
        print(f"  - OMO: {HOME / '.omo'}")
    if omx_synced:
        print(f"  - OMX: {HOME / '.omx'}")


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def _list_runtime() -> None:
    claude_root = HOME / ".claude"

    print("=== Agents ===")
    agents_dir = claude_root / "agents"
    if agents_dir.exists():
        for f in sorted(agents_dir.glob("*.md")):
            print(f"  {f.stem}")
    else:
        print("  (none)")

    print("\n=== Skills ===")
    skills_dir = claude_root / "skills"
    managed = {p.name for p in _managed_skills()}
    if skills_dir.exists():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir():
                tag = " [episteme]" if d.name in managed else " [external]"
                print(f"  {d.name}{tag}")
    else:
        print("  (none)")

    print("\n=== Plugins ===")
    installed_json = claude_root / "plugins" / "installed_plugins.json"
    if installed_json.exists():
        data = json.loads(installed_json.read_text(encoding="utf-8"))
        for name in sorted(data.get("plugins", {}).keys()):
            print(f"  {name}")
    else:
        print("  (none)")

    print("\n=== Hooks (global settings.json) ===")
    settings_path = claude_root / "settings.json"
    if settings_path.exists():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        for event, entries in settings.get("hooks", {}).items():
            for entry in entries:
                matcher = entry.get("matcher", "*")
                for h in entry.get("hooks", []):
                    cmd = h.get("command", "")
                    short = cmd.split("/")[-1] if "/" in cmd else cmd
                    print(f"  {event} [{matcher}] → {short}")


# ---------------------------------------------------------------------------
# private-skill
# ---------------------------------------------------------------------------

def _private_skill_source(name: str) -> Path:
    return REPO_ROOT / "skills" / "private" / name


def _private_skill_install_path(name: str, tool: str) -> Path:
    if tool != "claude":
        raise ValueError(f"unsupported private skill tool: {tool}")
    return HOME / ".claude" / "skills" / name


def _private_skill(action: str, name: str, tool: str) -> int:
    if tool != "claude":
        print(f"Private skills currently support only Claude. Unsupported tool: {tool}", file=sys.stderr)
        return 1

    source = _private_skill_source(name)
    install_path = _private_skill_install_path(name, tool)
    source_skill = source / "SKILL.md"
    installed = install_path.exists()

    if action == "status":
        print(f"Private skill: {name}")
        print(f"Tool: {tool}")
        print(f"Source: {source}")
        print(f"Install path: {install_path}")
        print(f"Source status: {'present' if source_skill.exists() else 'missing SKILL.md'}")
        print(f"Installed: {'yes' if installed else 'no'}")
        return 0

    if not source_skill.exists():
        print(f"Private skill source missing: {source_skill}", file=sys.stderr)
        return 1

    if action == "enable":
        if install_path.exists():
            shutil.rmtree(install_path)
        _copy_tree(source, install_path)
        print(f"Enabled private skill '{name}' for {tool}: {install_path}")
        return 0

    if action == "disable":
        if install_path.exists():
            shutil.rmtree(install_path)
            print(f"Disabled private skill '{name}' for {tool}: removed {install_path}")
        else:
            print(f"Private skill '{name}' is already absent for {tool}: {install_path}")
        return 0

    print(f"Unsupported private-skill action: {action}", file=sys.stderr)
    return 1


# ---------------------------------------------------------------------------
# memory record / list / search
# ---------------------------------------------------------------------------

def _memory_record(
    summary: str,
    memory_class: str,
    confidence: str,
    source: str,
) -> int:
    record_id = str(uuid.uuid4())
    record = {
        "id": record_id,
        "memory_class": memory_class,
        "summary": summary,
        "details": {},
        "provenance": {
            "source_type": source,
            "source_ref": "cli",
            "captured_at": _now_iso(),
            "captured_by": "episteme memory record",
            "confidence": confidence,
            "evidence_refs": [],
        },
        "status": "active",
        "version": "memory-contract-v1",
    }
    out_dir = MEMORY_RECORDS_DIR / memory_class
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{record_id}.memory.json"
    out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Memory record created: {out_path}")
    print(f"  id:      {record_id}")
    print(f"  class:   {memory_class}")
    print(f"  summary: {summary}")
    return 0


def _memory_list(
    memory_class: str | None,
    status: str,
    limit: int,
) -> int:
    classes = [memory_class] if memory_class else ["global", "project", "episodic"]
    records: list[dict] = []
    for cls in classes:
        cls_dir = MEMORY_RECORDS_DIR / cls
        if not cls_dir.exists():
            continue
        for f in cls_dir.glob("*.memory.json"):
            try:
                rec = json.loads(f.read_text(encoding="utf-8"))
                if rec.get("status") == status:
                    records.append(rec)
            except (json.JSONDecodeError, OSError):
                continue

    records.sort(key=lambda r: r.get("provenance", {}).get("captured_at", ""), reverse=True)
    records = records[:limit]

    if not records:
        print(f"No {status} memory records found.")
        return 0

    print(f"{'ID':<38}  {'CLASS':<10}  {'CONF':<8}  {'CAPTURED':<26}  SUMMARY")
    print("-" * 110)
    for rec in records:
        rid = str(rec.get("id", ""))[:36]
        cls = str(rec.get("memory_class", ""))[:10]
        conf = str(rec.get("provenance", {}).get("confidence", ""))[:8]
        ts = str(rec.get("provenance", {}).get("captured_at", ""))[:26]
        summary = str(rec.get("summary", ""))[:60]
        print(f"{rid:<38}  {cls:<10}  {conf:<8}  {ts:<26}  {summary}")
    return 0


def _memory_search(query: str) -> int:
    query_lower = query.lower()
    found = 0
    for cls in ["global", "project", "episodic"]:
        cls_dir = MEMORY_RECORDS_DIR / cls
        if not cls_dir.exists():
            continue
        for f in sorted(cls_dir.glob("*.memory.json")):
            try:
                rec = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if rec.get("status") != "active":
                continue
            summary = str(rec.get("summary", "")).lower()
            details_str = json.dumps(rec.get("details", {})).lower()
            if query_lower in summary or query_lower in details_str:
                if found == 0:
                    print(f"Search results for: {query!r}")
                    print()
                rid = str(rec.get("id", ""))[:36]
                ts = str(rec.get("provenance", {}).get("captured_at", ""))[:26]
                print(f"  [{cls}] {rid}  {ts}")
                print(f"    {rec.get('summary', '')}")
                print()
                found += 1
    if found == 0:
        print(f"No active records matching {query!r}")
    return 0


# ---------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------

def _doctor() -> int:
    failures: list[str] = []
    warnings: list[str] = []
    ok_count = 0
    info_count = 0

    def _line(status: str, message: str) -> None:
        """Print a status line with a fixed-width status label."""
        nonlocal ok_count, info_count
        label_map = {"ok": "[  ok  ]", "info": "[ info ]", "warn": "[ warn ]", "miss": "[ miss ]", "fail": "[ fail ]"}
        label = label_map.get(status, f"[{status:^6}]")
        print(f"  {label}  {message}")
        if status == "ok":
            ok_count += 1
        elif status == "info":
            info_count += 1

    def _section(title: str) -> None:
        print(f"\n  {title}")
        print(f"  {'─' * max(len(title), 32)}")

    print("🧠 episteme awareness check")
    print()
    print(f"  project core  : {REPO_ROOT}")
    print(f"  python runtime: {sys.executable}")
    print(f"  python prefix : {PYTHON_PREFIX} ({RUNTIME_KIND})")

    _section("runtime")
    # Conda checks: opt-in. Either the detected runtime is conda, or the operator
    # explicitly requires it via EPISTEME_REQUIRE_CONDA=1.
    if RUNTIME_KIND == "conda" or REQUIRE_CONDA:
        conda_bin = PYTHON_PREFIX / "bin" / "conda"
        if not conda_bin.exists():
            msg = f"missing conda binary at {conda_bin}"
            (failures if REQUIRE_CONDA else warnings).append(msg)
            _line("miss" if not REQUIRE_CONDA else "fail", f"conda binary: {conda_bin}")
        else:
            _line("ok", f"conda binary: {conda_bin}")
            try:
                envs = _run([str(conda_bin), "info", "--envs"]).stdout
                if re.search(r"^base\s+", envs, re.MULTILINE):
                    _line("ok", "conda base environment exists")
                else:
                    (failures if REQUIRE_CONDA else warnings).append("conda base environment not found")
                    _line("miss" if not REQUIRE_CONDA else "fail", "conda base environment not found")
            except subprocess.CalledProcessError as exc:
                (failures if REQUIRE_CONDA else warnings).append(f"failed to inspect conda envs: {exc}")
                _line("warn", f"failed to inspect conda envs: {exc}")
    else:
        _line("info", "non-conda runtime — skipping conda checks (set EPISTEME_REQUIRE_CONDA=1 to enforce)")

    _section("core tools")
    for tool in ["claude", "git", "jq"]:
        if _command_exists(tool):
            _line("ok", f"{tool}")
        else:
            failures.append(f"missing tool: {tool}")
            _line("fail", f"{tool} — required")

    _section("local-only tools")
    for tool in ["rg", "fd", "bat"]:
        if _command_exists(tool):
            _line("ok", f"{tool}")
        else:
            _line("info", f"{tool} — not required on remote machines")

    _section("optional tools")
    for tool in ["tmux", "gh", "sd", "ov"]:
        if _command_exists(tool):
            _line("ok", f"{tool}")
        else:
            _line("info", f"{tool} — not installed")

    _section("kernel integrity")
    # Runtime drift checks: Claude hook duplication
    claude_settings_path = HOME / ".claude" / "settings.json"
    if claude_settings_path.exists():
        try:
            from .adapters import claude as _claude
            settings = json.loads(claude_settings_path.read_text(encoding="utf-8"))
            hooks = settings.get("hooks", {}) if isinstance(settings, dict) else {}
            deduped = _claude.dedupe_hooks_map(hooks)
            orig_count = 0
            deduped_count = 0
            for entries in hooks.values() if isinstance(hooks, dict) else []:
                if isinstance(entries, list):
                    orig_count += len(entries)
            for entries in deduped.values():
                if isinstance(entries, list):
                    deduped_count += len(entries)

            if deduped_count < orig_count:
                msg = f"~/.claude/settings.json has {orig_count - deduped_count} duplicate hook entries — run `episteme sync` to normalize"
                warnings.append(msg)
                _line("warn", msg)
            else:
                _line("ok", "~/.claude/settings.json — no duplicate hooks")
        except json.JSONDecodeError:
            msg = "~/.claude/settings.json is not valid JSON — drift checks skipped"
            warnings.append(msg)
            _line("warn", msg)

    # Kernel integrity drift check
    from . import kernel_integrity as _kint
    if (REPO_ROOT / _kint.MANIFEST_PATH).exists():
        ok, diffs = _kint.verify(REPO_ROOT)
        if ok:
            _line("ok", "kernel manifest: in sync")
        else:
            msg = f"kernel drift: {len(diffs)} file(s) — run `episteme kernel update` to refresh"
            warnings.append(msg)
            _line("warn", msg)
    else:
        _line("info", "kernel manifest not initialized — run `episteme kernel update` to create one")

    _section("runtime sync state")
    hermes_operator = HOME / ".hermes" / "OPERATOR.md"
    if hermes_operator.exists() and hermes_operator.stat().st_size > 0:
        _line("ok", "hermes OPERATOR.md present")
    else:
        _line("miss", "hermes OPERATOR.md not found — run `episteme sync`")

    claude_md = HOME / ".claude" / "CLAUDE.md"
    if claude_md.exists():
        _line("ok", "claude ~/.claude/CLAUDE.md present")
    else:
        _line("miss", "claude ~/.claude/CLAUDE.md not found — run `episteme sync`")

    try:
        git_remote = _run(["git", "remote"], cwd=REPO_ROOT, check=False).stdout.strip()
        if git_remote:
            _line("ok", f"episteme git remote: {git_remote.splitlines()[0]}")
        else:
            _line("info", "episteme git remote: none configured (local-only repo)")
    except Exception:
        _line("info", "episteme git remote: could not determine (git not available)")

    # Summary block — always printed
    _section("summary")
    fail_count = len(failures)
    warn_count = len(warnings)
    print(f"  {ok_count} ok · {info_count} info · {warn_count} warn · {fail_count} fail")

    if failures:
        print("\n  failures:")
        for item in failures:
            print(f"    × {item}")

        print("\n  tips to fix:")
        if any("conda" in f.lower() for f in failures):
            print("    • Ensure Conda is installed and EPISTEME_PYTHON_PREFIX points to its root.")
            print(f"      Current: export EPISTEME_PYTHON_PREFIX={PYTHON_PREFIX}")
            print("      (Or unset EPISTEME_REQUIRE_CONDA to allow non-conda runtimes.)")
        if any("git" in f.lower() for f in failures):
            print("    • Ensure Git is installed and you are inside a repository.")
        return 1

    if warnings:
        print("\n  warnings:")
        for item in warnings:
            print(f"    ⚠ {item}")

    print("\n✅ awareness verified — the Soul is ready for transition.")
    return 0


# ---------------------------------------------------------------------------
# worktree / start / validate / update
# ---------------------------------------------------------------------------

def _current_repo_root(cwd: Path) -> Path:
    try:
        output = _run(["git", "rev-parse", "--show-toplevel"], cwd=cwd).stdout.strip()
    except subprocess.CalledProcessError:
        return cwd.resolve()
    return Path(output)


def _resolve_bootstrap_target(path_arg: str) -> Path:
    candidate = Path(path_arg).expanduser()
    if path_arg == ".":
        return _current_repo_root(Path.cwd())
    return candidate.resolve()


def _worktree(task_type: str, task_name: list[str], base_ref: str | None, cwd: Path) -> int:
    repo_root = _current_repo_root(cwd)
    if not (repo_root / ".git").exists():
        print(f"Not a git repository: {repo_root}", file=sys.stderr)
        return 1

    slug = re.sub(r"[^a-z0-9]+", "-", " ".join(task_name).lower()).strip("-")
    if not slug:
        print("Unable to derive worktree slug.", file=sys.stderr)
        return 1

    branch_name = f"{task_type}/{slug}"
    parent_dir = repo_root.parent
    worktree_path = parent_dir / f"{repo_root.name}__{task_type}-{slug}"

    if not base_ref:
        base_ref = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root).stdout.strip()

    branch_exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    ).returncode == 0

    if branch_exists:
        _run(["git", "worktree", "add", str(worktree_path), branch_name], cwd=repo_root, capture_output=False)
    else:
        _run(
            ["git", "worktree", "add", "-b", branch_name, str(worktree_path), base_ref],
            cwd=repo_root,
            capture_output=False,
        )

    print(f"Created worktree: {worktree_path}")
    print(f"Branch: {branch_name}")
    return 0


def _start(tool: str, cwd: Path) -> int:
    del cwd  # currently unused; kept for signature stability with caller
    if tool == "claude":
        os.execvp("claude", ["claude"])
    print(f"Unsupported tool: {tool}", file=sys.stderr)
    return 1


def _validate_manifest() -> int:
    failures: list[str] = []
    warnings: list[str] = []

    sources_path = REPO_ROOT / "skills" / "vendor" / "SOURCES.md"
    sources_text = ""
    if not sources_path.exists():
        failures.append("skills/vendor/SOURCES.md missing (required for vendor provenance)")
    else:
        sources_text = sources_path.read_text(encoding="utf-8")
        if "Curated vendor skills are sourced from" not in sources_text:
            warnings.append("skills/vendor/SOURCES.md missing required source heading")

    all_declared = RUNTIME_MANIFEST["vendor_skills"] + RUNTIME_MANIFEST["custom_skills"]

    for bucket in ("vendor", "custom"):
        key = f"{bucket}_skills"
        for name in RUNTIME_MANIFEST[key]:
            skill_md = REPO_ROOT / "skills" / bucket / name / "SKILL.md"
            if not skill_md.exists():
                failures.append(f"[{bucket}] '{name}' declared in manifest but SKILL.md not found at {skill_md}")
            else:
                print(f"[ok] [{bucket}] {name}")
                if bucket == "vendor":
                    raw = skill_md.read_text(encoding="utf-8")
                    if "## Provenance" not in raw:
                        warnings.append(
                            f"[vendor] '{name}' has no '## Provenance' section in SKILL.md "
                            "(recommended for inspired-not-copied traceability)"
                        )
                    if sources_text and name not in sources_text:
                        warnings.append(
                            f"[vendor] '{name}' is declared but not listed in skills/vendor/SOURCES.md"
                        )

    for bucket in ("vendor", "custom"):
        bucket_dir = REPO_ROOT / "skills" / bucket
        if not bucket_dir.exists():
            continue
        for skill_dir in sorted(bucket_dir.iterdir()):
            if skill_dir.is_dir() and skill_dir.name not in all_declared:
                warnings.append(f"[{bucket}] '{skill_dir.name}' directory exists but is not in manifest")

    agents_dir = REPO_ROOT / "core" / "agents"
    if agents_dir.exists():
        for f in sorted(agents_dir.glob("*.md")):
            print(f"[ok] [agent] {f.stem}")
    else:
        failures.append("core/agents/ directory missing")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ! {w}")

    if failures:
        print("\nValidation failed:")
        for f in failures:
            print(f"  x {f}")
        return 1

    print("\nValidation passed.")
    return 0


def _update() -> int:
    if not (REPO_ROOT / ".git").exists():
        print("episteme repo has no .git directory — cannot update.", file=sys.stderr)
        return 1
    try:
        result = _run(["git", "pull", "--ff-only"], cwd=REPO_ROOT, capture_output=False)
        return result.returncode
    except subprocess.CalledProcessError as exc:
        print(f"Update failed: {exc}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Harness system
# ---------------------------------------------------------------------------

def _load_harnesses() -> dict[str, dict]:
    """Load all harness definitions from core/harnesses/."""
    harnesses: dict[str, dict] = {}
    if not HARNESSES_DIR.exists():
        return harnesses
    for json_file in sorted(HARNESSES_DIR.glob("*.json")):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            harnesses[data["name"]] = data
        except (json.JSONDecodeError, KeyError):
            pass
    return harnesses


def _collect_project_signals(project_root: Path) -> tuple[str, set[str]]:
    """Return (dependency_text, directory_name_set) for a project root.

    Reads dependency/manifest files for import signatures, and walks one level
    of subdirectories for directory-name signals. Kept shallow and fast.
    """
    dep_files = [
        "requirements.txt", "requirements-dev.txt", "requirements_dev.txt",
        "pyproject.toml", "setup.py", "setup.cfg", "package.json",
        "Pipfile", "environment.yml", "environment.yaml",
    ]
    dep_parts: list[str] = []
    for name in dep_files:
        p = project_root / name
        if p.exists():
            try:
                dep_parts.append(p.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                pass
    dep_text = "\n".join(dep_parts).lower()

    dir_names: set[str] = set()
    try:
        for item in project_root.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                dir_names.add(item.name)
                try:
                    for subitem in item.iterdir():
                        if subitem.is_dir() and not subitem.name.startswith("."):
                            dir_names.add(subitem.name)
                except OSError:
                    pass
    except OSError:
        pass

    return dep_text, dir_names


def _score_harness(
    harness: dict,
    project_root: Path,
    dep_text: str,
    dir_names: set[str],
) -> tuple[int, list[str]]:
    """Score a harness against collected project signals.

    Weights: import signature = 3, file pattern = 2, directory = 1, config file = 1.
    Returns (score, list_of_matched_signal_descriptions).
    """
    score = 0
    signals: list[str] = []
    detection = harness.get("detection", {})

    # Import signatures in dependency manifests — strongest signal
    for sig in detection.get("import_signatures", []):
        if sig.lower() in dep_text:
            score += 3
            signals.append(f"dependency: {sig}")

    # File patterns — concrete structural evidence (early-exit after 3 matches)
    for pattern in detection.get("file_patterns", []):
        matches: list[Path] = []
        try:
            for m in project_root.glob(pattern):
                matches.append(m)
                if len(matches) >= 3:
                    break
        except (OSError, ValueError):
            continue
        if matches:
            score += 2
            signals.append(f"file: {pattern} ({len(matches)}{'+ ' if len(matches) >= 3 else ' '}found)")

    # Directory names — contextual hint
    for dname in detection.get("directory_names", []):
        if dname in dir_names:
            score += 1
            signals.append(f"directory: {dname}/")

    # Config files at project root — specific but weak
    for config in detection.get("config_files", []):
        if (project_root / config).exists():
            score += 1
            signals.append(f"config: {config}")

    return score, signals


def _detect_project_harness(project_root: Path) -> list[tuple[str, int, list[str]]]:
    """Detect the most likely harness type for a project.

    Returns a list of (harness_name, score, signals) sorted by score descending,
    excluding the generic fallback (which is always available via `harness apply`).
    """
    harnesses = _load_harnesses()
    if not harnesses:
        return []
    dep_text, dir_names = _collect_project_signals(project_root)
    results: list[tuple[str, int, list[str]]] = []
    for name, harness in harnesses.items():
        if name == "generic":
            continue
        score, signals = _score_harness(harness, project_root, dep_text, dir_names)
        results.append((name, score, signals))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def _render_harness_md(harness: dict) -> str:
    """Render the HARNESS.md content for a given harness definition."""
    name = harness["name"]
    label = harness["label"]
    description = harness["description"]
    profile = harness["execution_profile"]
    profile_desc = harness.get("profile_description", "")
    workflow_notes = harness.get("workflow_notes", [])
    safety_notes = harness.get("safety_notes", [])
    agents = harness.get("recommended_agents", [])
    skills = harness.get("recommended_skills", [])

    lines: list[str] = [
        f"# Project Harness: {label}",
        "",
        f"Generated by `episteme harness apply {name}`.",
        "Edit this file to customize the operating context for this project.",
        "",
        f"> {description}",
        "",
        "---",
        "",
        "## Execution Profile",
        "",
        f"`{profile}`" + (f" — {profile_desc}" if profile_desc else ""),
        "",
    ]

    if workflow_notes:
        lines += ["## Workflow Notes", ""]
        for note in workflow_notes:
            lines.append(f"- {note}")
        lines.append("")

    if safety_notes:
        lines += ["## Safety", ""]
        for note in safety_notes:
            lines.append(f"- {note}")
        lines.append("")

    if agents:
        lines += ["## Recommended Agents", ""]
        lines.append("`" + "` · `".join(agents) + "`")
        lines.append("")

    if skills:
        lines += ["## Recommended Skills", ""]
        lines.append("`" + "` · `".join(skills) + "`")
        lines.append("")

    return "\n".join(lines)


def _apply_harness_run_context(harness: dict, project_root: Path) -> bool:
    """Append harness-specific content to docs/RUN_CONTEXT.md if it exists.

    Skips silently if the file is absent or the section is already present.
    Returns True if the file was modified.
    """
    additions = harness.get("run_context_additions", [])
    if not additions:
        return False
    run_context_path = project_root / "docs" / "RUN_CONTEXT.md"
    if not run_context_path.exists():
        return False
    current = run_context_path.read_text(encoding="utf-8")
    header = next((line for line in additions if line.startswith("## ")), None)
    if header and header in current:
        return False
    extra = "\n" + "\n".join(additions) + "\n"
    _write_text(run_context_path, current.rstrip() + "\n" + extra)
    return True


def _apply_harness(harness_name: str, project_root: Path, *, force: bool = False) -> int:
    """Write HARNESS.md and extend RUN_CONTEXT.md for the given harness type."""
    harnesses = _load_harnesses()
    if harness_name not in harnesses:
        available = ", ".join(sorted(harnesses.keys()))
        print(f"Unknown harness: '{harness_name}'. Available: {available}", file=sys.stderr)
        return 1

    harness = harnesses[harness_name]
    harness_path = project_root / "HARNESS.md"

    if harness_path.exists() and not force:
        print(f"HARNESS.md already exists in {project_root}. Use --force to overwrite.")
        return 1

    _write_text(harness_path, _render_harness_md(harness))
    print(f"Applied harness '{harness_name}' to {project_root}")
    print(f"  - Created HARNESS.md")

    if _apply_harness_run_context(harness, project_root):
        print(f"  - Updated docs/RUN_CONTEXT.md with {harness_name} context")

    return 0


def _list_harnesses() -> None:
    harnesses = _load_harnesses()
    if not harnesses:
        print("No harnesses found in core/harnesses/")
        return
    print("Available harnesses:")
    print()
    for name, harness in sorted(harnesses.items()):
        description = harness.get("description", "")
        print(f"  {name:<22} {description}")
    print()
    print("Apply: episteme harness apply <name> [path]")
    print("Detect best fit: episteme detect [path]")


# ---------------------------------------------------------------------------
# Deterministic working-style profile system
# ---------------------------------------------------------------------------

PROFILE_DIMENSIONS = [
    "planning_strictness",
    "risk_tolerance",
    "testing_rigor",
    "parallelism_preference",
    "documentation_rigor",
    "automation_level",
]


def _profile_survey_questions() -> list[dict]:
    return [
        {
            "dimension": "planning_strictness",
            "question": (
                "You're about to start a non-trivial feature. What do you do first?\n"
                "  (This reveals how you think BEFORE you act.)"
            ),
            "choices": [
                "Open an editor and start writing — the shape emerges as I go.",
                "Jot a quick checklist of steps so I don't lose the thread.",
                "Draft a phased plan with explicit checkpoints before touching code.",
                "Require a written spec with assumptions, unknowns, and review gate before any implementation.",
            ],
        },
        {
            "dimension": "risk_tolerance",
            "question": (
                "An agent proposes an irreversible action (e.g., dropping a DB table, deleting files). What matters most?\n"
                "  (This reveals your default trust posture.)"
            ),
            "choices": [
                "Speed matters — proceed if the reasoning is sound.",
                "A quick sanity check is enough; I approve fast.",
                "I want the agent to pause, state the blast radius, and get confirmation.",
                "Hard stop: explicit approval gate + rollback plan required before proceeding.",
            ],
        },
        {
            "dimension": "testing_rigor",
            "question": (
                "You've written a function that touches core business logic. What's the minimum you need before calling it done?\n"
                "  (This reveals your quality bar, not your skill.)"
            ),
            "choices": [
                "If it runs without crashing, it ships.",
                "A quick manual test of the happy path is enough.",
                "Targeted unit tests for the new logic; CI must pass.",
                "Comprehensive tests covering edge cases and regressions; blocked until green.",
            ],
        },
        {
            "dimension": "parallelism_preference",
            "question": (
                "You have three independent tasks: a bug fix, a new feature, and a doc update. How do you run them?\n"
                "  (This reveals how you manage cognitive load and context.)"
            ),
            "choices": [
                "One at a time, fully sequenced — I finish before I start.",
                "Maybe two at once if they're truly independent.",
                "Parallel lanes with clear ownership, synchronized at checkpoints.",
                "Structured multi-worktree parallelism with explicit merge strategy from the start.",
            ],
        },
        {
            "dimension": "documentation_rigor",
            "question": (
                "You finish a complex session where decisions were made and trade-offs accepted. What do you write down?\n"
                "  (This reveals how you treat institutional memory.)"
            ),
            "choices": [
                "Nothing — the code is the documentation.",
                "A brief note in a commit message or quick comment.",
                "Update the relevant PLAN/PROGRESS/DECISIONS docs with key choices.",
                "Full session debrief: decisions, rejected alternatives, open risks — treated as a mandatory contract.",
            ],
        },
        {
            "dimension": "automation_level",
            "question": (
                "A linter fails on a PR. A formatter could auto-fix it, a hook could block it, or you could review manually. What's your default?\n"
                "  (This reveals how much you trust deterministic automation over human judgment.)"
            ),
            "choices": [
                "Manual review — I want eyes on everything before it changes.",
                "Auto-fix is fine for formatting; I still review logic.",
                "Automate quality gates; block on failures, auto-apply safe fixes.",
                "Comprehensive automation with strict guardrails — humans review exceptions, not the norm.",
            ],
        },
    ]


def _prompt_choice(question: str, choices: list[str]) -> int:
    while True:
        print()
        print(question)
        for idx, choice in enumerate(choices, start=1):
            print(f"  {idx}) {choice}")
        raw = input("Select 1-4: ").strip()
        if raw in {"1", "2", "3", "4"}:
            return int(raw)
        print("Invalid selection. Please enter 1, 2, 3, or 4.")


def _normalize_answers(answers: dict[str, int]) -> dict[str, int]:
    normalized: dict[str, int] = {}
    parsed: dict[str, int] = {}

    for key, raw in answers.items():
        try:
            parsed[key] = int(raw)
        except (TypeError, ValueError):
            continue

    # If any answer is 0, interpret the whole payload as 0..3 scale and map to 1..4.
    # Otherwise interpret as 1..4 directly.
    zero_based_mode = any(value == 0 for value in parsed.values())

    for key, value in parsed.items():
        if zero_based_mode:
            if 0 <= value <= 3:
                normalized[key] = value + 1
        else:
            if 1 <= value <= 4:
                normalized[key] = value
    return normalized


def _load_answers_file(path: Path) -> dict[str, int]:
    if not path.exists():
        raise FileNotFoundError(f"answers file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in answers file: {path} ({exc})") from exc

    if not isinstance(payload, dict):
        raise ValueError("answers file must be a JSON object")

    # Support either top-level map or {"answers": {...}}
    if "answers" in payload and isinstance(payload["answers"], dict):
        payload = payload["answers"]

    return _normalize_answers(payload)


def _profile_gap_survey(project_root: Path, answers: dict[str, int] | None = None) -> dict:
    """Context-Loading Protocol: load what is known, infer what can be detected, ask only genuine gaps.

    This replaces the blind 'ask all 12 questions' approach. The protocol:
    1. Load existing generated scores if present (prior knowledge).
    2. Run infer on the project root to detect behavioral signals.
    3. For each dimension, determine if a confident score already exists.
    4. Ask only for dimensions where existing evidence is absent or contradictory.
    """
    # Step 1: load any existing generated workstyle scores
    existing_workstyle, _ = _load_generated_scores(REPO_ROOT)

    # Step 2: run infer to detect repo signals
    print("Scanning project signals...")
    inferred = _profile_infer(project_root)
    inferred_scores: dict[str, int] = inferred.get("scores", {})
    inferred_evidence: dict[str, list[str]] = inferred.get("evidence", {})

    # Step 3: decide which dimensions need a question
    # Confidence threshold: if infer produced evidence (>= 1 signal hit), treat as confident
    # If existing scores also agree, skip the question entirely
    confirmed_scores: dict[str, int] = {}
    gaps: list[str] = []
    loaded_from: dict[str, str] = {}

    for dim in PROFILE_DIMENSIONS:
        infer_score = inferred_scores.get(dim, 0)
        infer_ev = inferred_evidence.get(dim, [])
        existing_score = existing_workstyle.get(dim) if existing_workstyle else None

        if existing_score is not None and len(infer_ev) >= 1:
            # Both prior score and current evidence exist: use blended value, no question
            blended = int(round(0.6 * existing_score + 0.4 * infer_score))
            confirmed_scores[dim] = max(0, min(3, blended))
            loaded_from[dim] = f"prior score={existing_score}, infer={infer_score} → blended={confirmed_scores[dim]}"
        elif len(infer_ev) >= 2:
            # Strong inference evidence: use inferred score, no question
            confirmed_scores[dim] = infer_score
            loaded_from[dim] = f"inferred from {len(infer_ev)} signals: {infer_ev[0]}"
        else:
            # Gap: insufficient evidence, must ask
            gaps.append(dim)

    if confirmed_scores:
        print(f"\nLoaded {len(confirmed_scores)} dimension(s) from existing evidence:")
        for dim, note in sorted(loaded_from.items()):
            print(f"  [{dim}] {note}")

    if not gaps:
        print("\nAll dimensions already covered by existing profile and repo signals.")
        print("No questions needed. Run with --overwrite to force a fresh survey.")
        return {
            "source": "gap_survey",
            "gaps_asked": 0,
            "scores": confirmed_scores,
            "evidence": {d: [loaded_from[d]] for d in confirmed_scores},
        }

    # Step 4: ask only for genuine gaps
    print(f"\n{len(gaps)} dimension(s) need your input (insufficient existing evidence):")
    for dim in gaps:
        ev = inferred_evidence.get(dim, [])
        note = f" (detected: {ev[0]})" if ev else " (no signals detected)"
        print(f"  - {dim}{note}")
    print()

    normalized_answers = _normalize_answers(answers or {})
    gap_responses: dict[str, dict] = {}
    gap_scores: dict[str, int] = {}

    questions_map = {q["dimension"]: q for q in _profile_survey_questions()}

    for dim in gaps:
        item = questions_map.get(dim)
        if item is None:
            continue
        if dim in normalized_answers:
            choice_idx = normalized_answers[dim]
            print(f"[answers-file] {dim}: selected option {choice_idx}")
        else:
            choice_idx = _prompt_choice(item["question"], item["choices"])
        score = choice_idx - 1
        gap_responses[dim] = {
            "question": item["question"],
            "selected_option": choice_idx,
            "selected_text": item["choices"][choice_idx - 1],
            "score": score,
        }
        gap_scores[dim] = score

    # Merge confirmed + gap answers
    final_scores = {**confirmed_scores, **gap_scores}
    final_evidence: dict[str, list[str]] = {}
    for dim in PROFILE_DIMENSIONS:
        if dim in gap_scores:
            item = questions_map.get(dim, {})
            choices = item.get("choices", [])
            choice_idx = gap_responses[dim]["selected_option"]
            final_evidence[dim] = [f"survey option {choice_idx}: {choices[choice_idx - 1] if choices else ''}"]
        elif dim in confirmed_scores:
            final_evidence[dim] = [loaded_from[dim]]

    return {
        "source": "gap_survey",
        "gaps_asked": len(gaps),
        "dimensions_confirmed": list(confirmed_scores.keys()),
        "dimensions_asked": gaps,
        "scores": final_scores,
        "responses": gap_responses,
        "evidence": final_evidence,
    }


def _profile_survey(answers: dict[str, int] | None = None) -> dict:
    print("Deterministic workstyle survey")
    print("Answer each question with 1..4. Higher values mean stricter/more structured defaults.")

    normalized_answers = _normalize_answers(answers or {})

    responses: dict[str, dict] = {}
    scores: dict[str, int] = {}
    evidence: dict[str, list[str]] = {}

    for item in _profile_survey_questions():
        dim = item["dimension"]
        if dim in normalized_answers:
            choice_idx = normalized_answers[dim]
            print(f"[answers-file] {dim}: selected option {choice_idx}")
        else:
            choice_idx = _prompt_choice(item["question"], item["choices"])
        score = choice_idx - 1
        responses[dim] = {
            "question": item["question"],
            "selected_option": choice_idx,
            "selected_text": item["choices"][choice_idx - 1],
            "score": score,
        }
        scores[dim] = score
        evidence[dim] = [f"survey option {choice_idx}: {item['choices'][choice_idx - 1]}"]

    return {
        "source": "survey",
        "scores": scores,
        "responses": responses,
        "evidence": evidence,
    }


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _git_text(args: list[str], cwd: Path) -> str:
    try:
        return _run(args, cwd=cwd).stdout.strip().lower()
    except subprocess.CalledProcessError:
        return ""


def _detect_branch_prefix_count(project_root: Path) -> int:
    txt = _git_text(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"], project_root)
    if not txt:
        return 0
    prefixes = ("feat/", "fix/", "docs/", "research/", "ops/")
    count = 0
    for line in txt.splitlines():
        if any(line.startswith(prefix) for prefix in prefixes):
            count += 1
    return count


def _project_has_tests(project_root: Path) -> bool:
    tests_dir = project_root / "tests"
    if tests_dir.exists() and tests_dir.is_dir():
        return True
    for pattern in ("test_*.py", "*_test.py", "*.spec.ts", "*.test.ts", "*.test.js"):
        try:
            if any(project_root.rglob(pattern)):
                return True
        except OSError:
            continue
    return False


def _project_has_ci(project_root: Path) -> bool:
    workflows = project_root / ".github" / "workflows"
    if not workflows.exists():
        return False
    try:
        return any(workflows.glob("*.yml")) or any(workflows.glob("*.yaml"))
    except OSError:
        return False


def _score_from_flags(flags: list[tuple[bool, str]]) -> tuple[int, list[str]]:
    score = 0
    evidence: list[str] = []
    for is_true, message in flags:
        if is_true:
            score += 1
            evidence.append(message)
    return min(3, score), evidence


def _profile_infer(project_root: Path) -> dict:
    docs_files = [
        project_root / "docs" / "REQUIREMENTS.md",
        project_root / "docs" / "PLAN.md",
        project_root / "docs" / "PROGRESS.md",
        project_root / "docs" / "NEXT_STEPS.md",
    ]
    docs_present = sum(1 for p in docs_files if p.exists())
    docs_dir_exists = (project_root / "docs").exists()
    tests_present = _project_has_tests(project_root)
    ci_present = _project_has_ci(project_root)
    branch_prefix_count = _detect_branch_prefix_count(project_root)

    commit_text = _git_text(["git", "log", "--oneline", "-n", "120"], project_root)
    agents_text = _safe_read_text(project_root / "AGENTS.md").lower()
    claude_settings_text = _safe_read_text(project_root / ".claude" / "settings.json")

    settings_has_hooks = False
    settings_has_deny = False
    if claude_settings_text:
        try:
            parsed = json.loads(claude_settings_text)
            settings_has_hooks = bool(parsed.get("hooks"))
            settings_has_deny = bool(parsed.get("permissions", {}).get("deny"))
        except json.JSONDecodeError:
            pass

    scores: dict[str, int] = {}
    evidence: dict[str, list[str]] = {}

    scores["planning_strictness"], evidence["planning_strictness"] = _score_from_flags([
        (docs_present >= 2 and (project_root / "docs" / "PLAN.md").exists() and (project_root / "docs" / "NEXT_STEPS.md").exists(), "PLAN and NEXT_STEPS detected"),
        (docs_present >= 4, "full staged docs set detected (REQUIREMENTS/PLAN/PROGRESS/NEXT_STEPS)"),
        ("plan" in commit_text or "phase" in commit_text or "milestone" in commit_text, "commit history references planning/milestones"),
    ])

    scores["risk_tolerance"], evidence["risk_tolerance"] = _score_from_flags([
        ("review gate" in agents_text or "no unattended" in agents_text or "guardrail" in agents_text, "AGENTS.md includes guardrail/review language"),
        (settings_has_deny, ".claude/settings.json contains deny permissions"),
        ("review" in commit_text or "safety" in commit_text or "guard" in commit_text, "commit history includes review/safety signals"),
    ])

    scores["testing_rigor"], evidence["testing_rigor"] = _score_from_flags([
        (tests_present, "test files/directories detected"),
        (ci_present, "CI workflow detected"),
        ("test" in commit_text or "pytest" in commit_text or "jest" in commit_text, "commit history includes test activity"),
    ])

    scores["parallelism_preference"], evidence["parallelism_preference"] = _score_from_flags([
        (branch_prefix_count >= 1, "task-style branch prefixes detected"),
        ("worktree" in agents_text or "one bounded task per worktree" in agents_text, "AGENTS.md references worktree-based parallelism"),
        (branch_prefix_count >= 3 or "worktree" in commit_text, "strong branch/worktree parallelism evidence"),
    ])

    scores["documentation_rigor"], evidence["documentation_rigor"] = _score_from_flags([
        (docs_dir_exists, "docs/ directory exists"),
        (docs_present >= 3, "3+ authoritative docs present"),
        ("docs" in commit_text or "readme" in commit_text, "commit history includes documentation changes"),
    ])

    scores["automation_level"], evidence["automation_level"] = _score_from_flags([
        (settings_has_hooks, ".claude/settings.json has hooks configured"),
        (ci_present, "CI automation detected"),
        (("hook" in commit_text or "automation" in commit_text or "checkpoint" in commit_text), "commit history includes automation/hook signals"),
    ])

    return {
        "source": "infer",
        "project_root": str(project_root),
        "scores": scores,
        "evidence": evidence,
        "signals": {
            "docs_present": docs_present,
            "tests_present": tests_present,
            "ci_present": ci_present,
            "branch_prefix_count": branch_prefix_count,
            "settings_has_hooks": settings_has_hooks,
            "settings_has_deny": settings_has_deny,
        },
    }


def _profile_hybrid(project_root: Path, answers: dict[str, int] | None = None) -> dict:
    survey = _profile_survey(answers=answers)
    inferred = _profile_infer(project_root)

    scores: dict[str, int] = {}
    evidence: dict[str, list[str]] = {}
    for dim in PROFILE_DIMENSIONS:
        s = survey["scores"][dim]
        i = inferred["scores"][dim]
        blended = int((0.6 * s + 0.4 * i) + 0.5)
        if blended < 0:
            blended = 0
        if blended > 3:
            blended = 3
        scores[dim] = blended
        evidence[dim] = [
            f"hybrid blend: survey={s}, infer={i}, weighted=0.6/0.4 => {blended}",
            *survey.get("evidence", {}).get(dim, []),
            *inferred.get("evidence", {}).get(dim, []),
        ]

    return {
        "source": "hybrid",
        "scores": scores,
        "evidence": evidence,
        "survey": survey,
        "infer": inferred,
    }


def _render_workstyle_explanations(mode: str, payload: dict) -> str:
    scores = payload.get("scores", {})
    evidence = payload.get("evidence", {})
    lines = [
        "# Workstyle Explanations",
        "",
        f"Mode: `{mode}`",
        f"Date: `{_today()}`",
        "",
        "## Score Table",
        "",
        "| Dimension | Score (0-3) |",
        "|---|---|",
    ]
    for dim in PROFILE_DIMENSIONS:
        lines.append(f"| {dim} | {scores.get(dim, 0)} |")
    lines += ["", "## Evidence", ""]
    for dim in PROFILE_DIMENSIONS:
        lines.append(f"### {dim}")
        items = evidence.get(dim, [])
        if not items:
            lines.append("- no explicit evidence captured")
        else:
            for item in items:
                lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Profile elicitation metadata (Gap B, v0.10.0-alpha)
# ---------------------------------------------------------------------------

# Days past elicitation after which the operator context is considered stale.
# Kernel defaults; overridable per-operator via the operator_profile.md field.
PROFILE_STALE_DAYS = 30

_LAST_ELICITED_RE = re.compile(
    r"^\s*(?:[-*+]\s+)?(?:_|\*|`)?\s*Last elicited\s*[:\-]\s*(?:_|\*|`)?\s*(\d{4}-\d{2}-\d{2})",
    re.IGNORECASE | re.MULTILINE,
)


def _read_last_elicited(profile_path: Path) -> date | None:
    """Parse `Last elicited: YYYY-MM-DD` out of the operator profile markdown.

    Tolerant to surrounding italics / backticks / bullet markers so
    hand-editing doesn't break detection. Returns None when absent or
    malformed — callers treat `None` as stale-unknown (still warn).
    """
    try:
        text = profile_path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = _LAST_ELICITED_RE.search(text)
    if not m:
        return None
    try:
        return date.fromisoformat(m.group(1))
    except ValueError:
        return None


def _profile_staleness(
    *,
    profile_path: Path | None = None,
    today: date | None = None,
) -> tuple[str, int | None, date | None]:
    """Return (status, age_days, elicited_on).

    status is one of:
        "missing"  — the profile file does not exist
        "unknown"  — file exists but has no parseable `Last elicited`
        "stale"    — elicited more than PROFILE_STALE_DAYS ago
        "fresh"    — elicited within the window
    """
    path = profile_path if profile_path is not None else (GLOBAL_MEMORY_DIR / "operator_profile.md")
    if not path.exists():
        return "missing", None, None
    elicited = _read_last_elicited(path)
    if elicited is None:
        return "unknown", None, None
    today = today or date.today()
    age = (today - elicited).days
    return ("stale" if age > PROFILE_STALE_DAYS else "fresh", age, elicited)


def _render_stale_profile_warning(
    status: str,
    age_days: int | None,
    elicited_on: date | None,
) -> str | None:
    """Render a visible warning block for the synced CLAUDE.md header.

    Returns None when no warning is required (fresh within 30d window).
    """
    if status == "fresh":
        return None
    lines: list[str] = [
        "",
        "> **⚠️ Stale Context Warning — Operator Profile**",
        ">",
    ]
    if status == "stale" and age_days is not None and elicited_on is not None:
        lines.append(
            f"> The operator profile was last elicited on **{elicited_on.isoformat()}** — "
            f"**{age_days} days ago**, past the {PROFILE_STALE_DAYS}-day freshness window."
        )
    elif status == "unknown":
        lines.append(
            "> The operator profile exists but declares no `Last elicited:` date. "
            "Treat preferences as provisional until refreshed."
        )
    elif status == "missing":
        lines.append(
            "> No operator profile found. Running without encoded preferences; "
            "behavior falls back to kernel defaults."
        )
    lines += [
        ">",
        "> Priorities, workflow policies, and risk tolerances drift. Before taking "
        "a high-impact action this session, confirm the posture below still matches the operator's current intent — "
        "or refresh it with `episteme profile hybrid --write`.",
        "",
    ]
    return "\n".join(lines)


def _compile_operator_profile(scores: dict[str, int], mode: str) -> str:
    planning = scores.get("planning_strictness", 0)
    risk = scores.get("risk_tolerance", 0)
    testing = scores.get("testing_rigor", 0)
    parallel = scores.get("parallelism_preference", 0)
    docs = scores.get("documentation_rigor", 0)
    automation = scores.get("automation_level", 0)

    return "\n".join([
        "# Operator Profile",
        "",
        f"Generated by `episteme profile {mode}` on {_today()}.",
        f"Last elicited: {_today()}",
        "This file captures deterministic working-style preferences for cross-tool runtime behavior.",
        "",
        "## Deterministic Workstyle Scorecard (0-3)",
        "",
        f"- planning_strictness: {planning}",
        f"- risk_tolerance: {risk}",
        f"- testing_rigor: {testing}",
        f"- parallelism_preference: {parallel}",
        f"- documentation_rigor: {docs}",
        f"- automation_level: {automation}",
        "",
        "## Working Style Summary",
        "",
        f"- Planning posture: {'strict staged planning' if planning >= 3 else 'structured planning' if planning >= 2 else 'light planning' if planning >= 1 else 'implementation-first'}.",
        f"- Risk posture: {'highly conservative with strong guardrails' if risk >= 3 else 'conservative default' if risk >= 2 else 'balanced speed/caution' if risk >= 1 else 'speed-prioritized'}.",
        f"- Testing posture: {'completion-blocking quality checks preferred' if testing >= 3 else 'strong test validation before completion' if testing >= 2 else 'targeted test checks' if testing >= 1 else 'minimal smoke validation'}.",
        f"- Parallelism posture: {'structured multi-lane worktree execution' if parallel >= 3 else 'bounded parallel lanes when useful' if parallel >= 2 else 'occasional parallel work' if parallel >= 1 else 'single-lane execution preference'}.",
        f"- Documentation posture: {'docs-first operating contract each session' if docs >= 3 else 'consistent authoritative docs maintenance' if docs >= 2 else 'milestone-level docs updates' if docs >= 1 else 'minimal documentation'}.",
        f"- Automation posture: {'comprehensive deterministic automation with guardrails' if automation >= 3 else 'high automation for quality/consistency' if automation >= 2 else 'basic helper automation' if automation >= 1 else 'manual-first operations'}.",
        "",
    ])


def _compile_workflow_policy(scores: dict[str, int], mode: str) -> str:
    planning = scores.get("planning_strictness", 0)
    risk = scores.get("risk_tolerance", 0)
    testing = scores.get("testing_rigor", 0)
    parallel = scores.get("parallelism_preference", 0)
    docs = scores.get("documentation_rigor", 0)
    automation = scores.get("automation_level", 0)

    flow = ["Explore", "Deconstruct (Reasoning Surface)", "Plan", "Falsify (Devil's Advocate)", "Implement", "Review", "Handoff"]
    if planning >= 2:
        flow.insert(3, "Validate plan against first-principles")

    lines = [
        "# Workflow Policy",
        "",
        f"Generated by `episteme profile {mode}` on {_today()}.",
        "Deterministic policy compiled from the workstyle scorecard.",
        "",
        "## Standard Flow",
    ]
    for i, step in enumerate(flow, start=1):
        lines.append(f"{i}. {step}")

    lines += [
        "",
        "## Reasoning Standards",
        "- **Divide and Conquer**: Structure chaotic info into clear distinctions.",
        "- **Known vs Unknown**: Explicitly list what is verified vs. assumed in every plan.",
        "- **Skepticism**: Seek reasons behind actions; do not accept heuristics at face value.",
        "- **Check-ins**: Perform lightweight reasoning check-ins during substantial problem-solving.",
        "",
        "## Project Memory",
        "- Authoritative project truth lives in `docs/` and `AGENTS.md`.",
        "- Tool-native memory is acceleration only, not source of truth.",
        "",
        "## Planning Policy",
    ]
    if planning >= 3:
        lines += [
            "- Require staged plan updates in `docs/PLAN.md` before major implementation.",
            "- Large tasks should be decomposed into bounded steps before execution.",
        ]
    elif planning >= 2:
        lines += ["- Keep staged execution notes in `docs/PLAN.md` for non-trivial work."]
    elif planning >= 1:
        lines += ["- Maintain at least a short plan/checklist before substantial edits."]
    else:
        lines += ["- Planning is lightweight; prefer fast iteration with explicit checkpoints."]

    lines += ["", "## Risk and Safety Policy"]
    if risk >= 3:
        lines += [
            "- Use strict guardrails and review gates for risky changes.",
            "- Avoid destructive operations without explicit confirmation.",
        ]
    elif risk >= 2:
        lines += ["- Conservative default: review critical changes before merge."]
    elif risk >= 1:
        lines += ["- Balanced posture: apply guardrails to high-impact operations."]
    else:
        lines += ["- Speed-first posture; still preserve baseline destructive-command protections."]

    lines += ["", "## Testing Policy"]
    if testing >= 3:
        lines += ["- Block completion when required tests fail."]
    elif testing >= 2:
        lines += ["- Run comprehensive relevant tests before completion."]
    elif testing >= 1:
        lines += ["- Run targeted smoke tests for changed areas."]
    else:
        lines += ["- Use minimal validation for rapid iteration."]

    lines += ["", "## Parallel Work Policy"]
    if parallel >= 3:
        lines += ["- Prefer bounded task parallelism via worktrees with one owner per lane."]
    elif parallel >= 2:
        lines += ["- Use parallel lanes for independent bounded tasks."]
    elif parallel >= 1:
        lines += ["- Use parallel work occasionally when risk is low and ownership is clear."]
    else:
        lines += ["- Prefer single active lane to reduce coordination overhead."]

    lines += ["", "## Documentation Policy"]
    if docs >= 3:
        lines += ["- Treat docs updates (`PLAN`, `PROGRESS`, `NEXT_STEPS`) as mandatory every substantial session."]
    elif docs >= 2:
        lines += ["- Keep authoritative docs consistently updated through milestones."]
    elif docs >= 1:
        lines += ["- Update docs at major checkpoints."]
    else:
        lines += ["- Keep concise docs; expand only when complexity grows."]

    lines += ["", "## Automation Policy"]
    if automation >= 3:
        lines += ["- Enable comprehensive deterministic automation with strict guardrails."]
    elif automation >= 2:
        lines += ["- Use strong automation for formatting, testing, and quality checks."]
    elif automation >= 1:
        lines += ["- Use basic helper automation while keeping critical decisions manual."]
    else:
        lines += ["- Prefer manual control and minimal automation."]

    lines += [
        "",
        "## Local Integration",
        "After updating global memory files, run:",
        "1. `episteme sync`",
        "2. `episteme doctor`",
        "",
    ]
    return "\n".join(lines)


def _write_workstyle_artifacts(mode: str, payload: dict) -> tuple[Path, Path, Path]:
    GENERATED_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    profile_path = GENERATED_PROFILE_DIR / "workstyle_profile.json"
    scores_path = GENERATED_PROFILE_DIR / "workstyle_scores.json"
    explain_path = GENERATED_PROFILE_DIR / "workstyle_explanations.md"

    profile_payload = {
        "mode": mode,
        "generated_on": _today(),
        "last_elicited": _today(),
        **payload,
    }
    score_payload = {
        "mode": mode,
        "generated_on": _today(),
        "last_elicited": _today(),
        "scores": payload.get("scores", {}),
    }

    _write_text(profile_path, json.dumps(profile_payload, indent=2) + "\n")
    _write_text(scores_path, json.dumps(score_payload, indent=2) + "\n")
    _write_text(explain_path, _render_workstyle_explanations(mode, payload) + "\n")
    return profile_path, scores_path, explain_path


def _write_compiled_memory(mode: str, payload: dict, *, overwrite: bool) -> None:
    scores = payload.get("scores", {})
    operator_path = GLOBAL_MEMORY_DIR / "operator_profile.md"
    workflow_path = GLOBAL_MEMORY_DIR / "workflow_policy.md"

    compiled_operator = _compile_operator_profile(scores, mode)
    compiled_workflow = _compile_workflow_policy(scores, mode)

    for target, content in ((operator_path, compiled_operator), (workflow_path, compiled_workflow)):
        if target.exists() and not overwrite:
            print(f"Skipped existing file (use --overwrite): {target}")
            continue
        _write_text(target, content + ("" if content.endswith("\n") else "\n"))
        print(f"Wrote: {target}")


def _print_profile_summary(mode: str, payload: dict) -> None:
    scores = payload.get("scores", {})
    print()
    print(f"Workstyle profile summary ({mode})")
    for dim in PROFILE_DIMENSIONS:
        print(f"  - {dim:<24} {scores.get(dim, 0)}")

    evidence = payload.get("evidence", {})
    print()
    print("Key evidence:")
    for dim in PROFILE_DIMENSIONS:
        dim_evidence = evidence.get(dim, [])
        if dim_evidence:
            print(f"  {dim}: {dim_evidence[0]}")


def _profile_audit_cli(*, since: str, write: bool, as_json: bool) -> int:
    """CLI entry for `episteme profile audit` (phase 12).

    Spec: docs/DESIGN_V0_11_PHASE_12.md.
    Library: src/episteme/_profile_audit.py (D2 retrospective-only,
    D3 re-elicitation not correction).
    """
    from episteme import _profile_audit

    m = re.match(r"^(\d+)d$", since)
    if not m:
        print(f"invalid --since value: {since!r} (expected e.g. '30d')", file=sys.stderr)
        return 1
    since_days = int(m.group(1))
    if since_days <= 0:
        print(f"--since must be a positive number of days; got {since_days}", file=sys.stderr)
        return 1

    result = _profile_audit.run_audit(since_days=since_days)

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(_profile_audit.render_text_report(result))

    if write:
        path = _profile_audit.write_audit_record(result)
        print(f"Wrote audit record: {path}", file=sys.stderr)

    return 0


def _profile_audit_ack_cli(args) -> int:
    """CLI entry for `episteme profile audit ack` (CP-AUDIT-ACK-01 / Event 78).

    Three modes dispatched by args:
    - `--list`: enumerate outstanding (un-acked) audit IDs with drift.
    - `--revoke <audit-id> --rationale "..."`: revoke a prior ack
      (audit-trail preserved; revoke appends a new chain entry).
    - `<audit-id> --rationale "..."`: ack the audit ID with rationale.

    Library: src/episteme/_profile_audit_ack.py (hash-chained ack-store
    at ~/.episteme/state/profile_audit_acks.jsonl).
    """
    from episteme import _profile_audit_ack as ack_mod

    if getattr(args, "list_outstanding", False):
        outstanding = ack_mod.list_outstanding_audits()
        if not outstanding:
            print("No outstanding (un-acked) profile-audit drift records.")
            return 0
        print(f"Outstanding profile-audit drift records ({len(outstanding)}):")
        print()
        for entry in outstanding:
            run_id = entry.get("run_id", "?")
            run_ts = entry.get("run_ts", "?")
            axes = entry.get("drift_axes") or []
            axes_str = ", ".join(axes) if axes else "(no drift axes named)"
            print(f"  {run_id}")
            print(f"    run_ts:      {run_ts}")
            print(f"    drift_axes:  {axes_str}")
            print(f"    ack via:     episteme profile audit ack {run_id} --rationale \"...\"")
            print()
        return 0

    audit_id = getattr(args, "audit_id", None)
    rationale = getattr(args, "rationale", None)
    revoke = getattr(args, "revoke", False)
    evidence_refs = getattr(args, "evidence_refs", None) or []

    if not audit_id:
        print(
            "audit_id is required (or pass --list to enumerate outstanding records).",
            file=sys.stderr,
        )
        return 2
    if not rationale:
        print(
            "--rationale is required (min 15 chars; lazy tokens like 'n/a' / 'tbd' rejected).",
            file=sys.stderr,
        )
        return 2

    try:
        if revoke:
            envelope = ack_mod.write_revoke(audit_id, rationale)
            print(f"Revoked ack for {audit_id}.")
        else:
            envelope = ack_mod.write_ack(
                audit_id,
                rationale,
                evidence_refs=evidence_refs,
            )
            print(f"Acked {audit_id}.")
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"  entry_hash: {envelope['entry_hash']}")
    print(f"  acker:      {envelope['payload'].get('acker', 'unknown')}")
    if evidence_refs:
        print(f"  evidence:   {', '.join(evidence_refs)}")
    return 0


def _profile_show() -> int:
    scores_path = GENERATED_PROFILE_DIR / "workstyle_scores.json"
    profile_path = GENERATED_PROFILE_DIR / "workstyle_profile.json"
    explain_path = GENERATED_PROFILE_DIR / "workstyle_explanations.md"

    if not scores_path.exists():
        print("No generated workstyle profile found.")
        print("Run: episteme profile survey --write")
        return 1

    try:
        data = json.loads(scores_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"Could not parse: {scores_path}", file=sys.stderr)
        return 1

    print(f"Mode: {data.get('mode', 'unknown')}")
    print(f"Generated: {data.get('generated_on', 'unknown')}")
    print()
    for dim in PROFILE_DIMENSIONS:
        print(f"  - {dim:<24} {data.get('scores', {}).get(dim, 0)}")
    print()
    print("Artifacts:")
    print(f"  - {profile_path}")
    print(f"  - {scores_path}")
    print(f"  - {explain_path}")
    return 0


COGNITIVE_DIMENSIONS = [
    "first_principles_depth",
    "exploration_breadth",
    "speed_vs_rigor_balance",
    "challenge_orientation",
    "uncertainty_tolerance",
    "autonomy_preference",
]


def _cognition_questions() -> list[dict]:
    return [
        {
            "dimension": "first_principles_depth",
            "question": (
                "A bug appears in a system you built 6 months ago. How do you approach the diagnosis?\n"
                "  (This reveals whether you think top-down or bottom-up.)"
            ),
            "choices": [
                "Try the obvious fix first — if it works, ship it.",
                "Scan logs and recent changes; trace backward from the symptom.",
                "Map the system's assumptions before touching anything, then verify which one broke.",
                "Decompose the full causal chain from first principles; treat surface symptoms as hypotheses, not facts.",
            ],
        },
        {
            "dimension": "exploration_breadth",
            "question": (
                "You need to choose a technical approach. You have one strong intuition. What do you do?\n"
                "  (This reveals your epistemic discipline around option space.)"
            ),
            "choices": [
                "Trust the intuition and move — deliberation is overrated.",
                "Quickly sanity-check one alternative before committing.",
                "Evaluate 2-3 plausible options with explicit trade-off notes.",
                "Map the full option space, score alternatives on shared criteria, then decide.",
            ],
        },
        {
            "dimension": "speed_vs_rigor_balance",
            "question": (
                "You're under deadline pressure and the analysis isn't complete. What governs the call?\n"
                "  (This reveals your default when speed and rigor are in conflict.)"
            ),
            "choices": [
                "Ship the best available option — perfect is the enemy of done.",
                "Ship with a noted caveat; clean it up in the next sprint.",
                "Delay if key unknowns are unresolved; partial rigor isn't rigor.",
                "Rigorous by default; deadline pressure is a reason to ask for more time, not cut corners.",
            ],
        },
        {
            "dimension": "challenge_orientation",
            "question": (
                "You present a plan. A teammate pushes back hard. How do you want the system to behave?\n"
                "  (This reveals how much you value adversarial stress-testing of your own ideas.)"
            ),
            "choices": [
                "Protect the plan's momentum — debate slows things down.",
                "Acknowledge the pushback and address it briefly, then continue.",
                "Treat pushback as valuable signal; steelman the critique before defending.",
                "Actively solicit devil's advocate challenges before committing to any plan.",
            ],
        },
        {
            "dimension": "uncertainty_tolerance",
            "question": (
                "You're asked to give an estimate for something you've never done before. What's your approach?\n"
                "  (This reveals your epistemic honesty about what you don't know.)"
            ),
            "choices": [
                "Give a number confidently — uncertainty is someone else's problem to manage.",
                "Give a range, but don't belabor the unknowns.",
                "State key assumptions explicitly alongside the estimate.",
                "Require explicit uncertainty quantification: confidence interval, named assumptions, and disconfirmation criteria.",
            ],
        },
        {
            "dimension": "autonomy_preference",
            "question": (
                "An agent has been given a task and hits an ambiguous decision point mid-execution. What should it do?\n"
                "  (This reveals your philosophy on agent autonomy vs. human oversight.)"
            ),
            "choices": [
                "Make the best call and move on — I'll review the result.",
                "Proceed with a logged assumption and surface it in the summary.",
                "Pause and present the decision point with a recommendation before acting.",
                "Full stop: surface the ambiguity, require explicit resolution before any action.",
            ],
        },
    ]


def _cognition_survey(answers: dict[str, int] | None = None) -> dict:
    print("Deterministic cognitive-style survey")
    print("Answer each question with 1..4. Higher values represent stronger structured cognitive posture.")

    normalized_answers = _normalize_answers(answers or {})

    responses: dict[str, dict] = {}
    scores: dict[str, int] = {}
    evidence: dict[str, list[str]] = {}

    for item in _cognition_questions():
        dim = item["dimension"]
        if dim in normalized_answers:
            choice_idx = normalized_answers[dim]
            print(f"[answers-file] {dim}: selected option {choice_idx}")
        else:
            choice_idx = _prompt_choice(item["question"], item["choices"])
        score = choice_idx - 1
        responses[dim] = {
            "question": item["question"],
            "selected_option": choice_idx,
            "selected_text": item["choices"][choice_idx - 1],
            "score": score,
        }
        scores[dim] = score
        evidence[dim] = [f"survey option {choice_idx}: {item['choices'][choice_idx - 1]}"]

    return {
        "source": "cognitive_survey",
        "scores": scores,
        "responses": responses,
        "evidence": evidence,
    }


def _render_cognitive_explanations(payload: dict) -> str:
    scores = payload.get("scores", {})
    evidence = payload.get("evidence", {})
    lines = [
        "# Cognitive Profile Explanations",
        "",
        f"Date: `{_today()}`",
        "",
        "## Score Table",
        "",
        "| Dimension | Score (0-3) |",
        "|---|---|",
    ]
    for dim in COGNITIVE_DIMENSIONS:
        lines.append(f"| {dim} | {scores.get(dim, 0)} |")
    lines += ["", "## Evidence", ""]
    for dim in COGNITIVE_DIMENSIONS:
        lines.append(f"### {dim}")
        items = evidence.get(dim, [])
        if not items:
            lines.append("- no explicit evidence captured")
        else:
            for item in items:
                lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)


def _compile_cognitive_profile(scores: dict[str, int], mode: str) -> str:
    fpd = scores.get("first_principles_depth", 0)
    exp = scores.get("exploration_breadth", 0)
    svr = scores.get("speed_vs_rigor_balance", 0)
    cho = scores.get("challenge_orientation", 0)
    unt = scores.get("uncertainty_tolerance", 0)
    aut = scores.get("autonomy_preference", 0)

    return "\n".join([
        "# Cognitive Profile",
        "",
        f"Generated by `episteme cognition {mode}` on {_today()}.",
        "Deterministic cognitive and philosophical operating profile.",
        "",
        "## Cognitive Scorecard (0-3)",
        f"- first_principles_depth: {fpd}",
        f"- exploration_breadth: {exp}",
        f"- speed_vs_rigor_balance: {svr}",
        f"- challenge_orientation: {cho}",
        f"- uncertainty_tolerance: {unt}",
        f"- autonomy_preference: {aut}",
        "",
        "## Philosophy of Work",
        f"- Reasoning depth posture: {'first-principles dominant' if fpd >= 3 else 'frequent first-principles decomposition' if fpd >= 2 else 'balanced decomposition/heuristics' if fpd >= 1 else 'heuristic-first'}.",
        f"- Option strategy: {'broad exploratory option search' if exp >= 3 else 'multi-option evaluation' if exp >= 2 else 'few-option comparison' if exp >= 1 else 'single viable path bias'}.",
        f"- Speed-rigor balance: {'rigor-first' if svr >= 3 else 'balanced with rigor lean' if svr >= 2 else 'speed-lean with checks' if svr >= 1 else 'speed-first'}.",
        "",
        "## Decision Attitude",
        f"- Challenge style: {'strong adversarial stress-testing' if cho >= 3 else 'structured critique encouraged' if cho >= 2 else 'moderate challenge when important' if cho >= 1 else 'low-friction consensus style'}.",
        f"- Uncertainty handling: {'explicit uncertainty + failure-mode analysis required' if unt >= 3 else 'explicit assumptions/confidence expected' if unt >= 2 else 'light assumption framing' if unt >= 1 else 'low-friction proceed posture'}.",
        f"- Autonomy posture: {'high autonomy with strict deterministic bounds' if aut >= 3 else 'high bounded autonomy' if aut >= 2 else 'moderate autonomy with checkpoints' if aut >= 1 else 'human-in-the-loop dominant'}.",
        "",
    ])


def _write_cognitive_artifacts(mode: str, payload: dict) -> tuple[Path, Path]:
    GENERATED_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    profile_path = GENERATED_PROFILE_DIR / "cognitive_profile.json"
    explain_path = GENERATED_PROFILE_DIR / "cognitive_explanations.md"

    packed = {
        "mode": mode,
        "generated_on": _today(),
        **payload,
    }
    _write_text(profile_path, json.dumps(packed, indent=2) + "\n")
    _write_text(explain_path, _render_cognitive_explanations(payload) + "\n")
    return profile_path, explain_path


def _cognition_infer(project_root: Path) -> dict:
    docs_files = [
        project_root / "docs" / "REQUIREMENTS.md",
        project_root / "docs" / "PLAN.md",
        project_root / "docs" / "PROGRESS.md",
        project_root / "docs" / "NEXT_STEPS.md",
    ]
    docs_present = sum(1 for p in docs_files if p.exists())
    docs_dir_exists = (project_root / "docs").exists()
    ci_present = _project_has_ci(project_root)

    commit_text = _git_text(["git", "log", "--oneline", "-n", "120"], project_root)
    branch_text = _git_text(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"], project_root)
    agents_text = _safe_read_text(project_root / "AGENTS.md").lower()
    plan_text = _safe_read_text(project_root / "docs" / "PLAN.md").lower()
    req_text = _safe_read_text(project_root / "docs" / "REQUIREMENTS.md").lower()
    settings_text = _safe_read_text(project_root / ".claude" / "settings.json")

    settings_has_hooks = False
    settings_has_deny = False
    if settings_text:
        try:
            parsed = json.loads(settings_text)
            settings_has_hooks = bool(parsed.get("hooks"))
            settings_has_deny = bool(parsed.get("permissions", {}).get("deny"))
        except json.JSONDecodeError:
            pass

    manifest_text = _safe_read_text(REPO_ROOT / "core" / "runtime_manifest.json").lower()

    scores: dict[str, int] = {}
    evidence: dict[str, list[str]] = {}

    scores["first_principles_depth"], evidence["first_principles_depth"] = _score_from_flags([
        ("assumption" in agents_text or "first-principles" in agents_text, "AGENTS.md references assumptions/first-principles reasoning"),
        ("root cause" in commit_text or "analysis" in commit_text or "rationale" in commit_text, "commit history references analytical decomposition"),
        ("why" in plan_text or "assumption" in plan_text, "PLAN.md contains rationale/assumption language"),
    ])

    scores["exploration_breadth"], evidence["exploration_breadth"] = _score_from_flags([
        ("option" in plan_text or "alternative" in plan_text, "PLAN.md references options/alternatives"),
        ("research/" in branch_text, "research branch prefix detected"),
        ("explore" in agents_text or "research" in agents_text, "AGENTS.md references exploration workflow"),
    ])

    scores["speed_vs_rigor_balance"], evidence["speed_vs_rigor_balance"] = _score_from_flags([
        (docs_present >= 3 and ci_present, "docs discipline + CI suggests balanced rigor"),
        ("review" in commit_text or "validate" in commit_text, "commit history includes validation/review language"),
        ("smallest useful verification" in agents_text or "review gate" in agents_text, "AGENTS.md includes verification controls"),
    ])

    scores["challenge_orientation"], evidence["challenge_orientation"] = _score_from_flags([
        ("review gate" in agents_text or "review required" in agents_text, "AGENTS.md requires review gates"),
        ("swing-review" in manifest_text, "runtime manifest includes adversarial review skill"),
        ("review" in commit_text or "critique" in commit_text, "commit history includes review-oriented activity"),
    ])

    scores["uncertainty_tolerance"], evidence["uncertainty_tolerance"] = _score_from_flags([
        ("constraint" in plan_text or "risk" in plan_text, "PLAN.md includes constraints/risks"),
        ("non-goal" in req_text, "REQUIREMENTS.md includes explicit non-goals"),
        (docs_dir_exists, "docs discipline suggests explicit uncertainty handling"),
    ])

    scores["autonomy_preference"], evidence["autonomy_preference"] = _score_from_flags([
        (settings_has_hooks, "tool hooks configured (bounded automation)"),
        ("bounded" in agents_text or "human review checkpoint" in agents_text, "AGENTS.md uses bounded automation language"),
        (settings_has_deny or ci_present, "guardrails/CI indicate controlled autonomy"),
    ])

    return {
        "source": "cognitive_infer",
        "project_root": str(project_root),
        "scores": scores,
        "evidence": evidence,
        "signals": {
            "docs_present": docs_present,
            "docs_dir_exists": docs_dir_exists,
            "ci_present": ci_present,
            "settings_has_hooks": settings_has_hooks,
            "settings_has_deny": settings_has_deny,
        },
    }


def _cognition_hybrid(project_root: Path, answers: dict[str, int] | None = None) -> dict:
    survey = _cognition_survey(answers=answers)
    inferred = _cognition_infer(project_root)

    scores: dict[str, int] = {}
    evidence: dict[str, list[str]] = {}
    for dim in COGNITIVE_DIMENSIONS:
        s = survey["scores"][dim]
        i = inferred["scores"][dim]
        blended = int((0.6 * s + 0.4 * i) + 0.5)
        blended = max(0, min(3, blended))
        scores[dim] = blended
        evidence[dim] = [
            f"hybrid blend: survey={s}, infer={i}, weighted=0.6/0.4 => {blended}",
            *survey.get("evidence", {}).get(dim, []),
            *inferred.get("evidence", {}).get(dim, []),
        ]

    return {
        "source": "cognitive_hybrid",
        "scores": scores,
        "evidence": evidence,
        "survey": survey,
        "infer": inferred,
    }


def _cognition_show() -> int:
    profile_path = GENERATED_PROFILE_DIR / "cognitive_profile.json"
    explain_path = GENERATED_PROFILE_DIR / "cognitive_explanations.md"
    if not profile_path.exists():
        print("No generated cognitive profile found.")
        print("Run: episteme cognition survey --write")
        return 1
    try:
        data = json.loads(profile_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"Could not parse: {profile_path}", file=sys.stderr)
        return 1

    print(f"Generated: {data.get('generated_on', 'unknown')}")
    print()
    for dim in COGNITIVE_DIMENSIONS:
        print(f"  - {dim:<24} {data.get('scores', {}).get(dim, 0)}")
    print()
    print("Artifacts:")
    print(f"  - {profile_path}")
    print(f"  - {explain_path}")
    return 0


def _cognition_command(
    action: str,
    path_arg: str | None,
    *,
    write: bool,
    overwrite: bool,
    answers: dict[str, int] | None = None,
) -> int:
    if action == "show":
        return _cognition_show()

    project_root = _resolve_bootstrap_target(path_arg or ".")

    if action == "survey":
        payload = _cognition_survey(answers=answers)
        mode = "survey"
    elif action == "infer":
        payload = _cognition_infer(project_root)
        mode = "infer"
    elif action == "hybrid":
        payload = _cognition_hybrid(project_root, answers=answers)
        mode = "hybrid"
    else:
        print(f"Unsupported cognition action: {action}", file=sys.stderr)
        return 1

    profile_path, explain_path = _write_cognitive_artifacts(mode, payload)

    print()
    print(f"Cognitive profile summary ({mode})")
    for dim in COGNITIVE_DIMENSIONS:
        print(f"  - {dim:<24} {payload.get('scores', {}).get(dim, 0)}")

    print()
    print("Wrote generated artifacts:")
    print(f"  - {profile_path}")
    print(f"  - {explain_path}")

    if write:
        target = GLOBAL_MEMORY_DIR / "cognitive_profile.md"
        content = _compile_cognitive_profile(payload.get("scores", {}), mode)
        if target.exists() and not overwrite:
            print(f"Skipped existing file (use --overwrite): {target}")
        else:
            _write_text(target, content + ("" if content.endswith("\n") else "\n"))
            print(f"Wrote: {target}")
        print()
        print("Next steps for local integration:")
        print("  1) episteme sync")
        print("  2) episteme doctor")
    else:
        print()
        print("Run with --write to compile cognitive profile into global memory markdown.")

    return 0


def _profile_command(
    mode: str,
    path_arg: str | None,
    *,
    write: bool,
    overwrite: bool,
    answers: dict[str, int] | None = None,
) -> int:
    project_root = _resolve_bootstrap_target(path_arg or ".")

    if mode == "survey":
        payload = _profile_survey(answers=answers)
    elif mode == "infer":
        payload = _profile_infer(project_root)
    elif mode == "hybrid":
        payload = _profile_hybrid(project_root, answers=answers)
    elif mode == "gap":
        payload = _profile_gap_survey(project_root, answers=answers)
    else:
        print(f"Unsupported profile mode: {mode}", file=sys.stderr)
        return 1

    profile_path, scores_path, explain_path = _write_workstyle_artifacts(mode, payload)
    _print_profile_summary(mode, payload)
    print()
    print("Wrote generated artifacts:")
    print(f"  - {profile_path}")
    print(f"  - {scores_path}")
    print(f"  - {explain_path}")

    if write:
        print()
        _write_compiled_memory(mode, payload, overwrite=overwrite)
        print()
        print("Next steps for local integration:")
        print("  1) episteme sync")
        print("  2) episteme doctor")
    else:
        print()
        print("Run with --write to compile scores into global memory markdown files.")

    return 0


def _prompt_yes_no(question: str, *, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        raw = input(f"{question} {suffix}: ").strip().lower()
        if not raw:
            return default
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("Please answer y or n.")


def _setup_mode_prompt(label: str) -> str:
    choice = _prompt_choice(
        f"Select {label} setup mode:",
        [
            "survey (explicit questionnaire)",
            "infer (derive from repository signals)",
            "hybrid (survey + infer)",
            "skip",
        ],
    )
    return ["survey", "infer", "hybrid", "skip"][choice - 1]


def _has_complete_answers(answers: dict[str, int] | None, required_dimensions: list[str]) -> bool:
    normalized = _normalize_answers(answers or {})
    return all(dim in normalized for dim in required_dimensions)


def _setup_command(
    *,
    path_arg: str,
    profile_mode: str | None,
    cognition_mode: str | None,
    governance_mode: str,
    write: bool,
    overwrite: bool,
    do_sync: bool,
    do_doctor: bool,
    profile_answers: dict[str, int] | None,
    cognition_answers: dict[str, int] | None,
    interactive: bool,
) -> int:
    governance_mode = (governance_mode or "balanced").strip().lower()
    if governance_mode not in {"minimal", "balanced", "strict"}:
        print(f"Unsupported governance pack: {governance_mode}", file=sys.stderr)
        return 1

    if interactive:
        print("🧭 episteme setup")
        print("Configure execution (workstyle) + thinking (cognition) defaults — your agent's soul.")
        print()
        if profile_mode is None and cognition_mode is None:
            questionnaire_first = _prompt_yes_no("Use questionnaire onboarding now?", default=True)
            if questionnaire_first:
                profile_mode = "survey"
                cognition_mode = "survey"
            else:
                profile_mode = _setup_mode_prompt("workstyle profile")
                cognition_mode = _setup_mode_prompt("cognitive profile")
        else:
            profile_mode = profile_mode or "survey"
            cognition_mode = cognition_mode or "survey"

        write = _prompt_yes_no("Write memory files now?", default=True)
        overwrite = _prompt_yes_no("Allow overwrite of existing memory files?", default=False) if write else False
        do_sync = _prompt_yes_no("Run episteme sync now?", default=True)
        do_doctor = _prompt_yes_no("Run episteme doctor now?", default=True)

    if profile_mode is None:
        profile_mode = "infer"
    if cognition_mode is None:
        cognition_mode = "infer"

    if profile_mode not in {"survey", "infer", "hybrid", "skip"}:
        print(f"Unsupported setup profile mode: {profile_mode}", file=sys.stderr)
        return 1
    if cognition_mode not in {"survey", "infer", "hybrid", "skip"}:
        print(f"Unsupported setup cognition mode: {cognition_mode}", file=sys.stderr)
        return 1

    if profile_mode == "skip" and cognition_mode == "skip":
        print("Nothing selected (both profile and cognition are skip).")
        return 0

    if not interactive:
        if profile_mode in {"survey", "hybrid"} and not _has_complete_answers(profile_answers, PROFILE_DIMENSIONS):
            print(
                "setup profile mode requires complete answers in non-interactive mode. "
                "Provide --profile-answers-file (or --answers-file) with all profile dimensions, "
                "or use --profile-mode infer.",
                file=sys.stderr,
            )
            return 1
        if cognition_mode in {"survey", "hybrid"} and not _has_complete_answers(cognition_answers, COGNITIVE_DIMENSIONS):
            print(
                "setup cognition mode requires complete answers in non-interactive mode. "
                "Provide --cognition-answers-file (or --answers-file) with all cognitive dimensions, "
                "or use --cognition-mode infer.",
                file=sys.stderr,
            )
            return 1

    path = _resolve_bootstrap_target(path_arg or ".")

    print()
    print(f"Setup target: {path}")
    print(
        f"Defaults: profile_mode={profile_mode}, cognition_mode={cognition_mode}, "
        f"governance_pack={governance_mode}, write={write}, overwrite={overwrite}, sync={do_sync}, doctor={do_doctor}"
    )
    if profile_mode != "skip":
        print(f"- Running profile {profile_mode}")
        rc = _profile_command(profile_mode, str(path), write=write, overwrite=overwrite, answers=profile_answers)
        if rc != 0:
            return rc
    else:
        print("- Skipping profile setup")

    if cognition_mode != "skip":
        print(f"- Running cognition {cognition_mode}")
        rc = _cognition_command(cognition_mode, str(path), write=write, overwrite=overwrite, answers=cognition_answers)
        if rc != 0:
            return rc
    else:
        print("- Skipping cognition setup")

    _write_personalization_blueprint(path)

    if do_sync:
        print()
        _sync_user_runtime(governance_mode)
    if do_doctor:
        print()
        rc = _doctor()
        if rc != 0:
            return rc

    print()
    print("─" * 60)
    print("  setup summary")
    print("─" * 60)
    print(f"  target          : {path}")
    print(f"  profile mode    : {profile_mode}")
    print(f"  cognition mode  : {cognition_mode}")
    print(f"  governance pack : {governance_mode}")
    print(f"  wrote memory    : {'yes' if write else 'no'}")
    print(f"  overwrite       : {'yes' if overwrite else 'no'}")
    print(f"  ran sync        : {'yes' if do_sync else 'no'}")
    print(f"  ran doctor      : {'yes' if do_doctor else 'no'}")
    print()
    print("✅ setup complete — profile and cognition are configured.")
    print()
    print("Next:")
    if not do_sync:
        print("  • `episteme sync`   propagate memory into Claude Code + Hermes")
    if not do_doctor:
        print("  • `episteme doctor` verify runtime wiring")
    print("  • `episteme bootstrap .` to scaffold a project, then `episteme start claude`")
    return 0


# ---------------------------------------------------------------------------
# bootstrap / new-project
# ---------------------------------------------------------------------------

def _bootstrap_project(project_root: Path, *, harness_name: str | None = None) -> None:
    project_root.mkdir(parents=True, exist_ok=True)
    mapping = _machine_context()
    mapping["PROJECT_ROOT"] = str(project_root)

    template_files = [
        "AGENTS.md",
        "CLAUDE.md",
        "docs/REQUIREMENTS.md",
        "docs/PLAN.md",
        "docs/PROGRESS.md",
        "docs/RUN_CONTEXT.md",
        "docs/NEXT_STEPS.md",
        ".claude/settings.json",
    ]
    created: list[str] = []
    preserved: list[str] = []
    for rel_path in template_files:
        target = project_root / rel_path
        if target.exists():
            preserved.append(rel_path)
            continue
        content = _replace_tokens(_load_template(rel_path), mapping)
        _write_text(target, content)
        created.append(rel_path)

    settings_local = project_root / ".claude" / "settings.local.json"
    if not settings_local.exists():
        _write_text(settings_local, "{}\n")
        created.append(".claude/settings.local.json")

    gitignore_path = project_root / ".gitignore"
    ignore_line = ".claude/settings.local.json"
    if gitignore_path.exists():
        current = gitignore_path.read_text(encoding="utf-8")
        if ignore_line not in current.splitlines():
            extra = current + ("\n" if not current.endswith("\n") else "") + ignore_line + "\n"
            _write_text(gitignore_path, extra)
    else:
        _write_text(gitignore_path, ignore_line + "\n")
        created.append(".gitignore")

    print(f"Bootstrapped project scaffold in {project_root}")
    if created:
        print("\nCreated:")
        for item in created:
            print(f"  - {item}")
    if preserved:
        print("\nPreserved existing:")
        for item in preserved:
            print(f"  - {item}")

    # Harness: auto-detect or apply named harness
    if harness_name:
        resolved = harness_name
        if harness_name == "auto":
            results = _detect_project_harness(project_root)
            if results and results[0][1] > 2:
                resolved = results[0][0]
                print(f"\nAuto-detected harness: {resolved} (score {results[0][1]})")
            else:
                resolved = "generic"
                print("\nNo strong harness signal detected — applying generic.")
        print()
        _apply_harness(resolved, project_root)

    print("\nNext:")
    print("  1. edit docs/REQUIREMENTS.md and docs/PLAN.md to describe this project")
    print("  2. `episteme sync` if you haven't already (propagates kernel memory to Claude/Hermes)")
    print("  3. `episteme start claude` to launch the agent surface in this project")


# ---------------------------------------------------------------------------
# Parser and main
# ---------------------------------------------------------------------------


def _kernel_verify() -> int:
    from . import kernel_integrity
    ok, diffs = kernel_integrity.verify(REPO_ROOT)
    if ok:
        print("[ok] kernel manifest matches working tree")
        return 0
    print("[fail] kernel drift detected:", file=sys.stderr)
    for d in diffs:
        print(f"  - {d}", file=sys.stderr)
    print("\nRun `episteme kernel update` to regenerate the manifest.", file=sys.stderr)
    return 2


def _kernel_update() -> int:
    from . import kernel_integrity
    path = kernel_integrity.write_manifest(REPO_ROOT)
    print(f"[ok] wrote {path.relative_to(REPO_ROOT)}")
    return 0


def _inject(target: Path = Path("."), strict: bool = True) -> int:
    cwd = target.resolve()
    if not cwd.exists():
        print(f"[inject] path does not exist: {cwd}", file=sys.stderr)
        return 1
    cognitive_dir = cwd / ".episteme"
    cognitive_dir.mkdir(parents=True, exist_ok=True)

    advisory_marker = cognitive_dir / "advisory-surface"
    if strict:
        if advisory_marker.exists():
            advisory_marker.unlink()
            print(f"[inject] removed advisory-surface marker   → strict mode restored")
        print(f"[inject] strict enforcement active (default) → {cognitive_dir}")
        print(f"         high-impact ops will BLOCK without a valid Reasoning Surface")
    else:
        advisory_marker.touch()
        print(f"[inject] advisory mode enabled              → {advisory_marker}")
        print(f"         high-impact ops will warn but NOT block.")
        print(f"         Remove this marker (or re-run without --no-strict) to restore strict mode.")

    surface_path = cognitive_dir / "reasoning-surface.json"
    if not surface_path.exists():
        from datetime import datetime, timezone as tz
        template = {
            "schema": "episteme/reasoning-surface@1",
            "timestamp": datetime.now(tz.utc).isoformat(),
            "core_question": "",
            "knowns": [],
            "unknowns": ["[fill this in before any high-impact action — must be >= 15 chars, not 'none'/'n/a'/'tbd']"],
            "assumptions": [],
            "disconfirmation": "",
        }
        surface_path.write_text(json.dumps(template, indent=2), encoding="utf-8")
        print(f"[inject] surface template written          → {surface_path}")
    else:
        print(f"[inject] surface already present           → {surface_path}")

    print()
    print(f"episteme enforcement active in: {cwd}")
    print("Next: edit .episteme/reasoning-surface.json")
    print("      Fill core_question, unknowns (>= 15 chars each), disconfirmation (>= 15 chars).")
    print("      Lazy values (none, n/a, tbd, 해당 없음) are rejected by the validator.")
    print("      Any high-impact op (git push, publish, migrations) blocks until the surface is valid.")
    return 0


def _surface_log(limit: int = 50, blocked_only: bool = False) -> int:
    audit_path = HOME / ".episteme" / "audit.jsonl"
    if not audit_path.exists():
        print("No audit log found. Activate enforcement first:")
        print("  episteme inject [path]   # deploy to a project")
        print("  episteme sync            # deploy globally")
        return 0

    entries: list[dict] = []
    with open(audit_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    if blocked_only:
        entries = [e for e in entries if e.get("action") == "blocked"]

    entries = entries[-limit:]

    if not entries:
        label = " (blocked only)" if blocked_only else ""
        print(f"No entries{label} in audit log.")
        return 0

    icons = {"blocked": "🔴", "advisory": "🟡", "passed": "🟢"}
    print(f"{'TIME':<28} {'ACTION':<10} {'STATUS':<12} {'TOOL':<10} OP")
    print("─" * 80)
    for e in entries:
        action = e.get("action", "?")
        icon = icons.get(action, "⚪")
        ts = (e.get("ts") or "?")[:19].replace("T", " ")
        print(
            f"{icon} {ts:<26} {action:<10} {e.get('status','?'):<12}"
            f" {e.get('tool','?'):<10} {e.get('op','?')}"
        )

    blocked_count = sum(1 for e in entries if e.get("action") == "blocked")
    print(f"\n{len(entries)} entries | {blocked_count} blocked")
    return 0


def _chain_dispatch(args) -> int:
    """Dispatch CP7 `episteme chain` subcommands — verify / reset / upgrade.

    Loads the hook modules lazily from ``core/hooks/`` so the CLI does
    not require the hooks on the import path at startup (they're only
    on the Claude Code runtime path).
    """
    import sys as _sys

    hooks_dir = REPO_ROOT / "core" / "hooks"
    if str(hooks_dir) not in _sys.path:
        _sys.path.insert(0, str(hooks_dir))

    try:
        import _framework  # type: ignore  # pyright: ignore[reportMissingImports]
        import _pending_contracts  # type: ignore  # pyright: ignore[reportMissingImports]
        import _chain as _chain_mod  # type: ignore  # pyright: ignore[reportMissingImports]
    except ImportError as exc:
        print(f"[episteme chain] error loading chain modules: {exc}", file=sys.stderr)
        return 2

    action = getattr(args, "chain_action", None)

    if action == "verify":
        fw = _framework.verify_chains()
        pc = _pending_contracts.verify_chain()
        pc_arch = _pending_contracts.verify_archive()
        # CP-AUDIT-ACK-01 / Event 78: include the profile-audit ack-store
        # in the chain-verify enumeration so its integrity is checked
        # alongside the framework + pending-contracts streams.
        try:
            from episteme import _profile_audit_ack as _ack_mod
            ack_verdict = _ack_mod.verify_chain()
        except Exception:  # noqa: BLE001 — degrade gracefully
            ack_verdict = None
        all_intact = True
        for stream_name, verdict in (
            ("protocols", fw.get("protocols")),
            ("deferred_discoveries", fw.get("deferred_discoveries")),
            ("pending_contracts", pc),
            ("pending_contracts_archive", pc_arch),
            ("profile_audit_acks", ack_verdict),
        ):
            if verdict is None:
                continue
            status = "INTACT" if verdict.intact else "BROKEN"
            if not verdict.intact:
                all_intact = False
            print(
                f"  {stream_name:32s} {status:8s} "
                f"entries={verdict.total_entries}"
                + (f"  break_index={verdict.break_index}" if verdict.break_index is not None else "")
                + (f"  reason={verdict.reason}" if verdict.reason else "")
            )
        return 0 if all_intact else 1

    if action == "reset":
        stream = args.stream
        stream_path = {
            "protocols": Path.home() / ".episteme" / "framework" / "protocols.jsonl",
            "deferred_discoveries": Path.home() / ".episteme" / "framework" / "deferred_discoveries.jsonl",
            "pending_contracts": Path.home() / ".episteme" / "state" / "pending_contracts.jsonl",
        }[stream]
        previous_head = None
        prior = _chain_mod.verify_chain(stream_path)
        if prior.head_hash:
            previous_head = prior.head_hash
        result = _chain_mod.reset_stream(
            stream_path,
            reason=args.reason,
            operator_confirmation=args.confirm,
            previous_head=previous_head,
        )
        print(f"[episteme chain reset] status={result.status}")
        if result.archived_path:
            print(f"  archived_to: {result.archived_path}")
        print(f"  new_genesis: {result.new_genesis_hash}")
        return 0

    if action == "recover":
        # CP-CHAIN-RECOVERY-PROTOCOL-01 / Event 80 — unified recovery
        # surface. mode=reset wraps reset_stream with the documented
        # attestation envelope fields. mode=selective and mode=migrate
        # are stubs that name their dependencies.
        mode = args.mode
        if mode == "selective":
            print(
                "[episteme chain recover] mode=selective is not yet implemented.",
                file=sys.stderr,
            )
            print(
                "  Depends on CP-CHAIN-RECOVERY-PROTOCOL-01 Component 5 "
                "(windowed-rebuild algorithm). See kernel/CHAIN_RECOVERY_PROTOCOL.md.",
                file=sys.stderr,
            )
            return 2
        if mode == "migrate":
            print(
                "[episteme chain recover] mode=migrate is not yet implemented.",
                file=sys.stderr,
            )
            print(
                "  Depends on CP-TEMPORAL-INTEGRITY-EXPANSION-01 (Cognitive Arm A) — "
                "supersede-with-history infrastructure required by the "
                "schema-migration walker. See kernel/CHAIN_RECOVERY_PROTOCOL.md.",
                file=sys.stderr,
            )
            return 2
        if mode != "reset":
            print(
                f"[episteme chain recover] unknown mode: {mode!r} "
                "(expected one of: reset, selective, migrate)",
                file=sys.stderr,
            )
            return 2

        # mode == "reset": delegate to reset_stream with the new
        # attestation fields populated.
        stream = args.stream
        stream_path = {
            "protocols": Path.home() / ".episteme" / "framework" / "protocols.jsonl",
            "deferred_discoveries": Path.home() / ".episteme" / "framework" / "deferred_discoveries.jsonl",
            "pending_contracts": Path.home() / ".episteme" / "state" / "pending_contracts.jsonl",
            "profile_audit_acks": Path.home() / ".episteme" / "state" / "profile_audit_acks.jsonl",
        }[stream]
        previous_head = None
        prior = _chain_mod.verify_chain(stream_path)
        if prior.head_hash:
            previous_head = prior.head_hash
        result = _chain_mod.reset_stream(
            stream_path,
            reason=args.reason,
            operator_confirmation=args.confirm,
            previous_head=previous_head,
            mode="reset",
            what_was_lost=getattr(args, "what_was_lost", None),
        )
        print(f"[episteme chain recover --mode=reset] status={result.status}")
        if result.archived_path:
            print(f"  archived_to: {result.archived_path}")
        print(f"  new_genesis: {result.new_genesis_hash}")
        return 0

    if action == "upgrade":
        # Only `protocols` has legacy cp5-pre-chain records at CP7.
        result = _framework.upgrade_cp5_prechain()
        print(f"[episteme chain upgrade] status={result.status}")
        print(f"  entries_processed={result.entries_processed}")
        if result.backup_path:
            print(f"  backup_path={result.backup_path}")
        print(f"  {result.message}")
        return 0

    print(f"[episteme chain] unknown action: {action}", file=sys.stderr)
    return 2


def _guide_dispatch(args) -> int:
    """Dispatch CP9 `episteme guide` — read-path for framework
    protocols and pending deferred_discoveries. Authoring / revision
    lands in v1.0.1."""
    import sys as _sys

    hooks_dir = REPO_ROOT / "core" / "hooks"
    if str(hooks_dir) not in _sys.path:
        _sys.path.insert(0, str(hooks_dir))
    try:
        import _framework  # type: ignore  # pyright: ignore[reportMissingImports]
    except ImportError as exc:
        print(f"[episteme guide] error loading framework module: {exc}", file=sys.stderr)
        return 2

    since = getattr(args, "guide_since", None)
    context = getattr(args, "guide_context", None)
    deferred = getattr(args, "guide_deferred", False)
    want_json = getattr(args, "guide_json", False)

    if since is not None:
        try:
            # Strict ISO-8601 parse per CP9 plan Q4. Accepts both
            # date-only and datetime forms.
            datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError:
            print(
                f"[episteme guide] --since must be strict ISO-8601 "
                f"(got {since!r})",
                file=sys.stderr,
            )
            return 2

    def _ts_passes(envelope: dict) -> bool:
        if since is None:
            return True
        ts = str(envelope.get("ts") or "")
        return ts >= since

    def _context_passes(payload: dict) -> bool:
        if context is None:
            return True
        needle = context.lower()
        protocol = str(payload.get("synthesized_protocol") or "").lower()
        if needle in protocol:
            return True
        sig = payload.get("context_signature")
        if isinstance(sig, dict):
            for v in sig.values():
                if isinstance(v, str) and needle in v.lower():
                    return True
        return False

    if deferred:
        envelopes = _framework.list_deferred_discoveries(status="pending")
        out_items = []
        for env in envelopes:
            if not isinstance(env, dict):
                continue
            payload = env.get("payload")
            if not isinstance(payload, dict):
                continue
            if not _ts_passes(env):
                continue
            if not _context_passes(payload):
                continue
            out_items.append({"ts": env.get("ts"), "payload": payload})
        if want_json:
            print(json.dumps(out_items, indent=2, ensure_ascii=False))
            return 0
        if not out_items:
            print("(no pending deferred discoveries)")
            return 0
        for i, item in enumerate(out_items, 1):
            p = item["payload"]
            print(f"Deferred discovery {i}/{len(out_items)}  logged={item['ts']}")
            print(f"  flaw_classification: {p.get('flaw_classification', '?')}")
            print(f"  description: {p.get('description', '?')}")
            print(f"  observable: {p.get('observable', '?')}")
            print(f"  log_only_rationale: {p.get('log_only_rationale', '?')}")
            print()
        return 0

    # Default path — list protocols.
    envelopes = _framework.list_protocols()
    out_items = []
    for env in envelopes:
        if not isinstance(env, dict):
            continue
        payload = env.get("payload")
        if not isinstance(payload, dict):
            continue
        if not _ts_passes(env):
            continue
        if not _context_passes(payload):
            continue
        out_items.append({"ts": env.get("ts"), "payload": payload})
    # Newest first.
    out_items.sort(key=lambda x: str(x.get("ts") or ""), reverse=True)

    if want_json:
        print(json.dumps(out_items, indent=2, ensure_ascii=False))
        return 0
    if not out_items:
        print("(no protocols match)")
        return 0
    total = len(out_items)
    for i, item in enumerate(out_items, 1):
        p = item["payload"]
        sig = p.get("context_signature") or {}
        print(f"Protocol {i}/{total}  synthesized={item['ts']}  "
              f"blueprint={p.get('blueprint', '?')}")
        if isinstance(sig, dict):
            sig_str = "  ".join(
                f"{k}={v!r}" for k, v in sig.items()
            )
            print(f"  context: {sig_str}")
        protocol_text = str(p.get("synthesized_protocol") or "").strip()
        print(f"  synthesized_protocol: {protocol_text}")
        cid = p.get("correlation_id", "?")
        print(f"  correlation_id: {cid}")
        print()
    return 0


def _review_dispatch(args) -> int:
    """Dispatch CP8 `episteme review` — list / stats / interactive."""
    import sys as _sys

    hooks_dir = REPO_ROOT / "core" / "hooks"
    if str(hooks_dir) not in _sys.path:
        _sys.path.insert(0, str(hooks_dir))
    try:
        import _spot_check  # type: ignore  # pyright: ignore[reportMissingImports]
    except ImportError as exc:
        print(f"[episteme review] error loading spot-check module: {exc}", file=sys.stderr)
        return 2

    if getattr(args, "review_stats", False):
        stats = _spot_check.stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return 0

    if getattr(args, "review_list", False):
        show_all = getattr(args, "all", False)
        entries = (
            _spot_check.list_entries() if show_all else _spot_check.list_pending()
        )
        if not entries:
            print("(no entries)" if show_all else "(no pending entries)")
            return 0
        for e in entries:
            cid = e.payload.get("correlation_id", "?")
            op = e.payload.get("op_label", "?")
            bp = e.payload.get("blueprint", "?")
            mults = ",".join(e.payload.get("multipliers_applied") or []) or "(none)"
            state = (
                "verdicted" if e.verdict is not None
                else "skipped" if e.skip_until is not None
                else "pending"
            )
            print(f"{cid:20s}  {state:10s}  {op:30s}  bp={bp}  mults={mults}")
        return 0

    # Interactive review path.
    correlation_id = getattr(args, "review_correlation_id", None)
    revise = getattr(args, "revise", False)
    if correlation_id:
        entry = _spot_check.get_entry(correlation_id)
        if entry is None:
            print(f"[episteme review] no entry with correlation_id {correlation_id!r}", file=sys.stderr)
            return 2
    else:
        pending = _spot_check.list_pending()
        if not pending:
            print("(no pending entries — queue empty)")
            return 0
        entry = pending[0]

    return _run_interactive_review(_spot_check, entry, revise=revise)


def _run_interactive_review(_spot_check, entry, *, revise: bool) -> int:
    """Interactive prompt flow for a single entry. Returns 0 on
    recorded verdict, 2 on invalid input / user abort."""
    payload = entry.payload
    multipliers = set(payload.get("multipliers_applied") or [])
    print()
    print(f"Op: {payload.get('op_label', '?')}")
    print(f"Blueprint: {payload.get('blueprint', '?')}")
    print(f"Queued: {payload.get('queued_at', '?')}")
    print(f"Correlation: {payload.get('correlation_id', '?')}")
    print(f"Effective rate: {payload.get('effective_rate_at_sample', '?')}")
    print(f"Multipliers: {','.join(multipliers) or '(none)'}")
    surface = payload.get("surface_snapshot") or {}
    if surface.get("core_question"):
        print(f"  core_question: {surface['core_question']}")
    if surface.get("disconfirmation"):
        print(f"  disconfirmation: {surface['disconfirmation']}")
    if surface.get("hypothesis"):
        print(f"  hypothesis: {surface['hypothesis']}")
    if entry.verdict is not None:
        prev = entry.verdict.get("verdicts", {})
        print(f"  EXISTING VERDICT: {prev}")
        if not revise:
            print(
                "This entry has a verdict already. Re-run with --revise to overwrite.",
                file=sys.stderr,
            )
            return 2
    print()

    def _prompt_enum(label: str, values, required: bool) -> str | None:
        opts = " / ".join(values)
        suffix = "" if required else " (or blank to skip this dimension)"
        while True:
            ans = input(f"{label} [{opts}]{suffix}: ").strip().lower()
            if not ans and not required:
                return None
            if ans in values:
                return ans
            print(f"  invalid — expected one of {sorted(values)}")

    try:
        sv_values = sorted(_spot_check.SURFACE_VALIDITY_VALUES)
        sv = _prompt_enum("surface_validity", sv_values, required=True)
        verdicts: dict = {"surface_validity": sv}

        if "synthesis_produced" in multipliers:
            pq_values = sorted(_spot_check.PROTOCOL_QUALITY_VALUES)
            pq = _prompt_enum("protocol_quality", pq_values, required=True)
            verdicts["protocol_quality"] = pq

        if "blueprint_d_resolution" in multipliers:
            ci_values = sorted(_spot_check.CASCADE_INTEGRITY_VALUES)
            ci = _prompt_enum("cascade_integrity", ci_values, required=True)
            verdicts["cascade_integrity"] = ci

        note = input("Optional note (blank to skip): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n[episteme review] aborted", file=sys.stderr)
        return 2

    try:
        _spot_check.write_verdict(
            correlation_id=payload.get("correlation_id", ""),
            verdicts=verdicts,
            note=note,
            is_revision=revise,
        )
    except Exception as exc:
        print(f"[episteme review] error: {exc}", file=sys.stderr)
        return 2
    print("Verdict recorded.")
    return 0


def _audit(fix: bool = False) -> int:
    """Reasoning audit: verify the current project session has addressed cognitive unknowns."""

    TARGET_FILES = ["PROGRESS.md", "PLAN.md", "NEXT_STEPS.md"]
    REASONING_SECTIONS = ["## Knowns", "## Unknowns", "## Assumptions", "## Disconfirmation"]
    REASONING_SURFACE_HEADER = "## Reasoning Surface"
    SOWATNOW_PATTERNS = ["## So-What Now?", "## TL;DR", "## So What Now?"]
    CHECKPOINT_PATTERNS = ["checkpoint", "verification", "verify", "gate", "acceptance criteria"]

    REASONING_STUB = """

## Reasoning Surface

### Knowns
- _fill in verified facts_

### Unknowns
- _fill in identified gaps or risks_

### Assumptions
- _fill in critical beliefs that require validation_

### Disconfirmation
- _What would prove us wrong? What signal would trigger a pivot?_
"""

    SOWATNOW_STUB = """

## So-What Now?

> _TL;DR: What is the single most important next action and why?_

- **Immediate**: _fill in_
- **Blockers**: _fill in_
- **Open Questions**: _fill in_
"""

    # Walk up from cwd to find target files
    cwd = Path.cwd()
    found_files: dict[str, Path] = {}
    search_dir = cwd
    for _ in range(6):  # walk up at most 6 levels
        for fname in TARGET_FILES:
            candidate = search_dir / "docs" / fname
            if candidate.exists() and fname not in found_files:
                found_files[fname] = candidate
            # also check directly in the dir
            candidate2 = search_dir / fname
            if candidate2.exists() and fname not in found_files:
                found_files[fname] = candidate2
        if search_dir.parent == search_dir:
            break
        search_dir = search_dir.parent

    results: list[tuple[str, str, bool, str]] = []  # (check_name, file_path, passed, detail)
    files_needing_reasoning_stub: list[Path] = []
    files_needing_sowatnow_stub: list[Path] = []

    for fname in TARGET_FILES:
        if fname not in found_files:
            results.append((f"{fname}: found", "not found", False, "file not present in project or docs/"))
            continue

        fpath = found_files[fname]
        content = fpath.read_text(encoding="utf-8", errors="ignore")
        content_lower = content.lower()

        results.append((f"{fname}: found", str(fpath), True, ""))

        # Check for Reasoning Surface block
        has_reasoning_surface = REASONING_SURFACE_HEADER.lower() in content_lower
        has_all_sections = all(sec.lower() in content_lower for sec in REASONING_SECTIONS)
        reasoning_ok = has_reasoning_surface or has_all_sections
        results.append(
            (f"{fname}: Reasoning Surface", str(fpath), reasoning_ok,
             "has Knowns/Unknowns/Assumptions/Disconfirmation" if reasoning_ok else "missing Reasoning Surface block")
        )
        if not reasoning_ok:
            files_needing_reasoning_stub.append(fpath)

        # NEXT_STEPS.md: check for So-What Now? / TL;DR
        if fname == "NEXT_STEPS.md":
            has_sowatnow = any(pat.lower() in content_lower for pat in SOWATNOW_PATTERNS)
            results.append(
                (f"{fname}: So-What Now? / TL;DR", str(fpath), has_sowatnow,
                 "summary section present" if has_sowatnow else "missing 'So-What Now?' or 'TL;DR' section")
            )
            if not has_sowatnow:
                files_needing_sowatnow_stub.append(fpath)

        # PLAN.md: check for verification checkpoints
        if fname == "PLAN.md":
            has_checkpoints = any(pat in content_lower for pat in CHECKPOINT_PATTERNS)
            results.append(
                (f"{fname}: Verification Checkpoints", str(fpath), has_checkpoints,
                 "checkpoint/verification language found" if has_checkpoints else "no explicit verification checkpoints found")
            )

    # Print results
    print()
    print("episteme audit — Reasoning Check")
    print("=" * 50)
    all_passed = True
    for check_name, fpath_str, passed, detail in results:
        status = "[ok]" if passed else "[missing]"
        line = f"  {status:<10} {check_name}"
        if detail and not passed:
            line += f"\n             -> {detail}"
        if fpath_str and fpath_str != "not found" and passed:
            line += f"\n             -> {fpath_str}"
        print(line)
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("All reasoning checks passed. Session is cognitively sound.")
    else:
        print("Some checks are missing. Run with --fix to append stub blocks.")

    # --fix: append stubs to files missing them
    if fix:
        print()
        print("Applying --fix: appending missing reasoning stubs...")
        for fpath in files_needing_reasoning_stub:
            existing = fpath.read_text(encoding="utf-8", errors="ignore")
            fpath.write_text(existing.rstrip() + REASONING_STUB, encoding="utf-8")
            print(f"  [fixed] appended Reasoning Surface stub to {fpath}")
        for fpath in files_needing_sowatnow_stub:
            existing = fpath.read_text(encoding="utf-8", errors="ignore")
            fpath.write_text(existing.rstrip() + SOWATNOW_STUB, encoding="utf-8")
            print(f"  [fixed] appended So-What Now? stub to {fpath}")
        if not files_needing_reasoning_stub and not files_needing_sowatnow_stub:
            print("  Nothing to fix — all stubs already present.")

    return 0 if all_passed else 1


_EPILOG_GROUPED = """\
command map (grouped by lifecycle phase):

  daily
    bootstrap, new-project   scaffold a project in the current directory
    sync                     propagate kernel memory + policies into Claude Code / Hermes
    start                    launch the preferred agent surface for this project
    doctor                   verify runtime wiring (Conda, core tools, optional tools)
    audit                    check whether the current session addressed its unknowns
    memory                   record, list, search, promote memory records

  setup & admin
    init                     seed kernel global memory from examples (one-shot after clone)
    setup                    interactive profile + cognition wizard
    profile, cognition       edit operator-profile and cognitive-style axes
    update                   pull the latest episteme from git
    list, validate           inventory installed agents/skills/plugins; check manifest

  project tools
    detect, harness          score and apply a harness to a project
    worktree                 create a git worktree for a bounded task
    viewer                   local read-only dashboard over this repo
    capture                  draft a reasoning-surface.json skeleton from text

  framework internals
    kernel                   manifest verify/update
    chain                    hash-chain verify/reset/upgrade
    guide                    list synthesized protocols and deferred discoveries
    inject, log              deploy enforcement, show audit log
    review                   spot-check sampled reasoning-surface entries
    evolve                   gated self-evolution episodes
    bridge                   external runtime event-log bridges
    private-skill            toggle experimental private skills

Run `episteme <command> --help` for flags and arguments on any command.
Cheatsheet with one-line explanations: docs/COMMANDS.md
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="episteme",
        description="🧠 episteme: the identity and context layer for autonomous agents.",
        epilog=_EPILOG_GROUPED,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Bootstrap personal memory files from *.example.md templates")
    sub.add_parser("doctor", help="Verify runtime wiring — Conda, core tools, optional tools")

    memory_cmd = sub.add_parser("memory", help="Create, list, and search memory records")
    memory_sub = memory_cmd.add_subparsers(dest="memory_action", required=True)
    m_record = memory_sub.add_parser("record", help="Create a new memory record")
    m_record.add_argument("--summary", required=True, help="Short human-readable summary of the memory")
    m_record.add_argument("--class", dest="memory_class", choices=["global", "project", "episodic"], default="episodic")
    m_record.add_argument("--confidence", choices=["low", "medium", "high"], default="medium")
    m_record.add_argument("--source", choices=["human", "agent", "tool"], default="human")
    m_list = memory_sub.add_parser("list", help="List memory records")
    m_list.add_argument("--class", dest="memory_class", choices=["global", "project", "episodic"], default=None)
    m_list.add_argument("--status", choices=["active", "archived", "superseded"], default="active")
    m_list.add_argument("--limit", type=int, default=20)
    m_search = memory_sub.add_parser("search", help="Search active memory records by text")
    m_search.add_argument("query", help="Text to search for (case-insensitive)")

    m_promote = memory_sub.add_parser(
        "promote",
        help="Scan episodic records for stable patterns; emit semantic-tier proposals (never auto-promotes)",
    )
    m_promote.add_argument(
        "--episodic-dir",
        default=None,
        help="Override episodic-tier directory (default: ~/.episteme/memory/episodic)",
    )
    m_promote.add_argument(
        "--reflective-dir",
        default=None,
        help="Override reflective-tier directory (default: ~/.episteme/memory/reflective)",
    )
    m_promote.add_argument(
        "--output",
        default=None,
        help="Write the Markdown report to this path instead of only stdout",
    )
    m_promote.add_argument(
        "--min-cluster",
        type=int,
        default=3,
        help="Minimum cluster size to emit a proposal (default: 3)",
    )

    sync = sub.add_parser("sync", help="Sync managed runtime assets into Claude Code and Hermes")
    sync.add_argument(
        "--governance-pack",
        choices=["minimal", "balanced", "strict"],
        default="balanced",
        help="Runtime governance profile for hook/safety integration (default: balanced)",
    )
    sync.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: show what would be written/updated without making changes. Exits 1 if changes needed.",
    )
    sub.add_parser("update", help="Pull the latest episteme from git")
    sub.add_parser("list", help="Show installed agents, skills, plugins, and active hooks")
    sub.add_parser("validate", help="Check manifest integrity — every declared skill must have a SKILL.md")

    for cmd in ("bootstrap", "new-project"):
        p = sub.add_parser(cmd, help="Scaffold the standard project structure")
        p.add_argument("path", nargs="?", default=".")
        p.add_argument(
            "--harness",
            metavar="TYPE",
            help="Apply a harness after scaffolding. Use 'auto' to detect from repo contents.",
        )

    detect = sub.add_parser("detect", help="Detect the best harness type for a project")
    detect.add_argument("path", nargs="?", default=".")

    harness_cmd = sub.add_parser("harness", help="Manage project harnesses")
    harness_sub = harness_cmd.add_subparsers(dest="harness_action", required=True)
    harness_sub.add_parser("list", help="List available harness types")
    h_apply = harness_sub.add_parser("apply", help="Apply a harness to a project")
    h_apply.add_argument("type", help="Harness type (ml-research, python-library, web-app, data-pipeline, generic)")
    h_apply.add_argument("path", nargs="?", default=".")
    h_apply.add_argument("--force", action="store_true", help="Overwrite an existing HARNESS.md")

    profile_cmd = sub.add_parser("profile", help="Deterministic working-style profiling and policy compilation")
    profile_sub = profile_cmd.add_subparsers(dest="profile_action", required=True)

    p_survey = profile_sub.add_parser("survey", help="Interactive survey-based profile scoring")
    p_survey.add_argument("--answers-file", metavar="JSON", help="Optional JSON file with prefilled survey answers")
    p_survey.add_argument("--write", action="store_true", help="Compile generated scores into global memory markdown files")
    p_survey.add_argument("--overwrite", action="store_true", help="Allow overwriting existing global memory markdown files")

    p_infer = profile_sub.add_parser("infer", help="Infer profile scores from repository signals")
    p_infer.add_argument("path", nargs="?", default=".")
    p_infer.add_argument("--write", action="store_true", help="Compile generated scores into global memory markdown files")
    p_infer.add_argument("--overwrite", action="store_true", help="Allow overwriting existing global memory markdown files")

    p_hybrid = profile_sub.add_parser("hybrid", help="Blend survey and inferred profile scores")
    p_hybrid.add_argument("path", nargs="?", default=".")
    p_hybrid.add_argument("--answers-file", metavar="JSON", help="Optional JSON file with prefilled survey answers")
    p_hybrid.add_argument("--write", action="store_true", help="Compile generated scores into global memory markdown files")
    p_hybrid.add_argument("--overwrite", action="store_true", help="Allow overwriting existing global memory markdown files")

    p_gap = profile_sub.add_parser(
        "gap",
        help="Context-Loading Protocol: load existing scores, detect repo signals, ask only missing dimensions",
    )
    p_gap.add_argument("path", nargs="?", default=".")
    p_gap.add_argument("--answers-file", metavar="JSON", help="Optional JSON file with prefilled answers for gap dimensions")
    p_gap.add_argument("--write", action="store_true", help="Compile generated scores into global memory markdown files")
    p_gap.add_argument("--overwrite", action="store_true", help="Allow overwriting existing global memory markdown files")

    profile_sub.add_parser("show", help="Show the latest generated workstyle scorecard")

    p_audit = profile_sub.add_parser(
        "audit",
        help="Audit the declared cognitive profile against the lived episodic record (phase 12)",
    )
    p_audit.add_argument(
        "--since",
        default="30d",
        metavar="<N>d",
        help="Rolling window over episodic records (default: 30d)",
    )
    p_audit.add_argument(
        "--write",
        action="store_true",
        help="Append the audit record to ~/.episteme/memory/reflective/profile_audit.jsonl",
    )
    p_audit.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit the full audit record as JSON instead of human-readable Markdown (stable format)",
    )

    # Nested ack subcommand under `profile audit ack`. CP-AUDIT-ACK-01 / Event 78.
    audit_sub = p_audit.add_subparsers(dest="audit_action", required=False)
    p_ack = audit_sub.add_parser(
        "ack",
        help="Acknowledge / list / revoke profile-audit drift findings",
    )
    p_ack.add_argument(
        "audit_id",
        nargs="?",
        help="Audit run-id to acknowledge (audit-YYYYMMDD-HHMMSS-NNNN); omit when using --list",
    )
    p_ack.add_argument(
        "--rationale",
        help="Substantive reason for the ack (min 15 chars; lazy tokens 'n/a' / 'tbd' / etc. rejected)",
    )
    p_ack.add_argument(
        "--list",
        dest="list_outstanding",
        action="store_true",
        help="List outstanding (un-acked) profile-audit drift records",
    )
    p_ack.add_argument(
        "--revoke",
        action="store_true",
        help="Revoke a prior ack (audit-trail preserved; revoke appends a new chain entry, never deletes)",
    )
    p_ack.add_argument(
        "--evidence-refs",
        dest="evidence_refs",
        nargs="*",
        default=[],
        metavar="REF",
        help="Optional event/episode references supporting the ack (e.g. 'Event 65' 'Event 66')",
    )

    cognition_cmd = sub.add_parser("cognition", help="Deterministic cognitive/philosophy profiling")
    cognition_sub = cognition_cmd.add_subparsers(dest="cognition_action", required=True)
    c_survey = cognition_sub.add_parser("survey", help="Interactive cognitive-style survey")
    c_survey.add_argument("--answers-file", metavar="JSON", help="Optional JSON file with prefilled cognitive answers")
    c_survey.add_argument("--write", action="store_true", help="Compile generated cognitive scores into global memory markdown")
    c_survey.add_argument("--overwrite", action="store_true", help="Allow overwriting existing cognitive_profile.md")

    c_infer = cognition_sub.add_parser("infer", help="Infer cognitive scores from repository signals")
    c_infer.add_argument("path", nargs="?", default=".")
    c_infer.add_argument("--write", action="store_true", help="Compile generated cognitive scores into global memory markdown")
    c_infer.add_argument("--overwrite", action="store_true", help="Allow overwriting existing cognitive_profile.md")

    c_hybrid = cognition_sub.add_parser("hybrid", help="Blend cognitive survey and inferred scores")
    c_hybrid.add_argument("path", nargs="?", default=".")
    c_hybrid.add_argument("--answers-file", metavar="JSON", help="Optional JSON file with prefilled cognitive answers")
    c_hybrid.add_argument("--write", action="store_true", help="Compile generated cognitive scores into global memory markdown")
    c_hybrid.add_argument("--overwrite", action="store_true", help="Allow overwriting existing cognitive_profile.md")

    cognition_sub.add_parser("show", help="Show the latest generated cognitive scorecard")

    setup = sub.add_parser("setup", help="Interactive/non-interactive setup wizard for profile + cognition")
    setup.add_argument("path", nargs="?", default=".", help="Project path used for infer/hybrid modes")
    setup.add_argument("--interactive", action="store_true", help="Run interactive wizard prompts")
    setup.add_argument("--profile-mode", choices=["survey", "infer", "hybrid", "skip"], default=None)
    setup.add_argument("--cognition-mode", choices=["survey", "infer", "hybrid", "skip"], default=None)
    setup.add_argument(
        "--governance-pack",
        choices=["minimal", "balanced", "strict"],
        default="balanced",
        help="Governance profile used when --sync is enabled during setup (default: balanced)",
    )
    setup.add_argument("--answers-file", metavar="JSON", help="Fallback JSON answers file used by both profile and cognition")
    setup.add_argument("--profile-answers-file", metavar="JSON", help="Optional JSON answers file for profile survey/hybrid")
    setup.add_argument("--cognition-answers-file", metavar="JSON", help="Optional JSON answers file for cognition survey/hybrid")
    setup.add_argument("--write", action="store_true", help="Compile results into authoritative global memory files")
    setup.add_argument("--overwrite", action="store_true", help="Allow overwriting existing authoritative files")
    setup.add_argument("--sync", action="store_true", help="Run episteme sync after setup")
    setup.add_argument("--doctor", action="store_true", help="Run episteme doctor after setup")

    audit = sub.add_parser("audit", help="Reasoning check: verify the current project session has addressed cognitive unknowns")
    audit.add_argument("--fix", action="store_true", help="Append stub Reasoning Surface blocks to files that are missing them")

    kernel = sub.add_parser("kernel", help="Kernel integrity manifest operations")
    kernel_sub = kernel.add_subparsers(dest="kernel_action", required=True)
    kernel_sub.add_parser("verify", help="Verify managed kernel files match the manifest")
    kernel_sub.add_parser("update", help="Regenerate kernel/MANIFEST.sha256 from current files")

    worktree = sub.add_parser("worktree", help="Create a git worktree for a bounded task")
    worktree.add_argument("task_type")
    worktree.add_argument("task_name", nargs="+")
    worktree.add_argument("--base", dest="base_ref")

    private_skill = sub.add_parser("private-skill", help="Enable or disable a private experimental skill")
    private_skill.add_argument("action", choices=["enable", "disable", "status"])
    private_skill.add_argument("name")
    private_skill.add_argument("--tool", default="claude")

    inject_cmd = sub.add_parser(
        "inject",
        help="Deploy cognitive enforcement to any directory in one command",
    )
    inject_cmd.add_argument(
        "path", nargs="?", type=Path, default=Path("."),
        help="Target directory (default: current dir)",
    )
    inject_cmd.add_argument(
        "--no-strict", dest="no_strict", action="store_true",
        help="Advisory mode only — do not enable hard blocking",
    )

    log_cmd = sub.add_parser(
        "log",
        help="Show audit log of reasoning-surface checks (passed / advisory / blocked)",
    )
    log_cmd.add_argument(
        "--limit", type=int, default=50,
        help="Number of recent entries to show (default: 50)",
    )
    log_cmd.add_argument(
        "--blocked", action="store_true",
        help="Show only blocked operations",
    )

    # CP7 — Pillar 2 hash-chain management.
    chain_cmd = sub.add_parser(
        "chain",
        help="Pillar 2 hash-chain operations (verify / reset / upgrade)",
    )
    chain_sub = chain_cmd.add_subparsers(dest="chain_action", required=True)

    chain_sub.add_parser(
        "verify",
        help="Verify all CP7 chains (framework protocols + deferred_discoveries + pending_contracts)",
    )

    c_reset = chain_sub.add_parser(
        "reset",
        help="Archive a broken chain and start a fresh one (operator escape hatch for legitimate state loss)",
    )
    c_reset.add_argument(
        "--stream",
        required=True,
        choices=["protocols", "deferred_discoveries", "pending_contracts"],
        help="Which chain stream to reset",
    )
    c_reset.add_argument(
        "--reason",
        required=True,
        help="Short reason for the reset (goes into the chain_reset genesis record)",
    )
    c_reset.add_argument(
        "--confirm",
        required=True,
        help="Operator confirmation string (e.g. 'I ACKNOWLEDGE CHAIN RESET')",
    )

    c_upgrade = chain_sub.add_parser(
        "upgrade",
        help="Retroactively wrap legacy cp5-pre-chain records in the cp7-chained-v1 envelope",
    )
    c_upgrade.add_argument(
        "--stream",
        default="protocols",
        choices=["protocols"],
        help="Stream to upgrade (only `protocols` has legacy records to upgrade at CP7)",
    )

    # CP-CHAIN-RECOVERY-PROTOCOL-01 / Event 80 — unified recovery surface
    # covering reset (functional), selective (stub), migrate (stub).
    c_recover = chain_sub.add_parser(
        "recover",
        help="Recover a broken chain (mode=reset functional; mode=selective and mode=migrate stubbed pending dependent CPs)",
    )
    c_recover.add_argument(
        "--mode",
        required=True,
        choices=["reset", "selective", "migrate"],
        help="Recovery mode: reset (full rewind), selective (windowed-rebuild; not yet implemented), migrate (schema migration; not yet implemented)",
    )
    c_recover.add_argument(
        "--stream",
        required=True,
        choices=["protocols", "deferred_discoveries", "pending_contracts", "profile_audit_acks"],
        help="Which chain stream to recover",
    )
    c_recover.add_argument(
        "--reason",
        required=True,
        help="Operator-supplied rationale (free text; recorded in the recovery-attestation envelope)",
    )
    c_recover.add_argument(
        "--confirm",
        required=True,
        help="Operator confirmation string (e.g. 'I ACKNOWLEDGE CHAIN RESET')",
    )
    c_recover.add_argument(
        "--what-was-lost",
        dest="what_was_lost",
        default=None,
        help="Optional description of data that won't be carried forward (recommended for mode=reset)",
    )

    # CP9 — Pillar 3 active guidance query.
    guide_cmd = sub.add_parser(
        "guide",
        help="List synthesized framework protocols (and pending deferred discoveries with --deferred)",
    )
    guide_cmd.add_argument(
        "--context", dest="guide_context", default=None,
        help="Substring filter on synthesized_protocol and context_signature fields (case-insensitive)",
    )
    guide_cmd.add_argument(
        "--since", dest="guide_since", default=None,
        help="Show only entries with ts >= <date> (strict ISO-8601, e.g. 2026-04-21 or 2026-04-21T12:00:00Z)",
    )
    guide_cmd.add_argument(
        "--deferred", dest="guide_deferred", action="store_true",
        help="List pending deferred_discoveries entries instead of protocols",
    )
    guide_cmd.add_argument(
        "--json", dest="guide_json", action="store_true",
        help="Emit structured JSON output for scripting",
    )

    # CP8 — Layer 8 spot-check review.
    review_cmd = sub.add_parser(
        "review",
        help="Review sampled Layer 8 spot-check entries (operator verdicts)",
    )
    review_cmd.add_argument(
        "--list", dest="review_list", action="store_true",
        help="List pending entries instead of entering interactive review",
    )
    review_cmd.add_argument(
        "--stats", dest="review_stats", action="store_true",
        help="Print queue statistics (total / verdicted / pending / distribution)",
    )
    review_cmd.add_argument(
        "--correlation-id", dest="review_correlation_id", default=None,
        help="Review the entry matching this correlation id (instead of the oldest pending)",
    )
    review_cmd.add_argument(
        "--revise", action="store_true",
        help="Record a new verdict even if the entry is already verdicted",
    )
    review_cmd.add_argument(
        "--all", action="store_true",
        help="With --list: include already-verdicted and skipped entries",
    )

    start = sub.add_parser("start", help="Start the preferred agent surface")
    start.add_argument("tool", nargs="?", default="claude", choices=["claude"])

    viewer = sub.add_parser("viewer", help="Start a local read-only dashboard over this repo")
    viewer.add_argument("--host", default="127.0.0.1")
    viewer.add_argument("--port", type=int, default=37776)

    capture = sub.add_parser(
        "capture",
        help="Draft a reasoning-surface.json skeleton from unstructured text (Slack thread, PR desc, ticket, email). Reads stdin if --input is omitted.",
    )
    capture.add_argument("--input", type=Path, default=None, help="Path to text input file (default: stdin)")
    capture.add_argument("--output", type=Path, default=None, help="Path to write draft JSON (default: stdout)")
    capture.add_argument("--by", dest="captured_by", default=None, help="Operator name to record in captured_by")
    capture.add_argument(
        "--core-question",
        dest="core_question",
        default=None,
        help="Override auto-extracted Core Question (recommended when the input is ambiguous)",
    )
    capture.add_argument(
        "--friction",
        dest="friction",
        default=None,
        help="Override auto-extracted uncomfortable_friction description",
    )
    capture.add_argument("--print", dest="print_only", action="store_true", help="Print to stdout and do not write even if --output is given")

    evolve = sub.add_parser("evolve", help="Run and manage gated self-evolution episodes")
    evolve_sub = evolve.add_subparsers(dest="evolve_action", required=True)

    bridge = sub.add_parser("bridge", help="Bridge external runtime event logs into memory-contract envelopes")
    bridge_sub = bridge.add_subparsers(dest="bridge_action", required=True)

    b_am = bridge_sub.add_parser(
        "anthropic-managed",
        help="Transform Anthropic Managed Agents event logs into memory-contract episodic records",
    )
    b_am.add_argument("--input", required=True, help="Path to Managed Agents events JSON file")
    b_am.add_argument("--output", help="Optional output path for memory envelope JSON")
    b_am.add_argument("--session-id", help="Override session id (otherwise derived from payload/input name)")
    b_am.add_argument("--project-id", help="Optional related project id for record linkage")
    b_am.add_argument("--source-ref", help="Optional source reference override for provenance")
    b_am.add_argument("--captured-by", default="episteme bridge", help="Provenance captured_by value")
    b_am.add_argument("--confidence", choices=["low", "medium", "high"], default="medium")
    b_am.add_argument("--dry-run", action="store_true", help="Parse and summarize without writing output")

    b_sub = bridge_sub.add_parser(
        "substrate",
        help="Push/pull memory-contract envelopes to any external memory substrate via a pluggable adapter.",
    )
    b_sub_act = b_sub.add_subparsers(dest="substrate_action", required=True)

    b_sub_act.add_parser("list-adapters", help="List installed substrate adapters")

    b_sub_desc = b_sub_act.add_parser("describe", help="Print an adapter's capability descriptor")
    b_sub_desc.add_argument("adapter")

    b_sub_ver = b_sub_act.add_parser("verify", help="Load an adapter and validate its descriptor against the v1 schema")
    b_sub_ver.add_argument("adapter")

    def _add_scope_args(p: argparse.ArgumentParser) -> None:
        for key in ("user-id", "project-id", "agent-id", "session-id", "run-id", "app-id", "org-id"):
            p.add_argument(f"--{key}", dest=key.replace("-", "_"), default=None)

    b_sub_push = b_sub_act.add_parser("push", help="Push a memory-contract-v1 envelope into the named substrate")
    b_sub_push.add_argument("adapter")
    b_sub_push.add_argument("--input", required=True, help="Path to memory-contract envelope JSON")
    b_sub_push.add_argument("--output", help="Optional path to write the push result JSON (default: stdout)")
    b_sub_push.add_argument("--config", help="Optional path to adapter config JSON")
    _add_scope_args(b_sub_push)

    b_sub_pull = b_sub_act.add_parser("pull", help="Pull from substrate, emit a memory-contract-v1 envelope")
    b_sub_pull.add_argument("adapter")
    b_sub_pull.add_argument("--query", default=None, help="Optional free-text query")
    b_sub_pull.add_argument("--limit", type=int, default=50)
    b_sub_pull.add_argument("--since", default=None, help="ISO-8601 timestamp lower bound")
    b_sub_pull.add_argument("--output", help="Optional path to write the envelope JSON (default: stdout)")
    b_sub_pull.add_argument("--config", help="Optional path to adapter config JSON")
    _add_scope_args(b_sub_pull)

    e_run = evolve_sub.add_parser("run", help="Create a candidate evolution episode")
    e_run.add_argument("--hypothesis", required=True, help="Hypothesis this evolution episode tests")
    e_run.add_argument("--mutation-type", required=True, choices=sorted(ALLOWED_EVOLUTION_MUTATIONS))
    e_run.add_argument("--target", required=True, help="Target file/policy for the mutation")
    e_run.add_argument("--expected-effect", required=True, help="Expected measurable effect")
    e_run.add_argument("--diff", default="", help="Optional mutation diff/summary")
    e_run.add_argument("--risk-level", default="medium", choices=["low", "medium", "high"])
    e_run.add_argument("--suite-ref", default="default-suite")
    e_run.add_argument("--seed", type=int, default=0)
    e_run.add_argument("--captured-by", default="episteme")

    e_report = evolve_sub.add_parser("report", help="Show an evolution episode summary")
    e_report.add_argument("episode_id")

    e_promote = evolve_sub.add_parser("promote", help="Promote an episode after gate checks")
    e_promote.add_argument("episode_id")
    e_promote.add_argument("--force", action="store_true", help="Override failed gates")

    e_rollback = evolve_sub.add_parser("rollback", help="Rollback a previously promoted episode")
    e_rollback.add_argument("episode_id")
    e_rollback.add_argument("--ref", required=True, help="Rollback reference/reason id")

    e_friction = evolve_sub.add_parser(
        "friction",
        help="Heuristic analyzer: scan calibration telemetry for predictions that failed in practice",
    )
    e_friction.add_argument(
        "--telemetry-dir",
        default=None,
        help="Override telemetry directory (default: ~/.episteme/telemetry)",
    )
    e_friction.add_argument(
        "--output",
        default=None,
        help="Write the Markdown report to this path instead of stdout",
    )
    e_friction.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of top-ranked unknowns / ops to surface (default: 5)",
    )

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    argv_list = list(argv) if argv is not None else sys.argv[1:]
    if argv_list and argv_list[0] in ("?", "help"):
        # `episteme ?` or `episteme help` → main help
        # `episteme ? sync` or `episteme help sync` → subcommand help
        if len(argv_list) > 1:
            argv_list = argv_list[1:] + ["--help"]
        else:
            argv_list = ["--help"]
    parser = build_parser()
    args = parser.parse_args(argv_list)

    if args.command == "init":
        return _init_memory()
    if args.command == "doctor":
        return _doctor()
    if args.command == "memory":
        if args.memory_action == "record":
            return _memory_record(
                summary=args.summary,
                memory_class=args.memory_class,
                confidence=args.confidence,
                source=args.source,
            )
        if args.memory_action == "list":
            return _memory_list(
                memory_class=getattr(args, "memory_class", None),
                status=args.status,
                limit=args.limit,
            )
        if args.memory_action == "search":
            return _memory_search(args.query)
        if args.memory_action == "promote":
            from pathlib import Path as _Path
            from . import _memory_promote as _mp
            report, count, written_to = _mp.run_promote(
                episodic_dir=_Path(args.episodic_dir) if args.episodic_dir else None,
                reflective_dir=_Path(args.reflective_dir) if args.reflective_dir else None,
                output_path=_Path(args.output) if args.output else None,
                min_cluster_size=args.min_cluster,
            )
            print(report)
            if written_to is not None:
                print(f"\nWrote {count} proposal(s) to: {written_to}")
            return 0
        return 0
    if args.command == "sync":
        if getattr(args, "check", False):
            return _sync_check(getattr(args, "governance_pack", "balanced"))
        print("🛸 Transitioning Soul to all available vessels...")
        _sync_user_runtime(getattr(args, "governance_pack", "balanced"))
        print("✅ Transition complete. Your agents are now aware.")
        print("\nNext: `episteme doctor` to verify wiring, or `episteme start claude` in a project.")
        return 0
    if args.command == "update":
        return _update()
    if args.command == "list":
        _list_runtime()
        return 0
    if args.command == "validate":
        return _validate_manifest()
    if args.command in ("bootstrap", "new-project"):
        _bootstrap_project(
            _resolve_bootstrap_target(args.path),
            harness_name=getattr(args, "harness", None),
        )
        return 0
    if args.command == "detect":
        project_root = _resolve_bootstrap_target(args.path)
        print(f"Analyzing {project_root} ...")
        print()
        results = _detect_project_harness(project_root)
        if not results or results[0][1] == 0:
            print("No harness signals detected. Apply the generic harness or specify one explicitly.")
            print("  episteme harness apply generic .")
            return 0
        print("Harness scores:")
        print()
        for i, (name, score, signals) in enumerate(results):
            if score == 0:
                continue
            marker = "  ← recommended" if i == 0 and score > 2 else ""
            print(f"  {name:<22} score {score}{marker}")
            for sig in signals[:6]:
                print(f"    · {sig}")
        print()
        best_name, best_score, _ = results[0]
        if best_score > 2:
            print(f"Recommended: {best_name}")
            print(f"  episteme harness apply {best_name} {args.path}")
        else:
            print("Low confidence — review scores above and choose manually.")
            print("  episteme harness list")
        return 0
    if args.command == "harness":
        if args.harness_action == "list":
            _list_harnesses()
            return 0
        if args.harness_action == "apply":
            return _apply_harness(
                args.type,
                _resolve_bootstrap_target(args.path),
                force=args.force,
            )
        return 0
    if args.command == "profile":
        if args.profile_action == "show":
            return _profile_show()
        if args.profile_action == "audit":
            if getattr(args, "audit_action", None) == "ack":
                return _profile_audit_ack_cli(args)
            return _profile_audit_cli(
                since=args.since,
                write=args.write,
                as_json=args.as_json,
            )
        if args.profile_action in ("survey", "infer", "hybrid", "gap"):
            path_arg = getattr(args, "path", ".")
            answers = None
            answers_file = getattr(args, "answers_file", None)
            if answers_file:
                try:
                    answers = _load_answers_file(Path(answers_file).expanduser())
                except (FileNotFoundError, ValueError) as exc:
                    print(str(exc), file=sys.stderr)
                    return 1
            return _profile_command(
                args.profile_action,
                path_arg,
                write=getattr(args, "write", False),
                overwrite=getattr(args, "overwrite", False),
                answers=answers,
            )
        return 0
    if args.command == "cognition":
        answers = None
        answers_file = getattr(args, "answers_file", None)
        if answers_file:
            try:
                answers = _load_answers_file(Path(answers_file).expanduser())
            except (FileNotFoundError, ValueError) as exc:
                print(str(exc), file=sys.stderr)
                return 1
        return _cognition_command(
            args.cognition_action,
            getattr(args, "path", "."),
            write=getattr(args, "write", False),
            overwrite=getattr(args, "overwrite", False),
            answers=answers,
        )
    if args.command == "setup":
        fallback_answers = None
        fallback_answers_file = getattr(args, "answers_file", None)
        if fallback_answers_file:
            try:
                fallback_answers = _load_answers_file(Path(fallback_answers_file).expanduser())
            except (FileNotFoundError, ValueError) as exc:
                print(str(exc), file=sys.stderr)
                return 1

        profile_answers = fallback_answers
        profile_answers_file = getattr(args, "profile_answers_file", None)
        if profile_answers_file:
            try:
                profile_answers = _load_answers_file(Path(profile_answers_file).expanduser())
            except (FileNotFoundError, ValueError) as exc:
                print(str(exc), file=sys.stderr)
                return 1

        cognition_answers = fallback_answers
        cognition_answers_file = getattr(args, "cognition_answers_file", None)
        if cognition_answers_file:
            try:
                cognition_answers = _load_answers_file(Path(cognition_answers_file).expanduser())
            except (FileNotFoundError, ValueError) as exc:
                print(str(exc), file=sys.stderr)
                return 1

        return _setup_command(
            path_arg=getattr(args, "path", "."),
            profile_mode=getattr(args, "profile_mode", None),
            cognition_mode=getattr(args, "cognition_mode", None),
            governance_mode=getattr(args, "governance_pack", "balanced"),
            write=getattr(args, "write", False),
            overwrite=getattr(args, "overwrite", False),
            do_sync=getattr(args, "sync", False),
            do_doctor=getattr(args, "doctor", False),
            profile_answers=profile_answers,
            cognition_answers=cognition_answers,
            interactive=getattr(args, "interactive", False),
        )
    if args.command == "worktree":
        return _worktree(args.task_type, args.task_name, args.base_ref, Path.cwd())
    if args.command == "private-skill":
        return _private_skill(args.action, args.name, args.tool)
    if args.command == "start":
        return _start(args.tool, Path.cwd())
    if args.command == "viewer":
        from episteme.viewer.server import serve
        return serve(host=args.host, port=args.port)
    if args.command == "capture":
        from episteme.capture import run_capture
        return run_capture(
            input_path=args.input,
            output_path=args.output,
            captured_by=args.captured_by,
            core_question=args.core_question,
            friction=args.friction,
            print_only=args.print_only,
        )
    if args.command == "evolve":
        if args.evolve_action == "run":
            return _evolve_run(
                hypothesis=args.hypothesis,
                mutation_type=args.mutation_type,
                target=args.target,
                expected_effect=args.expected_effect,
                diff_text=args.diff,
                risk_level=args.risk_level,
                suite_ref=args.suite_ref,
                seed=args.seed,
                captured_by=args.captured_by,
            )
        if args.evolve_action == "report":
            return _evolve_report(args.episode_id)
        if args.evolve_action == "promote":
            return _evolve_promote(args.episode_id, force=getattr(args, "force", False))
        if args.evolve_action == "rollback":
            return _evolve_rollback(args.episode_id, rollback_ref=getattr(args, "ref"))
        if args.evolve_action == "friction":
            td_raw = getattr(args, "telemetry_dir", None)
            out_raw = getattr(args, "output", None)
            return _evolve_friction(
                telemetry_dir=Path(td_raw).expanduser() if td_raw else None,
                output_path=Path(out_raw).expanduser() if out_raw else None,
                top_n=getattr(args, "top", 5),
            )
        return 0
    if args.command == "bridge":
        if args.bridge_action == "anthropic-managed":
            input_path = Path(getattr(args, "input")).expanduser()
            output_raw = getattr(args, "output", None)
            output_path = Path(output_raw).expanduser() if output_raw else None
            return _bridge_anthropic_managed(
                input_path=input_path,
                output_path=output_path,
                session_id=getattr(args, "session_id", None),
                project_id=getattr(args, "project_id", None),
                source_ref=getattr(args, "source_ref", None),
                captured_by=getattr(args, "captured_by", "episteme bridge"),
                confidence=getattr(args, "confidence", "medium"),
                dry_run=bool(getattr(args, "dry_run", False)),
            )
        if args.bridge_action == "substrate":
            return _bridge_substrate_dispatch(args)
        return 0
    if args.command == "inject":
        return _inject(
            target=getattr(args, "path", Path(".")),
            strict=not getattr(args, "no_strict", False),
        )
    if args.command == "log":
        return _surface_log(
            limit=getattr(args, "limit", 50),
            blocked_only=getattr(args, "blocked", False),
        )
    if args.command == "audit":
        return _audit(fix=getattr(args, "fix", False))
    if args.command == "chain":
        return _chain_dispatch(args)
    if args.command == "review":
        return _review_dispatch(args)
    if args.command == "guide":
        return _guide_dispatch(args)
    if args.command == "kernel":
        if args.kernel_action == "verify":
            return _kernel_verify()
        if args.kernel_action == "update":
            return _kernel_update()
        return 0
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
