"""Local viewer — read-only HTTP dashboard over ~/episteme.

Stdlib-only (http.server). No JS framework, no external deps. Exists so the
operator profile, recent reasoning surfaces, demo artifacts, benchmark results,
and substrate push/pull history are inspectable without grepping the filesystem.
"""

from .server import serve  # noqa: F401
