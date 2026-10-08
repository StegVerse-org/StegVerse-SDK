"""Generic SDK manifest adapter for the StegBrowser LLM interaction profile.

StegBrowser is the capability; llm.v1 is the profile. This module validates and
projects a manifest-selected Test-5-style request into the existing Universal
InTr state-transition runtime. It does not execute a browser, call a provider,
mint receipts, or create a Test-5-specific executor.
"""
from __future__ import annotations
from copy import deepcopy
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .route_resolution import route_from_manifest

PROCESSING_CAPABILITY = "stegbrowser"
PROFILE = "llm.v1"
REQUEST_EXTENSION = "stegverse_stegbrowser_request"
REQUEST_SCHEMA = "stegbrowser.llm-profile-request.v1"
JOURNEY_SCHEMA = "stegverse.packet-carried-endpoint-receipt-journey/v1"
JOURNEY_SCHEMA_V2 = "stegverse.packet-carried-endpoint-receipt-journey/v2"
JOURNEY_SCHEMAS = (JOURNEY_SCHEMA, JOURNEY_SCHEMA_V2)
ROUTE_ID = "stegverse.route.stegbrowser.v1"

#: Fields a branch may override. Anything absent falls back to the request-level
#: value, so a single-branch journey is byte-identical to the v1 shape.
BRANCH_OVERRIDES = ("prompt", "response_marker", "provider", "model", "secure_url")


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _branch(value: Any, index: int) -> dict[str, Any]:
    """Normalize one parallel round trip: origin -> ephemeral -> origin."""
    if not isinstance(value, Mapping):
        raise ValueError(f"journey branch {index} must be an object")
    outbound = _text(value.get("outbound_manifest_sha256"), f"branch {index} outbound_manifest_sha256")
    returned = _text(value.get("return_manifest_sha256"), f"branch {index} return_manifest_sha256")
    predecessor = _text(
        value.get("return_predecessor_manifest_sha256"),
        f"branch {index} return_predecessor_manifest_sha256",
    )
    if predecessor != outbound:
        raise ValueError(f"branch {index} return manifest must predecessor-link to its outbound manifest")
    if returned == outbound:
        raise ValueError(f"branch {index} return manifest must be distinct from its outbound manifest")
    branch: dict[str, Any] = {
        "branch_id": _text(value.get("branch_id", str(index)), f"branch {index} branch_id"),
        "ephemeral_endpoint": _text(value.get("ephemeral_endpoint"), f"branch {index} ephemeral_endpoint"),
        "outbound_manifest_sha256": outbound,
        "return_manifest_sha256": returned,
        "return_predecessor_manifest_sha256": predecessor,
    }
    for field in BRANCH_OVERRIDES:
        if value.get(field) is not None:
            branch[field] = _text(value.get(field), f"branch {index} {field}")
    actions = value.get("browser_actions")
    if actions is not None:
        if not isinstance(actions, list) or not actions or not all(isinstance(x, Mapping) for x in actions):
            raise ValueError(f"branch {index} browser_actions must be a non-empty object list when supplied")
        branch["browser_actions"] = [dict(x) for x in actions]
    return branch


def _normalized_journey(journey: Any) -> dict[str, Any]:
    """Accept a v1 single round trip or a v2 fan, and return the v2 shape.

    The packet carries the endpoint receipts, so the journey is what replay
    depends on. A v1 journey normalizes to exactly one branch: an existing
    single-worker request keeps its meaning and its receipt order unchanged,
    and a fan is the same structure with more branches rather than a second
    schema to reconcile at replay time.
    """
    if not isinstance(journey, Mapping) or journey.get("schema") not in JOURNEY_SCHEMAS:
        raise ValueError(f"journey schema must be one of {', '.join(JOURNEY_SCHEMAS)}")
    journey_id = _text(journey.get("journey_id"), "journey_id")
    origin = _text(journey.get("origin_endpoint"), "origin_endpoint")

    if journey.get("schema") == JOURNEY_SCHEMA:
        if journey.get("branches") is not None:
            raise ValueError("a v1 journey carries one round trip and declares no branches")
        supplied = [dict(journey, branch_id=journey.get("branch_id", "1"))]
    else:
        supplied = journey.get("branches")
        if not isinstance(supplied, list) or not supplied:
            raise ValueError("a v2 journey requires a non-empty branches array")

    branches = [_branch(entry, index) for index, entry in enumerate(supplied, start=1)]
    for field, label in (
        ("branch_id", "branch ids"),
        ("ephemeral_endpoint", "ephemeral endpoints"),
        ("outbound_manifest_sha256", "outbound manifests"),
    ):
        values = [b[field] for b in branches]
        if len(set(values)) != len(values):
            raise ValueError(f"journey {label} must be distinct across branches")
    # A shared marker would let one branch's response satisfy another's receipt.
    markers = [b["response_marker"] for b in branches if "response_marker" in b]
    if len(set(markers)) != len(markers):
        raise ValueError("journey response markers must be distinct across branches")
    return {
        "schema": JOURNEY_SCHEMA_V2,
        "journey_id": journey_id,
        "origin_endpoint": origin,
        "branch_count": len(branches),
        "branches": branches,
    }


