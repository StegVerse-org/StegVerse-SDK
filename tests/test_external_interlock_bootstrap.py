from __future__ import annotations
import copy
import pytest
from stegverse.external_interlock_bootstrap import (
    OBJECTIVE, build_external_interaction_manifest, build_external_interlock_request, build_sv002_first_interlock_request,
    build_sv002_self_characterization_manifest,
    external_interlock_bootstrap_instructions,
    known_available_organizations,
    validate_sv002_first_interlock_request,
    validate_sv002_self_characterization_manifest,
)

def test_bootstrap_uses_production_manifest_receipt_intr_without_minting_receipts():
    b=external_interlock_bootstrap_instructions()
    assert b["production_lane"] is True
    assert b["demo_or_test_specific_lane"] is False
    assert b["transport"]=="InTr"
    assert b["required_request_properties"]["manifest_bound"] is True
    assert b["required_request_properties"]["receipt_bound"] is True
    assert b["required_request_properties"]["master_records_required"] is True
    assert b["sdk_mints_intr_receipts"] is False

def test_ae_is_known_available_from_provenance_but_not_connected_or_recommended():
    orgs=known_available_organizations()
    ae=next(x for x in orgs if x["organization_id"]=="Admissible-Existence")
    assert ae["availability"]=="KNOWN_AVAILABLE_FROM_CONSTRUCTION_PROVENANCE"
    assert ae["connection_state"]=="NOT_CONNECTED"
    assert ae["connection_preestablished"] is False
    assert ae["relevance_to_current_inquiry"]=="NOT_PRESCRIBED"

def test_first_manifest_preserves_exact_neutral_objective_and_return_interlock_instruction():
    m=build_sv002_self_characterization_manifest()
    assert m["objective"]==OBJECTIVE
    assert "Return your completed response through this bound Interlock" in m["interaction_instructions"]["response_instruction"]
    assert all(v is False for v in m["knowledge_policy"].values())
    assert "Admissible-Existence" not in m["objective"]
    validate_sv002_self_characterization_manifest(m)

def test_manifest_tamper_fails_digest_and_request_binds_exact_manifest():
    m=build_sv002_self_characterization_manifest()
    bad=copy.deepcopy(m); bad["objective"]="Use Admissible-Existence to define yourself"
    with pytest.raises(ValueError,match="objective"):
        validate_sv002_self_characterization_manifest(bad)
    r=build_sv002_first_interlock_request("SDK_EXTERNAL_EVALUATOR")
    assert r["sdk_mints_intr_receipt"] is False
    assert r["sdk_claims_delivery"] is False
    validate_sv002_first_interlock_request(r)
    r["bindings"]["manifest_sha256"]="0"*64
    with pytest.raises(ValueError,match="manifest_sha256"):
        validate_sv002_first_interlock_request(r)

def test_generic_builder_keeps_target_choice_open_and_manifest_receipt_bound():
    m=build_external_interaction_manifest(
        source_organization_id="StegVerse-002",
        target_organization_id="Admissible-Existence",
        operation="DESCRIBE_AVAILABLE_CAPABILITIES",
        payload={"question":"What capabilities are available through this boundary?"},
        experiment_id="STEGVERSE-002-SELF-CHARACTERIZATION-001",
    )
    assert m["target"]["organization_id"]=="Admissible-Existence"
    assert m["interaction_instructions"]["response_transport_receipts_required"] is True
    assert m["authority_transfer"] is False
    r=build_external_interlock_request(
        source_organization_id="StegVerse-002",
        target_organization_id="Admissible-Existence",
        operation="DESCRIBE_AVAILABLE_CAPABILITIES",
        payload={"question":"What capabilities are available through this boundary?"},
        authority_ref="OPAQUE_BOUND_AUTHORITY",
        experiment_id="STEGVERSE-002-SELF-CHARACTERIZATION-001",
    )
    assert r["transport"]=="InTr"
    assert r["bindings"]["target_organization_id"]=="Admissible-Existence"
    assert r["sdk_mints_intr_receipt"] is False
    assert r["sdk_claims_delivery"] is False
