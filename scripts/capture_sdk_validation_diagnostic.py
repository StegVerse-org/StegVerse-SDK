#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "evidence" / "sdk-validation-diagnostic.json"

COMMANDS = [
    [sys.executable, "scripts/verify_universal_entry_envelope.py"],
    [sys.executable, "scripts/verify_free_tier_metadata_ingestion.py"],
    [sys.executable, "scripts/verify_hps_sdk_route.py", "examples/hps_sdk_route_allowed.json"],
    [sys.executable, "scripts/verify_hps_sdk_route.py", "examples/hps_sdk_route_expired.json"],
    [sys.executable, "scripts/verify_hps_sdk_route.py", "examples/hps_sdk_route_fail_closed.json"],
    [sys.executable, "scripts/verify_sdk_transition_candidate.py", "examples/sdk_transition_candidate.json"],
    [sys.executable, "scripts/verify_llm_route_comparison.py"],
    [sys.executable, "scripts/verify_comparison_orchestrator.py"],
    [sys.executable, "-m", "pytest", "tests/", "-q", "--maxfail=1"],
]


def main() -> int:
    records = []
    first_failure = None
    for command in COMMANDS:
        completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        record = {
            "command": command,
            "exit_code": completed.returncode,
            "output_tail": completed.stdout[-4000:],
        }
        records.append(record)
        if completed.returncode != 0:
            first_failure = record
            break

    payload = {
        "schema_version": "1.0.0",
        "record_type": "sdk_validation_diagnostic",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if first_failure is None else "FAIL",
        "first_failure": first_failure,
        "commands_executed": records,
        "manual_user_action_required": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"SDK VALIDATION DIAGNOSTIC: {payload['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
