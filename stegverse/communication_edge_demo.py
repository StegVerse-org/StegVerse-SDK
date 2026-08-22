"""Non-authorizing SDK demonstration for KV-hosted cross-edge communications.

This module is deliberately a conformance simulator. It demonstrates the public
shape and invariants of the StegWhisper -> StegTalk ST-031 -> KnowledgeVault flow
without granting bearer, execution, admissibility, or continuity authority.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


class CommunicationDemoError(ValueError):
    pass


POSTURE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "AUTO": {
        "security": 2.0,
        "privacy": 2.0,
        "recipient_compatibility": 2.0,
        "reliability": 1.8,
        "receipt_quality": 1.5,
        "bidirectionality": 1.2,
        "resilience": 1.1,
        "latency": 1.0,
        "bandwidth": 0.7,
        "cost": 0.6,
        "energy": 0.6,
        "metadata_minimization": 1.3,
    },
    "MOST_PRIVATE": {
        "security": 2.4, "privacy": 2.6, "recipient_compatibility": 1.5,
        "reliability": 1.2, "receipt_quality": 1.3, "bidirectionality": 1.0,
        "resilience": 0.8, "latency": 0.5, "bandwidth": 0.4, "cost": 0.3,
        "energy": 0.4, "metadata_minimization": 2.4,
    },
    "FASTEST": {
        "security": 1.5, "privacy": 1.2, "recipient_compatibility": 1.8,
        "reliability": 1.4, "receipt_quality": 0.8, "bidirectionality": 0.8,
        "resilience": 0.7, "latency": 2.7, "bandwidth": 1.7, "cost": 0.2,
        "energy": 0.3, "metadata_minimization": 0.9,
    },
    "LOWEST_COST": {
        "security": 1.4, "privacy": 1.2, "recipient_compatibility": 1.7,
        "reliability": 1.3, "receipt_quality": 0.8, "bidirectionality": 0.8,
        "resilience": 0.8, "latency": 0.6, "bandwidth": 0.5, "cost": 2.8,
        "energy": 0.5, "metadata_minimization": 0.9,
    },
    "LOWEST_ENERGY": {
        "security": 1.4, "privacy": 1.2, "recipient_compatibility": 1.7,
        "reliability": 1.2, "receipt_quality": 0.8, "bidirectionality": 0.8,
        "resilience": 0.7, "latency": 0.6, "bandwidth": 0.4, "cost": 0.5,
        "energy": 2.8, "metadata_minimization": 0.9,
    },
    "LOCAL_ONLY": {
        "security": 2.0, "privacy": 2.2, "recipient_compatibility": 1.6,
        "reliability": 1.0, "receipt_quality": 0.8, "bidirectionality": 0.8,
        "resilience": 0.6, "latency": 1.2, "bandwidth": 0.7, "cost": 1.0,
        "energy": 1.0, "metadata_minimization": 2.0,
    },
    "EMERGENCY_RESILIENT": {
        "security": 1.6, "privacy": 1.0, "recipient_compatibility": 2.0,
        "reliability": 2.5, "receipt_quality": 1.2, "bidirectionality": 1.0,
        "resilience": 3.0, "latency": 1.1, "bandwidth": 0.3, "cost": 0.2,
        "energy": 0.2, "metadata_minimization": 0.7,
    },
}

AMBIGUOUS = {"INDETERMINATE", "TIMEOUT_AFTER_DISPATCH", "UNKNOWN_AFTER_DISPATCH"}
SUCCESS = {"DELIVERED", "ACKNOWLEDGED", "EXECUTED"}


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _candidate_bearers(edge: Dict[str, Any], recipient: Dict[str, Any], constraints: Dict[str, Any]) -> List[str]:
    bearers = list(edge.get("available_bearers") or [])
    allowed = set(constraints.get("allowed_bearers") or bearers)
    prohibited = set(constraints.get("prohibited_bearers") or [])
    candidates = [b for b in bearers if b in allowed and b not in prohibited]
    state = recipient.get("state")
    if state == "KNOWN":
        accepted = set(recipient.get("accepted_bearers") or [])
        candidates = [b for b in candidates if b in accepted]
    elif state == "UNKNOWN":
        safe = set(recipient.get("safe_fallback_bearers") or [])
        candidates = [b for b in candidates if b in safe]
    elif state == "UNREACHABLE":
        return []
    else:
        raise CommunicationDemoError("recipient state must be KNOWN, UNKNOWN, or UNREACHABLE")
    preference = constraints.get("bearer_preference") or []
    rank = {name: index for index, name in enumerate(preference)}
    return sorted(candidates, key=lambda item: (rank.get(item, len(rank)), item))


def _exclude(edge: Dict[str, Any], recipient: Dict[str, Any], constraints: Dict[str, Any], posture: str) -> List[str]:
    reasons: List[str] = []
    if not edge.get("attested"):
        reasons.append("UNATTESTED_EDGE")
    if edge.get("expired"):
        reasons.append("EXPIRED_ADVERTISEMENT")
    current_edge = constraints.get("current_edge_id")
    if constraints.get("remote_edge_execution_authorized") is False:
        if not current_edge:
            reasons.append("CURRENT_EDGE_REQUIRED")
        elif edge.get("edge_id") != current_edge:
            reasons.append("REMOTE_EDGE_DENIED")
    capabilities = edge.get("capabilities") or {}
    if (posture == "LOCAL_ONLY" or constraints.get("local_only")):
        local = set(capabilities.get("local_bearers") or [])
        if not local.intersection(set(edge.get("available_bearers") or [])):
            reasons.append("LOCALITY_REQUIRED")
    if constraints.get("relay_permission") == "denied" and capabilities.get("requires_relay"):
        reasons.append("RELAY_DENIED")
    if constraints.get("allow_store_and_forward") is False and capabilities.get("store_and_forward"):
        reasons.append("STORE_AND_FORWARD_DENIED")
    if posture == "EMERGENCY_RESILIENT" and not constraints.get("emergency_authority"):
        reasons.append("EMERGENCY_AUTHORITY_REQUIRED")
    if not _candidate_bearers(edge, recipient, constraints):
        reasons.append("NO_RECIPIENT_COMPATIBLE_BEARER")
    minimum = constraints.get("minimum_metrics") or {}
    for key, floor in minimum.items():
        if float((edge.get("metrics") or {}).get(key, 0.0)) < float(floor):
            reasons.append("METRIC_BELOW_MINIMUM:%s" % key)
    return sorted(set(reasons))


def _score(edge: Dict[str, Any], posture: str) -> Dict[str, Any]:
    if posture not in POSTURE_WEIGHTS:
        raise CommunicationDemoError("unsupported posture")
    metrics = edge.get("metrics") or {}
    components: Dict[str, float] = {}
    total = 0.0
    for key, weight in POSTURE_WEIGHTS[posture].items():
        value = float(metrics.get(key, 0.0))
        if not 0.0 <= value <= 1.0:
            raise CommunicationDemoError("metric outside [0,1]: %s" % key)
        components[key] = round(value * weight, 6)
        total += components[key]
    return {"total": round(total, 6), "components": components}


def simulate_selection(packet: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate ST-031 selection without granting runtime authority."""
    posture = packet.get("posture")
    recipient = packet.get("recipient") or {}
    constraints = packet.get("constraints") or {}
    attempt_id = packet.get("attempt_id")
    if not attempt_id:
        raise CommunicationDemoError("attempt_id is required")
    evaluated: List[Dict[str, Any]] = []
    excluded: List[Dict[str, Any]] = []
    edges = list(packet.get("edges") or [])
    for edge in edges:
        reasons = _exclude(edge, recipient, constraints, posture)
        if reasons:
            excluded.append({"edge_id": edge.get("edge_id"), "reasons": reasons})
            continue
        score = _score(edge, posture)
        bearer = _candidate_bearers(edge, recipient, constraints)[0]
        evaluated.append({
            "edge_id": edge["edge_id"],
            "advertisement_id": edge["advertisement_id"],
            "advertisement_sha256": canonical_hash(edge),
            "selected_bearer": bearer,
            "score": score["total"],
            "score_components": score["components"],
        })
    if not evaluated:
        raise CommunicationDemoError("no admissible simulated edge")
    evaluated.sort(key=lambda item: (-item["score"], item["edge_id"], item["advertisement_id"]))
    primary = evaluated[0]
    receipt: Dict[str, Any] = {
        "schema_version": "0.1",
        "sdk_simulation_only": True,
        "authority_granted": False,
        "execution_performed": False,
        "attempt_id": attempt_id,
        "posture": posture,
        "recipient_state": recipient.get("state"),
        "candidate_set_sha256": canonical_hash({"edges": edges, "recipient": recipient, "constraints": constraints}),
        "selected_edge_id": primary["edge_id"],
        "selected_bearer": primary["selected_bearer"],
        "primary_score": primary["score"],
        "primary_score_components": primary["score_components"],
        "fallback_order": [
            {"edge_id": item["edge_id"], "bearer": item["selected_bearer"], "score": item["score"]}
            for item in evaluated[1:]
        ],
        "excluded_paths": sorted(excluded, key=lambda item: str(item.get("edge_id"))),
        "remote_edge_execution_authorized": bool(constraints.get("remote_edge_execution_authorized", True)),
        "multipath_authorized": bool(constraints.get("multipath_authorized", False)),
    }
    receipt["selection_sha256"] = canonical_hash(receipt)
    return receipt


