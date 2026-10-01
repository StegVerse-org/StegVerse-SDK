"""Refuse a substitute principal rather than running one that is well-formed.

The dangerous substitution is not the broken one. It is the one that is
available, well-intentioned and produces well-formed output under the identity
of a condition it does not satisfy: nothing errors, a result exists, and the
result belongs to a different experiment than the one it is filed under.

So a condition declares the principal class it requires and the prerequisites
that class must have established. A candidate presents its class and what it
has established. When the required class is unavailable, or available with a
prerequisite unmet, this refuses and emits a receipt naming both the missing
prerequisite and every substitute it refused by name. No alternate class
executes, however well-formed it is.

Refusing a substitute is not a judgement on it. An alternate class may be a
legitimate principal for its own declaration; it is only refused as a stand-in
for this one, and the receipt says so rather than implying the alternate is
invalid. What it may never do is materialize its result into this declaration's
lane.

A reachable alternate is reported even when the required class is established,
because a substitution route that exists is worth recording before it is taken
under time pressure rather than after.

Ordering is structural rather than procedural.
``execute_under_principal_class_conformance`` holds the executor and invokes it
only on conformance, so a non-conforming principal cannot run by a caller
forgetting to check first.

Generalized: the declaration, the candidates and the executor are all supplied
by the caller. This module declares no principal class of its own, names no
experiment, and carries no framework identifier.

Non-authorizing. It resolves and reports: it starts no runtime, establishes no
prerequisite, relaxes no declaration and observes no execution.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Iterable, Mapping

SCHEMA = "stegverse.sdk.principal-class-conformance/v1"
DECLARATION_SCHEMA = "stegverse.sdk.required-principal-class/v1"
RECEIPT_SCHEMA = "stegverse.sdk.principal-class-refusal-receipt/v1"

CLASS_ESTABLISHED = "REQUIRED_PRINCIPAL_CLASS_ESTABLISHED"
CLASS_UNAVAILABLE = "REQUIRED_PRINCIPAL_CLASS_UNAVAILABLE"
PREREQUISITE_NOT_ESTABLISHED = "REQUIRED_PRINCIPAL_CLASS_PREREQUISITE_NOT_ESTABLISHED"
SUBSTITUTE_REFUSED = "SUBSTITUTE_PRINCIPAL_CLASS_REFUSED"
UNDECLARED_CLASS_OFFERED = "UNRECOGNIZED_PRINCIPAL_CLASS_OFFERED"
DECLARATION_ALTERED = "FROZEN_PRINCIPAL_CLASS_DECLARATION_ALTERED_AFTER_FREEZE"

CONFORMS = "PRINCIPAL_CLASS_CONFORMS"
REFUSED = "PRINCIPAL_CLASS_SUBSTITUTION_REFUSED"
EXECUTION_WITHHELD = "PRINCIPAL_NOT_EXECUTED_CLASS_CONFORMANCE_REFUSED"

RETRY_ENTRYPOINT = "stegverse.principal_class_conformance.resolve_principal_class"

AUTHORITY_BOUNDARY = {
    "resolution_grants_authority": False,
    "resolution_starts_a_runtime": False,
    "resolution_establishes_a_prerequisite": False,
    "resolution_may_relax_the_declaration": False,
    "resolution_may_admit_a_substitute": False,
    "conformance_implies_execution_observed": False,
    "conformance_implies_readiness_of_other_gates": False,
    "refusal_invalidates_the_substitute_itself": False,
}

_REPAIRS = {
    CLASS_UNAVAILABLE: (
        "make the declared principal class available, or freeze a declaration that "
        "requires a class that is; an unavailable required class is not a reason to "
        "run a different one"),
    PREREQUISITE_NOT_ESTABLISHED: (
        "establish the named prerequisites for the declared class before invoking the "
        "principal; a class present without its prerequisites is not that class"),
    SUBSTITUTE_REFUSED: (
        "run this substitute under its own declaration and its own identifier if it is "
        "a legitimate principal there; it may never stand in for this declaration"),
    UNDECLARED_CLASS_OFFERED: (
        "add the offered class to the declaration's recognized classes deliberately, or "
        "withdraw it; an unrecognized class is read, never inferred into the set"),
    DECLARATION_ALTERED: (
        "restore the frozen declaration to the bytes its digest was taken over, or "
        "freeze a new declaration deliberately; never re-digest in place"),
}


class PrincipalClassRefused(ValueError):
    """The declaration or a candidate is malformed, so no resolution is possible."""


def _canonical(value: Any) -> Any:
    if isinstance(value, list):
        return [_canonical(item) for item in value]
    if isinstance(value, Mapping):
        return {key: _canonical(value[key]) for key in sorted(value)}
    return value


def _digest(value: Any) -> str:
    raw = json.dumps(_canonical(value), separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PrincipalClassRefused(label)
    return value.strip()


def declare_required_principal_class(
    *,
    declaration_id: str,
    required_class: str,
    prerequisites: Iterable[str],
    recognized_classes: Iterable[str],
) -> dict[str, Any]:
    """Freeze the principal class a condition requires and what it must establish.

    ``recognized_classes`` is every class the declaration knows exists, the
    required one included. A candidate outside that set is reported rather than
    treated as one more substitute, because an unknown class is a gap in the
    declaration, not a known alternative.
    """
    declaration_id = _text(declaration_id, "DECLARATION_ID_REQUIRED")
    required_class = _text(required_class, "REQUIRED_CLASS_REQUIRED")
    required_prerequisites = sorted({
        _text(item, "PREREQUISITE_MUST_BE_A_NON_EMPTY_STRING") for item in prerequisites})
    recognized = sorted({
        _text(item, "RECOGNIZED_CLASS_MUST_BE_A_NON_EMPTY_STRING")
        for item in recognized_classes} | {required_class})
    body = {
        "schema": DECLARATION_SCHEMA,
        "declaration_id": declaration_id,
        "required_principal_class": required_class,
        "required_prerequisites": required_prerequisites,
        "recognized_principal_classes": recognized,
        "substitution_permitted": False,
        "declaration_is_frozen": True,
        "authority_effect": "NONE_DECLARATION_ONLY",
    }
    return dict(body, declaration_sha256=_digest(body))


def _declaration_body(declaration: Mapping[str, Any]) -> dict[str, Any]:
    return _canonical({key: value for key, value in declaration.items()
                       if key != "declaration_sha256"})


def _candidates(candidates: Iterable[Any]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    read: list[dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            raise PrincipalClassRefused("CANDIDATE_MUST_BE_AN_OBJECT")
        principal_class = _text(candidate.get("principal_class"),
                                "CANDIDATE_PRINCIPAL_CLASS_REQUIRED")
        if principal_class in seen:
            raise PrincipalClassRefused(
                f"DUPLICATE_CANDIDATE_PRINCIPAL_CLASS:{principal_class}")
        seen.add(principal_class)
        established = sorted({str(item) for item in
                              (candidate.get("established_prerequisites") or ())})
        read.append({
            "principal_class": principal_class,
            "available": candidate.get("available") is True,
            "established_prerequisites": established,
            "runtime_ref": candidate.get("runtime_ref"),
        })
    read.sort(key=lambda item: item["principal_class"])
    return read


def _refusal(failed_predicate: str, *, owning_existing_goal: str,
             **detail: Any) -> dict[str, Any]:
    return dict({
        "failed_predicate": failed_predicate,
        "disposition": "FAIL_CLOSED",
        "required_evidence_or_repair": _REPAIRS[failed_predicate],
        "retry_entrypoint": RETRY_ENTRYPOINT,
        "owning_existing_goal": owning_existing_goal,
    }, **detail)


def resolve_principal_class(
    declaration: Mapping[str, Any],
    candidates: Iterable[Mapping[str, Any]],
    *,
    owning_existing_goal: str,
) -> dict[str, Any]:
    """Resolve whether the declared principal class is established.

    ALLOW only when the required class is available and every declared
    prerequisite is established on it. Any other available class is refused by
    name, and a reachable alternate is reported even on ALLOW.
    """
    owning_existing_goal = _text(owning_existing_goal, "OWNING_EXISTING_GOAL_REQUIRED")
    if not isinstance(declaration, Mapping):
        raise PrincipalClassRefused("DECLARATION_MUST_BE_AN_OBJECT")
    required_class = _text(declaration.get("required_principal_class"),
                           "DECLARATION_REQUIRED_CLASS_MISSING")

    refusals: list[dict[str, Any]] = []
    recomputed = _digest(_declaration_body(declaration))
    frozen = declaration.get("declaration_sha256")
    intact = recomputed == frozen
    if not intact:
        refusals.append(_refusal(
            DECLARATION_ALTERED, owning_existing_goal=owning_existing_goal,
            frozen_declaration_sha256=frozen, recomputed_declaration_sha256=recomputed))

    read = _candidates(candidates)
    recognized = {str(item) for item in
                  (declaration.get("recognized_principal_classes") or ())}
    required_prerequisites = [str(item) for item in
                              (declaration.get("required_prerequisites") or ())]

    required = next((c for c in read if c["principal_class"] == required_class), None)
    alternates = [c for c in read if c["principal_class"] != required_class]
    reachable_alternates = [c["principal_class"] for c in alternates if c["available"]]
    missing_prerequisites: list[str] = []
    required_established = False

    if intact:
        if required is None or not required["available"]:
            missing_prerequisites = list(required_prerequisites)
            refusals.append(_refusal(
                CLASS_UNAVAILABLE, owning_existing_goal=owning_existing_goal,
                required_principal_class=required_class,
                required_class_offered=required is not None,
                missing_prerequisites=missing_prerequisites))
        else:
            missing_prerequisites = sorted(
                set(required_prerequisites) - set(required["established_prerequisites"]))
            if missing_prerequisites:
                refusals.append(_refusal(
                    PREREQUISITE_NOT_ESTABLISHED,
                    owning_existing_goal=owning_existing_goal,
                    required_principal_class=required_class,
                    missing_prerequisites=missing_prerequisites,
                    established_prerequisites=required["established_prerequisites"]))
            else:
                required_established = True

        # An available alternate is refused by name only while the required
        # class is not established. Naming it is the point: an unlabelled
        # substitution route is what makes substitution happen.
        if not required_established:
            for alternate in alternates:
                if alternate["available"]:
                    refusals.append(_refusal(
                        SUBSTITUTE_REFUSED, owning_existing_goal=owning_existing_goal,
                        refused_principal_class=alternate["principal_class"],
                        refused_runtime_ref=alternate["runtime_ref"],
                        in_place_of_required_class=required_class,
                        substitute_may_run_under_its_own_declaration=True,
                        substitute_result_may_materialize_into_this_lane=False))

        for candidate in read:
            if candidate["principal_class"] not in recognized:
                refusals.append(_refusal(
                    UNDECLARED_CLASS_OFFERED, owning_existing_goal=owning_existing_goal,
                    offered_principal_class=candidate["principal_class"],
                    recognized_principal_classes=sorted(recognized)))

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "state": CONFORMS if not refusals else REFUSED,
        "disposition": "ALLOW" if not refusals else "FAIL_CLOSED",
        "declaration_id": declaration.get("declaration_id"),
        "declaration_sha256": frozen,
        "declaration_intact": intact,
        "required_principal_class": required_class,
        "required_principal_class_established": required_established,
        "missing_prerequisites": missing_prerequisites,
        "refused_substitute_classes": sorted(
            item["refused_principal_class"] for item in refusals
            if item["failed_predicate"] == SUBSTITUTE_REFUSED),
        "reachable_alternate_classes": sorted(reachable_alternates),
        "substitution_permitted": False,
        "refusals": refusals,
        "owning_existing_goal": owning_existing_goal,
        "authority_boundary": dict(AUTHORITY_BOUNDARY),
        "authority_effect": "NONE_CLASS_RESOLUTION_ONLY",
    }
    if refusals:
        # The receipt the gate requires: the missing prerequisite and the
        # refused substitute, in one record, each named.
        result["receipt_schema"] = RECEIPT_SCHEMA
        result["failed_predicate"] = REFUSED
        result["required_evidence_or_repair"] = (
            "establish the declared principal class and its prerequisites; a reachable "
            "alternate is not a fallback for this declaration")
        result["retry_entrypoint"] = RETRY_ENTRYPOINT
        result["receipt_sha256"] = _digest(
            {key: value for key, value in result.items() if key != "receipt_sha256"})
    return result


def execute_under_principal_class_conformance(
    declaration: Mapping[str, Any],
    candidates: Iterable[Mapping[str, Any]],
    *,
    owning_existing_goal: str,
    principal_executor: Callable[[Mapping[str, Any]], Any],
) -> dict[str, Any]:
    """Invoke the principal only if its declared class conforms, never otherwise.

    The executor is held rather than returned to, so a non-conforming principal
    cannot run by a caller forgetting to resolve the class first. The caller
    still owns what the executor does; this function owns only the ordering.
    """
    if not callable(principal_executor):
        raise PrincipalClassRefused("PRINCIPAL_EXECUTOR_REQUIRED")
    resolution = resolve_principal_class(
        declaration, candidates, owning_existing_goal=owning_existing_goal)
    if resolution["disposition"] != "ALLOW":
        return dict(resolution, principal_executed=False,
                    execution_state=EXECUTION_WITHHELD)
    executed = principal_executor(resolution)
    return dict(resolution, principal_executed=True, execution_reference=executed)
