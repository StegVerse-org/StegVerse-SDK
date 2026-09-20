"""Manifest-driven SDK processor for purpose-bound worker tests.

The caller supplies only source-native data plus a processor request to Manifest
Builder.  This processor derives the canonical TT worker request from the validated
manifest and executes the existing SDK purpose-bound worker implementation.  It
does not accept a second worker request file or infer missing preregistered evidence.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .purpose_bound_worker import SCHEMA as WORKER_SCHEMA, run_purpose_bound_worker
from .route_resolution import PURPOSE_BOUND_WORKER_ROUTE_ID, route_from_manifest

PROCESSING_CAPABILITY = "purpose_bound_worker"
ROUTE_ID = PURPOSE_BOUND_WORKER_ROUTE_ID
REQUEST_SCHEMA = "stegverse.sdk.purpose-bound-worker-test.v1"
RESULT_SCHEMA = "stegverse.sdk.purpose-bound-worker-manifest-result.v1"
REQUEST_EXTENSION = "stegverse_purpose_bound_worker_request"

_COMPONENTS = (
    "expected_task_execution",
    "known_delay",
    "inferred_unknown_delay_reserve",
    "records_decomposition",
    "safety_reserve",
)


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value.strip()


def validate_purpose_bound_worker_request(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("purpose_bound_worker processor_request must be an object")
    if value.get("schema") != REQUEST_SCHEMA:
        raise ValueError(f"purpose-bound worker request schema must be {REQUEST_SCHEMA}")
    test_id = _text(value.get("test_id"), "test_id")
    purpose = _text(value.get("purpose"), "purpose")
    capability = _text(value.get("required_capability"), "required_capability")
    payload = value.get("payload")
    if not isinstance(payload, Mapping) or not isinstance(payload.get("text"), str):
        raise ValueError("payload.text must be a string")
    policy = value.get("lifetime_policy")
    if not isinstance(policy, Mapping):
        raise ValueError("lifetime_policy is required")
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
    components = {}
    for name in _COMPONENTS:
        component = budget.get(name)
        if not isinstance(component, int) or isinstance(component, bool) or component < 0:
            raise ValueError(f"{name} must be a nonnegative integer")
        components[name] = component
    derived = sum(components.values())
    if policy.get("derived_max_lifetime_seconds") != derived:
        raise ValueError("derived_max_lifetime_seconds does not equal the component sum")
    _text(policy.get("unknown_delay_inference_basis"), "unknown_delay_inference_basis")
    expected = value.get("expected_evidence_fields")
    if not isinstance(expected, list) or not expected or not all(isinstance(x, str) and x.strip() for x in expected):
        raise ValueError("expected_evidence_fields must be a non-empty array of strings")
    return {
        "schema": REQUEST_SCHEMA,
        "test_id": test_id,
        "purpose": purpose,
        "required_capability": capability,
        "payload": deepcopy(dict(payload)),
        "lifetime_policy": deepcopy(dict(policy)),
        "expected_evidence_fields": list(dict.fromkeys(x.strip() for x in expected)),
    }


def derive_worker_request(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    processing = canonical.get("processing") or {}
    if processing.get("capability") != PROCESSING_CAPABILITY:
        raise ValueError("manifest processing capability does not select purpose_bound_worker")
    route = route_from_manifest(canonical)
    if route.get("route_id") != ROUTE_ID or route.get("processor_capability") != PROCESSING_CAPABILITY:
        raise ValueError("purpose-bound worker route binding mismatch")
    if route.get("runtime_binding") != "stegverse.purpose_bound_worker_processor.execute_manifest":
        raise ValueError("purpose-bound worker runtime binding is unavailable")
    extensions = canonical.get("extensions") or {}
    request = validate_purpose_bound_worker_request(extensions.get(REQUEST_EXTENSION))
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
                "payload": deepcopy(request["payload"]),
            },
        },
    }


def execute_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    request = validate_purpose_bound_worker_request(
        (canonical.get("extensions") or {}).get(REQUEST_EXTENSION)
    )
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
        "worker_live_after_close": worker_result.get("worker_live_after_close"),
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
        "worker_live_after_close": worker_result.get("worker_live_after_close") is False,
        "authority_effect": "NONE_MANIFEST_DRIVEN_SDK_TEST",
    }


__all__ = [
    "PROCESSING_CAPABILITY", "REQUEST_EXTENSION", "REQUEST_SCHEMA", "RESULT_SCHEMA",
    "ROUTE_ID", "derive_worker_request", "execute_manifest",
    "validate_purpose_bound_worker_request",
]
