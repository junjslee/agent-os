"""Kernel integrity manifest.

Tracks sha256 hashes of managed kernel files so drift between shipped kernel
and the working tree is detectable. Supports `verify` (read-only check) and
`update` (rewrite manifest from current files).
"""
from __future__ import annotations

import hashlib
from pathlib import Path


MANAGED_KERNEL_FILES: tuple[str, ...] = (
    "kernel/CONSTITUTION.md",
    "kernel/FAILURE_MODES.md",
    "kernel/HOOKS_MAP.md",
    "kernel/OPERATOR_PROFILE_SCHEMA.md",
    "kernel/REASONING_SURFACE.md",
    "kernel/REFERENCES.md",
    "kernel/README.md",
)

MANIFEST_PATH = "kernel/MANIFEST.sha256"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def compute_manifest(repo_root: Path) -> dict[str, str]:
    """Return {relative_path: sha256_hex} for all managed kernel files."""
    out: dict[str, str] = {}
    for rel in MANAGED_KERNEL_FILES:
        p = repo_root / rel
        if not p.exists():
            continue
        out[rel] = _sha256(p)
    return out


def parse_manifest(text: str) -> dict[str, str]:
    """Parse `<sha256>  <path>` lines (standard shasum output)."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        digest, path = parts
        out[path.strip()] = digest.strip().lower()
    return out


def render_manifest(manifest: dict[str, str]) -> str:
    """Emit shasum-style text, sorted by path."""
    lines = [
        "# episteme kernel integrity manifest.",
        "# Regenerate with: episteme kernel update",
        "",
    ]
    for path in sorted(manifest):
        lines.append(f"{manifest[path]}  {path}")
    return "\n".join(lines) + "\n"


def read_manifest(repo_root: Path) -> dict[str, str] | None:
    path = repo_root / MANIFEST_PATH
    if not path.exists():
        return None
    try:
        return parse_manifest(path.read_text(encoding="utf-8"))
    except OSError:
        return None


def write_manifest(repo_root: Path) -> Path:
    manifest = compute_manifest(repo_root)
    path = repo_root / MANIFEST_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_manifest(manifest), encoding="utf-8")
    return path


def verify(repo_root: Path) -> tuple[bool, list[str]]:
    """Return (ok, diff_messages). ok=False if manifest missing or any drift."""
    expected = read_manifest(repo_root)
    if expected is None:
        return False, [f"manifest not found at {MANIFEST_PATH}"]

    actual = compute_manifest(repo_root)
    diffs: list[str] = []

    for rel in sorted(set(expected) | set(actual)):
        exp = expected.get(rel)
        act = actual.get(rel)
        if exp is None:
            diffs.append(f"untracked kernel file present: {rel}")
        elif act is None:
            diffs.append(f"kernel file missing: {rel}")
        elif exp != act:
            diffs.append(f"drift: {rel} (expected {exp[:12]}..., got {act[:12]}...)")

    return (not diffs), diffs


__all__ = [
    "MANAGED_KERNEL_FILES",
    "MANIFEST_PATH",
    "compute_manifest",
    "parse_manifest",
    "render_manifest",
    "read_manifest",
    "write_manifest",
    "verify",
]
