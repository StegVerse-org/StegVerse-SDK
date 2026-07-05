#!/usr/bin/env python3
"""Run SDK return-path and AI Entry receipt preview checks without network access."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]

COMMANDS: tuple[tuple[str, ...], ...] = (
    (sys.executable, "scripts/check_workflow_parity.py"),
    (sys.executable, "scripts/check_sdk_local_import_path.py"),
    (sys.executable, "scripts/smoke_governed_llm_sdk.py"),
    (sys.executable, "scripts/verify_governed_llm_demo_packet.py"),
    (sys.executable, "scripts/check_pytest_compatibility_surface.py"),
    (sys.executable, "-m", "pytest", "tests/test_governed_llm_demo_packet.py", "-v"),
    (sys.executable, "scripts/verify_micro_node_return_path.py"),
    (sys.executable, "scripts/verify_ai_entry_receipt_capture.py"),
    (sys.executable, "scripts/check_ai_entry_receipt_issuer_boundary.py"),
    (sys.executable, "scripts/check_ai_entry_receipt_preview_fixtures.py"),
    (sys.executable, "scripts/check_ai_entry_sdk_access_decision_boundary.py"),
    (sys.executable, "scripts/check_ai_entry_sdk_access_decision_fixtures.py"),
    (sys.executable, "scripts/check_ai_entry_no_manual_tasks.py"),
    (sys.executable, "-m", "pytest", "tests/test_micro_node_return_path.py", "-v"),
    (sys.executable, "-m", "pytest", "tests/test_ai_entry_receipt_capture.py", "-v"),
)


def run_command(command: Sequence[str]) -> dict[str, object]:
    completed = subprocess.run(
        list(command),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = completed.stdout
    print("$ " + " ".join(command))
    print(output.rstrip())
    return {
        "command": " ".join(command),
        "returncode": completed.returncode,
        "passed": completed.returncode == 0,
        "output": output,
    }


def main() -> int:
    results: list[dict[str, object]] = []
    for command in COMMANDS:
        result = run_command(command)
        results.append(result)
        if not result["passed"]:
            report = {
                "goal": "SDK AI Entry checks",
                "repository": "StegVerse-org/StegVerse-SDK",
                "complete": False,
                "command": result["command"],
                "returncode": result["returncode"],
                "next_step": "inspect command output",
            }
            print(json.dumps(report, indent=2, sort_keys=True))
            return 1
    report = {
        "goal": "SDK AI Entry checks",
        "repository": "StegVerse-org/StegVerse-SDK",
        "complete": True,
        "results": results,
        "next_step": "review command output",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
