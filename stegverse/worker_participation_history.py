"""Non-authorizing reconstruction of manifested worker participation histories.

Receipts document continuity of individual transitions. Behavioral hypotheses
require a linked sequence and independently attributed observations. This
module neither verifies canonical Master Records nor executes worker code.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

SCHEMA = "stegverse.sdk.worker-participation-history.v1"
SHA = re.compile(r"^[0-9a-f]{64}$")
TRANSITIONS = {
    ("ASSIGNED", "EVALUATING"), ("EVALUATING", "REFUSED"),
    ("EVALUATING", "WORKING"), ("WORKING", "COMPLETED"),
    ("WORKING", "REFUSED"), ("REFUSED", "CLOSING"),
    ("COMPLETED", "CLOSING"), ("CLOSING", "RETIRED"),
    ("ASSIGNED", "EXPIRED"), ("EVALUATING", "EXPIRED"),
    ("WORKING", "EXPIRED"), ("REFUSED", "EXPIRED"),
    ("CLOSING", "EXPIRED"),
}
OPERATIONS = {"REQUESTED", "DENIED", "ADMITTED", "OBSERVED_EFFECT", "UNKNOWN"}
CUSTODY = "NON_AUTHORIZING_SOURCE_RECONSTRUCTION_ONLY"


def digest(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _sha(value: Any, label: str) -> None:
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError(f"{label} must be lowercase sha256")


def reconstruct_worker_histories(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Inspect exact linked, caller-supplied fixtures; never infer real effects."""
    if packet.get("schema") != SCHEMA:
        raise ValueError("history schema mismatch")
    _sha(packet.get("manifest_sha256"), "manifest_sha256")
    workers = packet.get("workers")
    if not isinstance(workers, list) or not workers:
        raise ValueError("workers required")
    identifiers: set[str] = set()
    histories = []
    for worker in workers:
        if not isinstance(worker, Mapping):
            raise ValueError("worker must be an object")
        wid, partition = worker.get("worker_id"), worker.get("partition_id")
        if not isinstance(wid, str) or not wid or wid in identifiers:
            raise ValueError("unique worker_id required")
        if not isinstance(partition, str) or not partition:
            raise ValueError("partition_id required")
        identifiers.add(wid)
        receipts = worker.get("transitions")
        if not isinstance(receipts, list) or not receipts:
            raise ValueError("transitions required")
        issues: list[str] = []
        previous_hash = None
        previous_state = None
        states = []
        for index, receipt in enumerate(receipts):
            if not isinstance(receipt, Mapping):
                raise ValueError("transition receipt must be an object")
            for field in ("receipt_sha256", "previous_receipt_sha256"):
                _sha(receipt.get(field), field)
            from_state, to_state = receipt.get("from_state"), receipt.get("to_state")
            if not isinstance(from_state, str) or not isinstance(to_state, str):
                raise ValueError("transition states required")
            if index and receipt["previous_receipt_sha256"] != previous_hash:
                issues.append("PREDECESSOR_GAP")
            if index and from_state != previous_state:
                issues.append("STATE_DISCONTINUITY")
            if index == 0 and from_state != "ASSIGNED":
                issues.append("INITIAL_STATE_UNVERIFIED")
            if (from_state, to_state) not in TRANSITIONS:
                issues.append("INVALID_LIFECYCLE_TRANSITION")
            previous_hash = receipt["receipt_sha256"]
            previous_state = to_state
            states.append(to_state)
        observations = worker.get("independent_observations", [])
        if not isinstance(observations, list):
            raise ValueError("independent_observations must be an array")
        observed_effects = []
        attempted = []
        receipt_positions = {r["receipt_sha256"]: n for n, r in enumerate(receipts)}
        refusal_positions = [n for n, r in enumerate(receipts) if r["to_state"] == "REFUSED"]
        for observation in observations:
            if not isinstance(observation, Mapping):
                raise ValueError("observation must be an object")
            if observation.get("operation_disposition") not in OPERATIONS:
                raise ValueError("unknown operation disposition")
            if not isinstance(observation.get("observer_id"), str) or not observation["observer_id"]:
                raise ValueError("observer_id required")
            _sha(observation.get("observation_sha256"), "observation_sha256")
            if observation["operation_disposition"] == "OBSERVED_EFFECT":
                observed_effects.append(observation["observation_sha256"])
            if observation["operation_disposition"] in {"REQUESTED", "DENIED"}:
                attempted.append(observation["observation_sha256"])
            anchor = observation.get("after_receipt_sha256")
            if anchor not in receipt_positions or (refusal_positions and
                    receipt_positions.get(anchor, -1) < refusal_positions[0] and
                    observation["operation_disposition"] in {"REQUESTED", "DENIED", "OBSERVED_EFFECT"}):
                issues.append("OBSERVATION_SEQUENCE_UNBOUND")
            # An observer label in a caller-authored fixture is not proof of independence.
        complete_chain = not issues
        refused = "REFUSED" in states
        retired = states[-1] == "RETIRED"
        expired = states[-1] == "EXPIRED"
        if refused and not (retired or expired):
            issues.append("REFUSAL_NOT_TERMINALLY_CLOSED")
        if not (retired or expired):
            issues.append("WORKER_NOT_TERMINAL")
        if not observations:
            issues.append("EXTERNAL_EFFECT_UNOBSERVED")
        if issues:
            classification = "INCOMPLETE_HISTORY"
        elif refused and attempted:
            classification = "REFUSAL_WITH_REPORTED_SUBSEQUENT_ATTEMPT"
        elif refused:
            classification = "REFUSAL_WITH_NO_REPORTED_SUBSEQUENT_ATTEMPT"
        else:
            classification = "OTHER_RECONSTRUCTED_PARTICIPATION"
        histories.append({
            "worker_id": wid, "partition_id": partition,
            "receipt_count": len(receipts), "states": states,
            "refused": refused, "retired": retired, "expired": expired,
            "predecessor_continuity_claim_consistent": complete_chain,
            "reported_attempt_count": len(attempted),
            "reported_external_effect_count": len(observed_effects),
            "classification": classification, "limitations": sorted(set(issues)),
            "external_effect_independently_proven": False,
            "master_records_verified": False,
        })
    return {"schema": "stegverse.sdk.worker-participation-history-review.v1",
            "manifest_sha256": packet["manifest_sha256"], "histories": histories,
            "decision": CUSTODY, "authority_effect": "NONE",
            "authentic_runtime_proven": False}
