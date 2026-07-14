import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/adapter-system-boundary-session-packet.v1.json"
PROVENANCE = ROOT / "tests/fixtures/adapter-system-boundary-session-packet.v1.provenance.json"


def test_mirrored_fixture_matches_adapter_provenance():
    packet = json.loads(FIXTURE.read_text(encoding="utf-8"))
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))

    declaration = packet["system_boundary_declaration"]
    receipt = packet["system_boundary_declaration_receipt"]
    reference = packet["system_boundary_declaration_ref"]

    assert provenance["producer_repo"] == "StegVerse-org/LLM-adapter"
    assert provenance["consumer_repo"] == "StegVerse-org/StegVerse-SDK"
    assert provenance["consumer_fixture"] == "tests/fixtures/adapter-system-boundary-session-packet.v1.json"
    assert declaration["declaration_id"] == provenance["declaration_id"]
    assert reference["declaration_id"] == provenance["declaration_id"]
    assert reference["digest"] == provenance["declaration_digest"]
    assert receipt["receipt_hash"] == provenance["receipt_hash"]
    assert reference["receipt_hash"] == provenance["receipt_hash"]
    assert receipt["source_commit"] == provenance["source_commit"]

    non_claims = provenance["required_non_claims"]
    for key in ("authorizing", "custody_transferred", "admissibility_determined", "production_binding_enabled"):
        assert reference[key] == non_claims[key]
    assert declaration["authority"]["model_has_execution_authority"] is non_claims["model_has_execution_authority"]
    for key in ("consciousness_claim", "personhood_claim", "welfare_claim"):
        assert declaration["claims_boundary"][key] == non_claims[key]
