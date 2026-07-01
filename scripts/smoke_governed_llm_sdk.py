#!/usr/bin/env python3
"""Smoke test SDK governed LLM validation, intake, manifest, and receipt handoff."""

from __future__ import annotations

import json

from stegverse import build_governed_llm_receipt_handoff


SESSION_PACKET = {
    "provider_request": {"provider": "fixture", "model": "fixture", "messages": []},
    "provider_request_hash": "request-hash",
    "provider_response": {
        "provider": "fixture",
        "model": "fixture",
        "output": "read only output",
        "request_hash": "request-hash",
        "response_hash": "response-hash",
    },
    "continuity": {"freshness_status": "current", "evidence": []},
    "adapter_result": {
        "decision": "ALLOW",
        "admissibility_status": "allowed_read_only_candidate",
        "reconstruction": {"decision": "ALLOW"},
    },
    "action_route": {"route_status": "no_action_route_required", "action_candidates": []},
    "commitment_request": {"status": "no_commitment_request_required"},
    "authority_decision": {"decision": "NOT_REQUIRED", "authority_decision_hash": "authority-hash"},
    "execution_handoff": {"status": "not_executable", "execution_handoff_hash": "handoff-hash"},
}


def main() -> int:
    handoff = build_governed_llm_receipt_handoff(SESSION_PACKET)
    expected = {
        "receipt_status": "route_ready_record_retained",
        "intake_decision": "ROUTE",
        "route": "route_read_only_or_external_executor_handoff",
        "retain_record": True,
    }
    actual = {
        "receipt_status": handoff["receipt_status"],
        "intake_decision": handoff["intake_decision"],
        "route": handoff["route"],
        "retain_record": handoff["retain_record"],
    }
    if actual != expected:
        print(json.dumps({"status": "FAIL", "expected": expected, "actual": actual}, indent=2, sort_keys=True))
        return 1

    print(json.dumps({"status": "PASS", "actual": actual}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
