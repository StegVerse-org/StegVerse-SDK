from __future__ import annotations

from unittest.mock import patch

import pytest

from stegverse.evaluator_review_intr import (
    EvaluatorReviewInTrError,
    REQUEST_SCHEMA,
    admit_evaluator_review_request,
    execute_admitted_demo_test,
)


def request(**overrides):
    payload = {
        "schema_version": REQUEST_SCHEMA,
        "request_class": "EVALUATOR_REVIEW",
        "operation": "APPROVE",
        "authority_ref": "opaque-authority-ref",
        "transport": "InTr",
        "payload": {"testId": "t1", "revision": 4, "manifestHash": "a" * 64},
        "bindings": {"test_id": "t1", "revision": 4, "manifest_hash": "a" * 64},
        "authority_transfer": False,
    }
    payload.update(overrides)
    return payload


def test_admits_exact_bound_intr_request():
    admitted = admit_evaluator_review_request(request())
    assert admitted.operation == "APPROVE"
    assert admitted.authority_ref == "opaque-authority-ref"
    assert admitted.test_id == "t1"
    assert admitted.revision == 4
    assert admitted.manifest_hash == "a" * 64


def test_rejects_non_intr_transport():
    with pytest.raises(EvaluatorReviewInTrError, match="InTr"):
        admit_evaluator_review_request(request(transport="HTTP_DIRECT"))


def test_rejects_authority_transfer():
    with pytest.raises(EvaluatorReviewInTrError, match="authority transfer"):
        admit_evaluator_review_request(request(authority_transfer=True))


def test_rejects_binding_mismatch():
    bad = request()
    bad["payload"] = dict(bad["payload"], revision=5)
    with pytest.raises(EvaluatorReviewInTrError, match="revision"):
        admit_evaluator_review_request(bad)


def test_rejects_invalid_manifest_hash():
    bad = request()
    bad["bindings"] = dict(bad["bindings"], manifest_hash="not-a-hash")
    with pytest.raises(EvaluatorReviewInTrError, match="64 lowercase hex"):
        admit_evaluator_review_request(bad)


def test_executes_current_basis_through_existing_sdk_surface():
    calls = []

    def fake_evaluate(packet):
        calls.append(packet)
        return {"schema": "stegverse.sdk-current-basis-result.v1", "result": {"ok": True}}

    value = request(
        operation="EXECUTE",
        payload={
            "testId": "cross-framework-current-basis-001",
            "revision": 4,
            "manifestHash": "a" * 64,
            "surface": "current-basis",
            "packet": {"schema": "stegverse.sdk-current-basis-test.v1"},
        },
        bindings={
            "test_id": "cross-framework-current-basis-001",
            "revision": 4,
            "manifest_hash": "a" * 64,
        },
    )
    with patch("stegverse.current_basis.evaluate_current_basis", side_effect=fake_evaluate):
        result = execute_admitted_demo_test(value)
    assert result["surface"] == "current-basis"
    assert result["sdk_grants_authority"] is False
    assert result["sdk_mints_intr_receipt"] is False
    assert result["result"]["result"]["ok"] is True
    assert calls == [{"schema": "stegverse.sdk-current-basis-test.v1"}]
