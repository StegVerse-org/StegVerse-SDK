"""Translate TVC-owned provider result evidence into SDK active-probe evidence.

The SDK does not issue TVC leases, obtain provider credentials, exchange OAuth
codes, or execute provider operations here. A runtime integration supplies an
already-produced, secret-free TVC result. This bridge validates that result and
projects only non-authorizing current-evidence fields into the canonical active
probe result consumed by WorkSpace readiness logic.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .active_probe_execution import ACTIVE_PROBE_RESULT_PROFILE

TVC_PERSONAL_KV_GOOGLE_DRIVE_RESULT_SCHEMA = (
    "stegverse.tvc.personal-kv-google-drive-materialization-result/v1"
)
TVC_WORKSPACE_GOOGLE_DRIVE_RESULT_SCHEMA = (
    "stegverse.tvc.workspace-google-drive-probe-result/v1"
)
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
    if not isinstance(request_hash, str) or not request_hash.startswith("sha256:") or len(request_hash) != 71:
        raise ValueError("TVC request_sha256 invalid")
    if not isinstance(binding_id, str) or not binding_id.startswith("kvpb_"):
        raise ValueError("TVC binding_id invalid")
    if not isinstance(receipt_hash, str) or not receipt_hash.startswith("sha256:") or len(receipt_hash) != 71:
        raise ValueError("TVC lease receipt hash invalid")
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
    if not isinstance(request_hash, str) or not request_hash.startswith("sha256:") or len(request_hash) != 71:
        raise ValueError("TVC WorkSpace request_sha256 invalid")
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
    raise ValueError("unsupported TVC Google Drive result schema")


def google_drive_probe_result_from_tvc(
    *,
    reason: str,
    tvc_result: Mapping[str, Any],
    observed_at: str,
    applicability: str | None = None,
) -> dict[str, Any]:
    """Project an already-produced TVC result into active-probe evidence.

    The existence of a valid TVC result proves only the specific provider operation
    represented by that result. The caller still supplies the exact active-probe
    reason being answered; active-probe execution separately verifies exact reason
    binding. `applicability` is accepted only for an applicability probe.
    """
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("probe reason required")
    if not isinstance(observed_at, str) or not observed_at.strip():
        raise ValueError("observed_at required")
    validated = validate_google_drive_tvc_result(tvc_result)
    probe = {
        "profile": ACTIVE_PROBE_RESULT_PROFILE,
        "reason": reason.strip(),
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
    if reason.endswith(":applicability_unknown"):
        if applicability not in {"APPLICABLE", "NOT_APPLICABLE"}:
            raise ValueError("applicability probe requires resolved applicability")
        probe["applicability"] = applicability
    elif applicability is not None:
        raise ValueError("applicability may only be supplied for applicability probe reasons")
    return probe


__all__ = [
    "TVC_PERSONAL_KV_GOOGLE_DRIVE_RESULT_SCHEMA",
    "TVC_WORKSPACE_GOOGLE_DRIVE_RESULT_SCHEMA",
    "WORKSPACE_SCOPE",
    "google_drive_probe_result_from_tvc",
    "validate_google_drive_tvc_result",
]
