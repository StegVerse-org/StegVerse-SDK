import io
import json

from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_wsgi import application


def call_app(method: str, path: str, body: bytes):
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = headers

    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": io.BytesIO(body),
    }
    response_body = b"".join(application(environ, start_response))
    return captured["status"], dict(captured["headers"]), json.loads(response_body.decode("utf-8"))


def test_wsgi_post_returns_pipeline_result():
    status, headers, result = call_app(
        "POST",
        "/api/ecosystem-chat",
        json.dumps(payload()).encode("utf-8"),
    )

    assert status == "202 Accepted"
    assert headers["Content-Type"] == "application/json"
    assert set(result) == {
        "intake",
        "receipt_decision",
        "issuer_result",
        "record_export",
        "persistence_plan",
        "destination_binding",
        "write_result",
    }
    assert result["intake"]["accepted"] is True
    assert result["issuer_result"]["issued"] is False
    assert result["destination_binding"]["binding_status"] == "DESTINATION_DISABLED"
    assert result["write_result"]["write_complete"] is False


def test_wsgi_get_is_rejected():
    status, _headers, result = call_app("GET", "/api/ecosystem-chat", b"{}")

    assert status == "405 Method Not Allowed"
    assert result["intake"]["accepted"] is False
    assert result["issuer_result"]["issued"] is False
    assert result["destination_binding"]["binding_status"] == "DESTINATION_DISABLED"
    assert result["write_result"]["write_complete"] is False
