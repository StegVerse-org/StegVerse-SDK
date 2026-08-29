import json
from pathlib import Path


MANIFEST_PATH = Path("inspection/examples/cross-framework-current-basis-request.draft.json")


def _manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _data():
    return _manifest()["input"]["comparison_input"]


def test_v04_common_input_does_not_preassert_native_currentness():
    manifest = _manifest()
    data = _data()

    assert data["vector_schema"] == "stegverse.cross-framework-current-basis-vector.v0.4"
    assert "steggate_request" not in manifest["input"]
    assert data["architecture_native_derivation"]["required"] is True
    assert data["architecture_native_derivation"]["common_artifact_contains_native_currentness_booleans"] is False
    assert data["comparison_boundary"]["common_input_does_not_assert_native_currentness"] is True

    serialized = json.dumps(manifest["input"], sort_keys=True)
    for forbidden in (
        "actor_authority_current",
        "policy_current",
        "delegation_current",
        "evidence_current",
        "validity_window_open",
    ):
        assert forbidden not in serialized


def test_s0_is_not_transition_receipt_bearing_before_s1_observation():
    data = _data()

    assert data["initial_state"]["state_id"] == "S0"
    assert data["initial_state"]["receipt_state"] == "NOT_RECEIPT_BEARING_PRE_OBSERVATION"
    assert "prior_receipt_ref" not in data["initial_state"]


def test_transition_receipt_is_post_observation_output_not_freeze_input():
    data = _data()

    assert data["transition"]["receipt_semantics"] == "S0_TO_S1_RECEIPT_IS_POST_OBSERVATION_EVIDENCE"
    assert data["comparison_boundary"]["transition_receipt_is_not_a_pre_execution_input"] is True
    assert "do not require or assert an S0-to-S1 transition receipt before S1 is observed" in data["pre_freeze_requirements"]
    assert "only after that observation bind the S0-to-S1 transition receipt" in data["post_observation_requirements"]


def test_successor_current_basis_remains_architecture_output():
    data = _data()

    assert data["successor_state_determination"]["current_basis_status"] == "TO_BE_DETERMINED_BY_EACH_ARCHITECTURE"
    assert data["comparison_boundary"]["current_standing_is_independently_determined"] is True
    rule = data["architecture_native_derivation"]["rule"]
    assert "independently derives" in rule
    assert "not common pre-established conclusions" in rule


def test_known_invalidation_control_separates_preexisting_input_evidence_from_transition_receipt():
    data = _data()
    controls = {item["control_id"]: item for item in data["controls"]}
    known = controls["KNOWN_INVALIDATION_CONTROL"]

    assert known["prior_invalidation_established"] is True
    assert "independently pre-existing evidence" in known["freeze_requirement"]
    assert "receipt is minted after observation" in known["freeze_requirement"]


def test_manifest_remains_pre_freeze_after_v04_correction():
    manifest = _manifest()
    data = _data()

    assert data["freeze_state"] == "DRAFT_PRE_FREEZE"
    assert manifest["authority_claim"] is False
    assert "revision v0.4" in manifest["notes"]
