from __future__ import annotations

from typing import Any, Mapping

PROOF_CAPABILITY_SCHEMA = "stegverse.release-proof-capability.v1"
REQUIRED_POST_RETURN_CAPABILITIES = (
    "SDK_POST_RETURN_EVIDENCE_V1",
    "STEGCORE_SPE_STANDING_BINDING_V1",
    "MASTER_RECORDS_OPERATION_CUSTODY_V1",
)


def verify_release_proof_capabilities(
    release_receipt: Mapping[str, Any],
    *,
    required: tuple[str, ...] = REQUIRED_POST_RETURN_CAPABILITIES,
) -> dict[str, Any]:
    """Reject a release set that predates capabilities used by the proof run."""
    receipt = dict(release_receipt)
    raw = receipt.get("proof_capabilities")
    if not isinstance(raw, list):
        return {
            "verified": False,
            "reason": "proof_capabilities_missing",
            "required": list(required),
            "observed": [],
            "authority_effect": "NONE",
        }

    components = receipt.get("components")
    component_commits: dict[str, str] = {}
    if isinstance(components, list):
        for component in components:
            if not isinstance(component, Mapping):
                continue
            repository = str(component.get("repository") or "").strip()
            commit_sha = str(component.get("commit_sha") or "").strip().lower()
            if repository and len(commit_sha) == 40:
                component_commits[repository] = commit_sha

    observed: dict[str, dict[str, Any]] = {}
    reasons: list[str] = []
    for item in raw:
        if not isinstance(item, Mapping):
            reasons.append("proof_capability_not_object")
            continue
        capability_id = str(item.get("capability_id") or "").strip()
        if not capability_id:
            reasons.append("proof_capability_id_missing")
            continue
        if item.get("schema") != PROOF_CAPABILITY_SCHEMA:
            reasons.append(f"{capability_id}:schema_invalid")
            continue
        repository = str(item.get("repository") or "").strip()
        release_commit = str(item.get("release_commit_sha") or "").strip().lower()
        feature_commit = str(item.get("feature_commit_sha") or "").strip().lower()
        if len(release_commit) != 40 or len(feature_commit) != 40:
            reasons.append(f"{capability_id}:commit_invalid")
            continue
        if item.get("feature_in_release_commit") is not True:
            reasons.append(f"{capability_id}:feature_not_in_release")
            continue
        if item.get("containment_verification") not in {"ANCESTOR_OR_EQUAL", "TREE_EQUIVALENT"}:
            reasons.append(f"{capability_id}:containment_verification_invalid")
            continue
        expected_release_commit = component_commits.get(repository)
        if expected_release_commit is None:
            reasons.append(f"{capability_id}:repository_not_in_release")
            continue
        if expected_release_commit != release_commit:
            reasons.append(f"{capability_id}:release_commit_mismatch")
            continue
        if item.get("authority_effect") not in {None, "NONE"}:
            reasons.append(f"{capability_id}:authority_escalation")
            continue
        observed[capability_id] = dict(item)

    missing = [capability for capability in required if capability not in observed]
    reasons.extend(f"missing:{capability}" for capability in missing)
    return {
        "verified": not reasons,
        "reason": "ok" if not reasons else "release_proof_capability_gate_failed",
        "reasons": reasons or ["ok"],
        "required": list(required),
        "observed": sorted(observed),
        "authority_effect": "NONE",
    }


__all__ = [
    "PROOF_CAPABILITY_SCHEMA",
    "REQUIRED_POST_RETURN_CAPABILITIES",
    "verify_release_proof_capabilities",
]
