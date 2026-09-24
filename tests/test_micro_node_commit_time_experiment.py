"""Source-level micro-node admissibility experiment; no runtime authority."""
from copy import deepcopy
import hashlib

import pytest

from stegverse.manifest_builder import build_manifest
from stegverse.micro_node_commit_time_experiment import (
    SCHEMA, _hash, evaluate_three_worker_experiment,
)
from stegverse.purpose_bound_worker_processor import (
    _group_result_commitment, derive_group_worker_requests,
)


def fixture():
    policy = {
        "mode": "DERIVED_COST_TASK_DELAY_BUDGET",
        "production_recompute_required": True,
        "decomposition_target": "RECORDS_ENABLED_PACKET",
        "retirement_condition": "PURPOSE_COMPLETED_OR_FAILED_OR_BUDGET_EXHAUSTED",
        "cost_analysis": {
            "expected_compute_units": 3, "external_cost_usd_ceiling": 0,
            "task_cost_basis": "bounded local semantic partition",
        },
        "time_budget_seconds": {
            "expected_task_execution": 6, "known_delay": 4,
            "inferred_unknown_delay_reserve": 8, "records_decomposition": 7,
            "safety_reserve": 5,
        },
        "derived_max_lifetime_seconds": 30,
        "unknown_delay_inference_basis": "test-only timing reserve",
    }
    manifest = build_manifest(
        data={"text": "Three separately attributable local semantic work units."},
        source_framework="SDK_TEST_ONLY", source_output_id="micro-node-001",
        process="purpose_bound_worker", created_at="2026-09-22T00:00:00Z",
        processor_request={
            "schema": "stegverse.sdk.purpose-bound-worker-group-test.v1",
            "test_id": "micro-node-commit-time-001",
            "purpose": "bounded test-only group",
            "required_capability": "text.integrity_summary",
            "worker_count": 3, "partition_ids": ["A", "B", "C"],
            "group_wall_clock_budget_seconds": 30,
            "per_worker_lifetime_policy": policy,
            "expected_evidence_fields": ["partition_reconstruction_exact"],
        },
    )
    requests = derive_group_worker_requests(manifest)
    bindings = []
    for i, req in enumerate(requests):
        bindings.append({
            "partition_id": ["A", "B", "C"][i],
            "partition_binding": req["transition_cell"]["candidate"]["partition_binding"],
            "worker_id": f"local-test-worker-{i}",
            "task_result_hash": hashlib.sha256(f"result-{i}".encode()).hexdigest(),
            "records_packet_hash": hashlib.sha256(f"packet-{i}".encode()).hexdigest(),
        })
    group = {
        "schema": "stegverse.sdk.purpose-bound-worker-group-manifest-result.v1",
        "test_id": "micro-node-commit-time-001",
        "worker_count": 3, "partition_ids": ["A", "B", "C"],
        "result_bindings": bindings,
        "group_result_binding_sha256": _group_result_commitment(
            "micro-node-commit-time-001", 3, bindings,
        ),
        "partition_reconstruction": {
            "exact": True,
            "source_sha256": hashlib.sha256(manifest["payload"]["text"].encode()).hexdigest(),
            "reconstructed_sha256": hashlib.sha256(manifest["payload"]["text"].encode()).hexdigest(),
        },
        "records_only": True, "worker_live_after_close": False,
    }
    rows = []
    for i, b in enumerate(bindings):
        hash_ = hashlib.sha256(f"receipt-{i}".encode()).hexdigest()
        prev = hashlib.sha256(f"predecessor-{i}".encode()).hexdigest()
        rows.append({
            "worker_id": b["worker_id"], "partition_id": b["partition_id"],
            "result_binding_sha256": _hash(b),
            "source_id": f"declared-origin-{i}",
            "custodian_id": f"declared-custodian-{i}",
            "independence_verified": True,  # caller claim, NOT independent verification
            "observation": "KNOWN", "mandatory_evidence_present": True,
            "custody": {
                "previous_receipt_sha256": prev,
                "reconstructed_predecessor_receipt_sha256": prev,
                "receipt_sha256": hash_, "reconstructed_receipt_sha256": hash_,
                "state": "RECORDED", "reconstruction_status": "PASS",
                "required_evidence_validation_status": "PASS",
            },
        })
    evidence = {
        "schema": SCHEMA, "manifest_sha256": _hash(manifest),
        "transition_id": "T-local-semantic-1", "workers": rows,
        "standing": {
            "transition_id": "T-local-semantic-1",
            "cta_disposition": "ALLOW", "current_at_commit": True,
            "tv_tvc_warrant_verified": True,
            "policy_sha256": hashlib.sha256(b"policy").hexdigest(),
            "current_state_sha256": hashlib.sha256(b"state").hexdigest(),
            "warrant_sha256": hashlib.sha256(b"warrant").hexdigest(),
        },
    }
    evidence["micro_node_request"] = {
        "transition_id": evidence["transition_id"],
        "origin_system": "SDK_TEST_ONLY", "return_path": "LOCAL_FIXTURE",
        "action": "EVALUATE_ONLY", "actor": "local-test-submitter",
        "target": "local-test-transition", "scope": "NO_AUTHORITY",
        "policy_ref": evidence["standing"]["policy_sha256"],
        "payload": {
            "sdk_manifest_sha256": evidence["manifest_sha256"],
            "sdk_group_result_binding_sha256": group["group_result_binding_sha256"],
            "partition_ids": ["A", "B", "C"],
        },
    }
    return manifest, group, evidence


