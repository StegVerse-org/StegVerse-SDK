#!/usr/bin/env python3
"""Ingest exported workflow observations into a testing data loop status artifact.

The input file is an array of observations:
[
  {
    "repository": "StegVerse-org/StegVerse-SDK",
    "commit": "abc123",
    "workflow_visible": true,
    "conclusion": "success"
  }
]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VISIBLE_CONCLUSIONS = {"success", "failure", "cancelled", "skipped", "timed_out", "action_required"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise SystemExit(f"{name} must be an array")
    return value


def require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SystemExit(f"{name} must be an object")
    return value


def normalize_visibility(observations: list[dict[str, Any]]) -> str:
    if not observations:
        return "unknown"
    visible = [obs.get("workflow_visible") is True for obs in observations]
    if all(visible):
        return "visible"
    if any(visible):
        return "partial"
    return "incomplete"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", required=True, type=Path)
    parser.add_argument("--observations", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    status = require_object(load_json(args.status), "status")
    observations_raw = require_list(load_json(args.observations), "observations")
    observations = [require_object(item, f"observations[{index}]") for index, item in enumerate(observations_raw)]

    by_repo = {item.get("repository"): item for item in status.get("repositories", []) if isinstance(item, dict)}
    for index, observation in enumerate(observations):
        repository = observation.get("repository")
        if not isinstance(repository, str) or not repository:
            raise SystemExit(f"observations[{index}].repository must be a non-empty string")
        if repository not in by_repo:
            raise SystemExit(f"observations[{index}].repository not present in status: {repository}")
        if "commit" in observation and isinstance(observation["commit"], str):
            by_repo[repository]["last_observed_commit"] = observation["commit"]
        if observation.get("workflow_visible") is True:
            by_repo[repository]["combined_status_visible"] = True
        elif observation.get("workflow_visible") is False:
            by_repo[repository]["combined_status_visible"] = False
        conclusion = observation.get("conclusion")
        if conclusion is not None:
            if conclusion not in VISIBLE_CONCLUSIONS:
                raise SystemExit(f"observations[{index}].conclusion is invalid")
            by_repo[repository]["last_observed_conclusion"] = conclusion

    status["ci_status_visibility"] = normalize_visibility(observations)
    if status["ci_status_visibility"] == "visible":
        status["remaining_gap"] = "Workflow status metadata is visible for all observed repositories."
    else:
        status["remaining_gap"] = "Workflow status metadata visibility remains incomplete for one or more repositories."

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