def simulate_recovery(selection: Dict[str, Any], outcome: str, *, side_effect_absence_confirmed: bool = False) -> Dict[str, Any]:
    """Demonstrate the KV/ST-031 fallback invariant without executing transport."""
    if selection.get("sdk_simulation_only") is not True:
        raise CommunicationDemoError("SDK demo accepts simulation selections only")
    if outcome in SUCCESS:
        action = "STOP"
        reason = "TERMINAL_SUCCESS"
    elif outcome in AMBIGUOUS:
        action = "VERIFY_EXTERNALLY"
        reason = "AMBIGUOUS_AFTER_DISPATCH"
    elif outcome == "FAILED" and not side_effect_absence_confirmed:
        action = "VERIFY_EXTERNALLY"
        reason = "SIDE_EFFECT_ABSENCE_NOT_CONFIRMED"
    elif outcome == "FAILED":
        if selection.get("fallback_order"):
            action = "TRY_FALLBACK"
            reason = "CONFIRMED_NO_SIDE_EFFECT"
        else:
            action = "STOP"
            reason = "NO_FALLBACK_REMAINING"
    else:
        raise CommunicationDemoError("unsupported simulated outcome")
    result: Dict[str, Any] = {
        "sdk_simulation_only": True,
        "authority_granted": False,
        "execution_performed": False,
        "selection_sha256": selection["selection_sha256"],
        "observed_outcome": outcome,
        "action": action,
        "reason": reason,
    }
    if action == "TRY_FALLBACK":
        result["fallback"] = selection["fallback_order"][0]
    result["recovery_sha256"] = canonical_hash(result)
    return result


def run_demo(packet: Dict[str, Any]) -> Dict[str, Any]:
    selection = simulate_selection(packet)
    scenarios = {
        "successful_delivery": simulate_recovery(selection, "DELIVERED"),
        "ambiguous_after_dispatch": simulate_recovery(selection, "TIMEOUT_AFTER_DISPATCH"),
        "confirmed_pre_side_effect_failure": simulate_recovery(selection, "FAILED", side_effect_absence_confirmed=True),
    }
    demo = {
        "demo_type": "STEGVERSE_COMMUNICATION_EDGE_CONFORMANCE",
        "sdk_simulation_only": True,
        "authority_granted": False,
        "execution_performed": False,
        "selection": selection,
        "recovery_scenarios": scenarios,
    }
    demo["demo_sha256"] = canonical_hash(demo)
    return demo
