"""Release-set-aware wrapper around the canonical sovereign validation runtime.

The underlying governance, route, receipt, and custody implementations are not
replaced.  This wrapper only binds immutable production component provenance into
new run evidence and reports historical-vs-current release-set differences during
replay and reconstruction.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from .production_release_set import compare_release_sets, installed_release_set
from .public_inspection import load_public_inspection_request
from . import sovereign_validation_runtime as canonical

RELEASE_SET_METADATA_KEY = "production_release_set"


def _merged_consequence_metadata(
    consequence_metadata: Mapping[str, Any] | None,
    release_set: Mapping[str, Any],
) -> dict[str, Any]:
    merged = dict(consequence_metadata or {})
    merged[RELEASE_SET_METADATA_KEY] = dict(release_set)
    merged["production_release_set_is_authority"] = False
    return merged


def run_sovereign_validation(
    request: Mapping[str, Any],
    *,
    custody_db: str | Path,
    host_identity: str = "stegverse-sovereign-local",
    consequence_executor=None,
    consequence_metadata: Mapping[str, Any] | None = None,
    route_source: str = "StegVerse-SDK:sovereign-validation",
    route_purpose: str = "production-lane-evaluator-validation",
) -> dict[str, Any]:
    release_set = installed_release_set()
    result = dict(canonical.run_sovereign_validation(
        request,
        custody_db=custody_db,
        host_identity=host_identity,
        consequence_executor=consequence_executor,
        consequence_metadata=_merged_consequence_metadata(consequence_metadata, release_set),
        route_source=route_source,
        route_purpose=route_purpose,
    ))
    result["production_release_set"] = release_set
    result["production_release_set_retained_with_exact_run"] = True
    result["production_release_set_is_authority"] = False
    return result


def _historical_release_set(manifest_receipt_id: str, custody_db: str | Path) -> dict[str, Any] | None:
    (_Carrier, _build, _route, Custody, _submit, _Registry, _Request, _eval, _Ledger, _run) = canonical._components()
    custody = Custody(custody_db)
    rid = manifest_receipt_id.strip().upper()
    package = custody.evidence_package(rid)["evidence_package"]
    metadata = ((package.get("manifest") or {}).get("metadata") or {})
    bounded = metadata.get("bounded_consequence") if isinstance(metadata, Mapping) else None
    if not isinstance(bounded, Mapping):
        return None
    value = bounded.get(RELEASE_SET_METADATA_KEY)
    return dict(value) if isinstance(value, Mapping) else None


def replay_sovereign(manifest_receipt_id: str, *, custody_db: str | Path) -> dict[str, Any]:
    original_release_set = _historical_release_set(manifest_receipt_id, custody_db)
    current_release_set = installed_release_set()
    artifact = dict(canonical.replay_sovereign(manifest_receipt_id, custody_db=custody_db))
    artifact["original_production_release_set"] = original_release_set
    artifact["current_production_release_set"] = current_release_set
    artifact["production_release_set_comparison"] = compare_release_sets(original_release_set, current_release_set)
    artifact["historical_release_set_available"] = original_release_set is not None
    return artifact


def reconstruct_sovereign(manifest_receipt_id: str, *, custody_db: str | Path) -> dict[str, Any]:
    original_release_set = _historical_release_set(manifest_receipt_id, custody_db)
    current_release_set = installed_release_set()
    artifact = dict(canonical.reconstruct_sovereign(manifest_receipt_id, custody_db=custody_db))
    artifact["original_production_release_set"] = original_release_set
    artifact["current_production_release_set"] = current_release_set
    artifact["production_release_set_comparison"] = compare_release_sets(original_release_set, current_release_set)
    artifact["historical_release_set_available"] = original_release_set is not None
    return artifact


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Canonical StegVerse production validation with immutable production release-set evidence")
    parser.add_argument("operation", choices=("run", "replay", "reconstruct"))
    parser.add_argument("target")
    parser.add_argument("--custody-db", default="./stegverse-master-records-validation.db")
    parser.add_argument("--host-identity", default="stegverse-sovereign-local")
    args = parser.parse_args(argv)
    if args.operation == "run":
        result = run_sovereign_validation(load_public_inspection_request(args.target), custody_db=args.custody_db, host_identity=args.host_identity)
    elif args.operation == "replay":
        result = replay_sovereign(args.target, custody_db=args.custody_db)
    else:
        result = reconstruct_sovereign(args.target, custody_db=args.custody_db)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
