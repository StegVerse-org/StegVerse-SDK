"""Deterministic SDK demonstration of cost-derived purpose-bound worker lifetimes.

This is a local semantic demonstration. It does not claim authentic WorkerCoordinator,
Interlock/InTr, TV/TVC, resident-runtime, or Master Records execution.
"""
from __future__ import annotations

import argparse
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Mapping

from .purpose_bound_worker import PurposeBoundWorkerError, _sha256, run_purpose_bound_worker

SCHEMA = "stegverse.sdk.tt-purpose-bound-worker-cost-demo.v1"
PACKET_SCHEMA = "stegverse.sdk.tt-purpose-bound-worker-cost-demo.records-only.v1"


def _sum_budget(budget: Mapping[str, Any]) -> int:
    names = (
        "expected_task_execution",
        "known_delay",
        "inferred_unknown_delay_reserve",
        "records_decomposition",
        "safety_reserve",
    )
    values = []
    for name in names:
        value = budget.get(name)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise PurposeBoundWorkerError(f"{name} must be a nonnegative integer")
        values.append(value)
    return sum(values)


def _validate_case(case: Mapping[str, Any], *, worker_count: int) -> dict[str, Any]:
    if case.get("worker_count") != worker_count:
        raise PurposeBoundWorkerError(f"worker_count must be {worker_count}")
    compute = case.get("expected_compute_units")
    if worker_count > 1:
        compute = case.get("per_worker_expected_compute_units")
    if not isinstance(compute, int) or isinstance(compute, bool) or compute <= 0:
        raise PurposeBoundWorkerError("positive expected compute units required")
    budget = case.get("time_budget_seconds")
    if worker_count > 1:
        budget = case.get("per_worker_time_budget_seconds")
    if not isinstance(budget, Mapping):
        raise PurposeBoundWorkerError("time budget required")
    derived = _sum_budget(budget)
    expected = case.get("derived_max_lifetime_seconds")
    if worker_count > 1:
        expected = case.get("per_worker_derived_max_lifetime_seconds")
    if expected != derived:
        raise PurposeBoundWorkerError("derived lifetime budget mismatch")
    purpose = case.get("purpose")
    if not isinstance(purpose, str) or not purpose.strip():
        raise PurposeBoundWorkerError("purpose required")
    return dict(case)


def _request(case: Mapping[str, Any], text: str, suffix: str) -> dict[str, Any]:
    lifetime = case.get("derived_max_lifetime_seconds")
    if case.get("worker_count") != 1:
        lifetime = case.get("per_worker_derived_max_lifetime_seconds")
    return {
        "schema": "stegverse.sdk.tt-purpose-bound-worker.v1",
        "transition_cell": {
            "cell_id": f"tt-purpose-cost-demo-{case['demo_task_id']}-{suffix}",
            "protocol_version": "cost-demo-v1",
            "pre_state": {"worker_live": False},
            "candidate": {
                "operation_id": f"{case['demo_task_id']}-{suffix}",
                "operation_class": "ARBITRARY_TRACKED_TASK",
                "purpose": case["purpose"],
                "required_capability": "text.integrity_summary",
                "max_lifetime_seconds": lifetime,
                "payload": {"text": text},
            },
        },
    }


