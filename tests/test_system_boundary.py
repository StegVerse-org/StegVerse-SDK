from copy import deepcopy

from stegverse.system_boundary import validate_system_boundary_declaration


def sample_declaration():
    return {
        "schema_version": "0.1",
        "declaration_id": "sdk-system-boundary-001",
        "system_id": "stegverse-governed-llm-demo",
        "generated_at": "2026-07-14T12:00:00Z",
        "surfaces": {
            "model": {
                "present": True,
                "state_kind": "transient",
                "persistence": "invocation",
                "mutable_by_inference": False,
                "storage_refs": [],
            },
            "orchestration": {
                "present": True,
                "state_kind": "session",
                "persistence": "session",
                "mutable_by_inference": True,
                "storage_refs": ["orchestrator/session-state"],
            },
            "session": {
                "present": True,
                "state_kind": "session",
                "persistence": "session",
                "mutable_by_inference": True,
                "storage_refs": ["session/continuity-packet"],
            },
            "memory": {
                "present": True,
                "state_kind": "durable",
                "persistence": "cross-session",
                "mutable_by_inference": False,
                "storage_refs": ["memory/governed-record-store"],
            },
            "environment": {
                "present": True,
                "state_kind": "external",
                "persistence": "indefinite",
                "mutable_by_inference": False,
                "storage_refs": ["environment/tool-observation-receipts"],
            },
        },
        "continuity": {
            "prior_state_can_affect_future_transition": True,
            "feedback_paths": [
                "model-output->orchestrator-state",
                "orchestrator-state->future-model-input",
            ],
            "trajectory_dependent": True,
            "reconstructable": True,
            "evidence_refs": ["receipt://session/001"],
        },
        "authority": {
            "model_has_execution_authority": False,
            "commit_boundary": "governed-transition/commitment-request",
            "decision_source": "policy-engine",
            "policy_refs": ["policy://governed-llm/default"],
            "delegation_refs": [],
        },
        "claims_boundary": {
            "consciousness_claim": "not_evaluated",
            "personhood_claim": "not_evaluated",
            "welfare_claim": "not_evaluated",
            "scope_note": "Operational state and authority boundaries only.",
        },
    }


def test_accepts_non_authorizing_system_boundary_declaration():
    result = validate_system_boundary_declaration(sample_declaration())

    assert result.accepted is True
    assert result.status == "accepted_for_non_authorizing_sdk_ingestion"
    assert result.errors == []
    assert result.non_claims["sdk_validation_is_execution"] is False
    assert result.non_claims["state_continuity_proves_consciousness"] is False


def test_rejects_false_continuity_without_feedback_paths():
    declaration = sample_declaration()
    declaration["continuity"]["feedback_paths"] = []

    result = validate_system_boundary_declaration(declaration)

    assert result.accepted is False
    assert "continuity cannot claim prior-state influence without feedback_paths" in result.errors


def test_rejects_model_execution_authority():
    declaration = sample_declaration()
    declaration["authority"]["model_has_execution_authority"] = True

    result = validate_system_boundary_declaration(declaration)

    assert result.accepted is False
    assert "model execution authority must be false" in result.errors


def test_rejects_missing_commit_boundary():
    declaration = sample_declaration()
    declaration["authority"]["commit_boundary"] = ""

    result = validate_system_boundary_declaration(declaration)

    assert result.accepted is False
    assert "commit boundary is required" in result.errors


def test_rejects_consciousness_claim():
    declaration = sample_declaration()
    declaration["claims_boundary"]["consciousness_claim"] = "conscious"

    result = validate_system_boundary_declaration(declaration)

    assert result.accepted is False
    assert "consciousness_claim must remain not_evaluated" in result.errors


def test_rejects_extra_top_level_keys():
    declaration = deepcopy(sample_declaration())
    declaration["unexpected"] = True

    result = validate_system_boundary_declaration(declaration)

    assert result.accepted is False
    assert "system-boundary declaration keys do not match required contract" in result.errors
