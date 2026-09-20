from __future__ import annotations

import unittest

from stegverse.manifest_builder import available_processors, build_manifest
from stegverse.manifest_execution import execute_manifest
from stegverse.atomic_task_worker_processor import REQUEST_SCHEMA
from stegverse.route_resolution import ATOMIC_TASK_WORKER_ROUTE_ID, PUBLISHED_ROUTES


SOURCE = {"text": "StegVerse tracks this arbitrary evaluator-submitted task."}
WORKER_MANIFEST = {
    "schema": "stegverse.sdk.worker-manifest.v1",
    "manifest_id": "stegagents-purpose-bound-worker-manifest-v1",
    "worker_id": "stegagents-governed-runtime-worker",
    "capabilities": ["text.integrity_summary"],
    "execution_model": "TASK_BOUND_EPHEMERAL",
    "self_authorization_allowed": False,
    "task_redefinition_allowed": False,
    "authority_scope": "TASK_BOUND_ONLY",
}


def request(test_number: int) -> dict:
    scenario = (
        "TEST_2_ATOMIC_TASK_WORKER_BINDING"
        if test_number == 2
        else "TEST_3_RICHARD_SHORT_LIVED_ACTOR_SEAM"
    )
    return {
        "schema": REQUEST_SCHEMA,
        "test_id": f"SDK-TEST{test_number}-EVALUATOR-001",
        "test_number": test_number,
        "scenario": scenario,
        "task": {
            "task_id": f"sdk-test{test_number}-evaluator-001",
            "cosv_task_vector": "20010000110000",
            "state": "HANDOFF_READY",
            "claim_id": None,
            "worker_instance_id": None,
            "worker_live": False,
            "purpose": "Analyze a supplied text payload for a tracked integrity summary.",
            "required_capability": "text.integrity_summary",
            "max_lifetime_seconds": 30,
        },
        "worker_manifest": WORKER_MANIFEST,
        "activation": {"claim_generation": 1, "fencing_token": 1},
        "preregistered_expectation": {
            "expected_disposition": "PASS_IF_NO_SPLIT_TASK_WORKER_STATE"
            if test_number == 2
            else "PASS_IF_SAME_TASK_WORKER_LINEAGE_CLOSES_RECORDS_ONLY"
        },
        "expected_evidence_fields": [
            "constitutive_transition",
            "reciprocal_task_worker_binding",
            "invocation_after_transition",
            "task_result",
            "close_and_retire",
            "records_only",
            "worker_live_after_close_false",
            "continued_authority_false",
        ],
    }


class EvaluatorAtomicTaskWorkerManifestTests(unittest.TestCase):
    def test_processor_is_public_manifest_builder_choice(self):
        self.assertIn("atomic_task_worker", available_processors())
        route = PUBLISHED_ROUTES[ATOMIC_TASK_WORKER_ROUTE_ID]
        self.assertTrue(route["runtime_installed"])
        self.assertEqual(route["processor_capability"], "atomic_task_worker")

    def _run(self, test_number: int):
        manifest = build_manifest(
            data=SOURCE,
            source_framework="external_evaluator",
            source_output_id=f"sdk-test-{test_number}-001",
            processor_request=request(test_number),
            process="atomic_task_worker",
            return_depth="full-trace",
            created_at=f"2026-09-19T20:0{test_number}:00Z",
        )
        self.assertEqual(manifest["payload"], SOURCE)
        self.assertEqual(manifest["processing"]["route_id"], ATOMIC_TASK_WORKER_ROUTE_ID)
        with self.assertRaisesRegex(ValueError, "AUTHENTIC_GOVERNED_RUNTIME_BINDING_REQUIRED"):
            execute_manifest(manifest)
        return manifest

    def test_test_two_uses_manifest_builder_and_generic_run_manifest_path(self):
        manifest = self._run(2)
        self.assertEqual(
            manifest["extensions"]["stegverse_processor_request"]["scenario"],
            "TEST_2_ATOMIC_TASK_WORKER_BINDING",
        )

    def test_test_three_reuses_same_evaluator_processor_and_path(self):
        manifest = self._run(3)
        self.assertEqual(
            manifest["extensions"]["stegverse_processor_request"]["scenario"],
            "TEST_3_RICHARD_SHORT_LIVED_ACTOR_SEAM",
        )


if __name__ == "__main__":
    unittest.main()