def _run_concurrent(case: Mapping[str, Any], payloads: list[str]) -> dict[str, Any]:
    if len(payloads) != 3:
        raise PurposeBoundWorkerError("concurrent case requires exactly three payload partitions")
    barrier = threading.Barrier(3)

    def run_one(index: int) -> dict[str, Any]:
        started_ns = time.monotonic_ns()
        barrier.wait(timeout=5)
        packet = run_purpose_bound_worker(_request(case, payloads[index], f"worker-{index + 1}"))
        completed_ns = time.monotonic_ns()
        return {
            "worker_index": index + 1,
            "started_ns": started_ns,
            "completed_ns": completed_ns,
            "records_packet": packet,
        }

    with ThreadPoolExecutor(max_workers=3) as pool:
        workers = list(pool.map(run_one, range(3)))

    worker_ids = [row["records_packet"]["worker_spec"]["worker_id"] for row in workers]
    overlap = max(row["started_ns"] for row in workers) <= min(row["completed_ns"] for row in workers)
    if len(set(worker_ids)) != 3:
        raise PurposeBoundWorkerError("concurrent workers must have distinct worker identities")
    if not overlap:
        raise PurposeBoundWorkerError("simultaneous worker overlap not observed")
    if not all(row["records_packet"]["records_only"] for row in workers):
        raise PurposeBoundWorkerError("concurrent worker did not decompose to records only")
    if not all(row["records_packet"]["worker_live_after_close"] is False for row in workers):
        raise PurposeBoundWorkerError("concurrent worker remained live after close")

    return {
        "demo_task_id": case["demo_task_id"],
        "worker_count": 3,
        "aggregate_expected_compute_units": case["aggregate_expected_compute_units"],
        "per_worker_expected_compute_units": case["per_worker_expected_compute_units"],
        "per_worker_derived_max_lifetime_seconds": case["per_worker_derived_max_lifetime_seconds"],
        "group_wall_clock_budget_seconds": case["group_wall_clock_budget_seconds"],
        "simultaneous_overlap_observed": overlap,
        "workers": workers,
        "records_only": True,
        "continued_authority_after_retirement": False,
    }


def run_cost_lifetime_demo(request: Mapping[str, Any]) -> dict[str, Any]:
    if request.get("schema") != SCHEMA:
        raise PurposeBoundWorkerError(f"schema must be {SCHEMA}")
    singles = request.get("individual_tasks")
    concurrent = request.get("concurrent_task")
    if not isinstance(singles, list) or len(singles) != 3:
        raise PurposeBoundWorkerError("exactly three individual tasks required")
    if not isinstance(concurrent, Mapping):
        raise PurposeBoundWorkerError("concurrent_task required")

    normalized_singles = [_validate_case(case, worker_count=1) for case in singles]
    normalized_concurrent = _validate_case(concurrent, worker_count=3)

    lifetimes = [case["derived_max_lifetime_seconds"] for case in normalized_singles]
    if not lifetimes[0] < lifetimes[1] < lifetimes[2]:
        raise PurposeBoundWorkerError("single-worker lifetimes must be strictly increasing")
    if normalized_concurrent["per_worker_derived_max_lifetime_seconds"] != lifetimes[1]:
        raise PurposeBoundWorkerError("concurrent per-worker lifetime must equal median single-worker reference")
    if normalized_concurrent["group_wall_clock_budget_seconds"] != lifetimes[1]:
        raise PurposeBoundWorkerError("concurrent group wall-clock budget must equal median single-worker reference")

    base_text = request.get("payload_text")
    if not isinstance(base_text, str) or not base_text:
        raise PurposeBoundWorkerError("payload_text required")

    single_packets = []
    for index, case in enumerate(normalized_singles, start=1):
        packet = run_purpose_bound_worker(_request(case, f"{base_text} | tier {index}", f"tier-{index}"))
        single_packets.append({
            "demo_task_id": case["demo_task_id"],
            "cost_class": case["cost_class"],
            "expected_compute_units": case["expected_compute_units"],
            "derived_max_lifetime_seconds": case["derived_max_lifetime_seconds"],
            "records_packet": packet,
        })

    concurrent_packet = _run_concurrent(
        normalized_concurrent,
        [f"{base_text} | parallel partition {index}" for index in (1, 2, 3)],
    )

    packet = {
        "schema": PACKET_SCHEMA,
        "source_schema": SCHEMA,
        "single_worker_cases": single_packets,
        "concurrent_case": concurrent_packet,
        "lifetime_demarcation_seconds": lifetimes,
        "median_reference_lifetime_seconds": lifetimes[1],
        "all_workers_records_only": all(
            row["records_packet"]["records_only"] and not row["records_packet"]["worker_live_after_close"]
            for row in single_packets
        ) and concurrent_packet["records_only"],
        "continued_authority_after_retirement": False,
        "runtime_binding_state": "LOCAL_SEMANTIC_DEMONSTRATION_ONLY",
        "authority_effect": "NONE",
    }
    packet["records_packet_hash"] = _sha256(packet)
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the four-case purpose-bound worker cost/lifetime demonstration.")
    parser.add_argument("--input", required=True)
    args = parser.parse_args(argv)
    request = json.loads(Path(args.input).read_text(encoding="utf-8"))
    print(json.dumps(run_cost_lifetime_demo(request), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
