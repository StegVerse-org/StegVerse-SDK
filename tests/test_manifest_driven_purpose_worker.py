from __future__ import annotations

import unittest

from stegverse.manifest_builder import available_processors, build_manifest
from stegverse.manifest_execution import execute_manifest
from stegverse.purpose_bound_worker_processor import REQUEST_SCHEMA
from stegverse.route_resolution import PURPOSE_BOUND_WORKER_ROUTE_ID, PUBLISHED_ROUTES


def request():
    return {
        "schema": REQUEST_SCHEMA,
        "test_id": "SDK-TEST1-PURPOSE-BOUND-WORKER-001",
        "purpose": "Analyze the manifested text payload for a tracked integrity summary.",
        "required_capability": "text.integrity_summary",
        "payload": {"text": "StegVerse SDK Test One manifest-driven evaluator submission."},
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
            data={"experiment": "SDK Test One", "case": 1},
            source_framework="external_evaluator",
            source_output_id="sdk-test-one-001",
            processor_request=request(),
            process="purpose_bound_worker",
            return_depth="full-trace",
            created_at="2026-09-19T19:45:00Z",
        )
        self.assertEqual(manifest["processing"]["capability"], "purpose_bound_worker")
        self.assertEqual(manifest["processing"]["route_id"], PURPOSE_BOUND_WORKER_ROUTE_ID)
        result = execute_manifest(manifest)
        self.assertTrue(result["evidence_expectations_satisfied"])
        self.assertEqual(result["missing_expected_evidence_fields"], [])
        self.assertEqual(
            [row["phase"] for row in result["worker_result"]["lifecycle_receipts"]],
            ["MATERIALIZED", "INVOCATION_STARTED", "TASK_COMPLETED", "RETIRED"],
        )
        self.assertEqual(
            result["derived_worker_request"]["transition_cell"]["candidate"]["max_lifetime_seconds"],
            15,
        )
        self.assertTrue(result["records_only"])
        self.assertFalse(result["worker_live_after_close"])


if __name__ == "__main__":
    unittest.main()
