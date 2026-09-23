"""Non-authorizing, manifest-compatible three-worker admissibility experiment.

This checks the existing SDK group result and explicitly supplied evidence
descriptors. It NEVER issues CTA/InTr decisions, attests independence, or calls
Master Records. Authentic runtime proof must come from existing authorities.
"""
from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
import re
from typing import Any

from .manifest_contract import validate_ingress_manifest
from .purpose_bound_worker_processor import (
    GROUP_REQUEST_SCHEMA, GROUP_RESULT_SCHEMA, REQUEST_EXTENSION,
    _group_result_commitment, derive_group_worker_requests,
    validate_purpose_bound_worker_request,
)

SCHEMA = "stegverse.sdk.micro-node-commit-time-experiment.v1"
SHA = re.compile(r"^[0-9a-f]{64}$")
DISPOSITIONS = {"ALLOW", "DENY", "FAIL_CLOSED", "ESCALATE", "REFUSE"}


def _hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def _sha(value: Any, name: str) -> str:
    if not isinstance(value, str) or SHA.fullmatch(value) is None:
        raise ValueError(f"{name} must be lowercase sha256")
    return value


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value


def evaluate_three_worker_experiment(
    manifest: Mapping[str, Any],
    group_result: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate source-test fixtures; never elevate descriptions into runtime proof."""
    canonical = validate_ingress_manifest(manifest)
    request = validate_purpose_bound_worker_request(
        _mapping(canonical["extensions"], "extensions").get(REQUEST_EXTENSION)
    )
    if request["schema"] != GROUP_REQUEST_SCHEMA or request["worker_count"] != 3:
        raise ValueError("exactly three existing SDK group workers are required")
    if canonical["processing"]["capability"] != "purpose_bound_worker":
        raise ValueError("the installed purpose-bound worker route is required")
    if group_result.get("schema") != GROUP_RESULT_SCHEMA or group_result.get("test_id") != request["test_id"]:
        raise ValueError("group result schema or test identity mismatch")
    if group_result.get("worker_count") != 3 or group_result.get("partition_ids") != request["partition_ids"]:
        raise ValueError("group worker or partition identity mismatch")

    derived = derive_group_worker_requests(manifest)
    bindings = group_result.get("result_bindings")
    if not isinstance(bindings, list) or len(bindings) != 3:
        raise ValueError("three result bindings required")
    seen_workers: set[str] = set()
    for i, binding in enumerate(bindings):
        row = _mapping(binding, "result binding")
        expected = derived[i]["transition_cell"]["candidate"]["partition_binding"]
        if row.get("partition_id") != request["partition_ids"][i] or row.get("partition_binding") != expected:
            raise ValueError("disjoint partition binding mismatch")
        worker = row.get("worker_id")
        if not isinstance(worker, str) or not worker or worker in seen_workers:
            raise ValueError("three distinct result worker identities required")
        seen_workers.add(worker)
        _sha(row.get("task_result_hash"), "task_result_hash")
        _sha(row.get("records_packet_hash"), "records_packet_hash")

    expected_group = _group_result_commitment(request["test_id"], 3, bindings)
    if group_result.get("group_result_binding_sha256") != expected_group:
        raise ValueError("group result commitment mismatch")
    if group_result.get("partition_reconstruction", {}).get("exact") is not True:
        raise ValueError("exact source partition reconstruction required")
    source = canonical["payload"]["text"]
    if group_result["partition_reconstruction"].get("source_sha256") != hashlib.sha256(source.encode()).hexdigest():
        raise ValueError("source partition hash mismatch")
    if group_result["partition_reconstruction"].get("reconstructed_sha256") != hashlib.sha256(source.encode()).hexdigest():
        raise ValueError("reconstructed partition hash mismatch")
    if group_result.get("records_only") is not True or group_result.get("worker_live_after_close") is not False:
        raise ValueError("group result must retire all workers and retain records only")

    ev = _mapping(evidence, "evidence")
    if ev.get("schema") != SCHEMA:
        raise ValueError("experiment evidence schema mismatch")
    if ev.get("manifest_sha256") != _hash(manifest):
        raise ValueError("exact ingress manifest identity mismatch")
    if ev.get("transition_id") != ev.get("standing", {}).get("transition_id"):
        raise ValueError("transition identity mismatch")
    rows = ev.get("workers")
    if not isinstance(rows, list) or len(rows) != 3:
        raise ValueError("three attributable worker evidence rows required")
    reasons: list[str] = []
    original_sources: list[str] = []
    custodians: list[str] = []
    dissent: list[str] = []
    unknown: list[str] = []
    for index, item in enumerate(rows):
        row = _mapping(item, "worker evidence")
        if row.get("worker_id") != bindings[index]["worker_id"] or row.get("partition_id") != bindings[index]["partition_id"]:
            raise ValueError("worker evidence is not bound to its exact result")
        if row.get("result_binding_sha256") != _hash(bindings[index]):
            raise ValueError("worker evidence/result binding hash mismatch")
        source_id = row.get("source_id")
        custodian = row.get("custodian_id")
        if not isinstance(source_id, str) or not source_id or not isinstance(custodian, str) or not custodian:
            raise ValueError("source and custody origin must be attributable")
        original_sources.append(source_id)
        custodians.append(custodian)
        observation = row.get("observation")
        if observation not in {"KNOWN", "UNKNOWN", "DISSENT"}:
            raise ValueError("observation must retain KNOWN, UNKNOWN or DISSENT")
        if observation == "UNKNOWN":
            unknown.append(row["worker_id"])
        if observation == "DISSENT":
            dissent.append(row["worker_id"])
        if row.get("mandatory_evidence_present") is not True:
            reasons.append("WORKER_MISSING_MANDATORY_EVIDENCE")
        if row.get("independence_verified") is not True:
            reasons.append("INDEPENDENT_ORIGIN_NOT_VERIFIED")
        custody = _mapping(row.get("custody"), "worker custody")
        for field in ("previous_receipt_sha256", "reconstructed_predecessor_receipt_sha256",
                      "receipt_sha256", "reconstructed_receipt_sha256"):
            _sha(custody.get(field), field)
        if (
            custody["previous_receipt_sha256"] != custody["reconstructed_predecessor_receipt_sha256"]
            or custody["receipt_sha256"] != custody["reconstructed_receipt_sha256"]
            or custody.get("state") != "RECORDED"
            or custody.get("reconstruction_status") != "PASS"
            or custody.get("required_evidence_validation_status") != "PASS"
        ):
            reasons.append("CANONICAL_PREDECESSOR_CUSTODY_UNVERIFIED")

    # Unique declared sources/custodians are necessary but not proof of independence.
    if len(set(original_sources)) != 3 or len(set(custodians)) != 3:
        reasons.append("CORRELATED_EVIDENCE_OR_CUSTODY_ORIGINS")
    if unknown:
        reasons.append("UNKNOWN_RETAINED")
    if dissent:
        reasons.append("DISSENT_RETAINED")
    standing = _mapping(ev.get("standing"), "standing")
    if standing.get("cta_disposition") not in DISPOSITIONS:
        raise ValueError("original CTA disposition must be preserved")
    for field in ("policy_sha256", "current_state_sha256", "warrant_sha256"):
        _sha(standing.get(field), field)
    if standing.get("current_at_commit") is not True or standing.get("tv_tvc_warrant_verified") is not True:
        reasons.append("COMMIT_TIME_STANDING_UNVERIFIED")
    if standing["cta_disposition"] != "ALLOW":
        reasons.append("CTA_DISPOSITION_" + standing["cta_disposition"])
    # A caller-authored standing/receipt fixture cannot prove authentic CTA, InTr,
    # TV/TVC or Master Records execution even when every local check succeeds.
    if not reasons:
        reasons.append("AUTHENTIC_GOVERNED_RUNTIME_NOT_OBSERVED")
    return {
        "schema": "stegverse.sdk.micro-node-commit-time-local-review.v1",
        "manifest_sha256": _hash(manifest),
        "group_result_binding_sha256": expected_group,
        "worker_count": 3,
        "source_origin_count": len(set(original_sources)),
        "custodian_count": len(set(custodians)),
        "dissent_worker_ids": dissent,
        "unknown_worker_ids": unknown,
        "cta_disposition_preserved": standing["cta_disposition"],
        "reasons": sorted(set(reasons)),
        "decision": "NON_AUTHORIZING_LOCAL_REVIEW_ONLY",
        "authentic_independence_proven": False,
        "authentic_governed_runtime_proven": False,
        "authority_effect": "NONE",
    }
