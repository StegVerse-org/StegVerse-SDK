"""Run the neutral cross-system IW falsifier suite against observed architecture outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from stegverse.iw_matrix_falsifier import (
    evaluate_irreversible_early_commit_falsifier,
    evaluate_temporal_order_falsifier,
)

SUITE_SCHEMA = "stegverse.iw-cross-system-falsifier-suite.v0.1"
RESULT_SCHEMA = "stegverse.iw-cross-system-falsifier-suite-result.v0.1"


def evaluate_suite(suite: Mapping[str, Any], observed: Mapping[str, Any]) -> dict[str, Any]:
    if suite.get("schema") != SUITE_SCHEMA:
        raise ValueError("unsupported_suite_schema")
    cases = suite.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("suite_cases_required")
    observed_cases = observed.get("cases")
    if not isinstance(observed_cases, Mapping):
        raise ValueError("observed_cases_required")

    results = []
    for case in cases:
        fid = str(case.get("falsifier_id") or "")
        cid = str(case.get("case_id") or "")
        if cid not in observed_cases:
            raise ValueError(f"missing_observed_case:{cid}")
        obs = observed_cases[cid]
        if not isinstance(obs, Mapping):
            raise ValueError(f"observed_case_must_be_object:{cid}")

        if fid == "IW-FALSIFIER-001":
            expected_runs = case["runs"]
            obs_runs = obs.get("runs")
            if not isinstance(obs_runs, list) or len(obs_runs) != len(expected_runs):
                raise ValueError(f"observed_run_count_mismatch:{cid}")
            merged_runs = []
            for expected, actual in zip(expected_runs, obs_runs):
                if expected["run_id"] != actual.get("run_id"):
                    raise ValueError(f"observed_run_id_mismatch:{cid}")
                if expected["arrival_order"] != actual.get("arrival_order"):
                    raise ValueError(f"arrival_order_changed:{cid}:{expected['run_id']}")
                merged_runs.append({
                    "run_id": expected["run_id"],
                    "arrival_order": expected["arrival_order"],
                    "committed_action": actual.get("committed_action"),
                })
            result = evaluate_temporal_order_falsifier({
                "case_id": cid,
                "governed_input_hash": case["governed_input_hash"],
                "candidate_set_hash": case["candidate_set_hash"],
                "order_is_explicit_governed_input": case["order_is_explicit_governed_input"],
                "runs": merged_runs,
            })
        elif fid == "IW-FALSIFIER-002":
            p = case["preconditions"]
            result = evaluate_irreversible_early_commit_falsifier({
                "case_id": cid,
                "lane_committed_action": obs.get("lane_committed_action"),
                "matrix_resolved_action": case["test_oracle_matrix_action"],
                "lane_local_checks_all_passed": p["lane_local_checks_all_passed"],
                "coupled_information_existed_before_boundary": p["coupled_information_existed_before_boundary"],
                "coupled_information_within_declared_scope": p["coupled_information_within_declared_scope"],
                "matrix_resolution_unique": p["matrix_resolution_unique"],
                "lane_crossed_action_boundary": p["lane_crossed_action_boundary"],
                "consequence_irreversible": p["consequence_irreversible"],
            })
        else:
            raise ValueError(f"unsupported_falsifier_id:{fid}")
        results.append(result)

    return {
        "schema": RESULT_SCHEMA,
        "suite_id": suite.get("suite_id"),
        "results": results,
        "architecture_falsified": any(r.get("architecture_falsified") is True for r in results),
        "boundary": {
            "sdk_runner_is_governance_authority": False,
            "sdk_runner_executes_actions": False,
            "counterpart_result_consumed_before_own_run": False,
        },
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("suite")
    parser.add_argument("observed")
    parser.add_argument("--output")
    args = parser.parse_args()

    suite = json.loads(Path(args.suite).read_text())
    observed = json.loads(Path(args.observed).read_text())
    result = evaluate_suite(suite, observed)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(payload)
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
