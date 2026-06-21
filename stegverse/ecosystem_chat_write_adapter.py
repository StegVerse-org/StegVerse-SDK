"""Write adapter interface for Ecosystem Chat persistence plans.

The default adapter fails closed and performs no external write.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class WriteResult:
    write_complete: bool
    write_id: str | None
    adapter_name: str
    receipt_id: str | None
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "write_complete": self.write_complete,
            "write_id": self.write_id,
            "adapter_name": self.adapter_name,
            "receipt_id": self.receipt_id,
            "errors": self.errors,
        }


class EcosystemChatWriteAdapter(Protocol):
    def write(self, persistence_plan: dict[str, Any]) -> WriteResult:
        """Evaluate a persistence plan and return a write result."""


class DisabledEcosystemChatWriteAdapter:
    adapter_name = "DISABLED_ECOSYSTEM_CHAT_WRITE_ADAPTER"

    def write(self, persistence_plan: dict[str, Any]) -> WriteResult:
        return WriteResult(
            write_complete=False,
            write_id=None,
            adapter_name=self.adapter_name,
            receipt_id=persistence_plan.get("receipt_id"),
            errors=["write adapter is not installed"],
        )


def write_with_adapter(
    persistence_plan: dict[str, Any],
    adapter: EcosystemChatWriteAdapter | None = None,
) -> dict[str, Any]:
    active_adapter = adapter or DisabledEcosystemChatWriteAdapter()
    return active_adapter.write(persistence_plan).to_dict()
