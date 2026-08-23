import copy

import pytest

from stegverse.interlock_transition import canonical_hash as interlock_hash
from stegverse.portable_governance_verifier import verify_portable_governance_bundle
from stegverse.spe_commitment_intake import build_spe_commitment_candidate, build_spe_intake_envelope
from stegverse.spe_steggate_bridge import build_steggate_request_candidate, stable_hash
from stegverse.transition_candidate import emit_sdk_transition_candidate

H1 = "sha256:" + "1" * 64
H2 = "sha256:" + "2" * 64
H3 = "sha256:" + "3" * 64
H4 = "sha256:" + "4" * 64
H5 = "sha256:" + "5" * 64
H6 = "sha256:" + "6" * 64


def _ingress(package_id, transition_id, run_id):
    return {
        "schema": "stegverse.interlock-transition.v1",
        "package_id": package_id,
        "transition_id": transition_id,
        "run_id": run_id,
        "connection": {
            "class": "INTERLOCK",
            "direction": "INGRESS",
            "participant_id": "reference-participant",
            "participant_boundary_receipt_hash": H1,
            "participant_binding_hash": H2,
        },
        "manifest": {
            "manifest_hash": H3,
            "source_state_hash": H4,
            "canonicalization": "JCS_RFC8785_NFC",
            "predecessor_receipts": [{"receipt_id": "p:r1", "issuer": "reference-participant", "receipt_hash": H1}],
        },
        "governance": {
            "mode": "DEFAULT_STEGVERSE",
            "profiles": [{"profile_id": "stegverse.default.reference.v1", "issuer": "StegVerse", "profile_hash": H5, "source": "STEGVERSE"}],
        },
        "manifold": {
            "predecessors": [{"state_id": "p:s1", "state_hash": H4}],
            "successors": [{"state_id": "sv:s2", "state_hash": H6}],
            "relationships": [{"from_state_id": "p:s1", "to_state_id": "sv:s2", "type": "CAUSE"}],
        },
        "boundary": {"state": "ACCEPT", "original_manifest_hash": H3, "repaired_manifest_hash": None},
        "authority": {
            "sdk_authority": "NONE",
            "participant_truth_assumed": False,
            "interlock_transfers_authority": False,
            "master_records_custody_claimed": False,
            "execution_authorized": False,
        },
        "reconstruction": {"required": True, "replay_scope": "MATERIAL_CAUSAL_CLOSURE", "linear_chain_is_special_case": True},
    }


