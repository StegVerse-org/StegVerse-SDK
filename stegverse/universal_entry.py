"""Universal entry routing primitives for StegVerse.

This module normalizes a manifest-bound request, evaluates declared node
capabilities, selects admissible routing lanes, and returns a non-authorizing
governed response envelope plus a deterministic routing receipt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
import re
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence

LANES = (
    "conversation",
    "ecosystem_query",
    "external_llm",
    "solver",
    "execution",
)

CAPABILITY_TO_LANE = {
    "conversation": "conversation",
    "ecosystem_read": "ecosystem_query",
    "external_llm": "external_llm",
    "solver": "solver",
    "execution": "execution",
}

RESTRICTED_PATTERNS = (
    re.compile(r"\b(secret|token|credential|deploy key|private key)\b", re.I),
    re.compile(r"\b(force[- ]?push|delete (?:branch|tag|repo|repository|workflow|release))\b", re.I),
    re.compile(r"\b(change permissions?|disable workflow|edit workflow)\b", re.I),
)

ECOSYSTEM_TERMS = (
    "stegverse",
    "site",
    "sdk",
    "manifest",
    "receipt",
    "handoff",
    "continuity",
    "admissibility",
    "transition",
    "publisher",
    "master-records",
    "repository",
)

EXTERNAL_TERMS = (
    "latest",
    "current news",
    "search the web",
    "external source",
    "outside research",
    "public web",
    "internet",
)

SOLVER_PATTERN = re.compile(
    r"(?:\bsolve\b|\bcalculate\b|\bequation\b|\bderivative\b|\bintegral\b|\d+\s*[+\-*/=]\s*\d+)",
    re.I,
)


class UniversalEntryError(ValueError):
    """Raised when an entry envelope violates a universal routing invariant."""


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Mapping[str, Any]) -> str:
    return "sha256:" + sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CapabilityRegistry:
    """Operational capability posture for a single portable node."""

    states: Mapping[str, str]

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "CapabilityRegistry":
        raw = data.get("capabilities", data)
        if not isinstance(raw, Mapping):
            raise UniversalEntryError("capability registry must be a mapping")
        states: Dict[str, str] = {}
        for capability in CAPABILITY_TO_LANE:
            value = raw.get(capability, "unavailable")
            if isinstance(value, bool):
                value = "operational" if value else "unavailable"
            value = str(value).lower()
            if value not in {"operational", "degraded", "unavailable", "disabled"}:
                raise UniversalEntryError(f"invalid capability state: {capability}={value}")
            states[capability] = value
        return cls(states=states)

    def allows(self, capability: str) -> bool:
        return self.states.get(capability) in {"operational", "degraded"}

    def state(self, capability: str) -> str:
        return self.states.get(capability, "unavailable")


@dataclass(frozen=True)
class RouteDecision:
    requested_lanes: Sequence[str]
    selected_lanes: Sequence[str]
    unavailable_lanes: Sequence[str]
    restricted: bool
    failed_closed: bool
    reason_codes: Sequence[str] = field(default_factory=tuple)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requested_lanes": list(self.requested_lanes),
            "selected_lanes": list(self.selected_lanes),
            "unavailable_lanes": list(self.unavailable_lanes),
            "restricted": self.restricted,
            "failed_closed": self.failed_closed,
            "reason_codes": list(self.reason_codes),
        }


def _request_text(envelope: Mapping[str, Any]) -> str:
    request = envelope.get("request")
    if not isinstance(request, Mapping):
        raise UniversalEntryError("request must be a mapping")
    text = request.get("message", request.get("content", ""))
    if not isinstance(text, str) or not text.strip():
        raise UniversalEntryError("request message/content must be non-empty text")
    return text.strip()


def _allowed_lanes(envelope: Mapping[str, Any]) -> List[str]:
    routing = envelope.get("routing")
    if not isinstance(routing, Mapping):
        raise UniversalEntryError("routing must be a mapping")
    allowed = routing.get("allowed_lanes")
    if allowed is None:
        allowed = [lane for lane in LANES if routing.get(f"{lane}_allowed") is True]
    if not isinstance(allowed, list):
        raise UniversalEntryError("routing.allowed_lanes must be a list")
    invalid = sorted(set(allowed) - set(LANES))
    if invalid:
        raise UniversalEntryError(f"unknown allowed lanes: {', '.join(invalid)}")
    return list(dict.fromkeys(allowed))


def _declared_capabilities(envelope: Mapping[str, Any]) -> List[str]:
    request = envelope.get("request", {})
    values = request.get("requested_capabilities", []) if isinstance(request, Mapping) else []
    if not isinstance(values, list):
        raise UniversalEntryError("request.requested_capabilities must be a list")
    invalid = sorted(set(values) - set(CAPABILITY_TO_LANE))
    if invalid:
        raise UniversalEntryError(f"unknown requested capabilities: {', '.join(invalid)}")
    return list(dict.fromkeys(values))


def classify_lanes(envelope: Mapping[str, Any]) -> List[str]:
    """Classify a request into one or more execution-neutral routing lanes."""

    text = _request_text(envelope)
    lowered = text.casefold()
    declared = _declared_capabilities(envelope)
    lanes = [CAPABILITY_TO_LANE[name] for name in declared]

    if any(pattern.search(text) for pattern in RESTRICTED_PATTERNS):
        return ["execution"]

    if SOLVER_PATTERN.search(text):
        lanes.append("solver")
    if any(term in lowered for term in ECOSYSTEM_TERMS):
        lanes.append("ecosystem_query")
    if any(term in lowered for term in EXTERNAL_TERMS):
        lanes.append("external_llm")

    # Conversation is the default interpretation layer and remains present for
    # natural synthesis unless the request is purely an execution request.
    if "execution" not in lanes:
        lanes.insert(0, "conversation")

    return list(dict.fromkeys(lanes or ["conversation"]))


def route_universal_entry(
    envelope: Mapping[str, Any],
    registry: CapabilityRegistry | Mapping[str, Any],
) -> RouteDecision:
    """Select lanes while enforcing manifest and capability boundaries."""

    if not isinstance(registry, CapabilityRegistry):
        registry = CapabilityRegistry.from_mapping(registry)

    allowed = _allowed_lanes(envelope)
    requested = classify_lanes(envelope)
    request = envelope.get("request", {})
    external_allowed = bool(request.get("external_information_allowed", False)) if isinstance(request, Mapping) else False
    restricted = any(pattern.search(_request_text(envelope)) for pattern in RESTRICTED_PATTERNS)

    selected: List[str] = []
    unavailable: List[str] = []
    reasons: List[str] = []

    for lane in requested:
        if lane not in allowed:
            unavailable.append(lane)
            reasons.append(f"LANE_NOT_ALLOWED:{lane}")
            continue
        if lane == "external_llm" and not external_allowed:
            unavailable.append(lane)
            reasons.append("EXTERNAL_INFORMATION_PROHIBITED")
            continue
        capability = next(name for name, mapped in CAPABILITY_TO_LANE.items() if mapped == lane)
        if not registry.allows(capability):
            unavailable.append(lane)
            reasons.append(f"CAPABILITY_{registry.state(capability).upper()}:{capability}")
            continue
        selected.append(lane)

    if restricted:
        selected = []
        reasons.append("RESTRICTED_REQUEST_REQUIRES_SEPARATE_AUTHORITY")

    failed_closed = restricted or not selected
    if failed_closed and "FAILED_CLOSED" not in reasons:
        reasons.append("FAILED_CLOSED")

    return RouteDecision(
        requested_lanes=requested,
        selected_lanes=selected,
        unavailable_lanes=list(dict.fromkeys(unavailable)),
        restricted=restricted,
        failed_closed=failed_closed,
        reason_codes=list(dict.fromkeys(reasons)),
    )


def build_routing_receipt(
    envelope: Mapping[str, Any],
    decision: RouteDecision,
) -> Dict[str, Any]:
    origin = envelope.get("origin", {})
    continuity = envelope.get("continuity", {})
    receipt_body: Dict[str, Any] = {
        "receipt_type": "stegverse.routing_receipt.v0.1",
        "authorizing": False,
        "execution_authority_granted": False,
        "custody_transferred": False,
        "admissibility_determined": False,
        "origin_entry_point": origin.get("entry_point") if isinstance(origin, Mapping) else None,
        "session_id": origin.get("session_id") if isinstance(origin, Mapping) else None,
        "message_id": origin.get("message_id") if isinstance(origin, Mapping) else None,
        "request_digest": digest(dict(envelope)),
        "route_decision": decision.to_dict(),
        "previous_receipt_id": continuity.get("previous_receipt_id") if isinstance(continuity, Mapping) else None,
    }
    receipt_body["receipt_id"] = digest(receipt_body)
    return receipt_body


def build_governed_return(
    envelope: Mapping[str, Any],
    decision: RouteDecision,
    *,
    response_text: str | None = None,
) -> Dict[str, Any]:
    receipt = build_routing_receipt(envelope, decision)
    if response_text is None:
        if decision.failed_closed:
            response_text = "The request could not be routed through the capabilities and authority available to this node."
        elif decision.unavailable_lanes:
            response_text = "The request was routed through available capabilities; unavailable lanes were preserved as explicit degradation."
        else:
            response_text = "The request was accepted for non-authorizing governed routing."

    return {
        "schema": "stegverse.governed_return.v0.1",
        "status": "failed_closed" if decision.failed_closed else "routed",
        "response": response_text,
        "selected_lanes": list(decision.selected_lanes),
        "unavailable_lanes": list(decision.unavailable_lanes),
        "authority": {
            "execution_authority_granted": False,
            "admissibility_determined": False,
            "custody_transferred": False,
        },
        "routing_receipt": receipt,
    }


def process_universal_entry(
    envelope: Mapping[str, Any],
    registry: CapabilityRegistry | Mapping[str, Any],
) -> Dict[str, Any]:
    decision = route_universal_entry(envelope, registry)
    return build_governed_return(envelope, decision)
