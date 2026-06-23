"""CLI wrapper for universal transition-table intake."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .universal_transition_table_intake import handle_universal_transition_table_package


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a universal transition-table package at the SDK boundary."
    )
    parser.add_argument("--package", required=True, help="Path to transition_test_package.json")
    parser.add_argument("--expected", required=True, help="Path to expected_result.json")
    parser.add_argument("--replay", required=True, help="Path to machine_replay_packet.json")
    parser.add_argument("--out", required=False, help="Optional output JSON path")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = handle_universal_transition_table_package(
        args.package,
        args.expected,
        args.replay,
    )
    payload = json.dumps(result, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
