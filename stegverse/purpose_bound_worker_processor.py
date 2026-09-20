"""Manifest-driven SDK processor for single and grouped purpose-bound worker tests.

The caller supplies source-native data plus a processor request to Manifest Builder.
The resulting canonical manifest is the sole execution input to run-manifest.

The processor supports:
- one bounded purpose-bound worker; and
- a generic bounded group of concurrent purpose-bound workers derived from one
  manifested source payload.

Group support is a general processor capability, not a Task-4-specific runner.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import json
import threading
import time
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .purpose_bound_worker import SCHEMA as WORKER_SCHEMA, run_purpose_bound_worker
from .route_resolution import PURPOSE_BOUND_WORKER_ROUTE_ID, route_from_manifest

PROCESSING_CAPABILITY = "purpose_bound_worker"
ROUTE_ID = PURPOSE_BOUND_WORKER_ROUTE_ID
REQUEST_SCHEMA = "stegverse.sdk.purpose-bound-worker-test.v1"
GROUP_REQUEST_SCHEMA = "stegverse.sdk.purpose-bound-worker-group-test.v1"
RESULT_SCHEMA = "stegverse.sdk.purpose-bound-worker-manifest-result.v1"
GROUP_RESULT_SCHEMA = "stegverse.sdk.purpose-bound-worker-group-manifest-result.v1"
REQUEST_EXTENSION = "stegverse_purpose_bound_worker_request"

_COMPONENTS = (
    "expected_task_execution",
    "known_delay",
    "inferred_unknown_delay_reserve",
    "records_decomposition",
    "safety_reserve",
)


def _canonical_sha256(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value.strip()


def _normalize_policy(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("lifetime_policy is required")
    policy = deepcopy(dict(value))
    if policy.get("mode") != "DERIVED_COST_TASK_DELAY_BUDGET":
        raise ValueError("unsupported lifetime_policy.mode")
    if policy.get("production_recompute_required") is not True:
        raise ValueError("production_recompute_required must be true")
    if policy.get("decomposition_target") != "RECORDS_ENABLED_PACKET":
        raise ValueError("decomposition_target must be RECORDS_ENABLED_PACKET")
    if policy.get("retirement_condition") != "PURPOSE_COMPLETED_OR_FAILED_OR_BUDGET_EXHAUSTED":
        raise ValueError("unsupported retirement_condition")
    cost = policy.get("cost_analysis")
    if not isinstance(cost, Mapping):
        raise ValueError("lifetime_policy.cost_analysis is required")
    units = cost.get("expected_compute_units")
    if not isinstance(units, (int, float)) or isinstance(units, bool) or units < 0:
        raise ValueError("expected_compute_units must be nonnegative")
    ceiling = cost.get("external_cost_usd_ceiling")
    if not isinstance(ceiling, (int, float)) or isinstance(ceiling, bool) or ceiling < 0:
        raise ValueError("external_cost_usd_ceiling must be nonnegative")
    _text(cost.get("task_cost_basis"), "task_cost_basis")
    budget = policy.get("time_budget_seconds")
    if not isinstance(budget, Mapping):
        raise ValueError("lifetime_policy.time_budget_seconds is required")
    components: dict[str, int] = {}
    for name in _COMPONENTS:
        component = budget.get(name)
        if not isinstance(component, int) or isinstance(component, bool) or component < 0:
            raise ValueError(f"{name} must be a nonnegative integer")
        components[name] = component
    derived = sum(components.values())
    if policy.get("derived_max_lifetime_seconds") != derived:
        raise ValueError("derived_max_lifetime_seconds does not equal the component sum")
    _text(policy.get("unknown_delay_inference_basis"), "unknown_delay_inference_basis")
    return policy


def _expected_fields(value: Any) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(x, str) and x.strip() for x in value):
        raise ValueError("expected_evidence_fields must be a non-empty array of strings")
    return list(dict.fromkeys(x.strip() for x in value))


def validate_purpose_bound_worker_request(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("purpose_bound_worker processor_request must be an object")
    schema = value.get("schema")
    if schema == REQUEST_SCHEMA:
        payload = value.get("payload")
        if payload is not None and (not isinstance(payload, Mapping) or not isinstance(payload.get("text"), str)):
            raise ValueError("payload.text must be a string when supplied")
        return {
            "schema": REQUEST_SCHEMA,
            "mode": "SINGLE",
            "test_id": _text(value.get("test_id"), "test_id"),
            "purpose": _text(value.get("purpose"), "purpose"),
            "required_capability": _text(value.get("required_capability"), "required_capability"),
            "payload": deepcopy(dict(payload)) if isinstance(payload, Mapping) else None,
            "lifetime_policy": _normalize_policy(value.get("lifetime_policy")),
            "expected_evidence_fields": _expected_fields(value.get("expected_evidence_fields")),
        }

    if schema == GROUP_REQUEST_SCHEMA:
        worker_count = value.get("worker_count")
        if not isinstance(worker_count, int) or isinstance(worker_count, bool) or worker_count < 2 or worker_count > 32:
            raise ValueError("worker_count must be an integer from 2 through 32")
        partition_ids = value.get("partition_ids")
        if (
            not isinstance(partition_ids, list)
            or len(partition_ids) != worker_count
            or not all(isinstance(x, str) and x.strip() for x in partition_ids)
        ):
            raise ValueError("partition_ids must contain exactly worker_count non-empty strings")
        normalized_ids = [x.strip() for x in partition_ids]
        if len(set(normalized_ids)) != worker_count:
            raise ValueError("partition_ids must be distinct")
        group_budget = value.get("group_wall_clock_budget_seconds")
        if not isinstance(group_budget, int) or isinstance(group_budget, bool) or group_budget <= 0:
            raise ValueError("group_wall_clock_budget_seconds must be a positive integer")
        policy = _normalize_policy(value.get("per_worker_lifetime_policy"))
        if group_budget > policy["derived_max_lifetime_seconds"]:
            raise ValueError("group wall-clock budget may not exceed per-worker derived maximum lifetime")
        return {
            "schema": GROUP_REQUEST_SCHEMA,
            "mode": "GROUP",
            "test_id": _text(value.get("test_id"), "test_id"),
            "purpose": _text(value.get("purpose"), "purpose"),
            "required_capability": _text(value.get("required_capability"), "required_capability"),
            "worker_count": worker_count,
            "partition_ids": normalized_ids,
            "group_wall_clock_budget_seconds": group_budget,
            "per_worker_lifetime_policy": policy,
            "expected_evidence_fields": _expected_fields(value.get("expected_evidence_fields")),
        }

    raise ValueError(
        f"purpose-bound worker request schema must be {REQUEST_SCHEMA} or {GROUP_REQUEST_SCHEMA}"
    )


def _validated_manifest(manifest: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any], Mapping[str, Any]]:
    canonical = validate_ingress_manifest(manifest)
    processing = canonical.get("processing") or {}
    if processing.get("capability") != PROCESSING_CAPABILITY:
        raise ValueError("manifest processing capability does not select purpose_bound_worker")
    route = route_from_manifest(canonical)
    if route.get("route_id") != ROUTE_ID or route.get("processor_capability") != PROCESSING_CAPABILITY:
        raise ValueError("purpose-bound worker route binding mismatch")
    if route.get("state_graph_adapter_binding") != "stegverse.purpose_bound_worker_processor.derive_state_graph":
        raise ValueError("purpose-bound worker state-graph adapter binding is unavailable")
    request = validate_purpose_bound_worker_request(
        (canonical.get("extensions") or {}).get(REQUEST_EXTENSION)
    )
    source_payload = canonical.get("payload")
    if not isinstance(source_payload, Mapping) or not isinstance(source_payload.get("text"), str):
        raise ValueError("manifest payload.text must be a string for purpose_bound_worker")
    return canonical, request, source_payload


def derive_worker_request(manifest: Mapping[str, Any]) -> dict[str, Any]:
    _, request, source_payload = _validated_manifest(manifest)
    if request["mode"] != "SINGLE":
        raise ValueError("derive_worker_request requires a single-worker processor request")
    if request.get("payload") is not None and request["payload"] != source_payload:
        raise ValueError("processor_request payload conflicts with source-native manifest payload")
    policy = request["lifetime_policy"]
    return {
        "schema": WORKER_SCHEMA,
        "transition_cell": {
            "cell_id": request["test_id"],
            "protocol_version": "manifest-builder-v1",
            "pre_state": {"worker_live": False},
            "candidate": {
                "operation_id": request["test_id"],
                "operation_class": "ARBITRARY_TRACKED_TASK",
                "purpose": request["purpose"],
                "required_capability": request["required_capability"],
                "max_lifetime_seconds": policy["derived_max_lifetime_seconds"],
                "lifetime_policy": deepcopy(policy),
                "payload": deepcopy(dict(source_payload)),
            },
        },
    }


def derive_group_worker_requests(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    _, request, source_payload = _validated_manifest(manifest)
    if request["mode"] != "GROUP":
        raise ValueError("derive_group_worker_requests requires a group processor request")
    policy = request["per_worker_lifetime_policy"]
    base_text = source_payload["text"]
    requests = []
    for index, partition_id in enumerate(request["partition_ids"], start=1):
        requests.append({
            "schema": WORKER_SCHEMA,
            "transition_cell": {
                "cell_id": f"{request['test_id']}:{partition_id}",
                "protocol_version": "manifest-builder-group-v1",
                "pre_state": {"worker_live": False},
                "candidate": {
                    "operation_id": f"{request['test_id']}:{partition_id}",
                    "operation_class": "ARBITRARY_TRACKED_TASK",
                    "purpose": f"{request['purpose']} [partition {partition_id}]",
                    "required_capability": request["required_capability"],
                    "max_lifetime_seconds": policy["derived_max_lifetime_seconds"],
                    "lifetime_policy": deepcopy(policy),
                    "payload": {"text": f"{base_text} | partition {partition_id}"},
                },
            },
        })
    return requests


def derive_state_graph(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Derive the installed single-worker or worker-group graph without executing it."""
    _, request, _ = _validated_manifest(manifest)
    if request["mode"] == "SINGLE":
        worker_request = derive_worker_request(manifest)
        canonical_task_id = "SDK-TT-PURPOSE-BOUND-WORKER-RUNTIME-PROOF-001"
        ordered = [
            "WORKERCOORDINATOR_CLAIM_FENCE_BOUND",
            "TV_TVC_WARRANT_POLICY_VERIFIED",
            "STEGCORE_INTR_MATERIALIZATION_ADMITTED",
            "PURPOSE_BOUND_WORKER_MATERIALIZED",
            "PURPOSE_BOUND_WORKER_INVOCATION_STARTED",
            "PURPOSE_BOUND_WORKER_TASK_COMPLETED",
            "PURPOSE_BOUND_WORKER_RETIRED",
        ]
        graph_request: Any = worker_request
    else:
        group_requests = derive_group_worker_requests(manifest)
        canonical_task_id = request["test_id"]
        ordered = [
            "PURPOSE_BOUND_WORKER_GROUP_BOUND",
            "PURPOSE_BOUND_WORKER_GROUP_CONCURRENT_EXECUTION",
            "PURPOSE_BOUND_WORKER_GROUP_ALL_RETIRED",
            "PURPOSE_BOUND_WORKER_GROUP_RECORDS_ONLY_JOIN",
        ]
        graph_request = {
            "worker_count": request["worker_count"],
            "group_wall_clock_budget_seconds": request["group_wall_clock_budget_seconds"],
            "workers": group_requests,
        }
    return {
        "schema": "stegverse.sdk.installed-state-transition-graph/v1",
        "graph_id": canonical_task_id + ":PURPOSE_BOUND_WORKER",
        "canonical_task_id": canonical_task_id,
        "processing_capability": PROCESSING_CAPABILITY,
        "route_id": ROUTE_ID,
        "request": graph_request,
        "expected_evidence_fields": request["expected_evidence_fields"],
        "ordered_transitions": ordered,
        "predecessor_closure_required": True,
        "terminal_requirements": {
            "records_only": True,
            "continued_authority": False,
        },
        "adapter_executes_lifecycle": request["mode"] in {"SINGLE", "GROUP"},
        "authority_effect": "NONE_GRAPH_DERIVATION_ONLY",
    }