def review(manifest=None, group=None, evidence=None):
    m, g, e = fixture()
    return evaluate_three_worker_experiment(
        m if manifest is None else manifest,
        g if group is None else group,
        e if evidence is None else evidence,
    )


def test_three_worker_manifest_and_local_evidence_never_authorize():
    m, g, e = fixture()
    outcome = evaluate_three_worker_experiment(m, g, e)
    assert outcome["worker_count"] == 3
    assert outcome["source_origin_count"] == 3
    assert outcome["authentic_independence_proven"] is False
    assert outcome["authentic_governed_runtime_proven"] is False
    assert outcome["reasons"] == ["AUTHENTIC_GOVERNED_RUNTIME_NOT_OBSERVED"]
    assert outcome["decision"] == "NON_AUTHORIZING_LOCAL_REVIEW_ONLY"


def test_unanimous_missing_mandatory_dependency_is_not_authorized():
    m, g, e = fixture()
    for row in e["workers"]:
        row["mandatory_evidence_present"] = False
    result = evaluate_three_worker_experiment(m, g, e)
    assert "WORKER_MISSING_MANDATORY_EVIDENCE" in result["reasons"]
    assert result["authentic_governed_runtime_proven"] is False


def test_preserves_dissent_and_unknowns():
    m, g, e = fixture()
    e["workers"][1]["observation"] = "DISSENT"
    e["workers"][2]["observation"] = "UNKNOWN"
    result = evaluate_three_worker_experiment(m, g, e)
    assert result["dissent_worker_ids"] == ["local-test-worker-1"]
    assert result["unknown_worker_ids"] == ["local-test-worker-2"]


def test_correlated_origins_are_not_independent():
    m, g, e = fixture()
    e["workers"][1]["source_id"] = e["workers"][0]["source_id"]
    e["workers"][1]["custodian_id"] = e["workers"][0]["custodian_id"]
    result = evaluate_three_worker_experiment(m, g, e)
    assert "CORRELATED_EVIDENCE_OR_CUSTODY_ORIGINS" in result["reasons"]


