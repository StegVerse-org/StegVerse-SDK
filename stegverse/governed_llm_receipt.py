"""Receipt handoff binding for governed LLM manifests.

This module creates a receipt-ready handoff from a governed LLM manifest. It is
not execution, authority, or installation; it only links hashes, optional
system-boundary references, and route status for downstream record retention.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from .governed_llm_manifest import build_governed_llm_manifest


GOVERNED_LLM_RECEIPT_SCHEMA_VERSION = "stegverse.sdk.governed_llm_receipt.v0.1"


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class GovernedLLMReceiptHandoff:
    """Receipt-ready handoff for governed LLM session manifests."""

    receipt_status: str
    manifest_hash: str
    session_hash: str
    intake_decision: str
    route: str
    retain_record: bool
    system_boundary_declaration_ref: Optional[dict[str, Any]] = None
    created_at: str = ""
    schema_version: str = GOVERNED_LLM_RECEIPT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if data["system_boundary_declaration_ref"] is None:
            data.pop("system_boundary_declaration_ref")
        data["created_at"] = self.created_at or utc_now_iso()
        data["receipt_handoff_hash"] = stable_hash(data)
        return data


def build_governed_llm_receipt_handoff(session_packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build receipt handoff from a governed LLM session packet."""

    manifest = build_governed_llm_manifest(session_packet)
    receipt_status = "record_retained"
    if manifest["intake_decision"] == "ROUTE":
        receipt_status = "route_ready_record_retained"
    elif manifest["intake_decision"] == "QUARANTINE":
        receipt_status = "quarantine_record_retained"
    elif manifest["intake_decision"] == "REJECT":
        receipt_status = "rejection_record_retained"
    elif manifest["intake_decision"] == "FAIL_CLOSED":
        receipt_status = "fail_closed_record_retained"

    handoff = GovernedLLMReceiptHandoff(
        receipt_status=receipt_status,
        manifest_hash=str(manifest["manifest_hash"]),
        session_hash=str(manifest["session_hash"]),
        intake_decision=str(manifest["intake_decision"]),
        route=str(manifest["route"]),
        retain_record=bool(manifest["retain_record"]),
        system_boundary_declaration_ref=manifest.get("system_boundary_declaration_ref"),
    )
    result = handoff.to_dict()
    result["manifest"] = manifest
    return result


__all__ = [
    "GOVERNED_LLM_RECEIPT_SCHEMA_VERSION",
    "GovernedLLMReceiptHandoff",
    "build_governed_llm_receipt_handoff",
]
