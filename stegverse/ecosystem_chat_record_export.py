"""Record export candidate for Ecosystem Chat.

Builds a deterministic export candidate from the receipt evaluation result.
No external write is performed by this module.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .ecosystem_chat_receipt_engine import evaluate_ecosystem_chat_payload_for_receipt

EXPORT_PENDING = "EXPORT_PENDING"
EXPORT_BLOCKED = "EXPORT_BLOCKED"


@dataclass(frozen=True)
class RecordExportCandidate:
    export_status: str
    export_hash: str
    request_hash: str
    receipt_id: None
    external_write_complete: bool
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "export_status": self.export_status,
            "export_hash": self.export_hash,
            "request_hash": self.request_hash,
            "receipt_id": self.receipt_id,
            "external_write_complete": self.external_write_complete,
            "errors": self.errors,
        }


def build_record_export_candidate(payload: dict[str, Any]) -> RecordExportCandidate:
    decision = evaluate_ecosystem_chat_payload_for_receipt(payload)
    status = EXPORT_PENDING if not decision["errors"] else EXPORT_BLOCKED
    export_base = {
        "decision": decision["decision"],
        "request_hash": decision["request_hash"],
        "receipt_id": decision["receipt_id"],
        "export_status": status,
    }
    return RecordExportCandidate(
        export_status=status,
        export_hash=_stable_hash(export_base),
        request_hash=decision["request_hash"],
        receipt_id=None,
        external_write_complete=False,
        errors=decision["errors"],
    )


def _stable_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
