"""Destination-bound write adapter for Ecosystem Chat.

This adapter requires a ready destination binding before delegating to another
write adapter. It does not perform writes by itself.
"""

from __future__ import annotations

from typing import Any

from .ecosystem_chat_destination_binding import DESTINATION_READY
from .ecosystem_chat_write_adapter import EcosystemChatWriteAdapter, WriteResult


class DestinationBoundWriteAdapter:
    adapter_name = "DESTINATION_BOUND_WRITE_ADAPTER"

    def __init__(self, destination_binding: dict[str, Any], delegate: EcosystemChatWriteAdapter):
        self.destination_binding = destination_binding
        self.delegate = delegate

    def write(self, persistence_plan: dict[str, Any]) -> WriteResult:
        if self.destination_binding.get("binding_status") != DESTINATION_READY:
            return WriteResult(
                write_complete=False,
                write_id=None,
                adapter_name=self.adapter_name,
                receipt_id=persistence_plan.get("receipt_id"),
                errors=["destination binding is not ready"],
            )

        result = self.delegate.write(persistence_plan)
        if not result.write_complete:
            return result

        destination_name = self.destination_binding.get("destination_name")
        if not isinstance(destination_name, str) or not destination_name:
            return WriteResult(
                write_complete=False,
                write_id=None,
                adapter_name=self.adapter_name,
                receipt_id=persistence_plan.get("receipt_id"),
                errors=["destination_name is missing after binding check"],
            )

        return WriteResult(
            write_complete=True,
            write_id=f"{destination_name}:{result.write_id}",
            adapter_name=self.adapter_name,
            receipt_id=result.receipt_id,
            errors=[],
        )
