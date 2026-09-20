"""Canonical WorkerCoordinator bridge for manifested StegAgents SDK processing.

This module does not mint claims, fences, credentials, transition decisions, or
custody. It carries one already-validated SDK manifest into the existing
WorkerCoordinator/StegAgents runtime and assembles the retained evidence back
into the SDK result.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest

SDK_MANIFEST_ENV = "STEGVERSE_SDK_INGRESS_MANIFEST_PATH"
ROOT_ENV = "STEGVERSE_HEARTBEAT_ROOT"
PURPOSE_TASK = "SDK-TT-PURPOSE-BOUND-WORKER-RUNTIME-PROOF-001"
ATOMIC_TASK = "SDK-TT-RICHARD-SEAM-AUTHENTIC-RUNTIME-001"


def _require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def _root() -> Path:
    raw = str(os.getenv(ROOT_ENV) or "").strip()
    _require(bool(raw), f"{ROOT_ENV} required for governed worker processing")
    root = Path(raw).expanduser().resolve()
    _require(root.is_dir(), "governed worker runtime root not materialized")
    _require((root / "scripts" / "run_worker_runtime.py").is_file(), "existing WorkerCoordinator entrypoint unavailable")
    return root


def _last_json(stdout: str) -> dict[str, Any] | None:
    for line in reversed([line.strip() for line in stdout.splitlines() if line.strip()]):
        try:
            value = json.loads(line)
        except Exception:
            continue
        if isinstance(value, dict):
            return value
    return None


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"expected object:{path}")
    return value


def _assignment(root: Path, task_id: str) -> dict[str, Any]:
    path = root / "events" / "master-records-worker-assignment.jsonl"
    _require(path.is_file(), "WorkerCoordinator assignment evidence missing")
    matches: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except Exception:
            continue
        if isinstance(row, dict) and row.get("task_id") == task_id:
            matches.append(row)
    _require(bool(matches), "WorkerCoordinator assignment evidence not retained for task")
    row = matches[-1]
    closure = row.get("canonical_master_records_transition")
    _require(isinstance(closure, Mapping), "WorkerCoordinator claim/fence Master Records closure missing")
    _require(closure.get("state") == "RECORDED", "WorkerCoordinator claim/fence not RECORDED")
    _require(closure.get("reconstruction_status") == "PASS", "WorkerCoordinator claim/fence reconstruction not PASS")
    _require(closure.get("required_evidence_validation_status") == "PASS", "WorkerCoordinator claim/fence required evidence not PASS")
    digest = closure.get("receipt_sha256")
    _require(isinstance(digest, str) and digest == closure.get("reconstructed_receipt_sha256"), "WorkerCoordinator claim/fence digest mismatch")
    return row


def _replay_projection(result: Mapping[str, Any], *, key: str = "master_records_replay") -> dict[str, Any]:
    replay = result.get(key)
    _require(isinstance(replay, Mapping), "event replay evidence missing")
    _require(replay.get("deterministic_disposition_match") is True, "event replay deterministic match failed")
    _require(replay.get("consequence_reexecuted") is False, "event replay reexecuted consequence")
    _require(replay.get("operation_transition_custody_status") == "RECORDED", "event replay custody not RECORDED")
    return dict(replay)


def _reconstruction_projection(result: Mapping[str, Any], *, key: str = "master_records_reconstruction") -> dict[str, Any]:
    reconstruction = result.get(key)
    _require(isinstance(reconstruction, Mapping), "event reconstruction evidence missing")
    _require(reconstruction.get("operation_transition_custody_status") == "RECORDED", "event reconstruction custody not RECORDED")
    return dict(reconstruction)


def _run_cycle(root: Path, task_id: str, manifest_path: Path) -> dict[str, Any]:
    env = dict(os.environ)
    env[SDK_MANIFEST_ENV] = str(manifest_path)
    env["STEGVERSE_HEARTBEAT_ROOT"] = str(root)
    completed = subprocess.run(
        [sys.executable, str(root / "scripts" / "run_worker_runtime.py"), "--root", str(root), "--task-id", task_id],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=1800,
        env=env,
    )
    observed = _last_json(completed.stdout)
    _require(completed.returncode == 0, "existing WorkerCoordinator targeted runtime returned nonzero")
    _require(isinstance(observed, Mapping), "WorkerCoordinator targeted runtime result missing")
    return {"returncode": completed.returncode, "result": dict(observed)}


def execute_worker_manifest(manifest: Mapping[str, Any], *, capability: str) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    processing = canonical.get("processing") or {}
    _require(processing.get("capability") == capability, "worker runtime processing capability mismatch")
    root = _root()
    manifest_hash = canonical.get("canonical_manifest_sha256")
    _require(isinstance(manifest_hash, str) and manifest_hash, "canonical manifest hash missing")
    ingress_dir = root / "runtime" / "sdk-manifest-ingress"
    ingress_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = ingress_dir / f"{manifest_hash}.json"
    encoded = json.dumps(canonical, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if manifest_path.exists():
        _require(manifest_path.read_text(encoding="utf-8") == encoded, "manifest ingress write-once collision")
    else:
        manifest_path.write_text(encoded, encoding="utf-8")

    if capability == "purpose_bound_worker":
        task_id = PURPOSE_TASK
        cycles = [_run_cycle(root, task_id, manifest_path)]
        receipt_path = root / "receipts" / "sovereign-host" / "sdk-tt-purpose-bound-worker-runtime-proof.latest.json"
        _require(receipt_path.is_file(), "purpose-bound runtime receipt missing")
        receipt = _load(receipt_path)
        _require(receipt.get("state") == "AUTHENTIC_PURPOSE_BOUND_WORKER_LIFECYCLE_OBSERVED", "purpose-bound runtime did not complete")
        result = receipt.get("result")
        _require(isinstance(result, Mapping), "purpose-bound governed result missing")
        replay = _replay_projection(result)
        reconstruction = _reconstruction_projection(result)
        assignment = _assignment(root, task_id)
        return {
            "schema": "stegverse.sdk.manifested-worker-runtime-result/v1",
            "processing_capability": capability,
            "route_id": processing.get("route_id"),
            "canonical_manifest_sha256": manifest_hash,
            "workercoordinator_task_id": task_id,
            "workercoordinator_cycles": cycles,
            "workercoordinator_assignment": assignment,
            "runtime_receipt": receipt,
            "governed_result": dict(result),
            "replay": replay,
            "reconstruction": reconstruction,
            "state": "COMPLETE",
            "records_only": result.get("records_only") is True,
            "worker_live_after_close": result.get("worker_live_after_close"),
            "authority_effect": "NONE_SDK_RETURN_ASSEMBLY_ONLY",
        }

    _require(capability == "atomic_task_worker", "unsupported worker runtime capability")
    task_id = ATOMIC_TASK
    cycles = [_run_cycle(root, task_id, manifest_path), _run_cycle(root, task_id, manifest_path)]
    assignment = _assignment(root, task_id)
    activation_path = root / "receipts" / "sovereign-host" / "sdk-tt-richard-seam-authentic-runtime" / "activation.latest.json"
    execution_path = root / "receipts" / "sovereign-host" / "sdk-tt-richard-seam-authentic-runtime" / "execution.latest.json"
    close_path = root / "receipts" / "sovereign-host" / "sdk-tt-richard-seam-authentic-runtime" / "close.latest.json"
    for path in (activation_path, execution_path, close_path):
        _require(path.is_file(), f"atomic task/worker runtime receipt missing:{path.name}")
    activation = _load(activation_path)
    execution = _load(execution_path)
    close = _load(close_path)
    _require(activation.get("state") == "AUTHENTIC_ATOMIC_TASK_WORKER_ACTIVATION_ADMITTED", "atomic activation incomplete")
    _require(execution.get("state") == "AUTHENTIC_TASK_RESULT_READY_FOR_GOVERNED_CLOSE", "atomic task execution incomplete")
    _require(close.get("state") == "AUTHENTIC_TASK_CLOSED_WORKER_RETIRED_RECORDS_ONLY", "atomic close incomplete")
    activation_result = activation.get("result")
    close_result = close.get("result")
    _require(isinstance(activation_result, Mapping) and isinstance(close_result, Mapping), "atomic governed result missing")
    activation_replay = _replay_projection(activation_result)
    activation_reconstruction = _reconstruction_projection(activation_result)
    close_replay = _replay_projection(close_result, key="records_only_replay")
    close_reconstruction = _reconstruction_projection(close_result, key="records_only_reconstruction")
    _require(close_result.get("records_only") is True, "atomic close is not records-only")
    _require(close_result.get("worker_live_after_close") is False, "atomic worker remained live")
    _require(close_result.get("continued_authority_after_retirement") is False, "atomic worker retained authority")
    return {
        "schema": "stegverse.sdk.manifested-worker-runtime-result/v1",
        "processing_capability": capability,
        "route_id": processing.get("route_id"),
        "canonical_manifest_sha256": manifest_hash,
        "workercoordinator_task_id": task_id,
        "workercoordinator_cycles": cycles,
        "workercoordinator_assignment": assignment,
        "activation_receipt": activation,
        "execution_receipt": execution,
        "close_receipt": close,
        "activation_replay": activation_replay,
        "activation_reconstruction": activation_reconstruction,
        "close_replay": close_replay,
        "close_reconstruction": close_reconstruction,
        "state": "COMPLETE",
        "records_only": True,
        "worker_live_after_close": False,
        "continued_authority_after_retirement": False,
        "authority_effect": "NONE_SDK_RETURN_ASSEMBLY_ONLY",
    }
