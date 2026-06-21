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
    receipt_id: str | None
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


def build_record_export_candidate(
    payload: dict[str, Any],
    issuer_result: dict[str, Any] | None = None,
) -> RecordExportCandidate:
    decision = evaluate_ecosystem_chat_payload_for_receipt(payload)
    issuer_errors = [] if issuer_result is None else list(issuer_result.get("errors", []))
    errors = [*decision["errors"], *issuer_errors]
    status = EXPORT_PENDING if not errors else EXPORT_BLOCKED
    receipt_id = _issued_receipt_id(issuer_result)
    export_base = {
        "decision": decision["decision"],
        "request_hash": decision["request_hash"],
        "receipt_id": receipt_id,
        "export_status": status,
    }
    return RecordExportCandidate(
        export_status=status,
        export_hash=_stable_hash(export_base),
        request_hash=decision["request_hash"],
        receipt_id=receipt_id,
        external_write_complete=False,
        errors=errors,
    )


def _issued_receipt_id(issuer_result: dict[str, Any] | None) -> str | None:
    if not issuer_result or issuer_result.get("issued") is not True:
        return None
    receipt_id = issuer_result.get("receipt_id")
    return receipt_id if isinstance(receipt_id, str) and receipt_id else None


def _stable_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
