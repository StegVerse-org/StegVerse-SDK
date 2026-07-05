#!/usr/bin/env python3
"""Verify SDK receipt preview fixtures remain preview-only and non-issuing."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "fixtures" / "ai-entry-receipt-preview-request.example.json"
RESPONSE = ROOT / "fixtures" / "ai-entry-receipt-preview-response.example.json"
REQUEST_FALSE = ("issue_real_receipt", "persist_receipt", "enable_reconstruction")
RESPONSE_FALSE = ("issued", "persisted", "reconstruction_available")


def fail(message: str) -> None:
    raise SystemExit(f"SDK_RECEIPT_PREVIEW_FIXTURES_FAIL: {message}")


def main() -> int:
    request = json.loads(REQUEST.read_text(encoding="utf-8"))
    response = json.loads(RESPONSE.read_text(encoding="utf-8"))
    if request.get("schema_version") != "stegverse.sdk.ai_entry.receipt_preview_request.v0.1":
        fail("bad request schema version")
    if response.get("schema_version") != "stegverse.sdk.ai_entry.receipt_preview_response.v0.1":
        fail("bad response schema version")
    if request.get("request_id") != response.get("request_id"):
        fail("request/response id mismatch")
    if request.get("activation_request_id") != response.get("activation_request_id"):
        fail("activation request id mismatch")
    if request.get("authority_decision") != "DENY":
        fail("request authority decision must be DENY")
    requested = request.get("requested_receipt", {})
    for key in REQUEST_FALSE:
        if requested.get(key) is not False:
            fail(f"request {key} must be false")
    if response.get("status") != "NOT_ISSUED":
        fail("response status must be NOT_ISSUED")
    preview = response.get("receipt_preview", {})
    for key in RESPONSE_FALSE:
        if preview.get(key) is not False:
            fail(f"response {key} must be false")
    if preview.get("authority_decision") != "DENY":
        fail("response authority decision must be DENY")
    if not response.get("missing_preconditions"):
        fail("missing preconditions required")
    print("SDK_RECEIPT_PREVIEW_FIXTURES_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
