import json
from copy import deepcopy
from pathlib import Path

import pytest

from stegverse import build_governed_llm_manifest, build_governed_llm_receipt_handoff
from stegverse.system_boundary_round_trip import validate_system_boundary_round_trip


FIXTURE = Path(__file__).parent / "fixtures" / "adapter-system-boundary-session-packet.v1.json"


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_adapter_origin_fixture_enters_manifest_without_reconstruction():
    packet = load_fixture()
    declaration = packet["system_boundary_declaration"]
    source_receipt = packet["system_boundary_declaration_receipt"]
    source_ref = packet["system_boundary_declaration_ref"]

    verification = validate_system_boundary_round_trip(
        declaration, source_receipt, source_ref
    )
    assert verification.accepted is True

    manifest = build_governed_llm_manifest(packet)
    handoff = build_governed_llm_receipt_handoff(packet)

    assert manifest["system_boundary_declaration"] == declaration
    assert manifest["system_boundary_declaration_ref"] == source_ref
    assert handoff["system_boundary_declaration_ref"] == source_ref
    assert handoff["manifest"]["system_boundary_declaration_ref"] == source_ref
    assert source_ref["receipt_hash"] == source_receipt["receipt_hash"]
    assert source_ref["production_binding_enabled"] is False


def test_adapter_origin_fixture_replay_is_reference_stable():
    first = build_governed_llm_manifest(load_fixture())
    second = build_governed_llm_manifest(load_fixture())

    assert first["system_boundary_declaration_ref"] == second["system_boundary_declaration_ref"]
    assert first["system_boundary_declaration"]["declaration_id"] == second["system_boundary_declaration"]["declaration_id"]


def test_adapter_origin_fixture_receipt_tamper_fails_closed():
    packet = load_fixture()
    packet["system_boundary_declaration_receipt"]["receipt_hash"] = "sha256:" + "0" * 64

    with pytest.raises(ValueError, match="round trip"):
        build_governed_llm_manifest(packet)


def test_adapter_origin_fixture_production_escalation_fails_closed():
    packet = deepcopy(load_fixture())
    packet["system_boundary_declaration_ref"]["production_binding_enabled"] = True

    with pytest.raises(ValueError, match="production_binding_enabled"):
        build_governed_llm_manifest(packet)
