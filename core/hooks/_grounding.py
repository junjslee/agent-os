"""Layer 3 · v1.0 RC CP4 — contextual grounding (blueprint-aware).

Runs AFTER Layer 2 in the hot path. For each blueprint-declared grounded
field (generic: `disconfirmation`, `unknowns`), extracts entity-shaped
tokens and checks whether they exist in the project working tree. Gate
is FP-averse per `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § Layer 3:

  reject   : grounded >= 2 AND (not_found / named) > 0.5
  advisory : some entities ungrounded but gate not crossed
  pass     : no entities extracted, all entities ground, or fresh-repo
             sparse-context (grounded < 2 AND at least one grounds).

FP discipline — every extractor requires a structural marker absent from
normal English prose:

  snake_case       mandatory `_` between lowercase groups
  SCREAMING_CASE   mandatory `_` between uppercase groups
  path_with_ext    recognised code / config extension after a `.`
  hex_sha          7-40 hex chars with at least one digit AND one letter

Single-word English ("velocity", "baseline", "migration", "build",
"results") does NOT extract as an entity. Raw numeric tokens ("60%",
"400ms") are intentionally omitted — real metric identifiers land via
snake_case (`latency_p95`) or SCREAMING_CASE (`P95_LATENCY`).

In-process warm cache keyed on (cwd, newest-tracked-file mtime). The
cache has no persistence; graceful degrade on any IO exception never
crashes the hot path.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


# ---------- Entity extractors (FP-averse) ---------------------------------

# snake_case: lowercase letter, then at least one `_segment`. Requires `_`.
_SNAKE_CASE_RE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")

# SCREAMING_CASE: uppercase letter, then at least one `_SEGMENT`. Requires `_`.
# Filters common acronyms (CI, API, URL, AWS) that lack underscores.
_SCREAMING_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")

# Path with known code / config extension. Narrow list to avoid matching
# "e.g." or "U.S.A" as file paths.
_CODE_EXTS = (
    "py", "md", "yaml", "yml", "json", "toml", "sh", "js", "ts", "jsx", "tsx",
    "go", "rs", "java", "cpp", "hpp", "c", "h", "sql", "css", "html",
    "ini", "cfg", "conf", "lock", "txt", "rst", "xml", "proto",
)
_PATH_EXT_RE = re.compile(
    r"\b[A-Za-z0-9_\-/]+\.(?:" + "|".join(_CODE_EXTS) + r")\b"
)

# Hex SHA: 7-40 hex chars, MUST contain at least one digit AND one letter.
# The dual lookahead filters all-digit page numbers ("1234567") and
# all-letter English hex words like "acceded".
_HEX_SHA_RE = re.compile(
    r"\b(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b"
)


def extract_entities(text: str) -> set[str]:
    """Return the FP-averse entity set found in `text`.

    Four extractors, each requiring a structural marker absent from
    normal English prose. See module docstring for the FP discipline.
    """
    if not text:
        return set()
    entities: set[str] = set()
    entities.update(m.group(0) for m in _SNAKE_CASE_RE.finditer(text))
    entities.update(m.group(0) for m in _SCREAMING_RE.finditer(text))
    entities.update(m.group(0) for m in _PATH_EXT_RE.finditer(text))
    entities.update(m.group(0) for m in _HEX_SHA_RE.finditer(text))
    return entities


# ---------- Project fingerprint (cached) ----------------------------------

# In-process warm cache. Keyed on (cwd, newest-tracked-file mtime). No
# on-disk persistence at CP4 — deferred until profiling shows in-process
# insufficient.
_CACHE: dict[tuple[str, int], tuple[frozenset[str], bytes]] = {}

_CONTENT_TOTAL_CAP = 2_000_000   # 2 MB across all scanned files
_PER_FILE_CAP = 64 * 1024        # 64 KB per file
_MAX_FILES_SCANNED = 500         # project-content scan cap
_GIT_LS_TIMEOUT = 5              # seconds


def _git_ls_files(cwd: Path) -> list[str] | None:
    """Return git-tracked file list, or None when git is unavailable."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=_GIT_LS_TIMEOUT,
            check=False,
        )
        if result.returncode != 0:
            return None
        return [line for line in result.stdout.splitlines() if line.strip()]
    except (OSError, subprocess.TimeoutExpired, subprocess.SubprocessError):
        return None


def _os_walk_files(cwd: Path) -> list[str]:
    """Non-git fallback file list, bounded. Skips hidden dirs / files."""
    out: list[str] = []
    try:
        cwd_resolved = cwd.resolve()
        for root, dirs, files in os.walk(str(cwd_resolved)):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for name in files:
                if name.startswith("."):
                    continue
                try:
                    rel = str(Path(root, name).relative_to(cwd_resolved))
                except ValueError:
                    continue
                out.append(rel)
                if len(out) >= _MAX_FILES_SCANNED:
                    return out
    except OSError:
        pass
    return out


def _newest_mtime(cwd: Path, files: list[str]) -> int:
    """Compute a stable cache key from the newest file mtime in the sample."""
    if not files:
        return 0
    m = 0
    for f in files[:100]:
        try:
            m = max(m, int((cwd / f).stat().st_mtime))
        except OSError:
            continue
    return m


