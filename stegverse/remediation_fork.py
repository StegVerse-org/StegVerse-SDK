"""The remediation fork every non-ALLOW carries (NODE_INGRESS_SETTLED_SPECIFICATION §8).

Remediation is a manifest carried on the packet. When a result is not ALLOW,
the Manifest Builder builds a remediation manifest bound to that exact
non-ALLOW, and it travels its own path: the route and processing capability
it declares (``stegverse.route.governed-remediation.v1`` / ``remediation``),
resolved like every other capability by the receiving organization's
capability bindings, to StegHealer. The original packet keeps its
disposition and lineage unchanged and continues independently. Two lanes,
one fork, each with its own receipts.

StegHealer classifies RESUBMIT or RE_MANIFEST, non-authorizing, and the
classification returns through the organization ``.github`` governance
interfaces. Only an authenticated, read-back governance decision lets the SDK
act (``stegverse.governed_remediation.perform_governed_remediation``).
StegHealer never alters, changes or creates a manifest: a RE_MANIFEST is
built here, by the Manifest Builder.

Nothing here classifies, decides, transports, records a receipt or grants
authority. A non-ALLOW of a remediation manifest does not fork again; it
stays the remediation lane's own non-ALLOW.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .route_resolution import GOVERNED_REMEDIATION_ROUTE_ID, canonical_sha256, route_from_manifest

OWNER_TASK_ID = "STEGHEALTH-ECOSYSTEM-FAILURE-REMEDIATION-001"
REMEDIATION_CAPABILITY = "remediation"
REQUEST_EXTENSION = "stegverse_remediation_fork_request"
REQUEST_SCHEMA = "stegverse.remediation-fork-request/v1"
FORK_SCHEMA = "stegverse.sdk.remediation-fork/v1"
NON_ALLOW = ("DENY", "FAIL_CLOSED")

_DIGESTS = ("original_request_sha256", "original_wire_manifest_sha256", "original_canonical_manifest_sha256")
_FIELDS = frozenset({
    "schema", *_DIGESTS, "original_processing_capability", "original_route_id",
    "original_destination", "non_allow", "non_allow_sha256",
})


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value


def validate_remediation_fork_request(value: Any) -> dict[str, Any]:
    """Closed request: the exact original identity and the exact non-ALLOW it judges."""
    if not isinstance(value, Mapping):
        raise ValueError("remediation processor_request must be an object")
    if value.get("schema") != REQUEST_SCHEMA:
        raise ValueError(f"remediation request schema must be {REQUEST_SCHEMA}")
    unknown = sorted(set(value) - _FIELDS)
    if unknown:
        raise ValueError("unknown remediation request fields: " + ", ".join(unknown))
    for field in (*_DIGESTS, "original_processing_capability", "original_route_id", "non_allow_sha256"):
        _text(value.get(field), field)
    if value["original_processing_capability"] == REMEDIATION_CAPABILITY:
        raise ValueError("REMEDIATION_FORK_OF_A_REMEDIATION_MANIFEST")
    non_allow = value.get("non_allow")
    if not isinstance(non_allow, Mapping) or non_allow.get("disposition") not in NON_ALLOW:
        raise ValueError("REMEDIATION_FORK_REQUIRES_NON_ALLOW")
    if canonical_sha256(dict(non_allow)) != value["non_allow_sha256"]:
        raise ValueError("REMEDIATION_FORK_NON_ALLOW_DIGEST_MISMATCH")
    if non_allow.get("request_sha256") not in (None, value["original_request_sha256"]):
        raise ValueError("REMEDIATION_FORK_NON_ALLOW_IS_FOR_ANOTHER_REQUEST")
    if not isinstance(value.get("original_destination"), Mapping):
        raise ValueError("original_destination is required")
    return deepcopy(dict(value))


def derive_state_graph(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Request graph for the remediation lane; classification belongs to StegHealer."""
    canonical = validate_ingress_manifest(manifest)
    route = route_from_manifest(canonical)
    if route.get("route_id") != GOVERNED_REMEDIATION_ROUTE_ID:
        raise ValueError("REMEDIATION_MANIFEST_ROUTE_MISMATCH")
    if (canonical.get("processing") or {}).get("capability") != REMEDIATION_CAPABILITY:
        raise ValueError("manifest processing capability does not select remediation")
    request = validate_remediation_fork_request((canonical.get("extensions") or {}).get(REQUEST_EXTENSION))
    return {
        "schema": "stegverse.sdk.installed-state-transition-graph/v1",
        "graph_id": f"{OWNER_TASK_ID}:REMEDIATION:{request['original_request_sha256']}:{request['non_allow_sha256']}",
        "canonical_task_id": None,
        "owner_task_id": OWNER_TASK_ID,
        "processing_capability": REMEDIATION_CAPABILITY,
        "route_id": GOVERNED_REMEDIATION_ROUTE_ID,
        "request": request,
        "ordered_transitions": [],
        "ordered_transitions_source": "RECEIVING_ORGANIZATION_MANIFEST_INGRESS",
        "classification_authority": "StegVerse-Labs/StegVerse-Healer",
        "classification_receipt_class": "REMEDIATION_CLASSIFIED",
        "classification_grants_authority": False,
        "requires_workercoordinator_claim_fence": False,
        "predecessor_closure_required": True,
        "adapter_executes_lifecycle": False,
        "authority_effect": "NONE_GRAPH_DERIVATION_ONLY",
    }


