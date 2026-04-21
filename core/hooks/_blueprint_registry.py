#!/usr/bin/env python3
"""Blueprint registry — v1.0 RC CP2 scaffolding.

Loads Cognitive Blueprint definitions from `core/blueprints/*.yaml` and
exposes them by name. Pure read. No synthesis, no field-contract
enforcement beyond structural well-formedness — deep field validation
per blueprint class lands at CP5 (Fence Reconstruction) / CP6 (schema
shapes for A + C + D) / CP10 (Architectural Cascade).

## Why this module exists

The v1.0 RC spec makes the Reasoning Surface scenario-polymorphic
(spec § Pillar 1 · Cognitive Blueprints). The hot path at CP3 will call
`_scenario_detector.detect_scenario(...)` to pick a blueprint name, then
consult this registry for the chosen blueprint's required-field
contract. The contract is the shape Layer 2 / 3 / 4 / 6 / 8 validate
against when the blueprint fires; when no blueprint fires, the generic
fallback's four fields apply.

At CP2 the hot path does NOT yet consult either module — CP2 is
substrate only. The scenario detector always returns "generic," the
registry loads one blueprint (generic_fallback), and
`reasoning_surface_guard.py` remains unchanged.

## Zero-dependency YAML parser

The spec names YAML as the blueprint file format, but
`pyproject.toml` maintains `dependencies = []` as a load-bearing
invariant (see Phase 9 / `_derived_knobs.py` rationale — PyYAML was
explicitly rejected to keep install footprint minimal and attack
surface shallow). We therefore hand-roll a minimal YAML-subset parser
covering the exact shapes v1.0 RC blueprints use:

- Top-level `key: value` pairs with scalar values (str, int, bool, null)
- Block-folded strings (`>` — newlines collapse to spaces)
- Block-literal strings (`|` — newlines preserved)
- Block lists (`- item` indented under a key) of scalars
- Inline empty list (`[]`) and inline empty dict (`{}`)
- Comments (`#` line-level) and blank lines

Not supported at CP2 (raises `BlueprintParseError`):

- Lists of dicts (CP5 adds this for Fence Reconstruction's
  `selector_triggers` shape)
- Nested maps beyond top level
- Inline non-empty lists / dicts
- YAML anchors / aliases / merge keys

The parser grows per-CP as blueprints declare new shapes. No
speculative shape support — every extension lands with the blueprint
that needs it.

## Registry discipline

- Load is lazy + cached. First call reads the directory; subsequent
  calls return the cached instances.
- Duplicate blueprint names (two files with the same `name:`) are a
  registry-load error. The registry refuses to guess which wins.
- A missing `core/blueprints/` directory yields an empty registry
  (not an error) — supports downstream forks that install without
  the blueprints directory and fall back to generic validation only.

Spec: `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § Pillar 1 · Cognitive
Blueprints § Blueprint registry governance.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
BLUEPRINTS_DIR = REPO_ROOT / "core" / "blueprints"


class BlueprintParseError(ValueError):
    """Raised when a blueprint YAML file fails structural parsing."""


class BlueprintValidationError(ValueError):
    """Raised when a blueprint is structurally parseable but violates
    CP2's minimum contract (non-empty `name`, list-typed
    `required_fields`). Deep per-blueprint field validation lands at
    CP5 / CP6 / CP10."""


@dataclass(frozen=True)
class Blueprint:
    """A loaded blueprint definition. CP2 shape — CP5+ may add fields
    (e.g. `selector_trigger_specs`, `synthesis_field_specs`). New fields
    are optional at load time until a hot-path consumer requires them."""

    name: str
    description: str
    version: int
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]
    synthesis_arm: bool
    selector_triggers: tuple[Any, ...]
    source_path: Path


# ---------------------------------------------------------------------------
# YAML subset parser
# ---------------------------------------------------------------------------

_TOP_LEVEL_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*?)\s*$")
_LIST_ITEM_RE = re.compile(r"^\s+-\s+(.+?)\s*$")


def _parse_scalar(value: str) -> Any:
    """Parse a YAML scalar literal. Order matters: quoted string first,
    then bool, null, int, float, bare string."""
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        return value[1:-1]
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        return value[1:-1]
    lower = value.lower()
    if lower in ("true", "yes"):
        return True
    if lower in ("false", "no"):
        return False
    if lower in ("null", "~", ""):
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def _parse_block_list(
    lines: list[str], start: int, *, source: Path
) -> tuple[list, int]:
    """Consume an indented block list starting at `start`. Returns the
    list contents and the index of the first line BEYOND the block."""
    items: list = []
    j = start
    while j < len(lines):
        raw = lines[j]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            j += 1
            continue
        list_match = _LIST_ITEM_RE.match(raw)
        if list_match:
            items.append(_parse_scalar(list_match.group(1)))
            j += 1
            continue
        if re.match(r"^\S", raw):
            # new top-level key — block ends here
            return items, j
        raise BlueprintParseError(
            f"{source}:{j + 1}: unsupported shape inside block list: {raw!r}. "
            f"CP2 parser handles scalar list items only; lists of dicts land at CP5+."
        )
    return items, j


def _parse_block_scalar(
    lines: list[str], start: int, *, folded: bool
) -> tuple[str, int]:
    """Consume an indented block-scalar body (after `>` or `|`). Returns
    the joined string and the index of the first line BEYOND the block."""
    collected: list[str] = []
    j = start
    while j < len(lines):
        raw = lines[j]
        if not raw.strip():
            if not folded:
                collected.append("")
            j += 1
            continue
        if re.match(r"^\S", raw):
            # new top-level key — block ends
            break
        collected.append(raw.strip())
        j += 1
    if folded:
        return " ".join(collected), j
    return "\n".join(collected), j


def _parse_yaml_subset(text: str, *, source: Path) -> dict:
    """Parse a subset of YAML sufficient for v1.0 RC CP2 blueprints.
    See module docstring § Zero-dependency YAML parser for the exact
    feature set."""
    result: dict = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        match = _TOP_LEVEL_KEY_RE.match(raw)
        if not match:
            raise BlueprintParseError(
                f"{source}:{i + 1}: could not parse as top-level `key: value`: {raw!r}"
            )
        key, rest = match.group(1), match.group(2)

        if key in result:
            raise BlueprintParseError(
                f"{source}:{i + 1}: duplicate top-level key `{key}`"
            )

        # empty value → block structure follows (block list or block scalar
        # marker; but block scalars are only valid when rest is `>` or `|`).
        if rest == "":
            block, next_i = _parse_block_list(lines, i + 1, source=source)
            result[key] = block
            i = next_i
            continue

        # block scalar markers
        if rest in (">", "|"):
            value, next_i = _parse_block_scalar(lines, i + 1, folded=(rest == ">"))
            result[key] = value
            i = next_i
            continue

        # inline empty list / dict
        if rest == "[]":
            result[key] = []
            i += 1
            continue
        if rest == "{}":
            result[key] = {}
            i += 1
            continue

        # inline non-empty list / dict / flow style — not supported at CP2
        if rest.startswith("[") or rest.startswith("{"):
            raise BlueprintParseError(
                f"{source}:{i + 1}: inline flow style ({rest!r}) not supported "
                f"at CP2; use block form or wait for CP5+ parser extension."
            )

        # bare scalar value
        result[key] = _parse_scalar(rest)
        i += 1

    return result


# ---------------------------------------------------------------------------
# Validation + construction
# ---------------------------------------------------------------------------


def _validate_and_construct(data: dict, *, source: Path) -> Blueprint:
    """CP2 minimum validation: `name` is a non-empty string;
    `required_fields`, `optional_fields`, `selector_triggers` are lists
    when present. Deep per-blueprint field validation (e.g. Fence
    Reconstruction requires `origin_evidence`, Blueprint D requires
    `blast_radius_map`) lands at CP5 / CP10. `data` is guaranteed to be
    a dict by `_parse_yaml_subset` — no defensive type-check needed."""
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise BlueprintValidationError(
            f"{source}: blueprint must declare a non-empty string `name`"
        )

    required = data.get("required_fields", [])
    if not isinstance(required, list):
        raise BlueprintValidationError(
            f"{source}: `required_fields` must be a list (got {type(required).__name__})"
        )

    optional = data.get("optional_fields", [])
    if not isinstance(optional, list):
        raise BlueprintValidationError(
            f"{source}: `optional_fields` must be a list (got {type(optional).__name__})"
        )

    selector_triggers = data.get("selector_triggers", [])
    if not isinstance(selector_triggers, list):
        raise BlueprintValidationError(
            f"{source}: `selector_triggers` must be a list "
            f"(got {type(selector_triggers).__name__})"
        )

    version = data.get("version", 1)
    if not isinstance(version, int):
        raise BlueprintValidationError(
            f"{source}: `version` must be an integer (got {type(version).__name__})"
        )

    return Blueprint(
        name=name.strip(),
        description=str(data.get("description", "")).strip(),
        version=version,
        required_fields=tuple(str(f) for f in required),
        optional_fields=tuple(str(f) for f in optional),
        synthesis_arm=bool(data.get("synthesis_arm", False)),
        selector_triggers=tuple(selector_triggers),
        source_path=source,
    )


def _load_file(path: Path) -> Blueprint:
    """Load a single blueprint YAML file."""
    if not path.is_file():
        raise BlueprintParseError(f"{path}: not a file")
    text = path.read_text(encoding="utf-8")
    data = _parse_yaml_subset(text, source=path)
    return _validate_and_construct(data, source=path)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class Registry:
    """Lazy-loaded blueprint registry. First call to `.get()` /
    `.known_names()` scans the directory; subsequent calls hit the
    cache. A non-existent directory yields an empty registry (not an
    error — supports forks that install without a blueprints
    directory)."""

    def __init__(self, blueprints_dir: Path = BLUEPRINTS_DIR) -> None:
        self._dir = blueprints_dir
        self._cache: dict[str, Blueprint] | None = None

    def _load(self) -> dict[str, Blueprint]:
        if self._cache is not None:
            return self._cache
        registry: dict[str, Blueprint] = {}
        if not self._dir.is_dir():
            self._cache = registry
            return registry
        for yaml_path in sorted(self._dir.glob("*.yaml")):
            blueprint = _load_file(yaml_path)
            if blueprint.name in registry:
                raise BlueprintValidationError(
                    f"duplicate blueprint name `{blueprint.name}` declared in "
                    f"{yaml_path}; first seen at {registry[blueprint.name].source_path}"
                )
            registry[blueprint.name] = blueprint
        self._cache = registry
        return registry

    def get(self, name: str) -> Blueprint:
        registry = self._load()
        if name not in registry:
            raise KeyError(
                f"blueprint `{name}` not found; known: {sorted(registry.keys())}"
            )
        return registry[name]

    def known_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._load().keys()))

    def reload(self) -> None:
        """Force a re-scan of the blueprints directory. Primarily for
        tests; production callers rely on the lazy-init path."""
        self._cache = None


_default_registry: Registry | None = None


def load_registry(blueprints_dir: Path | None = None) -> Registry:
    """Return a registry. Without an explicit directory, returns a
    process-wide singleton pointed at `core/blueprints/`. With an
    explicit directory, returns a fresh instance (for tests)."""
    global _default_registry
    if blueprints_dir is not None:
        return Registry(blueprints_dir)
    if _default_registry is None:
        _default_registry = Registry()
    return _default_registry
