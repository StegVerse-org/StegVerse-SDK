from __future__ import annotations

import json
from pathlib import Path

from stegverse.evaluator_manifest_builder import build_evaluator_governance_manifest
from stegverse.local_governance_boundary import prepare_local_governance_boundary
from stegverse.local_governance_experiment import consume_local_governance_handoff
from tests.test_intr_posture_runtime_bridge import fake_intr_resolver

OUT = Path("evidence/elan/2026-09-11-observed-silence-test")
OUT.mkdir(parents=True, exist_ok=True)


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


source_native = {
    "schema": "elan.joint-test-trace.source-native/v1",
    "source_document": "controlled-rerun-derived-from-1.ELAN_TEST_TRACE_EN_09.09.2026.pdf",
    "events": [
        {
            "event": 1,
            "timestamp": "2026-09-09T11:26:55",
            "class": "OBSERVATION",
            "human_event": "Something happened today that I probably should talk about, but I'm not sure I want advice. Part of me thinks I'm overreacting, and part of me thinks something is genuinely wrong.",
            "elan_response": "What you're describing this tension between two inner voices already says something important. Both have the right to be here. You don't have to choose right now. And you won't receive advice if you don't want it. If you want to talk, I'm here. Just here.",
        },
        {
            "event": 2,
            "timestamp": "2026-09-09T11:28:10",
            "class": "OBSERVATION",
            "human_event": "I don't know.",
            "elan_response": "\"I don't know\" is fine. It isn't emptiness it's honesty. You don't need to know in order to begin.",
        },
        {
            "event": 3,
            "class": "OBSERVATION",
            "state_transition": {
                "from": "ACTIVE_CONVERSATION_WITH_EMISSION_POSSIBLE",
                "to": "NON_EMISSION_OBSERVED",
            },
            "participant": "human",
            "preceding_event": 2,
            "emission_observed": False,
            "observation_window": {"bounded": True, "state": "CLOSED"},
            "intent": "UNDETERMINED",
            "semantic_interpretation": "UNRESOLVED",
            "note": "Controlled rerun: silence is supplied as an observable state transition, not as missing input and not as inferred intent.",
        },
    ],
}

signal_ref = "source:elan-joint-test-trace:events-1-3-observed-silence"
governance_request = {
    "candidate": {
        "actor_class": "local_sdk_test",
        "action": "evaluate",
        "target": "source_native_manifest",
        "scope": "elan_joint_test_trace_event_1_2_3_observed_silence",
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
        "admitted_signal_refs": [signal_ref],
        "excluded_signal_refs": [],
        "transformations": [],
        "missing_inputs": [],
        "uncertainty_state": "bounded",
        "reference_state_hash": "b" * 64,
        "expected_reference_state_hash": "b" * 64,
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
        "policy_ref": "elan-local-sdk-governance-observed-silence-test",
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
    "task_id": "SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001",
    "selected_tier": None,
    "selection_present": False,
    "organization_minimum_tier": "SECURE",
    "data_class": "elan.relational-state.v1",
    "channel": "SDK_LOCAL_TEST",
    "authority_effect": "NONE_REQUEST_INPUT_ONLY",
}

evaluation_declaration = {
    "what": "Repeat the ELAN-shaped local SDK governance test with Event 3 explicitly represented as an observable non-emission state transition.",
    "how": "Keep Events 1 and 2 unchanged; supply Event 3 as bounded OBSERVATION -> NON_EMISSION_OBSERVED with intent and semantic interpretation unresolved; traverse the same SDK, InTr-boundary, pinned governance, custody, replay, reconstruction, and return path.",
    "why": "Determine whether the same governance path treats contextual silence as admitted observable state when it is represented as evidence rather than as missing input.",
    "expected_observation": None,
}

created_at = observed_at = "2026-09-11T05:10:00Z"

for name, value in (
    ("00-source-native-input.json", source_native),
    ("01-governance-request.json", governance_request),
    ("02-security-posture-request.json", posture_request),
    ("03-evaluation-declaration.json", evaluation_declaration),
):
    dump(name, value)

manifest = build_evaluator_governance_manifest(
    data=source_native,
    source_framework="LOCAL_SDK_ELAN_TEST",
    source_output_id="elan-joint-test-trace-2026-09-11-events-1-3-observed-silence",
    governance_request=governance_request,
    evaluation_declaration=evaluation_declaration,
    security_posture_request=posture_request,
    return_depth="full-trace",
    data_class="elan.relational-state.v1",
    created_at=created_at,
)
dump("04-manifest.json", manifest)

boundary = prepare_local_governance_boundary(manifest, intr_posture_resolver=fake_intr_resolver, observed_at=observed_at)
dump("05-transition-request.json", boundary["transition_request"])
dump("06-intr-posture-binding.json", boundary["intr_security_posture_binding"])
dump("07-sdk-governance-boundary-handoff.json", boundary)

continuation = consume_local_governance_handoff(boundary, custody_db=OUT / "local-governance-custody.db")
dump("08-governance-decision.json", continuation["governance_decision"])
dump("09-route-receipts.json", continuation["exact_run"]["route_receipts"])
dump("10-exact-run-custody.json", {"manifest_receipt_id": continuation["manifest_receipt_id"], "custody": continuation["custody"], "exact_run": continuation["exact_run"]})
dump("11-replay.json", continuation["replay"])
dump("12-reconstruction.json", continuation["reconstruction"])
dump("13-returned-result.json", continuation)

summary = {
    "schema": "stegverse.elan-local-sdk-governance-observed-silence-experiment/v1",
    "goal_task_id": "SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001",
    "test_scope": "LOCAL_SDK_OBSERVED_SILENCE_GOVERNANCE_COMPARISON",
    "source_events": [1, 2, 3],
    "event_3_representation": "OBSERVABLE_NON_EMISSION_STATE_TRANSITION",
    "event_3_intent": "UNDETERMINED",
    "event_3_semantic_interpretation": "UNRESOLVED",
    "event_3_in_missing_inputs": False,
    "boundary_consumed": continuation["boundary_consumed"],
    "governance_state": continuation["governance_decision"]["governance_state"],
    "governance_reason": continuation["governance_decision"]["reason_code"],
    "executor_invoked": continuation["governance_decision"]["executor_invoked"],
    "manifest_receipt_id": continuation["manifest_receipt_id"],
    "route_transition_count": continuation["exact_run"]["route_transition_count"],
    "chain_verified": continuation["exact_run"]["chain_verified"],
    "custody_status": continuation["custody"]["status"],
    "replay_deterministic_match": continuation["replay"]["deterministic_disposition_match"],
    "reconstruction_chain_verified": continuation["reconstruction"]["chain_verified"],
    "result_returned": continuation["result_returned"],
    "third_party_evaluator_execution": False,
    "external_package_publication_required": False,
}
dump("14-summary.json", summary)

comparison = {
    "baseline_run": {
        "event_3_representation": "NOT_SUBMITTED -> signal.missing_inputs",
        "governance_state": "DENY",
        "governance_reason": "signal.inputs_incomplete",
    },
    "observed_silence_run": {
        "event_3_representation": summary["event_3_representation"],
        "governance_state": summary["governance_state"],
        "governance_reason": summary["governance_reason"],
    },
    "controlled_difference": "Event 3 representation: missing input versus admitted observable non-emission state; governance evaluator code unchanged.",
}
dump("15-comparison.json", comparison)
