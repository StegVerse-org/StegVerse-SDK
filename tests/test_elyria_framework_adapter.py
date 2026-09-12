import pytest

from stegverse.elyria_framework_adapter import (
    ElyriaFrameworkAdapter,
    ElyriaFrameworkAdapterError,
    build_elyria_assessment_request,
    normalize_elyria_assessment_response,
    normalize_elyria_no_bind_proof,
    normalize_elyria_replay_response,
)


def identity():
    return {
        "transition_id": "transition-elyria-1",
        "run_id": "run-elyria-1",
        "manifest_hash": "sha256:manifest-1",
    }


def movement():
    return {
        "movement_id": "MOVE-STEGVERSE-001",
        "source_node": "stegverse.interlock",
        "target_node": "elyria.public.assessment",
        "authority_present": True,
        "authority_scope_valid": True,
        "standing_active": True,
        "evidence_present": True,
        "evidence_sufficient": True,
        "custody_preserved": True,
        "refusal_condition_active": False,
        "revalidation_required": False,
        "receipt_available": True,
        "replay_available": True,
        "notes": "framework conformance fixture",
        "evidence_items": [],
    }


def receipt(verdict="ADMIT", **overrides):
    value = {
        "receipt_id": "RCT-ELYRIA-001",
        "movement_id": "MOVE-STEGVERSE-001",
        "verdict": verdict,
        "color": "green" if verdict == "ADMIT" else "red",
        "reasons": ["fixture"],
        "timestamp_utc": "2026-09-12T17:00:00+00:00",
        "input_hash": "0123456789abcdef",
        "engine_version": "0.3.0",
        "original_input": movement(),
        "evidence_summary": {"required": 0, "accepted": 0},
        "signature_algorithm": "HMAC-SHA256",
        "signature": "deadbeef",
    }
    value.update(overrides)
    return value


def replay():
    return {
        "receipt_id": "RCT-ELYRIA-001",
        "input_hash_matches": True,
        "verdict_matches": True,
        "signature_matches": True,
        "signature_algorithm": "HMAC-SHA256",
        "evidence_summary_matches": True,
        "actual": {
            "movement_id": "MOVE-STEGVERSE-001",
            "verdict": "ADMIT",
            "color": "green",
            "reasons": ["fixture"],
        },
    }


def no_bind():
    return {
        "proof_type": "elyria_no_bind_proof",
        "movement_attempted": movement(),
        "reason_admission_failed": ["standing inactive or expired"],
        "missing_or_invalid_standing_condition": "standing inactive or expired",
        "blocked_consequence_path": "protected_execution_route",
        "route_closure_state": "closed",
        "receipt_reference": "RCT-ELYRIA-001",
        "replay_reference": "replay:RCT-ELYRIA-001",
        "downstream_effect_status": "not_activated",
        "timestamp_utc": "2026-09-12T17:00:00+00:00",
    }


def test_request_reuses_external_adapter_shell_and_preserves_exact_http_body():
    source = movement()
    request = build_elyria_assessment_request(source, transition_identity=identity())
    assert request["elyria_http_body"] == source
    assert request["transition_identity"]["transition_id"] == "transition-elyria-1"
    assert request["authority"]["adapter_grants_authority"] is False
    assert request["authority"]["foreign_verdict_is_stegverse_admission"] is False


def test_request_does_not_synthesize_missing_elyria_evidence_fields():
    source = movement()
    source.pop("standing_active")
    with pytest.raises(ElyriaFrameworkAdapterError, match="standing_active"):
        build_elyria_assessment_request(source, transition_identity=identity())


def test_assessment_response_preserves_foreign_receipt_without_authority_promotion():
    result = normalize_elyria_assessment_response(
        receipt(), requested_movement=movement(), transition_identity=identity()
    )
    assert result["foreign_verdict"] == "ADMIT"
    assert result["foreign_receipt_id"] == "RCT-ELYRIA-001"
    assert result["foreign_receipt"]["signature"] == "deadbeef"
    assert result["stegverse_admission_determined"] is False
    assert result["authority_granted"] is False
    assert result["master_records_custody_recorded"] is False
    assert result["foreign_signature_verified_by_stegverse"] is False
    assert result["authentic_external_transport_observed"] is False


