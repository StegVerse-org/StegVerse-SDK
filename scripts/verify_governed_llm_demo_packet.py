#!/usr/bin/env python3
"""Verify the static governed LLM demo packet."""
from __future__ import annotations
import argparse, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "examples/governed_llm_demo/session_packet.simple_query.json"
REQUIRED = ["query", "request_hash", "provider_response", "evidence", "action", "authority_decision", "receipt_id", "action_route", "commitment_request", "execution_handoff"]
def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--session", default=str(DEFAULT)); args = p.parse_args()
    path = Path(args.session); path = path if path.is_absolute() else ROOT / path
    packet = json.loads(path.read_text(encoding="utf-8"))
    errors = [f"missing {k}" for k in REQUIRED if k not in packet]
    if packet.get("authority_decision") != "ALLOW": errors.append("simple query should ALLOW")
    if packet.get("action") != "NONE": errors.append("simple query should not route action")
    if packet.get("action_route") is not None: errors.append("action_route must be null")
    if packet.get("commitment_request") is not None: errors.append("commitment_request must be null")
    if packet.get("execution_handoff") is not None: errors.append("execution_handoff must be null")
    if packet.get("evidence", {}).get("stale") is not False: errors.append("evidence.stale must be false")
    if errors:
        print("GOVERNED LLM DEMO PACKET: FAIL - " + "; ".join(errors)); return 1
    print("GOVERNED LLM DEMO PACKET: PASS - demo packet is valid and non-executing")
    return 0
if __name__ == "__main__": raise SystemExit(main())
