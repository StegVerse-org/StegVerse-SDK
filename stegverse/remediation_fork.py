"""The remediation fork every non-ALLOW carries (NODE_INGRESS_SETTLED_SPECIFICATION §8).

Remediation is a manifest carried on the packet. When a result is not ALLOW,
the Manifest Builder builds a remediation manifest bound to that exact
non-ALLOW (lane ``stegverse.route.governed-remediation.v1`` / ``remediation``),
and it carries its own route, calculated from three things only: where the
need for remediation was recognized, the packet's current manifested path, and
the direct route from that point to StegHealer (``remediation_route``). The
lane enters at the nearest governed boundary on the manifested path and goes
directly to StegHealer from there; it never follows the rest of the original
path. The route is re-derived on every validation, so no caller can redirect it. The original packet keeps its
disposition and lineage unchanged and continues independently. Two lanes,
one fork, each with its own receipts.

A route-related non-ALLOW is recorded once, in the organization where it
happened. The manifest requires that record to be pushed to StegHealer
(``stegverse-labs.remediation``) over InTr on the route this module derives
(``remediation_route``). The originating organization requests no
classification, consumes no return, and makes no remediation decision.
StegHealer maps the error or failure against known errors and failures, then
either triggers a remediation task or returns the manifest and data packet to
the SDK. Those outcomes are recorded in StegHealer's organization.

The primary names are ``STEGHEALER["error_or_failure_map"]`` and
``STEGHEALTH_FAILURE_REMEDIATION_TASK_ID``. ``classifier`` and ``OWNER_TASK_ID``
remain deprecated aliases of those same values. The route record still carries
the key ``classifier`` because ``route_sha256`` covers it; removing that key
would change the hash of existing routes.

Nothing here classifies, decides, transports, records a receipt or grants
authority. A non-ALLOW of a remediation manifest does not fork again; it
stays the remediation lane's own non-ALLOW.
"""
from __future__ import annotations

import warnings
from copy import deepcopy
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .route_resolution import GOVERNED_REMEDIATION_ROUTE_ID, canonical_sha256, route_from_manifest

# The StegHealth task row derive_state_graph, fork_refusal, manifest_plan and
# governed_remediation read. The value is unchanged. OWNER_TASK_ID is the
# deprecated alias (see module __getattr__).
STEGHEALTH_FAILURE_REMEDIATION_TASK_ID = "STEGHEALTH-ECOSYSTEM-FAILURE-REMEDIATION-001"
REMEDIATION_CAPABILITY = "remediation"
REQUEST_EXTENSION = "stegverse_remediation_fork_request"
REQUEST_SCHEMA = "stegverse.remediation-fork-request/v1"
FORK_SCHEMA = "stegverse.sdk.remediation-fork/v1"
NON_ALLOW = ("DENY", "FAIL_CLOSED")

ROUTE_SCHEMA = "stegverse.remediation-route/v1"
# StegHealer maps the error or failure. The originating organization requests
# no classification. This is the intake the route names.
ERROR_OR_FAILURE_MAP = "app/manifest_remediation_intake.py::classify_sdk_deny"
_ERROR_OR_FAILURE_MAP_FIELD = "error_or_failure_map"
# Historical route-record key. route_sha256 covers this key, so the route
# record still emits it. It is a deprecated alias of error_or_failure_map.
_CLASSIFIER_FIELD = "classifier"


class _StegHealer(dict):
    """Primary field ``error_or_failure_map``; ``classifier`` is a deprecated alias.

    ``route_record`` is the object placed on the route and covered by
    ``route_sha256``. It keeps the historical key only, so existing route
    hashes stay byte-identical.
    """

    def __getitem__(self, key: str) -> Any:
        if key == _CLASSIFIER_FIELD:
            warnings.warn(
                "STEGHEALER['classifier'] is deprecated; use STEGHEALER['error_or_failure_map']",
                DeprecationWarning,
                stacklevel=2,
            )
            return ERROR_OR_FAILURE_MAP
        if key == _ERROR_OR_FAILURE_MAP_FIELD:
            return ERROR_OR_FAILURE_MAP
        return super().__getitem__(key)

    def get(self, key: str, default: Any = None) -> Any:
        if key == _CLASSIFIER_FIELD:
            warnings.warn(
                "STEGHEALER['classifier'] is deprecated; use STEGHEALER['error_or_failure_map']",
                DeprecationWarning,
                stacklevel=2,
            )
            return ERROR_OR_FAILURE_MAP
        if key == _ERROR_OR_FAILURE_MAP_FIELD:
            return ERROR_OR_FAILURE_MAP
        return super().get(key, default)

    def route_record(self) -> dict[str, str]:
        """The steghealer object hashed into ``route_sha256``.

        Historical key only. The value is the ``ERROR_OR_FAILURE_MAP`` constant.
        """
        return {
            "organization": super().__getitem__("organization"),
            "service_id": super().__getitem__("service_id"),
            "repository": super().__getitem__("repository"),
            "classifier": ERROR_OR_FAILURE_MAP,
        }


