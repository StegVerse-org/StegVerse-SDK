#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
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

REQUIRED_MODULES = ["jsonschema", "pytest", "requests", "yaml", "dotenv"]


def git_value(*args: str) -> str | None:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.stdout.strip() or None


def main() -> int:
    dependency_state = {
        module: importlib.util.find_spec(module) is not None for module in REQUIRED_MODULES
    }
    missing_dependencies = sorted(
        module for module, installed in dependency_state.items() if not installed
    )

    records = []
    first_failure = None
    failure_class = None

    if missing_dependencies:
        failure_class = "DIAGNOSTIC_ENVIRONMENT_INCOMPLETE"
        first_failure = {
            "command": [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
            "exit_code": 1,
            "output_tail": "Missing importable modules after dependency installation: "
            + ", ".join(missing_dependencies),
        }
    else:
        for command in COMMANDS:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            record = {
                "command": command,
                "exit_code": completed.returncode,
                "output_tail": completed.stdout[-4000:],
            }
            records.append(record)
            if completed.returncode != 0:
                failure_class = "SDK_VALIDATION_FAILURE"
                first_failure = record
                break

    source_commit = git_value("rev-parse", "HEAD")
    payload = {
        "schema_version": "1.2.0",
        "record_type": "sdk_validation_diagnostic",
        "generated_at": git_value("show", "-s", "--format=%cI", "HEAD"),
        "source_commit_sha": source_commit,
        "python_executable": sys.executable,
        "dependency_state": dependency_state,
        "missing_dependencies": missing_dependencies,
        "status": "PASS" if first_failure is None else "FAIL",
        "failure_class": failure_class,
        "first_failure": first_failure,
        "commands_executed": records,
        "manual_user_action_required": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2) + "\n"
    if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == rendered:
        print("SDK VALIDATION DIAGNOSTIC: UNCHANGED")
    else:
        OUTPUT.write_text(rendered, encoding="utf-8")
        print(f"SDK VALIDATION DIAGNOSTIC: {payload['status']}")
    print(f"SOURCE COMMIT: {source_commit}")
    print(f"FAILURE CLASS: {payload['failure_class'] or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
