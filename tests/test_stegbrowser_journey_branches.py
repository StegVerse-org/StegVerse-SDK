"""A journey is a fan of parallel round trips, and one worker is the N=1 case.

The packet carries the endpoint receipts, so the journey shape is what replay
depends on. Generalizing it while no authentic receipt exists costs nothing;
doing it after TEST5_A closes would change the shape across a custody boundary,
and receipts recorded under the old shape could not be replayed under the new
one. These tests pin both halves: a v1 single round trip keeps its exact
meaning and receipt order, and a v2 fan requires four receipts per branch with
no branch able to borrow another's.

Non-authorizing: manifest construction and graph derivation only. No receipt is
minted, no browser runs and no transition is admitted.
"""
from __future__ import annotations

import pytest

from stegverse.manifest_builder import build_manifest
from stegverse.manifest_state_transition_runtime import derive_execution_request
from stegverse.stegbrowser_processor import (
    JOURNEY_SCHEMA,
    JOURNEY_SCHEMA_V2,
    validate_stegbrowser_request,
)

DIGEST = {name: f"sha256:{char * 64}" for name, char in
          {"a_out": "a", "a_ret": "b", "c_out": "c", "c_ret": "d", "e_out": "e", "e_ret": "f"}.items()}


def v1_journey(**overrides):
    journey = {
        "schema": JOURNEY_SCHEMA,
        "journey_id": "test5-a",
        "origin_endpoint": "stegverse:test5-origin",
        "ephemeral_endpoint": "stegbrowser:ephemeral:a",
        "outbound_manifest_sha256": DIGEST["a_out"],
        "return_manifest_sha256": DIGEST["a_ret"],
        "return_predecessor_manifest_sha256": DIGEST["a_out"],
    }
    journey.update(overrides)
    return journey


def branch(letter, *, out, ret, **overrides):
    entry = {
        "branch_id": letter,
        "ephemeral_endpoint": f"stegbrowser:ephemeral:{letter}",
        "outbound_manifest_sha256": out,
        "return_manifest_sha256": ret,
        "return_predecessor_manifest_sha256": out,
    }
    entry.update(overrides)
    return entry


def v2_journey(branches, **overrides):
    journey = {
        "schema": JOURNEY_SCHEMA_V2,
        "journey_id": "test6-fan",
        "origin_endpoint": "stegverse:test6-origin",
        "branches": branches,
    }
    journey.update(overrides)
    return journey


def request(journey, **overrides):
    value = {
        "schema": "stegbrowser.llm-profile-request.v1",
        "profile": "llm.v1",
        "prompt": "Return the exact marker and identify this session.",
        "response_marker": "TEST_DEFAULT",
        "provider": "credential-free-huggingface-space",
        "journey": journey,
    }
    value.update(overrides)
    return value


def graph(journey, **overrides):
    manifest = build_manifest(
        data={"test": 6},
        data_class="stegverse.sdk-test.v1",
        source_framework="StegVerse-SDK-Evaluator",
        source_output_id="journey-branches",
        processor_request=request(journey, **overrides),
        process="stegbrowser",
        return_depth="full-trace",
        publisher_required=False,
    )
    return derive_execution_request(manifest)["state_graph"]


# --- the N=1 case must not change meaning -----------------------------------

def test_v1_journey_normalizes_to_exactly_one_branch():
    normalized = validate_stegbrowser_request(request(v1_journey()))["journey"]
    assert normalized["schema"] == JOURNEY_SCHEMA_V2
    assert normalized["branch_count"] == 1
    only = normalized["branches"][0]
    assert only["branch_id"] == "1"
    assert only["ephemeral_endpoint"] == "stegbrowser:ephemeral:a"
    assert only["outbound_manifest_sha256"] == DIGEST["a_out"]
    assert only["return_predecessor_manifest_sha256"] == DIGEST["a_out"]


def test_v1_journey_keeps_its_four_receipt_order():
    order = graph(v1_journey())["endpoint_receipt_journey"]["required_order"]
    assert order == [
        {"branch_id": "1", "leg": 1, "direction": "EGRESS"},
        {"branch_id": "1", "leg": 1, "direction": "INGRESS"},
        {"branch_id": "1", "leg": 2, "direction": "EGRESS"},
        {"branch_id": "1", "leg": 2, "direction": "INGRESS"},
    ]


def test_a_v1_journey_may_not_smuggle_branches():
    with pytest.raises(ValueError, match="declares no branches"):
        validate_stegbrowser_request(request(v1_journey(branches=[])))


# --- the fan ----------------------------------------------------------------

