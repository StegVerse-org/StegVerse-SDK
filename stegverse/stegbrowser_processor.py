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
ROUTE_ID = "stegverse.route.stegbrowser.v1"


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def validate_stegbrowser_request(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(value, Mapping) or value.get("schema") != REQUEST_SCHEMA:
        raise ValueError(f"StegBrowser request schema must be {REQUEST_SCHEMA}")
    if value.get("profile") != PROFILE:
        raise ValueError(f"StegBrowser profile must be {PROFILE}")
    journey = value.get("journey")
    if not isinstance(journey, Mapping) or journey.get("schema") != JOURNEY_SCHEMA:
        raise ValueError(f"journey schema must be {JOURNEY_SCHEMA}")
    normalized_journey = {
        "schema": JOURNEY_SCHEMA,
        "journey_id": _text(journey.get("journey_id"), "journey_id"),
        "origin_endpoint": _text(journey.get("origin_endpoint"), "origin_endpoint"),
        "ephemeral_endpoint": _text(journey.get("ephemeral_endpoint"), "ephemeral_endpoint"),
        "outbound_manifest_sha256": _text(journey.get("outbound_manifest_sha256"), "outbound_manifest_sha256"),
        "return_manifest_sha256": _text(journey.get("return_manifest_sha256"), "return_manifest_sha256"),
        "return_predecessor_manifest_sha256": _text(
            journey.get("return_predecessor_manifest_sha256"), "return_predecessor_manifest_sha256"
        ),
    }
    if normalized_journey["return_predecessor_manifest_sha256"] != normalized_journey["outbound_manifest_sha256"]:
        raise ValueError("return manifest must predecessor-link to outbound manifest")
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
        "endpoint_receipt_journey": {
            "journey_id": journey["journey_id"],
            "required_order": [
                {"leg": 1, "direction": "EGRESS"},
                {"leg": 1, "direction": "INGRESS"},
                {"leg": 2, "direction": "EGRESS"},
                {"leg": 2, "direction": "INGRESS"},
            ],
            "custody_order": ["ORGANIZATION_RECORDS", "MASTER_RECORDS"],
        },
        "authority_effect": "NONE_GRAPH_DERIVATION_ONLY",
    }


__all__ = [
    "JOURNEY_SCHEMA", "PROCESSING_CAPABILITY", "PROFILE", "REQUEST_EXTENSION",
    "REQUEST_SCHEMA", "ROUTE_ID", "derive_state_graph", "validate_stegbrowser_request",
]
