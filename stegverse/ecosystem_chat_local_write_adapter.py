"""Deterministic local write adapter for Ecosystem Chat.

This adapter is not used by the default pipeline. It must be injected explicitly.
"""

from __future__ import annotations

import hashlib

from .ecosystem_chat_write_adapter import WriteResult


class LocalEcosystemChatWriteAdapter:
    adapter_name = "LOCAL_ECOSYSTEM_CHAT_WRITE_ADAPTER"

    def write(self, persistence_plan: dict) -> WriteResult:
        if persistence_plan.get("persistence_status") != "PERSISTENCE_PENDING":
            return WriteResult(
                write_complete=False,
                write_id=None,
                adapter_name=self.adapter_name,
                receipt_id=persistence_plan.get("receipt_id"),
                errors=["persistence plan is not eligible for local write"],
            )

        receipt_id = persistence_plan.get("receipt_id")
        persistence_hash = persistence_plan.get("persistence_hash")
        if not isinstance(receipt_id, str) or not receipt_id:
            return self._deny(persistence_plan, "receipt_id is missing or invalid")
        if not isinstance(persistence_hash, str) or not persistence_hash.startswith("sha256:"):
            return self._deny(persistence_plan, "persistence_hash is missing or invalid")

        return WriteResult(
            write_complete=True,
            write_id=_write_id(receipt_id, persistence_hash),
            adapter_name=self.adapter_name,
            receipt_id=receipt_id,
            errors=[],
        )

    def _deny(self, persistence_plan: dict, message: str) -> WriteResult:
        return WriteResult(
            write_complete=False,
            write_id=None,
            adapter_name=self.adapter_name,
            receipt_id=persistence_plan.get("receipt_id"),
            errors=[message],
        )


def _write_id(receipt_id: str, persistence_hash: str) -> str:
    digest = hashlib.sha256(f"{receipt_id}:{persistence_hash}".encode("utf-8")).hexdigest()
    return "ecw-local-" + digest[:24]
