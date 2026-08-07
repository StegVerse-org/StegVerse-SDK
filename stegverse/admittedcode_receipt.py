"""Non-authorizing SDK consumer for portable AdmittedCode receipts."""
from __future__ import annotations
import hashlib, json
from typing import Any, Mapping

RECEIPT_SCHEMA = "stegverse.provider_harness_receipt.v1"


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def verify_admittedcode_receipt(receipt: Mapping[str, Any]) -> dict:
    required = {"schema", "decision", "key_requested", "gates", "scope", "receipt_id"}
    missing = sorted(required - set(receipt))
    if missing:
        return {"status": "REJECTED", "reason": f"missing_fields:{','.join(missing)}", "sdk_validation_is_execution": False, "sdk_intake_is_authority": False}
    if receipt.get("schema") != RECEIPT_SCHEMA:
        return {"status": "REJECTED", "reason": "unsupported_schema", "sdk_validation_is_execution": False, "sdk_intake_is_authority": False}
    if receipt.get("authority_effect", "NONE") != "NONE":
        return {"status": "REJECTED", "reason": "authority_escalation", "sdk_validation_is_execution": False, "sdk_intake_is_authority": False}
    if receipt.get("decision") not in {"ALLOW", "DENY", "FAIL_CLOSED"}:
        return {"status": "REJECTED", "reason": "invalid_decision", "sdk_validation_is_execution": False, "sdk_intake_is_authority": False}
    if receipt.get("decision") != "ALLOW" and receipt.get("key_requested") is not False:
        return {"status": "REJECTED", "reason": "refusal_reached_key", "sdk_validation_is_execution": False, "sdk_intake_is_authority": False}
    body = dict(receipt)
    supplied = body.pop("receipt_id")
    # provider-harness receipt_id covers the base receipt before portable review annotations.
    body.pop("review_packet", None)
    body.pop("authority_effect", None)
    calculated = "sha256:" + hashlib.sha256(_canonical(body)).hexdigest()
    if supplied != calculated:
        return {"status": "REJECTED", "reason": "receipt_hash_mismatch", "sdk_validation_is_execution": False, "sdk_intake_is_authority": False}
    return {
        "status": "ACCEPTED",
        "decision": receipt["decision"],
        "receipt_id": supplied,
        "sdk_validation_is_execution": False,
        "sdk_intake_is_authority": False,
        "receipt_handoff_is_master_record_installation": False,
        "authority_effect": "NONE",
    }
