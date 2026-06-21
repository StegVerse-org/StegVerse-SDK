import json

from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_http import handle_ecosystem_chat_http


def test_http_post_accepts_valid_payload():
    status, response = handle_ecosystem_chat_http("POST", "/api/ecosystem-chat", json.dumps(payload()))
    assert status == 202
    assert response["accepted"] is True
    assert response["receipt_id"] is None


def test_http_post_rejects_invalid_json():
    status, response = handle_ecosystem_chat_http("POST", "/api/ecosystem-chat", "not-json")
    assert status == 400
    assert response["accepted"] is False
    assert response["receipt_id"] is None
