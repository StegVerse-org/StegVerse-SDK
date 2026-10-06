from __future__ import annotations

import copy
import unittest

from stegverse.governance_navigation import canonical_sha256
from stegverse.manifest_builder import build_manifest
from stegverse.manifest_state_transition_runtime import derive_execution_request, validate_runtime_result
from stegverse.route_resolution import CANONICAL_PRODUCTION_ROUTE_ID


TASK_ID = "ORGANIZATION-BATCH-CUSTODY-REPLAY-001"
COSV = "10000000100000"
REQUEST_REF = (
    "control/resident-execution-request.d/"
    "canonical-work-organization-batch-custody-replay-001.json"
)


def canonical_request():
    return {
        "schema": "stegverse.resident-execution-request/v1",
        "request_id": "RESIDENT-EXEC-ORGANIZATION-BATCH-CUSTODY-REPLAY-001",
        "state": "REQUESTED",
        "task_id": TASK_ID,
        "cosv_profile": "task.v1",
        "cosv_task_vector": COSV,
        "pointer_source": "data/canonical-task-records/ORGANIZATION-BATCH-CUSTODY-REPLAY-001.json",
        "mode": "CANONICAL_WORK_EVENT_BOOTSTRAP",
        "entrypoint": "scripts/install_and_run_canonical_work_event_bootstrap.py",
        "credential_authority": "TV/TVC",
        "github_token_required": False,
        "github_token_runtime_authority": "NONE",
        "heartbeat_grants_execution_authority": False,
        "oscillator_grants_execution_authority": False,
        "second_machine_required": False,
        "network_source_fetch_allowed": False,
        "request_granted_authority": False,
        "authority_effect": "NONE_REQUEST_ONLY",
    }


def governance_request(payload):
    payload_hash = canonical_sha256(payload)
    candidate = {
        "actor_class": "canonical_task",
        "action": "execute_manifest_directed_organization_append",
        "target": TASK_ID,
        "scope": "organization_batch_custody_replay",
        "parameters": {"external_side_effect": False},
    }
    return {
        "candidate": candidate,
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": [REQUEST_REF],
        },
        "signal": {
            "admitted_signal_refs": [REQUEST_REF],
            "excluded_signal_refs": [],
            "transformations": [],
            "missing_inputs": [],
            "uncertainty_state": "bounded",
            "reference_state_hash": payload_hash,
            "expected_reference_state_hash": payload_hash,
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
            "policy_ref": "canonical-task-registry:" + TASK_ID,
            "delegation_ref": "tvc:manifest-governance-only",
            "evidence_refs": [REQUEST_REF],
        },
        "capability": {"allowed": True},
        "continuity": {"required": True},
        "approval": {"required": False},
        "permission_present": True,
    }


def fixture():
    payload = canonical_request()
    manifest = build_manifest(
        data=payload,
        source_framework="StegVerse-Labs/.github",
        source_output_id=payload["request_id"],
        processor_request=governance_request(payload),
        process="governance",
        return_depth="result+evidence",
        created_at="2026-09-29T02:00:00Z",
        declared_intent="Govern the canonical organization batch custody transition.",
        requested_consequence=(
            "On ALLOW only, execute the existing manifest-directed organization append "
            "and preserve downstream custody as execution evidence."
        ),
        publisher_required=False,
        initiator_class="canonical_task",
        initiator_ref=TASK_ID,
    )
    manifest["extensions"]["stegverse_canonical_task"] = {
        "task_id": TASK_ID,
        "correlation_id": TASK_ID,
        "registry_repository": "StegVerse-Labs/.github",
        "observed_registry_generation": 278,
        "cosv_task_vector": COSV,
        "canonical_request_ref": REQUEST_REF,
        "authority_effect": "NONE",
    }
    manifest["extensions"]["stegverse_organization_receipt_batch"] = {
        "release_condition": {"type": "COUNT", "count": 2}
    }
    return manifest


