"""Persistence planning for Ecosystem Chat records.

This module creates a deterministic plan for a future external write.
It does not perform persistence.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

PERSISTENCE_PENDING = "PERSISTENCE_PENDING"
PERSISTENCE_BLOCKED = "PERSISTENCE_BLOCKED"


@dataclass(frozen=True)
class PersistencePlan:
    persistence_status: str
    persistence_hash: str
    receipt_id: str | None
    export_hash: str | None
    external_write_complete: bool
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "persistence_status": self.persistence_status,
            "persistence_hash": self.persistence_hash,
            "receipt_id": self.receipt_id,
            "export_hash": self.export_hash,
            "external_write_complete": self.external_write_complete,
            "errors": self.errors,
        }


def build_persistence_plan(record_export: dict[str, Any]) -> PersistencePlan:
    errors = list(record_export.get("errors", []))
    receipt_id = record_export.get("receipt_id")
    export_hash = record_export.get("export_hash")

    if not isinstance(receipt_id, str) or not receipt_id:
        errors.append("receipt_id is required before persistence")
    if not isinstance(export_hash, str) or not export_hash.startswith("sha256:"):
        errors.append("export_hash is required before persistence")

    status = PERSISTENCE_PENDING if not errors else PERSISTENCE_BLOCKED
    base = {
        "persistence_status": status,
        "receipt_id": receipt_id if isinstance(receipt_id, str) else None,
        "export_hash": export_hash if isinstance(export_hash, str) else None,
    }

    return PersistencePlan(
        persistence_status=status,
        persistence_hash=_stable_hash(base),
        receipt_id=base["receipt_id"],
        export_hash=base["export_hash"],
        external_write_complete=False,
        errors=errors,
    )


def _stable_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
