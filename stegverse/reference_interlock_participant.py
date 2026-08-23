from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from .interlock_transition import validate_interlock_transition
from .interlock_return import validate_interlock_return

RECEIPT_SCHEMA = "stegverse.reference-participant-receipt.v1"


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _required(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} is required")
    return text


def _hash(value: Any, name: str) -> str:
    text = _required(value, name)
    if not text.startswith("sha256:") or len(text) != 71:
        raise ValueError(f"{name} must be sha256:<64 hex>")
    int(text[7:], 16)
    return text


def issue_reference_receipt(
    *,
    participant_id: str,
    state_id: str,
    state_hash: str,
    predecessor_receipt_hashes: Sequence[str] = (),
) -> dict[str, Any]:
    """Issue a deterministic participant-owned state receipt; no StegVerse authority is implied."""
    participant = _required(participant_id, "participant_id")
    state = _required(state_id, "state_id")
    state_digest = _hash(state_hash, "state_hash")
    predecessors = [_hash(item, "predecessor_receipt_hash") for item in predecessor_receipt_hashes]
    core = {
        "schema": RECEIPT_SCHEMA,
        "issuer": participant,
        "state_id": state,
        "state_hash": state_digest,
        "predecessor_receipt_hashes": predecessors,
        "authority": {
            "issuer_asserts_own_state": True,
            "stegverse_truth_assumed": False,
            "stegverse_authority_transferred": False,
        },
    }
    digest = canonical_hash(core)
    return {**core, "receipt_id": f"{participant}:{digest[7:23]}", "receipt_hash": digest}


def build_reference_interlock_ingress(
    *,
    participant_receipt: Mapping[str, Any],
    package_id: str,
    transition_id: str,
    run_id: str,
    governance_mode: str,
    governance_profiles: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Manifest a participant terminal receipt into the public StegVerse interlock contract."""
    receipt = dict(participant_receipt)
    _required(receipt.get("receipt_id"), "participant_receipt.receipt_id")
    participant = _required(receipt.get("issuer"), "participant_receipt.issuer")
    receipt_hash = _hash(receipt.get("receipt_hash"), "participant_receipt.receipt_hash")
    state_id = _required(receipt.get("state_id"), "participant_receipt.state_id")
    state_hash = _hash(receipt.get("state_hash"), "participant_receipt.state_hash")

    manifest_core = {
        "participant_id": participant,
        "participant_receipt_hash": receipt_hash,
        "source_state_hash": state_hash,
        "package_id": _required(package_id, "package_id"),
        "transition_id": _required(transition_id, "transition_id"),
        "run_id": _required(run_id, "run_id"),
    }
    manifest_hash = canonical_hash(manifest_core)
    boundary_state_id = f"stegverse:boundary:{transition_id}"
    boundary_state_hash = canonical_hash({"manifest_hash": manifest_hash, "participant_receipt_hash": receipt_hash})
    participant_binding_hash = canonical_hash({
        "participant_receipt_hash": receipt_hash,
        "manifest_hash": manifest_hash,
        "transition_id": transition_id,
    })

    record = {
        "schema": "stegverse.interlock-transition.v1",
        "package_id": package_id,
        "transition_id": transition_id,
        "run_id": run_id,
        "connection": {
            "class": "INTERLOCK",
            "direction": "INGRESS",
            "participant_id": participant,
            "participant_boundary_receipt_hash": receipt_hash,
            "participant_binding_hash": participant_binding_hash,
        },
        "manifest": {
            "manifest_hash": manifest_hash,
            "source_state_hash": state_hash,
            "canonicalization": "JCS_RFC8785_NFC",
            "predecessor_receipts": [{
                "receipt_id": receipt["receipt_id"],
                "issuer": participant,
                "receipt_hash": receipt_hash,
            }],
        },
        "governance": {"mode": governance_mode, "profiles": [dict(item) for item in governance_profiles]},
        "manifold": {
            "predecessors": [{"state_id": state_id, "state_hash": state_hash}],
            "successors": [{"state_id": boundary_state_id, "state_hash": boundary_state_hash}],
            "relationships": [{"from_state_id": state_id, "to_state_id": boundary_state_id, "type": "CAUSE"}],
        },
        "boundary": {"state": "ACCEPT", "original_manifest_hash": manifest_hash, "repaired_manifest_hash": None},
        "authority": {
            "sdk_authority": "NONE",
            "participant_truth_assumed": False,
            "interlock_transfers_authority": False,
            "master_records_custody_claimed": False,
            "execution_authorized": False,
        },
        "reconstruction": {
            "required": True,
            "replay_scope": "MATERIAL_CAUSAL_CLOSURE",
            "linear_chain_is_special_case": True,
        },
    }
    validate_interlock_transition(record)
    return record


def acknowledge_interlock_return(
    return_record: Mapping[str, Any],
    *,
    successor_state_id: str,
    successor_state_hash: str,
) -> dict[str, Any]:
    """Bind the exact StegVerse egress receipt into a participant-owned successor receipt."""
    value = dict(return_record)
    validate_interlock_return(value)
    acknowledgement = dict(value.get("acknowledgement") or {})
    if acknowledgement.get("state") != "PENDING":
        raise ValueError("reference acknowledgement requires PENDING return")
    participant = _required(value.get("participant_id"), "participant_id")
    receipts = list(value.get("egress", {}).get("receipts") or [])
    if not receipts:
        raise ValueError("return requires egress receipt")
    egress_hash = _hash(receipts[0].get("receipt_hash"), "egress receipt_hash")
    successor = issue_reference_receipt(
        participant_id=participant,
        state_id=successor_state_id,
        state_hash=successor_state_hash,
        predecessor_receipt_hashes=[egress_hash],
    )
    participant_binding_hash = canonical_hash({
        "participant_id": participant,
        "received_egress_receipt_hash": egress_hash,
        "successor_receipt_hash": successor["receipt_hash"],
    })
    resolved = {
        **value,
        "acknowledgement": {
            "state": "ACKNOWLEDGED",
            "received_egress_receipt_hash": egress_hash,
            "participant_binding_hash": participant_binding_hash,
            "participant_successor_receipts": [{
                "receipt_id": successor["receipt_id"],
                "issuer": successor["issuer"],
                "receipt_hash": successor["receipt_hash"],
            }],
        },
        "relationships": [{
            "from_receipt_hash": egress_hash,
            "to_receipt_hash": successor["receipt_hash"],
            "type": "BINDS_AS_PREDECESSOR",
        }],
    }
    validate_interlock_return(resolved)
    return {"return_record": resolved, "participant_successor_receipt": successor}


__all__ = [
    "RECEIPT_SCHEMA",
    "canonical_hash",
    "issue_reference_receipt",
    "build_reference_interlock_ingress",
    "acknowledge_interlock_return",
]
