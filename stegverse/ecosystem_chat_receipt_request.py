"""Receipt request model for Ecosystem Chat SDK intake.

This module builds a deterministic request object for a future governed
receipt engine. It does not issue receipts.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .ecosystem_chat_backend import handle_ecosystem_chat_submission
from .ecosystem_chat_receipt_authority import get_receipt_authority_status


@dataclass(frozen=True)
class ReceiptRequest:
    request_hash: str
    routed_module: str
    accepted: bool
    receipt_authority_installed: bool
    receipt_issuance_enabled: bool
    receipt_id: None
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_hash": self.request_hash,
            "routed_module": self.routed_module,
            "accepted": self.accepted,
            "receipt_authority_installed": self.receipt_authority_installed,
            "receipt_issuance_enabled": self.receipt_issuance_enabled,
            "receipt_id": self.receipt_id,
            "errors": self.errors,
        }


def build_ecosystem_chat_receipt_request(payload: dict[str, Any]) -> ReceiptRequest:
    """Build the pre-issuance receipt request for an SDK intake payload."""
    response = handle_ecosystem_chat_submission(payload)
    authority = get_receipt_authority_status()

    return ReceiptRequest(
        request_hash=_stable_hash(payload),
        routed_module=response["routed_module"],
        accepted=response["accepted"],
        receipt_authority_installed=authority.authority_installed,
        receipt_issuance_enabled=authority.receipt_issuance_enabled,
        receipt_id=None,
        errors=response["errors"],
    )


def _stable_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