@pytest.mark.parametrize("disposition", ["DENY", "FAIL_CLOSED", "ESCALATE", "REFUSE"])
def test_cta_original_disposition_is_never_coerced(disposition):
    m, g, e = fixture()
    e["standing"]["cta_disposition"] = disposition
    result = evaluate_three_worker_experiment(m, g, e)
    assert result["cta_disposition_preserved"] == disposition
    assert "CTA_DISPOSITION_" + disposition in result["reasons"]


def test_stale_standing_is_not_commit_authority():
    m, g, e = fixture()
    e["standing"]["current_at_commit"] = False
    result = evaluate_three_worker_experiment(m, g, e)
    assert "COMMIT_TIME_STANDING_UNVERIFIED" in result["reasons"]


def test_forged_predecessor_is_rejected_locally():
    m, g, e = fixture()
    e["workers"][0]["custody"]["reconstructed_predecessor_receipt_sha256"] = "0" * 64
    result = evaluate_three_worker_experiment(m, g, e)
    assert "CANONICAL_PREDECESSOR_CUSTODY_UNVERIFIED" in result["reasons"]


def test_partition_omission_fails_closed():
    m, g, e = fixture()
    g["result_bindings"] = g["result_bindings"][:-1]
    with pytest.raises(ValueError, match="three result bindings"):
        evaluate_three_worker_experiment(m, g, e)


def test_tampered_worker_binding_fails_closed():
    m, g, e = fixture()
    g["result_bindings"][0]["task_result_hash"] = "a" * 64
    with pytest.raises(ValueError, match="group result commitment"):
        evaluate_three_worker_experiment(m, g, e)


