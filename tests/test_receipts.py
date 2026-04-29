#!/usr/bin/env python3
"""Quick test for receipt verification."""

from stegverse import verify_receipt


def test_valid_receipt():
    receipt = {
        "receipt_id": "r-001",
        "decision": "allow",
        "timestamp": "2026-04-28T18:18:00Z",
    }
    assert verify_receipt(receipt) is True
    print("PASS: Valid receipt")


def test_invalid_receipt_missing_field():
    receipt = {
        "receipt_id": "r-002",
        "decision": "deny",
        # missing timestamp
    }
    assert verify_receipt(receipt) is False
    print("PASS: Invalid receipt (missing timestamp)")


def test_empty_receipt():
    assert verify_receipt({}) is False
    print("PASS: Empty receipt")


if __name__ == "__main__":
    test_valid_receipt()
    test_invalid_receipt_missing_field()
    test_empty_receipt()
    print("\nALL RECEIPT TESTS PASSED")
