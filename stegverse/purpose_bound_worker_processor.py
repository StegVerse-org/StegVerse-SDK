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
from .purpose_bound_worker import SCHEMA as WORKER_SCHEMA
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
    if payload is not None and (not isinstance(payload, Mapping) or not isinstance(payload.get("text"), str)):
        raise ValueError("payload.text must be a string when supplied")
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
        "payload": deepcopy(dict(payload)) if isinstance(payload, Mapping) else None,
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
    if route.get("state_graph_adapter_binding") != "stegverse.purpose_bound_worker_processor.derive_state_graph":
        raise ValueError("purpose-bound worker state-graph adapter binding is unavailable")
    extensions = canonical.get("extensions") or {}
    request = validate_purpose_bound_worker_request(extensions.get(REQUEST_EXTENSION))
    policy = request["lifetime_policy"]
    source_payload = canonical.get("payload")
    if not isinstance(source_payload, Mapping) or not isinstance(source_payload.get("text"), str):
        raise ValueError("manifest payload.text must be a string for purpose_bound_worker")
    if request.get("payload") is not None and request["payload"] != source_payload:
        raise ValueError("processor_request payload conflicts with source-native manifest payload")
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



def derive_state_graph(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Derive the installed purpose-bound state graph without executing it."""
    canonical = validate_ingress_manifest(manifest)
    request = validate_purpose_bound_worker_request(
        (canonical.get("extensions") or {}).get(REQUEST_EXTENSION)
    )
    worker_request = derive_worker_request(canonical)
    return {
        "schema": "stegverse.sdk.installed-state-transition-graph/v1",
        "graph_id": "SDK-TT-PURPOSE-BOUND-WORKER-RUNTIME-PROOF-001:PURPOSE_BOUND_WORKER",
        "canonical_task_id": "SDK-TT-PURPOSE-BOUND-WORKER-RUNTIME-PROOF-001",
        "processing_capability": PROCESSING_CAPABILITY,
        "route_id": ROUTE_ID,
        "request": worker_request,
        "expected_evidence_fields": request["expected_evidence_fields"],
        "ordered_transitions": [
            "WORKERCOORDINATOR_CLAIM_FENCE_BOUND",
            "TV_TVC_WARRANT_POLICY_VERIFIED",
            "STEGCORE_INTR_MATERIALIZATION_ADMITTED",
            "PURPOSE_BOUND_WORKER_MATERIALIZED",
            "PURPOSE_BOUND_WORKER_INVOCATION_STARTED",
            "PURPOSE_BOUND_WORKER_TASK_COMPLETED",
            "PURPOSE_BOUND_WORKER_RETIRED",
        ],
        "requires_workercoordinator_claim_fence": True,
        "predecessor_closure_required": True,
        "terminal_requirements": {
            "records_only": True,
            "continued_authority": False,
            "master_records_state": "RECORDED",
            "reconstruction_status": "PASS",
            "required_evidence_validation_status": "PASS",
            "exact_receipt_reconstruction_digest_equality": True,
        },
        "authority": {
            "claim_fence": "WORKERCOORDINATOR",
            "credential_warrant": "TV/TVC",
            "transition": "INTERLOCK_INTR",
            "execution": "STEGAGENTS_DOMAIN_COMPONENT",
            "custody_replay_reconstruction": "MASTER_RECORDS",
        },
        "adapter_executes_lifecycle": False,
        "authority_effect": "NONE_GRAPH_DERIVATION_ONLY",
    }


def execute_manifest(_manifest: Mapping[str, Any]) -> dict[str, Any]:
    raise ValueError(
        "PROCESSOR_ADAPTER_ONLY: purpose_bound_worker_processor cannot execute lifecycle; "
        "use the universal manifest state-transition runtime"
    )


__all__ = [
    "PROCESSING_CAPABILITY", "REQUEST_EXTENSION", "REQUEST_SCHEMA", "RESULT_SCHEMA",
    "ROUTE_ID", "derive_worker_request", "derive_state_graph", "execute_manifest",
    "validate_purpose_bound_worker_request",
]
