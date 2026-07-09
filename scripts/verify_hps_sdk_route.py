#!/usr/bin/env python3
"""Verify SDK HPS route decisions.

This script intentionally uses only the Python standard library.
It validates that SDK route decisions do not treat HPS as a static status flag.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DECISION_ALLOW = "ALLOW"
DECISION_DENY = "DENY"
DECISION_REVIEW = "REVIEW"
DECISION_FAIL_CLOSED = "FAIL_CLOSED"

REQUIRED_TOP = {
    "route_type",
    "route_id",
    "capability",
    "heartbeat_result",
    "standing_class",
    "standing_required",
    "capability_window_state",
    "supports",
    "expiration_triggers",
    "expected_decision",
}

REQUIRED_SUPPORTS = {
    "authority_valid",
    "policy_current",
    "delegation_current",
    "evidence_fresh",
    "coordinate_valid",
    "reconstruction_available",
}

VALID_DECISIONS = {DECISION_ALLOW, DECISION_DENY, DECISION_REVIEW, DECISION_FAIL_CLOSED}


@dataclass(frozen=True)
class RouteResult:
    ok: bool
    decision: str
    errors: list[str]


def require_keys(obj: dict[str, Any], required: set[str], location: str, errors: list[str]) -> None:
    for key in sorted(required - set(obj.keys())):
        errors.append(f"missing required field: {location}.{key}")


def load_route(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("route root must be a JSON object")
    return data


def standing_satisfies(actual: str, required: str) -> bool:
    order = {"FAILED": 0, "DEGRADED": 1, "RESTORED": 2}
    return order.get(actual, -1) >= order.get(required, 99)


def decide(route: dict[str, Any]) -> RouteResult:
    errors: list[str] = []
    require_keys(route, REQUIRED_TOP, "route", errors)
    if errors:
        return RouteResult(False, DECISION_FAIL_CLOSED, errors)

    if route.get("route_type") != "hps_sdk_route":
        errors.append("route.route_type must be hps_sdk_route")

    supports = route.get("supports", {})
    if not isinstance(supports, dict):
        errors.append("route.supports must be an object")
        supports = {}
    require_keys(supports, REQUIRED_SUPPORTS, "supports", errors)

    expiration_triggers = route.get("expiration_triggers", [])
    if not isinstance(expiration_triggers, list):
        errors.append("route.expiration_triggers must be a list")
        expiration_triggers = []

    if route.get("expected_decision") not in VALID_DECISIONS:
        errors.append("route.expected_decision is not recognized")

    heartbeat = route.get("heartbeat_result")
    standing_class = route.get("standing_class")
    standing_required = route.get("standing_required")
    window_state = route.get("capability_window_state")

    # Fail-closed conditions: missing/unknown heartbeat, failed standing, missing
    # reconstruction, invalid coordinate, or authority collapse.
    if heartbeat in {None, "UNKNOWN", "FAIL_CLOSED", "FAIL-CLOSED"}:
        decision = DECISION_FAIL_CLOSED
    elif standing_class == "FAILED":
        decision = DECISION_FAIL_CLOSED
    elif supports.get("reconstruction_available") is not True:
        decision = DECISION_FAIL_CLOSED
    elif supports.get("coordinate_valid") is not True:
        decision = DECISION_FAIL_CLOSED
    elif supports.get("authority_valid") is not True and window_state != "REVIEW":
        decision = DECISION_FAIL_CLOSED
    elif window_state == "REVIEW":
        decision = DECISION_REVIEW
    elif window_state in {"CLOSED", "EXPIRED"}:
        decision = DECISION_DENY
    elif expiration_triggers:
        decision = DECISION_DENY
    elif not standing_satisfies(str(standing_class), str(standing_required)):
        decision = DECISION_DENY
    elif heartbeat != "PASS":
        decision = DECISION_DENY
    elif any(supports.get(field) is not True for field in REQUIRED_SUPPORTS):
        decision = DECISION_DENY
    else:
        decision = DECISION_ALLOW

    expected = route.get("expected_decision")
    if expected in VALID_DECISIONS and expected != decision:
        errors.append(f"expected_decision {expected} does not match actual decision {decision}")

    return RouteResult(not errors, decision, errors)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: verify_hps_sdk_route.py <route.json>", file=sys.stderr)
        return 2
    try:
        result = decide(load_route(Path(argv[1])))
    except Exception as exc:
        print(f"FAIL_CLOSED: could not read route: {exc}", file=sys.stderr)
        return 1

    print(f"decision: {result.decision}")
    for error in result.errors:
        print(f"- {error}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
