#!/usr/bin/env python3
"""Validate the StegVerse universal entry envelope and core routing invariants."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover
    raise SystemExit("jsonschema is required: python -m pip install jsonschema") from exc

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "universal-entry-envelope.schema.v0.1.json"
DEFAULT_PACKET = ROOT / "examples" / "universal_entry" / "site_chat_good_morning.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level JSON value must be an object")
    return value


def validate_invariants(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    routing = packet["routing"]
    request = packet["request"]
    receipt = packet["receipt"]
    authority = packet["authority"]

    allowed = set(routing["allowed_lanes"])
    selected = set(routing["selected_lanes"])
    requested = set(request["requested_capabilities"])

    if not selected.issubset(allowed):
        errors.append("selected_lanes must be a subset of allowed_lanes")
    if routing["selection_status"] in {"ROUTED", "COMPLETED"} and not selected:
        errors.append("ROUTED or COMPLETED envelopes require at least one selected lane")
    if "external_llm" in selected and not request["external_information_allowed"]:
        errors.append("external_llm cannot be selected when external_information_allowed is false")
    if "execution" in selected and authority["execution_authority_granted"] is not False:
        errors.append("universal entry intake must not grant execution authority")
    if "execution" in selected and "execution" not in receipt["expected_types"]:
        errors.append("execution routing requires an expected execution receipt")
    if receipt["required"] and not receipt["expected_types"]:
        errors.append("required receipts must declare at least one expected type")
    if not requested.issubset(allowed):
        errors.append("requested_capabilities must be a subset of allowed_lanes")
    if routing["selection_status"] == "FAILED_CLOSED" and selected:
        errors.append("FAILED_CLOSED envelopes must not select capability lanes")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", nargs="?", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    args = parser.parse_args()

    schema = load_json(args.schema)
    packet = load_json(args.packet)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(packet, schema)

    errors = validate_invariants(packet)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print(f"PASS: {args.packet}")
    print(f"entry_point={packet['origin']['entry_point']}")
    print(f"selected_lanes={','.join(packet['routing']['selected_lanes'])}")
    print(f"receipt_required={str(packet['receipt']['required']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