def test_manifest_mutation_fails_exact_binding():
    m, g, e = fixture()
    e["manifest_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="manifest identity mismatch"):
        evaluate_three_worker_experiment(m, g, e)


def test_micro_node_request_exact_manifest_binding_required():
    m, g, e = fixture()
    e["micro_node_request"]["payload"]["sdk_group_result_binding_sha256"] = "a" * 64
    with pytest.raises(ValueError, match="micro-node request SDK manifest/group"):
        evaluate_three_worker_experiment(m, g, e)


def test_micro_node_request_requires_current_policy_identity():
    m, g, e = fixture()
    e["micro_node_request"]["policy_ref"] = "b" * 64
    with pytest.raises(ValueError, match="policy reference mismatch"):
        evaluate_three_worker_experiment(m, g, e)


# Stage-1 capability discovery: source-only fixtures, never external proof.
from stegverse.stage1_capability_discovery import (
    SCHEMA as STAGE1_SCHEMA, review_stage1_capabilities,
)


def stage1_fixture():
    m, g, e = fixture()
    participants = []
    for i, row in enumerate(e["workers"]):
        packet = hashlib.sha256(f"synthetic-observation-packet-{i}".encode()).hexdigest()
        participants.append({
            "worker_id": row["worker_id"],
            "result_binding_sha256": row["result_binding_sha256"],
            "source_id": row["source_id"], "custodian_id": row["custodian_id"],
            "observation": row["observation"],
            "observation_packet_sha256": packet,
            "observation_limits": ["synthetic test-only input; no external observation"],
            "capabilities": {
                key: {"status": "CLAIMED", "evidence_sha256": packet}
                for key in ("INGEST", "OBSERVE", "RECONSTRUCT")
            },
        })
    return m, g, e, {
        "schema": STAGE1_SCHEMA,
        "manifest_sha256": _hash(m),
        "group_result_binding_sha256": g["group_result_binding_sha256"],
        "participants": participants,
    }


def test_stage1_consistent_fixture_still_proves_no_external_capability():
    m, g, e, d = stage1_fixture()
    outcome = review_stage1_capabilities(m, g, e, d)
    assert outcome["fixture_status"] == "LOCAL_FIXTURE_CONSISTENT"
    assert outcome["capability_compatibility"]["OBSERVE"] == "LOCALLY_CLAIMED"
    assert outcome["independent_origin_proven"] is False
    assert outcome["external_participation_proven"] is False
    assert outcome["authentic_governance_proven"] is False
    assert outcome["master_records_custody_proven"] is False
    assert outcome["decision"] == "NON_AUTHORIZING_LOCAL_REVIEW_ONLY"


def test_stage1_shared_packet_does_not_prove_independence():
    m, g, e, d = stage1_fixture()
    first_packet = d["participants"][0]["observation_packet_sha256"]
    d["participants"][1]["observation_packet_sha256"] = first_packet
    for cap in d["participants"][1]["capabilities"].values():
        cap["evidence_sha256"] = first_packet
    outcome = review_stage1_capabilities(m, g, e, d)
    assert "SHARED_OBSERVATION_PACKET" in outcome["limitations"]
    assert outcome["independent_origin_proven"] is False


def test_stage1_common_custodian_surfaces_correlation():
    m, g, e, d = stage1_fixture()
    e["workers"][1]["custodian_id"] = e["workers"][0]["custodian_id"]
    d["participants"][1]["custodian_id"] = e["workers"][1]["custodian_id"]
    outcome = review_stage1_capabilities(m, g, e, d)
    assert "SHARED_CUSTODIAN" in outcome["limitations"]
    assert "EXISTING_EVIDENCE_CORRELATION" in outcome["limitations"]


@pytest.mark.parametrize("field", ["worker_id", "result_binding_sha256", "source_id",
                                      "custodian_id", "observation"])
def test_stage1_forged_or_stale_identity_rejected(field):
    m, g, e, d = stage1_fixture()
    d["participants"][0][field] = "tampered"
    with pytest.raises(ValueError, match="mismatch"):
        review_stage1_capabilities(m, g, e, d)


def test_stage1_manifest_binding_cannot_be_substituted():
    m, g, e, d = stage1_fixture()
    d["manifest_sha256"] = "b" * 64
    with pytest.raises(ValueError, match="manifest identity"):
        review_stage1_capabilities(m, g, e, d)


def test_stage1_unknown_and_dissent_retained_without_inferred_capability():
    m, g, e, d = stage1_fixture()
    e["workers"][1]["observation"] = d["participants"][1]["observation"] = "UNKNOWN"
    e["workers"][2]["observation"] = d["participants"][2]["observation"] = "DISSENT"
    d["participants"][1]["capabilities"]["OBSERVE"] = {
        "status": "UNKNOWN", "evidence_sha256": None,
    }
    outcome = review_stage1_capabilities(m, g, e, d)
    assert "UNKNOWN_RETAINED" in outcome["limitations"]
    assert "DISSENT_RETAINED" in outcome["limitations"]
    assert outcome["capability_compatibility"]["OBSERVE"] == "UNRESOLVED"
    assert outcome["participants"][2]["observation"] == "DISSENT"


def test_stage1_missing_limits_are_not_silently_accepted():
    m, g, e, d = stage1_fixture()
    d["participants"][2]["observation_limits"] = []
    with pytest.raises(ValueError, match="observation limits"):
        review_stage1_capabilities(m, g, e, d)


def test_stage1_unverified_capability_cannot_include_proof_digest():
    m, g, e, d = stage1_fixture()
    d["participants"][0]["capabilities"]["RECONSTRUCT"]["status"] = "UNKNOWN"
    with pytest.raises(ValueError, match="unproven capability"):
        review_stage1_capabilities(m, g, e, d)


def test_stage1_tampered_claim_packet_is_incomplete_not_authority():
    m, g, e, d = stage1_fixture()
    d["participants"][0]["capabilities"]["INGEST"]["evidence_sha256"] = "a" * 64
    outcome = review_stage1_capabilities(m, g, e, d)
    assert "CAPABILITY_PACKET_BINDING_MISMATCH" in outcome["limitations"]
    assert outcome["fixture_status"] == "LOCAL_FIXTURE_INCOMPLETE"
    assert outcome["authority_effect"] == "NONE"
