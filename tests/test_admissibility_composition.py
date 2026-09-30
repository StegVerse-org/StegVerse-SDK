from __future__ import annotations

import copy

from stegverse.admissibility import evaluate_admissibility_packet
from stegverse.admissibility_composition import (
    JOINT_RELATION_SCHEMA,
    evaluate_admissibility_composition,
)
from stegverse.joint_relation import (
    COVERAGE_BOUND,
    COVERAGE_MISMATCHED,
    COVERAGE_UNDECLARED,
    COVERS_COMPONENT_IDS,
    COVERS_COMPOSITION_ID,
    MISMATCH_COMPONENTS,
    MISMATCH_COMPOSITION,
    MISMATCH_INCOMPLETE,
)


def _component(object_id: str):
    packet = {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "tester": {
            "name_or_role": "composition-test",
            "discipline_id": "education_learning",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": object_id,
            "object_type": "model_response",
            "summary": "Individually admissible component.",
        },
        "route": {
            "recommended_route": ["transition_admissibility", "receipt_replay", "fail_closed"],
            "tests_run": ["transition_admissibility"],
            "route_deviation_reason": None,
        },
        "classification": {
            "declared_intent": "research_summary",
            "authority_source": "AUTH-STATIC-001",
            "evidence_posture": "receipt_backed",
            "replay_posture": "receipt_backed",
            "consequence_level": "low",
            "claim_limit": "Composition falsification fixture.",
        },
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_proof_authority": True,
        },
    }
    return evaluate_admissibility_packet(packet, strict=True)


def _joint_relation(*, covers=None, composition_id=None):
    """A validated relation record.

    ``covers``/``composition_id`` declare what the relation was validated over.
    A record that declares neither is the historical shape: still accepted, but
    not bound to any particular composition -- see the unbound test below.
    """
    relation = {
        "schema": JOINT_RELATION_SCHEMA,
        "relation_id": "JOINT-REL-001",
        "relation_status": "validated",
        "authority_source": "JOINT-RELATION-REVIEW-001",
        "evidence_posture": "receipt_backed",
        "replay_posture": "receipt_backed",
    }
    if covers is not None:
        relation[COVERS_COMPONENT_IDS] = list(covers)
    if composition_id is not None:
        relation[COVERS_COMPOSITION_ID] = composition_id
    return relation


def test_two_individually_admissible_components_do_not_imply_composition_admissibility():
    a = _component("A")
    b = _component("B")

    assert a["classification"]["decision"] == "ALLOW_WITH_POSTURE"
    assert b["classification"]["decision"] == "ALLOW_WITH_POSTURE"

    result = evaluate_admissibility_composition(
        [a, b],
        composition_id="A+B",
        joint_consequence_level="critical",
    )

    assert result["all_components_individually_admissible"] is True
    assert result["classification"]["decision"] == "FAIL_CLOSED"
    assert result["classification"]["allowed_next_state"] == "fail_closed"
    assert result["relation"]["status"] == "unresolved"
    assert result["relation"]["maturity_class"] == "under_development"
    assert result["relation"]["basis"] == "no_explicit_composition_admissibility_relation"
    assert result["separability"]["component_admissibility_implies_composition_admissibility"] is False


def test_validated_joint_relation_is_a_distinct_positive_control_not_execution_authority():
    a = _component("A")
    b = _component("B")

    result = evaluate_admissibility_composition(
        [a, b],
        composition_id="A+B-VALIDATED",
        joint_consequence_level="low",
        joint_relation=_joint_relation(covers=["A", "B"], composition_id="A+B-VALIDATED"),
    )

    assert result["classification"]["decision"] == "ALLOW_WITH_POSTURE"
    assert result["classification"]["allowed_next_state"] == "composition_relation_backed_claim"
    assert result["relation"]["status"] == "resolved"
    assert result["relation"]["maturity_class"] == "known_composition_with_posture"
    assert result["joint_relation_valid"] is True
    assert result["relation_binding_verified"] is True
    assert result["relation_coverage"]["coverage"] == COVERAGE_BOUND
    assert result["boundary"]["does_not_grant_execution_authority"] is True
    assert result["boundary"]["does_not_execute_components"] is True


