"""Execution-boundary admissibility evidence for consequential transitions.

This module turns the SDK's existing point admissibility results into a bounded
n=1 falsification surface. Historical authorization is recorded separately from
continuing admissibility at the point of consequence. The helper is
side-effect-free and non-authorizing: callers may use the resulting disposition
as SDK evidence, while actual execution authority remains with the canonical
StegCore/StegGate/Master Records path.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from .admissibility import stable_hash, utc_now

EXECUTION_BOUNDARY_CASE_SCHEMA = "stegverse.governed_admissibility.execution_boundary_case.v1"
EXECUTION_BOUNDARY_RESULT_SCHEMA = "stegverse.governed_admissibility.execution_boundary_result.v1"


def _valid_local_result(result: Mapping[str, Any]) -> bool:
    supplied = result.get("local_receipt_hash")
    if not isinstance(supplied, str) or not supplied.startswith("sha256:"):
        return False
    candidate = dict(result)
    candidate.pop("local_receipt_hash", None)
    return supplied == stable_hash(candidate)


def _classification(result: Mapping[str, Any]) -> Mapping[str, Any]:
    value = result.get("classification")
    return value if isinstance(value, Mapping) else {}


def _is_admissible(result: Mapping[str, Any]) -> bool:
    classification = _classification(result)
    decision = str(classification.get("decision") or "")
    next_state = str(classification.get("allowed_next_state") or "")
    return decision.startswith("ALLOW_") and next_state not in {"", "hold", "fail_closed"}


def _authority_source(result: Mapping[str, Any]) -> str:
    value = _classification(result).get("authority_source")
    return str(value or "").strip()


def _validate_transition_chain(transitions: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    if not transitions:
        return {
            "valid": False,
            "material_change_observed": False,
            "all_material_transitions_observed": False,
            "basis": "no_intervening_transition_evidence",
        }

    material = [item for item in transitions if bool(item.get("materially_relevant"))]
    if not material:
        return {
            "valid": False,
            "material_change_observed": False,
            "all_material_transitions_observed": False,
            "basis": "no_materially_relevant_state_change",
        }

    for item in material:
        required = ("transition_id", "from_state_hash", "to_state_hash", "observed_at")
        if any(not str(item.get(key) or "").strip() for key in required):
            return {
                "valid": False,
                "material_change_observed": True,
                "all_material_transitions_observed": False,
                "basis": "material_transition_evidence_incomplete",
            }
        if item.get("observed") is not True:
            return {
                "valid": False,
                "material_change_observed": True,
                "all_material_transitions_observed": False,
                "basis": "material_transition_not_observed",
            }

    for previous, current in zip(material, material[1:]):
        if str(previous.get("to_state_hash")) != str(current.get("from_state_hash")):
            return {
                "valid": False,
                "material_change_observed": True,
                "all_material_transitions_observed": True,
                "basis": "causal_transition_chain_discontinuous",
            }

    return {
        "valid": True,
        "material_change_observed": True,
        "all_material_transitions_observed": True,
        "basis": "material_transition_chain_observed",
        "first_state_hash": str(material[0].get("from_state_hash")),
        "boundary_state_hash": str(material[-1].get("to_state_hash")),
        "material_transition_ids": [str(item.get("transition_id")) for item in material],
    }


def evaluate_execution_boundary_case(case: Mapping[str, Any]) -> Dict[str, Any]:
    """Evaluate the minimum consequential execution-boundary falsification case.

    Expected case fields:
      - schema / case_id
      - candidate_transition.transition_id
      - initial_admissibility: SDK dynamic admissibility result
      - intervening_transitions: ordered observed state-transition evidence
      - boundary_admissibility: fresh SDK dynamic admissibility result
      - consequence: {status, alterable_at_boundary}

    The function does not execute or prevent an external action. It determines
    whether the submitted evidence establishes continuing admissibility and what
    the governed consequence disposition must be.
    """
    if case.get("schema") != EXECUTION_BOUNDARY_CASE_SCHEMA:
        raise ValueError("unexpected_execution_boundary_case_schema")

    case_id = str(case.get("case_id") or "").strip()
    if not case_id:
        raise ValueError("case_id_required")

    candidate = case.get("candidate_transition")
    if not isinstance(candidate, Mapping):
        raise ValueError("candidate_transition_required")
    transition_id = str(candidate.get("transition_id") or "").strip()
    if not transition_id:
        raise ValueError("candidate_transition_id_required")

    initial = case.get("initial_admissibility")
    boundary = case.get("boundary_admissibility")
    transitions = case.get("intervening_transitions")
    consequence = case.get("consequence")
    if not isinstance(initial, Mapping) or not isinstance(boundary, Mapping):
        raise ValueError("initial_and_boundary_admissibility_results_required")
    if not isinstance(transitions, Sequence) or isinstance(transitions, (str, bytes)):
        raise ValueError("intervening_transitions_must_be_a_sequence")
    if not isinstance(consequence, Mapping):
        raise ValueError("consequence_required")

    initial_integrity = _valid_local_result(initial)
    boundary_integrity = _valid_local_result(boundary)
    initial_admissible = initial_integrity and _is_admissible(initial)
    boundary_admissible = boundary_integrity and _is_admissible(boundary)
    chain = _validate_transition_chain(transitions)

    initial_authority = _authority_source(initial)
    boundary_authority = _authority_source(boundary)
    authority_held_constant = bool(initial_authority) and initial_authority == boundary_authority

    object_identity_preserved = (
        str(initial.get("input_object_id") or "") == transition_id
        and str(boundary.get("input_object_id") or "") == transition_id
    )

    consequence_status = str(consequence.get("status") or "pending").lower()
    alterable_at_boundary = consequence.get("alterable_at_boundary") is True

    evidence_complete = all(
        [
            initial_integrity,
            boundary_integrity,
            initial_admissible,
            chain.get("valid") is True,
            authority_held_constant,
            object_identity_preserved,
            alterable_at_boundary,
        ]
    )

    required_follow_up: list[str] = []
    if not initial_integrity:
        required_follow_up.append("Repair or reproduce the initial admissibility receipt.")
    if not boundary_integrity:
        required_follow_up.append("Repair or reproduce the boundary admissibility receipt.")
    if not initial_admissible:
        required_follow_up.append("The candidate must be initially admissible for this falsification case.")
    if chain.get("valid") is not True:
        required_follow_up.append(
            "Establish an observed, causally continuous materially relevant transition chain before consequence."
        )
    if not authority_held_constant:
        required_follow_up.append("Hold the original authority source constant across the test boundary.")
    if not object_identity_preserved:
        required_follow_up.append("Bind both admissibility evaluations to the same candidate transition id.")
    if not alterable_at_boundary:
        required_follow_up.append("Evaluate before the consequence becomes safely irreversible.")

    if not evidence_complete:
        decision = "FAIL_CLOSED"
        allowed_next_state = "fail_closed"
        basis = "execution_boundary_evidence_incomplete"
        continuing_admissibility_established = False
    elif boundary_admissible:
        decision = "PERMIT_CONSEQUENCE"
        allowed_next_state = "consequence_permitted_with_boundary_posture"
        basis = "continuing_admissibility_established_at_execution_boundary"
        continuing_admissibility_established = True
    else:
        decision = "PREVENT_CONSEQUENCE"
        allowed_next_state = "consequence_prevented"
        basis = "historical_authorization_does_not_establish_continuing_admissibility"
        continuing_admissibility_established = False

    if decision == "PERMIT_CONSEQUENCE":
        consequence_conforms = consequence_status in {"pending", "permitted", "executed"}
    elif decision in {"PREVENT_CONSEQUENCE", "FAIL_CLOSED"}:
        consequence_conforms = consequence_status in {"pending", "prevented", "blocked", "not_executed"}
    else:
        consequence_conforms = False

    if not evidence_complete:
        falsification_outcome = "INDETERMINATE_EVIDENCE_BOUNDARY"
    elif not consequence_conforms:
        falsification_outcome = "FAIL_CONSEQUENCE_NONCONFORMANCE"
    else:
        falsification_outcome = "PASS_MINIMUM_N1_BOUNDARY_CASE"

    result: Dict[str, Any] = {
        "schema": EXECUTION_BOUNDARY_RESULT_SCHEMA,
        "evaluated_at": utc_now(),
        "mode": "sdk_local_execution_boundary_evidence",
        "case_id": case_id,
        "candidate_transition_id": transition_id,
        "historical_authorization": {
            "authority_source": initial_authority or None,
            "held_constant": authority_held_constant,
            "initial_admissible": initial_admissible,
            "establishes_current_admissibility_by_itself": False,
        },
        "continuity": chain,
        "boundary_reassessment": {
            "receipt_integrity_valid": boundary_integrity,
            "same_candidate_transition": object_identity_preserved,
            "boundary_admissible": boundary_admissible,
            "continuing_admissibility_established": continuing_admissibility_established,
        },
        "consequence": {
            "status": consequence_status,
            "alterable_at_boundary": alterable_at_boundary,
            "conforms_to_boundary_disposition": consequence_conforms,
        },
        "classification": {
            "decision": decision,
            "allowed_next_state": allowed_next_state,
            "basis": basis,
            "required_follow_up": required_follow_up,
        },
        "falsification": {
            "minimum_case": "n=1",
            "outcome": falsification_outcome,
            "detects_changed_state": chain.get("material_change_observed") is True,
            "preserves_causal_relationship": chain.get("valid") is True,
            "reassesses_at_consequence": boundary_integrity,
            "distinguishes_history_from_current_admissibility": True,
            "consequence_accords_with_determination": consequence_conforms,
        },
        "evidence_standard": {
            "what_was_permitted": initial.get("local_receipt_hash"),
            "what_changed": chain.get("material_transition_ids", []),
            "what_system_observed": chain.get("boundary_state_hash"),
            "when_reassessed": boundary.get("evaluated_at"),
            "original_authority_still_applicable": authority_held_constant,
            "boundary_determination": _classification(boundary).get("decision"),
            "execution_disposition": decision,
            "independently_reconstructable": evidence_complete,
        },
        "boundary": {
            "does_not_execute_or_prevent_external_actions": True,
            "does_not_grant_execution_authority": True,
            "does_not_certify_domain_correctness": True,
            "canonical_execution_authority_remains_external": True,
        },
    }
    result["local_receipt_hash"] = stable_hash(result)
    return result
