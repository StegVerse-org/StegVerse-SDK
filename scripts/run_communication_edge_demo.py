#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from stegverse.communication_edge_demo import run_demo


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the non-authorizing StegVerse communication-edge SDK conformance demo")
    parser.add_argument("packet", nargs="?", default="examples/communication_edge_demo.json")
    args = parser.parse_args()
    packet = json.loads(Path(args.packet).read_text(encoding="utf-8"))
    print(json.dumps(run_demo(packet), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