def test_tampered_component_receipt_fails_closed_even_with_joint_relation():
    a = _component("A")
    b = _component("B")
    tampered = copy.deepcopy(b)
    tampered["classification"]["allowed_next_state"] = "tampered"

    result = evaluate_admissibility_composition(
        [a, tampered],
        composition_id="A+B-TAMPERED",
        joint_consequence_level="low",
        joint_relation=_joint_relation(),
    )

    assert result["component_integrity"] is False
    assert result["classification"]["decision"] == "FAIL_CLOSED"
    assert result["relation"]["basis"] == "component_receipt_integrity_failure"


def test_nonadmissible_component_blocks_composition():
    a = _component("A")
    blocked_packet = {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "tester": {
            "name_or_role": "composition-test",
            "discipline_id": "medicine_health",
            "domain_review_required": True,
        },
        "test_object": {"object_id": "BLOCKED", "object_type": "care_decision", "summary": "Blocked component."},
        "route": {"recommended_route": ["fail_closed"], "tests_run": ["fail_closed"], "route_deviation_reason": None},
        "classification": {
            "declared_intent": "care_decision",
            "authority_source": None,
            "evidence_posture": "source_backed",
            "replay_posture": "partially_replayable",
            "consequence_level": "high",
            "claim_limit": "No consequential movement.",
        },
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_proof_authority": True,
        },
    }
    blocked = evaluate_admissibility_packet(blocked_packet, strict=True)

    result = evaluate_admissibility_composition(
        [a, blocked],
        composition_id="A+BLOCKED",
        joint_consequence_level="low",
        joint_relation=_joint_relation(),
    )

    assert result["all_components_individually_admissible"] is False
    assert result["classification"]["decision"] == "FAIL_CLOSED"
    assert result["relation"]["basis"] == "one_or_more_components_not_individually_admissible"


# --- 2 to N: the arity the original controls never reached ------------------
#
# tasks/SDK-ADMISSIBILITY-COMPOSITION-002.json recorded its controls as
# "n2-negative-and-positive-controls", and every test above composes exactly two
# components. The non-separability rule was therefore demonstrated for a pair and
# assumed for the rest. These exercise it at N, and pin the failure the pair case
# could not expose: a relation validated over a subset silently covering a
# superset.


def _n_components(count: int):
    return [_component(chr(ord("A") + index)) for index in range(count)]


def _ids(count: int):
    return [chr(ord("A") + index) for index in range(count)]


def test_non_separability_holds_at_every_arity_not_just_two():
    """No relation, any N: never lifted from the components."""
    for count in (2, 3, 5, 12):
        result = evaluate_admissibility_composition(
            _n_components(count),
            composition_id=f"N{count}",
            joint_consequence_level="critical",
        )
        assert result["component_count"] == count
        assert result["all_components_individually_admissible"] is True
        assert result["classification"]["decision"] == "FAIL_CLOSED", count
        assert result["relation"]["basis"] == "no_explicit_composition_admissibility_relation"


def test_a_bound_relation_is_accepted_at_every_arity():
    for count in (2, 3, 5, 12):
        cid = f"N{count}"
        result = evaluate_admissibility_composition(
            _n_components(count),
            composition_id=cid,
            joint_consequence_level="critical",
            joint_relation=_joint_relation(covers=_ids(count), composition_id=cid),
        )
        assert result["classification"]["decision"] == "ALLOW_WITH_POSTURE", count
        assert result["relation_binding_verified"] is True
        assert result["relation_coverage"]["declared_arity"] == count
        assert result["relation_coverage"]["actual_arity"] == count


