"""LLM text to dynamic admissibility packet helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, Mapping, Optional

from .admissibility import TESTER_OUTPUT_SCHEMA, evaluate_admissibility_packet


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _object_id(*parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"LLM-OUTPUT-{digest}"


def build_llm_tester_packet(
    *,
    provider: str,
    model: str,
    prompt: str,
    output: str,
    declared_intent: str = "research_note",
    authority_source: Optional[str] = None,
    evidence_posture: str = "draft",
    replay_posture: str = "not_replayable",
    consequence_level: str = "medium",
    claim_limit: str = "Research-note only until authority and evidence are declared.",
    source_or_reference: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a tester packet for LLM text."""
    object_id = _object_id(provider, model, prompt, output, declared_intent)
    return {
        "schema": TESTER_OUTPUT_SCHEMA,
        "generated": _utc_now(),
        "tester": {
            "name_or_role": "LLM admissibility bridge",
            "discipline_id": "ai_llm_systems",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": object_id,
            "object_type": "model_response",
            "summary": f"LLM text from {provider}/{model} proposed for {declared_intent}.",
            "source_or_reference": source_or_reference or "sdk llm_admissibility bridge",
            "provider": provider,
            "model": model,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
        },
        "route": {
            "recommended_route": [
                "governance_filter",
                "llm_governance_comparison",
                "fail_closed",
            ],
            "tests_run": ["governance_filter"],
            "route_deviation_reason": None,
        },
        "classification": {
            "declared_intent": declared_intent,
            "authority_source": authority_source,
            "evidence_posture": evidence_posture,
            "replay_posture": replay_posture,
            "consequence_level": consequence_level,
            "claim_limit": claim_limit,
        },
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_proof_authority": True,
        },
        "notes": "LLM text represented as a dynamic admissibility tester packet.",
    }


def evaluate_llm_output_admissibility(
    *,
    provider: str,
    model: str,
    prompt: str,
    output: str,
    declared_intent: str = "research_note",
    authority_source: Optional[str] = None,
    evidence_posture: str = "draft",
    replay_posture: str = "not_replayable",
    consequence_level: str = "medium",
    claim_limit: str = "Research-note only until authority and evidence are declared.",
    source_or_reference: Optional[str] = None,
) -> Dict[str, Any]:
    """Build and evaluate a dynamic admissibility packet for LLM text."""
    packet = build_llm_tester_packet(
        provider=provider,
        model=model,
        prompt=prompt,
        output=output,
        declared_intent=declared_intent,
        authority_source=authority_source,
        evidence_posture=evidence_posture,
        replay_posture=replay_posture,
        consequence_level=consequence_level,
        claim_limit=claim_limit,
        source_or_reference=source_or_reference,
    )
    result = evaluate_admissibility_packet(packet)
    return {
        "schema": "stegverse.llm_admissibility.bridge_result.v1",
        "evaluated_at": result["evaluated_at"],
        "tester_packet": packet,
        "admissibility_result": result,
        "decision": result["classification"]["decision"],
        "allowed_next_state": result["classification"]["allowed_next_state"],
        "receipt_posture": result["receipt_posture"],
    }


def summarize_llm_admissibility(bridge_result: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a compact summary from an LLM admissibility bridge result."""
    result = bridge_result.get("admissibility_result", {})
    classification = result.get("classification", {}) if isinstance(result, Mapping) else {}
    return {
        "decision": classification.get("decision", bridge_result.get("decision", "REQUIRE_REVIEW")),
        "allowed_next_state": classification.get("allowed_next_state", bridge_result.get("allowed_next_state", "hold")),
        "receipt_posture": bridge_result.get("receipt_posture", "sdk_local_not_receipt_backed"),
        "required_follow_up": classification.get("required_follow_up", []),
    }
