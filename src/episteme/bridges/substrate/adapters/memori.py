"""Memori adapter — thin wrapper over the `memori` Python SDK.

Optional dependency: `pip install memori`. If the SDK isn't importable the
adapter's constructor raises a clear error and `list_adapters` still lists it
so `verify` can surface the unmet dependency.

Memori owns attribution via (entity_id, process_id). The adapter maps
scope.user_id → entity_id and scope.agent_id → process_id. Global memory is
skipped (authoritative truth stays in episteme, never in a substrate).
"""

from __future__ import annotations

import json
from typing import Any

from ..base import AdapterDescriptor, PushResult, ScopeMap, SubstrateAdapter


class MemoriAdapter(SubstrateAdapter):
    name = "memori"

    def __init__(self, config: dict | None = None) -> None:
        cfg = config or {}
        self._cfg = cfg
        self._client = None
        try:
            import memori  # type: ignore
        except ImportError:
            self._import_error = (
                "memori: python package not installed — `pip install memori` to enable this adapter"
            )
            self._module = None
        else:
            self._import_error = None
            self._module = memori

    def describe(self) -> AdapterDescriptor:
        return AdapterDescriptor(
            name=self.name,
            version="1.0.0",
            substrate={
                "name": "memori",
                "homepage": "https://memorilabs.ai",
                "transport": "sdk",
            },
            capabilities={
                "push": True,
                "pull": False,
                "delete": False,
                "update": False,
                "search": True,
                "filter_by_scope": True,
                "preserve_provenance": False,
                "native_entity_linking": True,
            },
            scope_keys=["user_id", "agent_id", "session_id"],
            lossy_fields=["provenance.evidence_refs", "provenance.confidence", "status"],
            config_schema={
                "type": "object",
                "properties": {"database_url": {"type": "string"}, "api_key": {"type": "string"}},
                "additionalProperties": True,
            },
        )

    def _ensure_client(self) -> Any:
        if self._module is None:
            raise RuntimeError(self._import_error)
        if self._client is None:
            self._client = self._module.Memori(**self._cfg)
        return self._client

    def push(self, envelope: dict[str, Any], scope: ScopeMap) -> PushResult:
        result = PushResult(adapter=self.name)
        if envelope.get("contract_version") != "memory-contract-v1":
            result.failed.append({"source_id": "(envelope)", "error": "unsupported contract_version"})
            return result

        try:
            client = self._ensure_client()
        except RuntimeError as exc:
            result.failed.append({"source_id": "(client)", "error": str(exc)})
            return result

        result.lossy = list(self.describe().lossy_fields)
        entity_id = scope.user_id or "unknown-entity"
        process_id = scope.agent_id or "episteme"

        for record in envelope.get("records") or []:
            source_id = str(record.get("id") or "unknown")
            if record.get("memory_class") == "global":
                result.skipped.append({
                    "source_id": source_id,
                    "reason": "memori does not route global memory; kept local-only",
                })
                continue
            summary = str(record.get("summary") or "").strip()
            content = summary or json.dumps(record.get("details") or {}, ensure_ascii=False)[:2000]
            try:
                recorder = getattr(client, "record", None) or getattr(client, "add", None)
                if recorder is None:
                    raise RuntimeError("memori SDK exposes neither `record` nor `add`; check version compatibility")
                substrate_id = recorder(
                    content,
                    entity_id=entity_id,
                    process_id=process_id,
                    metadata={
                        "episteme_source_id": source_id,
                        "memory_class": record.get("memory_class"),
                        "session_id": scope.session_id,
                        "provenance": record.get("provenance"),
                    },
                )
                result.pushed.append({"source_id": source_id, "substrate_id": str(substrate_id) if substrate_id else None})
            except Exception as exc:  # noqa: BLE001 — surface any SDK error verbatim to the caller
                result.failed.append({"source_id": source_id, "error": f"{type(exc).__name__}: {exc}"})
        return result


ADAPTER = MemoriAdapter
