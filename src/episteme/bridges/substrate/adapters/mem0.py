"""Mem0 adapter — POST /v1/memories on the Mem0 cloud API.

Requires `MEM0_API_KEY` in the environment (or `config["api_key"]`). Uses only
stdlib `urllib` — no extra runtime dependency. Degrades cleanly: every record
that the substrate cannot accept becomes a PushResult.skipped entry, not a
silent drop.

Lossy fields declared explicitly: Mem0 does not persist memory-contract
provenance fields natively, so `captured_by`, `confidence`, `evidence_refs`,
and `status` are sent in metadata but not used for Mem0's internal ranking.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from ..base import AdapterDescriptor, PullQuery, PushResult, ScopeMap, SubstrateAdapter


_DEFAULT_BASE_URL = "https://api.mem0.ai"


class Mem0Adapter(SubstrateAdapter):
    name = "mem0"

    def __init__(self, config: dict | None = None) -> None:
        cfg = config or {}
        self.api_key = cfg.get("api_key") or os.environ.get("MEM0_API_KEY")
        self.base_url = (cfg.get("base_url") or _DEFAULT_BASE_URL).rstrip("/")
        self.timeout = float(cfg.get("timeout", 30.0))

    def describe(self) -> AdapterDescriptor:
        return AdapterDescriptor(
            name=self.name,
            version="1.0.0",
            substrate={
                "name": "mem0",
                "homepage": "https://mem0.ai",
                "transport": "rest",
            },
            capabilities={
                "push": True,
                "pull": True,
                "delete": True,
                "update": False,
                "search": True,
                "filter_by_scope": True,
                "preserve_provenance": False,
                "native_entity_linking": True,
            },
            scope_keys=["user_id", "agent_id", "run_id", "app_id", "org_id", "project_id"],
            lossy_fields=["provenance.captured_by", "provenance.confidence", "provenance.evidence_refs", "status"],
            config_schema={
                "type": "object",
                "properties": {
                    "api_key": {"type": "string"},
                    "base_url": {"type": "string"},
                    "timeout": {"type": "number"}
                },
                "additionalProperties": False,
            },
        )

    def _require_key(self) -> None:
        if not self.api_key:
            raise RuntimeError("mem0: MEM0_API_KEY not set (or pass config.api_key)")

    def _request(self, method: str, path: str, body: dict | None = None) -> Any:
        self._require_key()
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Token {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body_bytes = resp.read()
            if not body_bytes:
                return None
            return json.loads(body_bytes.decode("utf-8"))

    @staticmethod
    def _record_to_messages(record: dict[str, Any]) -> list[dict[str, str]]:
        summary = str(record.get("summary") or "").strip()
        if not summary:
            details = record.get("details") or {}
            summary = json.dumps(details, ensure_ascii=False)[:2000]
        return [{"role": "user", "content": summary}]

    def push(self, envelope: dict[str, Any], scope: ScopeMap) -> PushResult:
        result = PushResult(adapter=self.name)
        if envelope.get("contract_version") != "memory-contract-v1":
            result.failed.append({"source_id": "(envelope)", "error": "unsupported contract_version"})
            return result
        if not scope.user_id:
            result.failed.append({"source_id": "(envelope)", "error": "mem0 requires scope.user_id"})
            return result

        result.lossy = list(self.describe().lossy_fields)

        for record in envelope.get("records") or []:
            source_id = str(record.get("id") or "unknown")
            if record.get("memory_class") == "global":
                result.skipped.append({
                    "source_id": source_id,
                    "reason": "mem0 does not route global memory; kept local-only",
                })
                continue
            payload: dict[str, Any] = {
                "messages": self._record_to_messages(record),
                "user_id": scope.user_id,
                "metadata": {
                    "episteme_source_id": source_id,
                    "memory_class": record.get("memory_class"),
                    "session_id": scope.session_id,
                    "project_id": scope.project_id,
                    "provenance": record.get("provenance"),
                },
            }
            for key in ("agent_id", "run_id", "app_id", "org_id"):
                val = getattr(scope, key, None)
                if val:
                    payload[key] = val
            try:
                response = self._request("POST", "/v1/memories/", payload)
                substrate_id = None
                if isinstance(response, list) and response:
                    substrate_id = response[0].get("id")
                result.pushed.append({"source_id": source_id, "substrate_id": substrate_id})
            except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as exc:
                result.failed.append({"source_id": source_id, "error": str(exc)})
        return result

    def pull(self, query: PullQuery) -> dict[str, Any]:
        if not query.scope.user_id:
            raise RuntimeError("mem0: pull requires scope.user_id")
        params = {"user_id": query.scope.user_id, "limit": query.limit}
        if query.query:
            params["query"] = query.query
        path = "/v1/memories/search/" if query.query else "/v1/memories/"
        response = self._request("POST" if query.query else "GET", path, params if query.query else None)
        records: list[dict[str, Any]] = []
        items = response if isinstance(response, list) else (response or {}).get("results") or []
        for item in items:
            records.append({
                "id": str(item.get("id")),
                "memory_class": "episodic",
                "summary": str(item.get("memory") or item.get("text") or ""),
                "details": {"substrate": "mem0", "raw": item},
                "provenance": {
                    "source_type": "imported",
                    "source_ref": f"mem0:{item.get('id')}",
                    "captured_at": item.get("created_at"),
                    "captured_by": "episteme bridge substrate pull mem0",
                    "confidence": "medium",
                },
                "status": "active",
                "version": "memory-contract-v1",
            })
        return {"contract_version": "memory-contract-v1", "records": records}

    def delete(self, substrate_id: str) -> bool:
        try:
            self._request("DELETE", f"/v1/memories/{substrate_id}/")
            return True
        except (urllib.error.HTTPError, urllib.error.URLError):
            return False


ADAPTER = Mem0Adapter
