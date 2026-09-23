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
