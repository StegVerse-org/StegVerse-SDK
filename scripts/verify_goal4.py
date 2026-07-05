#!/usr/bin/env python3
"""Run SDK AI Entry checks without network access."""
from __future__ import annotations

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
    (sys.executable, "scripts/check_ai_entry_sdk_access_decision_completion.py"),
    (sys.executable, "scripts/check_ai_entry_no_manual_tasks.py"),
    (sys.executable, "-m", "pytest", "tests/test_micro_node_return_path.py", "-v"),
    (sys.executable, "-m", "pytest", "tests/test_ai_entry_receipt_capture.py", "-v"),
)


def run_command(command: Sequence[str]) -> None:
    completed = subprocess.run(
        list(command),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print("$ " + " ".join(command))
    print(completed.stdout.rstrip())
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    for command in COMMANDS:
        run_command(command)
    print("SDK_GOAL4_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
