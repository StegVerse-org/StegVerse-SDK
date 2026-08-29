"""Admitted browser evaluator-review ingress for canonical Interlock + InTr paths.

This module does not implement transport, credentials, authority, or receipts. It
accepts requests after the receiving StegVerse Interlock runtime has transported
and admitted them, validates the browser/SDK contract, and delegates execution to
existing SDK test-client surfaces. Canonical governance remains owned by StegCore.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

REQUEST_SCHEMA = "stegverse.evaluator_review.interlock_request.v1"
REQUEST_CLASS = "EVALUATOR_REVIEW"
TRANSPORT = "InTr"
EXECUTE_OPERATION = "EXECUTE"
SUPPORTED_SURFACES = frozenset({"manifold-governance"})


class EvaluatorReviewInTrError(RuntimeError):
    """Fail-closed evaluator-review ingress error."""


@dataclass(frozen=True)
class AdmittedEvaluatorReviewRequest:
    operation: str
    authority_ref: str
    test_id: str | None
    revision: int | None
    manifest_hash: str | None
    payload: Mapping[str, Any]


def _required_text(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise EvaluatorReviewInTrError(f"{name} is required")
    return text


def _optional_hash(value: Any, name: str) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise EvaluatorReviewInTrError(f"{name} must be 64 lowercase hex characters")
    return text


def admit_evaluator_review_request(request: Mapping[str, Any]) -> AdmittedEvaluatorReviewRequest:
    """Validate a request already delivered by a canonical Interlock/InTr runtime.

    Transport proof is intentionally not minted or inferred here. The receiving
    Interlock runtime owns InTr receipt verification before calling this function.
    """
    if not isinstance(request, Mapping):
        raise EvaluatorReviewInTrError("request must be an object")
    if request.get("schema_version") != REQUEST_SCHEMA:
        raise EvaluatorReviewInTrError(f"unsupported request schema; expected {REQUEST_SCHEMA}")
    if request.get("request_class") != REQUEST_CLASS:
        raise EvaluatorReviewInTrError("unsupported request class")
    if request.get("transport") != TRANSPORT:
        raise EvaluatorReviewInTrError("canonical InTr transport declaration is required")
    if request.get("authority_transfer") is not False:
        raise EvaluatorReviewInTrError("authority transfer is prohibited")

    operation = _required_text(request.get("operation"), "operation")
    authority_ref = _required_text(request.get("authority_ref"), "authority_ref")
    payload = request.get("payload") or {}
    bindings = request.get("bindings") or {}
    if not isinstance(payload, Mapping):
        raise EvaluatorReviewInTrError("payload must be an object")
    if not isinstance(bindings, Mapping):
        raise EvaluatorReviewInTrError("bindings must be an object")

    test_id = bindings.get("test_id")
    if test_id is not None:
        test_id = _required_text(test_id, "bindings.test_id")
    revision = bindings.get("revision")
    if revision is not None:
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
            raise EvaluatorReviewInTrError("bindings.revision must be a non-negative integer")
    manifest_hash = _optional_hash(bindings.get("manifest_hash"), "bindings.manifest_hash")

    payload_test_id = payload.get("testId")
    if test_id is not None and payload_test_id is not None and str(payload_test_id) != test_id:
        raise EvaluatorReviewInTrError("payload testId does not match bound test_id")
    payload_revision = payload.get("revision")
    if revision is not None and payload_revision is not None and payload_revision != revision:
        raise EvaluatorReviewInTrError("payload revision does not match bound revision")
    payload_hash = payload.get("manifestHash")
    if manifest_hash is not None and payload_hash is not None and payload_hash != manifest_hash:
        raise EvaluatorReviewInTrError("payload manifestHash does not match bound manifest_hash")

    return AdmittedEvaluatorReviewRequest(
        operation=operation,
        authority_ref=authority_ref,
        test_id=test_id,
        revision=revision,
        manifest_hash=manifest_hash,
        payload=dict(payload),
    )


def execute_admitted_demo_test(request: Mapping[str, Any]) -> dict[str, Any]:
    """Execute an admitted browser test through an existing SDK client surface."""
    admitted = admit_evaluator_review_request(request)
    if admitted.operation != EXECUTE_OPERATION:
        raise EvaluatorReviewInTrError("EXECUTE operation required")

    surface = _required_text(admitted.payload.get("surface"), "payload.surface")
    if surface not in SUPPORTED_SURFACES:
        raise EvaluatorReviewInTrError(f"unsupported SDK demo/test surface: {surface}")
    packet = admitted.payload.get("packet")
    if not isinstance(packet, Mapping):
        raise EvaluatorReviewInTrError("payload.packet must be an object")

    if surface == "manifold-governance":
        from .manifold_governance import evaluate_manifold_governance

        result = evaluate_manifold_governance(packet)
    else:  # pragma: no cover - guarded by SUPPORTED_SURFACES
        raise EvaluatorReviewInTrError(f"unsupported SDK demo/test surface: {surface}")

    return {
        "schema": "stegverse.sdk.evaluator_review_execution.v1",
        "sdk_role": "ADMITTED_DEMO_TEST_CLIENT",
        "source_transport": TRANSPORT,
        "authority_ref": admitted.authority_ref,
        "authority_transfer": False,
        "sdk_grants_authority": False,
        "sdk_mints_intr_receipt": False,
        "test_id": admitted.test_id,
        "revision": admitted.revision,
        "manifest_hash": admitted.manifest_hash,
        "surface": surface,
        "result": result,
    }


__all__ = [
    "REQUEST_SCHEMA",
    "REQUEST_CLASS",
    "TRANSPORT",
    "SUPPORTED_SURFACES",
    "EvaluatorReviewInTrError",
    "AdmittedEvaluatorReviewRequest",
    "admit_evaluator_review_request",
    "execute_admitted_demo_test",
]
