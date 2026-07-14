#!/usr/bin/env python3
"""Validate the durable Goal 7 continuation record."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "data" / "goal7-repo-standards-gate-record-status.json"


def main() -> int:
    if not STATUS.exists():
        raise SystemExit("SDK GOAL7 STATUS: FAIL - status record missing")
    data = json.loads(STATUS.read_text(encoding="utf-8"))
    expected = {
        "status_id": "sdk-goal7-repo-standards-gate-record",
        "repository": "StegVerse-org/StegVerse-SDK",
        "status": "REPO_LOCAL_IMPLEMENTATION_COMPLETE",
        "workflow_strategy": "existing consolidated workflow; no new workflow",
        "archive_status": "READY_FOR_HANDOFF",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise SystemExit(
                f"SDK GOAL7 STATUS: FAIL - {key} expected {value!r}, got {data.get(key)!r}"
            )
    required_surfaces = {
        "stegverse/repo_standards_gate_record.py",
        "schemas/repo_standards_gate_record.schema.json",
        "tests/test_repo_standards_gate_record.py",
        "docs/REPO_STANDARDS_GATE_RECORD.md",
        "scripts/verify_goal7.py",
        "stegverse/__init__.py public exports",
    }
    if not required_surfaces.issubset(set(data.get("installed_surfaces", []))):
        raise SystemExit("SDK GOAL7 STATUS: FAIL - installed surface list incomplete")
    boundaries = data.get("authority_boundaries", {})
    if any(value is not False for value in boundaries.values()):
        raise SystemExit("SDK GOAL7 STATUS: FAIL - authority boundary elevated")
    print("SDK GOAL7 STATUS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
