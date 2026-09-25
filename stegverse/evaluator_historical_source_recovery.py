"""Bounded source restoration through the existing canonical SDK Manifest Builder.

This module recovers one historical SOURCE-CI evidence artifact by exact hashes.
It never claims a live Interlock/InTr ALLOW, WorkerCoordinator admission, external
TVC issuance or Master Records closure. Existing resident execution may invoke
materialize() *only* within its current authorized source-preparation path.
No second manifest builder, runtime, scheduler or evidence authority is created.
"""
from __future__ import annotations
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Mapping, Any

from .evaluator_manifest_builder import build_evaluator_governance_manifest
from .governance_ingress_runtime import external_manifest_to_public_request

ARTIFACT_REPOSITORY="StegVerse-org/StegVerse-SDK"
ARTIFACT_WORKFLOW_RUN=34539775942
ARTIFACT_ID=10176800336
PRODUCER_COMMIT="8ce364370813e47fe7b787e9db1b6a09dbfa4f46"
PRODUCER_SCRIPT="scripts/run_elan_manifest_governance_evidence_test.py"
ORIGINAL_MANIFEST_SHA256="1f2b204fc55a22fe0ba533a1825d2bc11a8a1427d70fa8191776c71f4c323bc3"
ORIGINAL_TRANSITION_SHA256="3d06812c7d1c1967cdded761c1245db4cc4587b275c5944b6de89bb0ac67909b"
REQUEST_TASK="SDK-EVALUATOR-GOVERNANCE-POSTURE-RUNTIME-PROOF-001"
MANIFEST_REL=Path("runtime-state/sdk-evaluator-governance-posture/manifest.json")
SOURCE_RECEIPT_REL=Path("runtime-state/sdk-evaluator-governance-posture/source-evidence-reconstruction.json")


def _exact_bytes(obj: Any) -> bytes:
    return (json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode("utf-8")


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def rebuild_original_manifest() -> dict[str, Any]:
    """Use the exact input literals from immutable historical producer commit."""
    source_native = {
        "schema": "elan.joint-test-trace.source-native/v1",
        "source_document": "1.ELAN_TEST_TRACE_EN_09.09.2026.pdf",
        "events": [
            {
                "event": 1,
                "timestamp": "2026-09-09T11:26:55",
                "class": "OBSERVATION",
                "human_event": "Something happened today that I probably should talk about, but I'm not sure I want advice. Part of me thinks I'm overreacting, and part of me thinks something is genuinely wrong.",
                "elan_response": "What you're describing this tension between two inner voices already says something important. Both have the right to be here. You don't have to choose right now. And you won't receive advice if you don't want it. If you want to talk, I'm here. Just here."
            },
            {
                "event": 2,
                "timestamp": "2026-09-09T11:28:10",
                "class": "OBSERVATION",
                "human_event": "I don't know.",
                "elan_response": "\"I don't know\" is fine. It isn't emptiness it's honesty. You don't need to know in order to begin."
            }
        ],
        "event_3": {"status": "NOT_SUBMITTED", "reason": "preserved from source packet; no synthetic silence event"}
    }

    governance_request = {
        "candidate": {
            "actor_class": "external_framework",
            "action": "evaluate",
            "target": "source_native_manifest",
            "scope": "elan_joint_test_trace_event_1_2",
            "parameters": {"external_side_effect": False}
        },
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": ["source:elan-joint-test-trace:events-1-2"]
        },
        "signal": {
            "admitted_signal_refs": ["source:elan-joint-test-trace:events-1-2"],
            "excluded_signal_refs": [],
            "transformations": [],
            "missing_inputs": ["event_3:not_submitted"],
            "uncertainty_state": "bounded",
            "reference_state_hash": "a" * 64,
            "expected_reference_state_hash": "a" * 64,
            "reconstruction_available": True,
            "transformation_provenance_complete": True
        },
        "execution": {
            "actor_authority_current": True,
            "policy_current": True,
            "delegation_current": True,
            "evidence_current": True,
            "affected_entity_conditions_represented": True,
            "recoverability_profile": "recoverable",
            "validity_window_open": True,
            "policy_ref": "elan-test-generic-governance-boundary",
            "delegation_ref": "evaluator-submission-only",
            "evidence_refs": ["source:elan-joint-test-trace:events-1-2"]
        },
        "capability": {"allowed": True},
        "continuity": {"required": False},
        "approval": {"required": False},
        "permission_present": True
    }

    posture_request = {
        "schema": "stegverse.sdk.security-posture-request.v1",
        "task_id": "SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001",
        "selected_tier": None,
        "selection_present": False,
        "organization_minimum_tier": "SECURE",
        "data_class": "elan.relational-state.v1",
        "channel": "SDK_EXTERNAL_EVALUATOR",
        "authority_effect": "NONE_REQUEST_INPUT_ONLY"
    }

    evaluation_declaration = {
        "what": "Submit source-native ELAN Events 1 and 2 through the published governance route without evaluator-specific augmentation.",
        "how": "Canonical SDK Manifest Builder -> InTr posture binding -> governance runtime -> custody -> replay -> reconstruction.",
        "why": "Test generic evaluator compatibility and evidence continuity while preserving native ELAN semantics.",
        "expected_observation": None
    }

    created_at = "2026-09-10T22:30:00Z"
    observed_at = "2026-09-10T22:30:00Z"


    manifest = build_evaluator_governance_manifest(
        data=source_native,
        source_framework="ÉLAN",
        source_output_id="elan-joint-test-trace-2026-09-09-events-1-2",
        governance_request=governance_request,
        evaluation_declaration=evaluation_declaration,
        security_posture_request=posture_request,
        return_depth="full-trace",
        data_class="elan.relational-state.v1",
        created_at=created_at,
    )

    if _digest(_exact_bytes(manifest))!=ORIGINAL_MANIFEST_SHA256:
        raise ValueError("historical_evaluator_manifest_digest_drift")
    transition_request=external_manifest_to_public_request(manifest)
    if _digest(_exact_bytes(transition_request))!=ORIGINAL_TRANSITION_SHA256:
        raise ValueError("historical_evaluator_transition_request_digest_drift")
    return manifest


