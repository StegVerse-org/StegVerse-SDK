"""MIR round-trip demo (Leg A of DEMO__MIR_ROUNDTRIP__SCOPING__01).

The demo composes installed SDK machinery to walk the canonical
MIR round-trip sequence at demonstrated-capability grade. These
tests assert the per-state mapping, including which canonical
states stand NOT_OBSERVED — the demo must never present a
demonstrated leg as an admitted runtime transition.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "mir_roundtrip_demo", ROOT / "examples" / "mir_roundtrip_demo.py"
)
demo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(demo)


def test_positive_leg_reaches_return_readiness_with_honest_limits():
    report = demo.run_roundtrip()
    assert report["demo_grade"] == "DEMONSTRATED_CAPABILITY"
    assert report["authentic_runtime_completion"] is False
    assert report["destination_profile"] == "MIR"
    assert report["execution_disposition"] == "ALLOW"
    assert report["communication_state"] == "READY_FOR_FINAL_STEGVERSE_EGRESS_TRANSITION"
    # The limits are stated by the machinery itself, not by prose.
    assert report["intr_admission_observed"] is False
    assert report["organization_receipt_observed"] is False
    assert report["interlock_intr_egress_observed"] is False
    assert report["far_side_transition_observed"] is False
    assert report["evidence_packet_verified"] is True
    assert report["evidence_packet_conditions"] == [
        {"requirement_id": "mir-roundtrip-governance", "disposition": "SUPPORTED"}
    ]


def test_negative_leg_refuses_authority_bearing_return_fail_closed():
    report = demo.run_roundtrip()
    negative = report["negative_leg"]
    assert negative["outcome"] == "MIR_GOVERNED_RETURN_FAIL_CLOSED"
    assert negative["refused"] is True
    assert "authority expansion" in negative["reason"]


def test_state_mapping_covers_the_canonical_sequence_in_order():
    report = demo.run_roundtrip()
    states = [row["state"] for row in report["state_mapping"]]
    assert states == demo.CANONICAL_SEQUENCE


def test_state_mapping_grades_match_the_scoped_honesty_boundary():
    report = demo.run_roundtrip()
    not_observed = {
        row["state"] for row in report["state_mapping"] if row["grade"] == "NOT_OBSERVED"
    }
    assert not_observed == demo.NOT_OBSERVED_STATES
    demonstrated = {
        row["state"] for row in report["state_mapping"] if row["grade"] == "DEMONSTRATED"
    }
    assert demonstrated == set(demo.CANONICAL_SEQUENCE) - demo.NOT_OBSERVED_STATES
    # Every row names its evidence; a grade without evidence is
    # the label-only failure this demo exists to avoid.
    assert all(row["evidence"] for row in report["state_mapping"])
