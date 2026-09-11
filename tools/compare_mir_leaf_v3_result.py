from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load(path: str) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def compare(expected: dict, observed: dict) -> dict:
    required = ("fixture_id", "leaf_scheme", "tree_profile", "leaf_hashes", "merkle_root", "checkpoint_tip")
    mismatches = []
    missing = []
    for key in required:
        if key not in observed:
            missing.append(key)
            continue
        if observed[key] != expected[key]:
            mismatches.append(key)

    if "proof_status" in observed and observed["proof_status"] not in {"NOT_REQUESTED", "UNAVAILABLE"}:
        mismatches.append("proof_status")
    if "witnesses" in observed and observed["witnesses"] != []:
        mismatches.append("witnesses")

    return {
        "schema": "stegverse.mir-leaf-v3-counterpart-comparison/v1",
        "fixture_id": expected.get("fixture_id"),
        "exact_match": not missing and not mismatches,
        "missing_fields": missing,
        "mismatched_fields": mismatches,
        "authority_effect": "NONE_CONFORMANCE_EVIDENCE_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare an independently produced MIR leaf v3 result to the frozen expected vector.")
    parser.add_argument("observed_result")
    parser.add_argument("--expected", default="fixtures/mir_leaf_v3_conformance_expected_result_v1.json")
    args = parser.parse_args()

    result = compare(_load(args.expected), _load(args.observed_result))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["exact_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
