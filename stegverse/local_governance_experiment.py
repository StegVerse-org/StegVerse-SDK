from __future__ import annotations

"""Local continuation from SDK_TO_GOVERNANCE into governed result evidence.

This module is a test-only semantic snapshot of the exact pinned governance path
used by the SDK governed-test contract. It consumes the already-materialized SDK
handoff, applies the canonical restrictive three-layer ordering relevant to this
experiment, records the same 10-stop manifested route shape, retains an immutable
exact-run custody record, and performs replay/reconstruction without re-executing
any consequence.

Pinned source basis:
- StegVerse-Labs/StegCore@ef38410505b0ef3e84148892b1d6e3cdef20f300
  - src/stegcore/three_layer.py
  - src/stegcore/transaction_lifecycle.py
  - src/stegcore/manifest_receipts.py
- Data-Continuation/core-lite@72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
  - core_lite/transaction_route.py
- master-records/orchestration@03312236c115bc814024d700810391340648601f
  - services/manifest_receipt_custody.py

It is not a deployed runtime claim and does not replace those packages.
"""

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Mapping


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _evaluate_three_layer(request: Mapping[str, Any]) -> dict[str, Any]:
    j = dict(request.get("judgment") or {})
    s = dict(request.get("signal") or {})
    e = dict(request.get("execution") or {})

    if not j.get("refusal_available"):
        return {"decision": "DENY", "reason_code": "judgment.refusal_unavailable"}
    if j.get("operator_recoverability") in {"degraded", "unavailable", "unknown", None}:
        return {"decision": "DENY", "reason_code": "judgment.operator_recoverability_insufficient"}
    if j.get("workload_state") == "overloaded" or j.get("time_pressure") == "critical":
        return {"decision": "DENY", "reason_code": "judgment.conditions_degraded"}
    if not s.get("admitted_signal_refs"):
        return {"decision": "DENY", "reason_code": "signal.none_admitted"}
    if s.get("missing_inputs") or s.get("uncertainty_state") in {"material", "unknown"}:
        return {"decision": "DENY", "reason_code": "signal.inputs_incomplete"}
    if not s.get("reconstruction_available") or not s.get("transformation_provenance_complete"):
        return {"decision": "DENY", "reason_code": "signal.state_unreconstructable"}
    if not s.get("reference_state_hash") or not s.get("expected_reference_state_hash"):
        return {"decision": "FAIL-CLOSED", "reason_code": "signal.reference_state_missing"}
    if s.get("reference_state_hash") != s.get("expected_reference_state_hash"):
        return {"decision": "FAIL-CLOSED", "reason_code": "signal.reference_state_discontinuous"}
    if not e.get("actor_authority_current"):
        return {"decision": "DENY", "reason_code": "execution.authority_stale"}
    if not e.get("policy_current") or not e.get("delegation_current"):
        return {"decision": "DENY", "reason_code": "execution.policy_or_delegation_stale"}
    if not e.get("evidence_current") or not e.get("validity_window_open"):
        return {"decision": "DENY", "reason_code": "execution.evidence_or_window_invalid"}
    if not e.get("affected_entity_conditions_represented"):
        return {"decision": "DENY", "reason_code": "execution.affected_entities_missing"}
    if e.get("recoverability_profile") == "unknown":
        return {"decision": "FAIL-CLOSED", "reason_code": "execution.recoverability_unknown"}
    return {"decision": "ALLOW", "reason_code": "ok"}


ROUTE_EVENTS = (
    "MANIFEST_ESTABLISHED", "SDK_ENTERED", "INGESTION_ENTERED", "CGE_ADMITTED",
    "CGE_ROUTED", "MODULE_ENTERED", "MODULE_RESULT", "CGE_RETURN_INGESTED",
    "ROUTE_CLEARED", "RETURNED",
)


def _receipt_chain(transaction_id: str, governance_result: Mapping[str, Any]) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    previous = None
    for sequence, event_type in enumerate(ROUTE_EVENTS):
        body = {
            "schema": "stegverse.master-records.manifest-route-event.v1",
            "transaction_id": transaction_id,
            "sequence": sequence,
            "event_type": event_type,
            "checkpoint_id": event_type.lower(),
            "module": "stegcore" if event_type in {"MODULE_ENTERED", "MODULE_RESULT"} else "local-sdk-route",
            "previous_event_hash": previous,
            "authority_granted": False,
            "details": {"governance_result": dict(governance_result)} if event_type == "MODULE_RESULT" else {},
        }
        event_hash = sha256(body)
        receipt = {**body, "event_hash": event_hash, "route_receipt_id": "MRR-" + event_hash.upper()}
        receipts.append(receipt)
        previous = event_hash
    return receipts


def _retain(path: str | Path, package: Mapping[str, Any]) -> dict[str, Any]:
    db = sqlite3.connect(str(path))
    db.execute("CREATE TABLE IF NOT EXISTS exact_runs (manifest_receipt_id TEXT PRIMARY KEY, package_json TEXT NOT NULL, record_sha256 TEXT NOT NULL)")
    package_json = canonical_json(dict(package))
    record_sha = hashlib.sha256(package_json.encode("utf-8")).hexdigest()
    db.execute("INSERT OR REPLACE INTO exact_runs VALUES(?,?,?)", (package["manifest_receipt_id"], package_json, record_sha))
    db.commit(); db.close()
    return {"status": "RECORDED", "record_sha256": record_sha, "custody_path": str(path)}


