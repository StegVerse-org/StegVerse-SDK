"""Translate TVC-owned provider result evidence into SDK active-probe evidence.

The SDK does not issue TVC leases, obtain provider credentials, exchange OAuth
codes, or execute provider operations here. A runtime integration supplies an
already-produced, secret-free TVC result. This bridge validates that result and
projects only non-authorizing current-evidence fields into the canonical active
probe result consumed by WorkSpace readiness logic.
"""
from __future__ import annotations

import hashlib
from copy import deepcopy
from typing import Any, Mapping

from .active_probe_execution import ACTIVE_PROBE_RESULT_PROFILE

TVC_PERSONAL_KV_GOOGLE_DRIVE_RESULT_SCHEMA = (
    "stegverse.tvc.personal-kv-google-drive-materialization-result/v1"
)
TVC_WORKSPACE_GOOGLE_DRIVE_RESULT_SCHEMA = (
    "stegverse.tvc.workspace-google-drive-probe-result/v1"
)
TVC_EXTERNAL_COLLAB_GOOGLE_DRIVE_RESULT_SCHEMA = (
    "stegverse.tvc.external-collaboration-google-drive-probe-result/v1"
)
TVC_EXTERNAL_COLLAB_BROKER_RESULT_SCHEMA = (
    "stegverse.tvc.google-drive-external-collaboration-metadata-probe/v1"
)
EXTERNAL_COLLAB_CREDENTIAL_CLASS = "TVC-EXTERNAL-COLLAB-GOOGLE-DRIVE-OWNER-SESSION-001"
EXTERNAL_COLLAB_CREDENTIAL_PURPOSE = "EXTERNAL_COLLABORATIVE_RESOURCE_READ_ONLY"
WORKSPACE_SCOPE = ["_System/Workspace/**"]

_PROTECTED_MARKERS = (
    "access_token",
    "refresh_token",
    "client_secret",
    "api_key",
    "authorization",
    "bearer",
    "password",
    "credential_value",
    "secret_value",
)


