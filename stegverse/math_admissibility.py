"""Math-solver artifact to dynamic admissibility packet helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, Mapping, Optional

from .admissibility import TESTER_OUTPUT_SCHEMA, evaluate_admissibility_packet
from .admissibility_receipts import build_admissibility_receipt_reference


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _object_id(*parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"MATH-ARTIFACT-{digest}"


def build_math_tester_packet(
    *,
    formalism_id: str,
    artifact_type: str,
    artifact_summary: str,
    declared_intent: str = "formalism_support_claim",
    authority_source: Optional[str] = None,
    evidence_posture: str = "research_note",
    replay_posture: str = "not_replayable",
    consequence_level: str = "medium",
    claim_limit: str = "May claim only that a proof or derivation attempt exists; may not claim proof closure.",
    source_or_reference: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a tester packet for a math-solver or formalism artifact."""
    object_id = _object_id(formalism_id, artifact_type, artifact_summary, declared_intent)
    return {
        "schema": TESTER_OUTPUT_SCHEMA,
        "generated": _utc_now(),
        "tester": {
            "name_or_role": "Math-solver admissibility bridge",
            "discipline_id": "mathematics_formal_methods",
            "domain_review_required": True,
        },
        "test_object": {
            "object_id": object_id,
            "object_type": artifact_type,
            "summary": artifact_summary,
            "source_or_reference": source_or_reference or "sdk math_admissibility bridge",
            "formalism_id": formalism_id,
            "artifact_summary_sha256": hashlib.sha256(artifact_summary.encode("utf-8")).hexdigest(),
        },
        "route": {
            "recommended_route": [
                "math_solver_adapter",
                "receipt_replay",
                "transition_admissibility",
            ],
            "tests_run": ["math_solver_adapter"],
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
        "notes": "Math-solver artifact represented as a dynamic admissibility tester packet.",
    }


def evaluate_math_artifact_admissibility(
    *,
    formalism_id: str,
    artifact_type: str,
    artifact_summary: str,
    declared_intent: str = "formalism_support_claim",
    authority_source: Optional[str] = None,
    evidence_posture: str = "research_note",
    replay_posture: str = "not_replayable",
    consequence_level: str = "medium",
    claim_limit: str = "May claim only that a proof or derivation attempt exists; may not claim proof closure.",
    source_or_reference: Optional[str] = None,
    include_receipt_reference: bool = False,
) -> Dict[str, Any]:
    """Build and evaluate a dynamic admissibility packet for a math artifact."""
    packet = build_math_tester_packet(
        formalism_id=formalism_id,
        artifact_type=artifact_type,
        artifact_summary=artifact_summary,
        declared_intent=declared_intent,
        authority_source=authority_source,
        evidence_posture=evidence_posture,
        replay_posture=replay_posture,
        consequence_level=consequence_level,
        claim_limit=claim_limit,
        source_or_reference=source_or_reference,
    )
    result = evaluate_admissibility_packet(packet)
    bridge = {
        "schema": "stegverse.math_admissibility.bridge_result.v1",
        "evaluated_at": result["evaluated_at"],
        "tester_packet": packet,
        "admissibility_result": result,
        "decision": result["classification"]["decision"],
        "allowed_next_state": result["classification"]["allowed_next_state"],
        "receipt_posture": result["receipt_posture"],
    }
    if include_receipt_reference:
        bridge["admissibility_receipt_reference"] = build_admissibility_receipt_reference(
            result,
            source="sdk_math_admissibility_bridge",
        )
    return bridge


def summarize_math_admissibility(bridge_result: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a compact summary from a math admissibility bridge result."""
    result = bridge_result.get("admissibility_result", {})
    classification = result.get("classification", {}) if isinstance(result, Mapping) else {}
    summary = {
        "decision": classification.get("decision", bridge_result.get("decision", "REQUIRE_REVIEW")),
        "allowed_next_state": classification.get("allowed_next_state", bridge_result.get("allowed_next_state", "hold")),
        "receipt_posture": bridge_result.get("receipt_posture", "sdk_local_not_receipt_backed"),
        "required_follow_up": classification.get("required_follow_up", []),
    }
    reference = bridge_result.get("admissibility_receipt_reference")
    if isinstance(reference, Mapping):
        summary["admissibility_reference_id"] = reference.get("reference_id")
    return summary
