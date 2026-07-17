"""Dependency-injected engine dispatch for universal-entry routing.

Entry adapters never call providers, solvers, repositories, or executors
directly. They submit a universal entry envelope to this dispatcher with a
registry of lane handlers. The dispatcher preserves route order, captures
per-lane results, fails closed on handler errors, and returns a governed
response envelope with a deterministic dispatch receipt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, MutableMapping, Protocol, Sequence

from .universal_entry import (
    CapabilityRegistry,
    RouteDecision,
    build_governed_return,
    digest,
    route_universal_entry,
)


class LaneHandler(Protocol):
    def __call__(
        self,
        envelope: Mapping[str, Any],
        context: Mapping[str, Any],
    ) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class HandlerRegistry:
    handlers: Mapping[str, LaneHandler]

    def get(self, lane: str) -> LaneHandler | None:
        return self.handlers.get(lane)


class UniversalDispatchError(RuntimeError):
    """Raised for malformed handler results or invalid dispatch configuration."""


def _validate_handler_result(lane: str, result: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(result, Mapping):
        raise UniversalDispatchError(f"handler for {lane} must return a mapping")
    status = str(result.get("status", "")).lower()
    if status not in {"completed", "degraded", "unavailable", "failed_closed"}:
        raise UniversalDispatchError(
            f"handler for {lane} returned invalid status: {status or '<missing>'}"
        )
    normalized = dict(result)
    normalized["lane"] = lane
    normalized["status"] = status
    normalized.setdefault("authorizing", False)
    normalized.setdefault("execution_authority_granted", False)
    normalized.setdefault("custody_transferred", False)
    normalized.setdefault("admissibility_determined", False)
    if normalized["authorizing"] is not False:
        raise UniversalDispatchError(f"handler for {lane} attempted authority escalation")
    if normalized["execution_authority_granted"] is not False:
        raise UniversalDispatchError(f"handler for {lane} attempted execution escalation")
    if normalized["custody_transferred"] is not False:
        raise UniversalDispatchError(f"handler for {lane} attempted custody escalation")
    if normalized["admissibility_determined"] is not False:
        raise UniversalDispatchError(f"handler for {lane} attempted admissibility escalation")
    return normalized


def build_dispatch_receipt(
    envelope: Mapping[str, Any],
    decision: RouteDecision,
    lane_results: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    result_summaries = [
        {
            "lane": result.get("lane"),
            "status": result.get("status"),
            "result_digest": digest(dict(result)),
        }
        for result in lane_results
    ]
    body: Dict[str, Any] = {
        "receipt_type": "stegverse.dispatch_receipt.v0.1",
        "authorizing": False,
        "execution_authority_granted": False,
        "custody_transferred": False,
        "admissibility_determined": False,
        "request_digest": digest(dict(envelope)),
        "selected_lanes": list(decision.selected_lanes),
        "failed_closed": decision.failed_closed,
        "lane_results": result_summaries,
    }
    body["receipt_id"] = digest(body)
    return body


def _default_response_text(
    decision: RouteDecision,
    lane_results: Sequence[Mapping[str, Any]],
) -> str:
    if decision.failed_closed:
        return "The request failed closed before any operational engine was invoked."
    failed = [r for r in lane_results if r.get("status") == "failed_closed"]
    unavailable = [r for r in lane_results if r.get("status") == "unavailable"]
    degraded = [r for r in lane_results if r.get("status") == "degraded"]
    if failed:
        return "One or more selected engines failed closed; no authority or execution was inferred."
    if unavailable:
        return "The request was only partially completed because one or more selected engines were unavailable."
    if degraded:
        return "The request completed through a degraded capability path."
    return "The request completed through the selected non-authorizing engines."


def _response_text(
    decision: RouteDecision,
    lane_results: Sequence[Mapping[str, Any]],
) -> str:
    """Use terminal conversation output when available, otherwise a bounded default."""
    if not decision.failed_closed:
        for result in reversed(lane_results):
            if result.get("lane") != "conversation":
                continue
            if result.get("status") not in {"completed", "degraded"}:
                break
            response = result.get("response")
            if isinstance(response, str) and response.strip():
                return response.strip()
            break
    return _default_response_text(decision, lane_results)


def _dispatch_order(selected_lanes: Sequence[str]) -> list[str]:
    """Run conversation last when it must synthesize other lane results."""
    lanes = list(selected_lanes)
    if "conversation" in lanes and len(lanes) > 1:
        lanes.remove("conversation")
        lanes.append("conversation")
    return lanes


def dispatch_universal_entry(
    envelope: Mapping[str, Any],
    capability_registry: CapabilityRegistry | Mapping[str, Any],
    handler_registry: HandlerRegistry | Mapping[str, LaneHandler],
    *,
    initial_context: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Route and dispatch a universal entry envelope through lane handlers.

    Handlers receive the immutable request envelope and an accumulated context
    containing the original universal envelope and prior lane results. The
    dispatcher catches handler exceptions, converts them into fail-closed lane
    results, and never grants authority.
    """

    if not isinstance(handler_registry, HandlerRegistry):
        handler_registry = HandlerRegistry(dict(handler_registry))

    decision = route_universal_entry(envelope, capability_registry)
    if decision.failed_closed:
        result = build_governed_return(envelope, decision)
        result["lane_results"] = []
        result["dispatch_receipt"] = build_dispatch_receipt(envelope, decision, [])
        return result

    context: MutableMapping[str, Any] = dict(initial_context or {})
    context["universal_entry_envelope"] = envelope
    context["route_decision"] = decision.to_dict()
    context["lane_results"] = []
    lane_results = []

    for lane in _dispatch_order(decision.selected_lanes):
        handler = handler_registry.get(lane)
        if handler is None:
            result = {
                "lane": lane,
                "status": "unavailable",
                "reason": "HANDLER_NOT_REGISTERED",
                "authorizing": False,
                "execution_authority_granted": False,
                "custody_transferred": False,
                "admissibility_determined": False,
            }
        else:
            try:
                result = _validate_handler_result(lane, handler(envelope, dict(context)))
            except Exception as exc:  # fail-closed boundary
                result = {
                    "lane": lane,
                    "status": "failed_closed",
                    "reason": f"HANDLER_FAILURE:{type(exc).__name__}",
                    "authorizing": False,
                    "execution_authority_granted": False,
                    "custody_transferred": False,
                    "admissibility_determined": False,
                }
        lane_results.append(result)
        context["lane_results"] = list(lane_results)
        context[f"{lane}_result"] = result

    any_failed = any(result["status"] == "failed_closed" for result in lane_results)
    effective_decision = decision
    if any_failed:
        effective_decision = RouteDecision(
            requested_lanes=decision.requested_lanes,
            selected_lanes=decision.selected_lanes,
            unavailable_lanes=decision.unavailable_lanes,
            restricted=decision.restricted,
            failed_closed=True,
            reason_codes=[*decision.reason_codes, "ENGINE_DISPATCH_FAILED_CLOSED"],
        )

    governed_return = build_governed_return(
        envelope,
        effective_decision,
        response_text=_response_text(effective_decision, lane_results),
    )
    governed_return["lane_results"] = lane_results
    governed_return["dispatch_receipt"] = build_dispatch_receipt(
        envelope, effective_decision, lane_results
    )
    return governed_return
