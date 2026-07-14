"""SDK validation for StegVerse system-boundary declarations.

This module validates operational state and authority boundaries only. It does
not determine consciousness, personhood, welfare status, or execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

REQUIRED_SURFACES = {"model", "orchestration", "session", "memory", "environment"}
VALID_STATE_KINDS = {"none", "transient", "session", "durable", "external"}
VALID_PERSISTENCE = {"none", "invocation", "session", "cross-session", "indefinite"}
VALID_DECISION_SOURCES = {"policy-engine", "human", "quorum", "none"}
REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "declaration_id",
    "system_id",
    "generated_at",
    "surfaces",
    "continuity",
    "authority",
    "claims_boundary",
}


@dataclass(frozen=True)
class SystemBoundaryValidationResult:
    accepted: bool
    status: str
    errors: list[str]
    non_claims: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "status": self.status,
            "errors": list(self.errors),
            "non_claims": dict(self.non_claims),
        }


def validate_system_boundary_declaration(
    declaration: Mapping[str, Any],
) -> SystemBoundaryValidationResult:
    """Validate a non-authorizing system-boundary declaration."""

    errors: list[str] = []
    if not isinstance(declaration, Mapping):
        return _deny(["system-boundary declaration must be an object"])

    if set(declaration) != REQUIRED_TOP_LEVEL_KEYS:
        return _deny(["system-boundary declaration keys do not match required contract"])

    if declaration.get("schema_version") != "0.1":
        errors.append("schema_version is not supported")

    for key in ("declaration_id", "system_id", "generated_at"):
        if not isinstance(declaration.get(key), str) or not declaration[key]:
            errors.append(f"{key} must be a non-empty string")

    surfaces = declaration.get("surfaces")
    if not isinstance(surfaces, Mapping) or set(surfaces) != REQUIRED_SURFACES:
        errors.append("surface set must be exact")
    else:
        errors.extend(_validate_surfaces(surfaces))

    continuity = declaration.get("continuity")
    if not isinstance(continuity, Mapping):
        errors.append("continuity must be an object")
    else:
        errors.extend(_validate_continuity(continuity))

    authority = declaration.get("authority")
    if not isinstance(authority, Mapping):
        errors.append("authority must be an object")
    else:
        errors.extend(_validate_authority(authority))

    claims = declaration.get("claims_boundary")
    if not isinstance(claims, Mapping):
        errors.append("claims_boundary must be an object")
    else:
        errors.extend(_validate_claims(claims))

    if errors:
        return _deny(errors)

    return SystemBoundaryValidationResult(
        accepted=True,
        status="accepted_for_non_authorizing_sdk_ingestion",
        errors=[],
        non_claims=_non_claims(),
    )


def _validate_surfaces(surfaces: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for name, surface in surfaces.items():
        if not isinstance(surface, Mapping):
            errors.append(f"surface {name} must be an object")
            continue
        if not isinstance(surface.get("present"), bool):
            errors.append(f"surface {name}.present must be boolean")
        if surface.get("state_kind") not in VALID_STATE_KINDS:
            errors.append(f"surface {name}.state_kind invalid")
        if surface.get("persistence") not in VALID_PERSISTENCE:
            errors.append(f"surface {name}.persistence invalid")
        if not isinstance(surface.get("mutable_by_inference"), bool):
            errors.append(f"surface {name}.mutable_by_inference must be boolean")
        if "storage_refs" in surface and not isinstance(surface["storage_refs"], list):
            errors.append(f"surface {name}.storage_refs must be an array")

    model = surfaces.get("model", {})
    if isinstance(model, Mapping):
        if model.get("persistence") != "invocation":
            errors.append("model boundary must remain invocation-scoped")
        if model.get("mutable_by_inference") is not False:
            errors.append("inference must not claim to rewrite model state")
    return errors


def _validate_continuity(continuity: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    prior_state = continuity.get("prior_state_can_affect_future_transition")
    feedback_paths = continuity.get("feedback_paths")
    trajectory = continuity.get("trajectory_dependent")
    reconstructable = continuity.get("reconstructable")

    if not isinstance(prior_state, bool):
        errors.append("continuity prior-state flag missing")
    if not isinstance(feedback_paths, list):
        errors.append("continuity feedback_paths missing")
    if not isinstance(trajectory, bool):
        errors.append("continuity trajectory flag missing")
    if not isinstance(reconstructable, bool):
        errors.append("continuity reconstructable flag missing")

    if prior_state is True and isinstance(feedback_paths, list) and not feedback_paths:
        errors.append("continuity cannot claim prior-state influence without feedback_paths")
    if trajectory is True and prior_state is not True:
        errors.append("trajectory dependence requires prior-state influence")
    return errors


def _validate_authority(authority: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if authority.get("model_has_execution_authority") is not False:
        errors.append("model execution authority must be false")
    if authority.get("decision_source") not in VALID_DECISION_SOURCES:
        errors.append("authority decision_source invalid")
    if not isinstance(authority.get("commit_boundary"), str) or not authority["commit_boundary"]:
        errors.append("commit boundary is required")
    return errors


def _validate_claims(claims: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("consciousness_claim", "personhood_claim", "welfare_claim"):
        if claims.get(key) != "not_evaluated":
            errors.append(f"{key} must remain not_evaluated")
    if not isinstance(claims.get("scope_note"), str) or not claims["scope_note"]:
        errors.append("claims boundary scope_note is required")
    return errors


def _non_claims() -> dict[str, bool]:
    return {
        "sdk_validation_is_execution": False,
        "sdk_validation_is_admissibility": False,
        "state_continuity_proves_consciousness": False,
        "self_report_proves_personhood": False,
        "model_output_grants_commit_time_standing": False,
    }


def _deny(errors: list[str]) -> SystemBoundaryValidationResult:
    return SystemBoundaryValidationResult(
        accepted=False,
        status="rejected",
        errors=errors,
        non_claims=_non_claims(),
    )
