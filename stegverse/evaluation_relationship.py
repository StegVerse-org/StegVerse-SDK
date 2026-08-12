from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from .demo_terms import verify_demo_terms_acceptance

REQUEST_SCHEMA = "stegverse.sdk.evaluation-interest-request.v1"
RESULT_SCHEMA = "stegverse.sdk.evaluation-relationship-result.v1"


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def _normalized_words(text: str) -> set[str]:
    return {part for part in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split() if len(part) > 1}


def resolve_evaluation_relationship(request: Mapping[str, Any], capability_catalog: Sequence[Mapping[str, Any]], *, terms_acceptance_receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not verify_demo_terms_acceptance(terms_acceptance_receipt):
        raise PermissionError("demo_terms_acceptance_required_or_invalid")
    if request.get("schema") != REQUEST_SCHEMA:
        raise ValueError("evaluation_request_schema_mismatch")
    request_id = str(request.get("request_id") or "").strip()
    objectives = [str(v).strip() for v in request.get("objectives") or [] if str(v).strip()]
    explicit = {str(v) for v in request.get("requested_capabilities") or [] if str(v)}
    excluded = {str(v) for v in request.get("exclude_capabilities") or [] if str(v)}
    max_depth = str(request.get("maximum_interaction") or "read_only")
    if not request_id or not objectives:
        raise ValueError("evaluation_request_identity_or_objectives_missing")
    if max_depth not in {"read_only", "deterministic_demo", "sandbox"}:
        raise ValueError("evaluation_request_interaction_invalid")
    depth_rank = {"read_only": 0, "deterministic_demo": 1, "sandbox": 2}
    catalog: dict[str, Mapping[str, Any]] = {}
    for item in capability_catalog:
        cid = str(item.get("capability_id") or "")
        if not cid or cid in catalog:
            raise ValueError("evaluation_catalog_invalid_or_duplicate_capability")
        catalog[cid] = item
    matched_by_objective: dict[str, list[str]] = {}
    unresolved: list[str] = []
    requested = set(explicit)
    for objective in objectives:
        words = _normalized_words(objective)
        matches: list[str] = []
        for cid, item in sorted(catalog.items()):
            tags = _normalized_words(" ".join(str(v) for v in item.get("tags") or []))
            title_words = _normalized_words(str(item.get("title") or ""))
            if words and words.intersection(tags | title_words):
                matches.append(cid)
        matched_by_objective[objective] = matches
        if matches:
            requested.update(matches)
        else:
            unresolved.append(objective)
    admitted: list[dict[str, Any]] = []
    denied: list[dict[str, str]] = []
    for cid in sorted(requested):
        if cid in excluded:
            denied.append({"capability_id": cid, "reason": "EVALUATOR_EXCLUDED"}); continue
        item = catalog.get(cid)
        if item is None:
            denied.append({"capability_id": cid, "reason": "NOT_IN_PACKAGE_CATALOG"}); continue
        if item.get("evaluator_visible") is not True:
            denied.append({"capability_id": cid, "reason": "PACKAGE_POLICY_DENIED"}); continue
        depth = str(item.get("interaction") or "read_only")
        if depth not in depth_rank or depth_rank[depth] > depth_rank[max_depth]:
            denied.append({"capability_id": cid, "reason": "EVALUATOR_INTERACTION_LIMIT"}); continue
        admitted.append({"capability_id": cid, "title": str(item.get("title") or cid), "interaction": depth, "route": item.get("route")})
    result: dict[str, Any] = {
        "schema": RESULT_SCHEMA,
        "request_id": request_id,
        "participant_id": str(terms_acceptance_receipt["participant_id"]),
        "terms_acceptance_receipt_hash": str(terms_acceptance_receipt["receipt_hash"]),
        "objectives": objectives,
        "matched_by_objective": matched_by_objective,
        "admitted_capabilities": admitted,
        "denied_or_unavailable": denied,
        "unresolved_objectives": unresolved,
        "maximum_interaction": max_depth,
        "recipient_specific_package": False,
        "identity_bound_package": False,
        "execution_authority_granted": False,
        "mutation_authority_granted": False,
        "publication_authority_granted": False,
        "wallet_authority_granted": False,
        "credential_authority_granted": False,
        "repository_access_granted": False,
        "unknown_interest_auto_admitted": False,
    }
    result["receipt_hash"] = _hash(result)
    return result


def verify_evaluation_relationship(result: Mapping[str, Any]) -> bool:
    if result.get("schema") != RESULT_SCHEMA:
        return False
    for key in ("participant_id", "terms_acceptance_receipt_hash"):
        if not isinstance(result.get(key), str) or not str(result.get(key)).strip():
            return False
    for key in ("recipient_specific_package", "identity_bound_package", "execution_authority_granted", "mutation_authority_granted", "publication_authority_granted", "wallet_authority_granted", "credential_authority_granted", "repository_access_granted", "unknown_interest_auto_admitted"):
        if result.get(key) is not False:
            return False
    candidate = dict(result)
    expected = candidate.pop("receipt_hash", None)
    return isinstance(expected, str) and expected == _hash(candidate)
