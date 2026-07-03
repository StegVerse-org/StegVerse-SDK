#!/usr/bin/env python3

"""
verify_governed_llm_demo_packet.py
----------------------------------

This script verifies the structure of a governed LLM demonstration session
packet.  It is designed to operate on the simplified packets produced by
the end‑to‑end demo in the LLM adapter, not on full production packets.

The script checks that:

* The packet is valid JSON.
* Required keys (`query`, `request_hash`, `provider_response`, `evidence`,
  `authority_decision`) are present.
* The authority decision is `ALLOW` for a simple informational query.

If the packet passes these checks, the script prints a success message and
exits with code 0.  Otherwise, it prints an error message and exits with
code 1.

Usage:
    python scripts/verify_governed_llm_demo_packet.py --session examples/governed_llm_demo/session_packet.simple_query.json
"""

import argparse
import json
import sys


def verify_demo_packet(path: str) -> bool:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            packet = json.load(fh)
    except Exception as exc:
        print(f"Error reading session packet: {exc}")
        return False
    required_keys = ["query", "request_hash", "provider_response", "evidence", "authority_decision"]
    missing = [k for k in required_keys if k not in packet]
    if missing:
        print(f"Missing required keys: {', '.join(missing)}")
        return False
    if not isinstance(packet.get("evidence"), dict):
        print("Evidence must be an object")
        return False
    decision = packet.get("authority_decision")
    if not isinstance(decision, str):
        print("Authority decision must be a string in the demo packet")
        return False
    if packet.get("query").strip().lower().startswith("what is the capital"):
        if decision != "ALLOW":
            print(f"Expected authority decision 'ALLOW' for simple query, got '{decision}'")
            return False
    print("Demo packet verification passed.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a governed LLM demo session packet")
    parser.add_argument("--session", required=True, help="Path to the governed session JSON file")
    args = parser.parse_args()
    ok = verify_demo_packet(args.session)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()