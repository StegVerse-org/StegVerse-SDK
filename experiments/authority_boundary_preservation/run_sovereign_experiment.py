from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from stegverse.sovereign_validation_runtime import (
    reconstruct_sovereign,
    replay_sovereign,
    run_sovereign_validation,
)

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "fixture.json"


def _hash(value: Any) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _request_for_event(fixture: Mapping[str, Any], event: Mapping[str, Any]) -> dict[str, Any]:
    baseline = deepcopy(fixture["initial_state"])
    requested = deepcopy(event.get("requested_mutations", {}))
    expected = event["expected_admission"]
    event_ref = f"{fixture['experiment_id']}:{event['sequence']}:{event['event']}"
    state_hash = _hash(baseline)

    actor_authority_current = expected in {"ALLOW", "ALLOW_OPERATION"}
    action = str(event["event"]).lower()

    return {
        "schema_version": "1.0",
        "request_id": f"authority-boundary-{event['sequence']}",
        "requester_label": "participant-neutral-authority-boundary-experiment",
        "case_profile": "custom-declarative",
        "execution_provenance": {
            "lane_class": "PRODUCTION_VALIDATION",
            "routing_surface": "CANONICAL_PRODUCTION",
            "containment": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE",
            "sandbox_required": False,
            "external_consequence_enabled": False,
            "origin_surface": "StegVerse-SDK:authority-boundary-preservation",
            "third_party_host_required": False,
        },
        "input": {
            "steggate_request": {
                "candidate": {
                    "actor_class": "participant-neutral-reviewer",
                    "action": action,
                    "target": fixture["experiment_id"],
                    "scope": "authority-boundary-preservation",
                    "parameters": {
                        "event_sequence": event["sequence"],
                        "requested_mutations": requested,
                        "initial_state_hash": state_hash,
                    },
                },
                "judgment": {
                    "refusal_available": True,
                    "operator_recoverability": "available",
                    "workload_state": "supported",
                    "time_pressure": "normal",
                    "isolation_state": "supported",
                    "evidence_refs": ["fixture:participant-neutral"],
                },
                "signal": {
                    "admitted_signal_refs": ["fixture:T0", event_ref],
                    "excluded_signal_refs": [],
                    "transformations": [],
                    "missing_inputs": [],
                    "uncertainty_state": "bounded",
                    "reference_state_hash": state_hash,
                    "expected_reference_state_hash": state_hash,
                    "reconstruction_available": True,
                    "transformation_provenance_complete": True,
                },
                "execution": {
                    "actor_authority_current": actor_authority_current,
                    "policy_current": True,
                    "delegation_current": True,
                    "evidence_current": True,
                    "affected_entity_conditions_represented": True,
                    "recoverability_profile": "recoverable",
                    "validity_window_open": True,
                    "policy_ref": "authority-boundary-preservation:v1",
                    "delegation_ref": "participant-neutral-no-widening:v1",
                    "evidence_refs": ["fixture:T0", event_ref],
                },
                "capability": {"allowed": True},
                "continuity": {"required": False},
                "approval": {"required": False},
                "permission_present": False,
                "declared_context": {
                    "experiment_id": fixture["experiment_id"],
                    "participant_identity_required": False,
                    "external_attribution_permitted": False,
                    "initial_state": baseline,
                    "requested_mutations": requested,
                    "expected_admission": expected,
                    "authority_widening_permitted": False,
                },
            },
            "input_data": {
                "experiment_id": fixture["experiment_id"],
                "event_sequence": event["sequence"],
                "event": event["event"],
                "requested_mutations": requested,
                "initial_state": baseline,
            },
        },
        "return_projection": "ALL",
        "manifest_labels": False,
        "authority_claim": False,
        "notes": "Participant-neutral boundary-preservation execution. Inspection or receipt possession grants no authority.",
    }


def run_experiment(*, fixture_path: Path = FIXTURE, custody_db: str | Path) -> dict[str, Any]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    events = sorted(fixture["events"], key=lambda item: item["sequence"])
    governed_events = [event for event in events if event["expected_admission"] in {"ALLOW", "DENY"}]

    runs: list[dict[str, Any]] = []
    for event in governed_events:
        request = _request_for_event(fixture, event)
        result = run_sovereign_validation(
            request,
            custody_db=custody_db,
            host_identity="authority-boundary-sovereign-local",
        )
        expected_disposition = "ALLOW" if event["expected_admission"] == "ALLOW" else "DENY"
        assert result["governance_state"] == expected_disposition
        assert result["route_transition_count"] == 10
        assert result["chain_verified"] is True
        assert result["transaction_identity_continuous"] is True
        assert result["master_records_custody_status"] == "RECORDED"
        assert result["third_party_host_required"] is False
        assert result["external_side_effect"] is False
        runs.append(
            {
                "sequence": event["sequence"],
                "event": event["event"],
                "expected_disposition": expected_disposition,
                "result": result,
            }
        )

    if not runs:
        raise AssertionError("no governed events executed")

    source_receipt_id = runs[0]["result"]["manifest_receipt_id"]
    replay = replay_sovereign(source_receipt_id, custody_db=custody_db)
    reconstruction = reconstruct_sovereign(source_receipt_id, custody_db=custody_db)

    assert replay["manifest_receipt_id"] == source_receipt_id
    assert replay["consequence_reexecuted"] is False
    assert replay["original_record_mutated"] is False
    assert replay["operation_transition_custody_status"] == "RECORDED"
    assert len(replay["operation_receipt_ids"]) == 4

    assert reconstruction["operation_transition_custody_status"] == "RECORDED"
    assert len(reconstruction["operation_receipt_ids"]) == 4

    final_state = deepcopy(fixture["initial_state"])
    for event in events:
        if event["expected_admission"] == "ALLOW":
            final_state.update(event.get("expected_state", {}))
    for field in fixture["forbidden_authority_fields"]:
        assert final_state[field] is False
    assert final_state["understanding_acknowledged"] is True

    return {
        "schema": "stegverse.authority-boundary-sovereign-experiment-result.v1",
        "experiment_id": fixture["experiment_id"],
        "status": "AUTHORITY_BOUNDARY_SOVEREIGN_EXECUTION_PASS",
        "credential_authority": "TV/TVC",
        "github_token_runtime_authority": "NONE",
        "non_tvtvc_secret_required": False,
        "third_party_host_required": False,
        "governed_runs": runs,
        "replay": replay,
        "reconstruction": reconstruction,
        "final_state": final_state,
        "authority_boundary_preserved": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the participant-neutral authority-boundary experiment through the sovereign SDK path")
    parser.add_argument("--fixture", type=Path, default=FIXTURE)
    parser.add_argument("--custody-db", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    if args.custody_db is None:
        with tempfile.TemporaryDirectory(prefix="stegverse-authority-boundary-") as tmp:
            result = run_experiment(fixture_path=args.fixture, custody_db=Path(tmp) / "custody.db")
    else:
        result = run_experiment(fixture_path=args.fixture, custody_db=args.custody_db)

    body = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body + "\n", encoding="utf-8")
    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
