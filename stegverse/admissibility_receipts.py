"""Receipt-reference helpers for dynamic admissibility results.

These helpers create stable local references for admissibility result packets.
They do not claim execution proof. They only identify the evaluated packet and
its posture so it can later be attached to an execution receipt or review record.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, Mapping, Optional

ADMISSIBILITY_RECEIPT_REFERENCE_SCHEMA = "stegverse.admissibility.receipt_reference.v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stable_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def build_admissibility_receipt_reference(
    result_packet: Mapping[str, Any],
    *,
    reference_id: Optional[str] = None,
    source: str = "sdk_dynamic_admissibility",
) -> Dict[str, Any]:
    """Build a stable local reference for a dynamic admissibility result packet."""
    result_hash = _stable_hash(result_packet)
    classification = result_packet.get("classification", {})
    if not isinstance(classification, Mapping):
        classification = {}

    reference = {
        "schema": ADMISSIBILITY_RECEIPT_REFERENCE_SCHEMA,
        "created_at": _utc_now(),
        "reference_id": reference_id or result_hash.replace("sha256:", "admref-")[:72],
        "source": source,
        "result_schema": result_packet.get("schema"),
        "result_hash": result_hash,
        "decision": classification.get("decision", result_packet.get("decision")),
        "allowed_next_state": classification.get("allowed_next_state", result_packet.get("allowed_next_state")),
        "receipt_posture": result_packet.get("receipt_posture", "sdk_local_not_receipt_backed"),
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_execution_proof": True,
        },
    }
    reference["reference_hash"] = _stable_hash(reference)
    return reference


def verify_admissibility_receipt_reference(reference: Mapping[str, Any]) -> bool:
    """Return True when the reference has the required local-reference fields."""
    required = {
        "schema",
        "created_at",
        "reference_id",
        "source",
        "result_schema",
        "result_hash",
        "decision",
        "allowed_next_state",
        "receipt_posture",
        "boundary",
        "reference_hash",
    }
    if not required.issubset(reference.keys()):
        return False
    if reference.get("schema") != ADMISSIBILITY_RECEIPT_REFERENCE_SCHEMA:
        return False
    boundary = reference.get("boundary")
    return isinstance(boundary, Mapping) and boundary.get("does_not_create_execution_proof") is True
