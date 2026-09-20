"""Universal manifest state-transition runtime client.

Every installed processing capability derives only its request/state graph locally.
The consequential lifecycle is executed by the existing StegVerse Universal InTr
runtime. This module never invokes repository-local runners, WorkerCoordinator,
Interlock/InTr, TV/TVC, StegAgents, or Master Records directly.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import urllib.error
import urllib.request
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .route_resolution import canonical_sha256, route_from_manifest

REQUEST_SCHEMA = "stegverse.sdk.manifest-state-transition-request/v1"
RESULT_SCHEMA = "stegverse.sdk.manifest-state-transition-result/v1"
UNIVERSAL_RUNTIME_BINDING = "stegverse.manifest_state_transition_runtime.execute_manifest"
INGRESS_URL_ENV = "STEGVERSE_UNIVERSAL_INTR_INGRESS_URL"
TRANSPORT_AUTHORIZATION_ENV = "STEGVERSE_INTR_TRANSPORT_AUTHORIZATION_ID"

_REQUIRED_CLOSURE = {
    "state": "RECORDED",
    "reconstruction_status": "PASS",
    "required_evidence_validation_status": "PASS",
}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _load_adapter(binding: str):
    if not isinstance(binding, str) or "." not in binding:
        raise ValueError("installed route has no state-graph adapter binding")
    module_name, function_name = binding.rsplit(".", 1)
    if not module_name.startswith("stegverse."):
        raise ValueError("state-graph adapter must resolve inside the installed StegVerse SDK")
    function = getattr(importlib.import_module(module_name), function_name, None)
    if not callable(function):
        raise ValueError(f"state-graph adapter is not callable: {binding}")
    return function


def derive_execution_request(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    route = route_from_manifest(canonical)
    if route.get("runtime_binding") != UNIVERSAL_RUNTIME_BINDING:
        raise ValueError("installed route does not use the universal manifest state-transition runtime")
    adapter_binding = route.get("state_graph_adapter_binding")
    adapter = _load_adapter(str(adapter_binding or ""))
    graph = adapter(canonical)
    if not isinstance(graph, Mapping):
        raise ValueError("state-graph adapter returned a non-object result")
    graph = dict(graph)
    if graph.get("adapter_executes_lifecycle") is not False and route.get("processor_capability") in {
        "purpose_bound_worker", "atomic_task_worker"
    }:
        raise ValueError("worker state-graph adapter may not execute its lifecycle")
    graph_id = graph.get("graph_id")
    if not isinstance(graph_id, str) or not graph_id:
        raise ValueError("state-graph adapter did not provide graph_id")
    task_id = graph.get("canonical_task_id")
    requires_worker_claim = graph.get("requires_workercoordinator_claim_fence")
    if requires_worker_claim is None:
        requires_worker_claim = bool(task_id)
    if requires_worker_claim and (not isinstance(task_id, str) or not task_id):
        raise ValueError("worker-claim state graph did not provide canonical_task_id")
    if task_id is not None and (not isinstance(task_id, str) or not task_id):
        raise ValueError("canonical_task_id must be null or a non-empty string")
    manifest_hash = canonical.get("canonical_manifest_sha256") or canonical_sha256(canonical)
    request = {
        "schema": REQUEST_SCHEMA,
        "canonical_manifest": dict(canonical),
        "canonical_manifest_sha256": manifest_hash,
        "processing_capability": route["processor_capability"],
        "route_id": route["route_id"],
        "route_declaration_hash": route["route_declaration_hash"],
        "state_graph": graph,
        "graph_id": graph_id,
        "canonical_task_id": task_id,
        "requires_workercoordinator_claim_fence": bool(requires_worker_claim),
        "predecessor_closure_required": True,
        "credential_authority": "TV/TVC",
        "claim_fence_authority": "WORKERCOORDINATOR",
        "transition_authority": "INTERLOCK_INTR",
        "custody_replay_reconstruction_authority": "MASTER_RECORDS",
        "request_grants_authority": False,
        "sdk_executes_lifecycle": False,
        "authority_effect": "NONE_MANIFEST_RUNTIME_REQUEST_ONLY",
    }
    request["request_sha256"] = _sha256(request)
    return request


def _post_existing_intr(request_body: Mapping[str, Any]) -> dict[str, Any]:
    ingress_url = str(os.environ.get(INGRESS_URL_ENV) or "").strip()
    if not ingress_url:
        raise ValueError("UNIVERSAL_INTR_INGRESS_NOT_CONFIGURED")
    authorization_id = str(os.environ.get(TRANSPORT_AUTHORIZATION_ENV) or "").strip()
    if not authorization_id:
        raise ValueError("TV_TVC_INTR_TRANSPORT_AUTHORIZATION_REQUIRED")
    raw = _canonical_bytes(request_body)
    req = urllib.request.Request(
        ingress_url,
        data=raw,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-StegVerse-Transport": "InTr",
            "X-StegVerse-Transport-Origin": "TVC_RELAY_EGRESS",
            "X-StegVerse-Authorization-Id": authorization_id,
            "X-StegVerse-Payload-SHA256": hashlib.sha256(raw).hexdigest(),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=1200) as response:
            body = json.loads(response.read().decode("utf-8"))
            if int(response.status) not in {200, 202}:
                raise ValueError(f"UNIVERSAL_INTR_HTTP_STATUS:{response.status}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[-2000:]
        raise ValueError(f"UNIVERSAL_INTR_HTTP_ERROR:{exc.code}:{detail}") from exc
    except urllib.error.URLError as exc:
        raise ValueError(f"UNIVERSAL_INTR_UNREACHABLE:{exc.reason}") from exc
    if not isinstance(body, Mapping):
        raise ValueError("UNIVERSAL_INTR_RESULT_OBJECT_REQUIRED")
    return dict(body)


def _validate_transition_closures(result: Mapping[str, Any], graph: Mapping[str, Any]) -> None:
    closures = result.get("transition_closures")
    ordered = graph.get("ordered_transitions")
    if not isinstance(ordered, list):
        raise ValueError("installed state graph ordered_transitions must be an array")
    if not ordered:
        ordered = result.get("resolved_ordered_transitions")
        if not isinstance(ordered, list) or not ordered or not all(isinstance(x, str) and x for x in ordered):
            raise ValueError("RUNTIME_CANONICAL_ORDERED_TRANSITIONS_REQUIRED")
    if not isinstance(closures, list) or len(closures) != len(ordered):
        raise ValueError("MASTER_RECORDS_TRANSITION_CLOSURE_COUNT_MISMATCH")
    previous_receipt = None
    for index, (expected_transition, raw) in enumerate(zip(ordered, closures)):
        if not isinstance(raw, Mapping):
            raise ValueError(f"MASTER_RECORDS_CLOSURE_OBJECT_REQUIRED:{index}")
        closure = dict(raw)
        if closure.get("transition_id") != expected_transition:
            raise ValueError(f"MASTER_RECORDS_TRANSITION_ORDER_MISMATCH:{index}")
        for key, expected in _REQUIRED_CLOSURE.items():
            if closure.get(key) != expected:
                raise ValueError(f"MASTER_RECORDS_CLOSURE_REQUIRED:{expected_transition}:{key}")
        receipt = closure.get("receipt_sha256")
        reconstructed = closure.get("reconstructed_receipt_sha256")
        if not isinstance(receipt, str) or not receipt or receipt != reconstructed:
            raise ValueError(f"MASTER_RECORDS_RECEIPT_RECONSTRUCTION_MISMATCH:{expected_transition}")
        if index:
            if closure.get("predecessor_receipt_sha256") != previous_receipt:
                raise ValueError(f"MASTER_RECORDS_IMMEDIATE_PREDECESSOR_MISMATCH:{expected_transition}")
        previous_receipt = receipt


def validate_runtime_result(result: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
    if result.get("schema") != RESULT_SCHEMA:
        raise ValueError("UNIVERSAL_INTR_RESULT_SCHEMA_MISMATCH")
    if result.get("state") != "COMPLETE":
        reason = result.get("reason") or result.get("blocker") or "runtime_not_complete"
        raise ValueError(f"UNIVERSAL_INTR_RUNTIME_NOT_COMPLETE:{reason}")
    for key in ("canonical_manifest_sha256", "graph_id", "canonical_task_id", "processing_capability", "route_id"):
        if result.get(key) != request.get(key):
            raise ValueError(f"UNIVERSAL_INTR_RESULT_BINDING_MISMATCH:{key}")
    graph = request["state_graph"]
    _validate_transition_closures(result, graph)
    if result.get("replay_status") != "PASS":
        raise ValueError("MASTER_RECORDS_REPLAY_REQUIRED")
    if result.get("reconstruction_status") != "PASS":
        raise ValueError("MASTER_RECORDS_RECONSTRUCTION_REQUIRED")
    terminal = result.get("terminal_state")
    if not isinstance(terminal, Mapping):
        raise ValueError("TERMINAL_STATE_REQUIRED")
    if terminal.get("records_only") is not True:
        raise ValueError("TERMINAL_RECORDS_ONLY_REQUIRED")
    if terminal.get("continued_authority") is not False:
        raise ValueError("TERMINAL_CONTINUED_AUTHORITY_FALSE_REQUIRED")
    receipt_id = result.get("manifest_receipt_id")
    if not isinstance(receipt_id, str) or not receipt_id:
        raise ValueError("MANIFEST_RECEIPT_ID_REQUIRED")
    return dict(result)


def execute_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    request = derive_execution_request(manifest)
    result = _post_existing_intr(request)
    return validate_runtime_result(result, request)


__all__ = [
    "INGRESS_URL_ENV",
    "REQUEST_SCHEMA",
    "RESULT_SCHEMA",
    "TRANSPORT_AUTHORIZATION_ENV",
    "UNIVERSAL_RUNTIME_BINDING",
    "derive_execution_request",
    "execute_manifest",
    "validate_runtime_result",
]
