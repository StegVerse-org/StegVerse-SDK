"""Composition of N worker LLM answers into one governed response.

Components are built by StegBrowser's own ``bind_llm_profile_result`` where it is
importable, so these tests exercise the real seam rather than a hand-shaped dict
that happens to match what the SDK expects.
"""

from __future__ import annotations

import copy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

import pytest

from stegverse.governed_composite_response import (
    COMPONENT_SCHEMA,
    COMPOSITE_SCHEMA,
    DISPOSITION_FAIL_CLOSED,
    DISPOSITION_GOVERNED,
    DISPOSITION_RELATION_UNRESOLVED,
    FAILURE_COMPONENT_COMMITMENT,
    FAILURE_COMPONENT_MARKER,
    FAILURE_DUPLICATE_JOURNEY,
    FAILURE_FOREIGN_FAN,
    FAILURE_NO_MAJORITY,
    FAILURE_NO_UNANIMITY,
    FAILURE_RELATION_COVERAGE,
    FAILURE_RELATION_STANDING,
    JOINT_RELATION_SCHEMA,
    STRATEGY_ATTRIBUTED_SET,
    STRATEGY_MAJORITY,
    STRATEGY_UNANIMOUS,
    CompositeResponseError,
    compose_governed_response,
    reconstruct_governed_response,
)
from stegverse.joint_relation import (
    BASIS_ENUMERATED,
    EXPIRATION,
    STALE_EXPIRED,
    STALE_NOT_YET_VALID,
    STALE_NO_EVALUATION_TIME,
    STALE_UNPARSEABLE,
    STANDING_OUTSIDE_WINDOW,
    STANDING_UNCHECKABLE,
    STANDING_WINDOW_UNDECLARED,
    STANDING_WITHIN_WINDOW,
    SURFACES_NOT_CHECKABLE_HERE,
    VALID_FROM,
    BASIS_MANIFEST_DECLARED,
    COVERS_JOURNEY_ID,
    MISMATCH_JOURNEY,
    MISMATCH_JOURNEY_UNAVAILABLE,
    COVERAGE_BOUND,
    COVERAGE_MISMATCHED,
    COVERAGE_UNDECLARED,
    MISMATCH_JOURNEY_BRANCHES,
    COVERS_COMPONENT_IDS,
    COVERS_COMPOSITION_ID,
    MISMATCH_COMPONENTS,
)

FAN = "FAN-TEST6"

_BROWSER_CANDIDATES = (
    Path("/home/user/stegbrowser/src/stegbrowser/llm_profile.py"),
    Path(__file__).resolve().parents[2] / "stegbrowser/src/stegbrowser/llm_profile.py",
)


