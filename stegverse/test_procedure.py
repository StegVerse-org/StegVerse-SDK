"""Self-describing evaluator procedure including route and release context."""
from __future__ import annotations

import argparse
import json
from typing import Any

from .evaluator_contract import evaluator_contract_summary
from .production_release_set import installed_release_set, public_release_catalog


def test_procedure(*, include_catalog: bool = True) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema": "stegverse.evaluator-test-procedure.v1",
        "contract": evaluator_contract_summary(),
        "test_path": [
            "evaluator-authored-public-inspection-request",
            "schema-and-capability-validation",
            "core-lite-manifested-route-carrier",
            "stegcore-steggate-commit-time-evaluation",
            "master-records-exact-run-custody",
            "sdk-return",
        ],
        "submission_command": "stegverse governance --select 0 --input <request.json>",
        "replay_command": "stegverse governance --select 1 --manifest-receipt-id <MR-...>",
        "reconstruction_command": "stegverse governance --select 2 --manifest-receipt-id <MR-...>",
        "installed_production_release_set": installed_release_set(),
        "historical_run_release_set_is_retained": True,
        "replay_compares_original_and_current_release_sets": True,
        "reconstruction_compares_original_and_current_release_sets": True,
        "authority_effect": "NONE",
    }
    if include_catalog:
        payload["current_public_release_catalog"] = public_release_catalog()
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="stegverse test-procedure", description="Show the evaluator test path and production release context")
    parser.add_argument("--offline", action="store_true", help="omit live public release-catalog lookup")
    args = parser.parse_args(argv)
    print(json.dumps(test_procedure(include_catalog=not args.offline), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
