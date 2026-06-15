"""Replay helpers for Governed Admissibility Bundles."""

from __future__ import annotations

from typing import Any, Dict, Mapping

from .admissibility import evaluate_admissibility_packet
from .admissibility_bundle import bundle_hash, verify_admissibility_bundle
from .admissibility_receipts import build_admissibility_receipt_reference

REPLAY_RESULT_SCHEMA = "stegverse.admissibility.replay_result.v1"


def replay_admissibility_bundle(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    """Replay a bundle's tester packet and compare stable structural hashes.

    The replay intentionally ignores timestamp equality because re-evaluation
    creates a new result timestamp and a new local receipt-reference timestamp.
    It compares the stable fields that define posture and allowed next state.
    """
    bundle_valid = verify_admissibility_bundle(bundle)
    tester_packet = bundle.get("tester_packet") if isinstance(bundle, Mapping) else None
    if not isinstance(tester_packet, Mapping):
        return {
            "schema": REPLAY_RESULT_SCHEMA,
            "bundle_valid": bundle_valid,
            "replay_success": False,
            "reason": "bundle missing tester_packet",
        }

    original_result = bundle.get("admissibility_result", {})
    original_reference = bundle.get("admissibility_receipt_reference", {})
    replayed_result = evaluate_admissibility_packet(tester_packet)
    replayed_reference = build_admissibility_receipt_reference(
        replayed_result,
        source="sdk_admissibility_bundle_replay",
    )

    original_classification = original_result.get("classification", {}) if isinstance(original_result, Mapping) else {}
    replayed_classification = replayed_result.get("classification", {})

    classification_match = {
        "decision": original_classification.get("decision") == replayed_classification.get("decision"),
        "allowed_next_state": original_classification.get("allowed_next_state") == replayed_classification.get("allowed_next_state"),
        "receipt_posture": original_result.get("receipt_posture") == replayed_result.get("receipt_posture") if isinstance(original_result, Mapping) else False,
    }

    hash_match = {
        "tester_packet_hash": bundle.get("hashes", {}).get("tester_packet_hash") == bundle_hash(tester_packet),
        "original_reference_hash_present": isinstance(original_reference, Mapping) and str(original_reference.get("reference_hash", "")).startswith("sha256:"),
        "replayed_reference_hash_present": str(replayed_reference.get("reference_hash", "")).startswith("sha256:"),
    }

    replay_success = bool(bundle_valid and all(classification_match.values()) and all(hash_match.values()))

    return {
        "schema": REPLAY_RESULT_SCHEMA,
        "bundle_valid": bundle_valid,
        "replay_success": replay_success,
        "classification_match": classification_match,
        "hash_match": hash_match,
        "original": {
            "decision": original_classification.get("decision"),
            "allowed_next_state": original_classification.get("allowed_next_state"),
            "receipt_posture": original_result.get("receipt_posture") if isinstance(original_result, Mapping) else None,
        },
        "replayed": {
            "decision": replayed_classification.get("decision"),
            "allowed_next_state": replayed_classification.get("allowed_next_state"),
            "receipt_posture": replayed_result.get("receipt_posture"),
            "result_hash": bundle_hash(replayed_result),
            "reference_hash": replayed_reference.get("reference_hash"),
        },
    }
