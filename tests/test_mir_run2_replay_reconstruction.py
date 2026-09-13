from __future__ import annotations

import hashlib
import json

from stegverse.mir_historical_accounting_delta import evaluate_mir_historical_accounting_delta
from stegverse.mir_run2_replay_reconstruction import reconstruct_run2_history, replay_run2_delta


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


def test_replay_reproduces_exact_delta_result():
    manifest, history, response_to, artifact = _fixture()
    delta = evaluate_mir_historical_accounting_delta(
        manifest=manifest,
        history=history,
        response_to=response_to,
        artifact=artifact,
    )
    replay = replay_run2_delta(
        manifest=manifest,
        history=history,
        response_to=response_to,
        artifact=artifact,
        prior_delta=delta,
    )
    assert replay["state"] == "REPLAY_MATCH"
    assert replay["equivalent"] is True
    assert replay["prior_delta_digest"] == replay["replayed_delta_digest"]


def test_reconstruction_reproduces_event_order_and_history_hash():
    _, history, _, artifact = _fixture()
    reconstruction = reconstruct_run2_history(history=history, artifact=artifact)
    assert reconstruction["state"] == "RECONSTRUCTED_EXACT"
    assert reconstruction["exact"] is True
    assert reconstruction["ordered_event_hashes_match"] is True
    assert reconstruction["history_hash_match"] is True
    assert reconstruction["event_count_match"] is True


def test_reconstruction_exposes_order_delta():
    _, history, _, artifact = _fixture()
    artifact["accounting"]["event_hashes"] = list(reversed(artifact["accounting"]["event_hashes"]))
    reconstruction = reconstruct_run2_history(history=history, artifact=artifact)
    assert reconstruction["state"] == "RECONSTRUCTION_DELTA"
    assert reconstruction["exact"] is False
    assert reconstruction["ordered_event_hashes_match"] is False
