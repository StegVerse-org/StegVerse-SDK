#!/usr/bin/env python3
"""Validate a StegVerse formal testing route manifest.

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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Path to formal testing route manifest JSON")
    args = parser.parse_args()

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {exc}")
    except OSError as exc:
        fail(f"unable to read manifest: {exc}")

    validate_manifest(require_object(manifest, "manifest"))
    print("PASS: formal testing route manifest is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