def _read_retained(path: str | Path, manifest_receipt_id: str) -> tuple[dict[str, Any], str]:
    db = sqlite3.connect(str(path))
    row = db.execute("SELECT package_json, record_sha256 FROM exact_runs WHERE manifest_receipt_id=?", (manifest_receipt_id,)).fetchone()
    db.close()
    if row is None:
        raise KeyError("manifest_receipt_not_found")
    return json.loads(row[0]), str(row[1])


def consume_local_governance_handoff(boundary: Mapping[str, Any], *, custody_db: str | Path) -> dict[str, Any]:
    if boundary.get("schema") != "stegverse.sdk.local-governance-boundary/v1":
        raise ValueError("unsupported_sdk_governance_boundary")
    if boundary.get("boundary_state") != "READY_FOR_GOVERNANCE_CONSUMPTION":
        raise ValueError("governance_boundary_not_ready")
    transition = boundary.get("transition_request") or {}
    request = ((transition.get("input") or {}).get("steggate_request") or {})
    if not request:
        raise ValueError("steggate_request_missing")

    evaluation = _evaluate_three_layer(request)
    disposition = "DENY" if evaluation["decision"] == "DENY" else ("FAIL_CLOSED" if evaluation["decision"] == "FAIL-CLOSED" else "ALLOW")
    executor_invoked = disposition == "ALLOW"
    transaction_id = "TX-" + sha256({"manifest_sha256": boundary["manifest_sha256"], "transition_request_sha256": boundary["transition_request_sha256"]})[:32].upper()
    decision = {
        "schema": "stegverse.local-governance-experiment-decision/v1",
        "transaction_id": transaction_id,
        "governance_state": disposition,
        "canonical_three_layer_decision": evaluation["decision"],
        "reason_code": evaluation["reason_code"],
        "executor_invoked": executor_invoked,
        "external_side_effect": False,
        "source_transition_request_sha256": boundary["transition_request_sha256"],
        "authority_effect": "NONE_TEST_EVIDENCE",
    }
    receipts = _receipt_chain(transaction_id, decision)
    receipt_chain_head = receipts[-1]["event_hash"]
    manifest_receipt_id = "MR-" + sha256({
        "transaction_id": transaction_id,
        "manifest_sha256": boundary["manifest_sha256"],
        "receipt_chain_head": receipt_chain_head,
        "canonical_runtime_identity": "stegverse:steggate:canonical:three-layer:v1",
    }).upper()
    package = {
        "schema": "stegverse.local-governance-experiment-exact-run/v1",
        "manifest_receipt_id": manifest_receipt_id,
        "transaction_id": transaction_id,
        "manifest_sha256": boundary["manifest_sha256"],
        "receipt_chain_head": receipt_chain_head,
        "canonical_runtime_identity": "stegverse:steggate:canonical:three-layer:v1",
        "governance_decision": decision,
        "route_receipts": receipts,
        "route_transition_count": len(receipts),
        "chain_verified": all(r["sequence"] == i and r["previous_event_hash"] == (None if i == 0 else receipts[i-1]["event_hash"]) for i, r in enumerate(receipts)),
        "consequence_reexecuted": False,
    }
    custody = _retain(custody_db, package)

    retained, retained_hash = _read_retained(custody_db, manifest_receipt_id)
    replay_eval = _evaluate_three_layer(request)
    replay_state = "DENY" if replay_eval["decision"] == "DENY" else ("FAIL_CLOSED" if replay_eval["decision"] == "FAIL-CLOSED" else "ALLOW")
    replay = {
        "schema": "stegverse.local-governance-experiment-replay/v1",
        "manifest_receipt_id": manifest_receipt_id,
        "original_disposition": disposition,
        "replay_disposition": replay_state,
        "deterministic_disposition_match": replay_state == disposition,
        "consequence_reexecuted": False,
        "original_record_mutated": False,
    }
    reconstruction = {
        "schema": "stegverse.local-governance-experiment-reconstruction/v1",
        "manifest_receipt_id": manifest_receipt_id,
        "transaction_id": retained["transaction_id"],
        "receipt_chain_head": retained["receipt_chain_head"],
        "route_transition_count": retained["route_transition_count"],
        "chain_verified": retained["chain_verified"],
        "retained_record_sha256": retained_hash,
        "reconstructed_record_sha256": hashlib.sha256(canonical_json(retained).encode("utf-8")).hexdigest(),
        "original_record_mutated": False,
        "consequence_reexecuted": False,
    }
    return {
        "schema": "stegverse.local-governance-experiment-result/v1",
        "boundary_consumed": True,
        "governance_decision": decision,
        "manifest_receipt_id": manifest_receipt_id,
        "custody": custody,
        "exact_run": package,
        "replay": replay,
        "reconstruction": reconstruction,
        "result_returned": True,
        "third_party_evaluator_execution": False,
        "external_package_publication_required": False,
        "source_basis": {
            "stegcore": "ef38410505b0ef3e84148892b1d6e3cdef20f300",
            "core_lite": "72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8",
            "master_records": "03312236c115bc814024d700810391340648601f",
        },
    }


__all__ = ["consume_local_governance_handoff"]
