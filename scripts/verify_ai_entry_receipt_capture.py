#!/usr/bin/env python3
"""Verify SDK AI Entry receipt capture boundary remains preview-only."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stegverse.ai_entry_receipt_capture import preview_ai_entry_receipt_capture


def fail(message: str) -> None:
    raise SystemExit(f"AI_ENTRY_RECEIPT_CAPTURE_FAIL: {message}")


def main() -> int:
    preview = preview_ai_entry_receipt_capture(
        user_input="Compare StegVerse with ChatGPT",
        route_id="llm_comparison",
        response_id="preview-llm-comparison",
    )
    if preview.schema_version != "stegverse.sdk.ai_entry_receipt_capture.v0.1":
        fail("bad schema_version")
    if preview.preview_only is not True:
        fail("preview_only must be true")
    for key in (
        "receipt_capture_enabled",
        "real_receipt_issued",
        "master_record_persisted",
        "execution_authority_granted",
        "credential_surface_enabled",
    ):
        if getattr(preview, key) is not False:
            fail(f"{key} must be false")
    if len(preview.input_hash) != 64:
        fail("input_hash must be sha256 hex")
    if preview.route_id != "llm_comparison":
        fail("route_id not preserved")
    if preview.response_id != "preview-llm-comparison":
        fail("response_id not preserved")
    if preview.reconstruction_metadata_required is not True:
        fail("reconstruction metadata must be required before activation")
    print("AI_ENTRY_RECEIPT_CAPTURE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