class TestOrganizationBatchGovernanceBinding(unittest.TestCase):
    def test_generic_governance_graph_binds_exact_canonical_task_without_new_authority(self):
        manifest = fixture()
        request = derive_execution_request(manifest)
        graph = request["state_graph"]
        self.assertEqual(graph["graph_id"], "RTC-GOVERNED-PROCESSING-002:" + TASK_ID)
        self.assertEqual(graph["canonical_task_id"], TASK_ID)
        self.assertFalse(graph["requires_workercoordinator_claim_fence"])
        self.assertFalse(graph["adapter_executes_lifecycle"])
        self.assertEqual(graph["processing_capability"], "governance")
        self.assertEqual(graph["route_id"], CANONICAL_PRODUCTION_ROUTE_ID)
        binding = graph["request"]["canonical_task_binding"]
        self.assertEqual(binding["task_id"], TASK_ID)
        self.assertEqual(binding["cosv_task_vector"], COSV)
        self.assertEqual(binding["canonical_request_ref"], REQUEST_REF)
        self.assertEqual(binding["original_request_sha256"], canonical_sha256(manifest["payload"]))
        self.assertEqual(binding["receipt_batch"]["release_condition"], {"type": "COUNT", "count": 2})
        self.assertFalse(request["request_grants_authority"])

    def test_rejects_changed_canonical_request_even_when_manifest_rehashes(self):
        manifest = fixture()
        manifest["payload"]["second_machine_required"] = True
        manifest["hashes"]["payload_sha256"] = canonical_sha256(manifest["payload"])
        with self.assertRaisesRegex(
            ValueError, "ORGANIZATION_BATCH_UNCHANGED_REQUEST_MISMATCH:second_machine_required"
        ):
            derive_execution_request(manifest)

    def test_rejects_missing_batch_policy_and_identity_drift(self):
        manifest = fixture()
        del manifest["extensions"]["stegverse_organization_receipt_batch"]
        with self.assertRaisesRegex(ValueError, "ORGANIZATION_BATCH_RECEIPT_BATCH_POLICY_REQUIRED"):
            derive_execution_request(manifest)

        manifest = fixture()
        manifest["extensions"]["stegverse_canonical_task"]["cosv_task_vector"] = "0" * 14
        with self.assertRaisesRegex(ValueError, "ORGANIZATION_BATCH_COSV_BINDING_MISMATCH"):
            derive_execution_request(manifest)

        manifest = fixture()
        manifest["extensions"]["stegverse_canonical_task"]["authority_effect"] = "ALLOW"
        with self.assertRaisesRegex(
            ValueError, "ORGANIZATION_BATCH_TASK_BINDING_MUST_NOT_GRANT_AUTHORITY"
        ):
            derive_execution_request(manifest)


    def test_runtime_result_preserves_parent_allow_and_separate_action_execution(self):
        request = derive_execution_request(fixture())

        def closure(transition_id, digest, predecessor=None):
            row = {
                "transition_id": transition_id,
                "state": "RECORDED",
                "reconstruction_status": "PASS",
                "required_evidence_validation_status": "PASS",
                "receipt_sha256": digest,
                "reconstructed_receipt_sha256": digest,
            }
            if predecessor is not None:
                row["predecessor_receipt_sha256"] = predecessor
            return row

        ingress = closure("INGRESS_ADMITTED", "1" * 64)
        governed = closure("GOVERNANCE_DISPOSITION", "2" * 64, "1" * 64)
        dispatch = closure("MANIFEST_DIRECTED_ORGANIZATION_APPEND_DISPATCHED", "3" * 64, "2" * 64)
        result = {
            "schema": "stegverse.sdk.manifest-state-transition-result/v1",
            "state": "COMPLETE",
            "disposition": "ALLOW",
            "terminal": False,
            "communication_terminal": False,
            "canonical_task_id": TASK_ID,
            "subject_or_correlation_id": TASK_ID,
            "processing_capability": "governance",
            "route_id": request["route_id"],
            "graph_id": request["graph_id"],
            "request_sha256": request["request_sha256"],
            "wire_manifest_sha256": request["wire_manifest_sha256"],
            "canonical_manifest_sha256": request["canonical_manifest_sha256"],
            "resolved_ordered_transitions": ["INGRESS_ADMITTED", "GOVERNANCE_DISPOSITION"],
            "transition_closures": [ingress, governed],
            "records_authority": "ORGANIZATION_RECORDS_ONLY",
            "publisher_executed": False,
            "site_propagation_executed": False,
            "authority_effect": "NONE_GOVERNANCE_DISPOSITION_ONLY",
            "manifest_directed_action": {
                "schema": "stegverse.manifest-directed-action-execution/v1",
                "action_id": "ORGANIZATION_APPEND",
                "execution_result": "COMPLETED",
                "governance_disposition": None,
                "canonical_manifest_sha256": request["canonical_manifest_sha256"],
                "parent_governance_receipt_sha256": "2" * 64,
                "dispatch_closure": dispatch,
                "organization_receipt_sha256": "sha256:" + "4" * 64,
                "organization_previous_receipt_sha256": "sha256:" + "5" * 64,
                "source_transition_sha256": "sha256:" + "6" * 64,
                "released_batch": {
                    "batch_id": "sha256:" + "7" * 64,
                    "execution_result": "FAILED",
                    "governance_disposition": None,
                    "reason": "ORGANIZATION_BATCH_AUTHENTIC_CUSTODY_SURFACE_UNAVAILABLE",
                    "authority_effect": "NONE",
                },
                "authority_effect": "NONE_EXECUTION_EVIDENCE_ONLY",
            },
        }
        checked = validate_runtime_result(result, request)
        self.assertEqual(checked["disposition"], "ALLOW")
        self.assertEqual(
            checked["manifest_directed_action"]["released_batch"]["execution_result"],
            "FAILED",
        )

        escalated = copy.deepcopy(result)
        escalated["manifest_directed_action"]["governance_disposition"] = "ALLOW"
        with self.assertRaisesRegex(
            ValueError, "ORGANIZATION_BATCH_ACTION_RESULT_MISMATCH:governance_disposition"
        ):
            validate_runtime_result(escalated, request)


if __name__ == "__main__":
    unittest.main()
