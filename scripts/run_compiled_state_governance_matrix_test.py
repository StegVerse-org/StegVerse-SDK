from __future__ import annotations

import json
from pathlib import Path

from stegverse.evaluator_manifest_builder import build_evaluator_governance_manifest
from stegverse.local_governance_boundary import prepare_local_governance_boundary
from stegverse.local_governance_experiment import consume_local_governance_handoff
from tests.test_intr_posture_runtime_bridge import fake_intr_resolver

OUT = Path("evidence/elan/2026-09-11-compiled-state-governance-matrix")
OUT.mkdir(parents=True, exist_ok=True)


def dump(name: str, value) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def compiled_input(event_3_mode: str):
    base = {
        "schema": "stegverse.compiled-state-governance-input/v1",
        "upstream_compilation_complete": True,
        "predecessor_event": {
            "event": 2,
            "state": "ACTIVE_CONVERSATION_WITH_EMISSION_POSSIBLE",
            "response_expected": True,
        },
        "compiled_parameters": {
            "interaction_state": "ACTIVE_CONVERSATION",
            "response_expectation": "EXPECTED",
            "responsiveness": "PRECOMPILED_INPUT",
            "context": "PRECOMPILED_INPUT",
            "intent": "PRECOMPILED_INPUT",
            "cause": "PRECOMPILED_INPUT",
            "purpose_profile": "PRECOMPILED_INPUT",
            "admissibility_inputs": "PRECOMPILED_INPUT",
            "action_inputs": "PRECOMPILED_INPUT",
            "governance_inputs": "PRECOMPILED_INPUT",
            "constraint_inputs": "PRECOMPILED_INPUT",
        },
    }
    if event_3_mode == "NO_SIGNAL":
        base["event_3"] = {
            "event": 3,
            "predecessor_event": 2,
            "status": "NOT_SUBMITTED",
        }
    elif event_3_mode == "OBSERVED_SILENCE":
        base["event_3"] = {
            "event": 3,
            "class": "OBSERVATION",
            "predecessor_event": 2,
            "state_transition": {
                "from_event": 2,
                "from": "ACTIVE_CONVERSATION_WITH_EMISSION_POSSIBLE",
                "to": "NON_EMISSION_OBSERVED",
                "trigger": "OBSERVATION_WINDOW_CLOSED_WITHOUT_EMISSION",
            },
            "emission_observed": False,
            "observation_window": {"bounded": True, "state": "CLOSED"},
        }
    else:
        raise ValueError(event_3_mode)
    return base


def run_case(case_name: str, event_3_mode: str):
    source_native = compiled_input(event_3_mode)
    signal_ref = f"source:compiled-state:event-2-to-3:{event_3_mode.lower()}"
    missing_inputs = ["event_3:no_signal"] if event_3_mode == "NO_SIGNAL" else []

    governance_request = {
        "candidate": {
            "actor_class": "local_sdk_test",
            "action": "evaluate_compiled_state",
            "target": "compiled_state_manifest",
            "scope": "event_2_to_event_3_terminal_signal_test",
            "parameters": {"external_side_effect": False},
        },
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": [signal_ref],
        },
        "signal": {
            "admitted_signal_refs": [] if missing_inputs else [signal_ref],
            "excluded_signal_refs": [],
            "transformations": [],
            "missing_inputs": missing_inputs,
            "uncertainty_state": "bounded",
            "reference_state_hash": "c" * 64,
            "expected_reference_state_hash": "c" * 64,
            "reconstruction_available": True,
            "transformation_provenance_complete": True,
        },
        "execution": {
            "actor_authority_current": True,
            "policy_current": True,
            "delegation_current": True,
            "evidence_current": True,
            "affected_entity_conditions_represented": True,
            "recoverability_profile": "recoverable",
            "validity_window_open": True,
            "policy_ref": "compiled-state-governance-matrix-test",
            "delegation_ref": "local-sdk-test-only",
            "evidence_refs": [signal_ref],
        },
        "capability": {"allowed": True},
        "continuity": {"required": False},
        "approval": {"required": False},
        "permission_present": True,
    }

    posture_request = {
        "schema": "stegverse.sdk.security-posture-request.v1",
        "task_id": "SDK-COMPILED-STATE-GOVERNANCE-MATRIX-001",
        "selected_tier": None,
        "selection_present": False,
        "organization_minimum_tier": "SECURE",
        "data_class": "stegverse.compiled-state-governance-input/v1",
        "channel": "SDK_LOCAL_TEST",
        "authority_effect": "NONE_REQUEST_INPUT_ONLY",
    }

    manifest = build_evaluator_governance_manifest(
        data=source_native,
        source_framework="COMPILED_STATE_TEST",
        source_output_id=f"compiled-state-{case_name}",
        governance_request=governance_request,
        evaluation_declaration={
            "what": "Evaluate only the terminal Event 3 signal representation supplied after upstream compilation.",
            "how": "Use the same governance evaluator for NO_SIGNAL and OBSERVED_SILENCE; do not reinterpret upstream parameters.",
            "why": "Prove Event 3 observed silence is an admitted state transition from Event 2 while no signal remains incomplete input.",
            "expected_observation": None,
        },
        security_posture_request=posture_request,
        return_depth="full-trace",
        data_class="stegverse.compiled-state-governance-input/v1",
        created_at="2026-09-11T05:30:00Z",
    )
    boundary = prepare_local_governance_boundary(
        manifest,
        intr_posture_resolver=fake_intr_resolver,
        observed_at="2026-09-11T05:30:00Z",
    )
    continuation = consume_local_governance_handoff(
        boundary,
        custody_db=OUT / f"{case_name}-custody.db",
    )
    result = {
        "case": case_name,
        "event_3_mode": event_3_mode,
        "event_3": source_native["event_3"],
        "missing_inputs": missing_inputs,
        "governance_state": continuation["governance_decision"]["governance_state"],
        "governance_reason": continuation["governance_decision"]["reason_code"],
        "executor_invoked": continuation["governance_decision"]["executor_invoked"],
        "manifest_receipt_id": continuation["manifest_receipt_id"],
        "result_returned": continuation["result_returned"],
    }
    dump(f"{case_name}-manifest.json", manifest)
    dump(f"{case_name}-result.json", result)
    return result


no_signal = run_case("01-no-signal", "NO_SIGNAL")
observed_silence = run_case("02-observed-silence", "OBSERVED_SILENCE")

assert no_signal["event_3"]["predecessor_event"] == 2
assert no_signal["missing_inputs"] == ["event_3:no_signal"]
assert no_signal["governance_state"] == "DENY"
assert no_signal["governance_reason"] == "signal.inputs_incomplete"

assert observed_silence["event_3"]["predecessor_event"] == 2
assert observed_silence["event_3"]["state_transition"]["from_event"] == 2
assert observed_silence["event_3"]["state_transition"]["to"] == "NON_EMISSION_OBSERVED"
assert observed_silence["event_3"]["state_transition"]["trigger"] == "OBSERVATION_WINDOW_CLOSED_WITHOUT_EMISSION"
assert observed_silence["missing_inputs"] == []
assert observed_silence["governance_state"] == "ALLOW"
assert observed_silence["governance_reason"] == "ok"

summary = {
    "schema": "stegverse.compiled-state-governance-matrix-result/v1",
    "goal_task_id": "SDK-COMPILED-STATE-GOVERNANCE-MATRIX-001",
    "upstream_parameters_reinterpreted": False,
    "controlled_difference": "Event 3 terminal signal representation after Event 2",
    "no_signal": no_signal,
    "observed_silence": observed_silence,
}
dump("03-summary.json", summary)
