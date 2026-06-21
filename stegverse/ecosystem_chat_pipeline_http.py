"""HTTP adapter for the Ecosystem Chat SDK pipeline."""

from __future__ import annotations

import json
from typing import Any

from .ecosystem_chat_http import ECOSYSTEM_CHAT_PATH
from .ecosystem_chat_pipeline import run_ecosystem_chat_pipeline


def handle_ecosystem_chat_pipeline_http(method: str, path: str, body: str | bytes) -> tuple[int, dict[str, Any]]:
    """Return an HTTP-style status and the full current pipeline result."""
    if method.upper() != "POST":
        return 405, _error_result("method must be POST")

    if path != ECOSYSTEM_CHAT_PATH:
        return 404, _error_result("path not found")

    try:
        raw_body = body.decode("utf-8") if isinstance(body, bytes) else body
        request_body = json.loads(raw_body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return 400, _error_result("body must be valid JSON")

    try:
        payload, destination_config = _extract_request_parts(request_body)
    except ValueError as error:
        return 400, _error_result(str(error))

    result = run_ecosystem_chat_pipeline(payload, destination_config=destination_config)
    accepted = result["intake"].get("accepted") is True
    status = 202 if accepted else 422
    return status, result


def _extract_request_parts(request_body: Any) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if not isinstance(request_body, dict):
        raise ValueError("body must be a JSON object")

    if "payload" not in request_body:
        return request_body, None

    allowed_keys = {"payload", "destination_config"}
    if set(request_body) - allowed_keys:
        raise ValueError("request envelope contains unsupported keys")

    payload = request_body.get("payload")
    destination_config = request_body.get("destination_config")
    if not isinstance(payload, dict):
        raise ValueError("request envelope payload must be an object")
    if destination_config is not None and not isinstance(destination_config, dict):
        raise ValueError("request envelope destination_config must be an object")
    return payload, destination_config


def _error_result(message: str) -> dict[str, Any]:
    return {
        "intake": {
            "accepted": False,
            "routed_module": "StegVerse-org/SDK",
            "receipt_id": None,
            "next_action": "Correct the request and resubmit.",
            "errors": [message],
        },
        "receipt_decision": {
            "decision": "ISSUANCE_BLOCKED",
            "request_hash": None,
            "routed_module": "StegVerse-org/SDK",
            "receipt_id": None,
            "reason": message,
            "errors": [message],
        },
        "issuer_result": {
            "issued": False,
            "receipt_id": None,
            "issuer_name": "DISABLED_ECOSYSTEM_CHAT_ISSUER",
            "errors": [message],
        },
        "record_export": {
            "export_status": "EXPORT_BLOCKED",
            "export_hash": None,
            "request_hash": None,
            "receipt_id": None,
            "external_write_complete": False,
            "errors": [message],
        },
        "persistence_plan": {
            "persistence_status": "PERSISTENCE_BLOCKED",
            "persistence_hash": None,
            "receipt_id": None,
            "export_hash": None,
            "external_write_complete": False,
            "errors": [message],
        },
        "destination_binding": {
            "binding_status": "DESTINATION_DISABLED",
            "binding_hash": None,
            "destination_name": None,
            "destination_type": None,
            "errors": [message],
        },
        "write_result": {
            "write_complete": False,
            "write_id": None,
            "adapter_name": "DISABLED_ECOSYSTEM_CHAT_WRITE_ADAPTER",
            "receipt_id": None,
            "errors": [message],
        },
    }
