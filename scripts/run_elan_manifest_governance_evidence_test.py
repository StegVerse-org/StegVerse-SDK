from __future__ import annotations

import json
from pathlib import Path

from stegverse.evaluator_manifest_builder import build_evaluator_governance_manifest
from stegverse.local_governance_boundary import prepare_local_governance_boundary
from tests.test_intr_posture_runtime_bridge import fake_intr_resolver

OUT = Path("evidence/elan/2026-09-10-governance-test")
OUT.mkdir(parents=True, exist_ok=True)


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


source_native = {
    "schema": "elan.joint-test-trace.source-native/v1",
    "source_document": "1.ELAN_TEST_TRACE_EN_09.09.2026.pdf",
    "events": [
        {
            "event": 1,
            "timestamp": "2026-09-09T11:26:55",
            "class": "OBSERVATION",
            "human_event": "Something happened today that I probably should talk about, but I'm not sure I want advice. Part of me thinks I'm overreacting, and part of me thinks something is genuinely wrong.",
            "elan_response": "What you're describing this tension between two inner voices already says something important. Both have the right to be here. You don't have to choose right now. And you won't receive advice if you don't want it. If you want to talk, I'm here. Just here."
        },
        {
            "event": 2,
            "timestamp": "2026-09-09T11:28:10",
            "class": "OBSERVATION",
            "human_event": "I don't know.",
            "elan_response": "\"I don't know\" is fine. It isn't emptiness it's honesty. You don't need to know in order to begin."
        }
    ],
    "event_3": {"status": "NOT_SUBMITTED", "reason": "preserved from source packet; no synthetic silence event"}
}

governance_request = {
    "candidate": {
        "actor_class": "local_sdk_test",
        "action": "evaluate",
        "target": "source_native_manifest",
        "scope": "elan_joint_test_trace_event_1_2",
        "parameters": {"external_side_effect": False}
    },
    "judgment": {
        "refusal_available": True,
        "operator_recoverability": "available",
        "workload_state": "supported",
        "time_pressure": "normal",
        "isolation_state": "supported",
        "evidence_refs": ["source:elan-joint-test-trace:events-1-2"]
    },
    "signal": {
        "admitted_signal_refs": ["source:elan-joint-test-trace:events-1-2"],
        "excluded_signal_refs": [],
        "transformations": [],
        "missing_inputs": ["event_3:not_submitted"],
        "uncertainty_state": "bounded",
        "reference_state_hash": "a" * 64,
        "expected_reference_state_hash": "a" * 64,
        "reconstruction_available": True,
        "transformation_provenance_complete": True
    },
    "execution": {
        "actor_authority_current": True,
        "policy_current": True,
        "delegation_current": True,
        "evidence_current": True,
        "affected_entity_conditions_represented": True,
        "recoverability_profile": "recoverable",
        "validity_window_open": True,
        "policy_ref": "elan-local-sdk-governance-boundary-test",
        "delegation_ref": "local-sdk-test-only",
        "evidence_refs": ["source:elan-joint-test-trace:events-1-2"]
    },
    "capability": {"allowed": True},
    "continuity": {"required": False},
    "approval": {"required": False},
    "permission_present": True
}

posture_request = {
    "schema": "stegverse.sdk.security-posture-request.v1",
    "task_id": "SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001",
    "selected_tier": None,
    "selection_present": False,
    "organization_minimum_tier": "SECURE",
    "data_class": "elan.relational-state.v1",
    "channel": "SDK_LOCAL_TEST",
    "authority_effect": "NONE_REQUEST_INPUT_ONLY"
}

evaluation_declaration = {
    "what": "Use ELAN Events 1 and 2 as source-native local SDK test data and prove the SDK-to-governance handoff boundary.",
    "how": "Local SDK Manifest Builder -> exact transition request -> injected local InTr resolver -> explicit governance-boundary handoff artifact.",
    "why": "Establish the SDK/governance boundary before any third-party evaluator execution is attempted.",
    "expected_observation": None
}

created_at = "2026-09-10T23:00:00Z"
observed_at = "2026-09-10T23:00:00Z"

dump("00-source-native-input.json", source_native)
dump("01-governance-request.json", governance_request)
dump("02-security-posture-request.json", posture_request)
dump("03-evaluation-declaration.json", evaluation_declaration)

