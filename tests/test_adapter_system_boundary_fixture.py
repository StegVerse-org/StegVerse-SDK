import json
from pathlib import Path

from stegverse import build_governed_llm_manifest, build_governed_llm_receipt_handoff


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/adapter_system_boundary_sdk_packet.v0.1.json"


def test_adapter_produced_fixture_enters_sdk_serialization_without_reconstruction():
    packet = json.loads(FIXTURE.read_text(encoding="utf-8"))

    manifest = build_governed_llm_manifest(packet)
    receipt = build_governed_llm_receipt_handoff(packet)

    expected_ref = packet["system_boundary_declaration_ref"]
    assert manifest["system_boundary_declaration"] == packet["system_boundary_declaration"]
    assert manifest["system_boundary_declaration_ref"] == expected_ref
    assert receipt["system_boundary_declaration_ref"] == expected_ref
    assert receipt["manifest"]["system_boundary_declaration_ref"] == expected_ref
    assert expected_ref["receipt_hash"] == packet["system_boundary_declaration_receipt"]["receipt_hash"]
    assert expected_ref["authorizing"] is False
    assert expected_ref["custody_transferred"] is False
    assert expected_ref["admissibility_determined"] is False
    assert expected_ref["production_binding_enabled"] is False


def test_adapter_fixture_preserves_transition_and_run_identity():
    packet = json.loads(FIXTURE.read_text(encoding="utf-8"))
    declaration = packet["system_boundary_declaration"]

    assert f"transition://{packet['transition_id']}" in declaration["continuity"]["evidence_refs"]
    assert f"run://{packet['run_id']}" in declaration["continuity"]["evidence_refs"]
    assert packet["system_boundary_declaration_ref"]["declaration_id"] == declaration["declaration_id"]
