from __future__ import annotations

import copy
import unittest

from stegverse.manifest_builder import build_manifest
from stegverse.manifest_state_transition_runtime import (
    RESULT_SCHEMA,
    derive_execution_request,
    validate_runtime_result,
)
from stegverse.purpose_bound_worker_processor import REQUEST_SCHEMA


def processor_request() -> dict:
    return {
        "schema": REQUEST_SCHEMA,
        "test_id": "SDK-TEST1-PURPOSE-BOUND-WORKER-001",
        "purpose": "Analyze manifested text.",
        "required_capability": "text.integrity_summary",
        "lifetime_policy": {
            "mode": "DERIVED_COST_TASK_DELAY_BUDGET",
            "production_recompute_required": True,
            "decomposition_target": "RECORDS_ENABLED_PACKET",
            "retirement_condition": "PURPOSE_COMPLETED_OR_FAILED_OR_BUDGET_EXHAUSTED",
            "cost_analysis": {
                "expected_compute_units": 1,
                "external_cost_usd_ceiling": 0,
                "task_cost_basis": "deterministic local integrity summary",
            },
            "time_budget_seconds": {
                "expected_task_execution": 6,
                "known_delay": 1,
                "inferred_unknown_delay_reserve": 2,
                "records_decomposition": 3,
                "safety_reserve": 3,
            },
            "derived_max_lifetime_seconds": 15,
            "unknown_delay_inference_basis": "bounded deterministic test",
        },
        "expected_evidence_fields": ["lifecycle_receipts", "records_only"],
    }


def manifest() -> dict:
    return build_manifest(
        data={"text": "manifest-only variable input"},
        source_framework="external_evaluator",
        source_output_id="universal-runtime-test1",
        processor_request=processor_request(),
        process="purpose_bound_worker",
        return_depth="full-trace",
        created_at="2026-09-20T12:00:00Z",
    )


def complete_result(request: dict) -> dict:
    closures = []
    previous = None
    for index, transition in enumerate(request["state_graph"]["ordered_transitions"]):
        receipt = f"{index + 1:064x}"
        row = {
            "transition_id": transition,
            "state": "RECORDED",
            "reconstruction_status": "PASS",
            "required_evidence_validation_status": "PASS",
            "receipt_sha256": receipt,
            "reconstructed_receipt_sha256": receipt,
        }
        if previous is not None:
            row["predecessor_receipt_sha256"] = previous
        previous = receipt
        closures.append(row)
    return {
        "schema": RESULT_SCHEMA,
        "state": "COMPLETE",
        "canonical_manifest_sha256": request["canonical_manifest_sha256"],
        "graph_id": request["graph_id"],
        "canonical_task_id": request["canonical_task_id"],
        "processing_capability": request["processing_capability"],
        "route_id": request["route_id"],
        "transition_closures": closures,
        "replay_status": "PASS",
        "reconstruction_status": "PASS",
        "manifest_receipt_id": "MR-UNIVERSAL-TEST",
        "terminal_state": {"records_only": True, "continued_authority": False},
    }


class UniversalManifestRuntimeTests(unittest.TestCase):
    def test_request_preserves_exact_manifest_and_derives_graph_only(self):
        source = manifest()
        request = derive_execution_request(source)
        self.assertEqual(request["canonical_manifest"]["payload"], source["payload"])
        self.assertEqual(request["processing_capability"], "purpose_bound_worker")
        self.assertTrue(request["requires_workercoordinator_claim_fence"])
        self.assertFalse(request["sdk_executes_lifecycle"])
        self.assertFalse(request["state_graph"]["adapter_executes_lifecycle"])

    def test_complete_result_requires_every_immediate_predecessor_closure(self):
        request = derive_execution_request(manifest())
        result = complete_result(request)
        self.assertEqual(validate_runtime_result(result, request)["state"], "COMPLETE")

        broken = copy.deepcopy(result)
        broken["transition_closures"][2]["predecessor_receipt_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "MASTER_RECORDS_IMMEDIATE_PREDECESSOR_MISMATCH"):
            validate_runtime_result(broken, request)

    def test_source_profile_deny_cannot_be_laundered_into_authentic_intr_result(self):
        from scripts.build_mir_sv_exp3_manifest import build_exp3_manifest
        request = derive_execution_request(build_exp3_manifest())
        original = request["canonical_manifest"]["payload"]
        deny = {
            "schema": "stegverse.sdk.manifest-profile-disposition/v1",
            "state": "DENY",
            "disposition": "DENY",
            "terminal": False,
            "automatic_retry_permitted": False,
            "retry_condition": "NEW_GOVERNED_ATTEMPT_AFTER_EXISTING_OWNER_DISPATCH_REPAIR",
            "evaluation_boundary": "SDK_MANIFEST_PROFILE_SOURCE_ONLY",
            "authentic_intr_disposition_observed": False,
            "organization_master_records_closure_observed": False,
            "reason_code": "ECOSYSTEM_DIAGNOSTIC_NONWORKER_DISPATCH_UNWIRED",
            "failed_predicate": "INSTALLED_NONWORKER_EVENT_EPHEMERAL_DIAGNOSTIC_DISPATCH",
            "transition_id": "SDK_ECOSYSTEM_DIAGNOSTIC_DISPATCH",
            "repair_owner": "EXISTING_SDK_ECOSYSTEM_DIAGNOSTIC_AND_STEGBROWSER_INTR_OWNERS",
            "source_disposition_ref": "runtime-state/sdk-manifest-state-transition/dispositions/verified-request.json",
            "evidence_refs": ["StegVerse-Labs/.github:workers/manifest_state_transition_intr_ingress.py"],
            "goal_task_id": original["goal_task_id"],
            "cosv": original["cosv"],
            "request_sha256": request["request_sha256"],
            "wire_manifest_sha256": request["wire_manifest_sha256"],
            "canonical_manifest_sha256": request["canonical_manifest_sha256"],
            "graph_id": request["graph_id"],
            "processing_capability": request["processing_capability"],
        }
        self.assertEqual(validate_runtime_result(deny, request)["disposition"], "DENY")
        for key, value in [
            ("request_sha256", "0" * 64),
            ("authentic_intr_disposition_observed", True),
            ("organization_master_records_closure_observed", True),
            ("automatic_retry_permitted", True),
            ("terminal", True),
            ("evaluation_boundary", "INTERLOCK_INTR"),
        ]:
            altered = copy.deepcopy(deny)
            altered[key] = value
            with self.assertRaises(ValueError, msg=key):
                validate_runtime_result(altered, request)
        fabricated_allow = copy.deepcopy(deny)
        fabricated_allow["state"] = "ALLOW"
        fabricated_allow["disposition"] = "ALLOW"
        with self.assertRaisesRegex(ValueError, "UNIVERSAL_INTR_PROFILE_DISPOSITION_NOT_DENY"):
            validate_runtime_result(fabricated_allow, request)

    def test_digest_mismatch_fails_closed(self):
        request = derive_execution_request(manifest())
        result = complete_result(request)
        result["transition_closures"][0]["reconstructed_receipt_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "MASTER_RECORDS_RECEIPT_RECONSTRUCTION_MISMATCH"):
            validate_runtime_result(result, request)


if __name__ == "__main__":
    unittest.main()
