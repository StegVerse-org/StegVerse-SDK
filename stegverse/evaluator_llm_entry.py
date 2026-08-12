from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .evaluation_relationship import verify_evaluation_relationship

SCHEMA = "stegverse.sdk.evaluator-llm-entry-request.v1"
CAPABILITY_ID = "llm_adapter.evaluator_interaction"
ROUTE = "sdk://StegVerse-org/LLM-adapter/evaluator-entry"


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def build_evaluator_llm_request(*, relationship: Mapping[str, Any], request_id: str, prompt: str, max_output_tokens: int = 256) -> dict[str, Any]:
    if not verify_evaluation_relationship(relationship):
        raise PermissionError("invalid_sdk_evaluation_relationship")
    admitted = {str(v.get("capability_id")): v for v in relationship.get("admitted_capabilities") or [] if isinstance(v, Mapping)}
    capability = admitted.get(CAPABILITY_ID)
    if capability is None or capability.get("route") != ROUTE:
        raise PermissionError("llm_evaluator_capability_not_admitted")
    request_id = request_id.strip(); prompt = prompt.strip()
    if not request_id or not prompt:
        raise ValueError("evaluator_llm_request_missing")
    if not isinstance(max_output_tokens, int) or not 1 <= max_output_tokens <= 512:
        raise ValueError("evaluator_llm_max_output_tokens_invalid")
    envelope: dict[str, Any] = {
        "schema": SCHEMA,
        "request_id": request_id,
        "participant_id": relationship["participant_id"],
        "relationship_receipt_hash": relationship["receipt_hash"],
        "terms_acceptance_receipt_hash": relationship["terms_acceptance_receipt_hash"],
        "capability_id": CAPABILITY_ID,
        "route": ROUTE,
        "evaluation_model_scope": "local_reference_only",
        "prompt": prompt,
        "max_output_tokens": max_output_tokens,
        "provider_selection_authority": False,
        "credential_access_granted": False,
        "execution_authority_granted": False,
        "repository_access_granted": False,
    }
    envelope["request_hash"] = _hash(envelope)
    return envelope


def verify_evaluator_llm_request(request: Mapping[str, Any], relationship: Mapping[str, Any]) -> bool:
    if request.get("schema") != SCHEMA or not verify_evaluation_relationship(relationship): return False
    if request.get("relationship_receipt_hash") != relationship.get("receipt_hash"): return False
    if request.get("terms_acceptance_receipt_hash") != relationship.get("terms_acceptance_receipt_hash"): return False
    if request.get("participant_id") != relationship.get("participant_id"): return False
    if request.get("capability_id") != CAPABILITY_ID or request.get("route") != ROUTE: return False
    if request.get("evaluation_model_scope") != "local_reference_only": return False
    for key in ("provider_selection_authority","credential_access_granted","execution_authority_granted","repository_access_granted"):
        if request.get(key) is not False: return False
    candidate = dict(request); expected = candidate.pop("request_hash", None)
    return isinstance(expected, str) and expected == _hash(candidate)
