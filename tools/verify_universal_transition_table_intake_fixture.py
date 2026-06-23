#!/usr/bin/env python3
"""Verify SDK universal transition-table intake fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from stegverse.universal_transition_table_intake import handle_universal_transition_table_package

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "universal_transition_table_intake"
OUT = FIXTURE / "sdk_intake_result.json"


def main() -> int:
    result = handle_universal_transition_table_package(
        FIXTURE / "transition_test_package.json",
        FIXTURE / "expected_result.json",
        FIXTURE / "replay_packet.json",
        FIXTURE / "commitment_candidate.json",
    )
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    assert result["manifest"]["route_eligible"] is True
    assert result["manifest"]["commitment_candidate_present"] is True
    assert result["commitment_candidate_receipt"]["accepted_as_non_authorizing"] is True
    assert result["commitment_candidate_receipt"]["authorizing"] is False
    assert result["commitment_candidate_receipt"]["implies_standing"] is False
    assert result["route_eligibility_receipt"]["fresh_standing_determination_required"] is True

    print("PASS universal transition-table intake fixture verified")
    print(f"PASS wrote SDK intake result: {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
