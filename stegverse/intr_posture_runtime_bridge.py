"""Runtime bridge from SDK evaluator manifests to authoritative Interlock/InTr posture resolution.

The SDK never resolves final posture. A caller supplies a resolver callable owned by
Interlock/InTr. This bridge computes the exact SDK-side bindings, invokes that
resolver, and validates the returned authoritative resolution before governance
execution proceeds.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping

from .governance_navigation import canonical_sha256
from .security_posture_request import validate_security_posture_request
from .security_posture_stack import project_intr_posture_resolution

Resolver = Callable[..., Mapping[str, Any]]


class InTrPostureBridgeError(ValueError):
    pass


def _sha256_uri(value: Any) -> str:
    return "sha256:" + canonical_sha256(value)


def resolve_manifest_posture(
    *,
    manifest: Mapping[str, Any],
    transition_request: Mapping[str, Any],
    resolver: Resolver,
    observed_at: str,
) -> dict[str, Any]:
    extensions = manifest.get("extensions")
    if not isinstance(extensions, Mapping):
        raise InTrPostureBridgeError("manifest_extensions_required")
    raw = extensions.get("security_posture_request")
    if raw is None:
        raise InTrPostureBridgeError("security_posture_request_required_for_posture_bound_execution")
    request = validate_security_posture_request(raw)
    task_id = request["task_id"]
    payload_binding = (
        _sha256_uri(manifest["payload"])
        if manifest.get("payload") is not None
        else "sha256:" + str(manifest.get("payload_commitment") or "")
    )
    transition_binding = _sha256_uri(transition_request)
    resolution = resolver(
        request=deepcopy(request),
        task_id=task_id,
        payload_sha256=payload_binding,
        transition_request_sha256=transition_binding,
        observed_at=observed_at,
    )
    projected = project_intr_posture_resolution(resolution)
    instance = projected.get("posture_instance") or {}
    if instance.get("task_id") != task_id:
        raise InTrPostureBridgeError("posture_instance_task_mismatch")
    if instance.get("payload_sha256") != payload_binding:
        raise InTrPostureBridgeError("posture_instance_payload_mismatch")
    if instance.get("transition_request_sha256") != transition_binding:
        raise InTrPostureBridgeError("posture_instance_transition_mismatch")
    return {
        "schema":"stegverse.sdk.intr-posture-runtime-binding.v1",
        "task_id":task_id,
        "payload_sha256":payload_binding,
        "transition_request_sha256":transition_binding,
        "resolution":deepcopy(dict(resolution)),
        "projection":projected,
        "sdk_resolved_posture":False,
        "resolution_authority":"INTERLOCK_INTR",
        "authority_effect":"NONE_VERIFICATION_AND_BINDING_ONLY",
    }


__all__ = ["InTrPostureBridgeError", "resolve_manifest_posture"]
