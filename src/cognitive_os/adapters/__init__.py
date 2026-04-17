"""Per-runtime adapters. Each module exposes a `sync()` entry point that
mounts the kernel into that runtime's native context-loading mechanism.

The kernel is vendor-neutral; adapters are the only place where runtime-
specific knowledge lives.
"""
