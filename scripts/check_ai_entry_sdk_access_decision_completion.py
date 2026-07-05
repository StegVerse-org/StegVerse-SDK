#!/usr/bin/env python3
"""Verify SDK access decision boundary completion remains non-granting."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "ai-entry-sdk-access-decision-completion.json"
COMPLETED = (
    "sdk_access_decision_boundary",
    "sdk_access_decision_boundary_verifier",
    "sdk_access_decision_request_fixture",
    "sdk_access_decision_response_fixture",
    "sdk_access_decision_fixture_verifier",
    "sdk_validation_wired",
)
FALSE_KEYS = (
    "sdk_access_granted",
    "credential_surface_enabled",
    "live_sdk_calls_allowed",
    "authority_issued",
    "execution_allowed",
    "real_receipt_issued",
)


def fail(message: str) -> None:
    raise SystemExit(f"SDK_ACCESS_DECISION_COMPLETION_FAIL: {message}")


def main() -> int:
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    if data.get("schema_version") != "stegverse.sdk.ai_entry.access_decision_completion.v0.1":
        fail("bad schema version")
    if data.get("state") != "preview_complete_non_granting":
        fail("state must be preview_complete_non_granting")
    completed = data.get("completed_components", {})
    for key in COMPLETED:
        if completed.get(key) is not True:
            fail(f"{key} must be true")
    boundary = data.get("current_boundary", {})
    for key in FALSE_KEYS:
        if boundary.get(key) is not False:
            fail(f"{key} must be false")
    if data.get("next_goal_candidate") != "Operator recoverability boundary":
        fail("next goal candidate mismatch")
    print("SDK_ACCESS_DECISION_COMPLETION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
