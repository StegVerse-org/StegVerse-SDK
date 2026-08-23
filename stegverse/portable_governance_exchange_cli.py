from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .portable_governance_exchange import (
    PortableGovernanceExchangeError,
    create_exchange,
    extract_bundle,
    verify_exchange,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stegverse-governance-exchange",
        description="Create, verify, or extract a bounded portable governance evidence exchange archive.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Verify a governance bundle and package it for independent sharing")
    create.add_argument("bundle", help="Path to stegverse.portable-governance-verification-bundle.v1 JSON")
    create.add_argument("archive", help="Destination .zip path")

    verify = sub.add_parser("verify", help="Verify archive hashes and independently reproduce the governance report")
    verify.add_argument("archive", help="Exchange .zip path")

    extract = sub.add_parser("extract", help="Verify first, then extract the bounded evidence files")
    extract.add_argument("archive", help="Exchange .zip path")
    extract.add_argument("destination", help="Empty destination directory")
    return parser


def _load_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PortableGovernanceExchangeError("bundle_json_root_must_be_object")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "create":
            result = create_exchange(_load_object(Path(args.bundle)), Path(args.archive))
        elif args.command == "verify":
            result = verify_exchange(Path(args.archive))
        else:
            result = extract_bundle(Path(args.archive), Path(args.destination))
    except (OSError, json.JSONDecodeError, ValueError, TypeError, PortableGovernanceExchangeError) as exc:
        print(json.dumps({
            "schema": "stegverse.portable-governance-evidence-exchange-error.v1",
            "status": "FAIL_CLOSED",
            "error": str(exc),
            "authority_effect": "NONE",
            "custody_installed": False,
        }, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
