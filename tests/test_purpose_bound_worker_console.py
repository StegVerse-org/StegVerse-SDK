from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from stegverse import purpose_bound_worker


def example_request() -> dict:
    return {
        "schema": "stegverse.sdk.tt-purpose-bound-worker.v1",
        "transition_cell": {
            "cell_id": "tt-cell-purpose-worker-001",
            "protocol_version": "local-demo-v1",
            "pre_state": {"worker_live": False},
            "candidate": {
                "operation_id": "tracked-task-001",
                "operation_class": "ARBITRARY_TRACKED_TASK",
                "purpose": "Analyze a supplied text payload for a tracked integrity summary.",
                "required_capability": "text.integrity_summary",
                "max_lifetime_seconds": 30,
                "payload": {"text": "StegVerse tracks this arbitrary local worker task."},
            },
        },
    }


class PurposeBoundWorkerTests(unittest.TestCase):
    def test_records_only_lifecycle(self) -> None:
        packet = purpose_bound_worker.run_purpose_bound_worker(example_request())
        self.assertTrue(packet["records_only"])
        self.assertFalse(packet["worker_live_after_close"])
        self.assertEqual(packet["authority_effect"], "NONE")
        self.assertEqual(packet["runtime_binding_state"], "LOCAL_SEMANTIC_DEMONSTRATION_ONLY")
        self.assertEqual(
            [r["phase"] for r in packet["lifecycle_receipts"]],
            ["MATERIALIZED", "INVOCATION_STARTED", "TASK_COMPLETED", "RETIRED"],
        )
        self.assertEqual(packet["lifecycle_receipts"][-1]["worker_live_after_close"], False)
        self.assertGreater(packet["task_result"]["word_count"], 0)

    def test_deterministic_records_packet(self) -> None:
        self.assertEqual(
            purpose_bound_worker.run_purpose_bound_worker(example_request())["records_packet_hash"],
            purpose_bound_worker.run_purpose_bound_worker(example_request())["records_packet_hash"],
        )

    def test_unsupported_capability_fails_closed(self) -> None:
        request = example_request()
        request["transition_cell"]["candidate"]["required_capability"] = "unknown.capability"
        with self.assertRaises(purpose_bound_worker.PurposeBoundWorkerError):
            purpose_bound_worker.run_purpose_bound_worker(request)

    def test_console_outputs_records_only_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "request.json"
            path.write_text(json.dumps(example_request()), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                rc = purpose_bound_worker.main(["--input", str(path)])
            self.assertEqual(rc, 0)
            packet = json.loads(output.getvalue())
            self.assertTrue(packet["records_only"])
            self.assertNotIn("executor", packet)
            self.assertFalse(packet["worker_live_after_close"])


if __name__ == "__main__":
    unittest.main()
