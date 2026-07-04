#!/usr/bin/env python3
"""Verify SDK micro-node governed return-path fixture compatibility."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stegverse.micro_node_return_path import validate_micro_node_return_path

DEFAULT_REQUEST = ROOT / "examples" / "micro_node_return_path" / "request.json"
DEFAULT_RETURN = ROOT / "examples" / "micro_node_return_path" / "governed_return.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, default=DEFAULT_REQUEST)
    parser.add_argument("--governed-return", type=Path, default=DEFAULT_RETURN)
    args = parser.parse_args()

    decision = validate_micro_node_return_path(read_json(args.request), read_json(args.governed_return))
    print(json.dumps(decision.to_dict(), indent=2, sort_keys=True))
    if decision.decision != "ALLOW":
        print("MICRO_NODE_RETURN_PATH_SDK_FAIL")
        return 1
    print("MICRO_NODE_RETURN_PATH_SDK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
