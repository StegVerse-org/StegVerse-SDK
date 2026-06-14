"""Example dynamic admissibility packet for StegVerse SDK.

This example mirrors the packet shape used by the StegVerse Site demo.
It does not call a remote API by default. It shows the SDK-facing
payload family that later validation and adapter helpers should consume.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Dict


def build_packet() -> Dict[str, Any]:
    """Build a discipline-aware admissibility tester packet."""
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "generated": now,
        "tester": {
            "name_or_role": "AI / LLM systems tester",
            "discipline_id": "ai_llm_systems",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": "TEST-OBJECT-SDK-EXAMPLE-0001",
            "object_type": "model_response",
            "summary": "Example model response proposed for public governance use.",
            "source_or_reference": "sdk example only",
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
            "declared_intent": "public_claim",
            "authority_source": None,
            "evidence_posture": "draft",
            "replay_posture": "not_replayable",
            "consequence_level": "medium",
            "claim_limit": (
                "May remain a research note only until authority and evidence "
                "are declared."
            ),
            "decision": "ALLOW_AS_NOTE",
            "allowed_next_state": "research_note",
            "required_follow_up": [
                "Declare authority source before public claim posture.",
                "Attach evidence or receipt reference before stronger posture.",
            ],
        },
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_proof_authority": True,
        },
        "notes": "SDK example packet only.",
    }


if __name__ == "__main__":
    print(json.dumps(build_packet(), indent=2, sort_keys=True))
