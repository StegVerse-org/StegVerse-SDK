from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas" / "prototype-builds"
EXAMPLE_DIR = ROOT / "examples" / "prototype-builds"

MODULE_SCHEMA = SCHEMA_DIR / "mhia-module-manifest.v1.schema.json"
MODULE_EXAMPLE = EXAMPLE_DIR / "mhia-left-ear-sensor-module.v1.json"
MECH_SCHEMA = SCHEMA_DIR / "mhia-mechanical-attachment-profile.v1.schema.json"
MECH_EXAMPLE = EXAMPLE_DIR / "mhia-ear-mechanical-profile.v1.json"
ELECTRICAL_SCHEMA = SCHEMA_DIR / "mhia-electrical-data-interface.v1.schema.json"
ELECTRICAL_EXAMPLE = EXAMPLE_DIR / "mhia-ear-electrical-data-interface.v1.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(schema_path: Path, example_path: Path):
    schema = _load(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(_load(example_path))
    return schema


def test_all_reference_contracts_validate():
    assert _validate(MODULE_SCHEMA, MODULE_EXAMPLE)["properties"]["schema"]["const"] == "stegverse.mhia.module_manifest.v1"
    assert _validate(MECH_SCHEMA, MECH_EXAMPLE)["properties"]["schema"]["const"] == "stegverse.mhia.mechanical_attachment_profile.v1"
    assert _validate(ELECTRICAL_SCHEMA, ELECTRICAL_EXAMPLE)["properties"]["schema"]["const"] == "stegverse.mhia.electrical_data_interface.v1"


@pytest.mark.parametrize(
    "field,value",
    [
        ("discovery_grants_authority", True),
        ("attachment_grants_authority", True),
        ("external_consequence_requires_admission", False),
    ],
)
def test_module_authority_boundary_fails_closed(field, value):
    packet = deepcopy(_load(MODULE_EXAMPLE))
    packet["authority_boundary"][field] = value
    with pytest.raises(ValidationError):
        Draft202012Validator(_load(MODULE_SCHEMA)).validate(packet)


def test_capability_id_requires_machine_readable_namespace():
    packet = deepcopy(_load(MODULE_EXAMPLE))
    packet["capabilities"][0]["id"] = "not a capability id"
    with pytest.raises(ValidationError):
        Draft202012Validator(_load(MODULE_SCHEMA)).validate(packet)


def test_module_provenance_is_required():
    packet = deepcopy(_load(MODULE_EXAMPLE))
    del packet["module"]["provenance"]
    with pytest.raises(ValidationError):
        Draft202012Validator(_load(MODULE_SCHEMA)).validate(packet)


@pytest.mark.parametrize(
    "section,field,value",
    [
        ("power", "role_negotiation_required", False),
        ("power", "energize_before_negotiation", True),
        ("discovery", "manifest_required_before_capability_use", False),
        ("discovery", "identity_required", False),
        ("discovery", "discovery_grants_authority", True),
        ("fault_behavior", "overcurrent_isolation", False),
        ("fault_behavior", "overvoltage_isolation", False),
        ("fault_behavior", "thermal_shutdown", False),
        ("fault_behavior", "unknown_module_power_state", "POWERED"),
        ("fault_behavior", "invalid_manifest_behavior", "ALLOW"),
    ],
)
def test_electrical_contract_fails_closed(section, field, value):
    packet = deepcopy(_load(ELECTRICAL_EXAMPLE))
    packet[section][field] = value
    with pytest.raises(ValidationError):
        Draft202012Validator(_load(ELECTRICAL_SCHEMA)).validate(packet)


def test_mechanical_profile_requires_user_serviceability_and_cycles():
    packet = deepcopy(_load(MECH_EXAMPLE))
    packet["serviceability"]["cycle_target"] = 50
    with pytest.raises(ValidationError):
        Draft202012Validator(_load(MECH_SCHEMA)).validate(packet)
