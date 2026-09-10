"""Evaluator governance execution with authoritative Interlock/InTr posture binding.

The SDK constructs the exact governance transition request but never resolves its
security posture. When posture-bound execution is requested, this module invokes
StegOS Interlock/InTr's resolver (or an injected resolver for deterministic tests),
verifies the exact task/payload/transition bindings, then executes the unchanged
transition request through the existing sovereign governance runtime.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Callable, Mapping

from .governance_ingress_runtime import external_manifest_to_public_request
from .intr_posture_runtime_bridge import resolve_manifest_posture

Resolver = Callable[..., Mapping[str, Any]]


def _load_intr_resolver() -> Resolver:
    try:
        from stegos.intr_security_posture_resolution import resolve_task_security_posture
    except ImportError as exc:
        raise RuntimeError(
            "Interlock/InTr security-posture resolver is unavailable; install/materialize "
            "the canonical StegOS runtime or inject intr_posture_resolver"
        ) from exc
    return resolve_task_security_posture


def run_evaluator_governance_manifest(
    manifest: Mapping[str, Any],
    *,
    custody_db: str,
    host_identity: str = "stegverse-sovereign-local",
    intr_posture_resolver: Resolver | None = None,
    posture_observed_at: str | None = None,
) -> dict[str, Any]:
    """Resolve posture at InTr, then run the exact unchanged governance request."""
    from .sovereign_validation_runtime import run_sovereign_validation

    transition_request = external_manifest_to_public_request(manifest)
    extensions = manifest.get("extensions") or {}
    posture_requested = isinstance(extensions, Mapping) and extensions.get("security_posture_request") is not None
    posture_binding = None
    if posture_requested:
        resolver = intr_posture_resolver or _load_intr_resolver()
        observed_at = posture_observed_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        posture_binding = resolve_manifest_posture(
            manifest=manifest,
            transition_request=transition_request,
            resolver=resolver,
            observed_at=observed_at,
        )

    # Execute the exact request whose SHA-256 was supplied to Interlock/InTr.
    governed_result = run_sovereign_validation(
        transition_request,
        custody_db=custody_db,
        host_identity=host_identity,
    )
    result = deepcopy(dict(governed_result))
    result["intr_security_posture_binding"] = posture_binding
    result["posture_bound_execution"] = posture_binding is not None
    result["sdk_resolved_posture"] = False
    return result


__all__ = ["run_evaluator_governance_manifest"]
