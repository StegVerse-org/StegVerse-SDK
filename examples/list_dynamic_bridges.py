"""List registered dynamic admissibility bridges."""

from __future__ import annotations

import json
from typing import Any, Dict

from stegverse.bridge_registry import bridge_ids, list_dynamic_bridges

BRIDGE_REGISTRY_SCHEMA = "stegverse.dynamic_admissibility.bridge_registry.v1"


def build_payload() -> Dict[str, Any]:
    return {
        "schema": BRIDGE_REGISTRY_SCHEMA,
        "bridge_ids": bridge_ids(),
        "bridges": list_dynamic_bridges(),
    }


def main() -> None:
    print(json.dumps(build_payload(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
