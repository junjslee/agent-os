"""Adapter discovery.

Adapters are python modules under `episteme.bridges.substrate.adapters`.
Each module must expose a top-level `ADAPTER: type[SubstrateAdapter]`.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import Type

from .base import SubstrateAdapter


_ADAPTERS_PACKAGE = "episteme.bridges.substrate.adapters"


def list_adapters() -> list[str]:
    pkg = importlib.import_module(_ADAPTERS_PACKAGE)
    return sorted(
        name
        for _, name, is_pkg in pkgutil.iter_modules(pkg.__path__)
        if not is_pkg and not name.startswith("_")
    )


def load_adapter(name: str, config: dict | None = None) -> SubstrateAdapter:
    if name not in list_adapters():
        available = ", ".join(list_adapters()) or "(none installed)"
        raise ValueError(f"unknown substrate adapter: {name!r}. available: {available}")
    module = importlib.import_module(f"{_ADAPTERS_PACKAGE}.{name}")
    adapter_cls: Type[SubstrateAdapter] = getattr(module, "ADAPTER", None)
    if adapter_cls is None:
        raise ValueError(f"adapter module {name!r} does not export ADAPTER class")
    return adapter_cls(config or {})
