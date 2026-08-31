from stegverse.admissibility import evaluate_admissibility_packet
from stegverse.admissibility_composition import evaluate_admissibility_composition
from stegverse.execution_boundary import EXECUTION_BOUNDARY_CASE_SCHEMA, evaluate_execution_boundary_case


def _component(object_id: str):
    packet = {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "tester": {
            "name_or_role": "iw-sdk-integration",
            "discipline_id": "education_learning",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": object_id,
            "object_type": "candidate_transition",
            "summary": "Individually admissible coupled-manifold component.",
        },
        "route": {
            "recommended_route": ["transition_admissibility", "receipt_replay", "fail_closed"],
            "tests_run": ["transition_admissibility"],
            "route_deviation_reason": None,
        },
        "classification": {
            "declared_intent": "research_summary",
            "authority_source": "AUTH-IW-STATIC-001",
            "evidence_posture": "receipt_backed",
            "replay_posture": "receipt_backed",
            "consequence_level": "low",
            "claim_limit": "IW SDK integration fixture.",
        },
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_proof_authority": True,
        },
    }
    return evaluate_admissibility_packet(packet, strict=True)


def _execution_case(initial, boundary, *, consequence_status="pending", alterable=True):
    return {
        "schema": EXECUTION_BOUNDARY_CASE_SCHEMA,
        "case_id": "IW-INTEGRATION-A1",
        "candidate_transition": {"transition_id": "A1"},
        "initial_admissibility": initial,
        "intervening_transitions": [
            {
                "transition_id": "COUPLED-STATE-OBSERVATION",
                "from_state_hash": "sha256:iw-state-0",
                "to_state_hash": "sha256:iw-state-1",
                "materially_relevant": True,
                "observed": True,
                "observed_at": "2026-08-31T14:00:00Z",
            }
        ],
        "boundary_admissibility": boundary,
        "consequence": {
            "status": consequence_status,
            "alterable_at_boundary": alterable,
        },
    }


def test_real_sdk_single_lane_can_permit_while_joint_manifold_fails_closed():
    a1_initial = _component("A1")
    a1_boundary = _component("A1")
    a2 = _component("A2")

    lane = evaluate_execution_boundary_case(_execution_case(a1_initial, a1_boundary))
    joint = evaluate_admissibility_composition(
        [a1_boundary, a2],
        composition_id="A1+A2",
        joint_consequence_level="critical",
    )

    assert a1_initial["classification"]["decision"] == "ALLOW_WITH_POSTURE"
    assert a2["classification"]["decision"] == "ALLOW_WITH_POSTURE"
    assert lane["classification"]["decision"] == "PERMIT_CONSEQUENCE"
    assert joint["all_components_individually_admissible"] is True
    assert joint["classification"]["decision"] == "FAIL_CLOSED"
    assert joint["relation"]["basis"] == "no_explicit_composition_admissibility_relation"
    assert joint["separability"]["component_admissibility_implies_composition_admissibility"] is False


def test_real_sdk_joint_classification_is_invariant_to_component_arrival_order():
    a1 = _component("A1")
    a2 = _component("A2")

    forward = evaluate_admissibility_composition(
        [a1, a2],
        composition_id="ORDER-INVARIANT",
        joint_consequence_level="critical",
    )
    reverse = evaluate_admissibility_composition(
        [a2, a1],
        composition_id="ORDER-INVARIANT",
        joint_consequence_level="critical",
    )

    assert forward["classification"] == reverse["classification"]
    assert forward["relation"] == reverse["relation"]
    assert forward["classification"]["decision"] == "FAIL_CLOSED"
    # Evidence serialization may preserve component ordering, so receipt hashes
    # need not match; the governance classification itself must remain invariant.


def test_real_sdk_irreversible_boundary_is_already_too_late_for_lane_reassessment():
    a1_initial = _component("A1")
    a1_boundary = _component("A1")
    a2 = _component("A2")

    lane_after_irreversibility = evaluate_execution_boundary_case(
        _execution_case(
            a1_initial,
            a1_boundary,
            consequence_status="executed",
            alterable=False,
        )
    )
    joint = evaluate_admissibility_composition(
        [a1_boundary, a2],
        composition_id="A1+A2-IRREVERSIBLE",
        joint_consequence_level="critical",
    )

    assert lane_after_irreversibility["classification"]["decision"] == "FAIL_CLOSED"
    assert lane_after_irreversibility["falsification"]["outcome"] == "INDETERMINATE_EVIDENCE_BOUNDARY"
    assert joint["classification"]["decision"] == "FAIL_CLOSED"
    assert "Evaluate before the consequence becomes safely irreversible." in lane_after_irreversibility["classification"]["required_follow_up"]
