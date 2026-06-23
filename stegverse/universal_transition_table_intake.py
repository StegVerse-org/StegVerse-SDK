"""Universal transition-table intake adapter.

This adapter validates a verified universal transition-table package at the SDK
boundary. It does not execute ingestion, sandbox, runtime, or trust-kernel paths.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class UniversalTransitionTableIntakeError(ValueError):
    """Raised when a universal transition-table package cannot enter SDK intake."""


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise UniversalTransitionTableIntakeError(message)


def handle_universal_transition_table_package(
    package_path: str | Path,
    expected_result_path: str | Path,
    replay_packet_path: str | Path,
) -> dict[str, Any]:
    """Validate a universal transition-table package for SDK intake.

    Returns manifest, intake receipt, and route-eligibility receipt dictionaries.
    The function is intentionally transport-free so CLI, tests, HTTP handlers, or
    ingestion shims can call it without coupling to a runtime.
    """

    package = _read_json(package_path)
    expected = _read_json(expected_result_path)
    replay = _read_json(replay_packet_path)

    package_id = package.get("package_id")
    _require(bool(package_id), "package_id is required")
    _require(expected.get("package_id") == package_id, "expected_result package_id mismatch")
    _require(replay.get("package_id") == package_id, "replay_packet package_id mismatch")
    _require(expected.get("expected_construction_status") == "CONSTRUCTED", "package is not constructed")
    _require(expected.get("expected_route_eligibility") is True, "expected route eligibility is false")
    _require(replay.get("sdk_route_eligible") is True, "replay route eligibility is false")
    _require(not replay.get("blocked_reasons"), "blocked reasons must be empty for SDK intake")
    _require(package.get("human_readable_result_required") is True, "human-readable result is required")
    _require(package.get("machine_replay_required") is True, "machine replay is required")
    _require(bool(package.get("receipt_requirements")), "receipt requirements are required")

    manifest_id = f"uttp-manifest-{package_id}"
    intake_receipt_id = f"uttp-intake-receipt-{package_id}"
    route_receipt_id = f"uttp-route-eligibility-{package_id}"

    manifest = {
        "manifest_id": manifest_id,
        "package_id": package_id,
        "source_package_path": str(package_path),
        "construction_status": expected["expected_construction_status"],
        "route_eligible": True,
        "route_purpose": "UNIVERSAL_TRANSITION_TABLE_TEST",
        "required_receipts": ["intake_receipt", "route_eligibility_receipt"],
    }

    intake_receipt = {
        "receipt_id": intake_receipt_id,
        "package_id": package_id,
        "manifest_id": manifest_id,
        "accepted_for_intake": True,
        "reason": "Verified universal transition-table package accepted at SDK boundary.",
        "next_receipt_required": "route_eligibility_receipt",
    }

    route_eligibility_receipt = {
        "receipt_id": route_receipt_id,
        "package_id": package_id,
        "route_eligible": True,
        "reason": "Package is constructed, route eligible, and has no blocked reasons.",
        "blocked_reasons": [],
    }

    return {
        "manifest": manifest,
        "intake_receipt": intake_receipt,
        "route_eligibility_receipt": route_eligibility_receipt,
    }


__all__ = [
    "UniversalTransitionTableIntakeError",
    "handle_universal_transition_table_package",
]
