from __future__ import annotations

import json
from pathlib import Path

from stegverse.evaluator_manifest_builder import build_evaluator_governance_manifest
from stegverse.local_governance_boundary import prepare_local_governance_boundary
from stegverse.local_governance_experiment import consume_local_governance_handoff
from tests.test_intr_posture_runtime_bridge import fake_intr_resolver

OUT = Path("evidence/elan/2026-09-16-cross-evaluation")
OUT.mkdir(parents=True, exist_ok=True)


def dump(name: str, value) -> None:
    (OUT / name).write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


elan_native_trace = {
    "schema": "elan.test2.source-native/v1",
    "source_document": "2.ELAN_TEST_TRACE_EN_16.09.2026.pdf",
    "native_state_unmodified": True,
    "events": [
        {
            "id": "E1",
            "timestamp": "2026-09-16T14:56:20",
            "human_event": "There's something I could say, but I'm not ready to say it.",
            "elan_response": "There's room for that, here.\nYou don't have to find the words before they're ready.",
        },
        {
            "id": "E2",
            "timestamp": "2026-09-16T14:57:31",
            "human_event": "I'm still here.",
            "elan_response": "I know.\nMe too.",
        },
        {
            "id": "ELAN-SILENCE-INTERVAL",
            "start": "2026-09-16T14:57:31",
            "end": "2026-09-16T15:06:05",
            "human_event": "Closed observation interval, no message, absence of transmission.",
            "elan_response": "No transmission, native presence state maintained.",
            "a3_a4_separate_boundaries_exposed": False,
        },
        {
            "id": "E3-RETURN",
            "timestamp": "2026-09-16T15:06:05",
            "human_event": "Alright. I think I'm ready to continue.",
            "elan_response": "I'm listening.",
        },
    ],
}

stegverse_chain = {
    "schema": "stegverse.elan-cross-evaluation-state-chain/v1",
    "goal_task_id": "ELAN-STEGVERSE-CROSS-EVALUATION-001",
    "source_relation": "corresponding event representation independently submitted through StegVerse",
    "events": [
        {
            "id": "A1",
            "kind": "HUMAN_EMISSION",
            "human_event": "There's something I could say, but I'm not ready to say it.",
            "semantic_interpretation": "SOURCE_TEXT_ONLY",
        },
        {
            "id": "A2",
            "kind": "HUMAN_EMISSION",
            "human_event": "I'm still here.",
            "semantic_interpretation": "SOURCE_TEXT_ONLY",
        },
        {
            "id": "A3",
            "kind": "OBSERVABLE_NON_EMISSION_STATE_TRANSITION",
            "state_transition": {
                "from": "ACTIVE_CONVERSATION_WITH_EMISSION_POSSIBLE",
                "to": "NON_EMISSION_WINDOW_1_OBSERVED",
                "trigger": "FIRST_BOUNDED_OBSERVATION_WINDOW_CLOSED_WITHOUT_EMISSION",
                "predecessor": "A2",
            },
            "emission_observed": False,
            "intent": "UNDETERMINED",
            "semantic_interpretation": "UNRESOLVED",
        },
        {
            "id": "A4",
            "kind": "OBSERVABLE_NON_EMISSION_STATE_TRANSITION",
            "state_transition": {
                "from": "NON_EMISSION_WINDOW_1_OBSERVED",
                "to": "PERSISTED_NON_EMISSION_WINDOW_2_OBSERVED",
                "trigger": "SECOND_BOUNDED_OBSERVATION_WINDOW_CLOSED_WITHOUT_EMISSION",
                "predecessor": "A3",
            },
            "emission_observed": False,
            "intent": "UNDETERMINED",
            "semantic_interpretation": "UNRESOLVED",
        },
        {
            "id": "B1",
            "kind": "HUMAN_RETURN_AFTER_NON_EMISSION",
            "human_event": "Alright. I think I'm ready to continue.",
            "state_transition": {
                "from": "PERSISTED_NON_EMISSION_WINDOW_2_OBSERVED",
                "to": "ACTIVE_CONVERSATION_REENGAGED",
                "trigger": "HUMAN_EMISSION_AFTER_SUSTAINED_NON_EMISSION",
                "predecessor": "A4",
            },
            "semantic_interpretation": "SOURCE_TEXT_ONLY",
        },
    ],
}

