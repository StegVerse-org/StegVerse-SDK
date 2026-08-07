import json, pathlib
from stegverse.admittedcode_receipt import verify_admittedcode_receipt

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "examples/governed_llm_demo/admittedcode"


def _load(name):
    return json.loads((FIXTURE_ROOT / name).read_text())


def test_generated_admittedcode_allow_fixture_verifies_independently():
    receipt = _load("admissibility_receipt.allow.json")
    result = verify_admittedcode_receipt(receipt)
    assert result["status"] == "ACCEPTED"
    assert result["decision"] == "ALLOW"
    assert result["authority_effect"] == "NONE"
    assert result["sdk_validation_is_execution"] is False
    assert result["sdk_intake_is_authority"] is False
    assert receipt["review_packet"]["source_verification"]["verified"] is True
    assert receipt["review_packet"]["source_binding"]["expected_outcome"] == "ALLOW"


def test_generated_admittedcode_deny_fixture_verifies_independently():
    receipt = _load("admissibility_receipt.deny.json")
    result = verify_admittedcode_receipt(receipt)
    assert result["status"] == "ACCEPTED"
    assert result["decision"] == "DENY"
    assert result["authority_effect"] == "NONE"
    assert result["sdk_validation_is_execution"] is False
    assert result["sdk_intake_is_authority"] is False
    assert receipt["key_requested"] is False
    assert receipt["review_packet"]["source_verification"]["verified"] is True
    assert receipt["review_packet"]["source_binding"]["expected_outcome"] == "QUARANTINE"


def test_portable_review_keeps_source_semantics_distinct_from_admittedcode_decision():
    receipt = _load("admissibility_receipt.deny.json")
    assert receipt["review_packet"]["source_binding"]["expected_outcome"] == "QUARANTINE"
    assert receipt["decision"] == "DENY"
    assert receipt["review_packet"]["source_binding"]["expected_outcome"] != receipt["decision"]