def test_a_relation_validated_for_a_subset_does_not_cover_a_superset():
    """The separability error one level up, and the reason 2 does not imply N.

    A relation genuinely validated over {A, B} is a valid record. Applied to
    {A, B, C} it is a statement about a different composition, and composing on
    it would lift a sub-composition's relation into a larger one.
    """
    result = evaluate_admissibility_composition(
        _n_components(3),
        composition_id="N3",
        joint_relation=_joint_relation(covers=["A", "B"], composition_id="N3"),
        joint_consequence_level="critical",
    )

    assert result["joint_relation_valid"] is True, "the record itself is well formed"
    assert result["classification"]["decision"] == "FAIL_CLOSED"
    assert result["relation"]["basis"] == "joint_relation_does_not_cover_this_composition"
    assert result["relation_coverage"]["coverage"] == COVERAGE_MISMATCHED
    assert result["relation_coverage"]["mismatch_reasons"] == [MISMATCH_COMPONENTS]
    assert result["relation_coverage"]["declared_arity"] == 2
    assert result["relation_coverage"]["actual_arity"] == 3
    assert result["separability"]["subset_relation_covers_superset_composition"] is False


def test_a_relation_for_another_composition_does_not_cover_this_one():
    result = evaluate_admissibility_composition(
        _n_components(3),
        composition_id="N3",
        joint_relation=_joint_relation(covers=_ids(3), composition_id="SOME-OTHER-COMPOSITION"),
        joint_consequence_level="critical",
    )
    assert result["classification"]["decision"] == "FAIL_CLOSED"
    assert result["relation_coverage"]["mismatch_reasons"] == [MISMATCH_COMPOSITION]


def test_naming_the_composition_without_the_components_does_not_pin_arity():
    """Opting in is all-or-nothing; a half declaration is a mismatch."""
    result = evaluate_admissibility_composition(
        _n_components(4),
        composition_id="N4",
        joint_relation=_joint_relation(composition_id="N4"),
        joint_consequence_level="critical",
    )
    assert result["classification"]["decision"] == "FAIL_CLOSED"
    assert result["relation_coverage"]["mismatch_reasons"] == [MISMATCH_INCOMPLETE]


def test_component_order_cannot_change_coverage():
    components = _n_components(4)
    cid = "N4"
    relation = _joint_relation(covers=["D", "C", "B", "A"], composition_id=cid)
    forward = evaluate_admissibility_composition(
        components, composition_id=cid, joint_relation=relation,
        joint_consequence_level="critical")
    reverse = evaluate_admissibility_composition(
        list(reversed(components)), composition_id=cid, joint_relation=relation,
        joint_consequence_level="critical")
    assert forward["relation_binding_verified"] is True
    assert reverse["relation_binding_verified"] is True
    assert forward["relation_coverage"]["actual_component_ids"] == \
        reverse["relation_coverage"]["actual_component_ids"]


def test_an_undeclared_relation_is_accepted_but_reported_as_unbound():
    """The historical shape stays admissible, and stops implying it is bound.

    Withdrawing acceptance here would make an existing 3-LLM governed
    composition ungoverned, which is the goal owner's call. What this check
    refuses to do is let the result read as though the relation had been
    verified against these components.
    """
    result = evaluate_admissibility_composition(
        _n_components(3),
        composition_id="N3",
        joint_relation=_joint_relation(),
        joint_consequence_level="critical",
    )
    assert result["classification"]["decision"] == "ALLOW_WITH_POSTURE"
    assert result["joint_relation_valid"] is True
    assert result["relation_binding_verified"] is False
    assert result["relation_coverage"]["coverage"] == COVERAGE_UNDECLARED
    assert result["relation"]["maturity_class"] == "known_composition_with_unbound_relation"
    assert any("does not declare" in step for step in
               result["classification"]["required_follow_up"])


def test_a_bare_string_coverage_is_not_read_as_a_character_sequence():
    """"AB" must not satisfy a two-component coverage by iterating characters."""
    relation = _joint_relation(composition_id="N2")
    relation[COVERS_COMPONENT_IDS] = "AB"
    result = evaluate_admissibility_composition(
        _n_components(2), composition_id="N2", joint_relation=relation,
        joint_consequence_level="critical")
    assert result["classification"]["decision"] == "FAIL_CLOSED"
    assert result["relation_coverage"]["coverage"] == COVERAGE_MISMATCHED
