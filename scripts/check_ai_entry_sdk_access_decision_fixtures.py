#!/usr/bin/env python3
"""Verify SDK access decision fixtures remain DENY and non-granting."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "fixtures" / "ai-entry-sdk-access-decision-request.example.json"
RESPONSE = ROOT / "fixtures" / "ai-entry-sdk-access-decision-response.example.json"
REQUEST_FALSE = (
    "grant_sdk_access",
    "enable_credentials",
    "allow_live_sdk_calls",
    "allow_execution",
)
OUTPUT_FALSE = (
    "sdk_access_granted",
    "credential_surface_enabled",
    "live_sdk_calls_allowed",
    "authority_issued",
    "execution_allowed",
    "real_receipt_issued",
)


def fail(message: str) -> None:
    raise SystemExit(f"SDK_ACCESS_DECISION_FIXTURES_FAIL: {message}")


def main() -> int:
    request = json.loads(REQUEST.read_text(encoding="utf-8"))
    response = json.loads(RESPONSE.read_text(encoding="utf-8"))
    if request.get("schema_version") != "stegverse.sdk.ai_entry.access_decision_request.v0.1":
        fail("bad request schema version")
    if response.get("schema_version") != "stegverse.sdk.ai_entry.access_decision_response.v0.1":
        fail("bad response schema version")
    if request.get("request_id") != response.get("request_id"):
        fail("request/response id mismatch")
    if request.get("activation_request_id") != response.get("activation_request_id"):
        fail("activation request id mismatch")
    if request.get("authority_decision") != "DENY":
        fail("request authority decision must be DENY")
    actor = request.get("actor_identity_context", {})
    if actor.get("actor_known") is not False or actor.get("actor_authorized") is not False:
        fail("actor must remain unknown/unauthorized")
    access = request.get("requested_access", {})
    for key in REQUEST_FALSE:
        if access.get(key) is not False:
            fail(f"request {key} must be false")
    if response.get("sdk_access_decision") != "DENY":
        fail("response decision must be DENY")
    outputs = response.get("decision_outputs", {})
    for key in OUTPUT_FALSE:
        if outputs.get(key) is not False:
            fail(f"response {key} must be false")
    if not response.get("missing_preconditions"):
        fail("missing preconditions required")
    print("SDK_ACCESS_DECISION_FIXTURES_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
