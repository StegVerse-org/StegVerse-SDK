from typing import Any, Dict

from .admissibility_receipts import verify_admissibility_receipt_reference


def verify_receipt(receipt: Dict[str, Any]) -> bool:
    required = {"receipt_id", "decision", "timestamp"}
    if not required.issubset(set(receipt.keys())):
        return False

    admissibility_reference = receipt.get("admissibility_receipt_reference")
    if admissibility_reference is None:
        return True
    if not isinstance(admissibility_reference, dict):
        return False
    return verify_admissibility_receipt_reference(admissibility_reference)
