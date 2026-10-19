"""Evaluator governance execution with authoritative Interlock/InTr posture binding.

The SDK constructs the exact governance transition request but never resolves its
security posture. Posture-free execution preserves the existing governance ingress
runtime path. Posture-bound execution invokes StegOS Interlock/InTr's resolver (or
an injected resolver for deterministic tests), verifies exact task/payload/transition
bindings, then executes the unchanged transition request.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Callable, Mapping

from .governance_ingress_runtime import external_manifest_to_public_request
from .intr_posture_runtime_bridge import resolve_manifest_posture
from .optional_package_refusal import optional_package_unavailable, render

Resolver = Callable[..., Mapping[str, Any]]

FAILURE_INTR_RESOLVER_UNAVAILABLE = "INTR_POSTURE_RESOLVER_UNAVAILABLE"
INTR_RESOLVER_REPAIR = (
    "Interlock/InTr security-posture resolver is unavailable; install/materialize "
    "the canonical StegOS runtime or inject intr_posture_resolver"
)


class IntrResolverUnavailable(RuntimeError):
    """No StegOS resolver installed and none injected; .disposition holds the six fields."""

    def __init__(self, disposition: Mapping[str, Any]):
        self.disposition = dict(disposition)
        super().__init__(f"{INTR_RESOLVER_REPAIR}: {render(self.disposition)}")


def _load_intr_resolver() -> Resolver:
    try:
        from stegos.intr_security_posture_resolution import resolve_task_security_posture
    except ImportError as exc:
        raise IntrResolverUnavailable(optional_package_unavailable(
            FAILURE_INTR_RESOLVER_UNAVAILABLE, "stegos.intr_security_posture_resolution", INTR_RESOLVER_REPAIR,
            "stegverse.evaluator_governance_runtime.run_evaluator_governance_manifest(intr_posture_resolver=...)",
        )) from exc
    return resolve_task_security_posture


def run_evaluator_governance_manifest(
    manifest: Mapping[str, Any],
    *,
    custody_db: str,
    host_identity: str = "stegverse-sovereign-local",
    intr_posture_resolver: Resolver | None = None,
    posture_observed_at: str | None = None,
) -> dict[str, Any]:
    """Preserve legacy execution unless posture-bound InTr resolution is requested."""
    extensions = manifest.get("extensions") or {}
    posture_requested = isinstance(extensions, Mapping) and extensions.get("security_posture_request") is not None
    if not posture_requested:
        from .governance_ingress_runtime import run_external_manifest
        governed_result = run_external_manifest(
            manifest,
            custody_db=custody_db,
            host_identity=host_identity,
        )
        result = deepcopy(dict(governed_result))
        result["intr_security_posture_binding"] = None
        result["posture_bound_execution"] = False
        result["sdk_resolved_posture"] = False
        return result

    from .sovereign_validation_runtime import run_sovereign_validation

    transition_request = external_manifest_to_public_request(manifest)
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
    result["posture_bound_execution"] = True
    result["sdk_resolved_posture"] = False
    return result


__all__ = ["run_evaluator_governance_manifest"]