def _reject_protected(value: Any, path: str = "tvc_result") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if any(marker in normalized for marker in _PROTECTED_MARKERS):
                raise ValueError(f"protected TVC result field prohibited: {path}.{key}")
            _reject_protected(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_protected(child, f"{path}[{index}]")
    elif isinstance(value, str):
        lowered = value.lower().strip()
        if lowered.startswith(("bearer ", "ya29.", "1//")):
            raise ValueError(f"protected TVC result value prohibited: {path}")


def _digest_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71:
        raise ValueError(f"{label} invalid")
    return value


def _validate_common_result(result: Mapping[str, Any]) -> None:
    if result.get("provider") != "GOOGLE_DRIVE":
        raise ValueError("TVC Google Drive provider identity mismatch")
    if result.get("credential_authority") != "TV/TVC":
        raise ValueError("TVC credential authority mismatch")
    if result.get("credential_material_exported") is not False:
        raise ValueError("credential material export prohibited")
    if result.get("provider_operation_authority_transferred") is not False:
        raise ValueError("provider operation authority transfer prohibited")
    if result.get("runtime_activation_claimed") is not False:
        raise ValueError("source bridge cannot accept runtime activation claim")
    if result.get("authority_effect") != "NONE_RESULT_EVIDENCE_ONLY":
        raise ValueError("TVC result must remain evidence-only")


def _validate_personal_kv_result(result: Mapping[str, Any]) -> dict[str, Any]:
    _validate_common_result(result)
    request_id = result.get("request_id")
    request_hash = result.get("request_sha256")
    binding_id = result.get("binding_id")
    receipt_hash = result.get("lease_receipt_sha256")
    if not isinstance(request_id, str) or len(request_id) < 16:
        raise ValueError("TVC request_id invalid")
    _require_sha256(request_hash, "TVC request_sha256")
    if not isinstance(binding_id, str) or not binding_id.startswith("kvpb_"):
        raise ValueError("TVC binding_id invalid")
    _require_sha256(receipt_hash, "TVC lease receipt hash")
    broker = result.get("broker_response")
    if not isinstance(broker, Mapping) or broker.get("decision") != "ALLOW_OPERATION_RESULT":
        raise ValueError("TVC broker result not allowed")
    return {
        "request_id": request_id,
        "request_sha256": request_hash,
        "binding_id": binding_id,
        "lease_receipt_sha256": receipt_hash,
        "source": "StegVerse-Labs/TVC:personal-kv-google-drive-materialization",
        "source_schema": TVC_PERSONAL_KV_GOOGLE_DRIVE_RESULT_SCHEMA,
    }


def _validate_workspace_result(result: Mapping[str, Any]) -> dict[str, Any]:
    _validate_common_result(result)
    if result.get("workspace_scope") != WORKSPACE_SCOPE:
        raise ValueError("TVC WorkSpace result scope mismatch")
    if result.get("delegated_operation") != "personal_kv_materialize":
        raise ValueError("TVC WorkSpace delegated operation mismatch")
    if result.get("provider_mutation_performed") is not False:
        raise ValueError("TVC WorkSpace provider mutation prohibited")
    delegated = result.get("delegated_result")
    if not isinstance(delegated, Mapping):
        raise ValueError("TVC WorkSpace delegated result required")
    if delegated.get("schema") != TVC_PERSONAL_KV_GOOGLE_DRIVE_RESULT_SCHEMA:
        raise ValueError("TVC WorkSpace delegated result schema invalid")
    normalized = _validate_personal_kv_result(delegated)
    request_id = result.get("request_id")
    request_hash = result.get("request_sha256")
    binding_id = result.get("binding_id")
    if not isinstance(request_id, str) or len(request_id) < 16:
        raise ValueError("TVC WorkSpace request_id invalid")
    _require_sha256(request_hash, "TVC WorkSpace request_sha256")
    if binding_id != normalized["binding_id"]:
        raise ValueError("TVC WorkSpace binding mismatch")
    return {
        "request_id": request_id,
        "request_sha256": request_hash,
        "binding_id": binding_id,
        "lease_receipt_sha256": normalized["lease_receipt_sha256"],
        "source": "StegVerse-Labs/TVC:workspace-google-drive-probe",
        "source_schema": TVC_WORKSPACE_GOOGLE_DRIVE_RESULT_SCHEMA,
    }


def _validate_external_collaboration_result(result: Mapping[str, Any]) -> dict[str, Any]:
    _validate_common_result(result)
    request_id = result.get("request_id")
    request_hash = result.get("request_sha256")
    binding_id = result.get("binding_id")
    provider_file_id = result.get("provider_file_id")
    probe_reason_sha256 = result.get("probe_reason_sha256")
    lease_receipt_sha256 = result.get("lease_receipt_sha256")
    if not isinstance(request_id, str) or len(request_id) < 16:
        raise ValueError("TVC external collaboration request_id invalid")
    _require_sha256(request_hash, "TVC external collaboration request_sha256")
    _require_sha256(probe_reason_sha256, "TVC external collaboration probe reason hash")
    _require_sha256(lease_receipt_sha256, "TVC external collaboration lease receipt hash")
    if not isinstance(binding_id, str) or not binding_id.startswith("wsprobe_"):
        raise ValueError("TVC external collaboration binding_id invalid")
    if not isinstance(provider_file_id, str) or not 3 <= len(provider_file_id) <= 256:
        raise ValueError("TVC external collaboration provider file id invalid")
    if result.get("credential_class") != EXTERNAL_COLLAB_CREDENTIAL_CLASS:
        raise ValueError("TVC external collaboration credential class mismatch")
    if result.get("credential_purpose") != EXTERNAL_COLLAB_CREDENTIAL_PURPOSE:
        raise ValueError("TVC external collaboration credential purpose mismatch")
    if result.get("readiness_assigned") is not False:
        raise ValueError("TVC external collaboration result may not assign readiness")

    observation = result.get("provider_observation")
    if not isinstance(observation, Mapping) or observation.get("schema") != TVC_EXTERNAL_COLLAB_BROKER_RESULT_SCHEMA:
        raise ValueError("TVC external collaboration provider observation invalid")
    if observation.get("binding_id") != binding_id or observation.get("provider_file_id") != provider_file_id:
        raise ValueError("TVC external collaboration provider observation binding mismatch")
    if observation.get("credential_class") != EXTERNAL_COLLAB_CREDENTIAL_CLASS or observation.get("credential_purpose") != EXTERNAL_COLLAB_CREDENTIAL_PURPOSE:
        raise ValueError("TVC external collaboration provider observation credential mismatch")
    if observation.get("probe_reason_sha256") != probe_reason_sha256:
        raise ValueError("TVC external collaboration provider observation reason mismatch")
    if observation.get("metadata_only") is not True or observation.get("read_only") is not True:
        raise ValueError("TVC external collaboration provider observation posture invalid")
    if observation.get("provider_mutation_performed") is not False or observation.get("credential_material_returned") is not False:
        raise ValueError("TVC external collaboration provider observation authority drift")
    if observation.get("readiness_assigned") is not False:
        raise ValueError("TVC external collaboration provider observation may not assign readiness")
    _require_sha256(result.get("provider_observation_sha256"), "TVC external collaboration provider observation hash")

    broker_receipt = result.get("broker_use_receipt")
    if not isinstance(broker_receipt, Mapping) or broker_receipt.get("decision") != "ALLOW_OPERATION_RESULT":
        raise ValueError("TVC external collaboration broker use receipt invalid")
    if broker_receipt.get("single_use_consumed") is not True:
        raise ValueError("TVC external collaboration broker lease not consumed")
    if broker_receipt.get("durable_replay_recorded") is not True or broker_receipt.get("durable_replay_consumed_before_provider_call") is not True:
        raise ValueError("TVC external collaboration durable replay evidence required")
    if broker_receipt.get("secret_material_returned") is not False:
        raise ValueError("TVC external collaboration broker secret return prohibited")

    return {
        "request_id": request_id,
        "request_sha256": request_hash,
        "binding_id": binding_id,
        "provider_file_id": provider_file_id,
        "probe_reason_sha256": probe_reason_sha256,
        "lease_receipt_sha256": lease_receipt_sha256,
        "source": "StegVerse-Labs/TVC:external-collaboration-google-drive-probe",
        "source_schema": TVC_EXTERNAL_COLLAB_GOOGLE_DRIVE_RESULT_SCHEMA,
    }


def validate_google_drive_tvc_result(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("TVC provider result must be an object")
    result = deepcopy(dict(value))
    _reject_protected(result)
    schema = result.get("schema")
    if schema == TVC_PERSONAL_KV_GOOGLE_DRIVE_RESULT_SCHEMA:
        return _validate_personal_kv_result(result)
    if schema == TVC_WORKSPACE_GOOGLE_DRIVE_RESULT_SCHEMA:
        return _validate_workspace_result(result)
    if schema == TVC_EXTERNAL_COLLAB_GOOGLE_DRIVE_RESULT_SCHEMA:
        return _validate_external_collaboration_result(result)
    raise ValueError("unsupported TVC Google Drive result schema")


def google_drive_probe_result_from_tvc(
    *,
    reason: str,
    tvc_result: Mapping[str, Any],
    observed_at: str,
    applicability: str | None = None,
) -> dict[str, Any]:
    """Project an already-produced TVC result into active-probe evidence.

    A valid TVC result proves only the specific provider operation represented by
    that result. The active-probe engine remains the component that derives any
    readiness transition after exact reason binding and complete predicate review.
    """
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("probe reason required")
    if not isinstance(observed_at, str) or not observed_at.strip():
        raise ValueError("observed_at required")
    normalized_reason = reason.strip()
    validated = validate_google_drive_tvc_result(tvc_result)
    expected_reason_hash = validated.get("probe_reason_sha256")
    if expected_reason_hash is not None and expected_reason_hash != _digest_text(normalized_reason):
        raise ValueError("TVC external collaboration probe reason does not match active-probe reason")
    probe = {
        "profile": ACTIVE_PROBE_RESULT_PROFILE,
        "reason": normalized_reason,
        "outcome": "SATISFIED",
        "observed_at": observed_at.strip(),
        "evidence_ref": (
            f"tvc:google-drive:{validated['request_id']}:"
            f"{validated['lease_receipt_sha256']}"
        ),
        "source": validated["source"],
        "source_schema": validated["source_schema"],
        "provider": "google_drive",
        "provider_request_sha256": validated["request_sha256"],
        "provider_binding_id": validated["binding_id"],
        "credential_authority": "TV/TVC",
        "credential_material_exported": False,
        "provider_operation_authority_transferred": False,
        "authority_effect": "NONE",
    }
    if "provider_file_id" in validated:
        probe["provider_file_id"] = validated["provider_file_id"]
        probe["provider_probe_reason_sha256"] = validated["probe_reason_sha256"]
        probe["durable_replay_required"] = True
    if normalized_reason.endswith(":applicability_unknown"):
        if applicability not in {"APPLICABLE", "NOT_APPLICABLE"}:
            raise ValueError("applicability probe requires resolved applicability")
        probe["applicability"] = applicability
    elif applicability is not None:
        raise ValueError("applicability may only be supplied for applicability probe reasons")
    return probe


__all__ = [
    "TVC_PERSONAL_KV_GOOGLE_DRIVE_RESULT_SCHEMA",
    "TVC_WORKSPACE_GOOGLE_DRIVE_RESULT_SCHEMA",
    "TVC_EXTERNAL_COLLAB_GOOGLE_DRIVE_RESULT_SCHEMA",
    "TVC_EXTERNAL_COLLAB_BROKER_RESULT_SCHEMA",
    "WORKSPACE_SCOPE",
    "google_drive_probe_result_from_tvc",
    "validate_google_drive_tvc_result",
]
