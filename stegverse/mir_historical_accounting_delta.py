from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

RUN2_TEST_ID = "MIR-STEGVERSE-HISTORICAL-ACCOUNTING-RUN-002"
EXPECTED_ARTIFACT_SCHEMA = "stegverse.mir-node-mirror.accounting/v2"
DELTA_SCHEMA = "stegverse.sdk.mir-historical-accounting-delta/v1"


class MirHistoricalAccountingDeltaError(RuntimeError):
    pass


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise MirHistoricalAccountingDeltaError(reason)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def evaluate_mir_historical_accounting_delta(
    *,
    manifest: Mapping[str, Any],
    history: Sequence[Mapping[str, Any]],
    response_to: str,
    artifact: Mapping[str, Any],
    revision: int = 1,
) -> dict[str, Any]:
    """Compare a returned MIR historical-accounting artifact to the original Run-2 evidence.

    This function evaluates equality/delta only. MIR evidence remains historical accounting
    and does not acquire StegVerse governance, transition, or publication authority.
    """
    _require(isinstance(manifest, Mapping), "manifest_required")
    _require(isinstance(history, Sequence) and not isinstance(history, (str, bytes, bytearray)), "history_required")
    history_value = [dict(item) for item in history if isinstance(item, Mapping)]
    _require(len(history_value) == len(history), "history_event_invalid")
    _require(isinstance(response_to, str) and bool(response_to.strip()), "response_to_required")
    _require(isinstance(revision, int) and not isinstance(revision, bool) and revision >= 1, "revision_invalid")
    _require(isinstance(artifact, Mapping), "artifact_required")
    _require(artifact.get("schema") == EXPECTED_ARTIFACT_SCHEMA, "artifact_schema_invalid")
    _require(artifact.get("authority_namespace_effect") == "NONE", "mir_artifact_authority_effect_forbidden")

    binding = artifact.get("binding")
    accounting = artifact.get("accounting")
    _require(isinstance(binding, Mapping), "artifact_binding_required")
    _require(isinstance(accounting, Mapping), "artifact_accounting_required")

    expected_manifest_hash = _sha256(dict(manifest))
    expected_history_hash = _sha256(history_value)
    expected_event_hashes = [_sha256(item) for item in history_value]
    expected_event_count = len(history_value)

    binding_checks = {
        "test_id": {
            "expected": RUN2_TEST_ID,
            "observed": binding.get("test_id"),
            "match": binding.get("test_id") == RUN2_TEST_ID,
        },
        "revision": {
            "expected": revision,
            "observed": binding.get("revision"),
            "match": binding.get("revision") == revision,
        },
        "response_to": {
            "expected": response_to,
            "observed": binding.get("response_to"),
            "match": binding.get("response_to") == response_to,
        },
        "manifest_hash": {
            "expected": expected_manifest_hash,
            "observed": binding.get("manifest_hash"),
            "match": binding.get("manifest_hash") == expected_manifest_hash,
        },
        "response_class": {
            "expected": "MIR_HISTORICAL_ACCOUNTING",
            "observed": binding.get("response_class"),
            "match": binding.get("response_class") == "MIR_HISTORICAL_ACCOUNTING",
        },
    }

    accounting_checks = {
        "history_sha256": {
            "expected": expected_history_hash,
            "observed": accounting.get("history_sha256"),
            "match": accounting.get("history_sha256") == expected_history_hash,
        },
        "event_count": {
            "expected": expected_event_count,
            "observed": accounting.get("event_count"),
            "match": accounting.get("event_count") == expected_event_count,
        },
        "event_hashes": {
            "expected": expected_event_hashes,
            "observed": accounting.get("event_hashes"),
            "match": accounting.get("event_hashes") == expected_event_hashes,
        },
    }

    mismatches: list[dict[str, Any]] = []
    for domain, checks in (("binding", binding_checks), ("accounting", accounting_checks)):
        for field, check in checks.items():
            if check["match"] is not True:
                mismatches.append({
                    "domain": domain,
                    "field": field,
                    "expected": check["expected"],
                    "observed": check["observed"],
                })

    exact_match = not mismatches
    return {
        "schema": DELTA_SCHEMA,
        "test_id": RUN2_TEST_ID,
        "response_to": response_to,
        "revision": revision,
        "state": "EXACT_MATCH" if exact_match else "DELTA_OBSERVED",
        "exact_match": exact_match,
        "binding_checks": binding_checks,
        "accounting_checks": accounting_checks,
        "mismatches": mismatches,
        "mismatch_count": len(mismatches),
        "original": {
            "manifest_hash": expected_manifest_hash,
            "history_sha256": expected_history_hash,
            "event_count": expected_event_count,
            "event_hashes": expected_event_hashes,
        },
        "returned_accounting": dict(accounting),
        "record_role": artifact.get("record_role"),
        "mir_evidence_authority": "HISTORICAL_ACCOUNTING_ONLY",
        "stegverse_governance_authority_transferred": False,
        "authority_effect": "NONE_DELTA_EVALUATION_ONLY",
    }


__all__ = [
    "DELTA_SCHEMA",
    "MirHistoricalAccountingDeltaError",
    "RUN2_TEST_ID",
    "evaluate_mir_historical_accounting_delta",
]
