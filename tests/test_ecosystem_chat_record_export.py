from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_record_export import (
    EXPORT_BLOCKED,
    EXPORT_PENDING,
    build_record_export_candidate,
)


def test_record_export_candidate_is_pending_without_external_write():
    candidate = build_record_export_candidate(payload()).to_dict()

    assert candidate["export_status"] == EXPORT_PENDING
    assert candidate["export_hash"].startswith("sha256:")
    assert candidate["request_hash"].startswith("sha256:")
    assert candidate["receipt_id"] is None
    assert candidate["external_write_complete"] is False
    assert candidate["errors"] == []


def test_record_export_candidate_accepts_issued_receipt_id():
    issuer_result = {
        "issued": True,
        "receipt_id": "ecr-local-abc123",
        "issuer_name": "TEST",
        "errors": [],
    }
    candidate = build_record_export_candidate(payload(), issuer_result).to_dict()

    assert candidate["export_status"] == EXPORT_PENDING
    assert candidate["receipt_id"] == "ecr-local-abc123"
    assert candidate["external_write_complete"] is False


def test_record_export_candidate_is_deterministic():
    first = build_record_export_candidate(payload()).to_dict()
    second = build_record_export_candidate(payload()).to_dict()

    assert first["export_hash"] == second["export_hash"]


def test_record_export_candidate_blocks_invalid_payload():
    data = payload()
    data["manifest"]["input_mode"] = "changed"
    candidate = build_record_export_candidate(data).to_dict()

    assert candidate["export_status"] == EXPORT_BLOCKED
    assert candidate["receipt_id"] is None
    assert candidate["external_write_complete"] is False
    assert candidate["errors"]
