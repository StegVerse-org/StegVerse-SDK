"""Bind exact Publisher artifact returns to complete SDK communication manifests.

This module owns SDK caller-return assembly only. It does not invoke Publisher,
LLM Adapter, Interlock/InTr, or a far-side transition and grants no authority.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
from typing import Any, Mapping

from .governance_navigation import RECEIPT_ID_RE
from .manifest_contract import validate_ingress_manifest

PUBLISHER_RETURN_SCHEMA = "stegverse.publisher.artifact-return/v1"
SDK_RETURN_BINDING_SCHEMA = "stegverse.sdk.publisher-return-binding/v1"
READY_STATE = "READY_FOR_FINAL_STEGVERSE_EGRESS_TRANSITION"


class PublisherReturnBindingError(ValueError):
    pass


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _sha256_value(value: Any) -> str:
    return _sha256_bytes(_canonical_json(value).encode("utf-8"))


def verify_publisher_return(return_bytes: bytes) -> dict[str, Any]:
    """Verify Publisher's exact-byte non-authorizing artifact-return envelope."""
    if not isinstance(return_bytes, bytes) or not return_bytes:
        raise PublisherReturnBindingError("exact Publisher return bytes required")
    try:
        value = json.loads(return_bytes.decode("utf-8"))
    except Exception as exc:
        raise PublisherReturnBindingError("Publisher return JSON invalid") from exc
    if not isinstance(value, dict):
        raise PublisherReturnBindingError("Publisher return must be an object")
    if _canonical_json(value).encode("utf-8") != return_bytes:
        raise PublisherReturnBindingError("Publisher return bytes are not canonical JSON")
    if value.get("schema") != PUBLISHER_RETURN_SCHEMA:
        raise PublisherReturnBindingError("Publisher return schema invalid")
    if value.get("authority_effect") != "NONE":
        raise PublisherReturnBindingError("Publisher return authority effect invalid")
    if any(value.get(key) is not False for key in (
        "publication_authorized", "release_authorized", "execution_authorized"
    )):
        raise PublisherReturnBindingError("Publisher return attempts authority expansion")

    required_strings = (
        "transfer_id", "source_export_id", "source_export_sha256", "generation_id"
    )
    for key in required_strings:
        if not isinstance(value.get(key), str) or not value[key]:
            raise PublisherReturnBindingError(f"Publisher return {key} required")

    manifest = value.get("manifest")
    if not isinstance(manifest, dict):
        raise PublisherReturnBindingError("Publisher artifact manifest missing")
    manifest_artifacts = manifest.get("artifacts")
    if not isinstance(manifest_artifacts, list):
        raise PublisherReturnBindingError("Publisher artifact manifest entries missing")
    by_path = {
        item.get("path"): item
        for item in manifest_artifacts
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }

    artifacts = value.get("artifacts")
    if not isinstance(artifacts, list):
        raise PublisherReturnBindingError("Publisher artifacts missing")
    for item in artifacts:
        if not isinstance(item, dict):
            raise PublisherReturnBindingError("Publisher artifact entry invalid")
        try:
            raw = base64.b64decode(item["content_base64"], validate=True)
        except Exception as exc:
            raise PublisherReturnBindingError("Publisher artifact base64 invalid") from exc
        if _sha256_bytes(raw) != item.get("sha256"):
            raise PublisherReturnBindingError("Publisher artifact digest mismatch")
        if len(raw) != item.get("bytes"):
            raise PublisherReturnBindingError("Publisher artifact length mismatch")
        manifest_item = by_path.get(item.get("path"))
        if not isinstance(manifest_item, dict) or manifest_item.get("sha256") != item.get("sha256"):
            raise PublisherReturnBindingError("Publisher artifact manifest binding mismatch")
    return copy.deepcopy(value)


