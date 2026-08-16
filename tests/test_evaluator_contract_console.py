import json

from stegverse import evaluator_console
from stegverse.evaluator_contract import evaluator_contract_example, evaluator_contract_schema


def test_contract_schema_matches_public_request_version():
    schema = evaluator_contract_schema()
    assert schema["properties"]["schema_version"]["const"] == "1.0"
    assert "evaluation_declaration" in schema["properties"]
    assert "input" in schema["properties"]


def test_contract_example_is_non_authorizing():
    example = evaluator_contract_example()
    assert example["authority_claim"] is False
    assert example["execution_provenance"]["external_consequence_enabled"] is False
    assert "steggate_request" in example["input"]


def test_console_contract_summary(capsys):
    assert evaluator_console.main(["contract"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["contract"] == "stegverse.public-inspection-request.v1"
    assert payload["schema_command"] == "stegverse contract --schema"


def test_console_contract_schema(capsys):
    assert evaluator_console.main(["contract", "--schema"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["title"] == "StegVerse Public Inspection Request"


def test_console_contract_example(capsys):
    assert evaluator_console.main(["contract", "--example"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["case_profile"] == "custom-declarative"
