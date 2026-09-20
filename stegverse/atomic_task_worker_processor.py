"""Evaluator-facing manifest processor shared by SDK Test 2 and Test 3.

Both tests use the same public SDK invocation surface:
source-native data + processor request -> Manifest Builder -> canonical manifest
-> run-manifest -> this installed processor.  Scenario labels do not grant authority
or select a hidden runner.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .atomic_task_worker_binding import SCHEMA as ATOMIC_SCHEMA, run_atomic_task_worker_binding
from .manifest_contract import validate_ingress_manifest
from .route_resolution import ATOMIC_TASK_WORKER_ROUTE_ID, route_from_manifest

PROCESSING_CAPABILITY = "atomic_task_worker"
ROUTE_ID = ATOMIC_TASK_WORKER_ROUTE_ID
REQUEST_SCHEMA = "stegverse.sdk.atomic-task-worker-test.v1"
RESULT_SCHEMA = "stegverse.sdk.atomic-task-worker-manifest-result.v1"
REQUEST_EXTENSION = "stegverse_atomic_task_worker_request"

SCENARIOS = {
    "TEST_2_ATOMIC_TASK_WORKER_BINDING",
    "TEST_3_RICHARD_SHORT_LIVED_ACTOR_SEAM",
}

DEFAULT_EXPECTED_EVIDENCE = [
    "constitutive_transition",
    "reciprocal_task_worker_binding",
    "invocation_after_transition",
    "task_result",
    "close_and_retire",
    "records_only",
    "worker_live_after_close_false",
    "continued_authority_false",
]


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    return deepcopy(dict(value))


def validate_atomic_task_worker_request(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("atomic_task_worker processor_request must be an object")
    if value.get("schema") != REQUEST_SCHEMA:
        raise ValueError(f"atomic task/worker request schema must be {REQUEST_SCHEMA}")
    test_id = value.get("test_id")
    if not isinstance(test_id, str) or not test_id.strip():
        raise ValueError("test_id is required")
    test_number = value.get("test_number")
    if test_number not in {2, 3}:
        raise ValueError("test_number must be 2 or 3")
    scenario = value.get("scenario")
    if scenario not in SCENARIOS:
        raise ValueError("unsupported scenario")
    if test_number == 2 and scenario != "TEST_2_ATOMIC_TASK_WORKER_BINDING":
        raise ValueError("Test 2 scenario mismatch")
    if test_number == 3 and scenario != "TEST_3_RICHARD_SHORT_LIVED_ACTOR_SEAM":
        raise ValueError("Test 3 scenario mismatch")
    task = _mapping(value.get("task"), "task")
    supplied_payload = task.pop("payload", None)
    if supplied_payload is not None and not isinstance(supplied_payload, Mapping):
        raise ValueError("task.payload must be an object when supplied")
    request = {
        "schema": ATOMIC_SCHEMA,
        "task": task,
        "worker_manifest": _mapping(value.get("worker_manifest"), "worker_manifest"),
        "activation": _mapping(value.get("activation"), "activation"),
    }
    expected = value.get("expected_evidence_fields", DEFAULT_EXPECTED_EVIDENCE)
    if not isinstance(expected, list) or not expected or not all(isinstance(x, str) and x.strip() for x in expected):
        raise ValueError("expected_evidence_fields must be a non-empty string array")
    prereg = value.get("preregistered_expectation")
    if not isinstance(prereg, Mapping):
        raise ValueError("preregistered_expectation is required")
    return {
        "schema": REQUEST_SCHEMA,
        "test_id": test_id.strip(),
        "test_number": test_number,
        "scenario": scenario,
        "atomic_request": request,
        "preregistered_expectation": deepcopy(dict(prereg)),
        "expected_evidence_fields": list(dict.fromkeys(x.strip() for x in expected)),
        "supplied_payload": deepcopy(dict(supplied_payload)) if isinstance(supplied_payload, Mapping) else None,
    }


def derive_atomic_request(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    processing = canonical.get("processing") or {}
    if processing.get("capability") != PROCESSING_CAPABILITY:
        raise ValueError("manifest processing capability does not select atomic_task_worker")
    route = route_from_manifest(canonical)
    if route.get("route_id") != ROUTE_ID or route.get("processor_capability") != PROCESSING_CAPABILITY:
        raise ValueError("atomic task/worker route binding mismatch")
    if route.get("runtime_binding") != "stegverse.atomic_task_worker_processor.execute_manifest":
        raise ValueError("atomic task/worker runtime binding is unavailable")
    req = validate_atomic_task_worker_request((canonical.get("extensions") or {}).get(REQUEST_EXTENSION))
    source_payload = canonical.get("payload")
    if not isinstance(source_payload, Mapping) or not isinstance(source_payload.get("text"), str):
        raise ValueError("manifest payload.text must be a string for atomic_task_worker")
    if req.get("supplied_payload") is not None and req["supplied_payload"] != source_payload:
        raise ValueError("processor_request task.payload conflicts with source-native manifest payload")
    atomic = deepcopy(req["atomic_request"])
    atomic["task"]["payload"] = deepcopy(dict(source_payload))
    return atomic


def _observations(packet: Mapping[str, Any]) -> dict[str, bool]:
    lifecycle = packet.get("lifecycle_receipts") or []
    phases = [row.get("phase") for row in lifecycle if isinstance(row, Mapping)]
    first = packet.get("constitutive_transition") or {}
    return {
        "constitutive_transition": first.get("phase") == "ACTIVATE_TASK_AND_CREATE_BIND_WORKER",
        "reciprocal_task_worker_binding": (
            first.get("task_id") == first.get("worker_bound_task_id")
            and bool(first.get("worker_instance_id"))
        ),
        "invocation_after_transition": phases[:2] == ["ACTIVATE_TASK_AND_CREATE_BIND_WORKER", "INVOCATION_STARTED"],
        "task_result": isinstance(packet.get("task_result"), Mapping) and bool(packet.get("task_result_hash")),
        "close_and_retire": phases[-1:] == ["CLOSE_TASK_AND_RETIRE_WORKER"],
        "records_only": packet.get("records_only") is True,
        "worker_live_after_close_false": packet.get("worker_live_after_close") is False,
        "continued_authority_false": packet.get("continued_task_bound_authority") is False,
    }


def execute_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    req = validate_atomic_task_worker_request((canonical.get("extensions") or {}).get(REQUEST_EXTENSION))
    packet = run_atomic_task_worker_binding(derive_atomic_request(manifest))
    observed = _observations(packet)
    missing = [name for name in req["expected_evidence_fields"] if observed.get(name) is not True]
    return {
        "schema": RESULT_SCHEMA,
        "test_id": req["test_id"],
        "test_number": req["test_number"],
        "scenario": req["scenario"],
        "processing_capability": PROCESSING_CAPABILITY,
        "route_id": ROUTE_ID,
        "preregistered_expectation": req["preregistered_expectation"],
        "expected_evidence_fields": req["expected_evidence_fields"],
        "evidence_observations": observed,
        "missing_expected_evidence_fields": missing,
        "evidence_expectations_satisfied": not missing,
        "records_packet": packet,
        "records_only": packet.get("records_only") is True,
        "worker_live_after_close": packet.get("worker_live_after_close"),
        "authority_effect": "NONE_EVALUATOR_MANIFEST_DRIVEN_SDK_TEST",
    }


__all__ = [
    "PROCESSING_CAPABILITY", "REQUEST_EXTENSION", "REQUEST_SCHEMA", "RESULT_SCHEMA",
    "ROUTE_ID", "derive_atomic_request", "execute_manifest",
    "validate_atomic_task_worker_request",
]
