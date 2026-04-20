"""Minimal read-only dashboard over the episteme repo.

Stdlib only. Serves on localhost; binds 127.0.0.1 by default so the viewer is
not reachable from the network without explicit --host. Endpoints:

  GET /                               dashboard (renders index.html)
  GET /api/overview                   JSON: kernel files + doc counts + latest benchmark
  GET /api/profile                    JSON: operator profile scorecard (if generated)
  GET /api/reasoning-surfaces         JSON: recent reasoning-surface.json files discovered under the repo
  GET /api/demos                      JSON: demos/ index
  GET /api/substrate                  JSON: noop substrate contents grouped by scope
  GET /api/benchmarks                 JSON: latest RESULTS.json
  GET /static/<file>                  CSS/JS assets
  GET /raw/<repo-relative-path>       Raw text of a file (whitelisted dirs only)
"""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit


REPO_ROOT = Path(__file__).resolve().parents[3]
VIEWER_DIR = Path(__file__).resolve().parent

# Whitelist of repo-relative path prefixes that `/raw/<path>` may read.
RAW_PREFIXES = (
    "kernel",
    "docs",
    "demos",
    "benchmarks",
    "core/memory/global/.generated",
    "core/memory/substrates/noop",
    "core/schemas",
)


def _safe_read(path: Path, limit: int = 4_000_000) -> str:
    if not path.exists() or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def _find_reasoning_surfaces() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in sorted(REPO_ROOT.rglob("reasoning-surface.json"))[:50]:
        if ".git" in p.parts or "node_modules" in p.parts:
            continue
        rel = str(p.relative_to(REPO_ROOT))
        try:
            payload = json.loads(_safe_read(p))
        except json.JSONDecodeError:
            payload = None
        out.append({
            "path": rel,
            "core_question": (payload or {}).get("core_question") if isinstance(payload, dict) else None,
            "size_bytes": p.stat().st_size,
        })
    return out


def _operator_profile() -> dict[str, Any]:
    gen = REPO_ROOT / "core" / "memory" / "global" / ".generated"
    scores_file = gen / "workstyle_scores.json"
    profile_file = gen / "workstyle_profile.json"
    return {
        "scores": json.loads(_safe_read(scores_file) or "null"),
        "profile": json.loads(_safe_read(profile_file) or "null"),
    }


def _demos_index() -> list[dict[str, Any]]:
    demos_dir = REPO_ROOT / "demos"
    out: list[dict[str, Any]] = []
    if not demos_dir.exists():
        return out
    for d in sorted(demos_dir.iterdir()):
        if not d.is_dir():
            continue
        out.append({
            "id": d.name,
            "has_reasoning_surface": (d / "reasoning-surface.json").exists(),
            "has_decision_trace": (d / "decision-trace.md").exists(),
            "has_verification": (d / "verification.md").exists(),
            "has_handoff": (d / "handoff.md").exists(),
            "readme_present": (d / "README.md").exists(),
        })
    return out


def _substrate_noop_index() -> list[dict[str, Any]]:
    root = REPO_ROOT / "core" / "memory" / "substrates" / "noop"
    groups: list[dict[str, Any]] = []
    if not root.exists():
        return groups
    for scope_dir in sorted(root.iterdir()):
        if not scope_dir.is_dir():
            continue
        records = sorted(scope_dir.glob("*.json"), reverse=True)[:20]
        groups.append({
            "scope": scope_dir.name,
            "count": sum(1 for _ in scope_dir.glob("*.json")),
            "recent": [str(p.relative_to(REPO_ROOT)) for p in records],
        })
    return groups


def _latest_benchmark() -> dict[str, Any] | None:
    path = REPO_ROOT / "benchmarks" / "kernel_v1" / "RESULTS.json"
    if not path.exists():
        return None
    try:
        return json.loads(_safe_read(path))
    except json.JSONDecodeError:
        return None


def _overview() -> dict[str, Any]:
    kernel_dir = REPO_ROOT / "kernel"
    docs_dir = REPO_ROOT / "docs"
    return {
        "kernel_files": sorted(p.name for p in kernel_dir.glob("*.md")) if kernel_dir.exists() else [],
        "doc_count": sum(1 for _ in docs_dir.glob("*.md")) if docs_dir.exists() else 0,
        "demos_count": len(_demos_index()),
        "benchmark": _latest_benchmark(),
    }


class _Handler(BaseHTTPRequestHandler):
    server_version = "episteme-viewer/0.1"

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        # Quiet by default; the viewer is meant to be a background utility.
        return

    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, status: int, body: str, mime: str = "text/html; charset=utf-8") -> None:
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        path = parsed.path

        routes: dict[str, Callable[[], Any]] = {
            "/api/overview": _overview,
            "/api/profile": _operator_profile,
            "/api/reasoning-surfaces": _find_reasoning_surfaces,
            "/api/demos": _demos_index,
            "/api/substrate": _substrate_noop_index,
            "/api/benchmarks": lambda: _latest_benchmark() or {},
        }
        if path in routes:
            self._send_json(200, routes[path]())
            return

        if path == "/" or path == "/index.html":
            html_body = _safe_read(VIEWER_DIR / "index.html")
            self._send_text(200, html_body or "<h1>episteme viewer</h1><p>index.html missing</p>")
            return

        if path.startswith("/static/"):
            rel = path[len("/static/"):]
            asset = VIEWER_DIR / rel
            if not asset.exists() or ".." in rel:
                self._send_text(404, "not found", "text/plain")
                return
            mime, _ = mimetypes.guess_type(str(asset))
            self._send_text(200, _safe_read(asset), mime or "application/octet-stream")
            return

        if path.startswith("/raw/"):
            rel = path[len("/raw/"):]
            if ".." in rel or rel.startswith("/"):
                self._send_text(400, "bad path", "text/plain")
                return
            if not any(rel.startswith(prefix) for prefix in RAW_PREFIXES):
                self._send_text(403, "path not in whitelist", "text/plain")
                return
            target = (REPO_ROOT / rel).resolve()
            if REPO_ROOT not in target.parents and target != REPO_ROOT:
                self._send_text(403, "outside repo", "text/plain")
                return
            content = _safe_read(target)
            if not content:
                self._send_text(404, "empty or missing", "text/plain")
                return
            self._send_text(200, f"<pre>{html.escape(content)}</pre>")
            return

        self._send_text(404, "not found", "text/plain")


def serve(host: str = "127.0.0.1", port: int = 37776) -> int:
    server = ThreadingHTTPServer((host, port), _Handler)
    print(f"episteme viewer: http://{host}:{port}/")
    print("(Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
        return 0
    finally:
        server.server_close()
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=37776)
    args = p.parse_args()
    return serve(host=args.host, port=args.port)


if __name__ == "__main__":
    raise SystemExit(main())
