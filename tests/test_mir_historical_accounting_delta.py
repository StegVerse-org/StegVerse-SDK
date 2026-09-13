from __future__ import annotations

import hashlib
import json

import pytest

from stegverse.mir_historical_accounting_delta import (
    MirHistoricalAccountingDeltaError,
    evaluate_mir_historical_accounting_delta,
)


def _sha(value):
    return "sha256:" + hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _fixture():
    manifest = {
        "schema": "stegverse.ingress-manifest/v1",
        "manifest_id": "RUN2-MANIFEST-001",
        "source": {"framework": "StegVerse", "class": "GOVERNED_RUN"},
    }
    history = [
        {"seq": 1, "transition": "TEST_INITIATED", "state": "BOUND"},
        {"seq": 2, "transition": "GOVERNANCE_EVALUATED", "state": "ALLOW"},
        {"seq": 3, "transition": "MIR_HANDOFF", "state": "EMITTED"},
    ]
    response_to = "RUN2-HANDOFF-001"
    event_hashes = [_sha(item) for item in history]
    accounting = {
        "scheme": "stegverse.mir-node-mirror.checkpoint.v2",
        "event_count": len(history),
        "history_sha256": _sha(history),
        "event_hashes": event_hashes,
    }
    accounting["tip"] = _sha(accounting)
    artifact = {
        "schema": "stegverse.mir-node-mirror.accounting/v2",
        "provenance": {
            "source_node_label": "MIR NODE MIRROR",
            "source_class": "EXTERNAL_SYSTEM_NODE_MIRROR",
        },
        "binding": {
            "test_id": "MIR-STEGVERSE-HISTORICAL-ACCOUNTING-RUN-002",
            "revision": 1,
            "manifest_hash": _sha(manifest),
            "response_to": response_to,
            "response_class": "MIR_HISTORICAL_ACCOUNTING",
        },
        "accounting": accounting,
        "record_role": "IMMUTABLE_STATE_TRANSITION_RECORD",
        "authority_namespace_effect": "NONE",
    }
    return manifest, history, response_to, artifact


def test_exact_mir_accounting_reconstructs_original_run_without_delta():
    manifest, history, response_to, artifact = _fixture()
    result = evaluate_mir_historical_accounting_delta(
        manifest=manifest,
        history=history,
        response_to=response_to,
        artifact=artifact,
    )
    assert result["state"] == "EXACT_MATCH"
    assert result["exact_match"] is True
    assert result["mismatch_count"] == 0
    assert result["mismatches"] == []
    assert result["mir_evidence_authority"] == "HISTORICAL_ACCOUNTING_ONLY"
    assert result["stegverse_governance_authority_transferred"] is False


def test_event_order_change_is_reported_as_delta():
    manifest, history, response_to, artifact = _fixture()
    artifact["accounting"]["event_hashes"] = list(reversed(artifact["accounting"]["event_hashes"]))
    result = evaluate_mir_historical_accounting_delta(
        manifest=manifest,
        history=history,
        response_to=response_to,
        artifact=artifact,
    )
    assert result["state"] == "DELTA_OBSERVED"
    assert result["exact_match"] is False
    assert any(item["field"] == "event_hashes" for item in result["mismatches"])


def test_history_hash_change_is_reported_as_delta():
    manifest, history, response_to, artifact = _fixture()
    artifact["accounting"]["history_sha256"] = "sha256:" + "0" * 64
    result = evaluate_mir_historical_accounting_delta(
        manifest=manifest,
        history=history,
        response_to=response_to,
        artifact=artifact,
    )
    assert any(item["field"] == "history_sha256" for item in result["mismatches"])


def test_manifest_binding_change_is_reported_as_delta():
    manifest, history, response_to, artifact = _fixture()
    artifact["binding"]["manifest_hash"] = "sha256:" + "f" * 64
    result = evaluate_mir_historical_accounting_delta(
        manifest=manifest,
        history=history,
        response_to=response_to,
        artifact=artifact,
    )
    assert any(item["field"] == "manifest_hash" for item in result["mismatches"])


def test_wrong_response_correlation_is_reported_as_delta():
    manifest, history, response_to, artifact = _fixture()
    artifact["binding"]["response_to"] = "OTHER-HANDOFF"
    result = evaluate_mir_historical_accounting_delta(
        manifest=manifest,
        history=history,
        response_to=response_to,
        artifact=artifact,
    )
    assert any(item["field"] == "response_to" for item in result["mismatches"])


def test_authority_bearing_mir_artifact_fails_closed():
    manifest, history, response_to, artifact = _fixture()
    artifact["authority_namespace_effect"] = "ALLOW"
    with pytest.raises(MirHistoricalAccountingDeltaError, match="mir_artifact_authority_effect_forbidden"):
        evaluate_mir_historical_accounting_delta(
            manifest=manifest,
            history=history,
            response_to=response_to,
            artifact=artifact,
        )
