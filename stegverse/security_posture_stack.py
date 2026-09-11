"""SDK security-posture request and projection helpers.

The SDK may describe caller-selected posture and posture-resolution inputs, and may
render authoritative results returned by Interlock/InTr. It does not resolve or mint
the authoritative automatic/effective posture for a transition.
"""
from __future__ import annotations

from typing import Any, Mapping

from .security_posture import TIER_TO_POSTURE, SecurityPostureError, _tier_rank, resolve_security_posture

REQUEST_SCHEMA = "stegverse.sdk.security-posture-request.v1"
RESOLUTION_SCHEMA = "stegos.intr-security-posture-resolution.v1"


def build_security_posture_request(
    *,
    task_id: str,
    selected_tier: str | None = None,
    organization_minimum_tier: str = "SECURE",
    data_class: str | None = None,
    channel: str | None = None,
) -> dict[str, Any]:
    """Describe posture inputs for Interlock/InTr without asserting a final tier."""
    if not task_id:
        raise SecurityPostureError("security_posture_task_id_required")
    if organization_minimum_tier not in TIER_TO_POSTURE:
        raise SecurityPostureError(f"unsupported_security_posture_organization_minimum_tier:{organization_minimum_tier}")
    if selected_tier is not None and selected_tier not in TIER_TO_POSTURE:
        raise SecurityPostureError(f"unsupported_security_posture_selected_tier:{selected_tier}")
    selected = resolve_security_posture(TIER_TO_POSTURE[selected_tier]) if selected_tier is not None else None
    return {
        "schema": REQUEST_SCHEMA,
        "task_id": task_id,
        "selected_tier": selected_tier,
        "selected_posture_id": selected["posture_id"] if selected else None,
        "selected_posture_sha256": selected["posture_sha256"] if selected else None,
        "selection_present": selected_tier is not None,
        "organization_minimum_tier": organization_minimum_tier,
        "data_class": data_class,
        "channel": channel,
        "authoritative_automatic_posture": None,
        "authoritative_effective_posture": None,
        "resolution_authority": "INTERLOCK_INTR",
        "credential_authority": "TV/TVC",
        "authority_effect": "NONE_REQUEST_INPUT_ONLY",
    }


def project_intr_posture_resolution(resolution: Mapping[str, Any]) -> dict[str, Any]:
    """Render the authoritative InTr result without reinterpreting it."""
    if resolution.get("schema") != RESOLUTION_SCHEMA:
        raise SecurityPostureError("invalid_intr_posture_resolution_schema")
    if resolution.get("resolution_authority") != "INTERLOCK_INTR":
        raise SecurityPostureError("intr_posture_resolution_authority_required")
    automatic = resolution.get("automatic_posture")
    selected = resolution.get("selected_posture")
    effective = resolution.get("effective_posture")
    if not all(isinstance(value, Mapping) for value in (automatic, selected, effective)):
        raise SecurityPostureError("intr_posture_resolution_incomplete")
    for value in (automatic, selected, effective):
        tier = str(value.get("tier") or "")
        if tier not in TIER_TO_POSTURE:
            raise SecurityPostureError("intr_posture_resolution_tier_invalid")
    if _tier_rank(str(selected["tier"])) < _tier_rank(str(automatic["tier"])):
        raise SecurityPostureError("intr_posture_resolution_contains_downgrade")
    if _tier_rank(str(effective["tier"])) != max(_tier_rank(str(automatic["tier"])), _tier_rank(str(selected["tier"]))):
        raise SecurityPostureError("intr_posture_effective_tier_inconsistent")
    return {
        "schema": "stegverse.sdk.security-posture-ui-projection.v1",
        "automatic_posture": dict(automatic),
        "selected_posture": dict(selected),
        "effective_posture": dict(effective),
        "posture_instance": dict(resolution.get("posture_instance") or {}),
        "resolution_authority": "INTERLOCK_INTR",
        "credential_authority": "TV/TVC",
        "sdk_reinterpreted_posture": False,
        "authority_effect": "NONE_UI_PROJECTION_ONLY",
    }


def select_posture_stack(*, task_id: str = "PREVIEW_ONLY", organization_minimum_tier: str = "SECURE", data_class: str | None = None, channel: str | None = None, selected_tier: str | None = None) -> dict[str, Any]:
    """Backward-compatible SDK request preview; not an authoritative posture resolution."""
    request = build_security_posture_request(
        task_id=task_id,
        selected_tier=selected_tier,
        organization_minimum_tier=organization_minimum_tier,
        data_class=data_class,
        channel=channel,
    )
    selected_posture = None
    if selected_tier is not None:
        selected_posture = {
            "tier": selected_tier,
            "posture_id": request["selected_posture_id"],
            "selection_present": True,
        }
    return {
        "schema": "stegverse.sdk.security-posture-request-preview.v1",
        "request": request,
        "selected_posture": selected_posture,
        "selection_present": selected_tier is not None,
        "automatic_posture": None,
        "effective_posture": None,
        "resolution_required_from": "INTERLOCK_INTR",
        "downgrade_below_automatic_floor_allowed": False,
        "authority_effect": "NONE_REQUEST_PREVIEW_ONLY",
    }
