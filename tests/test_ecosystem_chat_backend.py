from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_backend import handle_ecosystem_chat_submission


def test_backend_handler_returns_bounded_response_shape():
    result = handle_ecosystem_chat_submission(payload())
    assert set(result) == {"accepted", "routed_module", "receipt_id", "next_action", "errors"}
    assert result["accepted"] is True
    assert result["receipt_id"] is None


def test_backend_handler_rejects_payload_drift():
    data = payload()
    data["manifest"]["user_request"] = "changed after form generation"
    result = handle_ecosystem_chat_submission(data)
    assert result["accepted"] is False
    assert result["receipt_id"] is None
    assert result["errors"]