def fork_request(original_request: Mapping[str, Any], non_allow: Mapping[str, Any]) -> dict[str, Any]:
    """The remediation request bound to one original request and one of its non-ALLOW results."""
    return validate_remediation_fork_request({
        "schema": REQUEST_SCHEMA,
        "original_request_sha256": original_request.get("request_sha256"),
        "original_wire_manifest_sha256": original_request.get("wire_manifest_sha256"),
        "original_canonical_manifest_sha256": original_request.get("canonical_manifest_sha256"),
        "original_processing_capability": original_request.get("processing_capability"),
        "original_route_id": original_request.get("route_id"),
        "original_destination": original_request.get("manifest_declared_destination"),
        "non_allow": dict(non_allow),
        "non_allow_sha256": canonical_sha256(dict(non_allow)),
    })


def fork_refusal(detail: str) -> dict[str, Any]:
    """Six-field FAIL_CLOSED for a fork that could not be built; the original non-ALLOW is unchanged."""
    return {
        "schema": FORK_SCHEMA,
        "disposition": "FAIL_CLOSED",
        "failure_code": "REMEDIATION_FORK_NOT_BUILT",
        "failed_predicate": "REMEDIATION_FORK_BINDS_THE_COMPLETE_ORIGINAL_REQUEST",
        "required_evidence_or_repair": "the original request as derive_execution_request produced it (" + detail + ")",
        "retry_entrypoint": "stegverse/remediation_fork.py::build_remediation_fork",
        "owning_existing_goal": OWNER_TASK_ID,
        "next_attempt": "admit the result against the complete original request",
        "remediation_manifest": None,
        "handoff": None,
        "original_disposition_unchanged": True,
        "authority_effect": "NONE_REFUSAL_ONLY",
    }


def build_remediation_fork(
    original_request: Mapping[str, Any],
    non_allow: Mapping[str, Any],
    organization_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Build the remediation manifest a non-ALLOW carries, and its hand-off; None when no fork applies.

    The Manifest Builder builds it; its route is the one it declares. The hand-off
    is a hand-off only: the receiving runtime transports it, and nothing here
    contacts a receiver or records a receipt.
    """
    if non_allow.get("disposition") not in NON_ALLOW:
        return None
    if original_request.get("processing_capability") == REMEDIATION_CAPABILITY:
        return None
    from .manifest_builder import build_manifest
    from .manifest_state_transition_runtime import build_intr_handoff, derive_execution_request

    request = fork_request(original_request, non_allow)
    manifest = build_manifest(
        process=REMEDIATION_CAPABILITY,
        processor_request=request,
        data={"original_request_sha256": request["original_request_sha256"],
              "non_allow_sha256": request["non_allow_sha256"],
              "external_side_effect": False},
        data_class="sv.sdk.remediation-fork.v1",
        source_framework="StegVerse-org/StegVerse-SDK",
        source_output_id="remediation:" + request["original_request_sha256"] + ":" + request["non_allow_sha256"],
        # Bound to the original, not to the clock: one non-ALLOW of one request is one
        # fork, so a replayed fork is the same manifest and is answered once.
        created_at=(original_request.get("canonical_manifest") or {}).get("created_at"),
        declared_intent="Classify this non-ALLOW for governed remediation; decide nothing",
        requested_consequence="Return a non-authorizing RESUBMIT or RE_MANIFEST classification",
        publisher_required=False,
    )
    remediation_request = derive_execution_request(manifest, organization_boundary)
    return {
        "schema": FORK_SCHEMA,
        "original_request_sha256": request["original_request_sha256"],
        "non_allow_sha256": request["non_allow_sha256"],
        "remediation_manifest": manifest,
        "remediation_request_sha256": remediation_request["request_sha256"],
        "route_id": remediation_request["route_id"],
        "handoff": build_intr_handoff(remediation_request),
        "original_disposition_unchanged": True,
        "authority_effect": "NONE_MANIFEST_HANDOFF_ONLY",
    }


__all__ = [
    "FORK_SCHEMA", "OWNER_TASK_ID", "REMEDIATION_CAPABILITY", "REQUEST_EXTENSION", "REQUEST_SCHEMA",
    "build_remediation_fork", "derive_state_graph", "fork_refusal", "fork_request",
    "validate_remediation_fork_request",
]