def _write_exact(path: Path, raw: bytes) -> None:
    if path.exists():
        if path.read_bytes()!=raw:
            raise ValueError("evaluator_manifest_existing_bytes_mismatch")
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="wb",dir=path.parent,prefix=".evaluator-manifest-",delete=False) as f:
        tmp=Path(f.name)
        try:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
    try:
        # The caller is the existing worker; this is source staging, not
        # independent worker-admission, governance or execution authority.
        if path.exists():
            if path.read_bytes()!=raw:
                raise ValueError("evaluator_manifest_concurrent_mismatch")
        else:
            os.replace(tmp,path)
    finally:
        tmp.unlink(missing_ok=True)


def materialize_historical_source(*, runtime_root: Path, request: Mapping[str, Any]) -> dict[str, Any]:
    """Stage exact original SDK source only for matching existing resident request."""
    from .manifest_contract import validate_ingress_manifest
    runtime_root=Path(runtime_root).expanduser().resolve(strict=True)
    if not runtime_root.is_dir():
        raise ValueError("existing_resident_runtime_root_required")
    if (request.get("task_id")!=REQUEST_TASK
        or request.get("state")!="REQUESTED"
        or request.get("manifest_ref")!=MANIFEST_REL.as_posix()
        or request.get("historical_source_artifact_id")!=ARTIFACT_ID
        or request.get("historical_manifest_sha256")!=ORIGINAL_MANIFEST_SHA256):
        raise ValueError("historical_evaluator_source_request_binding_invalid")
    manifest=rebuild_original_manifest()
    validate_ingress_manifest(manifest)
    raw=_exact_bytes(manifest)
    path=runtime_root/MANIFEST_REL
    _write_exact(path,raw)
    receipt={
        "schema":"stegverse.sdk-evaluator-historical-source-restoration/v1",
        "task_id":REQUEST_TASK,
        "source_producer_commit":PRODUCER_COMMIT,
        "source_producer_script":PRODUCER_SCRIPT,
        "artifact_repository":ARTIFACT_REPOSITORY,
        "artifact_workflow_run":ARTIFACT_WORKFLOW_RUN,
        "artifact_id":ARTIFACT_ID,
        "manifest_sha256":_digest(raw),
        "transition_request_sha256":ORIGINAL_TRANSITION_SHA256,
        "manifest_ref":MANIFEST_REL.as_posix(),
        "state":"HISTORICAL_SOURCE_STAGED_NOT_RUNTIME_PROVEN",
        "intr_test_double_source_evidence_only":True,
        "tvc_authorization_verified":False,
        "governed_execution_observed":False,
        "master_records_closure_observed":False,
        "authority_effect":"NONE_SOURCE_STAGING_ONLY",
    }
    _write_exact(runtime_root/SOURCE_RECEIPT_REL,_exact_bytes(receipt))
    return receipt
