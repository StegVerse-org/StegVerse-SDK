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
SDK_COMPLETION_CAPSULE_PROFILE = "stegverse.sdk.downstream-completion-capsule/v1"
MIR_ROUNDTRIP_BINDING_PROFILE = "stegverse.publisher.mir-roundtrip-binding/v1"
MIR_ROUNDTRIP_GOAL_TASK_ID = "MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001"
MIR_ROUNDTRIP_COSV_ID = "50000000100000"
READY_STATE = "READY_FOR_FINAL_STEGVERSE_EGRESS_TRANSITION"
POST_PUBLISHER_FALSE_FLAGS = (
    "sdk_return_binding_observed",
    "final_stegverse_side_egress_transition_observed",
    "interlock_intr_egress_observed",
    "far_side_transition_observed",
    "authentic_external_mir_endpoint_substitution_observed",
    "communication_complete",
)


class PublisherReturnBindingError(ValueError):
    pass


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _sha256_value(value: Any) -> str:
    return _sha256_bytes(_canonical_json(value).encode("utf-8"))


def _normalize_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PublisherReturnBindingError(f"{label} required")
    text = value.strip().lower()
    if text.startswith("sha256:"):
        text = text[7:]
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise PublisherReturnBindingError(f"{label} must be a sha256 digest")
    return text


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise PublisherReturnBindingError(f"{label} must be an object")
    return copy.deepcopy(dict(value))


