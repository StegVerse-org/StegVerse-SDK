#!/usr/bin/env python3
"""Verify SDK-side micro-node adapter fixture compatibility."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "examples" / "micro_node_adapter_fixture"

REQUEST_FIELDS = {
    "transition_id",
    "origin_system",
    "return_path",
    "action",
    "actor",
    "target",
    "scope",
    "policy_ref",
    "delegation_ref",
    "payload",
}

RETURN_FIELDS = {
    "transition_id",
    "return_path",
    "decision",
    "receipt_hash",
    "returned_to_origin",
    "runtime_execution_granted",
    "provider_output_is_authority",
}


def read_json(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def main() -> int:
    request = read_json("request.json")
    returned = read_json("governed_return.json")
    failures: list[str] = []

    missing_request = sorted(REQUEST_FIELDS - set(request))
    missing_return = sorted(RETURN_FIELDS - set(returned))
    if missing_request:
        failures.append(f"request missing fields: {missing_request}")
    if missing_return:
        failures.append(f"governed return missing fields: {missing_return}")

    if request.get("transition_id") != returned.get("transition_id"):
        failures.append("transition_id mismatch")
    if request.get("return_path") != returned.get("return_path"):
        failures.append("return_path mismatch")
    if returned.get("decision") not in {"ALLOW", "DENY", "FAIL_CLOSED"}:
        failures.append("invalid terminal decision")
    if not returned.get("receipt_hash"):
        failures.append("missing receipt hash")
    if returned.get("returned_to_origin") is not True:
        failures.append("return path was not preserved")
    if returned.get("runtime_execution_granted") is not False:
        failures.append("runtime execution must remain disabled")
    if returned.get("provider_output_is_authority") is not False:
        failures.append("provider output must not become authority")
    if request.get("payload", {}).get("execution_authority_requested") is not False:
        failures.append("adapter request must not request execution authority")

    if failures:
        print("SDK_MICRO_NODE_ADAPTER_FIXTURE_FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("SDK_MICRO_NODE_ADAPTER_FIXTURE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
