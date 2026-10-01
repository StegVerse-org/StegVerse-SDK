"""Assert the resource surface actually served against a frozen declaration.

A readiness gate that checks the launcher is correct does not check that the
surface the launcher served is correct. Those are different predicates, and the
second is the one an experiment's condition rests on: a run whose served
resources differ from the frozen declaration has tested a different condition,
whatever the launcher did.

So the comparison is made against what was served, not against what was meant
to be served, and it is made before any evidence exists. Five divergence
classes fail closed, each named: a resource served but not declared, a resource
declared but not served, a declared resource whose content was substituted, a
resource served from cache, and a resource carrying provenance a prior attempt
must be excluded from.

The declaration is frozen by its own digest. A declaration edited after freezing
fails the assertion rather than silently widening it, because a surface
assertion that can be relaxed at the moment of asserting is not an assertion.

Ordering is structural rather than procedural. ``emit_under_served_surface_assertion``
holds the emitter and invokes it only on conformance, so a non-conforming
surface cannot emit evidence by a caller forgetting to check first.

Generalized: the declaration, the served surface and the emitter are all
supplied by the caller, so any evaluator can manifest this control for any
frozen condition. This module declares no resource set of its own.

Non-authorizing. It compares and reports: it serves no resource, substitutes
none, relaxes no declaration, and observes no runtime.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Iterable, Mapping

SCHEMA = "stegverse.sdk.served-surface-assertion/v1"
DECLARATION_SCHEMA = "stegverse.sdk.frozen-resource-surface/v1"

#: The five divergence classes a served surface may exhibit. Each fails closed.
EXTRA_SERVED = "EXTRA_RESOURCE_SERVED"
DECLARED_NOT_SERVED = "DECLARED_RESOURCE_NOT_SERVED"
CONTENT_SUBSTITUTED = "DECLARED_RESOURCE_CONTENT_SUBSTITUTED"
SERVED_FROM_CACHE = "RESOURCE_SERVED_FROM_CACHE"
POST_ATTEMPT_PROVENANCE = "RESOURCE_CARRIES_EXCLUDED_PRIOR_ATTEMPT_PROVENANCE"

DECLARATION_ALTERED = "FROZEN_DECLARATION_ALTERED_AFTER_FREEZE"

SURFACE_CONFORMS = "SERVED_SURFACE_EQUALS_FROZEN_DECLARATION"
SURFACE_DIVERGED = "SERVED_SURFACE_DIVERGED_FROM_FROZEN_DECLARATION"
EVIDENCE_WITHHELD = "EVIDENCE_NOT_EMITTED_SURFACE_ASSERTION_FAILED_CLOSED"

RETRY_ENTRYPOINT = "stegverse.served_surface_assertion.assert_served_surface"

AUTHORITY_BOUNDARY = {
    "assertion_grants_authority": False,
    "assertion_admits_execution": False,
    "assertion_serves_a_resource": False,
    "assertion_substitutes_a_resource": False,
    "assertion_may_relax_the_declaration": False,
    "conformance_implies_runtime_observation": False,
    "conformance_implies_readiness_of_other_gates": False,
}

_REPAIRS = {
    EXTRA_SERVED: (
        "remove the undeclared resource from the principal-readable surface, or "
        "freeze a new declaration that includes it and record why the condition changed"),
    DECLARED_NOT_SERVED: (
        "serve the declared resource, or freeze a new declaration without it; a "
        "declared resource that is absent is a different condition, not a lesser one"),
    CONTENT_SUBSTITUTED: (
        "serve the exact declared bytes; a resource whose content differs has "
        "substituted the condition under the same name"),
    SERVED_FROM_CACHE: (
        "serve the resource from its declared source so the bytes are the ones "
        "frozen, not ones retained from an earlier surface"),
    POST_ATTEMPT_PROVENANCE: (
        "exclude every artifact, output, receipt, summary, cache, derived "
        "representation and repair note of the prior attempt from the "
        "principal-accessible surface before the run begins"),
    DECLARATION_ALTERED: (
        "restore the frozen declaration to the bytes its digest was taken over, or "
        "freeze a new declaration deliberately; never re-digest in place"),
}


class ServedSurfaceRefused(ValueError):
    """The declaration or the served surface is malformed, so no comparison is possible."""


def _canonical(value: Any) -> Any:
    if isinstance(value, list):
        return [_canonical(item) for item in value]
    if isinstance(value, Mapping):
        return {key: _canonical(value[key]) for key in sorted(value)}
    return value


def _digest(value: Any) -> str:
    raw = json.dumps(_canonical(value), separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _resource_id(entry: Mapping[str, Any], label: str) -> str:
    value = entry.get("resource_id")
    if not isinstance(value, str) or not value.strip():
        raise ServedSurfaceRefused(f"{label}_RESOURCE_ID_REQUIRED")
    return value.strip()


def _content_sha256(entry: Mapping[str, Any], label: str) -> str:
    value = entry.get("content_sha256")
    if not isinstance(value, str) or not value.strip():
        raise ServedSurfaceRefused(f"{label}_CONTENT_SHA256_REQUIRED")
    return value.strip()


def _indexed(entries: Iterable[Any], label: str) -> dict[str, dict[str, Any]]:
    """Index resources by id, refusing a duplicate rather than collapsing it.

    A resource served twice is a malformed surface, not a divergence to be
    silently deduplicated into one.
    """
    indexed: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise ServedSurfaceRefused(f"{label}_RESOURCE_MUST_BE_AN_OBJECT")
        resource_id = _resource_id(entry, label)
        if resource_id in indexed:
            raise ServedSurfaceRefused(f"{label}_DUPLICATE_RESOURCE_ID:{resource_id}")
        indexed[resource_id] = dict(entry)
    return indexed


def declare_frozen_surface(
    resources: Iterable[Mapping[str, Any]],
    *,
    declaration_id: str,
    excluded_provenance: Iterable[str] = (),
) -> dict[str, Any]:
    """Freeze the principal-readable resource surface a condition declares.

    Each resource carries its ``resource_id`` and the ``content_sha256`` of the
    exact bytes the condition freezes. ``excluded_provenance`` names the prior
    attempts and lanes whose artifacts must not reach the surface at all.
    """
    if not isinstance(declaration_id, str) or not declaration_id.strip():
        raise ServedSurfaceRefused("DECLARATION_ID_REQUIRED")
    indexed = _indexed(resources, "DECLARED")
    if not indexed:
        raise ServedSurfaceRefused("DECLARED_SURFACE_MUST_NOT_BE_EMPTY")
    excluded = sorted({str(item).strip() for item in excluded_provenance if str(item).strip()})
    body = {
        "schema": DECLARATION_SCHEMA,
        "declaration_id": declaration_id.strip(),
        "resources": [
            {"resource_id": resource_id,
             "content_sha256": _content_sha256(entry, "DECLARED")}
            for resource_id, entry in sorted(indexed.items())
        ],
        "excluded_provenance": excluded,
        "declaration_is_frozen": True,
        "authority_effect": "NONE_DECLARATION_ONLY",
    }
    return dict(body, declaration_sha256=_digest(body))


def _declaration_body(declaration: Mapping[str, Any]) -> dict[str, Any]:
    body = {key: value for key, value in declaration.items() if key != "declaration_sha256"}
    return _canonical(body)


def _divergence(resource_id: str | None, failed_predicate: str, **detail: Any) -> dict[str, Any]:
    entry = {
        "resource_id": resource_id,
        "failed_predicate": failed_predicate,
        "disposition": "FAIL_CLOSED",
        "required_evidence_or_repair": _REPAIRS[failed_predicate],
        "retry_entrypoint": RETRY_ENTRYPOINT,
    }
    entry.update(detail)
    return entry


def assert_served_surface(
    declaration: Mapping[str, Any],
    served: Iterable[Mapping[str, Any]],
    *,
    owning_existing_goal: str,
) -> dict[str, Any]:
    """Compare the surface actually served against the frozen declaration.

    Returns ALLOW only when the served set equals the declared set exactly, every
    declared resource's content matches, nothing was served from cache, and no
    resource carries excluded prior-attempt provenance.
    """
    if not isinstance(owning_existing_goal, str) or not owning_existing_goal.strip():
        raise ServedSurfaceRefused("OWNING_EXISTING_GOAL_REQUIRED")
    if not isinstance(declaration, Mapping):
        raise ServedSurfaceRefused("DECLARATION_MUST_BE_AN_OBJECT")
    declared_entries = declaration.get("resources")
    if not isinstance(declared_entries, list) or not declared_entries:
        raise ServedSurfaceRefused("DECLARATION_RESOURCES_REQUIRED")

    divergences: list[dict[str, Any]] = []

    # The declaration's own integrity comes first: a comparison against an
    # altered declaration proves nothing, so it is never attempted.
    recomputed = _digest(_declaration_body(declaration))
    frozen_digest = declaration.get("declaration_sha256")
    declaration_intact = recomputed == frozen_digest
    if not declaration_intact:
        divergences.append(_divergence(
            None, DECLARATION_ALTERED,
            frozen_declaration_sha256=frozen_digest,
            recomputed_declaration_sha256=recomputed))

    declared = _indexed(declared_entries, "DECLARED")
    served_index = _indexed(served, "SERVED")
    excluded = {str(item) for item in (declaration.get("excluded_provenance") or ())}

    if declaration_intact:
        for resource_id in sorted(set(served_index) - set(declared)):
            divergences.append(_divergence(resource_id, EXTRA_SERVED))
        for resource_id in sorted(set(declared) - set(served_index)):
            divergences.append(_divergence(resource_id, DECLARED_NOT_SERVED))
        for resource_id in sorted(set(declared) & set(served_index)):
            expected = _content_sha256(declared[resource_id], "DECLARED")
            observed = _content_sha256(served_index[resource_id], "SERVED")
            if expected != observed:
                divergences.append(_divergence(
                    resource_id, CONTENT_SUBSTITUTED,
                    declared_content_sha256=expected,
                    served_content_sha256=observed))
        # Cache and prior-attempt provenance are properties of how a resource
        # arrived, so they are checked on everything served, declared or not.
        for resource_id, entry in sorted(served_index.items()):
            if entry.get("cached") is True:
                divergences.append(_divergence(resource_id, SERVED_FROM_CACHE))
            carried = sorted(
                {str(ref) for ref in (entry.get("provenance_refs") or ())} & excluded)
            if carried:
                divergences.append(_divergence(
                    resource_id, POST_ATTEMPT_PROVENANCE,
                    excluded_provenance_matched=carried))

    for entry in divergences:
        entry["owning_existing_goal"] = owning_existing_goal.strip()

    result = {
        "schema": SCHEMA,
        "state": SURFACE_CONFORMS if not divergences else SURFACE_DIVERGED,
        "disposition": "ALLOW" if not divergences else "FAIL_CLOSED",
        "declaration_id": declaration.get("declaration_id"),
        "declaration_sha256": frozen_digest,
        "declaration_intact": declaration_intact,
        "declared_resource_count": len(declared),
        "served_resource_count": len(served_index),
        "divergences": divergences,
        "owning_existing_goal": owning_existing_goal.strip(),
        "authority_boundary": dict(AUTHORITY_BOUNDARY),
        "authority_effect": "NONE_SURFACE_COMPARISON_ONLY",
    }
    if divergences:
        result["failed_predicate"] = SURFACE_DIVERGED
        result["required_evidence_or_repair"] = (
            "resolve every named divergence so the served surface equals the frozen "
            "declaration exactly; a surface that merely overlaps it is a different "
            "condition")
        result["retry_entrypoint"] = RETRY_ENTRYPOINT
    return result


def emit_under_served_surface_assertion(
    declaration: Mapping[str, Any],
    served: Iterable[Mapping[str, Any]],
    *,
    owning_existing_goal: str,
    evidence_emitter: Callable[[Mapping[str, Any]], Any],
) -> dict[str, Any]:
    """Emit evidence only if the served surface conforms, and never otherwise.

    The emitter is held rather than returned to, so a non-conforming surface
    cannot emit by a caller forgetting to check the assertion first. The caller
    still owns what the emitter does; this function owns only the ordering.
    """
    if not callable(evidence_emitter):
        raise ServedSurfaceRefused("EVIDENCE_EMITTER_REQUIRED")
    assertion = assert_served_surface(
        declaration, served, owning_existing_goal=owning_existing_goal)
    if assertion["disposition"] != "ALLOW":
        return dict(assertion, evidence_emitted=False, evidence_state=EVIDENCE_WITHHELD)
    emitted = evidence_emitter(assertion)
    return dict(assertion, evidence_emitted=True, evidence_reference=emitted)
