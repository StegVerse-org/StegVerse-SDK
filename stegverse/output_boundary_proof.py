"""Credentialless provider-output proof for StegVerse S/NS SDK testing.

This module never calls a model provider and never accepts provider credentials.
It wraps the existing SDK LLM admissibility bridge, then proves replay of the
preserved tester packet and semantic reconstruction of the candidate evidence.
It is non-authorizing and does not claim Node Sovereign membership.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Mapping

from .admissibility import evaluate_admissibility_packet
from .llm_admissibility import build_llm_tester_packet, evaluate_llm_output_admissibility

SCHEMA = "stegverse.output_boundary.proof.v1"
INPUT_SCHEMA = "stegverse.output_boundary.candidate.v1"


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canon(value).encode("utf-8")).hexdigest()


def _projection(result: Mapping[str, Any]) -> Dict[str, Any]:
    classification = result.get("classification", {})
    return {
        "decision": classification.get("decision"),
        "allowed_next_state": classification.get("allowed_next_state"),
        "required_follow_up": classification.get("required_follow_up", []),
        "receipt_posture": result.get("receipt_posture"),
    }


def evaluate_output_boundary_proof(candidate: Mapping[str, Any]) -> Dict[str, Any]:
    """Evaluate one externally generated LLM candidate without provider credentials."""
    required = ("deployment_class", "provider", "model", "prompt", "output", "provider_api_key_transferred_to_stegverse")
    missing = [key for key in required if key not in candidate]
    if missing:
        raise ValueError("missing required candidate fields: " + ", ".join(missing))

    deployment_class = str(candidate["deployment_class"]).upper()
    if deployment_class not in {"S", "NS"}:
        raise ValueError("deployment_class must be S or NS")
    if candidate["provider_api_key_transferred_to_stegverse"] is not False:
        raise ValueError("provider_api_key_transferred_to_stegverse must be false")

    provider = str(candidate["provider"])
    model = str(candidate["model"])
    prompt = str(candidate["prompt"])
    output = str(candidate["output"])
    intent = str(candidate.get("declared_intent", "research_note"))
    consequence = str(candidate.get("consequence_level", "medium"))

    bridge = evaluate_llm_output_admissibility(
        provider=provider,
        model=model,
        prompt=prompt,
        output=output,
        declared_intent=intent,
        consequence_level=consequence,
        evidence_posture=str(candidate.get("evidence_posture", "draft")),
        replay_posture="replayable_from_preserved_sdk_packet",
        source_or_reference=str(candidate.get("source_or_reference", "external provider candidate")),
        include_receipt_reference=True,
    )
    packet = bridge["tester_packet"]
    first_result = bridge["admissibility_result"]
    first_projection = _projection(first_result)

    replay_result = evaluate_admissibility_packet(packet)
    replay_projection = _projection(replay_result)

    reconstructed_packet = build_llm_tester_packet(
        provider=provider,
        model=model,
        prompt=prompt,
        output=output,
        declared_intent=intent,
        consequence_level=consequence,
        evidence_posture=str(candidate.get("evidence_posture", "draft")),
        replay_posture="replayable_from_preserved_sdk_packet",
        source_or_reference=str(candidate.get("source_or_reference", "external provider candidate")),
    )
    reconstructed_result = evaluate_admissibility_packet(reconstructed_packet)
    reconstructed_projection = _projection(reconstructed_result)

    original_object = packet.get("test_object", {})
    reconstructed_object = reconstructed_packet.get("test_object", {})
    semantic_reconstruction_match = all(
        original_object.get(key) == reconstructed_object.get(key)
        for key in ("object_id", "provider", "model", "prompt_sha256", "output_sha256")
    ) and first_projection == reconstructed_projection

    return {
        "schema": SCHEMA,
        "input_schema": INPUT_SCHEMA,
        "deployment_class": deployment_class,
        "sovereign_mode": "isolated" if deployment_class == "S" else "node_sovereign_profile",
        "node_sovereign_membership_granted": False,
        "provider": provider,
        "model": model,
        "provider_api_key_received_by_stegverse": False,
        "provider_api_key_required_by_proof_surface": False,
        "candidate_hash": _sha({"provider": provider, "model": model, "prompt": prompt, "output": output}),
        "prompt_sha256": original_object.get("prompt_sha256"),
        "output_sha256": original_object.get("output_sha256"),
        "object_id": original_object.get("object_id"),
        "governance": {
            "projection": first_projection,
            "admissibility_reference": bridge.get("admissibility_receipt_reference"),
        },
        "replay": {
            "projection": replay_projection,
            "match": replay_projection == first_projection,
            "preserved_packet_hash": _sha(packet),
        },
        "reconstruction": {
            "projection": reconstructed_projection,
            "semantic_match": semantic_reconstruction_match,
            "reconstructed_object_id": reconstructed_object.get("object_id"),
        },
        "proof": {
            "candidate_bound": True,
            "credential_nonpossession_asserted": True,
            "replay_match": replay_projection == first_projection,
            "semantic_reconstruction_match": semantic_reconstruction_match,
            "authority_effect": "NONE",
        },
    }


__all__ = ["INPUT_SCHEMA", "SCHEMA", "evaluate_output_boundary_proof"]
