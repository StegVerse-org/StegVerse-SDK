#!/usr/bin/env python3
"""Verify Goal 4 demo session interface stabilization record."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "goal4-demo-session-interface-stabilization.json"
GOAL4 = ROOT / "scripts" / "verify_goal4.py"
GUARD = ROOT / "scripts" / "check_goal4_demo_session_argument.py"
FIXTURE = ROOT / "fixtures" / "governed-llm-demo-session.json"


def stop(message: str) -> None:
    raise SystemExit(f"SDK_GOAL4_DEMO_SESSION_INTERFACE_STABILIZATION_FAIL: {message}")


def main() -> int:
    data = json.loads(RECORD.read_text(encoding="utf-8"))
    if data.get("schema_version") != "stegverse.sdk.goal4_demo_session_interface_stabilization.v0.1":
        stop("bad schema version")
    if data.get("state") != "preserved_guard_installed":
        stop("state mismatch")
    interface = data.get("protected_interface", {})
    if interface.get("required_argument") != "--session":
        stop("required argument mismatch")
    for path in (GOAL4, GUARD, FIXTURE):
        if not path.exists():
            stop(f"missing {path.relative_to(ROOT)}")
    goal4_text = GOAL4.read_text(encoding="utf-8")
    if "scripts/check_goal4_demo_session_argument.py" not in goal4_text:
        stop("Goal 4 guard not wired")
    if "--session" not in goal4_text:
        stop("Goal 4 session argument missing")
    if data.get("manual_tasks_remaining") != []:
        stop("manual tasks must remain empty")
    if data.get("next_goal_candidate") != "Goal 8 continuation after Goal 4 guard confirmation":
        stop("next goal candidate mismatch")
    print("SDK_GOAL4_DEMO_SESSION_INTERFACE_STABILIZATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