def _validate_mir_roundtrip_continuity(
    *,
    manifest: Mapping[str, Any],
    publisher_return: Mapping[str, Any],
    downstream_completion_capsule: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    """Require exact Publisher PR #71 continuity when a MIR binding is returned."""
    raw_binding = publisher_return.get("roundtrip_binding")
    if raw_binding is None and downstream_completion_capsule is None:
        return None
    if raw_binding is None:
        raise PublisherReturnBindingError("Publisher MIR round-trip binding required")
    if downstream_completion_capsule is None:
        raise PublisherReturnBindingError("original SDK downstream completion capsule required")

    binding = _require_mapping(raw_binding, "Publisher MIR round-trip binding")
    capsule = _require_mapping(downstream_completion_capsule, "original SDK downstream completion capsule")
    carried_capsule = _require_mapping(
        binding.get("downstream_completion_capsule"), "Publisher carried downstream completion capsule"
    )

    if binding.get("profile") != MIR_ROUNDTRIP_BINDING_PROFILE:
        raise PublisherReturnBindingError("Publisher MIR round-trip binding profile invalid")
    if binding.get("goal_task_id") != MIR_ROUNDTRIP_GOAL_TASK_ID:
        raise PublisherReturnBindingError("Publisher MIR round-trip Goal Task binding invalid")
    if str(binding.get("cosv_id")) != MIR_ROUNDTRIP_COSV_ID:
        raise PublisherReturnBindingError("Publisher MIR round-trip COSV binding invalid")
    if binding.get("publisher_transition") != "PUBLISHER_ARTIFACT_RETURN_PRODUCED":
        raise PublisherReturnBindingError("Publisher MIR transition binding invalid")
    if binding.get("publisher_transition_observed") is not True:
        raise PublisherReturnBindingError("Publisher MIR transition must be observed")
    if binding.get("authority_effect") != "NONE":
        raise PublisherReturnBindingError("Publisher MIR round-trip authority effect invalid")
    for field in POST_PUBLISHER_FALSE_FLAGS:
        if binding.get(field) is not False:
            raise PublisherReturnBindingError(f"Publisher MIR return must keep {field}=false")

    if capsule.get("profile") != SDK_COMPLETION_CAPSULE_PROFILE:
        raise PublisherReturnBindingError("original SDK completion capsule profile invalid")
    if capsule.get("authority_effect") != "NONE":
        raise PublisherReturnBindingError("original SDK completion capsule authority effect invalid")
    if carried_capsule != capsule:
        raise PublisherReturnBindingError("Publisher carried completion capsule does not exactly match original SDK capsule")

    completion = manifest.get("completion")
    if not isinstance(completion, Mapping):
        raise PublisherReturnBindingError("original manifest completion block required for MIR continuity")
    expected_manifest_hash = _normalize_sha256(_sha256_value(manifest), "computed manifest hash")
    expected_completion_hash = _normalize_sha256(_sha256_value(dict(completion)), "computed completion hash")
    capsule_manifest_hash = _normalize_sha256(capsule.get("manifest_hash"), "SDK capsule manifest_hash")
    capsule_completion_hash = _normalize_sha256(capsule.get("completion_hash"), "SDK capsule completion_hash")
    retained_packet_sha256 = _normalize_sha256(
        capsule.get("retained_packet_sha256"), "SDK capsule retained_packet_sha256"
    )
    response_to = capsule.get("response_to")
    if not isinstance(response_to, str) or not response_to.strip():
        raise PublisherReturnBindingError("SDK capsule response_to required")
    if capsule_manifest_hash != expected_manifest_hash:
        raise PublisherReturnBindingError("SDK capsule manifest hash does not match original manifest")
    if capsule_completion_hash != expected_completion_hash:
        raise PublisherReturnBindingError("SDK capsule completion hash does not match original manifest completion")
    if capsule.get("completion") != dict(completion):
        raise PublisherReturnBindingError("SDK capsule completion does not exactly match original manifest completion")

    if _normalize_sha256(binding.get("manifest_hash"), "MIR binding manifest_hash") != capsule_manifest_hash:
        raise PublisherReturnBindingError("MIR binding manifest hash mismatch")
    if _normalize_sha256(binding.get("completion_hash"), "MIR binding completion_hash") != capsule_completion_hash:
        raise PublisherReturnBindingError("MIR binding completion hash mismatch")
    if binding.get("response_to") != response_to:
        raise PublisherReturnBindingError("MIR binding response_to mismatch")
    if _normalize_sha256(
        binding.get("retained_packet_sha256"), "MIR binding retained_packet_sha256"
    ) != retained_packet_sha256:
        raise PublisherReturnBindingError("MIR binding retained packet hash mismatch")

    sdk_state = _require_mapping(binding.get("sdk_processor_state"), "Publisher carried SDK processor state")
    if sdk_state.get("state") != "SDK_MANIFEST_SELECTED_PROCESSING_EXECUTED":
        raise PublisherReturnBindingError("Publisher carried SDK processor state invalid")
    if sdk_state.get("processor_result_observed") is not True:
        raise PublisherReturnBindingError("Publisher carried SDK processor result must be observed")

    artifact_manifest = _require_mapping(publisher_return.get("manifest"), "Publisher artifact manifest")
    identity_pairs = (
        ("publisher_return_schema", publisher_return.get("schema"), "Publisher return schema binding mismatch"),
        ("publisher_return_source_export_id", publisher_return.get("source_export_id"), "Publisher source export id binding mismatch"),
        ("publisher_return_source_export_sha256", publisher_return.get("source_export_sha256"), "Publisher source export hash binding mismatch"),
        ("publisher_return_generation_id", publisher_return.get("generation_id"), "Publisher generation binding mismatch"),
        ("publisher_artifact_manifest_sha256", artifact_manifest.get("manifest_sha256"), "Publisher artifact manifest binding mismatch"),
    )
    for key, expected, error in identity_pairs:
        if binding.get(key) != expected:
            raise PublisherReturnBindingError(error)

    return binding


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
    source_export_schema = value.get("source_export_schema")
    if source_export_schema is not None:
        if source_export_schema != "stegverse.publisher.evidence-report-package/v1":
            raise PublisherReturnBindingError("unsupported Publisher source export schema")
        actual_manifest_hash = _sha256_value({k:v for k,v in manifest.items() if k != "manifest_sha256"})
        if manifest.get("manifest_sha256") != actual_manifest_hash:
            raise PublisherReturnBindingError("generic review artifact manifest digest mismatch")
        receipt = value.get("rendering_receipt")
        if not isinstance(receipt, dict) or receipt.get("manifest_sha256") != actual_manifest_hash:
            raise PublisherReturnBindingError("generic review rendering receipt manifest mismatch")
        if receipt.get("receipt_sha256") != _sha256_value(
            {k:v for k,v in receipt.items() if k != "receipt_sha256"}
        ):
            raise PublisherReturnBindingError("generic review rendering receipt digest mismatch")
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
    if source_export_schema is not None:
        manifest_paths=[i.get("path") for i in manifest_artifacts if isinstance(i,dict)]
        return_paths=[i.get("path") for i in artifacts if isinstance(i,dict)]
        if (len(manifest_paths)!=len(manifest_artifacts)
            or len(return_paths)!=len(artifacts)
            or len(manifest_paths)!=len(set(manifest_paths))
            or len(return_paths)!=len(set(return_paths))
            or set(manifest_paths)!=set(return_paths)):
            raise PublisherReturnBindingError("generic review source original coverage mismatch")

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
        if source_export_schema is not None:
            if (manifest_item.get("bytes")!=item.get("bytes")
                or manifest_item.get("format")!=item.get("format")):
                raise PublisherReturnBindingError("generic review artifact manifest metadata mismatch")
            if manifest_item.get("format")=="source-original" and (
                manifest_item.get("media_type")!=item.get("media_type")
                or manifest_item.get("source_class")!=item.get("source_class")
            ):
                raise PublisherReturnBindingError("generic review source provenance mismatch")
    return copy.deepcopy(value)


def assemble_publisher_return(
    *,
    manifest: Mapping[str, Any],
    manifest_receipt_id: str,
    publisher_return_bytes: bytes,
    downstream_completion_capsule: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Bind Publisher output to the original complete manifest and initiator.

    When Publisher carries the MIR PR #71 round-trip binding, the original SDK
    completion capsule is mandatory and must match exactly. The returned object
    is ready for the manifest-declared final StegVerse-side egress transition.
    It deliberately does not claim that transition, InTr egress, a far-side
    transition, authentic MIR substitution, or terminal communication completion.
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
    mir_binding = _validate_mir_roundtrip_continuity(
        manifest=normalized_manifest,
        publisher_return=publisher_return,
        downstream_completion_capsule=downstream_completion_capsule,
    )
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
        "publisher_transition_observed": mir_binding is not None,
        "sdk_return_binding_observed": True,
        "final_stegverse_transition_observed": False,
        "interlock_intr_egress_observed": False,
        "far_side_transition_observed": False,
        "authentic_external_mir_endpoint_substitution_observed": False,
        "communication_complete": False,
        "authority_effect": "NONE",
    }
    if mir_binding is not None:
        result["mir_roundtrip"] = {
            "profile": mir_binding["profile"],
            "goal_task_id": mir_binding["goal_task_id"],
            "cosv_id": str(mir_binding["cosv_id"]),
            "manifest_hash": mir_binding["manifest_hash"],
            "completion_hash": mir_binding["completion_hash"],
            "response_to": mir_binding["response_to"],
            "retained_packet_sha256": mir_binding["retained_packet_sha256"],
            "publisher_roundtrip_binding_sha256": _sha256_value(mir_binding),
            "downstream_completion_capsule_sha256": _sha256_value(downstream_completion_capsule),
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
    if result.get("sdk_return_binding_observed") is not True:
        raise PublisherReturnBindingError("SDK Publisher return binding observation missing")
    if any(result.get(key) is not False for key in (
        "final_stegverse_transition_observed",
        "interlock_intr_egress_observed",
        "far_side_transition_observed",
        "authentic_external_mir_endpoint_substitution_observed",
        "communication_complete",
    )):
        raise PublisherReturnBindingError("SDK return binding cannot claim downstream transitions")
    result["binding_sha256"] = supplied
    return result
