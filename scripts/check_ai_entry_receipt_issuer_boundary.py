#!/usr/bin/env python3
"""Verify AI Entry receipt issuer boundary remains preview-only and non-issuing."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOUNDARY = ROOT / "data" / "ai-entry-receipt-issuer-boundary.json"
FALSE_KEYS = (
    "real_receipt_issued",
    "receipt_persisted",
    "authority_issued",
    "execution_allowed",
    "credential_access_allowed",
    "live_calls_allowed",
)


def fail(message: str) -> None:
    raise SystemExit(f"SDK_RECEIPT_ISSUER_BOUNDARY_FAIL: {message}")


def main() -> int:
    data = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    if data.get("schema_version") != "stegverse.sdk.ai_entry.receipt_issuer_boundary.v0.1":
        fail("bad schema version")
    if data.get("state") != "boundary_defined_preview_only":
        fail("state must remain boundary_defined_preview_only")
    issuer = data.get("receipt_issuer", {})
    if issuer.get("mode") != "preview_only":
        fail("issuer mode must be preview_only")
    if issuer.get("default_status") != "NOT_ISSUED":
        fail("default status must be NOT_ISSUED")
    contract = data.get("non_issuing_contract", {})
    for key in FALSE_KEYS:
        if contract.get(key) is not False:
            fail(f"{key} must be false")
    print("SDK_RECEIPT_ISSUER_BOUNDARY_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
