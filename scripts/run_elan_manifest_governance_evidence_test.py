from __future__ import annotations

import json
from pathlib import Path
import tempfile

from stegverse.evaluator_manifest_builder import build_evaluator_governance_manifest
from stegverse.governance_ingress_runtime import external_manifest_to_public_request
from stegverse.intr_posture_runtime_bridge import resolve_manifest_posture
from stegverse.external_framework_runner import run_external_framework
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
        "actor_class": "external_framework",
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
        "policy_ref": "elan-test-generic-governance-boundary",
        "delegation_ref": "evaluator-submission-only",
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
    "channel": "SDK_EXTERNAL_EVALUATOR",
    "authority_effect": "NONE_REQUEST_INPUT_ONLY"
}

evaluation_declaration = {
    "what": "Submit source-native ELAN Events 1 and 2 through the published governance route without evaluator-specific augmentation.",
    "how": "Canonical SDK Manifest Builder -> InTr posture binding -> governance runtime -> custody -> replay -> reconstruction.",
    "why": "Test generic evaluator compatibility and evidence continuity while preserving native ELAN semantics.",
    "expected_observation": None
}

created_at = "2026-09-10T22:30:00Z"
observed_at = "2026-09-10T22:30:00Z"

dump("00-source-native-input.json", source_native)
dump("01-governance-request.json", governance_request)
dump("02-security-posture-request.json", posture_request)
dump("03-evaluation-declaration.json", evaluation_declaration)

manifest = build_evaluator_governance_manifest(
    data=source_native,
    source_framework="ÉLAN",
    source_output_id="elan-joint-test-trace-2026-09-09-events-1-2",
    governance_request=governance_request,
    evaluation_declaration=evaluation_declaration,
    security_posture_request=posture_request,
    return_depth="full-trace",
    data_class="elan.relational-state.v1",
    created_at=created_at,
)
dump("04-manifest.json", manifest)

transition_request = external_manifest_to_public_request(manifest)
dump("05-transition-request.json", transition_request)

posture_binding = resolve_manifest_posture(
    manifest=manifest,
    transition_request=transition_request,
    resolver=fake_intr_resolver,
    observed_at=observed_at,
)
dump("06-intr-posture-binding.json", posture_binding)

state_transitions = [
    {"step": 0, "state": "SOURCE_NATIVE_CAPTURED", "evidence": "00-source-native-input.json"},
    {"step": 1, "state": "GOVERNANCE_REQUEST_DECLARED", "evidence": "01-governance-request.json"},
    {"step": 2, "state": "POSTURE_REQUEST_DECLARED_NON_AUTHORIZING", "evidence": "02-security-posture-request.json"},
    {"step": 3, "state": "MANIFEST_BUILT_VALIDATED", "evidence": "04-manifest.json"},
    {"step": 4, "state": "GOVERNANCE_TRANSITION_REQUEST_MATERIALIZED", "evidence": "05-transition-request.json"},
    {"step": 5, "state": "INTR_POSTURE_BOUND_TEST_DOUBLE", "evidence": "06-intr-posture-binding.json", "authentic_live_intr": False},
]

with tempfile.TemporaryDirectory() as tmp:
    custody_db = str(Path(tmp) / "elan-governance-test.db")
    try:
        run = run_external_framework(
            data=source_native,
            source_framework="ÉLAN",
            source_output_id="elan-joint-test-trace-2026-09-09-events-1-2",
            processor_request=governance_request,
            evaluation_declaration=evaluation_declaration,
            security_posture_request=posture_request,
            return_depth="full-trace",
            data_class="elan.relational-state.v1",
            created_at=created_at,
            custody_db=custody_db,
            host_identity="stegverse-sdk-evidence-test",
            replay=True,
            reconstruct=True,
            intr_posture_resolver=fake_intr_resolver,
            posture_observed_at=observed_at,
        )
        dump("07-governed-run.json", run)
        dump("08-governed-result.json", run.get("governed_result"))
        dump("09-replay.json", run.get("replay"))
        dump("10-reconstruction.json", run.get("reconstruction"))
        state_transitions.extend([
            {"step": 6, "state": "GOVERNANCE_EXECUTED", "evidence": "08-governed-result.json", "manifest_receipt_id": run.get("manifest_receipt_id")},
            {"step": 7, "state": "REPLAY_COMPLETED", "evidence": "09-replay.json"},
            {"step": 8, "state": "RECONSTRUCTION_COMPLETED", "evidence": "10-reconstruction.json"},
            {"step": 9, "state": "RESULT_DOCUMENTED", "evidence": "11-state-transitions.json"}
        ])
        outcome = "SOURCE_LEVEL_GOVERNED_RUN_COMPLETE_WITH_TEST_DOUBLE_INTR"
        exit_code = 0
    except Exception as exc:
        dump("07-governed-run-error.json", {"type": type(exc).__name__, "message": str(exc)})
        state_transitions.append({"step": 6, "state": "GOVERNANCE_EXECUTION_FAILED", "evidence": "07-governed-run-error.json"})
        outcome = "SOURCE_LEVEL_GOVERNED_RUN_FAILED"
        exit_code = 1

dump("11-state-transitions.json", state_transitions)
summary = {
    "schema": "stegverse.elan-governance-evidence-test/v1",
    "goal_task_id": "SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001",
    "source_framework": "ÉLAN",
    "source_events": [1, 2],
    "event_3_synthesized": False,
    "manifest_return_depth": "full-trace",
    "intr_resolver_mode": "DETERMINISTIC_TEST_DOUBLE",
    "authentic_live_stegos_intr_proven": False,
    "outcome": outcome,
    "state_transition_count": len(state_transitions)
}
dump("12-summary.json", summary)

md = [
    "# ÉLAN -> StegVerse Governance Evidence Test",
    "",
    f"Outcome: `{outcome}`",
    "",
    "This run uses the current SDK Manifest Builder and governance runtime. The InTr resolver is the repository's deterministic test double, so this run can prove source-level composition/governance/custody/replay/reconstruction behavior but **cannot** prove authentic live StegOS/InTr runtime posture resolution.",
    "",
    "## State transitions",
]
for s in state_transitions:
    md.append(f"- {s['step']}: `{s['state']}` -> `{s['evidence']}`")
md += [
    "",
    "## Non-interference",
    "- Source-native ÉLAN Events 1 and 2 are preserved as payload data.",
    "- Event 3 remains NOT_SUBMITTED and is not synthesized.",
    "- Evaluation declaration contains no expected success observation.",
    "- Security posture request remains non-authorizing input.",
    "- SDK does not resolve final posture.",
    "",
    "## Authentic runtime boundary",
    "A separate authentic run is still required with the live `stegos.intr_security_posture_resolution.resolve_task_security_posture` resolver materialized in the execution environment."
]
(OUT / "13-results-documentation.md").write_text("\n".join(md) + "\n", encoding="utf-8")
raise SystemExit(exit_code)