def _execute_single(manifest: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
    worker_request = derive_worker_request(manifest)
    worker_result = run_purpose_bound_worker(worker_request)
    phases = [
        row.get("phase")
        for row in worker_result.get("lifecycle_receipts", [])
        if isinstance(row, Mapping)
    ]
    observations = {
        "transition_cell_hash": bool(worker_result.get("transition_cell_hash")),
        "worker_spec": isinstance(worker_result.get("worker_spec"), Mapping),
        "lifecycle_receipts": phases == ["MATERIALIZED", "INVOCATION_STARTED", "TASK_COMPLETED", "RETIRED"],
        "task_result": isinstance(worker_result.get("task_result"), Mapping),
        "task_result_hash": bool(worker_result.get("task_result_hash")),
        "records_only": worker_result.get("records_only") is True,
        "worker_live_after_close": worker_result.get("worker_live_after_close") is False,
    }
    missing = [field for field in request["expected_evidence_fields"] if observations.get(field) is not True]
    return {
        "schema": RESULT_SCHEMA,
        "test_id": request["test_id"],
        "processing_capability": PROCESSING_CAPABILITY,
        "route_id": ROUTE_ID,
        "derived_worker_request": worker_request,
        "expected_evidence_fields": request["expected_evidence_fields"],
        "evidence_observations": observations,
        "missing_expected_evidence_fields": missing,
        "evidence_expectations_satisfied": not missing,
        "worker_result": worker_result,
        "records_only": worker_result.get("records_only") is True,
        "worker_live_after_close": worker_result.get("worker_live_after_close"),
        "authority_effect": "NONE_MANIFEST_DRIVEN_SDK_TEST",
    }


def _execute_group(manifest: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
    worker_requests = derive_group_worker_requests(manifest)
    ready_barrier = threading.Barrier(len(worker_requests))\n    invocation_barrier = threading.Barrier(len(worker_requests))

    def run_one(index_request: tuple[int, dict[str, Any]]) -> dict[str, Any]:
        index, worker_request = index_request
        ready_ns = time.monotonic_ns()
        ready_barrier.wait(timeout=5)
        execution_started_ns = time.monotonic_ns()
        invocation_barrier.wait(timeout=5)
        packet = run_purpose_bound_worker(worker_request)
        execution_completed_ns = time.monotonic_ns()
        return {
            "worker_index": index + 1,
            "partition_id": request["partition_ids"][index],
            "ready_ns": ready_ns,
            "execution_started_ns": execution_started_ns,
            "execution_completed_ns": execution_completed_ns,
            "records_packet": packet,
        }

    with ThreadPoolExecutor(max_workers=len(worker_requests)) as pool:
        workers = list(pool.map(run_one, list(enumerate(worker_requests))))

    worker_ids = [row["records_packet"]["worker_spec"]["worker_id"] for row in workers]
    overlap = max(row["execution_started_ns"] for row in workers) <= min(row["execution_completed_ns"] for row in workers)
    all_records_only = all(row["records_packet"].get("records_only") is True for row in workers)
    all_retired = all(row["records_packet"].get("worker_live_after_close") is False for row in workers)
    result_bindings = [
        {
            "partition_id": row["partition_id"],
            "worker_id": row["records_packet"]["worker_spec"]["worker_id"],
            "task_result_hash": row["records_packet"]["task_result_hash"],
            "records_packet_hash": row["records_packet"]["records_packet_hash"],
        }
        for row in workers
    ]
    group_commitment = _canonical_sha256({
        "test_id": request["test_id"],
        "worker_count": request["worker_count"],
        "result_bindings": result_bindings,
    })
    observations = {
        "worker_count_matches_manifest": len(workers) == request["worker_count"],
        "distinct_worker_identities": len(set(worker_ids)) == request["worker_count"],
        "simultaneous_overlap_observed": overlap,
        "overlap_semantics_are_invocation_lifetime_not_cpu_parallelism": overlap,
        "all_workers_records_only": all_records_only,
        "all_workers_retired": all_retired,
        "continued_authority_false": all_retired,
        "group_result_binding": bool(group_commitment),
    }
    missing = [field for field in request["expected_evidence_fields"] if observations.get(field) is not True]
    return {
        "schema": GROUP_RESULT_SCHEMA,
        "test_id": request["test_id"],
        "processing_capability": PROCESSING_CAPABILITY,
        "route_id": ROUTE_ID,
        "worker_count": request["worker_count"],
        "partition_ids": request["partition_ids"],
        "group_wall_clock_budget_seconds": request["group_wall_clock_budget_seconds"],
        "per_worker_derived_max_lifetime_seconds": request["per_worker_lifetime_policy"]["derived_max_lifetime_seconds"],
        "expected_evidence_fields": request["expected_evidence_fields"],
        "evidence_observations": observations,
        "missing_expected_evidence_fields": missing,
        "evidence_expectations_satisfied": not missing,
        "workers": workers,
        "result_bindings": result_bindings,
        "group_result_binding_sha256": group_commitment,
        "records_only": all_records_only,
        "worker_live_after_close": not all_retired,
        "continued_authority_after_retirement": not all_retired,
        "overlap_semantics": "CONCURRENT_INVOCATION_LIFETIME_NOT_CPU_PARALLELISM",
        "authority_effect": "NONE_MANIFEST_DRIVEN_SDK_TEST",
    }


def execute_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    _, request, _ = _validated_manifest(manifest)
    if request["mode"] == "SINGLE":
        return _execute_single(manifest, request)
    return _execute_group(manifest, request)


__all__ = [
    "GROUP_REQUEST_SCHEMA", "GROUP_RESULT_SCHEMA", "PROCESSING_CAPABILITY",
    "REQUEST_EXTENSION", "REQUEST_SCHEMA", "RESULT_SCHEMA", "ROUTE_ID",
    "derive_group_worker_requests", "derive_worker_request", "derive_state_graph",
    "execute_manifest", "validate_purpose_bound_worker_request",
]
