"""Receipt engine evaluator for Ecosystem Chat SDK intake.

This module evaluates a pre-issuance receipt request and returns a bounded
receipt decision. It does not create proof receipts while authority is pending.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ecosystem_chat_receipt_request import ReceiptRequest, build_ecosystem_chat_receipt_request

ISSUANCE_PENDING = "ISSUANCE_PENDING"
ISSUANCE_BLOCKED = "ISSUANCE_BLOCKED"


@dataclass(frozen=True)
class ReceiptEngineDecision:
    decision: str
    request_hash: str
    routed_module: str
    receipt_id: None
    reason: str
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "request_hash": self.request_hash,
            "routed_module": self.routed_module,
            "receipt_id": self.receipt_id,
            "reason": self.reason,
            "errors": self.errors,
        }


def evaluate_ecosystem_chat_receipt_request(request: ReceiptRequest) -> ReceiptEngineDecision:
    """Evaluate a receipt request without issuing a proof receipt."""
    if request.errors or not request.accepted:
        return ReceiptEngineDecision(
            decision=ISSUANCE_BLOCKED,
            request_hash=request.request_hash,
            routed_module=request.routed_module,
            receipt_id=None,
            reason="SDK intake request was not accepted.",
            errors=request.errors,
        )

    if not request.receipt_authority_installed or not request.receipt_issuance_enabled:
        return ReceiptEngineDecision(
            decision=ISSUANCE_PENDING,
            request_hash=request.request_hash,
            routed_module=request.routed_module,
            receipt_id=None,
            reason="Receipt authority is not installed or issuance is disabled.",
            errors=[],
        )

    return ReceiptEngineDecision(
        decision=ISSUANCE_BLOCKED,
        request_hash=request.request_hash,
        routed_module=request.routed_module,
        receipt_id=None,
        reason="No governed receipt issuer is wired to this evaluator.",
        errors=["receipt issuer missing"],
    )


def evaluate_ecosystem_chat_payload_for_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    """Build and evaluate the receipt request for a Site payload."""
    request = build_ecosystem_chat_receipt_request(payload)
    return evaluate_ecosystem_chat_receipt_request(request).to_dict()
