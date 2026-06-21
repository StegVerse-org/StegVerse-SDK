"""HTTP adapter for Ecosystem Chat SDK intake.

The adapter is framework-neutral. Web runtimes can pass method, path, and a
JSON request body to get a status code and response dictionary.
"""

from __future__ import annotations

import json
from typing import Any

from .ecosystem_chat_backend import handle_ecosystem_chat_submission

ECOSYSTEM_CHAT_PATH = "/api/ecosystem-chat"


def handle_ecosystem_chat_http(method: str, path: str, body: str | bytes) -> tuple[int, dict[str, Any]]:
    """Return an HTTP-style status code and bounded SDK response body."""
    if method.upper() != "POST":
        return 405, _error_response("method must be POST")

    if path != ECOSYSTEM_CHAT_PATH:
        return 404, _error_response("path not found")

    try:
        raw_body = body.decode("utf-8") if isinstance(body, bytes) else body
        payload = json.loads(raw_body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return 400, _error_response("body must be valid JSON")

    response = handle_ecosystem_chat_submission(payload)
    status = 202 if response.get("accepted") else 422
    return status, response


def _error_response(message: str) -> dict[str, Any]:
    return {
        "accepted": False,
        "routed_module": "StegVerse-org/SDK",
        "receipt_id": None,
        "next_action": "Correct the request and resubmit.",
        "errors": [message],
    }
