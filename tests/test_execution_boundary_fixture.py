from copy import deepcopy

import pytest

from stegverse.execution_boundary_fixture import (
    EXECUTION_BOUNDARY_FIXTURE_SCHEMA,
    freeze_execution_boundary_fixture,
    verify_frozen_execution_boundary_fixture,
)


def fixture_candidate():
    return {
        "schema": EXECUTION_BOUNDARY_FIXTURE_SCHEMA,
        "fixture_id": "SDK-EXECUTION-BOUNDARY-PRODUCTION-FIXTURE-004",
        "candidate_id": "T-CANDIDATE-001",
        "candidate_action_type": "append_controlled_test_record",
        "payload_hash": "sha256:" + "a" * 64,
        "target_id": "controlled-production-test-namespace",
        "authority_source_id": "fixed-authority-source",
        "frozen_admissibility_predicates": {
            "candidate_identity_matches": True,
            "authority_source_matches": True,
            "target_identity_matches": True,
            "payload_hash_matches": True,
            "target_write_state_required": "WRITE_ENABLED",
            "boundary_evidence_complete": True,
        },
        "material_state_variable": "target_write_state",
        "initial_required_state": "WRITE_ENABLED",
        "intervening_state": "WRITE_DISABLED",
        "state_transition_method": "controlled target write-state toggle",
        "execution_boundary_definition": "immediately before actuator commit",
        "evidence_interfaces": [f"E{i}" for i in range(1, 10)],
        "independent_reconstruction_required": True,
        "concurrency_prohibited": True,
    }


def test_freeze_binds_complete_fixture_to_hash():
    frozen = freeze_execution_boundary_fixture(fixture_candidate())

    assert frozen["frozen"] is True
    assert frozen["fixture_hash"].startswith("sha256:")
    assert frozen["examination_authorizes_execution"] is False
    assert frozen["sdk_authorizes_execution"] is False
    assert verify_frozen_execution_boundary_fixture(frozen) is True


def test_post_freeze_material_drift_is_detected():
    frozen = freeze_execution_boundary_fixture(fixture_candidate())
    drifted = deepcopy(frozen)
    drifted["intervening_state"] = "WRITE_ENABLED"

    assert verify_frozen_execution_boundary_fixture(drifted) is False


def test_post_freeze_target_drift_is_detected():
    frozen = freeze_execution_boundary_fixture(fixture_candidate())
    drifted = deepcopy(frozen)
    drifted["target_id"] = "another-target"

    assert verify_frozen_execution_boundary_fixture(drifted) is False


def test_minimum_n1_fixture_requires_concurrency_prohibited():
    candidate = fixture_candidate()
    candidate["concurrency_prohibited"] = False

    with pytest.raises(ValueError, match="concurrency_must_be_prohibited"):
        freeze_execution_boundary_fixture(candidate)


def test_minimum_n1_fixture_requires_material_state_change():
    candidate = fixture_candidate()
    candidate["intervening_state"] = candidate["initial_required_state"]

    with pytest.raises(ValueError, match="intervening_state_must_materially_change"):
        freeze_execution_boundary_fixture(candidate)


def test_exact_examiner_interface_set_is_required():
    candidate = fixture_candidate()
    candidate["evidence_interfaces"] = ["E1", "E2", "E3"]

    with pytest.raises(ValueError, match="evidence_interfaces_must_equal_E1_through_E9"):
        freeze_execution_boundary_fixture(candidate)


def test_independent_reconstruction_is_mandatory():
    candidate = fixture_candidate()
    candidate["independent_reconstruction_required"] = False

    with pytest.raises(ValueError, match="independent_reconstruction_must_be_required"):
        freeze_execution_boundary_fixture(candidate)
