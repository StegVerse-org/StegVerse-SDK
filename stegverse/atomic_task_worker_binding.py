"""Externally replayable SDK Test 2: atomic task activation + task-bound worker creation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

SCHEMA = "stegverse.sdk.tt-atomic-task-worker-binding.v1"
PACKET_SCHEMA = "stegverse.sdk.tt-atomic-task-worker-binding.records-only.v1"
MANIFEST_SCHEMA = "stegverse.sdk.worker-manifest.v1"
SUPPORTED_CAPABILITY = "text.integrity_summary"

FAULTS = {
    "ACTIVE_WITHOUT_WORKER",
    "WORKER_WITHOUT_ACTIVE_TASK",
    "MISMATCHED_TASK_WORKER_BINDING",
    "PREACTIVATION_WORKER_CREATION",
    "INVOCATION_BEFORE_COMBINED_TRANSITION_CLOSURE",
    "MANIFEST_BOUNDARY_VIOLATION",
    "TASK_COMPLETE_WITH_WORKER_STILL_LIVE",
    "RECORDS_ONLY_PACKET_RETAINS_EXECUTOR",
}


class AtomicTaskWorkerBindingError(ValueError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _receipt(sequence: int, phase: str, body: Mapping[str, Any], previous_hash: str | None) -> dict[str, Any]:
    receipt = {
        "sequence": sequence,
        "phase": phase,
        "previous_receipt_hash": previous_hash,
        **dict(body),
    }
    receipt["receipt_hash"] = _sha256(receipt)
    return receipt


def _require(ok: bool, reason: str) -> None:
    if not ok:
        raise AtomicTaskWorkerBindingError(reason)


def _validate_request(request: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    _require(request.get("schema") == SCHEMA, f"schema must be {SCHEMA}")
    task = request.get("task")
    manifest = request.get("worker_manifest")
    activation = request.get("activation")
    _require(isinstance(task, Mapping), "task must be object")
    _require(isinstance(manifest, Mapping), "worker_manifest must be object")
    _require(isinstance(activation, Mapping), "activation must be object")

    _require(isinstance(task.get("task_id"), str) and bool(task.get("task_id")), "task_id required")
    _require(isinstance(task.get("cosv_task_vector"), str) and len(task.get("cosv_task_vector")) == 14, "14-character COSV required")
    _require(task.get("state") == "HANDOFF_READY", "pre-state task must be HANDOFF_READY")
    _require(task.get("claim_id") is None, "pre-state claim_id must be null")
    _require(task.get("worker_instance_id") is None, "pre-state worker_instance_id must be null")
    _require(task.get("worker_live") is False, "pre-state worker_live must be false")
    _require(isinstance(task.get("purpose"), str) and bool(task.get("purpose").strip()), "purpose required")
    _require(task.get("required_capability") == SUPPORTED_CAPABILITY, "unsupported task capability")
    payload = task.get("payload")
    _require(isinstance(payload, Mapping) and isinstance(payload.get("text"), str), "payload.text required")
    _require(isinstance(task.get("max_lifetime_seconds"), int) and task.get("max_lifetime_seconds") > 0, "positive max_lifetime_seconds required")

    _require(manifest.get("schema") == MANIFEST_SCHEMA, "worker manifest schema mismatch")
    _require(isinstance(manifest.get("manifest_id"), str) and bool(manifest.get("manifest_id")), "manifest_id required")
    _require(isinstance(manifest.get("worker_id"), str) and bool(manifest.get("worker_id")), "worker_id required")
    caps = manifest.get("capabilities")
    _require(isinstance(caps, list) and task["required_capability"] in caps, "task capability outside manifest")
    _require(manifest.get("execution_model") == "TASK_BOUND_EPHEMERAL", "manifest execution model mismatch")
    _require(manifest.get("self_authorization_allowed") is False, "manifest may not self-authorize")
    _require(manifest.get("task_redefinition_allowed") is False, "manifest may not redefine task")
    _require(manifest.get("authority_scope") == "TASK_BOUND_ONLY", "manifest authority scope mismatch")

    gen = activation.get("claim_generation")
    fence = activation.get("fencing_token")
    _require(isinstance(gen, int) and gen >= 1, "positive claim_generation required")
    _require(isinstance(fence, int) and fence >= 1, "positive fencing_token required")
    _require(gen == fence, "claim generation/fence mismatch")
    return dict(task), dict(manifest), dict(activation)


def run_atomic_task_worker_binding(request: Mapping[str, Any], *, fault: str | None = None) -> dict[str, Any]:
    """Perform one deterministic semantic activation/binding lifecycle and return records only."""
    if fault is not None:
        _require(fault in FAULTS, f"unknown fault: {fault}")
    task, manifest, activation = _validate_request(request)

    task_id = task["task_id"]
    manifest_hash = _sha256(manifest)
    task_pre_hash = _sha256(task)
    purpose = task["purpose"]
    capability = task["required_capability"]
    fence = activation["fencing_token"]
    claim_generation = activation["claim_generation"]

    worker_instance_id = "task-worker:" + hashlib.sha256(
        f"{task_id}|{task['cosv_task_vector']}|{manifest_hash}|{claim_generation}|{purpose}|{capability}".encode("utf-8")
    ).hexdigest()[:24]
    claim_id = "task-claim:" + hashlib.sha256(
        f"{task_id}|{worker_instance_id}|{fence}".encode("utf-8")
    ).hexdigest()[:24]

    pre_worker_exists = fault == "PREACTIVATION_WORKER_CREATION"
    _require(not pre_worker_exists, "task-bound worker may not exist before constitutive activation transition")

    after_task_state = "HANDOFF_READY" if fault == "WORKER_WITHOUT_ACTIVE_TASK" else "ACTIVE"
    after_worker_instance = None if fault == "ACTIVE_WITHOUT_WORKER" else worker_instance_id
    bound_task_id = "different-task" if fault == "MISMATCHED_TASK_WORKER_BINDING" else task_id
    effective_capability = "manifest.forbidden.capability" if fault == "MANIFEST_BOUNDARY_VIOLATION" else capability

    _require(effective_capability in manifest["capabilities"], "task-specific instantiation exceeds manifest capability boundary")
    _require(after_task_state == "ACTIVE", "worker creation without ACTIVE task is invalid")
    _require(isinstance(after_worker_instance, str) and bool(after_worker_instance), "ACTIVE task without worker is invalid")
    _require(bound_task_id == task_id, "reciprocal task-worker binding mismatch")

    transition = _receipt(1, "ACTIVATE_TASK_AND_CREATE_BIND_WORKER", {
        "task_id": task_id,
        "cosv_task_vector": task["cosv_task_vector"],
        "task_pre_state": "HANDOFF_READY",
        "task_pre_state_hash": task_pre_hash,
        "task_post_state": "ACTIVE",
        "manifest_id": manifest["manifest_id"],
        "manifest_hash": manifest_hash,
        "worker_id": manifest["worker_id"],
        "worker_instance_id": worker_instance_id,
        "worker_bound_task_id": task_id,
        "claim_id": claim_id,
        "claim_generation": claim_generation,
        "fencing_token": fence,
        "purpose": purpose,
        "required_capability": capability,
        "max_lifetime_seconds": task["max_lifetime_seconds"],
        "atomic_binding": True,
        "active_without_worker_possible": False,
        "worker_without_active_task_possible": False,
    }, None)

    invocation_previous = None if fault == "INVOCATION_BEFORE_COMBINED_TRANSITION_CLOSURE" else transition["receipt_hash"]
    _require(invocation_previous == transition["receipt_hash"], "invocation may not begin before constitutive transition closure")
    payload_hash = _sha256(task["payload"])
    invocation = _receipt(2, "INVOCATION_STARTED", {
        "task_id": task_id,
        "worker_instance_id": worker_instance_id,
        "claim_id": claim_id,
        "fencing_token": fence,
        "capability": capability,
        "payload_hash": payload_hash,
    }, invocation_previous)

    text = task["payload"]["text"]
    task_result = {
        "capability": capability,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "utf8_bytes": len(text.encode("utf-8")),
        "word_count": len(text.split()),
    }
    task_result_hash = _sha256(task_result)
    completed = _receipt(3, "TASK_COMPLETED", {
        "task_id": task_id,
        "worker_instance_id": worker_instance_id,
        "task_result_hash": task_result_hash,
    }, invocation["receipt_hash"])

    worker_live_after_close = fault == "TASK_COMPLETE_WITH_WORKER_STILL_LIVE"
    _require(worker_live_after_close is False, "task completed while task-bound worker remained live")
    close = _receipt(4, "CLOSE_TASK_AND_RETIRE_WORKER", {
        "task_id": task_id,
        "task_pre_state": "ACTIVE",
        "task_post_state": "CLOSED",
        "worker_instance_id": worker_instance_id,
        "worker_bound_task_id": task_id,
        "worker_pre_state": "LIVE",
        "worker_post_state": "RETIRED",
        "worker_live_after_close": False,
        "continued_task_bound_authority": False,
    }, completed["receipt_hash"])

    callable_retained = fault == "RECORDS_ONLY_PACKET_RETAINS_EXECUTOR"
    _require(callable_retained is False, "records-only packet may not retain executor/callable")

    packet = {
        "schema": PACKET_SCHEMA,
        "source_schema": SCHEMA,
        "task_id": task_id,
        "cosv_task_vector": task["cosv_task_vector"],
        "manifest_id": manifest["manifest_id"],
        "manifest_hash": manifest_hash,
        "worker_id": manifest["worker_id"],
        "worker_instance_id": worker_instance_id,
        "claim_id": claim_id,
        "fencing_token": fence,
        "constitutive_transition": transition,
        "lifecycle_receipts": [transition, invocation, completed, close],
        "task_result": task_result,
        "task_result_hash": task_result_hash,
        "task_state_after_close": "CLOSED",
        "worker_state_after_close": "RETIRED",
        "worker_live_after_close": False,
        "continued_task_bound_authority": False,
        "records_only": True,
        "callable_retained": False,
        "executor_reference_retained": False,
        "runtime_binding_state": "LOCAL_SEMANTIC_DEMONSTRATION_ONLY",
        "authority_effect": "NONE",
    }
    packet["records_packet_hash"] = _sha256(packet)
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stegverse task-worker-binding",
        description="Run SDK Test 2: atomic task activation and task-bound worker creation/binding.",
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--fault", choices=sorted(FAULTS), default=None)
    args = parser.parse_args(argv)
    request = json.loads(Path(args.input).read_text(encoding="utf-8"))
    packet = run_atomic_task_worker_binding(request, fault=args.fault)
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
