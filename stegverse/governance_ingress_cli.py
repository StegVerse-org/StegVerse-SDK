"""Credential-free executable entry for SDK governance options 000 and 0B."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from .governance_ingress_runtime import run_000_demo, run_external_manifest


def _load_manifest(path: str) -> Mapping[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"unable to read ingress manifest: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"ingress manifest is not valid JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ValueError("ingress manifest must contain a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m stegverse.governance_ingress_cli",
        description="Execute SDK governance option 000 or 0B through the canonical sovereign runtime",
    )
    parser.add_argument("option", choices=("000", "0B", "0b"))
    parser.add_argument("target", nargs="?", help="stegverse.ingress-manifest.v1 JSON file for option 0B")
    parser.add_argument("--custody-db", default="./stegverse-master-records-validation.db")
    parser.add_argument("--host-identity", default="stegverse-sovereign-local")
    args = parser.parse_args(argv)
    try:
        if args.option == "000":
            if args.target:
                raise ValueError("option 000 does not accept an external target")
            result = run_000_demo(custody_db=args.custody_db, host_identity=args.host_identity)
        else:
            if not args.target:
                raise ValueError("option 0B requires a stegverse.ingress-manifest.v1 JSON file")
            result = run_external_manifest(
                _load_manifest(args.target),
                custody_db=args.custody_db,
                host_identity=args.host_identity,
            )
    except ValueError as exc:
        print(json.dumps({"status": "INVALID_REQUEST", "error": str(exc), "authority_effect": "NONE"}, indent=2, sort_keys=True))
        return 2
    print(json.dumps(dict(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
