import json
from pathlib import Path

from stegverse.governed_llm_manifest import build_governed_llm_manifest
from stegverse.governed_llm_receipt import build_governed_llm_receipt_handoff


FIXTURE = Path("examples/adapter_governed_llm_session_packet.json")


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_adapter_origin_fixture_enters_manifest_serialization_directly():
    packet = load_fixture()
    manifest = build_governed_llm_manifest(packet)

    assert manifest["source_repo"] == "StegVerse-org/LLM-adapter"
    assert manifest["manifest_type"] == "governed_llm_session"
    assert manifest["intake_decision"] == "ROUTE"
    assert manifest["intake"]["validation_decision"] == "ALLOW"
    assert manifest["manifest_hash"]
    assert manifest["intake"]["session_hash"] == manifest["session_hash"]


def test_adapter_origin_fixture_enters_receipt_handoff_directly():
    packet = load_fixture()
    receipt = build_governed_llm_receipt_handoff(packet)

    assert receipt["source_repo"] == "StegVerse-org/StegVerse-SDK"
    assert receipt["receipt_hash"]
    assert receipt["manifest"]["source_repo"] == "StegVerse-org/LLM-adapter"
    assert receipt["manifest"]["intake_decision"] == "ROUTE"
    assert receipt["manifest"]["intake"]["validation_decision"] == "ALLOW"


def test_adapter_origin_fixture_remains_non_executable():
    packet = load_fixture()
    assert packet["execution_handoff"]["status"] == "not_executable"
    assert packet["authority_decision"]["decision"] == "NOT_REQUIRED"
    assert packet["action_route"]["action_candidates"] == []
