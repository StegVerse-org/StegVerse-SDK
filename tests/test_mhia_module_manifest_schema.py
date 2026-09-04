from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "prototype-builds" / "mhia-module-manifest.v1.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "prototype-builds" / "mhia-left-ear-sensor-module.v1.json"


def _schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _example():
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def test_schema_is_draft_2020_12_and_has_canonical_identity():
    schema = _schema()
    Draft202012Validator.check_schema(schema)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["properties"]["schema"]["const"] == "stegverse.mhia.module_manifest.v1"


def test_reference_module_manifest_validates():
    Draft202012Validator(_schema()).validate(_example())


@pytest.mark.parametrize(
    "field,value",
    [
        ("discovery_grants_authority", True),
        ("attachment_grants_authority", True),
        ("external_consequence_requires_admission", False),
    ],
)
def test_authority_boundary_fails_closed(field, value):
    packet = deepcopy(_example())
    packet["authority_boundary"][field] = value
    with pytest.raises(ValidationError):
        Draft202012Validator(_schema()).validate(packet)


def test_capability_id_requires_machine_readable_namespace():
    packet = deepcopy(_example())
    packet["capabilities"][0]["id"] = "not a capability id"
    with pytest.raises(ValidationError):
        Draft202012Validator(_schema()).validate(packet)


def test_module_provenance_is_required():
    packet = deepcopy(_example())
    del packet["module"]["provenance"]
    with pytest.raises(ValidationError):
        Draft202012Validator(_schema()).validate(packet)
