from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from stegverse.mhia_capability_graph import MHIACompositionError, compose_capability_graph


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = ROOT / "examples" / "prototype-builds"


def _load(name: str):
    return json.loads((EXAMPLE_DIR / name).read_text(encoding="utf-8"))


def _left():
    return _load("mhia-left-ear-sensor-module.v1.json")


def _right():
    return _load("mhia-right-ear-power-audio-module.v1.json")


def test_asymmetric_left_right_composition_is_deterministic():
    graph_a = compose_capability_graph([_left(), _right()])
    graph_b = compose_capability_graph([_right(), _left()])
    assert graph_a == graph_b
    assert [m["side"] for m in graph_a["modules"]] == ["left", "right"]
    ids = {c["capability_id"] for c in graph_a["capabilities"]}
    assert "SENSOR.MIC.ARRAY4" in ids
    assert "POWER.BATTERY.18WH" in ids
    assert "OUTPUT.AUDIO.STEREO_LEFT" in ids
    assert "OUTPUT.AUDIO.STEREO_RIGHT" in ids


def test_composition_never_inherits_authority():
    graph = compose_capability_graph([_left(), _right()])
    boundary = graph["authority_boundary"]
    assert boundary == {
        "discovery_grants_authority": False,
        "attachment_grants_authority": False,
        "composition_grants_authority": False,
        "authority_inherited_from_modules": False,
        "external_consequence_requires_admission": True,
    }


def test_duplicate_module_identity_fails_closed():
    duplicate = deepcopy(_left())
    with pytest.raises(MHIACompositionError, match="duplicate module_id"):
        compose_capability_graph([_left(), duplicate])


@pytest.mark.parametrize(
    "field,value",
    [
        ("discovery_grants_authority", True),
        ("attachment_grants_authority", True),
        ("external_consequence_requires_admission", False),
    ],
)
def test_unsafe_module_authority_claim_fails_closed(field, value):
    module = _left()
    module["authority_boundary"][field] = value
    with pytest.raises(MHIACompositionError):
        compose_capability_graph([module])


def test_incompatible_capability_declarations_are_quarantined():
    left = _left()
    right = _right()
    right["capabilities"].append(
        {
            "id": "SENSOR.MIC.ARRAY4",
            "version": "2",
            "direction": "output",
            "consequence_class": "external",
            "constraints": {},
            "calibration_ref": None,
        }
    )
    graph = compose_capability_graph([left, right])
    assert not any(c["capability_id"] == "SENSOR.MIC.ARRAY4" for c in graph["capabilities"])
    conflict = next(c for c in graph["conflicts"] if c["capability_id"] == "SENSOR.MIC.ARRAY4")
    assert conflict["usable"] is False
    assert conflict["reason"] == "INCOMPATIBLE_DECLARATIONS"


def test_compatible_duplicate_capability_keeps_multiple_providers():
    left = _left()
    right = _right()
    duplicate_capability = deepcopy(left["capabilities"][0])
    right["capabilities"].append(duplicate_capability)
    graph = compose_capability_graph([left, right])
    capability = next(c for c in graph["capabilities"] if c["capability_id"] == duplicate_capability["id"])
    assert len(capability["providers"]) == 2
