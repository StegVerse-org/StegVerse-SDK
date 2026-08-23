from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .portable_governance_verifier import verify_portable_governance_bundle


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stegverse-verify-governance",
        description=(
            "Independently verify a StegVerse portable governance evidence bundle "
            "without granting execution, admissibility, standing, or custody authority."
        ),
    )
    parser.add_argument("bundle", help="Path to a portable governance verification bundle JSON file")
    parser.add_argument(
        "--output",
        help="Optional path for the deterministic verification report JSON; stdout is used by default",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        bundle_path = Path(args.bundle)
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        if not isinstance(bundle, dict):
            raise ValueError("bundle JSON root must be an object")
        report = verify_portable_governance_bundle(bundle)
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(
            json.dumps(
                {
                    "schema": "stegverse.portable-governance-verification-report.v1",
                    "status": "FAIL_CLOSED",
                    "authority": {
                        "verification_authority": "NONE",
                        "execution_authorized": False,
                        "standing_minted": False,
                        "admissibility_decided": False,
                        "custody_claimed": False,
                    },
                    "error": str(exc),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
