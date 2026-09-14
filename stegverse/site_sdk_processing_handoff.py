"""Bind Site-to-SDK processing handoff packets to SDK manifest processing.

This module consumes the Site-emitted
``stegverse.site.sdk-processing-handoff/v1`` packet. It validates the handoff
without granting authority, then executes the admitted manifest through the
existing manifest-selected SDK route/runtime binding. It does not create a
MIR-specific processor, transport, Publisher path, egress path, or credential
path.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .governance_navigation import canonical_sha256
from .governance_ingress_runtime import external_manifest_to_public_request, run_external_manifest
from .manifest_contract import validate_ingress_manifest

SITE_SDK_PROCESSING_HANDOFF_SCHEMA = "stegverse.site.sdk-processing-handoff/v1"
SDK_HANDOFF_PROCESSING_RESULT_SCHEMA = "stegverse.sdk.site-processing-handoff-result/v1"
NEXT_TRANSITION = "EXECUTE_MANIFEST_SELECTED_SDK_PROCESSING_AFTER_EVALUATOR_INGRESS"
REQUIRED_SITE_STATE = "SDK_EVALUATOR_INGRESS_ADMITTED"
REQUIRED_NODE_TRANSITION = "EXTERNAL_COUNTERPART_RETURN_ADMITTED"
REQUIRED_RETURN_EXIT = "STEGVERSE_RETURN_EXIT"


class SiteSdkProcessingHandoffError(ValueError):
    pass


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise SiteSdkProcessingHandoffError(f"{label} must be an object")
    return deepcopy(dict(value))


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SiteSdkProcessingHandoffError(f"{label} is required")
    return value.strip()


def _normalize_sha256(value: Any, label: str) -> str:
    text = _require_text(value, label).lower()
    if text.startswith("sha256:"):
        text = text[7:]
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise SiteSdkProcessingHandoffError(f"{label} must be a sha256 digest")
    return text


def _verify_receipt(receipt: Mapping[str, Any], *, response_to: str, manifest_hash: str) -> dict[str, Any]:
    value = _require_mapping(receipt, "stegverse_return_exit_receipt")
    if value.get("transition_class") != REQUIRED_RETURN_EXIT:
        raise SiteSdkProcessingHandoffError("STEGVERSE_RETURN_EXIT receipt required")
    if _require_text(value.get("response_to"), "return receipt response_to") != response_to:
        raise SiteSdkProcessingHandoffError("return receipt response_to mismatch")
    if _normalize_sha256(value.get("manifest_sha256"), "return receipt manifest_sha256") != manifest_hash:
        raise SiteSdkProcessingHandoffError("return receipt manifest hash mismatch")
    if value.get("authority_effect") not in (None, "NONE", "NONE_ADMISSION_ONLY"):
        raise SiteSdkProcessingHandoffError("return receipt authority effect invalid")
    return value


def _verify_node_receipt(receipt: Any) -> dict[str, Any] | None:
    if receipt is None:
        return None
    value = _require_mapping(receipt, "node_transition_receipt")
    if value.get("transition") != REQUIRED_NODE_TRANSITION:
        raise SiteSdkProcessingHandoffError("Node EXTERNAL_COUNTERPART_RETURN_ADMITTED receipt required")
    if value.get("authority_effect") not in (None, "NONE", False):
        raise SiteSdkProcessingHandoffError("node transition authority effect invalid")
    return value


def validate_site_sdk_processing_handoff(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the Site handoff and return a canonical processing input.

    The returned value contains the admitted manifest object and the verified
    Site/Node receipts. Validation and route selection grant no authority.
    """
    handoff = _require_mapping(packet, "Site SDK processing handoff")
    if handoff.get("schema") != SITE_SDK_PROCESSING_HANDOFF_SCHEMA:
        raise SiteSdkProcessingHandoffError("Site SDK processing handoff schema invalid")
    if handoff.get("authority_effect") not in ("NONE", False):
        raise SiteSdkProcessingHandoffError("Site SDK processing handoff authority effect invalid")

    response_to = _require_text(handoff.get("response_to"), "response_to")
    retained_packet_sha256 = _normalize_sha256(
        handoff.get("retained_packet_sha256"), "retained_packet_sha256"
    )
    retained_packet_schema = _require_text(handoff.get("retained_packet_schema"), "retained_packet_schema")
    if retained_packet_schema != "stegverse.canonical-runtime-exact-return-packet/v1":
        raise SiteSdkProcessingHandoffError("retained packet schema invalid")

    if handoff.get("sdk_evaluator_ingress_state") != REQUIRED_SITE_STATE:
        raise SiteSdkProcessingHandoffError("SDK_EVALUATOR_INGRESS_ADMITTED state required")
    if handoff.get("next_required_transition") != NEXT_TRANSITION:
        raise SiteSdkProcessingHandoffError("manifest-selected SDK processing transition required")

    manifest = _require_mapping(handoff.get("manifest"), "manifest")
    canonical_manifest = validate_ingress_manifest(manifest)
    manifest_hash = _normalize_sha256(handoff.get("manifest_hash"), "manifest_hash")
    if manifest_hash != canonical_sha256(manifest):
        raise SiteSdkProcessingHandoffError("manifest_hash does not match supplied manifest")

    receipt = _verify_receipt(
        _require_mapping(handoff.get("stegverse_return_exit_receipt"), "stegverse_return_exit_receipt"),
        response_to=response_to,
        manifest_hash=manifest_hash,
    )
    node_receipt = _verify_node_receipt(handoff.get("node_transition_receipt"))

    return {
        "schema": SITE_SDK_PROCESSING_HANDOFF_SCHEMA,
        "manifest": canonical_manifest,
        "manifest_hash": manifest_hash,
        "response_to": response_to,
        "retained_packet_sha256": retained_packet_sha256,
        "retained_packet_schema": retained_packet_schema,
        "stegverse_return_exit_receipt": receipt,
        "sdk_evaluator_ingress_state": REQUIRED_SITE_STATE,
        "node_transition_receipt": node_receipt,
        "next_required_transition": NEXT_TRANSITION,
        "authority_effect": "NONE",
    }


