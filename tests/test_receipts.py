from stegverse.receipts import verify_receipt


def test_verify_receipt():
    receipt = {
        "receipt_id": "r-001",
        "decision": "allow",
        "timestamp": "2026-03-08T00:00:00Z",
    }
    assert verify_receipt(receipt) is True
