import json, pathlib
from stegverse.admittedcode_receipt import verify_admittedcode_receipt

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_generated_admittedcode_fixture_verifies_independently():
    path = ROOT / "examples/governed_llm_demo/admittedcode/admissibility_receipt.allow.json"
    result = verify_admittedcode_receipt(json.loads(path.read_text()))
    assert result["status"] == "ACCEPTED"
    assert result["decision"] == "ALLOW"
    assert result["authority_effect"] == "NONE"
    assert result["sdk_validation_is_execution"] is False
    assert result["sdk_intake_is_authority"] is False
