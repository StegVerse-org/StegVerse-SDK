import copy

import pytest

from stegverse.spe_steggate_bridge import (
    CANONICAL_STEGGATE_RUNTIME,
    build_steggate_request_candidate,
    stable_hash,
)

INTERLOCK_HASH = "sha256:" + "a" * 64


def _envelope(*, not_before=None, not_after=None):
    candidate_core = {
        "package_id": "pkg-bridge-001",
        "candidate_type": "COMMITMENT_CANDIDATE",
        "transition_id": "tx-bridge-001",
        "run_id": "run-bridge-001",
        "authorizing": False,
        "inherits_review_authority": False,
        "implies_standing": False,
        "requires_fresh_standing_determination": True,
        "bounded_scope": {"surface": "test"},
        "actor": "actor:test",
        "target": "target:test",
        "action": "govern:test",
        "review_ref": "review://bridge/001",
        "evidence_refs": ["evidence://bridge/001"],
        "policy_context": {"refs": ["policy://bridge/001"]},
        "delegation_context": {"refs": []},
        "validity_window": {"not_before": not_before, "not_after": not_after},
        "execution_context": {"mode": "evaluation_only"},
        "recoverability_profile": {"reconstructable": True},
        "source": {"repository_ref": "StegVerse-org/StegVerse-SDK"},
    }
    candidate = {**candidate_core, "candidate_hash": stable_hash(candidate_core)}
    envelope_core = {
        "schema_version": "stegverse.sdk.spe_commitment_intake.v0.1",
        "destination_repo": "StegVerse-Labs/Standing-Proof-Engine",
        "route_purpose": "FRESH_STANDING_DETERMINATION",
        "package_id": candidate["package_id"],
        "transition_id": candidate["transition_id"],
        "run_id": candidate["run_id"],
        "candidate_hash": candidate["candidate_hash"],
        "candidate": candidate,
        "authority": {
            "sdk_authorizing": False,
            "execution_authority_requested": False,
            "fresh_standing_determination_required": True,
        },
        "expected_result": ["ALLOW", "DENY", "FAIL_CLOSED"],
        "receipt_required": True,
    }
    return {**envelope_core, "envelope_hash": stable_hash(envelope_core)}


def _receipt(envelope, result="ALLOW"):
    receipt_core = {
        "schema_version": "stegverse.spe.sdk_commitment_intake.v0.1",
        "receipt_type": "SPE_STANDING_DETERMINATION",
        "source_repo": "StegVerse-org/StegVerse-SDK",
        "destination_repo": "StegVerse-Labs/Standing-Proof-Engine",
        "package_id": envelope["package_id"],
        "transition_id": envelope["transition_id"],
        "run_id": envelope["run_id"],
        "candidate_hash": envelope["candidate_hash"],
        "envelope_hash": envelope["envelope_hash"],
        "standing_result": result,
        "policy_refs": ["policy://bridge/001"],
        "delegation_refs": [],
        "evidence_refs": ["evidence://bridge/001"],
        "reasons": ["fixture"],
        "execution_authorized": False,
        "execution_performed": False,
        "master_record_installed": False,
        "next_boundary": "GOVERNED_EXECUTION_AUTHORITY" if result == "ALLOW" else None,
    }
    return {**receipt_core, "receipt_hash": stable_hash(receipt_core)}


def _interlock(envelope):
    return {
        "package_id": envelope["package_id"],
        "transition_id": envelope["transition_id"],
        "run_id": envelope["run_id"],
        "participant_id": "framework-a",
        "ingress_interlock_hash": INTERLOCK_HASH,
    }


def _three_layer_request():
    return {
        "judgment_conditions": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": ["evidence://bridge/001"],
        },
        "signal_admission": {
            "admitted_signal_refs": ["signal://bridge/001"],
            "excluded_signal_refs": [],
            "transformations": [],
            "missing_inputs": [],
            "uncertainty_state": "bounded",
            "reference_state_hash": "state-a",
            "expected_reference_state_hash": "state-a",
            "reconstruction_available": True,
            "transformation_provenance_complete": True,
        },
        "execution_boundary": {
            "actor_authority_current": True,
            "policy_current": True,
            "delegation_current": True,
            "evidence_current": True,
            "affected_entity_conditions_represented": True,
            "recoverability_profile": "recoverable",
            "validity_window_open": True,
            "policy_ref": "policy://bridge/001",
            "delegation_ref": "delegation://bridge/001",
            "evidence_refs": ["evidence://bridge/001"],
        },
        "action": "govern:test",
        "target": "target:test",
        "scope": "bounded:test",
    }


