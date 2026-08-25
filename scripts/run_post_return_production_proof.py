#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from stegverse.post_return_production_runner import run_post_return_production_proof
from stegverse.release_dependency_alignment import verify_installed_governed_test_dependency_alignment


def _load_release_receipt(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("release receipt must contain a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the coherent successor StegVerse sovereign POST_RETURN production proof."
    )
    parser.add_argument("--release-receipt", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--pre-steggate-bundle", required=True)
    parser.add_argument("--custody-db", required=True)
    parser.add_argument("--state-path", required=True)
    parser.add_argument("--exchange-path", required=True)
    parser.add_argument("--proof-path", required=True)
    parser.add_argument("--consequence-key", default="post_return_production_proof")
    parser.add_argument("--host-identity", default="stegverse-sovereign-local")
    args = parser.parse_args(argv)

    try:
        release_path = Path(args.release_receipt)
        release_receipt = _load_release_receipt(release_path)
        dependency_alignment = verify_installed_governed_test_dependency_alignment(release_receipt)
        if dependency_alignment.get("verified") is not True:
            raise RuntimeError(
                "installed_governed_test_dependency_alignment_failed:"
                + ",".join(dependency_alignment.get("reasons") or [])
            )
        result = run_post_return_production_proof(
            release_receipt_path=release_path,
            manifest_path=Path(args.manifest),
            pre_steggate_bundle_path=Path(args.pre_steggate_bundle),
            custody_db=Path(args.custody_db),
            state_path=Path(args.state_path),
            exchange_path=Path(args.exchange_path),
            proof_path=Path(args.proof_path),
            consequence_key=args.consequence_key,
            host_identity=args.host_identity,
        )
        result["installed_governed_test_dependency_alignment"] = dependency_alignment
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "FAIL_CLOSED",
                    "reason": str(exc),
                    "authority_effect": "NONE",
                    "production_proof_complete": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
