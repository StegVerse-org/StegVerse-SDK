"""CLI for the read-only ecosystem diagnostic SDK processor."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ecosystem_diagnostic_runtime import execute_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stegverse-diagnostic",
        description="Execute one manifested read-only ecosystem diagnostic request through the installed SDK processor.",
    )
    parser.add_argument("--manifest", required=True, help="canonical stegverse.ingress-manifest.v1 JSON")
    parser.add_argument("--output", help="write result JSON; default stdout")
    args = parser.parse_args(argv)

    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        result = execute_manifest(manifest)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
