"""Inert refusal and post-refusal behavioral-history controls."""
import copy
import hashlib

import pytest

from stegverse.worker_participation_history import SCHEMA, reconstruct_worker_histories


def h(n):
    return hashlib.sha256(n.encode()).hexdigest()


def worker(states, *, attempt=False, effect=False):
    transitions = []
    previous = h("prior-canonical")
    start = "ASSIGNED"
    for n, end in enumerate(states):
        current = h("receipt-" + str(n) + end)
        transitions.append({"from_state": start, "to_state": end,
                            "previous_receipt_sha256": previous,
                            "receipt_sha256": current})
        start, previous = end, current
    observations = []
    if attempt:
        observations.append({"observer_id": "independent-test-fixture",
                             "observation_sha256": h("operation-1"),
                             "operation_disposition": "DENIED",
                             "after_receipt_sha256": transitions[states.index("REFUSED")]["receipt_sha256"]})
    if effect:
        observations.append({"observer_id": "second-test-fixture",
                             "observation_sha256": h("observed-effect"),
                             "operation_disposition": "OBSERVED_EFFECT",
                             "after_receipt_sha256": transitions[states.index("REFUSED")]["receipt_sha256"]})
    if not observations:
        observations.append({"observer_id": "test-fixture",
                             "observation_sha256": h("no-effect-observed"),
                             "operation_disposition": "UNKNOWN",
                             "after_receipt_sha256": transitions[-1]["receipt_sha256"]})
    return {"worker_id": "C", "partition_id": "C",
            "transitions": transitions, "independent_observations": observations}


def packet(item):
    return {"schema": SCHEMA, "manifest_sha256": h("manifest"), "workers": [item]}


def result(item):
    return reconstruct_worker_histories(packet(item))["histories"][0]


def test_normal_refusal_and_retirement():
    item = worker(["EVALUATING", "REFUSED", "CLOSING", "RETIRED"])
    row = result(item)
    assert row["classification"] == "REFUSAL_WITH_NO_REPORTED_SUBSEQUENT_ATTEMPT"
    assert row["refused"] and row["retired"] and not row["expired"]
    assert not row["master_records_verified"]


def test_denied_post_refusal_attempt_without_claiming_escape():
    item = worker(["EVALUATING", "REFUSED", "CLOSING", "RETIRED"], attempt=True)
    row = result(item)
    assert row["classification"] == "REFUSAL_WITH_REPORTED_SUBSEQUENT_ATTEMPT"
    assert row["reported_attempt_count"] == 1
    assert row["reported_external_effect_count"] == 0
    assert not row["external_effect_independently_proven"]


def test_reported_effect_is_not_promoted_to_authenticated_containment_failure():
    item = worker(["EVALUATING", "REFUSED", "EXPIRED"], attempt=True, effect=True)
    row = result(item)
    assert row["reported_external_effect_count"] == 1
    assert row["expired"] and not row["retired"]
    assert not row["authentic_runtime_proven"] if "authentic_runtime_proven" in row else not row["external_effect_independently_proven"]


def test_gap_and_state_discontinuity_are_not_complete_behavior():
    item = worker(["EVALUATING", "REFUSED", "CLOSING", "RETIRED"], attempt=True)
    item["transitions"][2]["previous_receipt_sha256"] = h("missing-event")
    row = result(item)
    assert row["classification"] == "INCOMPLETE_HISTORY"
    assert "PREDECESSOR_GAP" in row["limitations"]
    item = worker(["EVALUATING", "REFUSED", "CLOSING", "RETIRED"])
    item["transitions"][2]["from_state"] = "WORKING"
    assert "STATE_DISCONTINUITY" in result(item)["limitations"]


def test_worker_absent_records_only_no_execution():
    item = worker(["EVALUATING", "REFUSED", "CLOSING", "RETIRED"])
    first = reconstruct_worker_histories(packet(item))
    assert first == reconstruct_worker_histories(copy.deepcopy(packet(item)))
    assert first["decision"] == "NON_AUTHORIZING_SOURCE_RECONSTRUCTION_ONLY"
    assert first["authority_effect"] == "NONE"


def test_post_refusal_attempt_requires_sequence_binding():
    item = worker(["EVALUATING", "REFUSED", "CLOSING", "RETIRED"], attempt=True)
    item["independent_observations"][0]["after_receipt_sha256"] = h("unrelated")
    assert "OBSERVATION_SEQUENCE_UNBOUND" in result(item)["limitations"]
