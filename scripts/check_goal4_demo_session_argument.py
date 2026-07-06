#!/usr/bin/env python3
"""Verify Goal 4 passes a stable demo session fixture to the packet verifier."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOAL4 = ROOT / "scripts" / "verify_goal4.py"
FIXTURE = ROOT / "fixtures" / "governed-llm-demo-session.json"
REQUIRED_COMMAND_PARTS = (
    "scripts/verify_governed_llm_demo_packet.py",
    "--session",
    "fixtures/governed-llm-demo-session.json",
)
REQUIRED_KEYS = {
    "query",
    "request_hash",
    "provider_response",
    "evidence",
    "authority_decision",
}


def stop(message: str) -> None:
    raise SystemExit(f"SDK_GOAL4_DEMO_SESSION_ARGUMENT_FAIL: {message}")


def main() -> int:
    goal4_text = GOAL4.read_text(encoding="utf-8")
    for part in REQUIRED_COMMAND_PARTS:
        if part not in goal4_text:
            stop(f"verify_goal4.py missing {part}")
    packet = json.loads(FIXTURE.read_text(encoding="utf-8"))
    missing = REQUIRED_KEYS.difference(packet)
    if missing:
        stop("fixture missing keys: " + ", ".join(sorted(missing)))
    if packet.get("authority_decision") != "ALLOW":
        stop("fixture authority decision must be ALLOW")
    if not isinstance(packet.get("evidence"), dict):
        stop("fixture evidence must be object")
    print("SDK_GOAL4_DEMO_SESSION_ARGUMENT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