def assemble_publisher_return(
    *,
    manifest: Mapping[str, Any],
    manifest_receipt_id: str,
    publisher_return_bytes: bytes,
) -> dict[str, Any]:
    """Bind Publisher output to the original complete manifest and initiator.

    The returned object is ready for the manifest-declared final StegVerse-side
    egress transition. It deliberately does not claim that transition, InTr egress,
    a far-side transition, or terminal communication completion occurred.
    """
    normalized_manifest = copy.deepcopy(dict(manifest))
    validate_ingress_manifest(normalized_manifest)
    completion = normalized_manifest.get("completion")
    if not isinstance(completion, Mapping):
        raise PublisherReturnBindingError("complete manifest completion block required")
    if completion.get("direction") != "SOUTH":
        raise PublisherReturnBindingError("completion.direction must be SOUTH")

    initiator = completion.get("initiator")
    publisher = completion.get("publisher")
    egress = completion.get("egress")
    if not isinstance(initiator, Mapping):
        raise PublisherReturnBindingError("completion.initiator required")
    if not isinstance(publisher, Mapping) or publisher.get("stage") != "PUBLISHER" or publisher.get("required") is not True:
        raise PublisherReturnBindingError("manifest must require Publisher stage")
    if not isinstance(egress, Mapping):
        raise PublisherReturnBindingError("completion.egress required")
    if egress.get("transport") != "INTERLOCK_INTR" or egress.get("far_side_transition_required") is not True:
        raise PublisherReturnBindingError("complete governed InTr egress contract required")
    surface = egress.get("final_stegverse_transition_surface")
    if not isinstance(surface, str) or not surface.strip():
        raise PublisherReturnBindingError("final StegVerse transition surface required")

    rid = str(manifest_receipt_id or "").strip().upper()
    if not RECEIPT_ID_RE.fullmatch(rid):
        raise PublisherReturnBindingError("valid manifest_receipt_id required")

    publisher_return = verify_publisher_return(publisher_return_bytes)
    projection = copy.deepcopy(normalized_manifest.get("return_projection") or {"mode": "NONE", "transition_classes": []})
    artifact_bindings = [
        {
            "format": item.get("format"),
            "path": item.get("path"),
            "sha256": item.get("sha256"),
            "bytes": item.get("bytes"),
        }
        for item in publisher_return["artifacts"]
    ]

    result = {
        "schema": SDK_RETURN_BINDING_SCHEMA,
        "direction": "SOUTH",
        "manifest_receipt_id": rid,
        "original_manifest_sha256": _sha256_value(normalized_manifest),
        "initiator": copy.deepcopy(dict(initiator)),
        "return_projection": projection,
        "publisher": {
            "declared_package_profile": publisher.get("package_profile"),
            "return_schema": publisher_return["schema"],
            "transfer_id": publisher_return["transfer_id"],
            "generation_id": publisher_return["generation_id"],
            "source_export_id": publisher_return["source_export_id"],
            "source_export_sha256": publisher_return["source_export_sha256"],
            "return_sha256": _sha256_bytes(publisher_return_bytes),
            "artifact_bindings": artifact_bindings,
        },
        "egress": copy.deepcopy(dict(egress)),
        "communication_state": READY_STATE,
        "final_stegverse_transition_observed": False,
        "interlock_intr_egress_observed": False,
        "far_side_transition_observed": False,
        "communication_complete": False,
        "authority_effect": "NONE",
    }
    result["binding_sha256"] = _sha256_value(result)
    return result


def verify_publisher_return_binding(value: Mapping[str, Any]) -> dict[str, Any]:
    """Verify deterministic SDK return binding without promoting completion."""
    result = copy.deepcopy(dict(value))
    if result.get("schema") != SDK_RETURN_BINDING_SCHEMA:
        raise PublisherReturnBindingError("SDK Publisher return binding schema invalid")
    supplied = result.pop("binding_sha256", None)
    if supplied != _sha256_value(result):
        raise PublisherReturnBindingError("SDK Publisher return binding digest mismatch")
    if result.get("authority_effect") != "NONE":
        raise PublisherReturnBindingError("SDK Publisher return binding authority effect invalid")
    if result.get("communication_state") != READY_STATE:
        raise PublisherReturnBindingError("SDK Publisher return binding state invalid")
    if any(result.get(key) is not False for key in (
        "final_stegverse_transition_observed",
        "interlock_intr_egress_observed",
        "far_side_transition_observed",
        "communication_complete",
    )):
        raise PublisherReturnBindingError("SDK return binding cannot claim downstream transitions")
    result["binding_sha256"] = supplied
    return result
