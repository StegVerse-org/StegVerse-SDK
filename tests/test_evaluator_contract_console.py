import copy
import json

import jsonschema
import pytest

from stegverse import evaluator_console
from stegverse.evaluator_contract import evaluator_contract_example, evaluator_contract_schema
from stegverse.governance_reference_graph import validate_governance_reference_graph


def test_contract_schema_matches_public_request_version():
    schema = evaluator_contract_schema()
    assert schema["properties"]["schema_version"]["const"] == "1.0"
    assert "evaluation_declaration" in schema["properties"]
    assert "input" in schema["properties"]


def test_contract_example_is_non_authorizing_and_schema_valid():
    schema = evaluator_contract_schema()
    example = evaluator_contract_example()
    assert example["authority_claim"] is False
    assert example["execution_provenance"]["external_consequence_enabled"] is False
    assert "steggate_request" in example["input"]
    jsonschema.Draft202012Validator(schema).validate(example)


def test_contract_schema_rejects_cross_lane_provenance():
    schema = evaluator_contract_schema()
    invalid = copy.deepcopy(evaluator_contract_example())
    invalid["execution_provenance"]["routing_surface"] = "DEMO_TEST_REPOSITORY"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(invalid)


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


def test_console_governance_graph_summary(capsys):
    assert evaluator_console.main(["governance-graph"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["contract"] == "stegverse.governance-reference-graph.v1"
    assert payload["authority_effect"] == "NONE_REPRESENTATION_ONLY"
    assert payload["unknown_relations_grant_authority"] is False
    assert payload["sdk_resolves_governance"] is False


def test_console_governance_graph_schema_and_example(capsys):
    assert evaluator_console.main(["governance-graph", "--schema"]) == 0
    schema = json.loads(capsys.readouterr().out)
    assert schema["title"] == "StegVerse Governance Reference Graph"

    assert evaluator_console.main(["governance-graph", "--example"]) == 0
    example = json.loads(capsys.readouterr().out)
    jsonschema.Draft202012Validator(schema).validate(example)
    validate_governance_reference_graph(example)
    assert example["metadata"]["example_projection"] == "HITL"
    assert example["metadata"]["example_projection_is_canonical_schema"] is False
    assert example["authority_boundary"]["hierarchy_grants_authority"] is False
