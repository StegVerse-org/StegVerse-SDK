#!/usr/bin/env python3
"""Fail when an artifact is named by its originating framework rather than its capability.

Scans tracked paths and SDK-owned schema identifiers, compares them against the
declared historical baseline, and reports. Non-authorizing: it renames nothing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stegverse.framework_naming_guard import (  # noqa: E402
    evaluate_framework_naming,
    framework_named_paths,
    load_baseline,
    owned_schema_ids,
)

SCANNED_SUFFIXES = (".py", ".json", ".md", ".yml", ".yaml", ".mjs", ".ts", ".js")


def tracked_paths() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    return [line for line in out.splitlines() if line.strip()]


def scan_owned_identifiers(paths: list[str]) -> list[str]:
    found: set[str] = set()
    for rel in paths:
        if not rel.endswith(SCANNED_SUFFIXES):
            continue
        try:
            text = (ROOT / rel).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        found.update(owned_schema_ids(text))
    return sorted(found)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--baseline", default=str(ROOT / "data" / "framework-named-historical-baseline.json")
    )
    parser.add_argument("--json", action="store_true", help="emit the evaluation record")
    parser.add_argument(
        "--strict", action="store_true", help="exit non-zero when not conforming"
    )
    args = parser.parse_args(argv)

    paths = tracked_paths()
    result = evaluate_framework_naming(
        paths=paths,
        owned_identifiers=scan_owned_identifiers(paths),
        baseline=load_baseline(args.baseline),
    )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(
            f"FRAMEWORK_NAMING_GUARD {result['verdict']} "
            f"observed={result['observed_count']} declared={result['declared_count']} "
            f"historical={len(result['historical'])} "
            f"pending_rename={len(result['pending_capability_rename'])}"
        )
        for artifact in result["undeclared"]:
            print(f"  UNDECLARED     {artifact}")
        for artifact in result["stale_baseline_entries"]:
            print(f"  STALE_BASELINE {artifact}")
        if result["required_repair"]:
            print(f"  repair: {result['required_repair']}")

    if args.strict and not result["conforming"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
