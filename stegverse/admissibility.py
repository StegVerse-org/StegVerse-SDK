"""Dynamic admissibility helpers for StegVerse SDK.

This module provides a small dependency-free evaluator for the packet family
used by the StegVerse Site dynamic demo. It is intentionally conservative:
it classifies posture and allowed next state, but does not certify domain
correctness or create proof authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional

TESTER_OUTPUT_SCHEMA = "stegverse.governed_admissibility.tester_output.v1"
DYNAMIC_RESULT_SCHEMA = "stegverse.governed_admissibility.dynamic_demo_result.v1"

DEFAULT_ROUTES: Dict[str, List[str]] = {
    "ai_llm_systems": ["governance_filter", "llm_governance_comparison", "fail_closed"],
    "mathematics_formal_methods": ["math_solver_adapter", "receipt_replay", "transition_admissibility"],
    "software_engineering": ["transition_admissibility", "receipt_replay", "fail_closed"],
    "cybersecurity_identity": ["fail_closed", "transition_admissibility", "receipt_replay"],
    "data_governance": ["transition_admissibility", "receipt_replay", "governance_filter"],
    "legal_policy": ["governance_filter", "llm_governance_comparison", "fail_closed"],
    "medicine_health": ["governance_filter", "fail_closed", "transition_admissibility"],
    "finance_markets": ["governance_filter", "transition_admissibility", "fail_closed"],
    "education_learning": ["governance_filter", "llm_governance_comparison", "transition_admissibility"],
    "science_research": ["governance_filter", "math_solver_adapter", "receipt_replay"],
    "engineering_infrastructure": ["transition_admissibility", "fail_closed", "receipt_replay"],
    "robotics_autonomy": ["transition_admissibility", "fail_closed", "receipt_replay"],
    "journalism_public_information": ["governance_filter", "llm_governance_comparison", "receipt_replay"],
    "government_civic_systems": ["transition_admissibility", "fail_closed", "receipt_replay"],
    "organizational_governance": ["transition_admissibility", "receipt_replay", "fail_closed"],
    "archives_records_history": ["receipt_replay", "governance_filter", "transition_admissibility"],
}

HIGH_STAKES_DISCIPLINES = {
    "legal_policy",
    "medicine_health",
    "finance_markets",
    "engineering_infrastructure",
    "government_civic_systems",
    "robotics_autonomy",
    "cybersecurity_identity",
}

HIGH_STAKES_INTENT_RE = re.compile(
    r"action|decision|care|financial|deploy|access|motion|eligibility|payment|credential",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AdmissibilityDecision:
    """SDK-side result for a dynamic admissibility packet."""

    decision: str
    allowed_next_state: str
    required_follow_up: List[str] = field(default_factory=list)
    receipt_posture: str = "sdk_local_not_receipt_backed"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_hash(payload: Mapping[str, Any]) -> str:
    """Return a stable local SHA-256 hash for a packet or result."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _as_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return []
    return [str(value)]


def validate_tester_packet(packet: Mapping[str, Any]) -> List[str]:
    """Return validation errors for a tester-output packet.

    This is a lightweight structural validator. Full JSON Schema validation can
    be layered on top by callers that install a schema validation dependency.
    """
    errors: List[str] = []
    required = ["schema", "tester", "test_object", "route", "classification", "boundary"]
    for key in required:
        if key not in packet:
            errors.append(f"missing required field: {key}")

    if packet.get("schema") not in {TESTER_OUTPUT_SCHEMA, "stegverse.governed_admissibility.dynamic_demo_input.v1"}:
        errors.append("unexpected schema for tester packet")

    tester = packet.get("tester") or {}
    if not isinstance(tester, Mapping):
        errors.append("tester must be an object")
    else:
        for key in ["name_or_role", "discipline_id", "domain_review_required"]:
            if key not in tester:
                errors.append(f"tester missing field: {key}")

    test_object = packet.get("test_object") or {}
    if not isinstance(test_object, Mapping):
        errors.append("test_object must be an object")
    else:
        for key in ["object_id", "object_type", "summary"]:
            if key not in test_object:
                errors.append(f"test_object missing field: {key}")

    classification = packet.get("classification") or {}
    if not isinstance(classification, Mapping):
        errors.append("classification must be an object")
    else:
        for key in ["declared_intent", "evidence_posture", "replay_posture", "consequence_level", "claim_limit"]:
            if key not in classification:
                errors.append(f"classification missing field: {key}")

    return errors


