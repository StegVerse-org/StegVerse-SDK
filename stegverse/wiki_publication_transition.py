"""Deterministic reviewed-wiki publication candidate -> SDK manifest binding.

This module does not authorize publication or synthesize governance evidence. It
binds an already-reviewed publication transition to the existing generic SDK
manifest contract and requires the caller to provide the complete governance
request that the canonical runtime will evaluate.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .governance_navigation import canonical_sha256
from .manifest_builder import build_manifest

TRANSITION_TYPE = "external_framework_wiki_publication_transition"
ALLOW = "ALLOW_PUBLICATION_CANDIDATE"
NON_ALLOW = {"DENY_PUBLICATION", "REVIEW_REQUIRED"}
DECISIONS = {ALLOW, *NON_ALLOW}
ACTIVE_TARGET_PROFILES = {
    "admissibility": {
        "repository": "StegVerse-Labs/admissibility-wiki",
        "path_prefix": "docs/external-frameworks/",
    },
}
RESERVED_TARGET_PROFILES = {
    "stegguardian": "StegVerse-002/stegguardian-wiki",
    "stegtalk": "StegVerse-Labs/stegtalk-wiki",
    "sdk": "StegVerse-org/StegVerse-SDK",
}
BOUNDARY = {
    "transition_is_not_repository_write": True,
    "transition_is_not_certification": True,
    "transition_creates_no_standing": True,
    "separate_repository_mutation_required": True,
}
REQUIRED_FIELDS = {
    "schema_version",
    "transition_type",
    "package_id",
    "correction_receipt_id",
    "publisher_ref",
    "target_path",
    "decision",
    "source_commit_ref",
    "evidence_references",
    "publication_executed",
    "boundary",
}
PUBLISHER_PACKAGE_PROFILE = "stegverse.publisher.wiki-publication-transition/v1"


def _required_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is required")
    return value.strip()


def validate_publication_transition(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("publication transition must be an object")
    transition = deepcopy(dict(value))
    missing = sorted(REQUIRED_FIELDS - set(transition))
    unknown = sorted(set(transition) - REQUIRED_FIELDS)
    if missing:
        raise ValueError("publication transition missing required fields: " + ", ".join(missing))
    if unknown:
        raise ValueError("publication transition contains unknown fields: " + ", ".join(unknown))
    if transition.get("schema_version") != "1.0.0":
        raise ValueError("publication transition schema_version must be 1.0.0")
    if transition.get("transition_type") != TRANSITION_TYPE:
        raise ValueError("publication transition type mismatch")
    if transition.get("publication_executed") is not False:
        raise ValueError("publication transition must preserve publication_executed=false")
    if transition.get("boundary") != BOUNDARY:
        raise ValueError("publication transition boundary mismatch")
    for field in ("package_id", "correction_receipt_id", "publisher_ref", "target_path", "source_commit_ref"):
        _required_text(transition.get(field), field)
    decision = transition.get("decision")
    if decision not in DECISIONS:
        raise ValueError("publication transition decision invalid")
    evidence = transition.get("evidence_references")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("publication transition evidence_references must be non-empty")
    if not all(isinstance(item, str) and item.strip() for item in evidence):
        raise ValueError("publication transition evidence_references invalid")
    return transition


def publication_governance_candidate(
    transition: Mapping[str, Any], *, target_profile: str = "admissibility"
) -> dict[str, Any]:
    canonical = validate_publication_transition(transition)
    profile = ACTIVE_TARGET_PROFILES.get(target_profile)
    if profile is None:
        if target_profile in RESERVED_TARGET_PROFILES:
            raise ValueError(f"target profile {target_profile!r} is reserved but not enabled")
        raise ValueError("unknown target profile")
    target_path = canonical["target_path"]
    if not target_path.startswith(profile["path_prefix"]) or ".." in target_path:
        raise ValueError("publication target path outside target profile")
    transition_sha256 = canonical_sha256(canonical)
    return {
        "actor_class": "external_framework_publication_candidate",
        "action": "publish_governed_wiki_projection",
        "target": f"{profile['repository']}:{target_path}",
        "scope": "wiki_publication",
        "parameters": {
            "publication_transition_sha256": transition_sha256,
            "package_id": canonical["package_id"],
            "correction_receipt_id": canonical["correction_receipt_id"],
            "publisher_ref": canonical["publisher_ref"],
            "source_commit_ref": canonical["source_commit_ref"],
            "target_repository": profile["repository"],
            "target_path": target_path,
            "decision": canonical["decision"],
            "evidence_references": list(canonical["evidence_references"]),
            "publication_executed": False,
            "external_side_effect": canonical["decision"] == ALLOW,
        },
    }


def prepare_wiki_publication_manifest(
    *,
    transition: Mapping[str, Any],
    governance_request: Mapping[str, Any],
    target_profile: str = "admissibility",
    created_at: str | None = None,
    return_depth: str = "full-trace",
) -> dict[str, Any]:
    """Bind a reviewed publication transition to the existing generic SDK manifest.

    Governance evidence is caller supplied and remains subject to the existing
    canonical runtime. This function only verifies that its candidate exactly
    matches the deterministic publication action derived from the transition.
    """
    canonical = validate_publication_transition(transition)
    if not isinstance(governance_request, Mapping):
        raise ValueError("complete governance_request is required")
    expected_candidate = publication_governance_candidate(
        canonical, target_profile=target_profile
    )
    supplied_candidate = governance_request.get("candidate")
    if supplied_candidate != expected_candidate:
        raise ValueError(
            "governance_request candidate does not exactly bind publication transition"
        )
    target_repository = expected_candidate["parameters"]["target_repository"]
    decision = canonical["decision"]
    context_refs = [
        canonical["package_id"],
        canonical["correction_receipt_id"],
        canonical["source_commit_ref"],
        *canonical["evidence_references"],
    ]
    requested_consequence = (
        "Evaluate the reviewed wiki publication candidate through canonical governance; "
        "repository mutation remains forbidden until exact governed Master Records closure."
        if decision == ALLOW
        else
        "Record the reviewed wiki publication disposition through canonical governance "
        "with zero repository mutation."
    )
    return build_manifest(
        data=canonical,
        source_framework="external_chat_publication_transition",
        source_output_id=canonical_sha256(canonical),
        processor_request=governance_request,
        process="governance",
        return_depth=return_depth,
        data_class="stegverse.external-framework-wiki-publication-transition.v1",
        created_at=created_at,
        context_refs=context_refs,
        declared_intent="Evaluate a reviewed external-framework wiki publication transition.",
        requested_consequence=requested_consequence,
        initiator_class="external_framework_publication_candidate",
        initiator_ref=canonical["package_id"],
        publisher_required=decision == ALLOW,
        publisher_package_profile=PUBLISHER_PACKAGE_PROFILE,
        destination_profile=target_repository,
    )


__all__ = [
    "ACTIVE_TARGET_PROFILES",
    "RESERVED_TARGET_PROFILES",
    "prepare_wiki_publication_manifest",
    "publication_governance_candidate",
    "validate_publication_transition",
]