def _load_project_fingerprint(cwd: Path) -> tuple[frozenset[str], bytes]:
    """Return (filename-set, bounded-content-blob) for the project at cwd.

    Cached in-process by (cwd, newest-mtime). Graceful degrade on IO
    errors — an unreadable file is skipped; an unreadable project returns
    empty sets.
    """
    files = _git_ls_files(cwd)
    if files is None:
        files = _os_walk_files(cwd)

    mtime_key = _newest_mtime(cwd, files)
    cache_key = (str(cwd.resolve()) if cwd.exists() else str(cwd), mtime_key)
    cached = _CACHE.get(cache_key)
    if cached is not None:
        return cached

    filenames: set[str] = set()
    for f in files:
        filenames.add(f)
        filenames.add(Path(f).name)

    content_parts: list[bytes] = []
    total = 0
    for f in files[:_MAX_FILES_SCANNED]:
        if total >= _CONTENT_TOTAL_CAP:
            break
        try:
            with open(cwd / f, "rb") as fh:
                blob = fh.read(_PER_FILE_CAP)
        except (OSError, FileNotFoundError):
            continue
        content_parts.append(blob)
        total += len(blob)

    entry = (frozenset(filenames), b"\n".join(content_parts))
    _CACHE[cache_key] = entry
    return entry


def _clear_cache_for_tests() -> None:
    """Test-only cache reset. Not exported via __all__."""
    _CACHE.clear()


def _is_grounded(entity: str, filenames: frozenset[str], content: bytes) -> bool:
    """True iff `entity` appears in project filenames or bounded content."""
    if not entity:
        return False
    if entity in filenames:
        return True
    for fn in filenames:
        if entity in fn:
            return True
    try:
        return entity.encode("utf-8") in content
    except (UnicodeEncodeError, AttributeError):
        return False


# ---------- Gate & verdict ------------------------------------------------

# Per-blueprint declaration of which fields Layer 3 runs grounding against.
# Mirrors CP3's `_CLASSIFIED_FIELDS_BY_BLUEPRINT` pattern (inlined, not
# YAML-driven, to keep the registry parser stable at CP4). Generic
# blueprint grounds the same fields Layer 2 classifies — the composition
# cost is: Layer 2 forces trigger + observable vocabulary, Layer 3 then
# forces those observables to be real project entities. CP5 (Fence
# Reconstruction) adds a `constraint_identified` grounding entry.
_GROUNDED_FIELDS_BY_BLUEPRINT: dict[str, tuple[str, ...]] = {
    "generic": ("disconfirmation", "unknowns"),
    # CP5: Fence grounds `constraint_identified` to a real project
    # file (spec § Blueprint B: "line-level precision"). Disconfirmation
    # + unknowns carry through from generic so the compose-across-layers
    # discipline applies equally on Fence surfaces.
    "fence_reconstruction": (
        "disconfirmation",
        "unknowns",
        "constraint_identified",
    ),
}


def _collect_entities(surface: dict, field_names: tuple[str, ...]) -> set[str]:
    """Union of entities extracted from each named field on the surface."""
    entities: set[str] = set()
    for field in field_names:
        value = surface.get(field)
        if isinstance(value, str):
            entities.update(extract_entities(value))
        elif isinstance(value, list):
            for entry in value:
                if isinstance(entry, str):
                    entities.update(extract_entities(entry))
    return entities


def layer3_verdict_from_counts(n_named: int, n_grounded: int) -> str:
    """Pure verdict function. Exported for direct unit testing.

    Per spec § Layer 3:
      reject   : grounded >= 2 AND (not_found / named) > 0.5
      pass     : n_named == 0, or n_not_found == 0 (all ground)
      advisory : some entities ungrounded but gate not crossed
    """
    if n_named == 0:
        return "pass"
    n_not_found = n_named - n_grounded
    if n_not_found == 0:
        return "pass"
    if n_grounded >= 2 and (n_not_found / n_named) > 0.5:
        return "reject"
    return "advisory"


def ground_blueprint_fields(
    surface: dict,
    blueprint_name: str,
    cwd: Path,
) -> tuple[str, str]:
    """Return ("pass" | "advisory" | "reject", detail).

    Graceful degrade: any IO exception yields ("pass", "<note>"); the
    caller decides whether to emit the note to stderr as a fallback.
    """
    field_set = _GROUNDED_FIELDS_BY_BLUEPRINT.get(
        blueprint_name, _GROUNDED_FIELDS_BY_BLUEPRINT["generic"]
    )
    named = _collect_entities(surface, field_set)
    if not named:
        return ("pass", "")

    try:
        filenames, content = _load_project_fingerprint(cwd)
    except OSError as exc:
        return ("pass", f"Layer 3 fallback (IO error: {exc.__class__.__name__})")

    grounded = {e for e in named if _is_grounded(e, filenames, content)}
    n_named = len(named)
    n_grounded = len(grounded)
    verdict = layer3_verdict_from_counts(n_named, n_grounded)
    not_found = sorted(named - grounded)

    if verdict == "reject":
        sample = ", ".join(not_found[:5])
        suffix = " ..." if len(not_found) > 5 else ""
        detail = (
            f"Layer 3 grounding (blueprint `{blueprint_name}`) rejected: "
            f"{n_named} entities named; {n_grounded} grounded; "
            f"{n_named - n_grounded} not found in project tree: "
            f"{sample}{suffix}. Claims reference entities that do not "
            "exist in this project. Name real file paths, snake_case "
            "identifiers, SCREAMING_CASE env vars, or git SHAs that grep "
            "to the working tree."
        )
        return ("reject", detail)

    if verdict == "advisory":
        sample = ", ".join(not_found[:3])
        suffix = " ..." if len(not_found) > 3 else ""
        detail = (
            f"Layer 3 grounding (blueprint `{blueprint_name}`) advisory: "
            f"{n_named - n_grounded} of {n_named} named entities not found: "
            f"{sample}{suffix}. Consider grounding to real project entities."
        )
        return ("advisory", detail)

    return ("pass", "")
