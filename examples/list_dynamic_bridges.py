"""List registered dynamic admissibility bridges."""

from __future__ import annotations

import json

from stegverse.bridge_registry import bridge_ids, list_dynamic_bridges


def main() -> None:
    payload = {
        "schema": "stegverse.dynamic_admissibility.bridge_registry.v1",
        "bridge_ids": bridge_ids(),
        "bridges": list_dynamic_bridges(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
