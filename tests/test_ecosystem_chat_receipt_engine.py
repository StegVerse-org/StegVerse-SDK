from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_receipt_engine import (
    ISSUANCE_BLOCKED,
    ISSUANCE_PENDING,
    evaluate_ecosystem_chat_payload_for_receipt,
)


def test_receipt_engine_returns_pending_when_authority_is_disabled():
    decision = evaluate_ecosystem_chat_payload_for_receipt(payload())

    assert decision["decision"] == ISSUANCE_PENDING
    assert decision["receipt_id"] is None
    assert decision["request_hash"].startswith("sha256:")
    assert decision["errors"] == []


def test_receipt_engine_blocks_invalid_intake():
    data = payload()
    data["receipt_window"]["correctness_errors"] = ["missing declared goal"]
    decision = evaluate_ecosystem_chat_payload_for_receipt(data)

    assert decision["decision"] == ISSUANCE_BLOCKED
    assert decision["receipt_id"] is None
    assert decision["errors"]
