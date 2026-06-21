#!/usr/bin/env python3
"""Validate SDK to Core-Node fanout request artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REQUEST = ROOT / "examples" / "sdk_core_node_fanout_request.sample.json"
EXPECTED_PATHS = ["PATH-1", "PATH-2", "PATH-3", "PATH-4", "PATH-5"]
REQUIRED_RESULT_FIELDS = {
    "path_id",
    "result_status",
    "elapsed_time_ms",
    "memory_peak_mb",
    "estimated_cost_usd",
    "receipt_count",
    "failure_or_warning_state",
    "human_readable_summary",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(request: dict) -> None:
    if request["sdk_intake"]["repo"] != "StegVerse-org/StegVerse-SDK":
        raise AssertionError("request must originate from SDK intake")
    if not request["sdk_intake"]["package_hash"].startswith("sha256:"):
        raise AssertionError("package hash must be sha256-prefixed")
    if request["core_node_target"]["repo"] != "StegVerse-org/core-node-runtime-demo":
        raise AssertionError("request must target core-node-runtime-demo")
    if request["core_node_target"]["runtime"] != "core-node":
        raise AssertionError("request runtime must be core-node")

    path_ids = [item["path_id"] for item in request["fanout_paths"]]
    if path_ids != EXPECTED_PATHS:
        raise AssertionError("fanout request must include PATH-1 through PATH-5 in order")
    if not all(item["enabled"] is True for item in request["fanout_paths"]):
        raise AssertionError("all fanout paths must be enabled for comparison")

    result_fields = set(request["result_shape_required"])
    if result_fields != REQUIRED_RESULT_FIELDS:
        raise AssertionError("result shape fields do not match required comparison shape")

    witness = request["witness_loop"]
    if witness != {"independent": True, "target": "master-records", "receipt_references_only": True}:
        raise AssertionError("witness loop must remain independent and receipt-reference only")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", nargs="?", default=str(DEFAULT_REQUEST))
    args = parser.parse_args()

    validate(read_json(Path(args.request)))
    print("PASS: SDK core-node fanout request is valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
