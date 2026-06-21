"""Destination binding contract for Ecosystem Chat production writes.

The default binding is disabled. Production destinations must be configured
explicitly before a write adapter can be considered production-bound.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

DESTINATION_DISABLED = "DESTINATION_DISABLED"
DESTINATION_READY = "DESTINATION_READY"


@dataclass(frozen=True)
class DestinationBinding:
    binding_status: str
    binding_hash: str | None
    destination_name: str | None
    destination_type: str | None
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "binding_status": self.binding_status,
            "binding_hash": self.binding_hash,
            "destination_name": self.destination_name,
            "destination_type": self.destination_type,
            "errors": self.errors,
        }


def build_destination_binding(config: dict[str, Any] | None = None) -> DestinationBinding:
    if config is None:
        return DestinationBinding(
            binding_status=DESTINATION_DISABLED,
            binding_hash=None,
            destination_name=None,
            destination_type=None,
            errors=["destination binding is not configured"],
        )

    destination_name = config.get("destination_name")
    destination_type = config.get("destination_type")
    errors: list[str] = []

    if not isinstance(destination_name, str) or not destination_name.strip():
        errors.append("destination_name is required")
    if destination_type not in {"master-records", "local-test"}:
        errors.append("destination_type is not allowed")

    if errors:
        return DestinationBinding(
            binding_status=DESTINATION_DISABLED,
            binding_hash=None,
            destination_name=destination_name if isinstance(destination_name, str) else None,
            destination_type=destination_type if isinstance(destination_type, str) else None,
            errors=errors,
        )

    base = {
        "destination_name": destination_name,
        "destination_type": destination_type,
    }
    return DestinationBinding(
        binding_status=DESTINATION_READY,
        binding_hash=_stable_hash(base),
        destination_name=destination_name,
        destination_type=destination_type,
        errors=[],
    )


def _stable_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