@pytest.mark.parametrize("verdict", ["ADMIT", "HOLD", "REFUSE", "NO_PROVABLE_ADMISSION"])
def test_all_public_elyria_verdicts_remain_foreign_observations(verdict):
    result = normalize_elyria_assessment_response(
        receipt(verdict), requested_movement=movement(), transition_identity=identity()
    )
    assert result["foreign_verdict"] == verdict
    assert result["foreign_framework_observation"] is True
    assert result["stegverse_admission_determined"] is False
    assert result["authority_granted"] is False


def test_assessment_response_fails_closed_on_movement_identity_mismatch():
    with pytest.raises(ElyriaFrameworkAdapterError, match="movement_id mismatch"):
        normalize_elyria_assessment_response(
            receipt(movement_id="MOVE-OTHER"),
            requested_movement=movement(),
            transition_identity=identity(),
        )


def test_assessment_response_fails_closed_when_framework_mutates_original_input():
    mutated = movement()
    mutated["standing_active"] = False
    with pytest.raises(ElyriaFrameworkAdapterError, match="original_input mismatch"):
        normalize_elyria_assessment_response(
            receipt(original_input=mutated),
            requested_movement=movement(),
            transition_identity=identity(),
        )


def test_assessment_response_fails_closed_on_unknown_verdict():
    with pytest.raises(ElyriaFrameworkAdapterError, match="unsupported Elyria verdict"):
        normalize_elyria_assessment_response(
            receipt("MAGIC"), requested_movement=movement(), transition_identity=identity()
        )


def test_replay_is_preserved_as_foreign_replay_evidence_only():
    result = normalize_elyria_replay_response(
        replay(), receipt_id="RCT-ELYRIA-001", transition_identity=identity()
    )
    assert result["foreign_replay_all_checks_pass"] is True
    assert result["foreign_replay"]["signature_matches"] is True
    assert result["stegverse_admission_determined"] is False
    assert result["authority_granted"] is False
    assert result["authentic_external_transport_observed"] is False


def test_replay_fails_closed_on_receipt_identity_mismatch():
    value = replay()
    value["receipt_id"] = "RCT-OTHER"
    with pytest.raises(ElyriaFrameworkAdapterError, match="receipt_id mismatch"):
        normalize_elyria_replay_response(
            value, receipt_id="RCT-ELYRIA-001", transition_identity=identity()
        )


def test_no_bind_route_closure_is_preserved_as_assertion_not_stegverse_observation():
    result = normalize_elyria_no_bind_proof(no_bind(), transition_identity=identity())
    assert result["foreign_route_closure_assertion"] == "closed"
    assert result["foreign_downstream_effect_assertion"] == "not_activated"
    assert result["route_closure_observed_by_stegverse"] is False
    assert result["downstream_effect_observed_by_stegverse"] is False
    assert result["authority_granted"] is False


def test_dependency_injected_adapter_sends_only_public_elyria_http_body():
    captured = {}

    def assess_transport(payload):
        captured.update(payload)
        return receipt()

    adapter = ElyriaFrameworkAdapter(assess_transport=assess_transport, replay_transport=lambda _: replay())
    assessment = adapter.assess(movement(), transition_identity=identity())
    replay_result = adapter.replay("RCT-ELYRIA-001", transition_identity=identity())

    assert captured == movement()
    assert assessment["foreign_verdict"] == "ADMIT"
    assert replay_result["foreign_replay_all_checks_pass"] is True


def test_missing_transition_identity_fails_closed_before_transport():
    called = False

    def assess_transport(payload):
        nonlocal called
        called = True
        return receipt()

    adapter = ElyriaFrameworkAdapter(assess_transport=assess_transport)
    with pytest.raises(ElyriaFrameworkAdapterError, match="run_id"):
        adapter.assess(movement(), transition_identity={"transition_id": "transition-elyria-1"})
    assert called is False
