import json

from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_pipeline_http import handle_ecosystem_chat_pipeline_http


def test_pipeline_http_post_returns_full_pipeline():
    status, result = handle_ecosystem_chat_pipeline_http("POST", "/api/ecosystem-chat", json.dumps(payload()))

    assert status == 202
    assert set(result) == {
        "intake",
        "receipt_decision",
        "issuer_result",
        "record_export",
        "persistence_plan",
        "write_result",
    }
    assert result["intake"]["accepted"] is True
    assert result["receipt_decision"]["receipt_id"] is None
    assert result["issuer_result"]["issued"] is False
    assert result["issuer_result"]["receipt_id"] is None
    assert result["record_export"]["external_write_complete"] is False
    assert result["persistence_plan"]["external_write_complete"] is False
    assert result["write_result"]["write_complete"] is False


def test_pipeline_http_rejects_wrong_method():
    status, result = handle_ecosystem_chat_pipeline_http("GET", "/api/ecosystem-chat", "{}")

    assert status == 405
    assert result["intake"]["accepted"] is False
    assert result["receipt_decision"]["decision"] == "ISSUANCE_BLOCKED"
    assert result["issuer_result"]["issued"] is False
    assert result["record_export"]["export_status"] == "EXPORT_BLOCKED"
    assert result["persistence_plan"]["persistence_status"] == "PERSISTENCE_BLOCKED"
    assert result["write_result"]["write_complete"] is False


def test_pipeline_http_rejects_invalid_json():
    status, result = handle_ecosystem_chat_pipeline_http("POST", "/api/ecosystem-chat", "not-json")

    assert status == 400
    assert result["intake"]["receipt_id"] is None
    assert result["issuer_result"]["receipt_id"] is None
    assert result["record_export"]["external_write_complete"] is False
    assert result["persistence_plan"]["external_write_complete"] is False
    assert result["write_result"]["write_complete"] is False
