"""General customer-owned, single-host canonical governance route.

This module does NOT replace StegGate policy, issue credentials, operate a hosted
StegVerse runtime or mint Master Records receipts. Manifest-only run-manifest
is intentionally non-authorizing: a customer host must explicitly supply its
own authenticated standing verifier, bounded executor and durable evidence
writer to the programmatic execute_local_manifest entrypoint.
"""
from __future__ import annotations

from typing import Any, Callable, Mapping

from .manifest_contract import validate_ingress_manifest
from .route_resolution import CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID, route_from_manifest


class CustomerLocalRouteRefused(ValueError):
    """Exact local pre-commit prerequisite not established."""


def _checked_local_route(manifest: Mapping[str, Any]) -> dict[str, Any]:
    checked = validate_ingress_manifest(manifest)
    route = route_from_manifest(checked)
    if (
        checked["processing"]["capability"] != "governance"
        or route["route_id"] != CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID
        or route["processor_capability"] != "governance"
        or route["routing_surface"] != "CUSTOMER_LOCAL"
        or route["runtime_binding"] != "stegverse.customer_local_governance.execute_manifest"
    ):
        raise CustomerLocalRouteRefused("CUSTOMER_LOCAL_ROUTE_BINDING_NOT_ESTABLISHED")
    if checked.get("completion") is not None:
        raise CustomerLocalRouteRefused("FEDERATED_COMPLETION_NOT_CUSTOMER_LOCAL")
    return checked


def execute_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Safe SDK run-manifest interface without any implicit authority or network."""
    _checked_local_route(manifest)
    raise CustomerLocalRouteRefused(
        "CUSTOMER_LOCAL_HOST_BINDINGS_REQUIRED: use execute_local_manifest with "
        "an independently trusted standing verifier, precommit evidence writer "
        "and bounded customer-owned executor"
    )


def execute_local_manifest(
    manifest: Mapping[str, Any],
    *,
    authority_evidence: Mapping[str, Any],
    authority_verifier: Callable[..., Mapping[str, Any]],
    precommit_recorder: Callable[[Mapping[str, Any]], Any],
    executor: Callable[[], Any],
    result_recorder: Callable[[Mapping[str, Any]], Any],
) -> dict[str, Any]:
    """Delegate the ONLY decision/commit gate to actual locally installed StegCore.

    Trust in the customer-supplied verifier and durable recorders MUST be
    established independently by the deploying customer. This function does
    not implement credential checks, replay reservations, checkpointing or
    independently immutable custody; a product integrating it must provide
    and test those requirements itself.
    """
    checked = _checked_local_route(manifest)
    if not all(callable(x) for x in (
        authority_verifier, precommit_recorder, executor, result_recorder
    )):
        raise CustomerLocalRouteRefused("CUSTOMER_LOCAL_TRUSTED_CALLBACKS_REQUIRED")
    request_data = checked["extensions"].get("stegverse_governance_request")
    if not isinstance(request_data, Mapping):
        raise CustomerLocalRouteRefused("CANONICAL_GOVERNANCE_REQUEST_REQUIRED")
    target = checked["candidate"]["target"]
    try:
        resolution = authority_verifier(authority_evidence, target=target)
    except Exception as exc:
        raise CustomerLocalRouteRefused(
            "CUSTOMER_AUTHORITY_VERIFICATION_FAILED:" + type(exc).__name__
        ) from exc
    if (
        not isinstance(resolution, Mapping)
        or resolution.get("status") not in ("valid", "approved")
        or resolution.get("target_binding") != target
    ):
        raise CustomerLocalRouteRefused("CUSTOMER_AUTHORITY_NOT_ESTABLISHED")
    try:
        from stegcore import AdmissibilityRequest
        from stegcore.steggate_runtime import governed_steggate_execute
    except ImportError as exc:
        raise CustomerLocalRouteRefused("CANONICAL_STEGCORE_NOT_INSTALLED") from exc
    request = AdmissibilityRequest.model_validate(request_data)
    observation = governed_steggate_execute(
        request,
        executor,
        declared_execution_context=dict(request_data.get("declared_context") or {}),
        authority_resolution=dict(resolution),
        pre_execution_observer=precommit_recorder,
    )
    result = {
        "schema": "stegverse.sdk.customer-local-governance-result/v1",
        "processing_route_id": CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID,
        "status": observation.status,
        "disposition": observation.evaluation.disposition,
        "executor_invoked": observation.executor_invoked,
        "decision_state_hash": observation.evaluation.decision_state_hash,
        "canonical_pre_state_hash": observation.pre_state_hash,
        "canonical_post_state_hash": observation.post_state_hash,
        "canonical_coherence_receipt": observation.coherence_receipt,
        "authority_boundary": "CUSTOMER_LOCAL_NOT_STEGVERSE_MASTER_RECORDS",
    }
    # Independent output custody is the integrating customer's responsibility.
    result_recorder(result)
    return result
