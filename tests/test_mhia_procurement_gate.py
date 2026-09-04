from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from stegverse.mhia_procurement_gate import (
    assert_procurement_freeze_ready,
    evaluate_procurement_candidate_bom,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "prototype-builds" / "mhia-procurement-candidate-bom.v0.json"


def _candidate():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_current_candidate_bom_fails_closed_until_all_evidence_exists():
    result = evaluate_procurement_candidate_bom(_candidate())
    assert result.ready_to_freeze is False
    assert "spring_contact_system.manufacturer_unresolved" in result.blockers
    assert "microphone.orderable_candidate_unresolved" in result.blockers
    assert "removable_battery_cell.cost_checked_not_verified" in result.blockers


def test_frozen_state_cannot_override_missing_evidence():
    packet = _candidate()
    packet["freeze_state"] = "FROZEN"
    result = evaluate_procurement_candidate_bom(packet)
    assert result.ready_to_freeze is False
    assert "frozen_state_without_complete_evidence" in result.blockers
    with pytest.raises(ValueError):
        assert_procurement_freeze_ready(packet)


def test_complete_candidate_can_pass_without_implying_purchase_or_hardware_validation():
    packet = _candidate()
    for item in packet["items"]:
        item["manufacturer"] = item["manufacturer"] or "REFERENCE-MANUFACTURER"
        item["family"] = item["family"] or "REFERENCE-FAMILY"
        item["orderable_candidate"] = item["orderable_candidate"] or f"REFERENCE-{item['role']}"
        item["package"] = item["package"] or "REFERENCE-ENVELOPE"
        for key in item["verification"]:
            item["verification"][key] = True
    result = evaluate_procurement_candidate_bom(packet)
    assert result.ready_to_freeze is True
    assert result.blockers == ()


def test_duplicate_role_is_rejected():
    packet = _candidate()
    packet["items"].append(deepcopy(packet["items"][0]))
    result = evaluate_procurement_candidate_bom(packet)
    assert result.ready_to_freeze is False
    assert "host_mcu.duplicate_role" in result.blockers
