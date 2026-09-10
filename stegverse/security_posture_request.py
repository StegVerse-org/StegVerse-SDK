"""Non-authorizing SDK request inputs for authoritative Interlock/InTr posture resolution."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

REQUEST_SCHEMA = "stegverse.sdk.security-posture-request.v1"
EXTENSION_KEY = "security_posture_request"
TIERS = {"SECURE", "HIGH", "HIGHEST"}


class SecurityPostureRequestError(ValueError):
    pass


def validate_security_posture_request(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise SecurityPostureRequestError("security_posture_request must be an object")
    request = deepcopy(dict(value))
    allowed = {
        "schema",
        "task_id",
        "selected_tier",
        "selection_present",
        "organization_minimum_tier",
        "data_class",
        "channel",
        "authority_effect",
    }
    unknown = sorted(set(request) - allowed)
    if unknown:
        raise SecurityPostureRequestError(
            "unknown security_posture_request fields: " + ", ".join(unknown)
        )
    if request.get("schema") != REQUEST_SCHEMA:
        raise SecurityPostureRequestError("invalid_sdk_posture_request_schema")
    task_id = request.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        raise SecurityPostureRequestError("security_posture_request.task_id is required")
    if request.get("authority_effect") != "NONE_REQUEST_INPUT_ONLY":
        raise SecurityPostureRequestError("sdk_posture_request_must_be_non_authorizing")
    selection_present = request.get("selection_present")
    if not isinstance(selection_present, bool):
        raise SecurityPostureRequestError("security_posture_request.selection_present must be boolean")
    selected_tier = request.get("selected_tier")
    if selection_present:
        if selected_tier not in TIERS:
            raise SecurityPostureRequestError("explicit security posture selection requires a supported selected_tier")
    elif selected_tier is not None:
        raise SecurityPostureRequestError("selected_tier must be null/absent when selection_present=false")
    org_minimum = request.get("organization_minimum_tier", "SECURE")
    if org_minimum not in TIERS:
        raise SecurityPostureRequestError("unsupported organization_minimum_tier")
    request["organization_minimum_tier"] = org_minimum
    data_class = request.get("data_class")
    if data_class is not None and (not isinstance(data_class, str) or not data_class.strip()):
        raise SecurityPostureRequestError("security_posture_request.data_class must be non-empty when supplied")
    channel = request.get("channel")
    if channel is not None and (not isinstance(channel, str) or not channel.strip()):
        raise SecurityPostureRequestError("security_posture_request.channel must be non-empty when supplied")
    return request


def build_security_posture_request(
    *,
    task_id: str,
    selected_tier: str | None = None,
    selection_present: bool = False,
    organization_minimum_tier: str = "SECURE",
    data_class: str | None = None,
    channel: str | None = None,
) -> dict[str, Any]:
    return validate_security_posture_request(
        {
            "schema": REQUEST_SCHEMA,
            "task_id": task_id,
            "selected_tier": selected_tier,
            "selection_present": selection_present,
            "organization_minimum_tier": organization_minimum_tier,
            "data_class": data_class,
            "channel": channel,
            "authority_effect": "NONE_REQUEST_INPUT_ONLY",
        }
    )


__all__ = [
    "EXTENSION_KEY",
    "REQUEST_SCHEMA",
    "SecurityPostureRequestError",
    "build_security_posture_request",
    "validate_security_posture_request",
]
