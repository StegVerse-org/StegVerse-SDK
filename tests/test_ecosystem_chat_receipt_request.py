from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_receipt_request import build_ecosystem_chat_receipt_request


def test_receipt_request_is_deterministic_for_same_payload():
    first = build_ecosystem_chat_receipt_request(payload()).to_dict()
    second = build_ecosystem_chat_receipt_request(payload()).to_dict()

    assert first["request_hash"] == second["request_hash"]
    assert first["request_hash"].startswith("sha256:")


def test_receipt_request_preserves_pending_receipt_state():
    request = build_ecosystem_chat_receipt_request(payload()).to_dict()

    assert request["accepted"] is True
    assert request["routed_module"] == "Site"
    assert request["receipt_id"] is None
    assert request["receipt_authority_installed"] is False
    assert request["receipt_issuance_enabled"] is False
    assert request["errors"] == []
