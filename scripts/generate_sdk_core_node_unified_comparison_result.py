#!/usr/bin/env python3
"""Generate human-readable SDK Core-Node comparison result."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "examples" / "sdk_core_node_unified_comparison_receipt.sample.json"
OUTPUT = ROOT / "examples" / "sdk_core_node_unified_comparison_result.sample.md"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def format_cost(value: float) -> str:
    if 0 < value < 0.001:
        return f"{value:.8f}".rstrip("0").rstrip(".")
    return str(value)


def main() -> int:
    receipt = read_json(RECEIPT)
    lines = [
        "# SDK Core-Node Unified Comparison Result",
        "",
        f"Request: `{receipt['request_id']}`  ",
        f"Package: `{receipt['package_id']}`  ",
        f"Baseline: `{receipt['baseline_path']}`  ",
        f"Runtime: `{receipt['core_node_runtime']}`",
        "",
        "## Path comparison",
        "",
        "| Path | Status | Elapsed ms | Memory MB | Cost USD | Receipts | Warning state | Summary |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]

    for item in receipt["path_results"]:
        lines.append(
            "| {path_id} | {status} | {elapsed} | {memory} | {cost} | {receipts} | {warning} | {summary} |".format(
                path_id=item["path_id"],
                status=item["result_status"],
                elapsed=item["elapsed_time_ms"],
                memory=item["memory_peak_mb"],
                cost=format_cost(float(item["estimated_cost_usd"])),
                receipts=item["receipt_count"],
                warning=item["failure_or_warning_state"],
                summary=item["human_readable_summary"],
            )
        )

    lines.extend(["", "## Witness references", ""])
    for receipt_id in receipt["witness_receipts"]:
        lines.append(f"- `{receipt_id}`")

    lines.extend(["", "## Human result shape", "", "```text"])
    lines.extend(receipt["human_result_shape"])
    lines.append("```")

    OUTPUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