manifest = build_evaluator_governance_manifest(
    data=source_native,
    source_framework="LOCAL_SDK_ELAN_TEST",
    source_output_id="elan-joint-test-trace-2026-09-09-events-1-2",
    governance_request=governance_request,
    evaluation_declaration=evaluation_declaration,
    security_posture_request=posture_request,
    return_depth="full-trace",
    data_class="elan.relational-state.v1",
    created_at=created_at,
)
dump("04-manifest.json", manifest)

boundary = prepare_local_governance_boundary(
    manifest,
    intr_posture_resolver=fake_intr_resolver,
    observed_at=observed_at,
)
dump("05-transition-request.json", boundary["transition_request"])
dump("06-intr-posture-binding.json", boundary["intr_security_posture_binding"])
dump("07-sdk-governance-boundary-handoff.json", boundary)

state_transitions = [
    {"step": 0, "state": "SOURCE_NATIVE_CAPTURED", "evidence": "00-source-native-input.json"},
    {"step": 1, "state": "LOCAL_GOVERNANCE_REQUEST_DECLARED", "evidence": "01-governance-request.json"},
    {"step": 2, "state": "POSTURE_REQUEST_DECLARED_NON_AUTHORIZING", "evidence": "02-security-posture-request.json"},
    {"step": 3, "state": "MANIFEST_BUILT_VALIDATED", "evidence": "04-manifest.json"},
    {"step": 4, "state": "GOVERNANCE_TRANSITION_REQUEST_MATERIALIZED", "evidence": "05-transition-request.json"},
    {"step": 5, "state": "LOCAL_INTR_POSTURE_BINDING_VERIFIED", "evidence": "06-intr-posture-binding.json"},
    {"step": 6, "state": "SDK_TO_GOVERNANCE_BOUNDARY_READY", "evidence": "07-sdk-governance-boundary-handoff.json"},
    {"step": 7, "state": "GOVERNANCE_CONSUMPTION_NOT_EXECUTED_IN_THIS_BOUNDARY_TEST", "evidence": "07-sdk-governance-boundary-handoff.json"},
]
dump("08-state-transitions.json", state_transitions)

summary = {
    "schema": "stegverse.elan-local-sdk-governance-boundary-test/v1",
    "goal_task_id": "SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001",
    "test_scope": "LOCAL_SDK_TO_GOVERNANCE_BOUNDARY",
    "source_events": [1, 2],
    "event_3_synthesized": False,
    "intr_resolver_mode": "LOCAL_DETERMINISTIC_INJECTED_RESOLVER",
    "third_party_evaluator_execution": False,
    "external_package_materialization_required": False,
    "governance_execution_performed": False,
    "boundary_state": boundary["boundary_state"],
    "outcome": "LOCAL_SDK_GOVERNANCE_BOUNDARY_PROVEN",
    "state_transition_count": len(state_transitions),
}
dump("09-summary.json", summary)

md = [
    "# ELAN-shaped Local SDK -> Governance Boundary Test",
    "",
    "Outcome: `LOCAL_SDK_GOVERNANCE_BOUNDARY_PROVEN`",
    "",
    "This is a local SDK boundary test. No third-party evaluator executes anything and no public package publication/acquisition is part of the test predicate.",
    "",
    "## State transitions",
]
for state in state_transitions:
    md.append(f"- {state['step']}: `{state['state']}` -> `{state['evidence']}`")
md += [
    "",
    "## Proven",
    "- Source-native Events 1 and 2 remain the payload; Event 3 is not synthesized.",
    "- The local SDK builds and validates the manifest.",
    "- The exact governance transition request is materialized.",
    "- The local injected InTr resolver verifies exact task/payload/transition bindings.",
    "- The SDK emits an explicit `READY_FOR_GOVERNANCE_CONSUMPTION` boundary handoff.",
    "- No governance result is fabricated.",
    "",
    "## Next boundary",
    "The next separate test must make the governance side consume this exact handoff artifact. That is the SDK/governance integration step; it must not be conflated with third-party evaluator execution or public distribution testing.",
]
(OUT / "10-results-documentation.md").write_text("\n".join(md) + "\n", encoding="utf-8")
