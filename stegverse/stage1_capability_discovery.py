"""Stage-1 capability discovery over EXISTING SDK three-worker evidence descriptors.

Pure source-shape comparison. No external attestation, authority, credentials,
resident invocation, Master Records query, or claim of actual observations.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .micro_node_commit_time_experiment import (
    _hash, _mapping, _sha, evaluate_three_worker_experiment,
)

SCHEMA = "stegverse.sdk.stage1-capability-discovery.v1"
CAPABILITIES = ("INGEST", "OBSERVE", "RECONSTRUCT")
STATUSES = {"CLAIMED", "UNSUPPORTED", "UNKNOWN", "DISSENT"}
EXIT_STATES = {"LOCAL_FIXTURE_CONSISTENT", "LOCAL_FIXTURE_INCOMPLETE"}


def review_stage1_capabilities(
    manifest: Mapping[str, Any],
    group_result: Mapping[str, Any],
    evidence: Mapping[str, Any],
    descriptor: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate exact bindings and preserve limitations without proving independence."""
    base = evaluate_three_worker_experiment(manifest, group_result, evidence)
    d = _mapping(descriptor, "stage1 descriptor")
    if d.get("schema") != SCHEMA:
        raise ValueError("stage1 descriptor schema mismatch")
    if d.get("manifest_sha256") != base["manifest_sha256"]:
        raise ValueError("stage1 manifest identity mismatch")
    if d.get("group_result_binding_sha256") != base["group_result_binding_sha256"]:
        raise ValueError("stage1 group identity mismatch")
    rows = d.get("participants")
    if not isinstance(rows, list) or len(rows) != 3:
        raise ValueError("exact three participant evidence rows required")
    bound_workers = evidence["workers"]
    source_by_origin: dict[str, str] = {}
    shared_packets: dict[str, str] = {}
    issues: set[str] = set()
    outcomes: list[dict[str, Any]] = []
    statuses_by_capability: dict[str, list[str]] = {x: [] for x in CAPABILITIES}
    for i, item in enumerate(rows):
        row = _mapping(item, "participant")
        worker = _mapping(bound_workers[i], "existing worker")
        if row.get("worker_id") != worker["worker_id"]:
            raise ValueError("stage1 worker attribution mismatch")
        if row.get("result_binding_sha256") != worker["result_binding_sha256"]:
            raise ValueError("stage1 result binding mismatch")
        if row.get("source_id") != worker["source_id"] or row.get("custodian_id") != worker["custodian_id"]:
            raise ValueError("stage1 origin/custodian mismatch")
        if row.get("observation") != worker["observation"]:
            raise ValueError("stage1 UNKNOWN/DISSENT mismatch")
        packet = _sha(row.get("observation_packet_sha256"), "observation_packet_sha256")
        origin = row["source_id"]
        if origin in source_by_origin and source_by_origin[origin] != row["worker_id"]:
            issues.add("CORRELATED_ORIGIN")
        source_by_origin[origin] = row["worker_id"]
        if packet in shared_packets:
            issues.add("SHARED_OBSERVATION_PACKET")
        shared_packets[packet] = row["worker_id"]
        limits = row.get("observation_limits")
        if not isinstance(limits, list) or not limits or any(not isinstance(x, str) or not x.strip() for x in limits):
            raise ValueError("explicit nonempty observation limits required")
        capabilities = _mapping(row.get("capabilities"), "capabilities")
        if set(capabilities) != set(CAPABILITIES):
            raise ValueError("exact Stage-1 capability keys required")
        summary: dict[str, str] = {}
        for name in CAPABILITIES:
            claim = _mapping(capabilities[name], "capability")
            status = claim.get("status")
            if status not in STATUSES:
                raise ValueError("invalid capability status")
            if status == "CLAIMED":
                _sha(claim.get("evidence_sha256"), "capability evidence_sha256")
                if claim.get("evidence_sha256") != packet:
                    issues.add("CAPABILITY_PACKET_BINDING_MISMATCH")
            else:
                if claim.get("evidence_sha256") is not None:
                    raise ValueError("unproven capability cannot carry proof digest")
                issues.add("CAPABILITY_NOT_CLAIMED")
            summary[name] = status
            statuses_by_capability[name].append(status)
        if row["observation"] == "UNKNOWN":
            issues.add("UNKNOWN_RETAINED")
        if row["observation"] == "DISSENT":
            issues.add("DISSENT_RETAINED")
        outcomes.append({"worker_id": row["worker_id"], "source_id": origin,
                         "custodian_id": row["custodian_id"],
                         "observation": row["observation"],
                         "observation_limits": list(limits), "claims": summary})
    if len({x["custodian_id"] for x in outcomes}) != 3:
        issues.add("SHARED_CUSTODIAN")
    if "CORRELATED_EVIDENCE_OR_CUSTODY_ORIGINS" in base["reasons"]:
        issues.add("EXISTING_EVIDENCE_CORRELATION")
    # Distinct IDs or caller-supplied evidence digests cannot establish a
    # third party actually observed, signed, or retained any packet.
    compat = {
        k: ("LOCALLY_CLAIMED" if all(v == "CLAIMED" for v in values)
            else "UNRESOLVED")
        for k, values in statuses_by_capability.items()
    }
    return {
        "schema": "stegverse.sdk.stage1-capability-local-review.v1",
        "manifest_sha256": base["manifest_sha256"],
        "group_result_binding_sha256": base["group_result_binding_sha256"],
        "descriptor_sha256": _hash(d),
        "participants": outcomes,
        "capability_compatibility": compat,
        "limitations": sorted(issues),
        "fixture_status": ("LOCAL_FIXTURE_CONSISTENT" if not issues
                           else "LOCAL_FIXTURE_INCOMPLETE"),
        "decision": "NON_AUTHORIZING_LOCAL_REVIEW_ONLY",
        "external_participation_proven": False,
        "independent_origin_proven": False,
        "authentic_governance_proven": False,
        "master_records_custody_proven": False,
        "authority_effect": "NONE",
    }