# StegHealer's one location: the StegVerse-Labs organization, service
# stegverse-labs.remediation (the address form organization_slug + "." +
# capability every organization answers at), served by StegVerse-Labs/StegVerse-Healer.
STEGHEALER = _StegHealer({
    "organization": "StegVerse-Labs",
    "service_id": "stegverse-labs.remediation",
    "repository": "StegVerse-Labs/StegVerse-Healer",
    _ERROR_OR_FAILURE_MAP_FIELD: ERROR_OR_FAILURE_MAP,
    # Deprecated alias of error_or_failure_map. Present so a copied mapping
    # still answers "classifier". The route record omits the new key.
    _CLASSIFIER_FIELD: ERROR_OR_FAILURE_MAP,
})

_DIGESTS = ("original_request_sha256", "original_wire_manifest_sha256", "original_canonical_manifest_sha256")
_FIELDS = frozenset({
    "schema", *_DIGESTS, "original_processing_capability", "original_route_id",
    "original_destination", "non_allow", "non_allow_sha256", "remediation_route", "original_request",
})


def recognition_location(non_allow: Mapping[str, Any], original_destination: Mapping[str, Any]) -> dict[str, Any]:
    """Where the need for remediation was recognized: the SDK, or the organization that returned the result."""
    boundary = non_allow.get("evaluation_boundary")
    if isinstance(boundary, str) and boundary.startswith("SDK_"):
        return {"node": "SDK", "organization": None, "evaluation_boundary": boundary}
    organization = non_allow.get("organization") or original_destination.get("organization")
    if not isinstance(organization, str) or not organization:
        raise ValueError("REMEDIATION_RECOGNITION_LOCATION_NOT_DETERMINABLE")
    return {"node": "ORGANIZATION", "organization": organization,
            "evaluation_boundary": boundary if isinstance(boundary, str) else None}


def _assert_intr_on_every_crossing(hops: list[Mapping[str, Any]]) -> None:
    """No hop crosses an organization boundary without InTr egress and ingress."""
    egress = {(h["from"], h["to"]) for h in hops if h["crossing"] == "INTERLOCK_INTR_EGRESS"}
    ingress = {(h["from"], h["to"]) for h in hops if h["crossing"] == "INTERLOCK_INTR_INGRESS"}
    for hop in hops:
        if hop["crossing"] not in ("INTERLOCK_INTR_EGRESS", "INTERLOCK_INTR_INGRESS", "INTERNAL_ENDPOINT"):
            raise ValueError("REMEDIATION_ROUTE_CROSSING_IS_NOT_INTERLOCK_INTR")
        if hop["crossing"] == "INTERLOCK_INTR_EGRESS" and (hop["from"], hop["to"]) not in ingress:
            raise ValueError("REMEDIATION_ROUTE_EGRESS_WITHOUT_INTR_INGRESS")
        if (hop["crossing"] == "INTERLOCK_INTR_INGRESS" and hop["from"] != "SDK"
                and (hop["from"], hop["to"]) not in egress):
            raise ValueError("REMEDIATION_ROUTE_INGRESS_WITHOUT_INTR_EGRESS")


