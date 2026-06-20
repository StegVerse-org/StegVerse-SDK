#!/usr/bin/env python3
"""Validate StegVerse formal testing route artifacts.

This validator intentionally avoids third-party dependencies so it can run in
minimal SDK and GitHub Actions environments.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"
INGESTION_POINT = "StegVerse-org/StegVerse-SDK"
SHA256_RE = re.compile(r"^sha256:[a-f0-9]{64}$")

ROUTE_REPOSITORIES = {
    "public_demo_validation": "StegVerse-org/stegverse-demo-suite",
    "formal_demo_runner": "StegVerse-org/demo-suite-runner",
    "rigorous_sandbox_testing": "StegGhost/entity-sandbox-runner",
    "standing_proof": "StegVerse-Labs/Standing-Proof-Engine",
    "boundary_glm_case": "StegVerse-Labs/Boundary-Test",
}

RESULT_VALUES = {"PASS", "PARTIAL", "FAIL", "ALLOW", "DENY", "DEFER", "ERROR"}
LOOP_STEPS = [
    "human_input",
    "sdk_or_llm_adapter_intake",
    "stegverse_org_ingestion_outbound",
    "stegghost_ingestion_cge_admission",
    "ephemeral_sandbox_batch",
    "stegghost_ingestion_cge_return_validation",
    "stegverse_org_ingestion_return",
    "human_delivery",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{name} must be an object")
    return value


def require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        fail(f"{name} must be a non-empty string")
    return value


def validate_sha(value: Any, name: str) -> None:
    text = require_string(value, name)
    if not SHA256_RE.match(text):
        fail(f"{name} must match sha256:<64 lowercase hex chars>")


def validate_sdk_intake(intake: dict[str, Any], prefix: str = "sdk_intake") -> None:
    if intake.get("ingestion_point") != INGESTION_POINT:
        fail(f"{prefix}.ingestion_point must be {INGESTION_POINT}")
    validate_sha(intake.get("dataset_manifest_hash"), f"{prefix}.dataset_manifest_hash")
    require_string(intake.get("intake_receipt_id"), f"{prefix}.intake_receipt_id")
    if "intake_receipt_hash" in intake:
        validate_sha(intake.get("intake_receipt_hash"), f"{prefix}.intake_receipt_hash")


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema_version") != SCHEMA_VERSION:
        fail(f"schema_version must be {SCHEMA_VERSION}")

    if manifest.get("ingestion_point") != INGESTION_POINT:
        fail(f"ingestion_point must be {INGESTION_POINT}")

    validate_sha(manifest.get("dataset_manifest_hash"), "dataset_manifest_hash")
    require_string(manifest.get("intake_receipt_id"), "intake_receipt_id")

    if "intake_receipt_hash" in manifest:
        validate_sha(manifest.get("intake_receipt_hash"), "intake_receipt_hash")

    routes = manifest.get("declared_routes")
    if not isinstance(routes, list) or not routes:
        fail("declared_routes must be a non-empty array")

    seen: set[str] = set()
    for index, route_value in enumerate(routes):
        route = require_object(route_value, f"declared_routes[{index}]")
        route_id = require_string(route.get("route_id"), f"declared_routes[{index}].route_id")
        repository = require_string(route.get("repository"), f"declared_routes[{index}].repository")
        require_string(route.get("purpose"), f"declared_routes[{index}].purpose")

        expected_repository = ROUTE_REPOSITORIES.get(route_id)
        if expected_repository is None:
            fail(f"declared_routes[{index}].route_id is not recognized")
        if repository != expected_repository:
            fail(
                f"declared_routes[{index}].repository must be {expected_repository} "
                f"for route_id {route_id}"
            )
        if route.get("route_receipt_required") is not True:
            fail(f"declared_routes[{index}].route_receipt_required must be true")
        if route_id in seen:
            fail(f"duplicate route_id: {route_id}")
        seen.add(route_id)


def validate_result_receipt(receipt: dict[str, Any]) -> None:
    if receipt.get("schema_version") != SCHEMA_VERSION:
        fail(f"schema_version must be {SCHEMA_VERSION}")

    route_id = require_string(receipt.get("route_id"), "route_id")
    repository = require_string(receipt.get("repository"), "repository")
    expected_repository = ROUTE_REPOSITORIES.get(route_id)
    if expected_repository is None:
        fail("route_id is not recognized")
    if repository != expected_repository:
        fail(f"repository must be {expected_repository} for route_id {route_id}")

    validate_sdk_intake(require_object(receipt.get("sdk_intake"), "sdk_intake"))

    result = require_string(receipt.get("result"), "result")
    if result not in RESULT_VALUES:
        fail(f"result must be one of {sorted(RESULT_VALUES)}")

    require_string(receipt.get("route_receipt_id"), "route_receipt_id")
    if "route_receipt_hash" in receipt:
        validate_sha(receipt.get("route_receipt_hash"), "route_receipt_hash")

    evidence = receipt.get("evidence", [])
    if evidence is not None:
        if not isinstance(evidence, list):
            fail("evidence must be an array when present")
        for index, item_value in enumerate(evidence):
            item = require_object(item_value, f"evidence[{index}]")
            require_string(item.get("name"), f"evidence[{index}].name")
            validate_sha(item.get("hash"), f"evidence[{index}].hash")


def validate_testing_loop(loop: dict[str, Any]) -> None:
    if loop.get("schema_version") != SCHEMA_VERSION:
        fail(f"schema_version must be {SCHEMA_VERSION}")
    if loop.get("source") != "human_requester":
        fail("source must be human_requester")
    if loop.get("intake_boundary") not in {"SDK", "LLM Adapter"}:
        fail("intake_boundary must be SDK or LLM Adapter")
    validate_sha(loop.get("dataset_manifest_hash"), "dataset_manifest_hash")
    require_string(loop.get("intake_receipt_id"), "intake_receipt_id")
    if "intake_receipt_hash" in loop:
        validate_sha(loop.get("intake_receipt_hash"), "intake_receipt_hash")
    if loop.get("master_records_required") is not True:
        fail("master_records_required must be true")

    steps = loop.get("loop_steps")
    if not isinstance(steps, list):
        fail("loop_steps must be an array")
    actual_steps = [require_object(step, f"loop_steps[{index}]").get("step_id") for index, step in enumerate(steps)]
    if actual_steps != LOOP_STEPS:
        fail("loop_steps must match the corrected testing data loop order")
    for index, step_value in enumerate(steps):
        step = require_object(step_value, f"loop_steps[{index}]")
        require_string(step.get("actor"), f"loop_steps[{index}].actor")
        require_string(step.get("action"), f"loop_steps[{index}].action")
        if step.get("master_records_receipt_required") is not True:
            fail(f"loop_steps[{index}].master_records_receipt_required must be true")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path, help="Path to route manifest, result receipt, or testing loop JSON")
    parser.add_argument(
        "--kind",
        choices=("manifest", "result", "loop"),
        default="manifest",
        help="Artifact kind to validate. Defaults to manifest.",
    )
    args = parser.parse_args()

    try:
        artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {exc}")
    except OSError as exc:
        fail(f"unable to read artifact: {exc}")

    artifact_obj = require_object(artifact, "artifact")
    if args.kind == "manifest":
        validate_manifest(artifact_obj)
        print("PASS: formal testing route manifest is valid")
    elif args.kind == "result":
        validate_result_receipt(artifact_obj)
        print("PASS: formal testing route result receipt is valid")
    else:
        validate_testing_loop(artifact_obj)
        print("PASS: testing data loop is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
