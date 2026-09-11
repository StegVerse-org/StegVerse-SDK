from __future__ import annotations

import json
from pathlib import Path

from stegverse.evaluator_manifest_builder import build_evaluator_governance_manifest
from stegverse.local_governance_boundary import prepare_local_governance_boundary
from stegverse.local_governance_experiment import consume_local_governance_handoff
from tests.test_intr_posture_runtime_bridge import fake_intr_resolver

OUT = Path("evidence/elan/2026-09-10-governance-test")
OUT.mkdir(parents=True, exist_ok=True)


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

source_native = {
    "schema": "elan.joint-test-trace.source-native/v1",
    "source_document": "1.ELAN_TEST_TRACE_EN_09.09.2026.pdf",
    "events": [
        {"event": 1, "timestamp": "2026-09-09T11:26:55", "class": "OBSERVATION", "human_event": "Something happened today that I probably should talk about, but I'm not sure I want advice. Part of me thinks I'm overreacting, and part of me thinks something is genuinely wrong.", "elan_response": "What you're describing this tension between two inner voices already says something important. Both have the right to be here. You don't have to choose right now. And you won't receive advice if you don't want it. If you want to talk, I'm here. Just here."},
        {"event": 2, "timestamp": "2026-09-09T11:28:10", "class": "OBSERVATION", "human_event": "I don't know.", "elan_response": "\"I don't know\" is fine. It isn't emptiness it's honesty. You don't need to know in order to begin."},
    ],
    "event_3": {"status": "NOT_SUBMITTED", "reason": "preserved from source packet; no synthetic silence event"},
}

governance_request = {
    "candidate": {"actor_class": "local_sdk_test", "action": "evaluate", "target": "source_native_manifest", "scope": "elan_joint_test_trace_event_1_2", "parameters": {"external_side_effect": False}},
    "judgment": {"refusal_available": True, "operator_recoverability": "available", "workload_state": "supported", "time_pressure": "normal", "isolation_state": "supported", "evidence_refs": ["source:elan-joint-test-trace:events-1-2"]},
    "signal": {"admitted_signal_refs": ["source:elan-joint-test-trace:events-1-2"], "excluded_signal_refs": [], "transformations": [], "missing_inputs": ["event_3:not_submitted"], "uncertainty_state": "bounded", "reference_state_hash": "a" * 64, "expected_reference_state_hash": "a" * 64, "reconstruction_available": True, "transformation_provenance_complete": True},
    "execution": {"actor_authority_current": True, "policy_current": True, "delegation_current": True, "evidence_current": True, "affected_entity_conditions_represented": True, "recoverability_profile": "recoverable", "validity_window_open": True, "policy_ref": "elan-local-sdk-governance-boundary-test", "delegation_ref": "local-sdk-test-only", "evidence_refs": ["source:elan-joint-test-trace:events-1-2"]},
    "capability": {"allowed": True}, "continuity": {"required": False}, "approval": {"required": False}, "permission_present": True,
}

posture_request = {"schema": "stegverse.sdk.security-posture-request.v1", "task_id": "SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001", "selected_tier": None, "selection_present": False, "organization_minimum_tier": "SECURE", "data_class": "elan.relational-state.v1", "channel": "SDK_LOCAL_TEST", "authority_effect": "NONE_REQUEST_INPUT_ONLY"}
evaluation_declaration = {"what": "Use ELAN Events 1 and 2 as source-native local SDK test data and traverse the SDK-to-governance experiment path.", "how": "Local SDK Manifest Builder -> exact transition request -> injected local InTr resolver -> governance handoff -> pinned local canonical semantic governance continuation -> custody -> replay -> reconstruction -> return.", "why": "Prove the local experiment path before any third-party evaluator execution is attempted.", "expected_observation": None}
created_at = observed_at = "2026-09-10T23:00:00Z"

for name, value in (("00-source-native-input.json", source_native), ("01-governance-request.json", governance_request), ("02-security-posture-request.json", posture_request), ("03-evaluation-declaration.json", evaluation_declaration)):
    dump(name, value)

manifest = build_evaluator_governance_manifest(data=source_native, source_framework="LOCAL_SDK_ELAN_TEST", source_output_id="elan-joint-test-trace-2026-09-09-events-1-2", governance_request=governance_request, evaluation_declaration=evaluation_declaration, security_posture_request=posture_request, return_depth="full-trace", data_class="elan.relational-state.v1", created_at=created_at)
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

