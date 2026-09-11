"""Provider-neutral bounded external-resource consumer for WorkSpace projections.

Consumes the existing ingress-bound Interlock request and produces deterministic
local projection lifecycle state. This module does not itself perform provider I/O,
mint InTr receipts, grant governance authority, or claim delivery/custody.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping

from .active_probe_execution import ProbeExecutor, execute_active_probes
from .external_interlock_ingress_binding import validate_ingress_bound_interlock_request
from .governance_navigation import canonical_sha256

WORKSPACE_CONSUMER_PROFILE = "stegverse.workspace-resource-consumer.v1"
SUPPORTED_OPERATIONS = {"OBSERVE", "MATERIALIZE", "REFRESH", "REVOKE", "EXPIRE", "DESTROY"}
ProviderHook = Callable[[str, Mapping[str, Any]], Mapping[str, Any]]


def _nested_ingress(request: Mapping[str, Any]) -> dict[str, Any]:
    validated = validate_ingress_bound_interlock_request(request)
    return deepcopy(
        validated["payload"]["manifest"]["payload"]["canonical_ingress_manifest"]
    )


def _transition(ingress: Mapping[str, Any]) -> dict[str, Any]:
    extensions = ingress.get("extensions")
    if not isinstance(extensions, Mapping):
        raise ValueError("ingress extensions missing")
    transition = extensions.get("stegverse_state_transition")
    if not isinstance(transition, Mapping):
        raise ValueError("stegverse_state_transition evidence required")
    return deepcopy(dict(transition))


def consume_workspace_resource(
    *,
    request: Mapping[str, Any],
    operation: str,
    projection_id: str,
    prior_projection_ref: str | None = None,
    provider_hook: ProviderHook | None = None,
    probe_executor: ProbeExecutor | None = None,
) -> dict[str, Any]:
    """Consume a validated canonical ingress object into bounded projection state.

    MATERIALIZE/REFRESH require READY evidence. If current represented evidence is
    PROBE_REQUIRED, a runtime-supplied active probe executor may gather current
    evidence and the canonical transition normalizer re-derives readiness. Caller
    manifest data never supplies the executor or directly overrides readiness.

    REVOKE/EXPIRE/DESTROY remain available even if current readiness is not READY.
    A provider hook may return observations, but its output remains provider evidence
    and does not become governance, transport, receipt, or custody authority.
    """
    op = str(operation or "").strip().upper()
    if op not in SUPPORTED_OPERATIONS:
        raise ValueError(f"unsupported workspace operation: {op}")
    projection = str(projection_id or "").strip()
    if not projection:
        raise ValueError("projection_id is required")

    ingress = _nested_ingress(request)
    transition = _transition(ingress)
    readiness_before_probe = transition.get("readiness")
    active_probe_evidence: list[dict[str, Any]] = []

    if op in {"MATERIALIZE", "REFRESH"} and readiness_before_probe != "READY" and probe_executor is not None:
        probe_resolution = execute_active_probes(
            state_transition=transition,
            ingress_manifest=ingress,
            executor=probe_executor,
        )
        transition = probe_resolution["transition"]
        active_probe_evidence = deepcopy(probe_resolution["probe_results"])

    readiness = transition.get("readiness")
    if op in {"MATERIALIZE", "REFRESH"} and readiness != "READY":
        reasons = transition.get("probe_reasons") or []
        raise ValueError(f"workspace {op} requires READY state; probe required: {reasons}")

    provider_observation: dict[str, Any] | None = None
    if provider_hook is not None:
        observed = provider_hook(op, deepcopy(ingress))
        if not isinstance(observed, Mapping):
            raise ValueError("provider_hook must return an object")
        provider_observation = deepcopy(dict(observed))

    state = {
        "profile": WORKSPACE_CONSUMER_PROFILE,
        "operation": op,
        "projection_id": projection,
        "resource_manifest_sha256": canonical_sha256(ingress),
        "transition_id": transition.get("transition_id"),
        "state_domain": transition.get("state_domain"),
        "prior_state_ref": transition.get("prior_state_ref"),
        "new_state_ref": transition.get("new_state_ref"),
        "prior_projection_ref": prior_projection_ref,
        "readiness_before_probe": readiness_before_probe,
        "readiness": readiness,
        "probe_reasons": deepcopy(transition.get("probe_reasons") or []),
        "active_probe_executed": bool(active_probe_evidence),
        "active_probe_evidence": active_probe_evidence,
        "provider_observation": provider_observation,
        "provider_io_claimed": provider_hook is not None,
        "authority_transfer": False,
        "governance_authority": False,
        "intr_receipt_minted": False,
        "mir_custody_claimed": False,
        "master_records_custody_claimed": False,
    }
    state["projection_state_ref"] = "sha256:" + canonical_sha256(state)
    return state


__all__ = [
    "SUPPORTED_OPERATIONS",
    "WORKSPACE_CONSUMER_PROFILE",
    "consume_workspace_resource",
]
