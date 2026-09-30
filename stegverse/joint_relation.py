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
# A relation may instead name the governed journey whose manifest declares the
# branch set. All transitions are receipted and all transport is by governed
# manifest, so that manifest already states which components exist before any of
# them runs -- the set is determined, not observed. Naming the journey is
# therefore a checkable coverage, not a weaker one: the check derives the
# expected component set from the declared branches and compares.
COVERS_JOURNEY_ID = "covers_journey_id"
COVERAGE_FIELDS = (COVERS_COMPOSITION_ID, COVERS_COMPONENT_IDS, COVERS_JOURNEY_ID)

BASIS_ENUMERATED = "RELATION_ENUMERATED_THE_COMPONENT_SET"
BASIS_MANIFEST_DECLARED = "GOVERNED_MANIFEST_DECLARED_THE_BRANCH_SET"

COVERAGE_BOUND = "BOUND_TO_THIS_COMPOSITION"
COVERAGE_UNDECLARED = "COVERAGE_UNDECLARED"
COVERAGE_MISMATCHED = "DOES_NOT_COVER_THIS_COMPOSITION"

MISMATCH_INCOMPLETE = "coverage_partially_declared_so_arity_is_not_pinned"
MISMATCH_JOURNEY = "declared_coverage_names_a_different_journey"
MISMATCH_JOURNEY_BRANCHES = "components_are_not_the_branch_set_the_manifest_declared"
MISMATCH_JOURNEY_UNAVAILABLE = "relation_names_a_journey_but_no_journey_was_supplied_to_check_it"
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


def derive_component_ids_from_journey(journey: Mapping[str, Any] | None) -> list[str] | None:
    """The component ids a governed journey's manifest declares, or None.

    A branch of journey ``J`` is component ``"J:<branch_id>"`` -- the identity
    the composite already relies on. Returns None when the journey does not
    determine a set: no journey, no branch list, or a ``branch_count`` that
    disagrees with the branches enumerated, which is a malformed manifest rather
    than a coverage question.
    """
    if not isinstance(journey, Mapping):
        return None
    journey_id = journey.get("journey_id")
    branches = journey.get("branches")
    if not isinstance(journey_id, str) or not journey_id.strip():
        return None
    if not isinstance(branches, list) or not branches:
        return None
    declared_count = journey.get("branch_count")
    if isinstance(declared_count, int) and declared_count != len(branches):
        return None
    ids: list[str] = []
    for branch in branches:
        if not isinstance(branch, Mapping):
            return None
        branch_id = branch.get("branch_id")
        if not isinstance(branch_id, str) or not branch_id.strip():
            return None
        ids.append(f"{journey_id}:{branch_id}")
    return sorted(ids)


def evaluate_relation_coverage(
    relation: Mapping[str, Any] | None,
    *,
    composition_id: str,
    component_ids: Sequence[str],
    journey: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Report whether ``relation`` covers this composition at this arity.

    ``component_ids`` identifies the components being composed -- input object
    ids for admissibility composition, branch journey ids for a governed
    composite response. Order does not matter; the comparison is on the set.

    ``journey`` is the governed journey whose manifest declared the branches. A
    relation naming that journey is checked against the set the manifest states,
    so coverage does not have to be enumerated by hand to be verified. Every
    basis a relation declares must hold.
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
            "declared_journey_id": None,
            "basis": None,
            "mismatch_reasons": [],
            "limit": UNDECLARED_LIMIT,
            **actual,
        }

    declared_cid = relation.get(COVERS_COMPOSITION_ID)
    declared_ids = _declared_component_ids(relation)
    declared_journey = relation.get(COVERS_JOURNEY_ID)
    has_journey = isinstance(declared_journey, str) and bool(declared_journey.strip())
    has_enumerated = any(
        field in relation for field in (COVERS_COMPOSITION_ID, COVERS_COMPONENT_IDS)
    )
    # A supplied journey declares the set on the manifest's behalf, so coverage is
    # undeclared only when neither the manifest nor the relation states one.
    declared_any = (
        any(field in relation for field in COVERAGE_FIELDS)
        or derive_component_ids_from_journey(journey) is not None
    )

    result: Dict[str, Any] = {
        "declared_composition_id": declared_cid if isinstance(declared_cid, str) else None,
        "declared_component_ids": declared_ids,
        "declared_arity": None if declared_ids is None else len(declared_ids),
        "declared_journey_id": declared_journey if has_journey else None,
        **actual,
    }

    if not declared_any:
        result.update({
            "coverage": COVERAGE_UNDECLARED,
            "binding_verified": False,
            "basis": None,
            "mismatch_reasons": [],
            "limit": UNDECLARED_LIMIT,
        })
        return result

    reasons: list[str] = []
    bases: list[str] = []

    # The manifest is the binding. A manifested request either has the right
    # shape -- a journey whose declared branches are exactly these components --
    # or it does not; nothing further has to opt in for the binding to be
    # checkable. A relation may still name the journey, and then it must be this
    # one.
    derived = derive_component_ids_from_journey(journey)
    if derived is not None:
        result["derived_component_ids"] = derived
        journey_id = journey.get("journey_id")
        if has_journey and journey_id != declared_journey:
            reasons.append(MISMATCH_JOURNEY)
        elif derived != actual_ids:
            # The manifest stated a branch set and these are not it: a subset, a
            # superset, or branches from elsewhere.
            reasons.append(MISMATCH_JOURNEY_BRANCHES)
        else:
            bases.append(BASIS_MANIFEST_DECLARED)
    elif has_journey:
        # The relation names a journey but none was supplied to check it against.
        reasons.append(MISMATCH_JOURNEY_UNAVAILABLE)

    if has_enumerated:
        # Enumerating is all-or-nothing: naming the composition without naming
        # the components leaves arity unpinned, which is the hole this exists for.
        if not isinstance(declared_cid, str) or not declared_cid.strip() or declared_ids is None:
            reasons.append(MISMATCH_INCOMPLETE)
        else:
            if declared_cid != str(composition_id):
                reasons.append(MISMATCH_COMPOSITION)
            if declared_ids != actual_ids:
                reasons.append(MISMATCH_COMPONENTS)
            if not reasons:
                bases.append(BASIS_ENUMERATED)

    if reasons:
        result.update({
            "coverage": COVERAGE_MISMATCHED,
            "binding_verified": False,
            "basis": None,
            "mismatch_reasons": reasons,
        })
        return result

    result.update({
        "coverage": COVERAGE_BOUND,
        "binding_verified": True,
        "basis": bases[0] if len(bases) == 1 else "+".join(sorted(bases)),
        "mismatch_reasons": [],
        "limit": BOUND_LIMIT,
    })
    return result


__all__ = [
    "BASIS_ENUMERATED",
    "BASIS_MANIFEST_DECLARED",
    "BOUND_LIMIT",
    "COVERAGE_BOUND",
    "COVERAGE_FIELDS",
    "COVERAGE_MISMATCHED",
    "COVERAGE_UNDECLARED",
    "COVERS_COMPONENT_IDS",
    "COVERS_COMPOSITION_ID",
    "COVERS_JOURNEY_ID",
    "JOINT_RELATION_SCHEMA",
    "MISMATCH_COMPONENTS",
    "MISMATCH_COMPOSITION",
    "MISMATCH_INCOMPLETE",
    "MISMATCH_JOURNEY",
    "MISMATCH_JOURNEY_BRANCHES",
    "MISMATCH_JOURNEY_UNAVAILABLE",
    "UNDECLARED_LIMIT",
    "derive_component_ids_from_journey",
    "evaluate_relation_coverage",
    "validate_joint_relation",
]
