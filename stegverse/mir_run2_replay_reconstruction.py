from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from stegverse.mir_historical_accounting_delta import (
    DELTA_SCHEMA,
    RUN2_TEST_ID,
    evaluate_mir_historical_accounting_delta,
)

REPLAY_SCHEMA = "stegverse.sdk.mir-run2-replay/v1"
RECONSTRUCTION_SCHEMA = "stegverse.sdk.mir-run2-reconstruction/v1"


class MirRun2ReplayReconstructionError(RuntimeError):
    pass


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise MirRun2ReplayReconstructionError(reason)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def replay_run2_delta(
    *,
    manifest: Mapping[str, Any],
    history: Sequence[Mapping[str, Any]],
    response_to: str,
    artifact: Mapping[str, Any],
    prior_delta: Mapping[str, Any],
    revision: int = 1,
) -> dict[str, Any]:
    _require(prior_delta.get("schema") == DELTA_SCHEMA, "prior_delta_schema_invalid")
    replayed = evaluate_mir_historical_accounting_delta(
        manifest=manifest,
        history=history,
        response_to=response_to,
        artifact=artifact,
        revision=revision,
    )
    prior_digest = _sha(dict(prior_delta))
    replay_digest = _sha(replayed)
    equivalent = replayed == dict(prior_delta)
    return {
        "schema": REPLAY_SCHEMA,
        "test_id": RUN2_TEST_ID,
        "response_to": response_to,
        "revision": revision,
        "state": "REPLAY_MATCH" if equivalent else "REPLAY_DIVERGENCE",
        "equivalent": equivalent,
        "prior_delta_digest": prior_digest,
        "replayed_delta_digest": replay_digest,
        "replayed_delta": replayed,
        "authority_effect": "NONE_REPLAY_EVIDENCE_ONLY",
    }


def reconstruct_run2_history(
    *,
    history: Sequence[Mapping[str, Any]],
    artifact: Mapping[str, Any],
) -> dict[str, Any]:
    _require(isinstance(history, Sequence) and not isinstance(history, (str, bytes, bytearray)), "history_required")
    events = [dict(item) for item in history if isinstance(item, Mapping)]
    _require(len(events) == len(history), "history_event_invalid")
    accounting = artifact.get("accounting")
    _require(isinstance(accounting, Mapping), "artifact_accounting_required")

    reconstructed_hashes = [_sha(item) for item in events]
    expected_hashes = accounting.get("event_hashes")
    ordered_match = expected_hashes == reconstructed_hashes
    history_hash_match = accounting.get("history_sha256") == _sha(events)
    count_match = accounting.get("event_count") == len(events)
    complete = ordered_match and history_hash_match and count_match

    return {
        "schema": RECONSTRUCTION_SCHEMA,
        "test_id": RUN2_TEST_ID,
        "state": "RECONSTRUCTED_EXACT" if complete else "RECONSTRUCTION_DELTA",
        "exact": complete,
        "event_count": len(events),
        "reconstructed_event_hashes": reconstructed_hashes,
        "ordered_event_hashes_match": ordered_match,
        "history_hash_match": history_hash_match,
        "event_count_match": count_match,
        "reconstructed_history_sha256": _sha(events),
        "source_accounting_tip": accounting.get("tip"),
        "authority_effect": "NONE_RECONSTRUCTION_EVIDENCE_ONLY",
    }


__all__ = [
    "RECONSTRUCTION_SCHEMA",
    "REPLAY_SCHEMA",
    "MirRun2ReplayReconstructionError",
    "reconstruct_run2_history",
    "replay_run2_delta",
]
