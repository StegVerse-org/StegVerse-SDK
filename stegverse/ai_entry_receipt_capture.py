"""Disabled-by-default receipt capture boundary for StegVerse AI Entry.

This module provides an SDK-side preview of what receipt capture would need to
record without issuing receipts, persisting master records, exposing
credentials, or granting execution authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any


@dataclass(frozen=True)
class AIEntryReceiptCapturePreview:
    schema_version: str
    preview_only: bool
    receipt_capture_enabled: bool
    real_receipt_issued: bool
    master_record_persisted: bool
    execution_authority_granted: bool
    credential_surface_enabled: bool
    input_hash: str
    route_id: str
    response_id: str
    reconstruction_metadata_required: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def preview_ai_entry_receipt_capture(
    *,
    user_input: str,
    route_id: str,
    response_id: str,
) -> AIEntryReceiptCapturePreview:
    digest = sha256(user_input.encode("utf-8")).hexdigest()
    return AIEntryReceiptCapturePreview(
        schema_version="stegverse.sdk.ai_entry_receipt_capture.v0.1",
        preview_only=True,
        receipt_capture_enabled=False,
        real_receipt_issued=False,
        master_record_persisted=False,
        execution_authority_granted=False,
        credential_surface_enabled=False,
        input_hash=digest,
        route_id=route_id,
        response_id=response_id,
        reconstruction_metadata_required=True,
    )


def main() -> int:
    import json

    preview = preview_ai_entry_receipt_capture(
        user_input="How do I access the SDK?",
        route_id="sdk_access_guidance",
        response_id="preview-sdk-access-guidance",
    )
    print(json.dumps(preview.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
