from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from stegverse import purpose_bound_worker_cost_demo as demo
from stegverse.purpose_bound_worker import PurposeBoundWorkerError

FIXTURE = Path("inspection/examples/tt-purpose-worker-cost-demo.example.json")


class PurposeBoundWorkerCostDemoTests(unittest.TestCase):
    def fixture(self) -> dict:
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_four_case_cost_lifetime_demo(self) -> None:
        packet = demo.run_cost_lifetime_demo(self.fixture())
        self.assertEqual(packet["lifetime_demarcation_seconds"], [15, 30, 60])
        self.assertEqual(packet["median_reference_lifetime_seconds"], 30)
        self.assertTrue(packet["all_workers_records_only"])
        self.assertFalse(packet["continued_authority_after_retirement"])
        self.assertEqual(packet["runtime_binding_state"], "LOCAL_SEMANTIC_DEMONSTRATION_ONLY")

    def test_individual_worker_lifetimes_are_strictly_demarcated(self) -> None:
        packet = demo.run_cost_lifetime_demo(self.fixture())
        rows = packet["single_worker_cases"]
        self.assertEqual([r["expected_compute_units"] for r in rows], [1, 3, 9])
        self.assertEqual([r["derived_max_lifetime_seconds"] for r in rows], [15, 30, 60])
        self.assertTrue(all(r["records_packet"]["records_only"] for r in rows))
        self.assertTrue(all(r["records_packet"]["worker_live_after_close"] is False for r in rows))

    def test_fourth_task_uses_three_simultaneous_median_budget_workers(self) -> None:
        packet = demo.run_cost_lifetime_demo(self.fixture())
        group = packet["concurrent_case"]
        self.assertEqual(group["worker_count"], 3)
        self.assertEqual(group["aggregate_expected_compute_units"], 9)
        self.assertEqual(group["per_worker_expected_compute_units"], 3)
        self.assertEqual(group["per_worker_derived_max_lifetime_seconds"], 30)
        self.assertEqual(group["group_wall_clock_budget_seconds"], 30)
        self.assertTrue(group["simultaneous_overlap_observed"])
        worker_ids = [w["records_packet"]["worker_spec"]["worker_id"] for w in group["workers"]]
        self.assertEqual(len(set(worker_ids)), 3)
        self.assertTrue(all(w["records_packet"]["records_only"] for w in group["workers"]))
        self.assertFalse(group["continued_authority_after_retirement"])

    def test_concurrent_budget_drift_fails_closed(self) -> None:
        request = copy.deepcopy(self.fixture())
        request["concurrent_task"]["per_worker_derived_max_lifetime_seconds"] = 31
        with self.assertRaises(PurposeBoundWorkerError):
            demo.run_cost_lifetime_demo(request)


if __name__ == "__main__":
    unittest.main()