def execute_site_sdk_processing_handoff(
    packet: Mapping[str, Any], *, custody_db: str, host_identity: str = "stegverse-sovereign-local"
) -> dict[str, Any]:
    """Execute the handoff's admitted manifest through the selected SDK route.

    This causes only the SDK-owned manifest-selected processing transition. It
    reports, but does not claim, later Publisher, SDK-return, egress, InTr egress,
    far-side final, or authentic external MIR substitution transitions.
    """
    handoff = validate_site_sdk_processing_handoff(packet)
    manifest = handoff["manifest"]
    request = external_manifest_to_public_request(manifest)
    result = run_external_manifest(manifest, custody_db=custody_db, host_identity=host_identity)
    completion = manifest.get("completion") or {}
    publisher = completion.get("publisher") if isinstance(completion, Mapping) else None
    publisher_required = bool(isinstance(publisher, Mapping) and publisher.get("required") is True)

    return {
        "schema": SDK_HANDOFF_PROCESSING_RESULT_SCHEMA,
        "state": "SDK_MANIFEST_SELECTED_PROCESSING_EXECUTED",
        "transition_class": NEXT_TRANSITION,
        "processing_capability": manifest["processing"]["capability"],
        "route_id": manifest["processing"]["route_id"],
        "request_id": request["request_id"],
        "manifest_hash": handoff["manifest_hash"],
        "response_to": handoff["response_to"],
        "retained_packet_sha256": handoff["retained_packet_sha256"],
        "stegverse_return_exit_receipt": deepcopy(handoff["stegverse_return_exit_receipt"]),
        "sdk_evaluator_ingress_state": handoff["sdk_evaluator_ingress_state"],
        "node_transition_receipt": deepcopy(handoff["node_transition_receipt"]),
        "processor_result": deepcopy(dict(result)),
        "processor_result_observed": True,
        "publisher_transition_required": publisher_required,
        "publisher_transition_observed": False,
        "sdk_return_binding_observed": False,
        "final_stegverse_side_egress_transition_observed": False,
        "interlock_intr_egress_observed": False,
        "far_side_transition_observed": False,
        "authentic_external_mir_endpoint_substitution_observed": False,
        "communication_complete": False,
        "authority_effect": "NONE",
    }


__all__ = [
    "SITE_SDK_PROCESSING_HANDOFF_SCHEMA",
    "SDK_HANDOFF_PROCESSING_RESULT_SCHEMA",
    "NEXT_TRANSITION",
    "SiteSdkProcessingHandoffError",
    "validate_site_sdk_processing_handoff",
    "execute_site_sdk_processing_handoff",
]
