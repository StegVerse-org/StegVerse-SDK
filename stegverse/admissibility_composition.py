"""Deterministic n>1 admissibility composition checks.

Component admissibility is not lifted into joint admissibility. A composition is
a distinct candidate relation and must carry its own validated relation record.
This SDK helper is side-effect free and non-authorizing; it exists to expose
relation coverage and to falsify unsafe separability assumptions.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from .admissibility import stable_hash, utc_now

COMPOSITION_RESULT_SCHEMA = "stegverse.governed_admissibility.composition_result.v1"
JOINT_RELATION_SCHEMA = "stegverse.governed_admissibility.joint_relation.v1"


def _valid_local_result(result: Mapping[str, Any]) -> bool:
    supplied = result.get("local_receipt_hash")
    if not isinstance(supplied, str) or not supplied.startswith("sha256:"):
        return False
    candidate = dict(result)
    candidate.pop("local_receipt_hash", None)
    return supplied == stable_hash(candidate)


def _component_admissible(result: Mapping[str, Any]) -> bool:
    classification = result.get("classification")
    if not isinstance(classification, Mapping):
        return False
    decision = str(classification.get("decision") or "")
    next_state = str(classification.get("allowed_next_state") or "")
    return decision.startswith("ALLOW_") and next_state not in {"", "hold", "fail_closed"}


def _validated_joint_relation(relation: Mapping[str, Any] | None) -> bool:
    if not isinstance(relation, Mapping):
        return False
    if relation.get("schema") != JOINT_RELATION_SCHEMA:
        return False
    if str(relation.get("relation_status") or "") != "validated":
        return False
    for key in ("relation_id", "authority_source"):
        if not isinstance(relation.get(key), str) or not str(relation.get(key)).strip():
            return False
    return (
        relation.get("evidence_posture") == "receipt_backed"
        and relation.get("replay_posture") == "receipt_backed"
    )


def evaluate_admissibility_composition(
    components: Sequence[Mapping[str, Any]],
    *,
    composition_id: str,
    joint_consequence_level: str,
    joint_relation: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Evaluate whether a set of component results has a covered joint relation.

    This function deliberately does not infer composition admissibility from
    component ALLOW dispositions. A validated joint relation is a separate
    prerequisite. Missing/tampered components or absent joint relation coverage
    fail closed.
    """
    cid = str(composition_id or "").strip()
    if not cid:
        raise ValueError("composition_id_required")
    if len(components) < 2:
        raise ValueError("composition_requires_at_least_two_components")

    consequence = str(joint_consequence_level or "medium").lower()
    high_consequence = consequence in {"high", "critical"}

    component_summaries: list[Dict[str, Any]] = []
    component_integrity = True
    all_individually_admissible = True
    for index, component in enumerate(components):
        valid = _valid_local_result(component)
        admissible = valid and _component_admissible(component)
        component_integrity = component_integrity and valid
        all_individually_admissible = all_individually_admissible and admissible
        classification = component.get("classification") if isinstance(component.get("classification"), Mapping) else {}
        component_summaries.append(
            {
                "index": index,
                "input_object_id": component.get("input_object_id"),
                "receipt_hash": component.get("local_receipt_hash"),
                "integrity_valid": valid,
                "individually_admissible": admissible,
                "decision": classification.get("decision"),
                "allowed_next_state": classification.get("allowed_next_state"),
            }
        )

    joint_relation_valid = _validated_joint_relation(joint_relation)

    if not component_integrity:
        decision = "FAIL_CLOSED"
        allowed_next_state = "fail_closed"
        relation = {
            "status": "resolved",
            "maturity_class": "known_guard",
            "execution_posture": "non_authorizing_fail_closed",
            "basis": "component_receipt_integrity_failure",
        }
        required_follow_up = ["Repair or reproduce every component receipt before composition evaluation."]
    elif not all_individually_admissible:
        decision = "FAIL_CLOSED"
        allowed_next_state = "fail_closed"
        relation = {
            "status": "resolved",
            "maturity_class": "known_guard",
            "execution_posture": "non_authorizing_fail_closed",
            "basis": "one_or_more_components_not_individually_admissible",
        }
        required_follow_up = ["Composition cannot advance while any component is individually non-admissible."]
    elif not joint_relation_valid:
        decision = "FAIL_CLOSED"
        allowed_next_state = "fail_closed"
        relation = {
            "status": "unresolved",
            "maturity_class": "under_development",
            "execution_posture": "non_authorizing_fail_closed",
            "basis": "no_explicit_composition_admissibility_relation",
        }
        required_follow_up = [
            "Component admissibility does not imply composition admissibility; retain this composition as RELATION_UNRESOLVED until a governed joint relation is validated."
        ]
    else:
        decision = "ALLOW_WITH_POSTURE"
        allowed_next_state = "composition_relation_backed_claim"
        relation = {
            "status": "resolved",
            "maturity_class": "known_composition_with_posture",
            "execution_posture": "non_authorizing_relation_evidence_only",
            "basis": "validated_joint_relation_record",
            "relation_id": joint_relation.get("relation_id"),
        }
        required_follow_up = [
            "Keep the validated joint-relation record attached; this SDK result does not grant execution authority."
        ]

    result: Dict[str, Any] = {
        "schema": COMPOSITION_RESULT_SCHEMA,
        "evaluated_at": utc_now(),
        "mode": "sdk_local_admissibility_composition",
        "composition_id": cid,
        "component_count": len(components),
        "components": component_summaries,
        "component_integrity": component_integrity,
        "all_components_individually_admissible": all_individually_admissible,
        "joint_consequence_level": consequence,
        "high_consequence": high_consequence,
        "joint_relation_supplied": isinstance(joint_relation, Mapping),
        "joint_relation_valid": joint_relation_valid,
        "classification": {
            "decision": decision,
            "allowed_next_state": allowed_next_state,
            "required_follow_up": required_follow_up,
        },
        "relation": relation,
        "separability": {
            "component_admissibility_implies_composition_admissibility": False,
            "joint_relation_required": True,
        },
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_create_proof_authority": True,
            "does_not_grant_execution_authority": True,
            "does_not_execute_components": True,
        },
    }
    result["local_receipt_hash"] = stable_hash(result)
    return result
