from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping

SCHEMA_ID = "stegverse.interlock-return.v1"
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
ACK_STATES = {"PENDING", "ACKNOWLEDGED", "REJECTED"}
RELATIONSHIP_TYPES = {"ACKNOWLEDGES", "BINDS_AS_PREDECESSOR", "REJECTS"}


def canonical_hash(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _required_string(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} is required")
    return text


def _require_hash(value: Any, name: str) -> str:
    text = _required_string(value, name)
    if not SHA256_RE.fullmatch(text):
        raise ValueError(f"{name} must be sha256:<64 lowercase hex>")
    return text


def _receipt_ref(item: Mapping[str, Any], name: str) -> str:
    _required_string(item.get("receipt_id"), f"{name}.receipt_id")
    _required_string(item.get("issuer"), f"{name}.issuer")
    return _require_hash(item.get("receipt_hash"), f"{name}.receipt_hash")


def validate_interlock_return(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate reciprocal interlock return structure without granting authority."""
    value = dict(record)
    if value.get("schema") != SCHEMA_ID:
        raise ValueError("unsupported interlock return schema")
    for field in ("package_id", "transition_id", "run_id", "participant_id"):
        _required_string(value.get(field), field)

    binding = dict(value.get("binding") or {})
    _require_hash(binding.get("ingress_interlock_hash"), "binding.ingress_interlock_hash")
    _require_hash(binding.get("governance_record_hash"), "binding.governance_record_hash")
    _require_hash(binding.get("material_causal_closure_hash"), "binding.material_causal_closure_hash")

    egress = dict(value.get("egress") or {})
    egress_manifest_hash = _require_hash(egress.get("manifest_hash"), "egress.manifest_hash")
    _require_hash(egress.get("governed_state_hash"), "egress.governed_state_hash")
    receipts = list(egress.get("receipts") or [])
    if not receipts:
        raise ValueError("egress requires at least one StegVerse receipt")
    egress_hashes = set()
    for index, receipt in enumerate(receipts):
        if not isinstance(receipt, Mapping):
            raise ValueError("egress receipt must be an object")
        receipt_hash = _receipt_ref(receipt, f"egress.receipts[{index}]")
        egress_hashes.add(receipt_hash)

    acknowledgement = dict(value.get("acknowledgement") or {})
    ack_state = acknowledgement.get("state")
    if ack_state not in ACK_STATES:
        raise ValueError("acknowledgement.state is invalid")
    received_hash = acknowledgement.get("received_egress_receipt_hash")
    participant_binding_hash = acknowledgement.get("participant_binding_hash")
    successor_receipts = list(acknowledgement.get("participant_successor_receipts") or [])
    successor_hashes = set()
    for index, receipt in enumerate(successor_receipts):
        if not isinstance(receipt, Mapping):
            raise ValueError("participant successor receipt must be an object")
        receipt_hash = _receipt_ref(receipt, f"acknowledgement.participant_successor_receipts[{index}]")
        successor_hashes.add(receipt_hash)

    if ack_state == "PENDING":
        if received_hash is not None or participant_binding_hash is not None or successor_receipts:
            raise ValueError("PENDING acknowledgement cannot claim participant receipt binding")
    else:
        received = _require_hash(received_hash, "acknowledgement.received_egress_receipt_hash")
        if received not in egress_hashes:
            raise ValueError("participant acknowledgement must bind an exact egress receipt")
        _require_hash(participant_binding_hash, "acknowledgement.participant_binding_hash")
        if not successor_receipts:
            raise ValueError("resolved acknowledgement requires participant successor receipt")

    relationships = list(value.get("relationships") or [])
    if ack_state == "PENDING" and relationships:
        raise ValueError("PENDING acknowledgement cannot assert return relationships")
    for index, edge in enumerate(relationships):
        if not isinstance(edge, Mapping):
            raise ValueError("return relationship must be an object")
        from_hash = _require_hash(edge.get("from_receipt_hash"), f"relationships[{index}].from_receipt_hash")
        to_hash = _require_hash(edge.get("to_receipt_hash"), f"relationships[{index}].to_receipt_hash")
        relation_type = edge.get("type")
        if relation_type not in RELATIONSHIP_TYPES:
            raise ValueError("return relationship type is invalid")
        if from_hash not in egress_hashes or to_hash not in successor_hashes:
            raise ValueError("return relationship must connect egress to participant successor receipts")
        if ack_state == "ACKNOWLEDGED" and relation_type == "REJECTS":
            raise ValueError("ACKNOWLEDGED return cannot use REJECTS relationship")
        if ack_state == "REJECTED" and relation_type != "REJECTS":
            raise ValueError("REJECTED return relationships must use REJECTS")

    if ack_state != "PENDING" and not relationships:
        raise ValueError("resolved acknowledgement requires at least one return relationship")

    reconstruction = dict(value.get("reconstruction") or {})
    if reconstruction.get("required") is not True:
        raise ValueError("reconstruction.required must be true")
    if reconstruction.get("replay_scope") != "MATERIAL_CAUSAL_CLOSURE":
        raise ValueError("reconstruction.replay_scope must be MATERIAL_CAUSAL_CLOSURE")
    if reconstruction.get("egress_manifest_hash") != egress_manifest_hash:
        raise ValueError("reconstruction must bind exact egress manifest")

    authority = dict(value.get("authority") or {})
    required_authority = {
        "sdk_authority": "NONE",
        "participant_truth_assumed": False,
        "return_transfers_authority": False,
        "master_records_custody_claimed": False,
        "execution_authorized": False,
    }
    for field, expected in required_authority.items():
        if authority.get(field) != expected:
            raise ValueError(f"authority.{field} must be {expected!r}")

    return value


__all__ = [
    "SCHEMA_ID",
    "ACK_STATES",
    "RELATIONSHIP_TYPES",
    "canonical_hash",
    "validate_interlock_return",
]