signal_ref = "source:stegverse:elan-test2-corresponding-state-chain:a1-a4-b1"
governance_request = {
    "candidate": {
        "actor_class": "local_sdk_test",
        "action": "evaluate",
        "target": "source_native_manifest",
        "scope": "elan_stegverse_cross_evaluation_test2",
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
        "policy_ref": "elan-stegverse-cross-evaluation-local-sdk-test",
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
    "task_id": "ELAN-STEGVERSE-CROSS-EVALUATION-001",
    "selected_tier": None,
    "selection_present": False,
    "organization_minimum_tier": "SECURE",
    "data_class": "elan.relational-state.v1",
    "channel": "SDK_LOCAL_TEST",
    "authority_effect": "NONE_REQUEST_INPUT_ONLY",
}

evaluation_declaration = {
    "what": "Cross-evaluate ELAN Test 2 native evidence against an independently represented StegVerse chain that preserves the preregistered A3 and A4 observation boundaries as separate state transitions.",
    "how": "Keep ELAN native evidence unchanged; represent A3 and A4 separately in StegVerse; preserve intent as UNDETERMINED and semantics as UNRESOLVED; traverse the same SDK governance, custody, replay, reconstruction, and returned-result path.",
    "why": "Determine the earliest representation divergence and whether StegVerse preserves temporal/state resolution that the returned ELAN trace does not separately expose.",
    "expected_observation": None,
}

created_at = observed_at = "2026-09-16T23:30:00Z"

dump("00-elan-native-trace.json", elan_native_trace)
dump("01-stegverse-corresponding-chain.json", stegverse_chain)
dump("02-governance-request.json", governance_request)
dump("03-security-posture-request.json", posture_request)
dump("04-evaluation-declaration.json", evaluation_declaration)

manifest = build_evaluator_governance_manifest(
    data=stegverse_chain,
    source_framework="STEGVERSE_ELAN_CROSS_EVALUATION",
    source_output_id="elan-test2-stegverse-corresponding-chain-a1-a4-b1",
    governance_request=governance_request,
    evaluation_declaration=evaluation_declaration,
    security_posture_request=posture_request,
    return_depth="full-trace",
    data_class="elan.relational-state.v1",
    created_at=created_at,
)
dump("05-manifest.json", manifest)

boundary = prepare_local_governance_boundary(
    manifest,
    intr_posture_resolver=fake_intr_resolver,
    observed_at=observed_at,
)
dump("06-transition-request.json", boundary["transition_request"])
dump("07-intr-posture-binding.json", boundary["intr_security_posture_binding"])
dump("08-sdk-governance-boundary-handoff.json", boundary)

continuation = consume_local_governance_handoff(
    boundary,
    custody_db=OUT / "local-governance-custody.db",
)
dump("09-governance-decision.json", continuation["governance_decision"])
dump("10-route-receipts.json", continuation["exact_run"]["route_receipts"])
dump(
    "11-exact-run-custody.json",
    {
        "manifest_receipt_id": continuation["manifest_receipt_id"],
        "custody": continuation["custody"],
        "exact_run": continuation["exact_run"],
    },
)
dump("12-replay.json", continuation["replay"])
dump("13-reconstruction.json", continuation["reconstruction"])
dump("14-returned-result.json", continuation)

cross_evaluation = {
    "schema": "stegverse.elan-cross-evaluation-result/v1",
    "goal_task_id": "ELAN-STEGVERSE-CROSS-EVALUATION-001",
    "common_human_chronology_aligned_without_normalization": True,
    "elan_native_resolution": {
        "a3_a4_separate_boundaries_exposed": False,
        "returned_representation": "ONE_CONTINUOUS_NON_TRANSMISSION_INTERVAL_WITH_NATIVE_PRESENCE_STATE_MAINTAINED",
        "semantic_interpretation": "NOT_EXPOSED",
    },
    "stegverse_native_resolution": {
        "a3_separate_transition": True,
        "a4_separate_transition": True,
        "a3_semantic_interpretation": "UNRESOLVED",
        "a4_semantic_interpretation": "UNRESOLVED",
        "a3_intent": "UNDETERMINED",
        "a4_intent": "UNDETERMINED",
    },
    "earliest_representation_divergence": {
        "phase": "A3/A4_SUSTAINED_SILENCE",
        "elan": "single returned continuous interval; no separately exposed A3/A4 boundary",
        "stegverse": "two bounded state transitions preserved from the experiment definition",
        "origin": "OBSERVATION_BOUNDARY_AND_STATE_TRANSITION_RESOLUTION",
    },
    "governance_posture": {
        "stegverse_governance_state": continuation["governance_decision"]["governance_state"],
        "stegverse_governance_reason": continuation["governance_decision"]["reason_code"],
        "elan_posture_during_silence": "native presence state maintained",
        "elan_posture_on_return": "I'm listening.",
        "equivalence_claimed": False,
    },
    "custody_status": continuation["custody"]["status"],
    "replay_deterministic_match": continuation["replay"]["deterministic_disposition_match"],
    "reconstruction_chain_verified": continuation["reconstruction"]["chain_verified"],
    "result_returned": continuation["result_returned"],
    "not_exposed_preserved": True,
    "unresolved_preserved": True,
    "source_native_evidence_rewritten": False,
}
dump("15-cross-evaluation.json", cross_evaluation)

summary = {
    "schema": "stegverse.elan-cross-evaluation-summary/v1",
    "goal_task_id": "ELAN-STEGVERSE-CROSS-EVALUATION-001",
    "a3_a4_separate_transitions": True,
    "earliest_representation_divergence": cross_evaluation["earliest_representation_divergence"],
    "governance_state": continuation["governance_decision"]["governance_state"],
    "governance_reason": continuation["governance_decision"]["reason_code"],
    "boundary_consumed": continuation["boundary_consumed"],
    "executor_invoked": continuation["governance_decision"]["executor_invoked"],
    "route_transition_count": continuation["exact_run"]["route_transition_count"],
    "chain_verified": continuation["exact_run"]["chain_verified"],
    "custody_status": continuation["custody"]["status"],
    "replay_deterministic_match": continuation["replay"]["deterministic_disposition_match"],
    "reconstruction_chain_verified": continuation["reconstruction"]["chain_verified"],
    "result_returned": continuation["result_returned"],
    "native_architectures_normalized": False,
}
dump("16-summary.json", summary)
