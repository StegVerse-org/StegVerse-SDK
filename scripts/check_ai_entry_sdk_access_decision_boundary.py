#!/usr/bin/env python3
"""Verify SDK access decision boundary remains preview-only and non-granting."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOUNDARY = ROOT / "data" / "ai-entry-sdk-access-decision-boundary.json"
FALSE_KEYS = (
    "sdk_access_granted",
    "credential_surface_enabled",
    "live_sdk_calls_allowed",
    "authority_issued",
    "execution_allowed",
    "real_receipt_issued",
)


def fail(message: str) -> None:
    raise SystemExit(f"SDK_ACCESS_DECISION_BOUNDARY_FAIL: {message}")


def main() -> int:
    data = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    if data.get("schema_version") != "stegverse.sdk.ai_entry.access_decision_boundary.v0.1":
        fail("bad schema version")
    if data.get("state") != "boundary_defined_preview_only":
        fail("state must remain boundary_defined_preview_only")
    decision = data.get("access_decision", {})
    if decision.get("mode") != "preview_only":
        fail("mode must be preview_only")
    if decision.get("default_decision") != "DENY":
        fail("default decision must be DENY")
    contract = data.get("non_granting_contract", {})
    for key in FALSE_KEYS:
        if contract.get(key) is not False:
            fail(f"{key} must be false")
    print("SDK_ACCESS_DECISION_BOUNDARY_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
