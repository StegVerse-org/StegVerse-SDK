import json
from pathlib import Path


MANIFEST_PATH = Path("inspection/examples/cross-framework-current-basis-request.draft.json")


def _manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_s0_is_not_transition_receipt_bearing_before_s1_observation():
    manifest = _manifest()
    data = manifest["input"]["input_data"]
    continuity = manifest["input"]["steggate_request"]["continuity"]

    assert data["vector_schema"] == "stegverse.cross-framework-current-basis-vector.v0.3"
    assert data["initial_state"]["state_id"] == "S0"
    assert data["initial_state"]["receipt_state"] == "NOT_RECEIPT_BEARING_PRE_OBSERVATION"
    assert "prior_receipt_ref" not in data["initial_state"]
    assert continuity["required"] is False
    assert continuity["previous_receipt_verified"] is False
    assert continuity["previous_receipt_hash"] == "UNAVAILABLE_BEFORE_S1_OBSERVATION"


def test_transition_receipt_is_post_observation_output_not_freeze_input():
    data = _manifest()["input"]["input_data"]

    assert data["transition"]["receipt_semantics"] == "S0_TO_S1_RECEIPT_IS_POST_OBSERVATION_EVIDENCE"
    assert data["comparison_boundary"]["transition_receipt_is_not_a_pre_execution_input"] is True
    assert any(
        "do not require or assert an S0-to-S1 transition receipt before S1 is observed" == requirement
        for requirement in data["pre_freeze_requirements"]
    )
    assert any(
        "only after that observation bind the S0-to-S1 transition receipt" == requirement
        for requirement in data["post_observation_requirements"]
    )


def test_known_invalidation_control_separates_preexisting_input_evidence_from_transition_receipt():
    data = _manifest()["input"]["input_data"]
    controls = {item["control_id"]: item for item in data["controls"]}
    known = controls["KNOWN_INVALIDATION_CONTROL"]

    assert known["prior_invalidation_established"] is True
    assert "independently pre-existing evidence" in known["freeze_requirement"]
    assert "transition receipt is minted after observation" in known["freeze_requirement"]


def test_manifest_remains_pre_freeze_after_semantic_correction():
    manifest = _manifest()
    data = manifest["input"]["input_data"]

    assert data["freeze_state"] == "DRAFT_PRE_FREEZE"
    assert manifest["authority_claim"] is False
    assert "revision v0.3" in manifest["notes"]