def _predicates():
    return {
        "authority_current": True,
        "consent_or_standing_required": True,
        "continuity_current": True,
        "governing_conditions_current": True,
        "consequence_attributable": True,
        "consequence_reconstructable": True,
    }


def _build(envelope=None, receipt=None, observed_at="2026-08-23T04:30:00+00:00"):
    envelope = envelope or _envelope()
    receipt = receipt or _receipt(envelope)
    return build_steggate_request_candidate(
        envelope,
        receipt,
        interlock_context=_interlock(envelope),
        observed_at=observed_at,
        three_layer_request=_three_layer_request(),
        permission_predicates=_predicates(),
    )


def test_allow_receipt_builds_non_authorizing_canonical_request():
    bridge = _build()
    assert bridge["standing_binding"]["standing_result"] == "ALLOW"
    assert bridge["standing_binding"]["standing_current"] is True
    assert bridge["admissibility_candidate"]["runtime_identity"] == CANONICAL_STEGGATE_RUNTIME
    assert bridge["admissibility_candidate"]["decision"] == "PENDING"
    assert bridge["authority"]["execution_authorized"] is False
    assert bridge["authority"]["sdk_authority"] == "NONE"


def test_deny_and_fail_closed_do_not_progress():
    for result in ("DENY", "FAIL_CLOSED"):
        envelope = _envelope()
        with pytest.raises(ValueError, match="does not allow progression"):
            _build(envelope, _receipt(envelope, result))


def test_receipt_hash_is_independently_verified():
    envelope = _envelope()
    receipt = _receipt(envelope)
    receipt["receipt_hash"] = "0" * 64
    with pytest.raises(ValueError, match="receipt_hash mismatch"):
        _build(envelope, receipt)


def test_candidate_and_envelope_hashes_are_independently_verified():
    envelope = _envelope()
    envelope["candidate"]["action"] = "mutated"
    with pytest.raises(ValueError, match="candidate_hash mismatch"):
        _build(envelope, _receipt(_envelope()))


def test_interlock_identity_mismatch_fails_closed():
    envelope = _envelope()
    interlock = _interlock(envelope)
    interlock["transition_id"] = "wrong"
    with pytest.raises(ValueError, match="interlock transition_id mismatch"):
        build_steggate_request_candidate(
            envelope,
            _receipt(envelope),
            interlock_context=interlock,
            observed_at="2026-08-23T04:30:00+00:00",
            three_layer_request=_three_layer_request(),
            permission_predicates=_predicates(),
        )


def test_stale_validity_window_cannot_progress():
    envelope = _envelope(not_after="2026-08-23T04:00:00+00:00")
    with pytest.raises(ValueError, match="not current"):
        _build(envelope, _receipt(envelope), observed_at="2026-08-23T04:30:00+00:00")


def test_future_validity_window_cannot_progress():
    envelope = _envelope(not_before="2026-08-23T05:00:00+00:00")
    with pytest.raises(ValueError, match="not current"):
        _build(envelope, _receipt(envelope), observed_at="2026-08-23T04:30:00+00:00")


def test_caller_cannot_supply_standing_current_predicate():
    envelope = _envelope()
    predicates = _predicates()
    predicates["consent_or_standing_current"] = True
    with pytest.raises(ValueError, match="derived from verified SPE standing"):
        build_steggate_request_candidate(
            envelope,
            _receipt(envelope),
            interlock_context=_interlock(envelope),
            observed_at="2026-08-23T04:30:00+00:00",
            three_layer_request=_three_layer_request(),
            permission_predicates=predicates,
        )


def test_spe_cannot_claim_execution_authority():
    envelope = _envelope()
    receipt = _receipt(envelope)
    receipt["execution_authorized"] = True
    core = dict(receipt)
    core.pop("receipt_hash")
    receipt["receipt_hash"] = stable_hash(core)
    with pytest.raises(ValueError, match="cannot authorize execution"):
        _build(envelope, receipt)


def test_three_layer_request_hash_and_bridge_hash_are_deterministic():
    left = _build()
    right = _build()
    assert left["admissibility_candidate"]["three_layer_request_hash"] == right["admissibility_candidate"]["three_layer_request_hash"]
    assert left["bridge_hash"] == right["bridge_hash"]
    altered = copy.deepcopy(right)
    altered["admissibility_candidate"]["three_layer_request"]["scope"] = "changed"
    assert stable_hash(altered) != stable_hash(left)