def test_a_fan_requires_four_endpoint_receipts_per_branch():
    journey = v2_journey([
        branch("a", out=DIGEST["a_out"], ret=DIGEST["a_ret"]),
        branch("c", out=DIGEST["c_out"], ret=DIGEST["c_ret"]),
        branch("e", out=DIGEST["e_out"], ret=DIGEST["e_ret"]),
    ])
    receipts = graph(journey)["endpoint_receipt_journey"]
    assert receipts["branch_count"] == 3
    assert len(receipts["required_order"]) == 12
    assert [r["branch_id"] for r in receipts["required_order"]] == (
        ["a"] * 4 + ["c"] * 4 + ["e"] * 4
    )
    assert receipts["record_order"] == ["ORGANIZATION_RECORDS", "MASTER_RECORDS"]


def test_each_branch_carries_its_own_llm_and_marker():
    """Test 6's point: one query, N workers, a different LLM on each."""
    journey = v2_journey([
        branch("a", out=DIGEST["a_out"], ret=DIGEST["a_ret"],
               provider="openai", response_marker="TEST6_A"),
        branch("c", out=DIGEST["c_out"], ret=DIGEST["c_ret"],
               provider="anthropic", response_marker="TEST6_C"),
    ])
    resolved = graph(journey)["branches"]
    assert [b["provider"] for b in resolved] == ["openai", "anthropic"]
    assert [b["response_marker"] for b in resolved] == ["TEST6_A", "TEST6_C"]


def test_a_branch_without_overrides_inherits_the_request_default():
    journey = v2_journey([
        branch("a", out=DIGEST["a_out"], ret=DIGEST["a_ret"]),
        branch("c", out=DIGEST["c_out"], ret=DIGEST["c_ret"], provider="anthropic"),
    ])
    resolved = graph(journey)["branches"]
    assert resolved[0]["provider"] == "credential-free-huggingface-space"
    assert resolved[1]["provider"] == "anthropic"


# --- no branch may borrow another's evidence --------------------------------

@pytest.mark.parametrize("field,label", [
    ("branch_id", "branch ids"),
    ("ephemeral_endpoint", "ephemeral endpoints"),
])
def test_branches_must_be_distinct(field, label):
    duplicate = branch("c", out=DIGEST["c_out"], ret=DIGEST["c_ret"])
    duplicate[field] = branch("a", out=DIGEST["a_out"], ret=DIGEST["a_ret"])[field]
    journey = v2_journey([branch("a", out=DIGEST["a_out"], ret=DIGEST["a_ret"]), duplicate])
    with pytest.raises(ValueError, match=label):
        validate_stegbrowser_request(request(journey))


def test_two_branches_may_not_share_an_outbound_manifest():
    journey = v2_journey([
        branch("a", out=DIGEST["a_out"], ret=DIGEST["a_ret"]),
        branch("c", out=DIGEST["a_out"], ret=DIGEST["c_ret"]),
    ])
    with pytest.raises(ValueError, match="outbound manifests"):
        validate_stegbrowser_request(request(journey))


def test_a_shared_response_marker_is_rejected():
    """A shared marker would let one branch's response satisfy another's receipt."""
    journey = v2_journey([
        branch("a", out=DIGEST["a_out"], ret=DIGEST["a_ret"], response_marker="SAME"),
        branch("c", out=DIGEST["c_out"], ret=DIGEST["c_ret"], response_marker="SAME"),
    ])
    with pytest.raises(ValueError, match="response markers"):
        validate_stegbrowser_request(request(journey))


def test_a_branch_return_must_predecessor_link_to_its_own_outbound():
    journey = v2_journey([
        branch("a", out=DIGEST["a_out"], ret=DIGEST["a_ret"]),
        dict(branch("c", out=DIGEST["c_out"], ret=DIGEST["c_ret"]),
             return_predecessor_manifest_sha256=DIGEST["a_out"]),
    ])
    with pytest.raises(ValueError, match="predecessor-link"):
        validate_stegbrowser_request(request(journey))


def test_a_return_manifest_is_distinct_from_its_outbound():
    journey = v2_journey([branch("a", out=DIGEST["a_out"], ret=DIGEST["a_out"])])
    with pytest.raises(ValueError, match="distinct from its outbound"):
        validate_stegbrowser_request(request(journey))


def test_an_empty_fan_is_rejected():
    with pytest.raises(ValueError, match="non-empty branches"):
        validate_stegbrowser_request(request(v2_journey([])))


def test_an_unknown_journey_schema_is_rejected():
    with pytest.raises(ValueError, match="journey schema"):
        validate_stegbrowser_request(request(v1_journey(schema="something/v9")))


def test_graph_derivation_grants_no_authority():
    derived = graph(v2_journey([branch("a", out=DIGEST["a_out"], ret=DIGEST["a_ret"])]))
    assert derived["authority_effect"] == "NONE_GRAPH_DERIVATION_ONLY"
    assert derived["adapter_executes_lifecycle"] is False
    assert derived["requires_workercoordinator_claim_fence"] is True
