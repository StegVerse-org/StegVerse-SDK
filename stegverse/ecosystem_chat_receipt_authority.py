"""Receipt authority boundary for Ecosystem Chat.

This module intentionally does not issue receipts yet.
It defines the contract that the future governed receipt engine must satisfy.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReceiptAuthorityStatus:
    authority_installed: bool
    receipt_issuance_enabled: bool
    authority_name: str


def get_receipt_authority_status() -> ReceiptAuthorityStatus:
    return ReceiptAuthorityStatus(
        authority_installed=False,
        receipt_issuance_enabled=False,
        authority_name="SDK_RECEIPT_AUTHORITY_PENDING",
    )
