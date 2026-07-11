from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .universal_transition_table_intake import validate_commitment_candidate

SPE_COMMITMENT_INTAKE_SCHEMA_VERSION = "stegverse.sdk.spe_commitment_intake.v0.1"


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _stable_hash(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def build_spe_commitment_candidate(
    transition_candidate: Mapping[str, Any],
    *,
    action: str,
    bounded_scope: Mapping[str, Any],
    review_ref: str,
    policy_context: Mapping[str, Any],
    delegation_context: Mapping[str, Any],
    validity_window: Mapping[str, Any],
    execution_context: Mapping[str, Any],
    recoverability_profile: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a non-authorizing Commitment Candidate from an SDK transition record.

    This function preserves the SDK transition identity and presents the candidate
    for a fresh SPE standing determination. It does not grant execution authority.
    """

    transition_id = str(transition_candidate.get("transition_id", "")).strip()
    run_id = str(transition_candidate.get("run_id", "")).strip()
    lifecycle_state = transition_candidate.get("lifecycle_state")
    origin = transition_candidate.get("origin", {})
    relationships = transition_candidate.get("relationships", {})
    governance = transition_candidate.get("governance", {})

    if not transition_id or not run_id:
        raise ValueError("transition_id and run_id are required")
    if lifecycle_state != "DECLARED":
        raise ValueError("SDK transition candidate must remain DECLARED")
    if origin.get("origin_class") != "SDK_INPUT":
        raise ValueError("origin_class must be SDK_INPUT")
    if governance.get("admissibility_result") != "PENDING":
        raise ValueError("admissibility_result must remain PENDING")
    if governance.get("commit_time_validity") != "PENDING":
        raise ValueError("commit_time_validity must remain PENDING")
    if not action.strip():
        raise ValueError("action is required")
    if not review_ref.strip():
        raise ValueError("review_ref is required")

    candidate = {
        "package_id": transition_id,
        "candidate_type": "COMMITMENT_CANDIDATE",
        "transition_id": transition_id,
        "run_id": run_id,
        "authorizing": False,
        "inherits_review_authority": False,
        "implies_standing": False,
        "requires_fresh_standing_determination": True,
        "bounded_scope": dict(bounded_scope),
        "actor": relationships.get("actor_ref"),
        "target": relationships.get("target_ref"),
        "action": action,
        "review_ref": review_ref,
        "evidence_refs": list(governance.get("evidence_refs", [])),
        "policy_context": dict(policy_context),
        "delegation_context": dict(delegation_context),
        "validity_window": dict(validity_window),
        "execution_context": dict(execution_context),
        "recoverability_profile": dict(recoverability_profile),
        "source": {
            "repository_ref": relationships.get("repository_ref"),
            "task_ref": relationships.get("task_ref"),
            "handoff_ref": relationships.get("handoff_ref"),
            "origin_manifest_id": origin.get("origin_manifest_id"),
        },
    }

    validate_commitment_candidate(candidate, transition_id)
    candidate["candidate_hash"] = _stable_hash(candidate)
    return candidate


def build_spe_intake_envelope(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Wrap a validated candidate in a deterministic, transport-neutral SPE envelope."""

    package_id = str(candidate.get("package_id", "")).strip()
    validate_commitment_candidate(dict(candidate), package_id)

    candidate_hash = candidate.get("candidate_hash") or _stable_hash(dict(candidate))
    envelope_core = {
        "schema_version": SPE_COMMITMENT_INTAKE_SCHEMA_VERSION,
        "destination_repo": "StegVerse-Labs/Standing-Proof-Engine",
        "route_purpose": "FRESH_STANDING_DETERMINATION",
        "package_id": package_id,
        "transition_id": candidate.get("transition_id"),
        "run_id": candidate.get("run_id"),
        "candidate_hash": candidate_hash,
        "candidate": dict(candidate),
        "authority": {
            "sdk_authorizing": False,
            "execution_authority_requested": False,
            "fresh_standing_determination_required": True,
        },
        "expected_result": ["ALLOW", "DENY", "FAIL_CLOSED"],
        "receipt_required": True,
    }
    return {**envelope_core, "envelope_hash": _stable_hash(envelope_core)}


__all__ = [
    "SPE_COMMITMENT_INTAKE_SCHEMA_VERSION",
    "build_spe_commitment_candidate",
    "build_spe_intake_envelope",
]
