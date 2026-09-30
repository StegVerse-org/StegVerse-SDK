"""One joint-relation record, and whether it covers the composition using it.

Two modules composed N things and each kept its own copy of the same relation
validator: ``admissibility_composition`` and ``governed_composite_response``.
The copies were logically identical, so a fix to one would silently not reach
the other. They now share this one.

The substantive part is coverage. Both modules refuse to lift *component*
admissibility into *composite* admissibility -- a validated joint relation is a
separate prerequisite. But the relation record itself carried no statement of
what it had been validated over, and neither validator asked. A single record
reading ``relation_status: validated`` satisfied a pair and a dozen equally, and
satisfied any composition_id. That is the same separability error one level up:
a relation validated for a subset was being lifted to a superset.

It was invisible at n=2, which is the only arity the original controls
validated (see tasks/SDK-ADMISSIBILITY-COMPOSITION-002.json:
``n2-negative-and-positive-controls``). Going from 2 to N is what exposes it.

So a relation may now declare what it covers, and a declared coverage is
checked against the composition in front of it. A relation that declares
nothing is still accepted -- withdrawing that would make an existing 3-LLM
governed composition ungoverned, which is a call for the goal owner, not a
detail of this check -- but the result says in the open that its relation is
not bound to the composition it is backing, rather than implying it is.

Opting in is therefore all-or-nothing: a record naming the composition but not
the components still does not pin arity, which is the hole. A partial
declaration is a mismatch, not a weaker kind of binding.

This module is side-effect free and non-authorizing. It reports whether a
record covers a composition; it does not validate the record's own authority,
which is the issuer's, nor grant execution authority to anything.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

JOINT_RELATION_SCHEMA = "stegverse.governed_admissibility.joint_relation.v1"

# What a relation optionally declares about its own scope.
COVERS_COMPOSITION_ID = "covers_composition_id"
COVERS_COMPONENT_IDS = "covers_component_ids"
COVERAGE_FIELDS = (COVERS_COMPOSITION_ID, COVERS_COMPONENT_IDS)

COVERAGE_BOUND = "BOUND_TO_THIS_COMPOSITION"
COVERAGE_UNDECLARED = "COVERAGE_UNDECLARED"
COVERAGE_MISMATCHED = "DOES_NOT_COVER_THIS_COMPOSITION"

MISMATCH_INCOMPLETE = "coverage_partially_declared_so_arity_is_not_pinned"
MISMATCH_COMPOSITION = "declared_coverage_names_a_different_composition"
MISMATCH_COMPONENTS = "declared_coverage_is_not_this_component_set"

UNDECLARED_LIMIT = (
    "This relation does not declare what it was validated over, so it cannot be "
    "checked against this composition. It is accepted as evidence that a joint "
    "relation exists, not as evidence that one covers these components at this "
    "arity. n=2 is the only arity the original composition controls validated."
)

BOUND_LIMIT = (
    "This relation declares the composition and component set it was validated "
    "over, and they match the composition being evaluated. That binds the record "
    "to this composition; it does not certify the composition is correct."
)


def validate_joint_relation(relation: Mapping[str, Any] | None) -> bool:
    """Structural validity of the record itself, unchanged from both copies.

    Says nothing about what the relation covers -- see evaluate_relation_coverage.
    """
    if not isinstance(relation, Mapping):
        return False
    if relation.get("schema") != JOINT_RELATION_SCHEMA:
        return False
    if str(relation.get("relation_status") or "") != "validated":
        return False
    for key in ("relation_id", "authority_source"):
        value = relation.get(key)
        if not isinstance(value, str) or not value.strip():
            return False
    return (
        relation.get("evidence_posture") == "receipt_backed"
        and relation.get("replay_posture") == "receipt_backed"
    )


def _declared_component_ids(relation: Mapping[str, Any]) -> list[str] | None:
    declared = relation.get(COVERS_COMPONENT_IDS)
    if declared is None:
        return None
    if isinstance(declared, str) or not isinstance(declared, Sequence):
        # A bare string would silently read as a sequence of characters.
        return []
    return sorted(str(item) for item in declared)


def evaluate_relation_coverage(
    relation: Mapping[str, Any] | None,
    *,
    composition_id: str,
    component_ids: Sequence[str],
) -> Dict[str, Any]:
    """Report whether ``relation`` covers this composition at this arity.

    ``component_ids`` identifies the components being composed -- input object
    ids for admissibility composition, branch journey ids for a governed
    composite response. Order does not matter; the comparison is on the set.
    """
    actual_ids = sorted(str(item) for item in component_ids)
    actual = {
        "actual_composition_id": str(composition_id),
        "actual_component_ids": actual_ids,
        "actual_arity": len(actual_ids),
    }

    if not isinstance(relation, Mapping):
        return {
            "coverage": COVERAGE_UNDECLARED,
            "binding_verified": False,
            "declared_composition_id": None,
            "declared_component_ids": None,
            "declared_arity": None,
            "mismatch_reasons": [],
            "limit": UNDECLARED_LIMIT,
            **actual,
        }

    declared_cid = relation.get(COVERS_COMPOSITION_ID)
    declared_ids = _declared_component_ids(relation)
    declared_any = any(field in relation for field in COVERAGE_FIELDS)

    result: Dict[str, Any] = {
        "declared_composition_id": declared_cid if isinstance(declared_cid, str) else None,
        "declared_component_ids": declared_ids,
        "declared_arity": None if declared_ids is None else len(declared_ids),
        **actual,
    }

    if not declared_any:
        result.update({
            "coverage": COVERAGE_UNDECLARED,
            "binding_verified": False,
            "mismatch_reasons": [],
            "limit": UNDECLARED_LIMIT,
        })
        return result

    reasons: list[str] = []
    # Opting in is all-or-nothing: naming the composition without naming the
    # components leaves arity unpinned, which is the hole this check exists for.
    if not isinstance(declared_cid, str) or not declared_cid.strip() or declared_ids is None:
        reasons.append(MISMATCH_INCOMPLETE)
    else:
        if declared_cid != str(composition_id):
            reasons.append(MISMATCH_COMPOSITION)
        if declared_ids != actual_ids:
            reasons.append(MISMATCH_COMPONENTS)

    if reasons:
        result.update({
            "coverage": COVERAGE_MISMATCHED,
            "binding_verified": False,
            "mismatch_reasons": reasons,
        })
        return result

    result.update({
        "coverage": COVERAGE_BOUND,
        "binding_verified": True,
        "mismatch_reasons": [],
        "limit": BOUND_LIMIT,
    })
    return result


__all__ = [
    "BOUND_LIMIT",
    "COVERAGE_BOUND",
    "COVERAGE_FIELDS",
    "COVERAGE_MISMATCHED",
    "COVERAGE_UNDECLARED",
    "COVERS_COMPONENT_IDS",
    "COVERS_COMPOSITION_ID",
    "JOINT_RELATION_SCHEMA",
    "MISMATCH_COMPONENTS",
    "MISMATCH_COMPOSITION",
    "MISMATCH_INCOMPLETE",
    "UNDECLARED_LIMIT",
    "evaluate_relation_coverage",
    "validate_joint_relation",
]
