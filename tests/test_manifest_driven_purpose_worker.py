from __future__ import annotations

import copy
import hashlib
import json
import unittest

from stegverse.manifest_builder import available_processors, build_manifest
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.manifest_execution import execute_manifest
from stegverse.purpose_bound_worker_processor import REQUEST_SCHEMA, derive_state_graph, execute_manifest as execute_processor_manifest
from stegverse.route_resolution import PURPOSE_BOUND_WORKER_ROUTE_ID, PUBLISHED_ROUTES


def request():
    return {
        "schema": REQUEST_SCHEMA,
        "test_id": "SDK-TEST1-PURPOSE-BOUND-WORKER-001",
        "purpose": "Analyze the manifested text payload for a tracked integrity summary.",
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
            "unknown_delay_inference_basis": "single-worker deterministic evaluator demo",
        },
        "expected_evidence_fields": [
            "transition_cell_hash",
            "worker_spec",
            "lifecycle_receipts",
            "task_result",
            "task_result_hash",
            "records_only",
            "worker_live_after_close",
        ],
    }


class ManifestDrivenPurposeWorkerTests(unittest.TestCase):
    def test_installed_processor_is_manifest_builder_visible(self):
        self.assertIn("purpose_bound_worker", available_processors())
        route = PUBLISHED_ROUTES[PURPOSE_BOUND_WORKER_ROUTE_ID]
        self.assertTrue(route["runtime_installed"])
        self.assertEqual(route["processor_capability"], "purpose_bound_worker")

    def test_test_one_runs_from_builder_manifest_only(self):
        manifest = build_manifest(
            data={"text": "StegVerse tracks this arbitrary evaluator-submitted task."},
            source_framework="external_evaluator",
            source_output_id="sdk-test-one-001",
            processor_request=request(),
            process="purpose_bound_worker",
            return_depth="full-trace",
            created_at="2026-09-19T19:45:00Z",
        )
        self.assertEqual(manifest["processing"]["capability"], "purpose_bound_worker")
        self.assertEqual(manifest["processing"]["route_id"], PURPOSE_BOUND_WORKER_ROUTE_ID)
        graph = derive_state_graph(manifest)
        self.assertEqual(graph["canonical_task_id"], "SDK-TT-PURPOSE-BOUND-WORKER-RUNTIME-PROOF-001")
        result = execute_manifest(manifest)
        direct_result = execute_processor_manifest(manifest)
        self.assertEqual(result["schema"], "stegverse.sdk.purpose-bound-worker-manifest-result.v1")
        self.assertTrue(result["evidence_expectations_satisfied"])
        self.assertTrue(result["records_only"])
        self.assertFalse(result["worker_live_after_close"])
        self.assertEqual(
            [row["phase"] for row in result["worker_result"]["lifecycle_receipts"]],
            ["MATERIALIZED", "INVOCATION_STARTED", "TASK_COMPLETED", "RETIRED"],
        )
        canonical = validate_ingress_manifest(manifest)
        direct_hash = hashlib.sha256(
            json.dumps(direct_result, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        request_hash = hashlib.sha256(
            json.dumps(
                result["manifest_lineage"]["run_manifest_request"],
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(result["canonical_manifest_sha256"], canonical["canonical_manifest_sha256"])
        self.assertEqual(result["request_sha256"], request_hash)
        self.assertEqual(result["processor_result_sha256"], direct_hash)
        self.assertEqual(result["manifest_lineage"]["canonical_manifest_sha256"], result["canonical_manifest_sha256"])
        self.assertEqual(result["manifest_lineage"]["request_sha256"], result["request_sha256"])
        self.assertEqual(result["manifest_lineage"]["processor_result_sha256"], result["processor_result_sha256"])


    def test_worker_cost_components_reject_malformed_or_mismatched_budget_through_builder(self):
        # Existing WORKER-TASK-RESOURCE-COST-LINKAGE-001 owner: source-only
        # negative acceptance of the installed, published SDK manifest route.
        cases = [
            ("negative_seconds", ("time_budget_seconds", "known_delay"), -1),
            ("boolean_seconds", ("time_budget_seconds", "safety_reserve"), True),
            ("missing_component", ("time_budget_seconds", "records_decomposition"), None),
            ("mismatched_derived_sum", ("derived_max_lifetime_seconds",), 16),
            ("missing_cost_basis", ("cost_analysis", "task_cost_basis"), ""),
            ("negative_compute_units", ("cost_analysis", "expected_compute_units"), -1),
        ]
        for name, keypath, invalid in cases:
            with self.subTest(name=name):
                candidate = copy.deepcopy(request())
                policy = candidate["lifetime_policy"]
                target = policy
                for key in keypath[:-1]:
                    target = target[key]
                if invalid is None:
                    target.pop(keypath[-1])
                else:
                    target[keypath[-1]] = invalid
                with self.assertRaises(ValueError):
                    build_manifest(
                        data={"text": "bounded source-only negative test"},
                        source_framework="external_evaluator",
                        source_output_id="worker-cost-negative-" + name,
                        processor_request=candidate,
                        process="purpose_bound_worker",
                        return_depth="full-trace",
                        created_at="2026-09-26T12:00:00Z",
                    )

    def test_valid_worker_cost_budget_survives_published_manifest_builder(self):
        candidate = request()
        manifest = build_manifest(
            data={"text": "bounded source-only worker-cost test"},
            source_framework="external_evaluator",
            source_output_id="worker-cost-positive-001",
            processor_request=candidate,
            process="purpose_bound_worker",
            return_depth="full-trace",
            created_at="2026-09-26T12:00:00Z",
        )
        canonical = validate_ingress_manifest(manifest)
        normalized = canonical["extensions"]["stegverse_purpose_bound_worker_request"]
        policy = normalized["lifetime_policy"]
        components = policy["time_budget_seconds"]
        self.assertEqual(policy["derived_max_lifetime_seconds"], sum(components.values()))
        self.assertEqual(policy["cost_analysis"]["task_cost_basis"], candidate["lifetime_policy"]["cost_analysis"]["task_cost_basis"])
        self.assertEqual(canonical["processing"]["route_id"], PURPOSE_BOUND_WORKER_ROUTE_ID)
        # This is SDK semantics only; not an authentic WorkerCoordinator/InTr/MR run.


if __name__ == "__main__":
    unittest.main()
