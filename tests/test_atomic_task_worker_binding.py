from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from stegverse import atomic_task_worker_binding as binding


def example_request() -> dict:
    fixture = Path(__file__).resolve().parents[1] / "inspection" / "examples" / "tt-atomic-task-worker-binding.example.json"
    return json.loads(fixture.read_text(encoding="utf-8"))


class AtomicTaskWorkerBindingTests(unittest.TestCase):
    def test_positive_atomic_binding_lifecycle(self) -> None:
        packet = binding.run_atomic_task_worker_binding(example_request())
        self.assertTrue(packet["records_only"])
        self.assertFalse(packet["worker_live_after_close"])
        self.assertFalse(packet["continued_task_bound_authority"])
        self.assertFalse(packet["callable_retained"])
        self.assertFalse(packet["executor_reference_retained"])
        transition = packet["constitutive_transition"]
        self.assertEqual(transition["task_pre_state"], "HANDOFF_READY")
        self.assertEqual(transition["task_post_state"], "ACTIVE")
        self.assertEqual(transition["task_id"], transition["worker_bound_task_id"])
        self.assertEqual(packet["task_id"], transition["task_id"])
        self.assertEqual(packet["worker_instance_id"], transition["worker_instance_id"])
        self.assertEqual(
            [row["phase"] for row in packet["lifecycle_receipts"]],
            [
                "ACTIVATE_TASK_AND_CREATE_BIND_WORKER",
                "INVOCATION_STARTED",
                "TASK_COMPLETED",
                "CLOSE_TASK_AND_RETIRE_WORKER",
            ],
        )
        self.assertEqual(packet["lifecycle_receipts"][1]["previous_receipt_hash"], transition["receipt_hash"])

    def test_deterministic_packet(self) -> None:
        first = binding.run_atomic_task_worker_binding(example_request())
        second = binding.run_atomic_task_worker_binding(example_request())
        self.assertEqual(first["worker_instance_id"], second["worker_instance_id"])
        self.assertEqual(first["claim_id"], second["claim_id"])
        self.assertEqual(first["records_packet_hash"], second["records_packet_hash"])

    def test_all_required_falsification_cases_fail_closed(self) -> None:
        for fault in sorted(binding.FAULTS):
            with self.subTest(fault=fault):
                with self.assertRaises(binding.AtomicTaskWorkerBindingError):
                    binding.run_atomic_task_worker_binding(example_request(), fault=fault)

    def test_manifest_capability_mismatch_fails_closed(self) -> None:
        request = example_request()
        request["worker_manifest"]["capabilities"] = ["other.capability"]
        with self.assertRaises(binding.AtomicTaskWorkerBindingError):
            binding.run_atomic_task_worker_binding(request)


if __name__ == "__main__":
    unittest.main()
