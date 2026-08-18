"""Independent verification helpers for evaluator-boundary evidence.

This module deliberately performs verification only. It grants no runtime,
execution, signing, governance, or custody authority.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


VERIFIER_SCHEMA = "stegverse.evaluation-boundary-verification.v1"
HASH_ALGORITHM = "sha256"
CANONICALIZATION_PROFILE = "stegverse.sdk-canonical-json.v1"


def canonical_json_bytes(value: Any) -> bytes:
    """Return the exact byte representation used by the SDK binding hashes.

    Profile ``stegverse.sdk-canonical-json.v1`` is fixed as UTF-8 JSON with
    object keys sorted, no insignificant whitespace, and non-ASCII characters
    emitted directly. It is intentionally versioned rather than described as
    RFC 8785/JCS.
    """
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def verify_evaluation_boundary_result(
    result: Mapping[str, Any],
    *,
    normalized_manifest: Mapping[str, Any] | None = None,
    governance_request: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify immutable bindings exposed by a sovereign SDK result.

    ``normalized_manifest`` must be the normalized manifest that was submitted.
    ``governance_request`` must be the exact normalized governance request
    retained for the run. Either may be omitted when a reviewer only possesses
    the returned result; omitted checks are reported as ``NOT_PROVIDED`` rather
    than silently passing.
    """
    body = dict(result)
    declared_result_hash = body.pop("result_binding_hash", None)
    computed_result_hash = canonical_sha256(body)

    checks: dict[str, Any] = {
        "result_binding": {
            "status": "PASS" if declared_result_hash == computed_result_hash else "FAIL",
            "declared": declared_result_hash,
            "computed": computed_result_hash,
        }
    }

    if normalized_manifest is None:
        checks["submitted_manifest_binding"] = {"status": "NOT_PROVIDED"}
    else:
        computed = canonical_sha256(normalized_manifest)
        declared = result.get("submitted_manifest_hash")
        checks["submitted_manifest_binding"] = {
            "status": "PASS" if declared == computed else "FAIL",
            "declared": declared,
            "computed": computed,
        }

    if governance_request is None:
        checks["governance_request_binding"] = {"status": "NOT_PROVIDED"}
    else:
        computed = canonical_sha256(governance_request)
        declared = result.get("governance_request_hash")
        checks["governance_request_binding"] = {
            "status": "PASS" if declared == computed else "FAIL",
            "declared": declared,
            "computed": computed,
        }

    supplied = [entry["status"] for entry in checks.values() if entry["status"] != "NOT_PROVIDED"]
    verified = bool(supplied) and all(status == "PASS" for status in supplied)
    complete = all(entry["status"] != "NOT_PROVIDED" for entry in checks.values())

    return {
        "schema": VERIFIER_SCHEMA,
        "hash_algorithm": HASH_ALGORITHM,
        "canonicalization_profile": CANONICALIZATION_PROFILE,
        "verification_complete": complete,
        "verified": verified,
        "checks": checks,
        "authority_granted": False,
    }


def _load_object(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Verify StegVerse evaluator-boundary binding hashes")
    parser.add_argument("result", help="sovereign result JSON")
    parser.add_argument("--manifest", help="normalized submitted manifest JSON")
    parser.add_argument("--governance-request", help="exact normalized governance request JSON")
    args = parser.parse_args(argv)

    report = verify_evaluation_boundary_result(
        _load_object(args.result),
        normalized_manifest=_load_object(args.manifest) if args.manifest else None,
        governance_request=_load_object(args.governance_request) if args.governance_request else None,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
