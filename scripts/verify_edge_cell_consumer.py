from __future__ import annotations

import json
from pathlib import Path

from stegverse.edge_cell_consumer import validate_edge_cell_source_binding


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "edge_cell_source_binding.json"


def main() -> int:
    binding = json.loads(FIXTURE.read_text(encoding="utf-8"))
    first = validate_edge_cell_source_binding(binding)
    second = validate_edge_cell_source_binding(binding)

    if not first.accepted:
        print("EDGE_CELL_SDK_CONSUMER_FAIL")
        print(json.dumps(first.to_dict(), indent=2, sort_keys=True))
        return 1
    if first.to_dict() != second.to_dict():
        print("EDGE_CELL_SDK_CONSUMER_FAIL")
        print(json.dumps({"error": "consumer result is not deterministic"}, indent=2))
        return 1
    if first.non_claims != {
        "sdk_acceptance_is_execution_authority": False,
        "sdk_acceptance_is_admissibility": False,
        "sdk_acceptance_is_custody": False,
        "source_receipt_is_destination_custody": False,
        "conditional_capabilities_are_activated": False,
    }:
        print("EDGE_CELL_SDK_CONSUMER_FAIL")
        print(json.dumps({"error": "required non-claims are not preserved"}, indent=2))
        return 1

    print("EDGE_CELL_SDK_CONSUMER_PASS")
    print(json.dumps(first.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
