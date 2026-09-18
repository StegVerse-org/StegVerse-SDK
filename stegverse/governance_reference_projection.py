from __future__ import annotations

"""Authority-neutral semantic projection for recognized Governance Reference Graph relations.

This module maps recognized GRG relation shapes to existing canonical semantic-owner
inputs. It does not grant authority, implement policy semantics, or claim live runtime
execution. Unknown relations remain preserved, hash-bound, and non-authorizing.
"""

from copy import deepcopy
from typing import Any, Callable, Mapping

from .authority_basis_bridge import resolve_governance_authority_basis
from .governance_navigation import canonical_sha256
from .governance_reference_graph import validate_governance_reference_graph

AuthorityResolver = Callable[..., Mapping[str, Any]]

AUTHORITY_RELATION = "HAS_SCOPED_AUTHORITY"
CONSTRAINT_RELATION = "REQUIRES_CONSTRAINT"
AUTHORITY_OWNER = "StegCore.authority_basis.resolve_authority_basis"
POLICY_SHAPE_OWNER = "StegCore.policy-shape"
PROJECTION_SCHEMA = "stegverse.sdk.grg-semantic-projection.v1"


def _candidate(value: Mapping[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for field in ("action", "target", "scope"):
        item = value.get(field)
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"candidate.{field} is required")
        out[field] = item.strip()
    return out


def _selector_covers(selector: Mapping[str, Any] | None, candidate: Mapping[str, str]) -> bool:
    if not selector:
        return True
    mapping = {"actions": "action", "targets": "target", "scopes": "scope"}
    for plural, singular in mapping.items():
        values = selector.get(plural)
        if values is None:
            continue
        if "*" not in values and candidate[singular] not in values:
            return False
    return True


def _authority_basis_complete(
    graph: Mapping[str, Any],
    *,
    subject: str,
    candidate: Mapping[str, str],
) -> bool:
    relevant = [
        item
        for item in graph.get("coverage", [])
        if item.get("relation") == AUTHORITY_RELATION
        and item.get("subject") in {None, subject}
        and _selector_covers(item.get("selector"), candidate)
    ]
    return any(item.get("complete") is True for item in relevant)


def _authority_assertions(
    graph: Mapping[str, Any],
    *,
    subject: str,
) -> list[dict[str, Any]]:
    nodes = {item["node_id"]: item for item in graph["nodes"]}
    assertions: list[dict[str, Any]] = []
    for relation in graph["relations"]:
        if relation.get("relation") != AUTHORITY_RELATION or relation.get("subject") != subject:
            continue
        applicability = relation.get("applicability") or {}
        required = ("actions", "targets", "scopes", "status", "valid_from", "valid_until")
        if any(not applicability.get(field) for field in required):
            continue
        assertions.append(
            {
                "assertion_id": relation["relation_id"],
                "subject_identity": nodes[subject]["ref"],
                "actions": list(applicability["actions"]),
                "targets": list(applicability["targets"]),
                "scopes": list(applicability["scopes"]),
                "status": applicability["status"],
                "valid_from": applicability["valid_from"],
                "valid_until": applicability["valid_until"],
                "source_ref": relation["source_ref"],
                "evidence_refs": list(relation.get("evidence_refs") or []),
            }
        )
    return assertions


def _authority_projection(
    graph: Mapping[str, Any],
    relation: Mapping[str, Any],
    *,
    task_id: str,
    candidate: Mapping[str, str],
    observed_at: str,
    authority_resolver: AuthorityResolver | None,
) -> dict[str, Any]:
    nodes = {item["node_id"]: item for item in graph["nodes"]}
    subject = relation["subject"]
    request = {
        "schema": "stegcore.authority-basis-request.v1",
        "task_id": task_id,
        "actor_identity": nodes[subject]["ref"],
        "actor_role": None,
        "candidate": dict(candidate),
        "authority_assertions": _authority_assertions(graph, subject=subject),
        "delegation_assertions": [],
        "delegation_required": False,
        "authority_basis_complete": _authority_basis_complete(
            graph, subject=subject, candidate=candidate
        ),
        "delegation_basis_complete": True,
        "authority_effect": "NONE_TEST_EVIDENCE_ONLY",
    }
    projected_hash = canonical_sha256(request)
    governance_result = None
    projection_state = "RECOGNIZED_PROJECTED"
    if authority_resolver is not None:
        governance_request = {
            "candidate": dict(candidate),
            "execution": {
                "actor_authority_current": None,
                "delegation_current": None,
                "evidence_refs": [],
            },
        }
        _, binding = resolve_governance_authority_basis(
            governance_request=governance_request,
            authority_basis_request=request,
            resolver=authority_resolver,
            observed_at=observed_at,
        )
        governance_result = binding
        projection_state = "CANONICALLY_EVALUATED"
    return {
        "relation_id": relation["relation_id"],
        "relation_type": AUTHORITY_RELATION,
        "recognition_state": "RECOGNIZED",
        "canonical_semantic_owner": AUTHORITY_OWNER,
        "projection_state": projection_state,
        "projected_input": request,
        "projected_input_hash": "sha256:" + projected_hash,
        "governance_result": governance_result,
        "authority_effect": "NONE_PROJECTION_ONLY",
        "transition_runtime_binding_state": "NOT_LIVE_RUNTIME_BOUND",
        "evidence_receipt_refs": [],
    }


def _constraint_projection(
    relation: Mapping[str, Any],
    *,
    candidate: Mapping[str, str],
) -> dict[str, Any]:
    constraint_ref = relation.get("constraint_ref")
    canonical = isinstance(constraint_ref, str) and constraint_ref.startswith(
        "stegcore:policy-shape:"
    )
    projected = {
        "constraint_ref": constraint_ref,
        "candidate": dict(candidate),
        "relation_id": relation["relation_id"],
        "source_ref": relation["source_ref"],
        "evidence_refs": list(relation.get("evidence_refs") or []),
    }
    return {
        "relation_id": relation["relation_id"],
        "relation_type": CONSTRAINT_RELATION,
        "recognition_state": "RECOGNIZED",
        "canonical_semantic_owner": POLICY_SHAPE_OWNER if canonical else None,
        "projection_state": "RECOGNIZED_PROJECTED" if canonical else "REPRESENTED_ONLY",
        "projected_input": projected if canonical else None,
        "projected_input_hash": ("sha256:" + canonical_sha256(projected)) if canonical else None,
        "governance_result": None,
        "authority_effect": "NONE_PROJECTION_ONLY",
        "transition_runtime_binding_state": "NOT_LIVE_RUNTIME_BOUND",
        "evidence_receipt_refs": [],
        "semantic_owner_callable": False,
        "first_unsatisfied_existing_seam": (
            None
            if not canonical
            else "StegCore policy-shape relation projection has no callable public semantic-owner seam"
        ),
    }


def project_governance_reference_graph(
    graph: Mapping[str, Any],
    *,
    task_id: str,
    candidate: Mapping[str, Any],
    observed_at: str,
    authority_resolver: AuthorityResolver | None = None,
) -> dict[str, Any]:
    validated = validate_governance_reference_graph(graph)
    exact_candidate = _candidate(candidate)
    before_hash = validated["graph_sha256"]
    projections: list[dict[str, Any]] = []
    for relation in validated["relations"]:
        relation_type = relation["relation"]
        if relation_type == AUTHORITY_RELATION:
            item = _authority_projection(
                validated,
                relation,
                task_id=task_id,
                candidate=exact_candidate,
                observed_at=observed_at,
                authority_resolver=authority_resolver,
            )
        elif relation_type == CONSTRAINT_RELATION:
            item = _constraint_projection(relation, candidate=exact_candidate)
        else:
            item = {
                "relation_id": relation["relation_id"],
                "relation_type": relation_type,
                "recognition_state": "UNKNOWN_RELATION",
                "canonical_semantic_owner": None,
                "projection_state": "UNKNOWN_RELATION_PRESERVED",
                "projected_input": None,
                "projected_input_hash": None,
                "governance_result": None,
                "authority_effect": "NONE_NON_AUTHORIZING_EVIDENCE_ONLY",
                "transition_runtime_binding_state": "NOT_LIVE_RUNTIME_BOUND",
                "evidence_receipt_refs": list(relation.get("evidence_refs") or []),
                "preserved_relation": deepcopy(dict(relation)),
            }
        projections.append(item)
    if validated["graph_sha256"] != before_hash:
        raise ValueError("GRG projection must not mutate graph hash")
    return {
        "schema": PROJECTION_SCHEMA,
        "task_id": task_id,
        "graph_id": validated["graph_id"],
        "graph_sha256": validated["graph_sha256"],
        "candidate": exact_candidate,
        "observed_at": observed_at,
        "authority_effect": "NONE_PROJECTION_AND_VERIFICATION_ONLY",
        "sdk_resolves_governance": False,
        "live_runtime_bound": False,
        "relations": projections,
    }


__all__ = [
    "AUTHORITY_OWNER",
    "POLICY_SHAPE_OWNER",
    "PROJECTION_SCHEMA",
    "project_governance_reference_graph",
]