def remediation_route(non_allow: Mapping[str, Any], *, original_route_id: str,
                      original_processing_capability: str, original_destination: Mapping[str, Any]) -> dict[str, Any]:
    """The remediation lane's route: recognition point, current manifested path, direct leg to StegHealer.

    The SDK transports nothing, so a need recognized in the SDK enters at the first
    governed boundary of the manifested path (its declared destination organization);
    a need recognized by an organization enters at that organization. From there the
    lane goes directly to StegHealer.
    """
    recognized = recognition_location(non_allow, original_destination)
    destination_organization = original_destination.get("organization")
    if not isinstance(destination_organization, str) or not destination_organization:
        raise ValueError("REMEDIATION_MANIFESTED_PATH_HAS_NO_DESTINATION_ORGANIZATION")
    entry = destination_organization if recognized["node"] == "SDK" else recognized["organization"]
    # Direct is the shortest path, never a bypass: every organization boundary on
    # it is crossed by InTr, egress at the sender and ingress at the receiver.
    hops = []
    if recognized["node"] == "SDK":
        hops.append({"from": "SDK", "to": entry, "crossing": "INTERLOCK_INTR_INGRESS"})
    if entry != STEGHEALER["organization"]:
        hops.append({"from": entry, "to": STEGHEALER["organization"], "crossing": "INTERLOCK_INTR_EGRESS"})
        hops.append({"from": entry, "to": STEGHEALER["organization"], "crossing": "INTERLOCK_INTR_INGRESS"})
    hops.append({"from": STEGHEALER["organization"], "to": STEGHEALER["service_id"], "crossing": "INTERNAL_ENDPOINT"})
    _assert_intr_on_every_crossing(hops)
    route = {
        "schema": ROUTE_SCHEMA,
        "recognized_at": recognized,
        "manifested_path": {
            "route_id": original_route_id,
            "processing_capability": original_processing_capability,
            "destination_organization": destination_organization,
            "destination_service": (original_destination.get("receiving_operation") or {}).get("addressed_service"),
        },
        "entry_organization": entry,
        "direct_route_to_steghealer": hops,
        "steghealer": STEGHEALER.route_record(),
        "follows_remaining_manifested_path": False,
    }
    route["route_sha256"] = canonical_sha256(route)
    return route


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
    # StegHealer binds the whole original request document, not only its digests,
    # so the lane carries it; every identity it repeats must be the bound one.
    original = value.get("original_request")
    if not isinstance(original, Mapping):
        raise ValueError("original_request is required")
    if original_wire_manifest_sha256(original) != value["original_wire_manifest_sha256"]:
        raise ValueError("REMEDIATION_FORK_ORIGINAL_REQUEST_MISMATCH:wire_manifest_sha256")
    for field, key in (("original_request_sha256", "request_sha256"),
                       ("original_canonical_manifest_sha256", "canonical_manifest_sha256"),
                       ("original_processing_capability", "processing_capability"),
                       ("original_route_id", "route_id"),
                       ("original_destination", "manifest_declared_destination")):
        if original.get(key) != value[field]:
            raise ValueError("REMEDIATION_FORK_ORIGINAL_REQUEST_MISMATCH:" + key)
    expected = remediation_route(non_allow, original_route_id=value["original_route_id"],
                                 original_processing_capability=value["original_processing_capability"],
                                 original_destination=value["original_destination"])
    if value.get("remediation_route") != expected:
        raise ValueError("REMEDIATION_ROUTE_IS_NOT_THE_CALCULATED_ROUTE")
    return deepcopy(dict(value))


