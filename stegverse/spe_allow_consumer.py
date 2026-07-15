"""Consume Standing-Proof-Engine receipts without converting ALLOW into execution.

A valid SPE ALLOW receipt permits progression to a separately governed authority
boundary only. It never grants execution, delegation, mutation, publication,
admissibility, or custody authority.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping


SPE_ALLOW_CONSUMER_SCHEMA_VERSION = "stegverse.sdk.spe_allow_consumer.v0.1"


class SPEAllowConsumerError(ValueError):
    """Raised when an SPE receipt or progression packet violates the contract."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + sha256(_canonical(value).encode("utf-8")).hexdigest()


def validate_spe_receipt(
    receipt: Mapping[str, Any],
    *,
    expected_transition_id: str,
    expected_run_id: str,
    expected_candidate_hash: str,
) -> dict[str, Any]:
    """Validate an identity-bound SPE standing receipt."""
    if receipt.get("schema") != "stegverse.spe.standing_receipt.v0.1":
        raise SPEAllowConsumerError("unsupported SPE receipt schema")

    for field, expected in (
        ("transition_id", expected_transition_id),
        ("run_id", expected_run_id),
        ("candidate_hash", expected_candidate_hash),
    ):
        if str(receipt.get(field, "")) != str(expected):
            raise SPEAllowConsumerError(f"SPE receipt {field} mismatch")

    decision = str(receipt.get("decision", ""))
    if decision not in {"ALLOW", "DENY", "FAIL_CLOSED"}:
        raise SPEAllowConsumerError("invalid SPE decision")

    if not str(receipt.get("receipt_id", "")).strip():
        raise SPEAllowConsumerError("SPE receipt_id is required")
    if not str(receipt.get("policy_ref", "")).strip():
        raise SPEAllowConsumerError("SPE policy_ref is required")
    if not str(receipt.get("standing_evidence_ref", "")).strip():
        raise SPEAllowConsumerError("SPE standing_evidence_ref is required")

    protected_false = (
        "authorizing",
        "execution_authority_granted",
        "delegation_granted",
        "mutation_authorized",
        "publication_authorized",
        "custody_transferred",
        "admissibility_determined",
    )
    for field in protected_false:
        if receipt.get(field) is not False:
            raise SPEAllowConsumerError(f"SPE receipt escalated {field}")

    expected = dict(receipt)
    receipt_hash = expected.pop("receipt_hash", None)
    if receipt_hash != _digest(expected):
        raise SPEAllowConsumerError("SPE receipt digest mismatch")
    return dict(receipt)


def build_progression_packet(
    receipt: Mapping[str, Any],
    *,
    expected_transition_id: str,
    expected_run_id: str,
    expected_candidate_hash: str,
    next_boundary: str,
) -> dict[str, Any]:
    """Build a deterministic progression packet from a validated SPE receipt."""
    validated = validate_spe_receipt(
        receipt,
        expected_transition_id=expected_transition_id,
        expected_run_id=expected_run_id,
        expected_candidate_hash=expected_candidate_hash,
    )
    if not next_boundary.strip():
        raise SPEAllowConsumerError("next_boundary is required")

    decision = validated["decision"]
    progression_permitted = decision == "ALLOW"
    body = {
        "schema": SPE_ALLOW_CONSUMER_SCHEMA_VERSION,
        "transition_id": expected_transition_id,
        "run_id": expected_run_id,
        "candidate_hash": expected_candidate_hash,
        "spe_receipt_id": validated["receipt_id"],
        "spe_receipt_hash": validated["receipt_hash"],
        "spe_decision": decision,
        "standing_evidence_ref": validated["standing_evidence_ref"],
        "policy_ref": validated["policy_ref"],
        "next_boundary": next_boundary,
        "progression_permitted": progression_permitted,
        "progression_status": (
            "READY_FOR_NEXT_GOVERNED_BOUNDARY"
            if progression_permitted
            else "PROGRESSION_BLOCKED"
        ),
        "execution_permitted": False,
        "authorizing": False,
        "execution_authority_granted": False,
        "delegation_granted": False,
        "mutation_authorized": False,
        "publication_authorized": False,
        "custody_transferred": False,
        "admissibility_determined": False,
        "fresh_authority_determination_required": True,
    }
    body["progression_packet_id"] = _digest(body)
    return body


def validate_progression_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    if packet.get("schema") != SPE_ALLOW_CONSUMER_SCHEMA_VERSION:
        raise SPEAllowConsumerError("unsupported progression packet schema")
    for field in (
        "execution_permitted",
        "authorizing",
        "execution_authority_granted",
        "delegation_granted",
        "mutation_authorized",
        "publication_authorized",
        "custody_transferred",
        "admissibility_determined",
    ):
        if packet.get(field) is not False:
            raise SPEAllowConsumerError(f"progression packet escalated {field}")
    if packet.get("fresh_authority_determination_required") is not True:
        raise SPEAllowConsumerError("fresh authority determination must remain required")
    decision = packet.get("spe_decision")
    expected_progression = decision == "ALLOW"
    if packet.get("progression_permitted") is not expected_progression:
        raise SPEAllowConsumerError("progression decision mismatch")
    expected = dict(packet)
    packet_id = expected.pop("progression_packet_id", None)
    if packet_id != _digest(expected):
        raise SPEAllowConsumerError("progression packet digest mismatch")
    return dict(packet)


__all__ = [
    "SPE_ALLOW_CONSUMER_SCHEMA_VERSION",
    "SPEAllowConsumerError",
    "validate_spe_receipt",
    "build_progression_packet",
    "validate_progression_packet",
]
