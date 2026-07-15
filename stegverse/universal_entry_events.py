"""Continuation events for universal-entry routing and engine activity."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

_ALLOWED_EVENT_TYPES = {
    "routing",
    "retrieval",
    "provider_usage",
    "solver",
    "synthesis",
}


class UniversalEntryEventError(ValueError):
    pass


def _canonical(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Mapping[str, Any]) -> str:
    return "sha256:" + sha256(_canonical(value).encode("utf-8")).hexdigest()


def build_continuation_event(
    *,
    event_type: str,
    envelope: Mapping[str, Any],
    payload: Mapping[str, Any],
    prior_event_id: str | None = None,
) -> dict[str, Any]:
    if event_type not in _ALLOWED_EVENT_TYPES:
        raise UniversalEntryEventError(f"unsupported event_type: {event_type}")
    origin = envelope.get("origin")
    continuity = envelope.get("continuity")
    if not isinstance(origin, Mapping) or not isinstance(continuity, Mapping):
        raise UniversalEntryEventError("origin and continuity are required")
    required = {
        "session_id": origin.get("session_id"),
        "message_id": origin.get("message_id"),
        "transition_id": continuity.get("transition_id"),
        "run_id": continuity.get("run_id"),
    }
    missing = [name for name, value in required.items() if not str(value or "").strip()]
    if missing:
        raise UniversalEntryEventError(f"missing event identity: {', '.join(missing)}")
    body = {
        "schema": "stegverse.universal_entry_event.v0.1",
        "event_type": event_type,
        "session_id": required["session_id"],
        "message_id": required["message_id"],
        "transition_id": required["transition_id"],
        "run_id": required["run_id"],
        "origin_entry_point": origin.get("entry_point"),
        "prior_event_id": prior_event_id,
        "payload": dict(payload),
        "authorizing": False,
        "execution_authority_granted": False,
        "custody_transferred": False,
        "admissibility_determined": False,
    }
    body["event_id"] = _digest(body)
    return body


def build_dispatch_event_chain(
    envelope: Mapping[str, Any],
    governed_return: Mapping[str, Any],
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    routing = build_continuation_event(
        event_type="routing",
        envelope=envelope,
        payload={
            "selected_lanes": list(governed_return.get("selected_lanes", [])),
            "unavailable_lanes": list(governed_return.get("unavailable_lanes", [])),
            "status": governed_return.get("status"),
            "routing_receipt_id": (governed_return.get("routing_receipt") or {}).get("receipt_id"),
            "dispatch_receipt_id": (governed_return.get("dispatch_receipt") or {}).get("receipt_id"),
        },
    )
    events.append(routing)
    prior = routing["event_id"]
    for result in governed_return.get("lane_results", []) or []:
        lane = result.get("lane")
        if lane == "ecosystem_query":
            event_type = "retrieval"
            payload = {
                "status": result.get("status"),
                "sources": list(result.get("sources", []) or []),
                "evidence_count": result.get("evidence_count", 0),
            }
        elif lane == "external_llm":
            event_type = "provider_usage"
            payload = {
                "status": result.get("status"),
                "provider": result.get("provider"),
                "model": result.get("model"),
                "usage": result.get("usage"),
                "provider_receipt": result.get("provider_receipt"),
            }
        elif lane == "solver":
            event_type = "solver"
            payload = {
                "status": result.get("status"),
                "expression": result.get("expression"),
                "result": result.get("result"),
                "checked_locally": result.get("checked_locally", False),
            }
        elif lane == "conversation" and result.get("synthesis") is True:
            event_type = "synthesis"
            payload = {
                "status": result.get("status"),
                "source_count": result.get("source_count", 0),
                "sources": list(result.get("sources", []) or []),
            }
        else:
            continue
        event = build_continuation_event(
            event_type=event_type,
            envelope=envelope,
            payload=payload,
            prior_event_id=prior,
        )
        events.append(event)
        prior = event["event_id"]
    return events


def validate_event_chain(events: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    prior: str | None = None
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(events):
        if raw.get("schema") != "stegverse.universal_entry_event.v0.1":
            raise UniversalEntryEventError("unsupported event schema")
        if raw.get("event_type") not in _ALLOWED_EVENT_TYPES:
            raise UniversalEntryEventError("unsupported event type")
        if raw.get("prior_event_id") != prior:
            raise UniversalEntryEventError(f"event chain discontinuity at index {index}")
        if any(raw.get(field) is not False for field in (
            "authorizing", "execution_authority_granted", "custody_transferred", "admissibility_determined"
        )):
            raise UniversalEntryEventError("event attempted authority or custody escalation")
        expected = dict(raw)
        event_id = expected.pop("event_id", None)
        if event_id != _digest(expected):
            raise UniversalEntryEventError("event digest mismatch")
        normalized.append(dict(raw))
        prior = str(event_id)
    return normalized
