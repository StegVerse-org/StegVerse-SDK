"""Installed CLI for the non-authorizing communication-edge SDK demo."""

from __future__ import annotations

import argparse
import json
from importlib import resources
from pathlib import Path
from typing import Any, Dict

from .communication_edge_demo import run_demo


def _load_packet(path: str | None) -> Dict[str, Any]:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    text = resources.files("stegverse.demo_data").joinpath("communication_edge_demo.json").read_text(encoding="utf-8")
    return json.loads(text)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="stegverse-comm-demo",
        description="Run the non-authorizing StegVerse communication-edge SDK conformance demo",
    )
    parser.add_argument(
        "packet",
        nargs="?",
        help="Optional JSON capability packet. If omitted, use the packaged deterministic demo packet.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit compact canonical-style JSON instead of indented output.",
    )
    args = parser.parse_args()
    result = run_demo(_load_packet(args.packet))
    if args.compact:
        print(json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    else:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
