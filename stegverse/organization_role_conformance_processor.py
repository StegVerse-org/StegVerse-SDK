"""Manifest binding for an organization-role conformance request.

The role-version propagation owner emits one request per stale organization;
the receiving organization's existing manifest ingress evaluates its own source
against the target version and appends ALLOW, DENY or actionable FAIL_CLOSED
under its ledger lock. This module only admits the request shape and derives
the request graph. The request rides the existing extension contract beside
``extensions.stegverse_route``; it is never a top-level manifest field.

Issuer, destination, binding, version and file-digest predicates are the
receiving organization's to evaluate, so a structurally complete request is
carried unchanged rather than judged here. Nothing here reads organization
source, appends a receipt, mints a WorkerCoordinator claim/fence or grants
authority.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .route_resolution import ORGANIZATION_ROLE_CONFORMANCE_ROUTE_ID, route_from_manifest

PROCESSING_CAPABILITY = "organization_role_conformance"
ROUTE_ID = ORGANIZATION_ROLE_CONFORMANCE_ROUTE_ID
REQUEST_EXTENSION = "stegverse_organization_role_conformance_request"
REQUEST_SCHEMA = "stegverse.organization-role-conformance-request/v1"
_REQUEST_FIELDS = frozenset({
    "schema", "issuer", "destination_organization", "manifest_binding", "target_role_version",
})


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value


def validate_organization_role_conformance_request(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("organization_role_conformance processor_request must be an object")
    if value.get("schema") != REQUEST_SCHEMA:
        raise ValueError(f"organization_role_conformance request schema must be {REQUEST_SCHEMA}")
    unknown = sorted(set(value) - _REQUEST_FIELDS)
    if unknown:
        raise ValueError("unknown organization_role_conformance request fields: " + ", ".join(unknown))
    issuer = value.get("issuer")
    if not isinstance(issuer, Mapping):
        raise ValueError("issuer must be an object")
    _text(issuer.get("repository"), "issuer.repository")
    _text(issuer.get("owner_task_id"), "issuer.owner_task_id")
    _text(value.get("destination_organization"), "destination_organization")
    for field in ("manifest_binding", "target_role_version"):
        if not isinstance(value.get(field), Mapping):
            raise ValueError(f"{field} must be an object")
    # Carried byte-for-byte: the receiving organization recomputes the binding
    # and file digests from exactly what the issuer declared.
    return deepcopy(dict(value))


def derive_state_graph(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    route = route_from_manifest(canonical)
    if route.get("route_id") != ROUTE_ID or route.get("processor_capability") != PROCESSING_CAPABILITY:
        raise ValueError("ORGANIZATION_ROLE_CONFORMANCE_MANIFEST_ROUTE_CAPABILITY_MISMATCH")
    if (canonical.get("processing") or {}).get("capability") != PROCESSING_CAPABILITY:
        raise ValueError("manifest processing capability does not select organization_role_conformance")
    request = validate_organization_role_conformance_request(
        (canonical.get("extensions") or {}).get(REQUEST_EXTENSION)
    )
    owner_task_id = request["issuer"]["owner_task_id"]
    return {
        "schema": "stegverse.sdk.installed-state-transition-graph/v1",
        "graph_id": owner_task_id + ":ORGANIZATION-ROLE-CONFORMANCE",
        "canonical_task_id": owner_task_id,
        "processing_capability": PROCESSING_CAPABILITY,
        "route_id": ROUTE_ID,
        "request": request,
        "ordered_transitions": [],
        "ordered_transitions_source": "RECEIVING_ORGANIZATION_MANIFEST_INGRESS",
        # The receiving organization appends its disposition under its own
        # ledger lock; evaluation claims no worker.
        "requires_workercoordinator_claim_fence": False,
        "predecessor_closure_required": True,
        "adapter_executes_lifecycle": False,
        "authority_effect": "NONE_GRAPH_DERIVATION_ONLY",
    }


__all__ = [
    "PROCESSING_CAPABILITY", "ROUTE_ID", "REQUEST_EXTENSION", "REQUEST_SCHEMA",
    "validate_organization_role_conformance_request", "derive_state_graph",
]