def evaluate_admissibility_packet(packet: Mapping[str, Any], *, strict: bool = False) -> Dict[str, Any]:
    """Evaluate a dynamic admissibility tester packet.

    The evaluator mirrors the public Site demo logic while returning an SDK-shaped
    result packet. It is local and side-effect free.
    """
    errors = validate_tester_packet(packet)
    if strict and errors:
        raise ValueError("invalid admissibility packet: " + "; ".join(errors))

    tester = packet.get("tester") if isinstance(packet.get("tester"), Mapping) else {}
    test_object = packet.get("test_object") if isinstance(packet.get("test_object"), Mapping) else {}
    route_obj = packet.get("route") if isinstance(packet.get("route"), Mapping) else {}
    classification = packet.get("classification") if isinstance(packet.get("classification"), Mapping) else {}

    discipline = _as_str(tester.get("discipline_id"), "unknown")
    recommended_route = _list(route_obj.get("recommended_route")) or DEFAULT_ROUTES.get(discipline, ["governance_filter", "fail_closed"])

    consequence = _as_str(classification.get("consequence_level"), "medium").lower()
    authority_source = classification.get("authority_source")
    evidence = _as_str(classification.get("evidence_posture"), "none").lower()
    replay = _as_str(classification.get("replay_posture"), "not_replayable").lower()
    declared_intent = _as_str(classification.get("declared_intent"), _as_str(test_object.get("object_type"), "unknown")).lower()

    high_consequence = (
        consequence in {"high", "critical"}
        or discipline in HIGH_STAKES_DISCIPLINES
        or bool(HIGH_STAKES_INTENT_RE.search(declared_intent))
    )

    decision = "ALLOW_AS_NOTE"
    allowed_next_state = "research_note"
    required_follow_up: List[str] = []

    if errors:
        decision = "REQUIRE_REVIEW"
        allowed_next_state = "hold"
        required_follow_up.extend(errors)

    if not authority_source and high_consequence:
        decision = "FAIL_CLOSED"
        allowed_next_state = "fail_closed"
        required_follow_up.append("Declare authority source before high-consequence movement.")
    elif not authority_source and decision != "FAIL_CLOSED":
        decision = "REQUIRE_REVIEW"
        allowed_next_state = "hold"
        required_follow_up.append("Add authority source or reviewer before stronger posture.")

    if evidence in {"none", "draft"} and decision != "FAIL_CLOSED":
        decision = "REQUIRE_RECEIPT" if high_consequence else "ALLOW_AS_NOTE"
        allowed_next_state = "hold" if high_consequence else "research_note"
        required_follow_up.append("Attach evidence, source, receipt, or review before public claim posture.")

    if replay in {"not_replayable", "none"} and evidence in {"source_backed", "receipt_backed"} and decision != "FAIL_CLOSED":
        decision = "REQUIRE_REPLAY"
        allowed_next_state = "hold"
        required_follow_up.append("Add replay path before promotion beyond research note.")

    if authority_source and evidence == "receipt_backed" and replay == "receipt_backed" and not high_consequence and not errors:
        decision = "ALLOW_WITH_POSTURE"
        allowed_next_state = "receipt_backed_claim"
        required_follow_up.append("Keep receipt reference attached to any publication or action.")

    result: Dict[str, Any] = {
        "schema": DYNAMIC_RESULT_SCHEMA,
        "evaluated_at": utc_now(),
        "mode": "sdk_local_dynamic_admissibility",
        "input_object_id": test_object.get("object_id"),
        "discipline_id": discipline,
        "recommended_route": recommended_route,
        "classification": {
            "declared_intent": classification.get("declared_intent", "unknown"),
            "authority_source": authority_source,
            "evidence_posture": evidence,
            "replay_posture": replay,
            "consequence_level": consequence,
            "claim_limit": classification.get("claim_limit", "No claim beyond research-note posture without review."),
            "decision": decision,
            "allowed_next_state": allowed_next_state,
            "required_follow_up": required_follow_up,
        },
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_proof_authority": True,
        },
        "receipt_posture": "receipt_backed" if replay == "receipt_backed" else "sdk_local_not_receipt_backed",
    }
    result["local_receipt_hash"] = stable_hash(result)
    return result


def result_to_decision(result: Mapping[str, Any]) -> AdmissibilityDecision:
    """Convert a result packet into a compact decision object."""
    classification = result.get("classification") if isinstance(result.get("classification"), Mapping) else {}
    return AdmissibilityDecision(
        decision=_as_str(classification.get("decision"), "REQUIRE_REVIEW"),
        allowed_next_state=_as_str(classification.get("allowed_next_state"), "hold"),
        required_follow_up=_list(classification.get("required_follow_up")),
        receipt_posture=_as_str(result.get("receipt_posture"), "sdk_local_not_receipt_backed"),
    )


def to_dict(decision: AdmissibilityDecision) -> Dict[str, Any]:
    return asdict(decision)