def _load_browser_profile():
    """Load StegBrowser's llm_profile directly, bypassing its package imports."""

    for path in _BROWSER_CANDIDATES:
        if not path.exists():
            continue
        spec = importlib.util.spec_from_file_location("_sb_llm_profile", path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None


BROWSER = _load_browser_profile()


def _sha256(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + sha256(data.encode("utf-8")).hexdigest()


def _worker(
    branch: str,
    provider: str,
    model: str,
    answer: str,
    *,
    fan: str = FAN,
    prompt: str = "Which protocol governs the return leg?",
) -> Dict[str, Any]:
    """Return one worker's llm-profile result for a branch of a fan."""

    journey_id = f"{fan}:{branch}"
    marker = f"MARKER-{branch}"
    response_text = f"{answer} {marker}"
    if BROWSER is not None:
        request = {
            "schema": BROWSER.REQUEST_SCHEMA,
            "profile": BROWSER.PROFILE,
            "prompt": prompt,
            "response_marker": marker,
            "provider": provider,
            "model": model,
            "journey": {
                "schema": BROWSER.JOURNEY_SCHEMA,
                "journey_id": journey_id,
                "origin_endpoint": "origin",
                "ephemeral_endpoint": f"ephemeral-{branch}",
                "outbound_manifest_sha256": "a" * 64,
                "return_manifest_sha256": "b" * 64,
                "return_predecessor_manifest_sha256": "a" * 64,
            },
        }
        packet = BROWSER.begin_llm_profile_packet(request)
        bound = BROWSER.bind_llm_profile_result(
            packet=packet, response_text=response_text, provider=provider, model=model
        )
        return dict(bound["result"])

    result = {
        "schema": COMPONENT_SCHEMA,
        "profile": "llm.v1",
        "request_commitment": _sha256({"prompt": prompt, "journey_id": journey_id}),
        "response_marker": marker,
        "provider": provider,
        "model": model,
        "response_text": response_text,
        "journey_id": journey_id,
    }
    result["response_commitment"] = _sha256(result)
    return result


VALID_RELATION = {
    "schema": JOINT_RELATION_SCHEMA,
    "relation_status": "validated",
    "relation_id": "REL-TEST6-001",
    "authority_source": "KV/SKAP Vault",
    "evidence_posture": "receipt_backed",
    "replay_posture": "receipt_backed",
}


def _journey_for(components: List[Mapping[str, Any]], *, fan: str = FAN) -> Dict[str, Any]:
    """The journey whose manifest declared exactly these branches.

    Real components arrive from a manifested fan, and that manifest states the
    branch set before any branch runs. Composing without one is composing an
    unmanifested request, which the tests below cover separately.
    """
    branch_ids = sorted(
        str(c["journey_id"]).split(":", 1)[1]
        for c in components
        if ":" in str(c["journey_id"])
    )
    return {
        "journey_id": fan,
        "branch_count": len(branch_ids),
        "branches": [{"branch_id": b} for b in branch_ids],
    }


_UNMANIFESTED = object()


def _compose(
    components: List[Mapping[str, Any]],
    *,
    strategy: str = STRATEGY_UNANIMOUS,
    relation: Optional[Mapping[str, Any]] = VALID_RELATION,
    fan: str = FAN,
    journey: Any = None,
    evaluated_at: Optional[str] = None,
) -> Dict[str, Any]:
    if journey is _UNMANIFESTED:
        journey = None
    elif journey is None:
        journey = _journey_for(components, fan=fan)
    return compose_governed_response(
        components,
        composition_id="CMP-TEST6",
        fan_journey_id=fan,
        strategy=strategy,
        joint_relation=relation,
        journey=journey,
        evaluated_at=evaluated_at,
    )


def _agreeing_fan() -> List[Mapping[str, Any]]:
    return [
        _worker("b0", "anthropic", "claude-opus", "The return leg is predecessor-linked."),
        _worker("b1", "openai", "gpt", "The return leg is predecessor-linked."),
        _worker("b2", "google", "gemini", "The return leg is predecessor-linked."),
    ]


def test_stegbrowser_is_the_component_producer_under_test() -> None:
    """Guard the fixture: silently falling back would hide a seam break."""
    if BROWSER is None:
        pytest.skip("StegBrowser checkout not present")
    component = _worker("b0", "anthropic", "claude-opus", "answer")
    assert component["schema"] == COMPONENT_SCHEMA


def test_three_different_llms_agreeing_compose_one_governed_response() -> None:
    composite = _compose(_agreeing_fan())
    assert composite["disposition"] == DISPOSITION_GOVERNED
    assert composite["governed_claim"] is True
    assert composite["composite_answer"] == "The return leg is predecessor-linked."
    assert composite["distinct_model_count"] == 3
    assert composite["unanimous"] is True


def test_each_branch_has_its_own_request_commitment() -> None:
    """Why the fan id, not the request commitment, is the query binding.

    Every branch commits to its own provider, model, marker and journey_id, so
    no two workers in a fan can share a request_commitment even when the prompt
    is identical.
    """
    composite = _compose(_agreeing_fan())
    commitments = {c["request_commitment"] for c in composite["components"]}
    assert len(commitments) == 3
    assert composite["query_binding"]["same_prompt_verified_from_components"] is False
    assert composite["query_binding"]["fan_journey_id"] == FAN


def test_marker_differences_alone_do_not_read_as_disagreement() -> None:
    """Each branch carries its own marker; only the answer should be compared."""
    composite = _compose(_agreeing_fan())
    assert composite["distinct_answer_count"] == 1
    markers = {c["journey_id"] for c in composite["components"]}
    assert len(markers) == 3


def test_a_divergent_worker_fails_a_unanimous_composition_closed() -> None:
    fan = _agreeing_fan() + [_worker("b3", "meta", "llama", "The return leg is unlinked.")]
    composite = _compose(fan)
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert FAILURE_NO_UNANIMITY in composite["failure_codes"]
    assert composite["composite_answer"] is None
    assert composite["governed_claim"] is False


def test_divergence_is_reported_with_the_workers_behind_each_answer() -> None:
    fan = _agreeing_fan() + [_worker("b3", "meta", "llama", "The return leg is unlinked.")]
    composite = _compose(fan)
    support = {
        group["support_count"]: group["worker_journey_ids"]
        for group in composite["answer_groups"]
    }
    assert sorted(support) == [1, 3]
    assert support[1] == [f"{FAN}:b3"]
    assert support[3] == [f"{FAN}:b0", f"{FAN}:b1", f"{FAN}:b2"]


def test_majority_strategy_selects_the_answer_a_strict_majority_returned() -> None:
    fan = _agreeing_fan() + [_worker("b3", "meta", "llama", "The return leg is unlinked.")]
    composite = _compose(fan, strategy=STRATEGY_MAJORITY)
    assert composite["disposition"] == DISPOSITION_GOVERNED
    assert composite["composite_answer"] == "The return leg is predecessor-linked."


def test_majority_strategy_fails_closed_on_an_even_split() -> None:
    fan = [
        _worker("b0", "anthropic", "claude-opus", "Linked."),
        _worker("b1", "openai", "gpt", "Linked."),
        _worker("b2", "google", "gemini", "Unlinked."),
        _worker("b3", "meta", "llama", "Unlinked."),
    ]
    composite = _compose(fan, strategy=STRATEGY_MAJORITY)
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert FAILURE_NO_MAJORITY in composite["failure_codes"]
    assert composite["composite_answer"] is None


def test_attributed_set_selects_nothing_and_still_reports_every_answer() -> None:
    fan = _agreeing_fan() + [_worker("b3", "meta", "llama", "The return leg is unlinked.")]
    composite = _compose(fan, strategy=STRATEGY_ATTRIBUTED_SET)
    assert composite["disposition"] == DISPOSITION_GOVERNED
    assert composite["selected_answer_sha256"] is None
    assert composite["composite_answer"] is None
    assert composite["distinct_answer_count"] == 2


def test_without_a_validated_joint_relation_the_composite_is_not_a_governed_claim() -> None:
    composite = _compose(_agreeing_fan(), relation=None)
    assert composite["disposition"] == DISPOSITION_RELATION_UNRESOLVED
    assert composite["governed_claim"] is False
    # The answer is still carried and still attributed; only the claim is withheld.
    assert composite["composite_answer"] == "The return leg is predecessor-linked."
    assert composite["separability"][
        "component_admissibility_implies_composite_admissibility"
    ] is False


def test_unanimous_agreement_is_never_reported_as_correctness() -> None:
    composite = _compose(_agreeing_fan())
    assert composite["unanimous"] is True
    assert composite["boundary"]["agreement_is_evidence_of_correctness"] is False
    assert composite["boundary"]["composition_synthesizes_new_text"] is False
    assert composite["boundary"]["composition_calls_an_llm"] is False


def test_the_composite_answer_is_verbatim_one_of_the_component_answers() -> None:
    fan = _agreeing_fan()
    composite = _compose(fan)
    answers = {
        c["response_text"].replace(c["response_marker"], " ").strip() for c in fan
    }
    assert composite["composite_answer"] in answers


def test_a_tampered_component_response_fails_closed() -> None:
    fan = _agreeing_fan()
    tampered = dict(fan[1])
    tampered["response_text"] = f"Something else entirely. {tampered['response_marker']}"
    composite = _compose([fan[0], tampered, fan[2]])
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert FAILURE_COMPONENT_COMMITMENT in composite["failure_codes"]


def test_a_component_missing_its_own_marker_fails_closed() -> None:
    fan = _agreeing_fan()
    stripped = dict(fan[1])
    stripped["response_text"] = "No marker here."
    composite = _compose([fan[0], stripped, fan[2]])
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert FAILURE_COMPONENT_MARKER in composite["failure_codes"]


def test_the_same_worker_answer_cannot_be_counted_twice() -> None:
    fan = _agreeing_fan()
    composite = _compose([fan[0], fan[0], fan[1]])
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert FAILURE_DUPLICATE_JOURNEY in composite["failure_codes"]


def test_a_component_from_another_fan_cannot_be_folded_in() -> None:
    outsider = _worker("b0", "meta", "llama", "Linked.", fan="FAN-SOMETHING-ELSE")
    composite = _compose(_agreeing_fan() + [outsider])
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert FAILURE_FOREIGN_FAN in composite["failure_codes"]


def test_component_order_cannot_change_the_composite() -> None:
    fan = _agreeing_fan()
    forward = _compose(fan)
    backward = _compose(list(reversed(fan)))
    assert forward["composite_sha256"] == backward["composite_sha256"]


def test_a_composite_reconstructs_from_its_components_alone() -> None:
    fan = _agreeing_fan()
    composite = _compose(fan)
    replay = reconstruct_governed_response(composite, fan)
    assert replay["reconstruction_status"] == "RECONSTRUCTED"
    assert replay["reconstructed"] is True
    assert replay["reconstructed_composite_sha256"] == composite["composite_sha256"]


def test_reconstruction_diverges_when_a_component_is_swapped() -> None:
    fan = _agreeing_fan()
    composite = _compose(fan)
    substituted = fan[:2] + [_worker("b2", "google", "gemini", "A different answer.")]
    replay = reconstruct_governed_response(composite, substituted)
    assert replay["reconstructed"] is False
    assert replay["reconstruction_status"] in {"DIVERGED", "FAILED"}


def test_reconstruction_rejects_a_foreign_schema() -> None:
    with pytest.raises(CompositeResponseError):
        reconstruct_governed_response({"schema": "something.else.v1"}, _agreeing_fan())


def test_a_single_worker_is_not_a_composition() -> None:
    with pytest.raises(CompositeResponseError):
        _compose([_worker("b0", "anthropic", "claude-opus", "Linked.")])


def test_an_undeclared_strategy_is_refused() -> None:
    with pytest.raises(CompositeResponseError):
        _compose(_agreeing_fan(), strategy="WHATEVER_LOOKS_BEST")


def test_the_composite_declares_its_own_schema_and_digest() -> None:
    composite = _compose(_agreeing_fan())
    assert composite["schema"] == COMPOSITE_SCHEMA
    assert composite["composite_sha256"].startswith("sha256:")


# --- reachable from Ecosystem Chat, not only from a console -----------------


def test_chat_can_request_a_composition_and_read_its_verification() -> None:
    """Test 6 starts with a query posed in Chat, so Chat must reach composition."""
    from stegverse.ecosystem_chat_entry import (
        COMPOSE,
        COMPOSITION_VERIFICATION_FIELDS,
        SCHEMA,
        console_equivalent_request,
        validate_chat_entry,
    )

    fan = _agreeing_fan()
    entry = validate_chat_entry(
        {
            "schema": SCHEMA,
            "operation": COMPOSE,
            "composition_id": "CMP-CHAT-1",
            "fan_journey_id": FAN,
            "strategy": STRATEGY_UNANIMOUS,
            "components": fan,
        }
    )
    assert entry["capability"] == "COMPOSE_GOVERNED_RESPONSE"
    assert entry["composition_request"]["component_count"] == 3
    assert entry["verification"]["compare_fields"] == list(
        COMPOSITION_VERIFICATION_FIELDS
    )
    assert entry["verification"]["legible_without_a_console"] is True
    # Chat interfaces with the composer; it neither selects nor writes the answer.
    assert entry["composer_directive"]["composite_selected_by_chat"] is False
    assert entry["composer_directive"]["answer_generated_by_chat"] is False
    # And the request projects onto the console's own shape, not a Chat dialect.
    projected = console_equivalent_request(entry)
    assert projected["selection"] == COMPOSE
    assert projected["composition"]["fan_journey_id"] == FAN
    assert "manifest_receipt_id" not in projected


def test_the_fields_chat_shows_are_the_ones_that_settle_the_verification() -> None:
    """Every compare field must exist on a real composite plus its replay."""
    from stegverse.ecosystem_chat_entry import COMPOSITION_VERIFICATION_FIELDS

    fan = _agreeing_fan()
    composite = _compose(fan)
    available = dict(composite)
    available.update(reconstruct_governed_response(composite, fan))
    missing = [f for f in COMPOSITION_VERIFICATION_FIELDS if f not in available]
    assert missing == [], f"Chat is told to compare fields that do not exist: {missing}"


def test_chat_cannot_request_a_composition_of_one_worker() -> None:
    from stegverse.ecosystem_chat_entry import COMPOSE, SCHEMA, validate_chat_entry

    with pytest.raises(ValueError):
        validate_chat_entry(
            {
                "schema": SCHEMA,
                "operation": COMPOSE,
                "composition_id": "CMP-CHAT-2",
                "fan_journey_id": FAN,
                "components": [_worker("b0", "anthropic", "claude-opus", "Linked.")],
            }
        )


def test_chat_cannot_request_an_undeclared_strategy() -> None:
    from stegverse.ecosystem_chat_entry import COMPOSE, SCHEMA, validate_chat_entry

    with pytest.raises(ValueError):
        validate_chat_entry(
            {
                "schema": SCHEMA,
                "operation": COMPOSE,
                "composition_id": "CMP-CHAT-3",
                "fan_journey_id": FAN,
                "strategy": "PICK_THE_BEST_ONE",
                "components": _agreeing_fan(),
            }
        )


# --- the relation is bound to the composition it backs, or says it is not -----
#
# The composite recorded two booleans about its relation: supplied, and valid.
# Neither said which relation, nor what that relation had been validated over, so
# one record satisfied a pair and a dozen alike and satisfied any composition_id.
# These pin the binding, at the arity where its absence matters.


CID = "CMP-TEST6"


def _bound_relation(components, *, composition_id=CID):
    """The relation a fan of these components would actually be validated over."""
    relation = dict(VALID_RELATION)
    relation[COVERS_COMPOSITION_ID] = composition_id
    relation[COVERS_COMPONENT_IDS] = sorted(str(c["journey_id"]) for c in components)
    return relation


def test_the_composite_records_which_relation_backed_it() -> None:
    """A verifier could not previously tell which relation to go and check."""
    composite = _compose(_agreeing_fan())
    assert composite["joint_relation_id"] == "REL-TEST6-001"


def test_a_bound_relation_still_yields_a_governed_claim_and_reports_the_binding() -> None:
    fan = _agreeing_fan()
    composite = _compose(fan, relation=_bound_relation(fan))
    assert composite["disposition"] == DISPOSITION_GOVERNED
    assert composite["governed_claim"] is True
    assert composite["relation_binding_verified"] is True
    assert composite["relation_coverage"]["coverage"] == COVERAGE_BOUND
    assert composite["relation_coverage"]["actual_arity"] == 3


def test_an_unmanifested_composition_is_not_a_governed_claim() -> None:
    """Governance covers all output, and here it is the simple kind: the request
    either has the right manifest shape or it does not.

    With no journey, nothing states which components should exist, so there is
    nothing to check the composition against. The answer is still returned and
    still attributed; only the claim is withheld -- the same standing as a
    composition with no relation at all.
    """
    composite = _compose(_agreeing_fan(), journey=_UNMANIFESTED)
    assert composite["disposition"] == DISPOSITION_RELATION_UNRESOLVED
    assert composite["governed_claim"] is False
    assert composite["relation_binding_verified"] is False
    assert composite["relation_coverage"]["coverage"] == COVERAGE_UNDECLARED
    assert composite["composite_answer"] == "The return leg is predecessor-linked."


def test_a_manifested_composition_is_governed_from_the_requests_own_shape() -> None:
    """The manifest declared these three branches, so the answer is governed."""
    composite = _compose(_agreeing_fan())
    assert composite["disposition"] == DISPOSITION_GOVERNED
    assert composite["governed_claim"] is True
    assert composite["relation_binding_verified"] is True
    assert composite["relation_coverage"]["coverage"] == COVERAGE_BOUND
    assert composite["relation_coverage"]["basis"] == BASIS_MANIFEST_DECLARED


def test_a_manifest_declaring_more_branches_than_arrived_is_not_governed() -> None:
    """A subset of a declared branch set is not the set the manifest stated."""
    fan = _agreeing_fan()
    composite = _compose(fan[:2], journey=_journey_for(fan))
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert FAILURE_RELATION_COVERAGE in composite["failure_codes"]
    assert composite["relation_coverage"]["mismatch_reasons"] == [MISMATCH_JOURNEY_BRANCHES]


def test_a_relation_for_two_branches_does_not_cover_three() -> None:
    """2 to N: a relation validated over a subset must not carry the superset."""
    fan = _agreeing_fan()
    relation = _bound_relation(fan[:2])
    composite = _compose(fan, relation=relation)

    assert composite["joint_relation_valid"] is True, "the record itself is well formed"
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert FAILURE_RELATION_COVERAGE in composite["failure_codes"]
    assert composite["relation_coverage"]["mismatch_reasons"] == [MISMATCH_COMPONENTS]
    assert composite["relation_coverage"]["declared_arity"] == 2
    assert composite["relation_coverage"]["actual_arity"] == 3
    assert composite["separability"]["subset_relation_covers_superset_composition"] is False


def test_a_relation_for_another_composition_does_not_cover_this_fan() -> None:
    fan = _agreeing_fan()
    composite = _compose(fan, relation=_bound_relation(fan, composition_id="OTHER-CMP"))
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert FAILURE_RELATION_COVERAGE in composite["failure_codes"]


def test_a_bound_composite_reconstructs_including_its_coverage_verdict() -> None:
    """Replay must reproduce the binding, not a generic stand-in relation."""
    fan = _agreeing_fan()
    composite = _compose(fan, relation=_bound_relation(fan))
    replay = reconstruct_governed_response(composite, fan)

    # The comparison covers every recorded field but the digest itself, so an
    # equal digest is the statement that the coverage verdict replayed too.
    assert replay["reconstruction_status"] == "RECONSTRUCTED"
    assert replay["reconstructed_composite_sha256"] == composite["composite_sha256"]
    assert composite["relation_binding_verified"] is True
    assert composite["joint_relation_id"] == "REL-TEST6-001"


def test_a_coverage_mismatch_reconstructs_as_the_same_failure() -> None:
    """A fail-closed composite replays to the same verdict, not to a pass."""
    fan = _agreeing_fan()
    composite = _compose(fan, relation=_bound_relation(fan[:2]))
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    replay = reconstruct_governed_response(composite, fan)
    assert replay["reconstruction_status"] == "RECONSTRUCTED"
    assert replay["reconstructed_composite_sha256"] == composite["composite_sha256"]


def test_claiming_a_binding_the_components_do_not_support_diverges() -> None:
    """The recorded coverage is inside the digest, so it cannot be edited after."""
    fan = _agreeing_fan()
    composite = _compose(fan, relation=_bound_relation(fan[:2]))
    forged = copy.deepcopy(composite)
    forged["relation_binding_verified"] = True
    forged["relation_coverage"] = dict(
        forged["relation_coverage"], coverage=COVERAGE_BOUND, mismatch_reasons=[]
    )
    replay = reconstruct_governed_response(forged, fan)
    assert replay["reconstruction_status"] == "DIVERGED"
    assert replay["reconstructed"] is False


def test_a_relation_naming_another_journey_does_not_cover_this_one() -> None:
    """Naming a journey is a claim about which manifest, and it must be this one."""
    fan = _agreeing_fan()
    relation = dict(VALID_RELATION)
    relation[COVERS_JOURNEY_ID] = "SOME-OTHER-FAN"
    composite = _compose(fan, relation=relation)
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert composite["relation_coverage"]["mismatch_reasons"] == [MISMATCH_JOURNEY]
    assert composite["relation_coverage"]["declared_journey_id"] == "SOME-OTHER-FAN"


def test_a_relation_naming_a_journey_that_was_not_supplied_cannot_be_checked() -> None:
    """Unverifiable is not the same as verified, so it does not pass."""
    fan = _agreeing_fan()
    relation = dict(VALID_RELATION)
    relation[COVERS_JOURNEY_ID] = FAN
    composite = _compose(fan, relation=relation, journey=_UNMANIFESTED)
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert composite["relation_coverage"]["mismatch_reasons"] == [MISMATCH_JOURNEY_UNAVAILABLE]


def test_an_unmanifested_composition_can_still_be_bound_by_enumeration() -> None:
    """The explicit basis, for a composition that has no journey to read."""
    fan = _agreeing_fan()
    composite = _compose(fan, relation=_bound_relation(fan), journey=_UNMANIFESTED)
    assert composite["disposition"] == DISPOSITION_GOVERNED
    assert composite["relation_binding_verified"] is True
    assert composite["relation_coverage"]["basis"] == BASIS_ENUMERATED


def test_a_relation_contradicting_the_manifest_fails_rather_than_averaging() -> None:
    """Both bases declared, only one holds: the composition is not governed."""
    fan = _agreeing_fan()
    composite = _compose(fan, relation=_bound_relation(fan[:2]))
    assert composite["relation_coverage"]["coverage"] == COVERAGE_MISMATCHED
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED


# --- standing is current, never carried --------------------------------------
#
# Coverage says the relation is about this composition. It says nothing about
# whether the relation is still current, and the two are independent: a relation
# can cover this exact component set and have expired. The coverage check alone
# admitted that case, which is the hole these close.

NOW = "2026-09-30T04:00:00Z"


def _timed_relation(components, *, valid_from=None, expiration=None):
    relation = _bound_relation(components)
    if valid_from is not None:
        relation[VALID_FROM] = valid_from
    if expiration is not None:
        relation[EXPIRATION] = expiration
    return relation


def test_a_relation_with_no_window_is_governed_and_says_currency_was_not_checked() -> None:
    """Preserved: withdrawing this would ungovern every window-less relation."""
    composite = _compose(_agreeing_fan())
    assert composite["disposition"] == DISPOSITION_GOVERNED
    assert composite["relation_standing"]["standing"] == STANDING_WINDOW_UNDECLARED
    assert composite["relation_standing_verified"] is False
    assert "currency was not" in composite["relation_standing"]["limit"]


def test_a_relation_inside_its_declared_window_has_verified_standing() -> None:
    fan = _agreeing_fan()
    composite = _compose(
        fan,
        relation=_timed_relation(fan, valid_from="2026-09-01T00:00:00Z",
                                 expiration="2026-12-31T00:00:00Z"),
        evaluated_at=NOW,
    )
    assert composite["disposition"] == DISPOSITION_GOVERNED
    assert composite["relation_standing"]["standing"] == STANDING_WITHIN_WINDOW
    assert composite["relation_standing_verified"] is True


def test_an_expired_relation_that_still_covers_this_composition_fails_closed() -> None:
    """The hole. Coverage holds; standing does not; the old check saw only coverage."""
    fan = _agreeing_fan()
    composite = _compose(
        fan, relation=_timed_relation(fan, expiration="2026-01-01T00:00:00Z"),
        evaluated_at=NOW,
    )

    # Coverage genuinely passes -- this relation is about exactly these branches.
    assert composite["relation_coverage"]["coverage"] == COVERAGE_BOUND
    assert composite["relation_binding_verified"] is True
    # Standing is what refuses it.
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert FAILURE_RELATION_STANDING in composite["failure_codes"]
    assert composite["relation_standing"]["standing"] == STANDING_OUTSIDE_WINDOW
    assert composite["relation_standing"]["stale_reasons"] == [STALE_EXPIRED]
    assert composite["separability"]["prior_validity_is_current_standing"] is False


def test_a_relation_not_yet_valid_fails_closed() -> None:
    fan = _agreeing_fan()
    composite = _compose(
        fan, relation=_timed_relation(fan, valid_from="2027-01-01T00:00:00Z"),
        evaluated_at=NOW,
    )
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert composite["relation_standing"]["stale_reasons"] == [STALE_NOT_YET_VALID]


def test_a_declared_window_with_no_evaluation_time_is_not_treated_as_current() -> None:
    """Unverifiable is not verified, so it fails closed rather than passing."""
    fan = _agreeing_fan()
    composite = _compose(fan, relation=_timed_relation(fan, expiration="2027-01-01T00:00:00Z"))
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert composite["relation_standing"]["standing"] == STANDING_UNCHECKABLE
    assert composite["relation_standing"]["stale_reasons"] == [STALE_NO_EVALUATION_TIME]


def test_an_unparseable_window_fails_closed_rather_than_being_ignored() -> None:
    fan = _agreeing_fan()
    composite = _compose(fan, relation=_timed_relation(fan, expiration="whenever"),
                         evaluated_at=NOW)
    assert composite["disposition"] == DISPOSITION_FAIL_CLOSED
    assert composite["relation_standing"]["stale_reasons"] == [STALE_UNPARSEABLE]


def test_verified_standing_names_the_surfaces_it_did_not_check() -> None:
    """A verified window must not read as verified authority."""
    fan = _agreeing_fan()
    composite = _compose(
        fan, relation=_timed_relation(fan, expiration="2027-01-01T00:00:00Z"),
        evaluated_at=NOW,
    )
    standing = composite["relation_standing"]
    assert standing["standing_verified"] is True
    assert standing["surfaces_not_checkable_here"] == list(SURFACES_NOT_CHECKABLE_HERE)
    for surface in ("actor_surface", "policy_surface", "delegation_surface"):
        assert surface in standing["surfaces_not_checkable_here"]


def test_an_expired_composite_replays_to_the_same_refusal() -> None:
    """Replay asks the standing question at the recorded instant, not at now."""
    fan = _agreeing_fan()
    composite = _compose(
        fan, relation=_timed_relation(fan, expiration="2026-01-01T00:00:00Z"),
        evaluated_at=NOW,
    )
    replay = reconstruct_governed_response(composite, fan)
    assert replay["reconstruction_status"] == "RECONSTRUCTED"
    assert replay["reconstructed_composite_sha256"] == composite["composite_sha256"]


def test_a_composite_edited_to_claim_standing_it_lacks_diverges() -> None:
    fan = _agreeing_fan()
    composite = _compose(
        fan, relation=_timed_relation(fan, expiration="2026-01-01T00:00:00Z"),
        evaluated_at=NOW,
    )
    forged = copy.deepcopy(composite)
    forged["relation_standing_verified"] = True
    forged["relation_standing"] = dict(
        forged["relation_standing"], standing=STANDING_WITHIN_WINDOW, stale_reasons=[]
    )
    replay = reconstruct_governed_response(forged, fan)
    assert replay["reconstruction_status"] == "DIVERGED"
    assert replay["reconstructed"] is False
