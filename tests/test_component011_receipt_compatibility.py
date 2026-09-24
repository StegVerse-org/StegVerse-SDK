"""Only source snapshots; never run a probe or claim authentic custody."""
import hashlib
import json
from copy import deepcopy

from stegverse.component011_receipt_compatibility import (
    SCHEMA, reconcile_component011_snapshots,
)


def sha(obj):
    return "sha256:" + hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def sample():
    claim = {"claim_id": "synthetic-G1", "fencing_token": 1}
    denial = [
        {"probe_id": probe, "decision": "DENY", "consumed": False,
         "consequence_reachable": False}
        for probe in ("FILESYSTEM_OPEN", "NETWORK_IMPORT", "ENVIRONMENT_IMPORT")
    ]
    boundary = {
        "schema": "stegverse.ungoverned-ai-defensive-envelope-resident-boundary/v1",
        "task_id": "ECOSYSTEM-INGRESS-AI-BOUNDARIES-001",
        "component_id": "RTC-NONCHATGPT-AI-DECISION-SANDBOX-011",
        "state": "REPRESENTATIVE_BOUNDARY_PROBE_OBSERVED",
        "claim": claim, "tvc_source_head": "synthetic-test-only",
        "external_provider_observed": False,
        "probe": {"denied_interactions": denial},
        "checks": {key: True for key in (
            "allow_consumed", "allow_result", "filesystem_not_exposed",
            "network_not_exposed", "temporary_state_destroyed",
            "deny_not_consumed", "deny_consequence_unreachable",
            "ambient_credentials_not_exposed", "egress_evidence_only",
        )},
    }
    consumption = {
        "schema": "stegverse.ungoverned-ai-defensive-envelope-request-consumption/v1",
        "task_id": boundary["task_id"],
        "terminal": True, "bridge_contract_valid": True,
        "runtime_execution_attempted": True,
    }
    transition = {
        "schema": "stegverse.canonical-state-transition-receipt/v1",
        "subject_or_correlation_id": boundary["task_id"],
        "transition_id": "synthetic-transition",
        "transition_evidence": {"component011_boundary_receipt_sha256": sha(boundary)},
    }
    organization = {
        "schema": "stegverse.organization-transition-receipt/v1",
        "organization": "StegVerse-Labs",
        "source_receipt_schema": transition["schema"],
        "source_transition_sha256": sha(transition),
        "canonical_state_transition_receipt_sha256": sha(transition),
        "receipt_sha256": "sha256:synthetic-organization-only",
    }
    master_records = {
        "state": "RECORDED", "reconstruction_status": "PASS",
        "required_evidence_validation_status": "PASS",
        "receipt_sha256": "synthetic-equal", "reconstructed_receipt_sha256": "synthetic-equal",
        "organization_receipt_sha256": organization["receipt_sha256"],
    }
    return consumption, boundary, transition, organization, master_records


def inspect(*items):
    return reconcile_component011_snapshots(
        consumption=items[0], boundary=items[1], canonical_transition=items[2],
        organization=items[3], master_records=items[4],
    )


def test_no_receipts_retains_all_missing_predicates():
    r = reconcile_component011_snapshots()
    assert r["schema"] == SCHEMA
    assert "AUTHENTIC_REQUEST_CONSUMPTION_RECEIPT_MISSING" in r["missing_or_unproven"]
    assert "AUTHENTIC_ORGANIZATION_LEDGER_RECEIPT_MISSING" in r["missing_or_unproven"]
    assert "CANONICAL_MASTER_RECORDS_READBACK_MISSING" in r["missing_or_unproven"]
    assert not r["authentic_runtime_proven"]


def test_all_synthetic_claims_can_never_promote_authority():
    r = inspect(*sample())
    assert all(r["structural_checks"].values())
    assert "CONSUMPTION_TO_BOUNDARY_RECEIPT_EXACT_BINDING_NOT_PROVEN" in r["missing_or_unproven"]
    assert r["decision"] == "NON_AUTHORIZING_SOURCE_RECONCILIATION_ONLY"
    assert not r["organization_custody_proven"]
    assert not r["master_records_reconstructed"]
    assert "PACKAGE_INSTALL_HOOK_OS_CONTAINMENT" in r["not_proven_effects"]


def test_denial_claim_must_have_consumed_false_and_unreachable_effect():
    x = list(sample())
    x[1]["probe"]["denied_interactions"][0]["consumed"] = True
    assert "BOUNDARY_DENIAL_OR_CLAIM_NOT_STRUCTURALLY_PROVEN" in inspect(*x)["missing_or_unproven"]


def test_worker_claim_fence_and_tvc_head_required():
    x = list(sample())
    x[1]["claim"]["fencing_token"] = 0
    x[1]["tvc_source_head"] = ""
    assert not inspect(*x)["structural_checks"]["boundary_shape"]


def test_mismatched_source_and_org_linkage_detected():
    x = list(sample())
    x[2]["transition_evidence"]["component011_boundary_receipt_sha256"] = "wrong"
    x[3]["source_transition_sha256"] = "wrong"
    reasons = inspect(*x)["missing_or_unproven"]
    assert "BOUNDARY_TO_CANONICAL_TRANSITION_EXACT_LINK_MISSING" in reasons
    assert "ORGANIZATION_SOURCE_TRANSITION_EXACT_LINK_MISSING" in reasons


def test_master_records_claims_must_match_org_receipt_and_exact_digest():
    x = list(sample())
    x[4]["reconstructed_receipt_sha256"] = "mismatch"
    x[4]["organization_receipt_sha256"] = "wrong"
    assert "MASTER_RECORDS_CLOSURE_OR_ORG_BINDING_MISSING" in inspect(*x)["missing_or_unproven"]


def test_incorrect_consumption_does_not_become_runtime_execution():
    x = list(sample())
    x[0]["terminal"] = False
    assert "REQUEST_CONSUMPTION_NOT_TERMINALLY_BOUND" in inspect(*x)["missing_or_unproven"]


def test_snapshot_type_rejected():
    import pytest
    with pytest.raises(ValueError):
        reconcile_component011_snapshots(boundary="untrusted")
