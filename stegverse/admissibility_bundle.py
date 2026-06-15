"""Governed Admissibility Bundle helpers.

A bundle packages the original tester packet, the admissibility result, and the
local admissibility receipt reference into one portable object for exchange
between the Site, SDK, adapters, and future runtime services.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, Mapping, Optional

from .admissibility_receipts import verify_admissibility_receipt_reference

ADMISSIBILITY_BUNDLE_SCHEMA = "stegverse.admissibility.bundle.v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def bundle_hash(bundle: Mapping[str, Any]) -> str:
    """Return a stable hash for a bundle-like payload."""
    encoded = json.dumps(bundle, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def build_admissibility_bundle(
    *,
    tester_packet: Mapping[str, Any],
    result_packet: Mapping[str, Any],
    receipt_reference: Mapping[str, Any],
    bridge_type: str = "generic_tester_packet",
    execution_receipt: Optional[Mapping[str, Any]] = None,
    source: str = "sdk_admissibility_bundle",
) -> Dict[str, Any]:
    """Build a portable governed admissibility bundle."""
    bundle = {
        "schema": ADMISSIBILITY_BUNDLE_SCHEMA,
        "created_at": _utc_now(),
        "source": source,
        "bridge_type": bridge_type,
        "tester_packet": dict(tester_packet),
        "admissibility_result": dict(result_packet),
        "admissibility_receipt_reference": dict(receipt_reference),
        "execution_receipt": dict(execution_receipt) if execution_receipt is not None else None,
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_execution_proof": True,
        },
        "hashes": {
            "tester_packet_hash": bundle_hash(tester_packet),
            "admissibility_result_hash": bundle_hash(result_packet),
            "admissibility_reference_hash": bundle_hash(receipt_reference),
            "execution_receipt_hash": bundle_hash(execution_receipt) if execution_receipt is not None else None,
        },
    }
    bundle["bundle_hash"] = bundle_hash(bundle)
    return bundle


def verify_admissibility_bundle(bundle: Mapping[str, Any]) -> bool:
    """Return True if a governed admissibility bundle is structurally valid."""
    required = {
        "schema",
        "created_at",
        "source",
        "bridge_type",
        "tester_packet",
        "admissibility_result",
        "admissibility_receipt_reference",
        "execution_receipt",
        "boundary",
        "hashes",
        "bundle_hash",
    }
    if not required.issubset(bundle.keys()):
        return False
    if bundle.get("schema") != ADMISSIBILITY_BUNDLE_SCHEMA:
        return False

    reference = bundle.get("admissibility_receipt_reference")
    if not isinstance(reference, Mapping):
        return False
    if not verify_admissibility_receipt_reference(reference):
        return False

    hashes = bundle.get("hashes")
    if not isinstance(hashes, Mapping):
        return False

    if hashes.get("tester_packet_hash") != bundle_hash(bundle.get("tester_packet", {})):
        return False
    if hashes.get("admissibility_result_hash") != bundle_hash(bundle.get("admissibility_result", {})):
        return False
    if hashes.get("admissibility_reference_hash") != bundle_hash(reference):
        return False

    execution_receipt = bundle.get("execution_receipt")
    expected_execution_hash = bundle_hash(execution_receipt) if execution_receipt is not None else None
    if hashes.get("execution_receipt_hash") != expected_execution_hash:
        return False

    copied = dict(bundle)
    supplied_hash = copied.pop("bundle_hash")
    return supplied_hash == bundle_hash(copied)
