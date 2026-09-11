"""Local SDK -> governance boundary preparation.

This module proves the SDK-side boundary contract without requiring a deployed,
published, or third-party governance runtime. It constructs the exact governance
transition request, resolves the requested InTr posture through an injected local
resolver, verifies the exact bindings, and emits a non-authorizing handoff artifact
for governance consumption.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Mapping

from .governance_ingress_runtime import external_manifest_to_public_request
from .intr_posture_runtime_bridge import resolve_manifest_posture

Resolver = Callable[..., Mapping[str, Any]]


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def prepare_local_governance_boundary(
    manifest: Mapping[str, Any],
    *,
    intr_posture_resolver: Resolver,
    observed_at: str,
) -> dict[str, Any]:
    """Prepare and prove the local SDK-side governance handoff boundary.

    No governance decision is synthesized. No runtime package is imported. The
    returned artifact states only that the exact SDK request has reached the
    governance-consumption boundary with verified InTr posture bindings.
    """
    transition_request = external_manifest_to_public_request(manifest)
    posture_binding = resolve_manifest_posture(
        manifest=manifest,
        transition_request=transition_request,
        resolver=intr_posture_resolver,
        observed_at=observed_at,
    )
    manifest_hash = _canonical_sha256(manifest)
    transition_hash = _canonical_sha256(transition_request)
    return {
        "schema": "stegverse.sdk.local-governance-boundary/v1",
        "boundary": "SDK_TO_GOVERNANCE",
        "boundary_state": "READY_FOR_GOVERNANCE_CONSUMPTION",
        "execution_scope": "LOCAL_SDK_BOUNDARY_TEST",
        "manifest_sha256": manifest_hash,
        "transition_request_sha256": transition_hash,
        "transition_request": transition_request,
        "intr_security_posture_binding": posture_binding,
        "exact_request_preserved": True,
        "governance_execution_performed": False,
        "governance_result_claimed": False,
        "external_package_materialization_required": False,
        "third_party_evaluator_execution": False,
        "authority_effect": "NONE",
        "observed_at": observed_at,
    }


__all__ = ["prepare_local_governance_boundary"]
