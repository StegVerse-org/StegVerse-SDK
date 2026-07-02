#!/usr/bin/env python3
"""Verify the static governed LLM demo packet.

This check validates the demonstration packet shape without granting execution
authority, persistence authority, or master-record installation authority.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SESSION = REPO_ROOT / "examples" / "governed_llm_demo" / "session_packet.simple_query.json"


REQUIRED_FIELDS = [
    "query",
    "request_hash",
    "provider_response",
    "evidence",
    "action",
    "authority_decision",
    "receipt_id",
    "action_route",
    "commitment_request",
    "execution_handoff",
]


def fail(message: str) -> int:
    print(f"GOVERNED LLM DEMO PACKET: FAIL - {message}")
    return 1


def load_packet(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in packet:
            errors.append(f"missing field: {field}")
    if packet.get("query") != "What is the capital of France?":
        errors.append("unexpected query")
    if packet.get("authority_decision") != "ALLOW":
        errors.append("simple query should ALLOW")
    if packet.get("action") != "NONE":
        errors.append("simple query should not route an action")
    if packet.get("action_route") is not None:
        errors.append("action_route must be null for simple query")
    if packet.get("commitment_request") is not None:
        errors.append("commitment_request must be null for simple query")
    if packet.get("execution_handoff") is not None:
        errors.append("execution_handoff must be null for simple query")
    evidence = packet.get("evidence", {})
    if evidence.get("stale") is not False:
        errors.append("evidence.stale must be false")
    if not evidence.get("sources"):
        errors.append("evidence.sources must not be empty")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", default=str(DEFAULT_SESSION))
    args = parser.parse_args()
    session = Path(args.session)
    if not session.is_absolute():
        session = REPO_ROOT / session
    packet = load_packet(session)
    errors = validate(packet)
    if errors:
        return fail("; ".join(errors))
    print("GOVERNED LLM DEMO PACKET: PASS - demo packet is valid and non-executing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
