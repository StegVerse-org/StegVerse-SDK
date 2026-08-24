from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from .interlock_return import validate_interlock_return
from .interlock_transition import canonical_hash as interlock_hash, validate_interlock_transition
from .portable_governance_exchange import create_exchange, verify_exchange
from .portable_governance_verifier import verify_portable_governance_bundle
from .reference_interlock_participant import acknowledge_interlock_return

RETURN_SCHEMA = "stegverse.interlock-return.v1"
PROOF_SCHEMA = "stegverse.sdk.post-return-production-proof.v1"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _prefixed(value: Any, field: str) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("sha256:"):
        digest = text[7:]
    else:
        digest = text
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError(f"{field} must be a SHA-256 digest")
    return "sha256:" + digest


def build_pending_interlock_return(
    ingress: Mapping[str, Any],
    sovereign_result: Mapping[str, Any],
    custody_record: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind an exact canonical sovereign run and Master Records record into return evidence."""
    ingress_value = validate_interlock_transition(ingress)
    result = dict(sovereign_result)
    custody = dict(custody_record)

    if result.get("master_records_custody_status") != "RECORDED":
        raise ValueError("canonical run is not recorded in Master Records")
    if result.get("chain_verified") is not True:
        raise ValueError("canonical StegCore receipt chain is not verified")
    if result.get("transaction_identity_continuous") is not True:
        raise ValueError("canonical transaction identity is discontinuous")
    if not isinstance(result.get("execution_result"), Mapping):
        raise ValueError("canonical run has no bounded execution result")
    if result["execution_result"].get("state_transition_performed") is not True:
        raise ValueError("canonical run did not perform the required bounded state transition")

    rid = str(result.get("manifest_receipt_id") or "").strip().upper()
    if not rid.startswith("MR-"):
        raise ValueError("canonical manifest_receipt_id is required")
    if str(custody.get("manifest_receipt_id") or "").strip().upper() != rid:
        raise ValueError("custody manifest receipt identity mismatch")
    evidence = custody.get("evidence_package")
    if not isinstance(evidence, Mapping):
        raise ValueError("custody evidence_package is required")
    if str(evidence.get("transaction_id") or "") != str(result.get("transaction_id") or ""):
        raise ValueError("custody transaction identity mismatch")

    master_record_hash = _prefixed(custody.get("master_record_sha256"), "master_record_sha256")
    manifest_hash = _prefixed(evidence.get("manifest_hash"), "evidence_package.manifest_hash")
    route_chain_head = _prefixed(result.get("route_receipt_chain_head"), "route_receipt_chain_head")
    governed_state_hash = _hash({
        "transaction_id": result["transaction_id"],
        "manifest_receipt_id": rid,
        "governance_state": result.get("governance_state"),
        "result_binding_hash": result.get("result_binding_hash"),
        "execution_result": result["execution_result"],
    })
    closure_hash = _hash({
        "ingress_interlock_hash": interlock_hash(ingress_value),
        "master_record_sha256": master_record_hash,
        "route_receipt_chain_head": route_chain_head,
        "governed_state_hash": governed_state_hash,
        "result_binding_hash": result.get("result_binding_hash"),
        "execution_result": result["execution_result"],
    })

    record = {
        "schema": RETURN_SCHEMA,
        "package_id": ingress_value["package_id"],
        "transition_id": ingress_value["transition_id"],
        "run_id": ingress_value["run_id"],
        "participant_id": ingress_value["connection"]["participant_id"],
        "binding": {
            "ingress_interlock_hash": interlock_hash(ingress_value),
            "governance_record_hash": master_record_hash,
            "material_causal_closure_hash": closure_hash,
        },
        "egress": {
            "manifest_hash": manifest_hash,
            "governed_state_hash": governed_state_hash,
            "receipts": [{
                "receipt_id": rid,
                "issuer": "StegVerse/MasterRecords",
                "receipt_hash": master_record_hash,
            }],
        },
        "acknowledgement": {
            "state": "PENDING",
            "received_egress_receipt_hash": None,
            "participant_binding_hash": None,
            "participant_successor_receipts": [],
        },
        "relationships": [],
        "reconstruction": {
            "required": True,
            "replay_scope": "MATERIAL_CAUSAL_CLOSURE",
            "egress_manifest_hash": manifest_hash,
        },
        "authority": {
            "sdk_authority": "NONE",
            "participant_truth_assumed": False,
            "return_transfers_authority": False,
            "master_records_custody_claimed": False,
            "execution_authorized": False,
        },
    }
    return validate_interlock_return(record)


def build_post_return_bundle(
    pre_steggate_bundle: Mapping[str, Any],
    acknowledged_return: Mapping[str, Any],
) -> dict[str, Any]:
    """Promote the exact PRE_STEGGATE bundle only when a reciprocal return is valid."""
    pre = dict(pre_steggate_bundle)
    pre_report = verify_portable_governance_bundle(pre)
    if pre_report.get("stage") != "PRE_STEGGATE":
        raise ValueError("source bundle must be PRE_STEGGATE")
    returned = validate_interlock_return(acknowledged_return)
    if returned.get("acknowledgement", {}).get("state") != "ACKNOWLEDGED":
        raise ValueError("POST_RETURN requires participant ACKNOWLEDGED return")
    for field in ("package_id", "transition_id", "run_id"):
        if returned.get(field) != pre.get(field):
            raise ValueError(f"return {field} mismatch")
    bundle = {**pre, "stage": "POST_RETURN", "interlock_return": returned}
    verify_portable_governance_bundle(bundle)
    return bundle


def complete_post_return_evidence(
    *,
    pre_steggate_bundle: Mapping[str, Any],
    sovereign_result: Mapping[str, Any],
    custody_record: Mapping[str, Any],
    successor_state_id: str,
    successor_state_hash: str,
    exchange_path: str | Path,
    replay: Callable[[str], Mapping[str, Any]],
    reconstruct: Callable[[str], Mapping[str, Any]],
) -> dict[str, Any]:
    """Finish return, exchange, independent verification, replay, and reconstruction after the canonical run."""
    pending = build_pending_interlock_return(
        pre_steggate_bundle["ingress_interlock"],
        sovereign_result,
        custody_record,
    )
    acknowledgement = acknowledge_interlock_return(
        pending,
        successor_state_id=successor_state_id,
        successor_state_hash=successor_state_hash,
    )
    acknowledged = acknowledgement["return_record"]
    post_bundle = build_post_return_bundle(pre_steggate_bundle, acknowledged)
    independent_report = verify_portable_governance_bundle(post_bundle)

    exchange = create_exchange(post_bundle, Path(exchange_path))
    exchange_verification = verify_exchange(Path(exchange_path))
    rid = str(sovereign_result["manifest_receipt_id"])
    replay_result = dict(replay(rid))
    reconstruct_result = dict(reconstruct(rid))

    if replay_result.get("deterministic_disposition_match") is not True:
        raise ValueError("replay disposition mismatch")
    if replay_result.get("consequence_reexecuted") is not False:
        raise ValueError("replay reexecuted consequence")
    if replay_result.get("operation_transition_custody_status") != "RECORDED":
        raise ValueError("replay operation transition is not in custody")
    if reconstruct_result.get("manifest_receipt_id") != rid:
        raise ValueError("reconstruction manifest receipt mismatch")
    if reconstruct_result.get("consequence_reexecuted") is not False:
        raise ValueError("reconstruction reexecuted consequence")
    if reconstruct_result.get("original_record_mutated") is not False:
        raise ValueError("reconstruction mutated original record")
    if reconstruct_result.get("operation_transition_custody_status") != "RECORDED":
        raise ValueError("reconstruction operation transition is not in custody")

    return {
        "schema": PROOF_SCHEMA,
        "status": "PASS",
        "manifest_receipt_id": rid,
        "transaction_id": sovereign_result["transaction_id"],
        "governance_state": sovereign_result.get("governance_state"),
        "bounded_consequence": dict(sovereign_result["execution_result"]),
        "master_records": {
            "status": "RECORDED",
            "master_record_sha256": custody_record["master_record_sha256"],
        },
        "interlock_return_state": acknowledged["acknowledgement"]["state"],
        "participant_successor_receipt": acknowledgement["participant_successor_receipt"],
        "portable_verification": independent_report,
        "exchange": exchange,
        "exchange_verification": exchange_verification,
        "replay": replay_result,
        "reconstruction": reconstruct_result,
        "authority": {
            "sdk_authority": "NONE",
            "verification_authority": "NONE",
            "exchange_authority": "NONE",
            "copied_evidence_is_canonical_custody": False,
        },
    }


__all__ = [
    "RETURN_SCHEMA",
    "PROOF_SCHEMA",
    "build_pending_interlock_return",
    "build_post_return_bundle",
    "complete_post_return_evidence",
]
