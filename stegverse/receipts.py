from typing import Any, Dict


def verify_receipt(receipt: Dict[str, Any]) -> bool:
    required = {"receipt_id", "decision", "timestamp"}
    return required.issubset(set(receipt.keys()))