def validate_stegbrowser_request(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(value, Mapping) or value.get("schema") != REQUEST_SCHEMA:
        raise ValueError(f"StegBrowser request schema must be {REQUEST_SCHEMA}")
    if value.get("profile") != PROFILE:
        raise ValueError(f"StegBrowser profile must be {PROFILE}")
    journey = _normalized_journey(value.get("journey"))
    normalized_journey = journey
    provider = value.get("provider")
    if provider is not None:
        provider = _text(provider, "provider")
    secure_url = value.get("secure_url")
    if secure_url is not None:
        secure_url = _text(secure_url, "secure_url")
        if not secure_url.startswith("https://"):
            raise ValueError("StegBrowser llm.v1 secure_url must use https")
    model = value.get("model")
    if model is not None:
        model = _text(model, "model")
    actions = value.get("browser_actions")
    if actions is not None and (not isinstance(actions, list) or not actions or not all(isinstance(x, Mapping) for x in actions)):
        raise ValueError("StegBrowser llm.v1 browser_actions must be a non-empty object list when supplied")
    return {
        "schema": REQUEST_SCHEMA,
        "profile": PROFILE,
        "prompt": _text(value.get("prompt"), "prompt"),
        "response_marker": _text(value.get("response_marker"), "response_marker"),
        "provider": provider,
        "model": model,
        "secure_url": secure_url,
        "browser_actions": ([dict(x) for x in actions] if actions is not None else None),
        "journey": normalized_journey,
    }


def _resolved_branch(request: Mapping[str, Any], branch: Mapping[str, Any]) -> dict[str, Any]:
    """A branch's effective interaction: its own overrides over request defaults."""
    resolved = {
        "branch_id": branch["branch_id"],
        "ephemeral_endpoint": branch["ephemeral_endpoint"],
        "outbound_manifest_sha256": branch["outbound_manifest_sha256"],
        "return_manifest_sha256": branch["return_manifest_sha256"],
    }
    for field in BRANCH_OVERRIDES:
        resolved[field] = branch.get(field, request.get(field))
    resolved["browser_actions"] = branch.get("browser_actions", request.get("browser_actions"))
    return resolved


def _required_receipt_order(journey: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Four endpoint receipts per branch, in the order the packet must carry them.

    Each branch is one round trip - origin EGRESS, ephemeral INGRESS, ephemeral
    EGRESS on the predecessor-linked return manifest, origin INGRESS - so a fan
    of N branches requires 4N receipts and no branch can borrow another's.
    """
    order: list[dict[str, Any]] = []
    for branch in journey["branches"]:
        for leg in (1, 2):
            for direction in ("EGRESS", "INGRESS"):
                order.append({
                    "branch_id": branch["branch_id"],
                    "leg": leg,
                    "direction": direction,
                })
    return order


def derive_state_graph(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    route = route_from_manifest(canonical)
    if route.get("route_id") != ROUTE_ID or route.get("processor_capability") != PROCESSING_CAPABILITY:
        raise ValueError("manifest is not bound to installed StegBrowser capability")
    extensions = canonical.get("extensions")
    request = validate_stegbrowser_request(
        extensions.get(REQUEST_EXTENSION) if isinstance(extensions, Mapping) else None
    )
    journey = request["journey"]
    return {
        "schema": "stegverse.sdk.stegbrowser-state-graph/v1",
        "graph_id": f"stegbrowser:{journey['journey_id']}",
        "canonical_task_id": "EPHEMERAL-STEGBROWSER-EXTERNAL-AI-ACTIVATION-001",
        "requires_workercoordinator_claim_fence": True,
        "adapter_executes_lifecycle": False,
        "capability": "StegBrowser",
        "profile": PROFILE,
        "request": deepcopy(request),
        "ordered_transitions": [
            "INGRESS_ADMITTED",
            "STEGBROWSER_LEASE_ADMITTED",
            "LLM_PROFILE_INTERACTION",
            "EGRESS_ADMITTED",
            "ORGANIZATION_RECORDED",
            "MASTER_RECORDS_RECONSTRUCTED",
        ],
        "branch_count": journey["branch_count"],
        "branches": [_resolved_branch(request, branch) for branch in journey["branches"]],
        "endpoint_receipt_journey": {
            "journey_id": journey["journey_id"],
            "branch_count": journey["branch_count"],
            "required_order": _required_receipt_order(journey),
            "record_order": ["ORGANIZATION_RECORDS", "MASTER_RECORDS"],
        },
        "authority_effect": "NONE_GRAPH_DERIVATION_ONLY",
    }


__all__ = [
    "BRANCH_OVERRIDES", "JOURNEY_SCHEMA", "JOURNEY_SCHEMAS", "JOURNEY_SCHEMA_V2",
    "PROCESSING_CAPABILITY", "PROFILE", "REQUEST_EXTENSION", "REQUEST_SCHEMA",
    "ROUTE_ID", "derive_state_graph", "validate_stegbrowser_request",
]
