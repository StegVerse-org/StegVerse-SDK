#!/usr/bin/env python3
"""Validate SDK to Core-Node unified comparison receipt artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECEIPT = ROOT / "examples" / "sdk_core_node_unified_comparison_receipt.sample.json"
EXPECTED_PATHS = ["PATH-1", "PATH-2", "PATH-3", "PATH-4", "PATH-5"]
REQUIRED_SHAPE = [
    "path_id",
    "result_status",
    "elapsed_time_ms",
    "memory_peak_mb",
    "estimated_cost_usd",
    "receipt_count",
    "failure_or_warning_state",
    "human_readable_summary",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(receipt: dict) -> None:
    if receipt["core_node_runtime"] != "StegVerse-org/core-node-runtime-demo":
        raise AssertionError("receipt must reference the core-node runtime demo")
    if receipt["baseline_path"] != "PATH-1":
        raise AssertionError("receipt baseline must be PATH-1")
    if receipt["human_result_shape"] != REQUIRED_SHAPE:
        raise AssertionError("human result shape must match required SDK comparison shape")

    path_ids = [item["path_id"] for item in receipt["path_results"]]
    if path_ids != EXPECTED_PATHS:
        raise AssertionError("receipt must contain PATH-1 through PATH-5 in order")

    for item in receipt["path_results"]:
        if list(item.keys()) != REQUIRED_SHAPE:
            raise AssertionError(f"{item['path_id']} does not use the required result shape")
        if item["result_status"] not in {"PASS", "FAIL", "WARN"}:
            raise AssertionError(f"{item['path_id']} has invalid result status")
        for numeric_field in ["elapsed_time_ms", "memory_peak_mb", "estimated_cost_usd"]:
            if item[numeric_field] < 0:
                raise AssertionError(f"{item['path_id']} has negative {numeric_field}")
        if item["receipt_count"] < 0:
            raise AssertionError(f"{item['path_id']} has negative receipt_count")
        if not item["human_readable_summary"]:
            raise AssertionError(f"{item['path_id']} missing human summary")

    if not receipt["witness_receipts"]:
        raise AssertionError("receipt must include witness receipt references")
    if not all(ref.startswith("master-records-") for ref in receipt["witness_receipts"]):
        raise AssertionError("witness receipts must reference master-records")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", nargs="?", default=str(DEFAULT_RECEIPT))
    args = parser.parse_args()

    validate(read_json(Path(args.receipt)))
    print("PASS: SDK core-node unified comparison receipt is valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
