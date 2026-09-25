"""Actionable SDK boundary diagnostics for attempted manifested transitions.

These are local evaluation reports, never InTr governance receipts. An uncalled
resident cannot be represented as a downstream DENY. The normal SDK runtime and
its existing TV/TVC, InTr and Master Records boundaries remain unchanged.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .manifest_state_transition_runtime import (
    _post_existing_intr, derive_execution_request, validate_runtime_result,
)


def _hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


_ATTACHMENT_REMEDIATION = {
    "UNIVERSAL_INTR_INGRESS_NOT_CONFIGURED": (
        "intr.endpoint.configured/v1", "Install the existing admitted InTr ingress URL",
    ),
    "TV_TVC_RELAY_AUTHORIZATION_REQUIRED": (
        "tvc.relay.authorization.present/v1", "Resolve the existing TV/TVC scoped relay authorization",
    ),
}


def _local_diagnostic(
    manifest: Mapping[str, Any], request: Mapping[str, Any] | None,
    boundary: str, failure_code: str, failed_predicate: str, repair: str,
    disposition: str = "DENY", response_hash: str | None = None,
) -> dict[str, Any]:
    manifest_digest = _hash(dict(manifest))
    report = {
        "schema": "stegverse.sdk.local-transition-diagnostic/v1",
        "evidence_class": "ATTEMPTED_INGRESS",
        "diagnostic_only": True,
        "is_intr_receipt": False,
        "is_master_records_receipt": False,
        "consequence_committed": False,
        "manifest_sha256": manifest_digest,
        "canonical_manifest_sha256": request.get("canonical_manifest_sha256") if request else None,
        "canonical_task_id": request.get("canonical_task_id") if request else None,
        "graph_id": request.get("graph_id") if request else None,
        "processing_capability": request.get("processing_capability") if request else None,
        "route_id": request.get("route_id") if request else None,
        "boundary": boundary,
        "disposition": disposition,
        "failure_code": failure_code,
        "failed_predicate": failed_predicate,
        "required_evidence_or_repair": repair,
        "retry_entrypoint": "sdk.attempt_manifest_transition",
        "response_sha256": response_hash,
        "next_attempt": "Repair this exact boundary and retry the same manifest",
    }
    report["diagnostic_sha256"] = _hash(report)
    return report


def attempt_manifest_transition(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Attempt existing SDK -> InTr and return a specific boundary diagnosis.

    Authentic success returns the existing validated runtime result unchanged.
    Only SDK-local non-entry or response-validation errors become diagnostic
    non-ALLOW reports. No diagnostic is an admitted InTr or Master Records receipt.
    """
    if not isinstance(manifest, Mapping):
        raise TypeError("manifest must be a mapping")
    try:
        request = derive_execution_request(manifest)
    except ValueError as exc:
        return _local_diagnostic(
            manifest, None, "SDK_MANIFEST_ADMISSION", "SDK_MANIFEST_ADMISSION_REJECTED",
            "sdk.manifest.valid-and-installed-route/v1", str(exc),
        )
    try:
        result = _post_existing_intr(request)
    except ValueError as exc:
        message = str(exc)
        code = message.split(":", 1)[0]
        if code in _ATTACHMENT_REMEDIATION:
            predicate, repair = _ATTACHMENT_REMEDIATION[code]
            return _local_diagnostic(
                manifest, request, "SDK_TO_INTR_ATTACHMENT", code, predicate, repair
            )
        return _local_diagnostic(
            manifest, request, "SDK_TO_INTR_TRANSPORT", code,
            "sdk.intr.transport.response/v1", message, "FAIL_CLOSED",
        )
    try:
        return validate_runtime_result(result, request)
    except ValueError as exc:
        return _local_diagnostic(
            manifest, request, "SDK_INTR_RESULT_ACCEPTANCE", str(exc).split(":", 1)[0],
            "sdk.intr.result.binding-and-custody/v1", str(exc),
            "FAIL_CLOSED", response_hash=_hash(result),
        )
