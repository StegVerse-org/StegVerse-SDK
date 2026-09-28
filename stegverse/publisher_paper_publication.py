"""Non-authorizing Publisher paper -> existing generic SDK manifest binding.

This is distinct from external-framework wiki publication. It validates an
exact source-byte fingerprint and the supplied review references; neither the
SDK nor this converter authenticates independent reviewers or publishes a paper.
"""
from __future__ import annotations

import hashlib
import re
from copy import deepcopy
from typing import Any, Mapping

from .governance_navigation import canonical_sha256
from .manifest_builder import build_manifest
from .manifest_contract import validate_ingress_manifest
from .security_posture_request import (
    EXTENSION_KEY as SECURITY_POSTURE_REQUEST_EXTENSION,
    validate_security_posture_request,
)

TASK_ID = "ECOSYSTEM-ECONOMIC-WHITEPAPER-GATED-ROADMAP-001"
TARGET_REPOSITORY = "GCAT-BCAT-Engine/Publisher"
PROFILE = "stegverse.publisher.paper-publication-candidate/v1"
PUBLISHER_PACKAGE_PROFILE = "stegverse.publisher.evidence-report-package/v1"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")
    return value.strip()


def validate_publisher_paper_candidate(
    value: Mapping[str, Any], *, source_bytes: bytes
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("publication_candidate_required")
    if not isinstance(source_bytes, bytes):
        raise ValueError("original_source_bytes_required")
    candidate = deepcopy(dict(value))
    expected = {
        "schema", "goal_task_id", "target_repository", "target_path",
        "source_commit_sha", "source_sha256", "source_git_blob_sha",
        "editorial_owner_approved", "review_report_sha256",
        "publication_executed", "authority_effect",
    }
    if set(candidate) != expected:
        raise ValueError("publisher_candidate_fields_mismatch")
    if candidate["schema"] != PROFILE or candidate["goal_task_id"] != TASK_ID:
        raise ValueError("publisher_candidate_profile_or_task_mismatch")
    if candidate["target_repository"] != TARGET_REPOSITORY:
        raise ValueError("publisher_papers_target_repository_mismatch")
    path = _text(candidate["target_path"], "target_path")
    if not path.startswith("papers/") or path.endswith("/") or ".." in path or "\\" in path:
        raise ValueError("publisher_papers_target_path_invalid")
    if candidate["editorial_owner_approved"] is not True:
        raise ValueError("publisher_editorial_owner_approval_missing")
    if candidate["publication_executed"] is not False or candidate["authority_effect"] != "NONE":
        raise ValueError("publisher_candidate_cannot_claim_authority_or_publication")
    commit = candidate["source_commit_sha"]
    digest = candidate["source_sha256"]
    blob = candidate["source_git_blob_sha"]
    if not all(isinstance(s, str) for s in (commit, digest, blob)):
        raise ValueError("source_identity_format_invalid")
    if not _COMMIT.fullmatch(commit) or not _DIGEST.fullmatch(digest) or not _COMMIT.fullmatch(blob):
        raise ValueError("source_identity_format_invalid")
    if hashlib.sha256(source_bytes).hexdigest() != digest:
        raise ValueError("exact_original_source_sha256_mismatch")
    header = b"blob " + str(len(source_bytes)).encode("ascii") + b"\\0"
    if hashlib.sha1(header + source_bytes).hexdigest() != blob:
        raise ValueError("exact_original_git_blob_sha_mismatch")
    reviews = candidate["review_report_sha256"]
    if not isinstance(reviews, Mapping) or set(reviews) != {"economics", "legal"}:
        raise ValueError("publisher_exact_reviewer_evidence_missing")
    if not all(isinstance(reviews[k], str) and _DIGEST.fullmatch(reviews[k]) for k in reviews):
        raise ValueError("publisher_exact_reviewer_evidence_missing")
    return candidate


def publisher_paper_governance_candidate(value: Mapping[str, Any]) -> dict[str, Any]:
    """Compute the exact requested action; not an approval or runtime outcome."""
    return {
        "actor_class": "publisher_paper_publication_candidate",
        "action": "request_governed_paper_publication",
        "target": f"{TARGET_REPOSITORY}:{value['target_path']}",
        "scope": "publisher_paper_publication",
        "parameters": {
            "goal_task_id": TASK_ID,
            "source_commit_sha": value["source_commit_sha"],
            "source_sha256": value["source_sha256"],
            "source_git_blob_sha": value["source_git_blob_sha"],
            "target_repository": TARGET_REPOSITORY,
            "target_path": value["target_path"],
            "review_report_sha256": dict(value["review_report_sha256"]),
            "publication_executed": False,
            "external_side_effect_requested": True,
        },
    }


def prepare_publisher_paper_manifest(
    *,
    candidate: Mapping[str, Any],
    source_bytes: bytes,
    governance_request: Mapping[str, Any],
    security_posture_request: Mapping[str, Any],
    created_at: str | None = None,
) -> dict[str, Any]:
    canonical = validate_publisher_paper_candidate(candidate, source_bytes=source_bytes)
    if not isinstance(governance_request, Mapping):
        raise ValueError("complete_governance_request_required")
    expected_action = publisher_paper_governance_candidate(canonical)
    if governance_request.get("candidate") != expected_action:
        raise ValueError("publisher_governance_candidate_exact_binding_mismatch")
    posture = validate_security_posture_request(security_posture_request)
    if posture["task_id"] != TASK_ID:
        raise ValueError("publisher_posture_task_binding_mismatch")
    data = {
        "candidate": canonical,
        "source_text_utf8": source_bytes.decode("utf-8"),
    }
    manifest = build_manifest(
        data=data,
        source_framework="publisher_approved_paper_source",
        source_output_id=canonical_sha256(data),
        processor_request=governance_request,
        process="governance",
        return_depth="full-trace",
        data_class=PROFILE,
        created_at=created_at,
        context_refs=[
            TASK_ID, canonical["source_commit_sha"], canonical["source_sha256"],
            canonical["source_git_blob_sha"], *canonical["review_report_sha256"].values()
        ],
        declared_intent="Evaluate exact owner-approved Publisher paper through existing governed ingress.",
        requested_consequence=(
            "Request governed publication decision for this exact paper. "
            "No repository mutation before separately observed original Interlock/InTr ALLOW "
            "and reconstructed same-transition Master Records closure."
        ),
        initiator_class="publisher_paper_publication_candidate",
        initiator_ref=TASK_ID,
        publisher_required=True,
        publisher_package_profile=PUBLISHER_PACKAGE_PROFILE,
        destination_profile=TARGET_REPOSITORY,
    )
    manifest["extensions"][SECURITY_POSTURE_REQUEST_EXTENSION] = posture
    validate_ingress_manifest(manifest)
    return manifest