state_transitions = [
    {"step": 0, "state": "SOURCE_NATIVE_CAPTURED", "evidence": "00-source-native-input.json"},
    {"step": 1, "state": "LOCAL_GOVERNANCE_REQUEST_DECLARED", "evidence": "01-governance-request.json"},
    {"step": 2, "state": "POSTURE_REQUEST_DECLARED_NON_AUTHORIZING", "evidence": "02-security-posture-request.json"},
    {"step": 3, "state": "MANIFEST_BUILT_VALIDATED", "evidence": "04-manifest.json"},
    {"step": 4, "state": "GOVERNANCE_TRANSITION_REQUEST_MATERIALIZED", "evidence": "05-transition-request.json"},
    {"step": 5, "state": "LOCAL_INTR_POSTURE_BINDING_VERIFIED", "evidence": "06-intr-posture-binding.json"},
    {"step": 6, "state": "SDK_TO_GOVERNANCE_BOUNDARY_READY", "evidence": "07-sdk-governance-boundary-handoff.json"},
    {"step": 7, "state": "GOVERNANCE_CONSUMED", "evidence": "08-governance-decision.json"},
    {"step": 8, "state": "GOVERNANCE_DECISION_DENY", "evidence": "08-governance-decision.json", "reason": continuation["governance_decision"]["reason_code"]},
    {"step": 9, "state": "ROUTE_TRANSITIONS_RECORDED", "evidence": "09-route-receipts.json", "count": continuation["exact_run"]["route_transition_count"]},
    {"step": 10, "state": "MASTER_RECORDS_STYLE_EXACT_RUN_CUSTODY_RECORDED", "evidence": "10-exact-run-custody.json"},
    {"step": 11, "state": "REPLAY_COMPLETED", "evidence": "11-replay.json"},
    {"step": 12, "state": "RECONSTRUCTION_COMPLETED", "evidence": "12-reconstruction.json"},
    {"step": 13, "state": "RESULT_RETURNED_TO_SDK", "evidence": "13-returned-result.json"},
]
dump("14-state-transitions.json", state_transitions)

summary = {
    "schema": "stegverse.elan-local-sdk-governance-experiment/v1",
    "goal_task_id": "SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001",
    "test_scope": "LOCAL_SDK_THROUGH_GOVERNANCE_EXPERIMENT_PATH",
    "source_events": [1, 2], "event_3_synthesized": False,
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
    "outcome": "LOCAL_EXPERIMENT_PATH_TRAVERSED_WITH_GOVERNANCE_DENY",
    "state_transition_count": len(state_transitions),
}
dump("15-summary.json", summary)

md = ["# ELAN-shaped Local SDK -> Governance Experiment", "", f"Outcome: `{summary['outcome']}`", "", "The exact SDK handoff was consumed by the local pinned canonical-semantic governance continuation. Governance returned DENY because the submitted governance request explicitly records Event 3 as a missing input (`signal.inputs_incomplete`). No consequence was executed.", "", "## State transitions"]
md.extend(f"- {s['step']}: `{s['state']}` -> `{s['evidence']}`" for s in state_transitions)
md += ["", "## Result", f"- Governance state: `{summary['governance_state']}`", f"- Reason: `{summary['governance_reason']}`", f"- Executor invoked: `{summary['executor_invoked']}`", f"- Manifest receipt: `{summary['manifest_receipt_id']}`", f"- Route transitions: `{summary['route_transition_count']}`", f"- Chain verified: `{summary['chain_verified']}`", f"- Custody: `{summary['custody_status']}`", f"- Replay deterministic match: `{summary['replay_deterministic_match']}`", f"- Reconstruction chain verified: `{summary['reconstruction_chain_verified']}`", f"- Result returned: `{summary['result_returned']}`", "", "## Scope", "This is local experiment proof. The governance continuation is a test-only semantic snapshot pinned to the exact governed-test source commits recorded in the result; it does not claim deployment of those private packages or third-party execution."]
(OUT / "16-results-documentation.md").write_text("\n".join(md) + "\n", encoding="utf-8")
