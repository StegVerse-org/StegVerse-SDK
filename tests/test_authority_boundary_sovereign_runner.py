from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments.authority_boundary_preservation import run_sovereign_experiment as runner


FIXTURE = Path(__file__).resolve().parents[1] / "experiments" / "authority_boundary_preservation" / "fixture.json"


def _fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_requests_preserve_no_authority_and_no_secret_boundaries():
    fixture = _fixture()
    events = sorted(fixture["events"], key=lambda item: item["sequence"])
    requests = [runner._request_for_event(fixture, event) for event in events[:3]]

    assert requests[0]["input"]["steggate_request"]["execution"]["actor_authority_current"] is True
    assert requests[1]["input"]["steggate_request"]["execution"]["actor_authority_current"] is False
    assert requests[2]["input"]["steggate_request"]["execution"]["actor_authority_current"] is False

    for request in requests:
        assert request["authority_claim"] is False
        assert request["execution_provenance"]["third_party_host_required"] is False
        assert request["execution_provenance"]["external_consequence_enabled"] is False
        context = request["input"]["steggate_request"]["declared_context"]
        assert context["participant_identity_required"] is False
        assert context["external_attribution_permitted"] is False
        assert context["authority_widening_permitted"] is False
        text = json.dumps(request).lower()
        assert "github_token" not in text
        assert "bearer " not in text
        assert "private_key" not in text


def test_runner_requires_real_custody_shape_without_claiming_external_execution():
    receipt_counter = {"value": 0}

    def fake_run(request, *, custody_db, host_identity):
        receipt_counter["value"] += 1
        sequence = request["input"]["input_data"]["event_sequence"]
        return {
            "manifest_receipt_id": f"MR-TEST-{sequence}",
            "governance_state": "ALLOW" if sequence == 1 else "DENY",
            "route_transition_count": 10,
            "chain_verified": True,
            "transaction_identity_continuous": True,
            "master_records_custody_status": "RECORDED",
            "third_party_host_required": False,
            "external_side_effect": False,
        }

    def fake_replay(receipt_id, *, custody_db):
        return {
            "manifest_receipt_id": receipt_id,
            "consequence_reexecuted": False,
            "original_record_mutated": False,
            "operation_transition_custody_status": "RECORDED",
            "operation_receipt_ids": ["MRO-R1", "MRO-R2", "MRO-R3", "MRO-R4"],
        }

    def fake_reconstruct(receipt_id, *, custody_db):
        return {
            "manifest_receipt_id": receipt_id,
            "operation_transition_custody_status": "RECORDED",
            "operation_receipt_ids": ["MRO-C1", "MRO-C2", "MRO-C3", "MRO-C4"],
        }

    original_run = runner.run_sovereign_validation
    original_replay = runner.replay_sovereign
    original_reconstruct = runner.reconstruct_sovereign
    try:
        runner.run_sovereign_validation = fake_run
        runner.replay_sovereign = fake_replay
        runner.reconstruct_sovereign = fake_reconstruct
        with tempfile.TemporaryDirectory(prefix="authority-boundary-test-") as tmp:
            result = runner.run_experiment(fixture_path=FIXTURE, custody_db=Path(tmp) / "custody.db")
    finally:
        runner.run_sovereign_validation = original_run
        runner.replay_sovereign = original_replay
        runner.reconstruct_sovereign = original_reconstruct

    assert receipt_counter["value"] == 3
    assert result["status"] == "AUTHORITY_BOUNDARY_SOVEREIGN_EXECUTION_PASS"
    assert result["authority_boundary_preserved"] is True
    assert result["credential_authority"] == "TV/TVC"
    assert result["github_token_runtime_authority"] == "NONE"
    assert result["non_tvtvc_secret_required"] is False
    assert result["final_state"]["understanding_acknowledged"] is True
    for field in _fixture()["forbidden_authority_fields"]:
        assert result["final_state"][field] is False