def derive_state_graph(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Request graph for the remediation lane; mapping the error or failure belongs to StegHealer."""
    canonical = validate_ingress_manifest(manifest)
    route = route_from_manifest(canonical)
    if route.get("route_id") != GOVERNED_REMEDIATION_ROUTE_ID:
        raise ValueError("REMEDIATION_MANIFEST_ROUTE_MISMATCH")
    if (canonical.get("processing") or {}).get("capability") != REMEDIATION_CAPABILITY:
        raise ValueError("manifest processing capability does not select remediation")
    request = validate_remediation_fork_request((canonical.get("extensions") or {}).get(REQUEST_EXTENSION))
    return {
        "schema": "stegverse.sdk.installed-state-transition-graph/v1",
        "graph_id": f"{STEGHEALTH_FAILURE_REMEDIATION_TASK_ID}:REMEDIATION:{request['original_request_sha256']}:{request['non_allow_sha256']}",
        "canonical_task_id": None,
        "owner_task_id": STEGHEALTH_FAILURE_REMEDIATION_TASK_ID,
        "processing_capability": REMEDIATION_CAPABILITY,
        "route_id": GOVERNED_REMEDIATION_ROUTE_ID,
        "request": request,
        "ordered_transitions": [],
        "ordered_transitions_source": "RECEIVING_ORGANIZATION_MANIFEST_INGRESS",
        "remediation_route": request["remediation_route"],
        "classification_authority": STEGHEALER["repository"],
        "classification_receipt_class": "REMEDIATION_CLASSIFIED",
        "classification_grants_authority": False,
        "requires_workercoordinator_claim_fence": False,
        "predecessor_closure_required": True,
        "adapter_executes_lifecycle": False,
        "authority_effect": "NONE_GRAPH_DERIVATION_ONLY",
    }


def original_wire_manifest_sha256(request: Mapping[str, Any]) -> str:
    """Wire identity of an original request.

    Requests derived before SDK #323 carry no wire_manifest_sha256 field; their
    wire identity is the digest of the canonical_manifest they hold (53a6749).
    """
    declared = request.get("wire_manifest_sha256")
    if isinstance(declared, str) and declared:
        return declared
    original = request.get("canonical_manifest")
    if not isinstance(original, Mapping):
        raise ValueError("REMEDIATION_REQUEST_WIRE_IDENTITY_REQUIRED")
    return canonical_sha256(dict(original))


def fork_request(original_request: Mapping[str, Any], non_allow: Mapping[str, Any]) -> dict[str, Any]:
    """The remediation request bound to one original request and one of its non-ALLOW results."""
    destination = original_request.get("manifest_declared_destination")
    if not isinstance(destination, Mapping):
        raise ValueError("original_destination is required")
    return validate_remediation_fork_request({
        "remediation_route": remediation_route(
            non_allow, original_route_id=str(original_request.get("route_id") or ""),
            original_processing_capability=str(original_request.get("processing_capability") or ""),
            original_destination=destination),
        "schema": REQUEST_SCHEMA,
        "original_request_sha256": original_request.get("request_sha256"),
        "original_wire_manifest_sha256": original_wire_manifest_sha256(original_request),
        "original_canonical_manifest_sha256": original_request.get("canonical_manifest_sha256"),
        "original_processing_capability": original_request.get("processing_capability"),
        "original_route_id": original_request.get("route_id"),
        "original_destination": original_request.get("manifest_declared_destination"),
        "non_allow": dict(non_allow),
        "non_allow_sha256": canonical_sha256(dict(non_allow)),
        "original_request": dict(original_request),
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
        "owning_existing_goal": STEGHEALTH_FAILURE_REMEDIATION_TASK_ID,
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

    The Manifest Builder builds it; its route is calculated (``remediation_route``). The hand-off
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
    entry = request["remediation_route"]["entry_organization"]
    if (remediation_request.get("manifest_declared_destination") or {}).get("organization") != entry:
        # The lane is handed to the boundary its calculated route enters at, or not at all.
        raise ValueError("REMEDIATION_HANDOFF_IS_NOT_AT_THE_CALCULATED_ENTRY:" + str(entry))
    return {
        "schema": FORK_SCHEMA,
        "original_request_sha256": request["original_request_sha256"],
        "non_allow_sha256": request["non_allow_sha256"],
        "remediation_manifest": manifest,
        "remediation_request_sha256": remediation_request["request_sha256"],
        "route_id": remediation_request["route_id"],
        "remediation_route": request["remediation_route"],
        "handoff": build_intr_handoff(remediation_request),
        "original_disposition_unchanged": True,
        "authority_effect": "NONE_MANIFEST_HANDOFF_ONLY",
    }


def __getattr__(name: str) -> Any:
    """Deprecated compatibility aliases. The primary names are the constants above."""
    if name == "OWNER_TASK_ID":
        warnings.warn(
            "OWNER_TASK_ID is deprecated; use STEGHEALTH_FAILURE_REMEDIATION_TASK_ID",
            DeprecationWarning,
            stacklevel=2,
        )
        return STEGHEALTH_FAILURE_REMEDIATION_TASK_ID
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ERROR_OR_FAILURE_MAP", "FORK_SCHEMA", "ROUTE_SCHEMA", "STEGHEALER",
    "STEGHEALTH_FAILURE_REMEDIATION_TASK_ID", "recognition_location", "remediation_route",
    "REMEDIATION_CAPABILITY", "REQUEST_EXTENSION", "REQUEST_SCHEMA",
    "build_remediation_fork", "derive_state_graph", "fork_refusal", "fork_request",
    "validate_remediation_fork_request",
]