def _bundle():
    transition_id = "portable.verify.001"
    run_id = "run-portable-001"
    package_id = transition_id
    transition = emit_sdk_transition_candidate(
        transition_id=transition_id,
        run_id=run_id,
        event_id="event-portable-001",
        actor_ref="actor:reference",
        target_ref="target:reference",
        repository_ref="StegVerse-org/StegVerse-SDK",
        task_ref="task:portable-verifier",
        handoff_ref="PORTABLE_GOVERNANCE_VERIFIER_MIRROR_HANDOFF.md",
        policy_refs=["policy://reference/v1"],
        evidence_refs=["evidence://reference/001"],
    )
    candidate = build_spe_commitment_candidate(
        transition,
        action="reference_action",
        bounded_scope={"surface": "reference"},
        review_ref="review://reference/001",
        policy_context={"refs": ["policy://reference/v1"]},
        delegation_context={"refs": []},
        validity_window={"not_before": "2026-08-23T00:00:00+00:00", "not_after": "2026-08-24T00:00:00+00:00"},
        execution_context={"mode": "evaluation_only"},
        recoverability_profile={"reconstructable": True, "rollback_supported": False},
    )
    envelope = build_spe_intake_envelope(candidate)
    receipt_core = {
        "schema_version": "stegverse.spe.sdk_commitment_intake.v0.1",
        "receipt_type": "SPE_STANDING_DETERMINATION",
        "source_repo": "StegVerse-org/StegVerse-SDK",
        "destination_repo": "StegVerse-Labs/Standing-Proof-Engine",
        "package_id": package_id,
        "transition_id": transition_id,
        "run_id": run_id,
        "candidate_hash": envelope["candidate_hash"],
        "envelope_hash": envelope["envelope_hash"],
        "standing_result": "ALLOW",
        "policy_refs": ["policy://reference/v1"],
        "delegation_refs": [],
        "evidence_refs": ["evidence://reference/001"],
        "reasons": ["reference standing satisfied"],
        "execution_authorized": False,
        "execution_performed": False,
        "master_record_installed": False,
        "next_boundary": "GOVERNED_EXECUTION_AUTHORITY",
    }
    receipt = {**receipt_core, "receipt_hash": stable_hash(receipt_core)}
    ingress = _ingress(package_id, transition_id, run_id)
    request = {
        "judgment_conditions": {"refusal_available": True, "operator_recoverability": "available"},
        "signal_admission": {
            "admitted_signal_refs": ["evidence://reference/001"],
            "missing_inputs": [],
            "uncertainty_state": "bounded",
            "reference_state_hash": H4,
            "expected_reference_state_hash": H4,
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
            "policy_ref": "policy://reference/v1",
            "delegation_ref": "delegation://none",
        },
        "action": "reference_action",
        "target": "target:reference",
        "scope": "reference",
    }
    bridge = build_steggate_request_candidate(
        envelope,
        receipt,
        interlock_context={
            "package_id": package_id,
            "transition_id": transition_id,
            "run_id": run_id,
            "ingress_interlock_hash": interlock_hash(ingress),
            "participant_id": "reference-participant",
        },
        observed_at="2026-08-23T12:00:00+00:00",
        three_layer_request=request,
        permission_predicates={
            "authority_current": True,
            "continuity_current": True,
            "governing_conditions_current": True,
            "consequence_attributable": True,
            "consequence_reconstructable": True,
            "consent_or_standing_required": True,
        },
    )
    return {
        "schema": "stegverse.portable-governance-verification-bundle.v1",
        "stage": "PRE_STEGGATE",
        "package_id": package_id,
        "transition_id": transition_id,
        "run_id": run_id,
        "ingress_interlock": ingress,
        "spe_envelope": envelope,
        "spe_receipt": receipt,
        "steggate_bridge": bridge,
        "interlock_return": None,
    }


def test_pre_steggate_bundle_verifies_independently():
    report = verify_portable_governance_bundle(_bundle())
    assert report["status"] == "PASS"
    assert report["stage"] == "PRE_STEGGATE"
    assert report["authority"]["verification_authority"] == "NONE"
    assert "STEGGATE_BRIDGE_HASH_VALID" in report["checks"]


def test_tampered_ingress_breaks_bridge_binding():
    bundle = _bundle()
    bundle["ingress_interlock"]["manifold"]["successors"][0]["state_hash"] = H5
    with pytest.raises(ValueError, match="ingress interlock hash mismatch"):
        verify_portable_governance_bundle(bundle)


def test_tampered_spe_receipt_fails_hash_verification():
    bundle = _bundle()
    bundle["spe_receipt"]["reasons"] = ["mutated after receipt"]
    with pytest.raises(ValueError, match="receipt_hash mismatch"):
        verify_portable_governance_bundle(bundle)


def test_identity_discontinuity_fails():
    bundle = _bundle()
    bundle["steggate_bridge"]["transition_id"] = "other"
    bridge_core = dict(bundle["steggate_bridge"])
    bridge_core.pop("bridge_hash")
    bundle["steggate_bridge"]["bridge_hash"] = stable_hash(bridge_core)
    with pytest.raises(ValueError, match="StegGate bridge transition_id mismatch"):
        verify_portable_governance_bundle(bundle)


def test_pre_steggate_cannot_claim_return():
    bundle = _bundle()
    bundle["interlock_return"] = {}
    with pytest.raises(ValueError, match="cannot claim interlock return"):
        verify_portable_governance_bundle(bundle)


def test_verifier_does_not_accept_execution_authority():
    bundle = _bundle()
    bundle["steggate_bridge"]["authority"]["execution_authorized"] = True
    bridge_core = dict(bundle["steggate_bridge"])
    bridge_core.pop("bridge_hash")
    bundle["steggate_bridge"]["bridge_hash"] = stable_hash(bridge_core)
    with pytest.raises(ValueError, match="cannot authorize execution"):
        verify_portable_governance_bundle(bundle)
