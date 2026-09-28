#!/usr/bin/env python3
"""Build the exact approved Private-State Economy publication manifest.

Source-only construction. This script never calls run-manifest and grants no
publication, release, Interlock/InTr, TV/TVC, or Master Records authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from stegverse.publisher_paper_publication import (
    PROFILE,
    TASK_ID,
    TARGET_REPOSITORY,
    prepare_publisher_paper_manifest,
    publisher_paper_governance_candidate,
)
from stegverse.security_posture_request import build_security_posture_request
from stegverse.manifest_state_transition_runtime import derive_execution_request

SOURCE_COMMIT = "f9a140d02e162c8284db7fe22b9093e70c25207a"
SOURCE_PATH = "papers/StegVerse_Private_State_Economy_White_Paper_v0.1.md"
SOURCE_SHA256 = "3329a0c47161eb4613c32bbc5e0a393116f395cb8fa78368ed21fed8775c3dca"
SOURCE_GIT_BLOB_SHA = "5c03d8ef1d79c65bb2338268c156d00295caa48a"
COSV = "10100000102000"
POLICY_MODE = "RESEARCH_PUBLICATION_WITH_DISCLOSED_UNVERIFIED_EXTERNAL_REVIEW"
POLICY_REF = (
    "GCAT-BCAT-Engine/Publisher:"
    "docs/ENTITY_ECONOMY_VOLUME_III_INDEPENDENT_REVIEW_PACKET.md"
    "#2026-09-28-owner-policy-disposition"
)
CREATED_AT = "2026-09-28T18:47:00Z"


def _git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw
    ).hexdigest()


def build(source_bytes: bytes) -> tuple[dict, dict]:
    if hashlib.sha256(source_bytes).hexdigest() != SOURCE_SHA256:
        raise ValueError("approved_source_sha256_mismatch")
    if _git_blob_sha(source_bytes) != SOURCE_GIT_BLOB_SHA:
        raise ValueError("approved_source_git_blob_mismatch")

    candidate = {
        "schema": PROFILE,
        "goal_task_id": TASK_ID,
        "target_repository": TARGET_REPOSITORY,
        "target_path": SOURCE_PATH,
        "source_commit_sha": SOURCE_COMMIT,
        "source_sha256": SOURCE_SHA256,
        "source_git_blob_sha": SOURCE_GIT_BLOB_SHA,
        "editorial_owner_approved": True,
        "review_policy": {
            "mode": POLICY_MODE,
            "policy_ref": POLICY_REF,
            "external_review_claimed": False,
            "owner_attested_convergence": True,
            "economics_report_sha256": None,
            "legal_report_sha256": None,
        },
        "publication_executed": False,
        "authority_effect": "NONE",
    }
    action = publisher_paper_governance_candidate(candidate)
    evidence_refs = [
        f"task:{TASK_ID}",
        f"cosv:{COSV}",
        f"publisher-source-sha256:{SOURCE_SHA256}",
        "GCAT-BCAT-Engine/Publisher#72:owner-approved-documentation",
        "GCAT-BCAT-Engine/Publisher#88:research-review-policy-disposition",
        POLICY_REF,
    ]
    governance_request = {
        "candidate": action,
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": evidence_refs,
        },
        "signal": {
            "admitted_signal_refs": evidence_refs,
            "excluded_signal_refs": [],
            "transformations": [],
            "missing_inputs": [],
            "uncertainty_state": "bounded",
            "reference_state_hash": SOURCE_SHA256,
            "expected_reference_state_hash": SOURCE_SHA256,
            "reconstruction_available": True,
            "transformation_provenance_complete": True,
        },
        "execution": {
            # Owner authorized the request, but this source build has no TV/TVC
            # attestation of the consequential actor. InTr must resolve it.
            "actor_authority_current": False,
            "policy_current": True,
            "delegation_current": False,
            "evidence_current": True,
            "affected_entity_conditions_represented": True,
            "recoverability_profile": "recoverable",
            "validity_window_open": True,
            "policy_ref": "GCAT-BCAT-Engine/Publisher#88",
            "delegation_ref": "OWNER_DIRECT_REQUEST_NO_DELEGATION",
            "evidence_refs": evidence_refs,
        },
        "capability": {"allowed": True},
        "continuity": {"required": True, "previous_receipt_verified": False},
        "approval": {"required": False},
        "permission_present": True,
        "declared_context": {
            "goal_task_id": TASK_ID,
            "cosv_task_vector": COSV,
            "owner_document_approval": True,
            "external_signed_review_claimed": False,
            "research_review_policy_mode": POLICY_MODE,
            "authority_effect": "NONE_REQUEST_CONTEXT_ONLY",
        },
    }
    posture = build_security_posture_request(
        task_id=TASK_ID,
        selection_present=False,
        organization_minimum_tier="SECURE",
        data_class=PROFILE,
        channel="publisher-papers",
    )
    manifest = prepare_publisher_paper_manifest(
        candidate=candidate,
        source_bytes=source_bytes,
        governance_request=governance_request,
        security_posture_request=posture,
        created_at=CREATED_AT,
    )
    request = derive_execution_request(manifest)
    if request["credential_authority"] != "TV/TVC":
        raise ValueError("tvc_credential_authority_not_preserved")
    if request["transition_authority"] != "INTERLOCK_INTR":
        raise ValueError("intr_transition_authority_not_preserved")
    if request["request_grants_authority"] is not False:
        raise ValueError("source_request_authority_escalation")
    return manifest, request


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--manifest-output", type=Path, required=True)
    p.add_argument("--request-output", type=Path, required=True)
    args = p.parse_args()
    raw = args.source.read_bytes()
    manifest, request = build(raw)
    args.manifest_output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    args.request_output.write_text(
        json.dumps(request, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "state": "EXACT_MANIFEST_PREPARED_SOURCE_ONLY",
        "goal_task_id": TASK_ID,
        "cosv": COSV,
        "source_sha256": SOURCE_SHA256,
        "canonical_manifest_sha256": request["canonical_manifest_sha256"],
        "request_sha256": request["request_sha256"],
        "runtime_invoked": False,
        "authority_effect": "NONE_SOURCE_ONLY",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
