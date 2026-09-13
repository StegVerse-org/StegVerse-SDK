"""ELAN -> Interlock/InTr semantic-resolution bridge.

This module intentionally separates transport evidence, observable facts, assertions,
interpretation candidates, and InTr admission. Transport never grants transition
authority by itself.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, List


READY_FOR_INTR_ADMISSION = "READY_FOR_INTR_ADMISSION"
RESOLUTION_REQUIRED = "RESOLUTION_REQUIRED"


@dataclass(frozen=True)
class Candidate:
    id: str
    statement: str
    status: str
    elimination_reasons: List[str]
    consequence_class: str

    @classmethod
    def from_mapping(cls, value: Dict[str, Any]) -> "Candidate":
        return cls(
            id=value["id"],
            statement=value["statement"],
            status=value["status"],
            elimination_reasons=list(value.get("elimination_reasons", [])),
            consequence_class=value["consequence_class"],
        )


class BridgeContractError(ValueError):
    """Raised when an ELAN bridge envelope violates the bridge contract."""


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return sha256(_canonical_json(value)).hexdigest()


def _surviving(candidates: Iterable[Candidate]) -> List[Candidate]:
    return [candidate for candidate in candidates if candidate.status == "SURVIVING"]


def _validate_candidate(candidate: Candidate) -> None:
    if candidate.status not in {"SURVIVING", "ELIMINATED"}:
        raise BridgeContractError(f"unsupported candidate status: {candidate.status}")
    if candidate.status == "ELIMINATED" and not candidate.elimination_reasons:
        raise BridgeContractError(
            f"eliminated candidate {candidate.id} requires an explicit elimination reason"
        )


def evaluate_bridge_envelope(envelope: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate semantic-resolution state before InTr admission.

    The function deliberately does not run governance or mutate InTr state. It only
    determines whether the submitted representation is safe to hand to the existing
    InTr admission boundary.
    """

    if envelope.get("bridge_version") != "elan.intr.bridge.v1":
        raise BridgeContractError("bridge_version must be elan.intr.bridge.v1")

    candidates = [Candidate.from_mapping(item) for item in envelope.get("interpretation_candidates", [])]
    if not candidates:
        raise BridgeContractError("at least one interpretation candidate is required")

    for candidate in candidates:
        _validate_candidate(candidate)

    survivors = _surviving(candidates)
    if not survivors:
        raise BridgeContractError("at least one interpretation candidate must survive")

    expected_resolution = (
        "SINGLE_SURVIVING_INTERPRETATION"
        if len(survivors) == 1
        else "UNRESOLVED_INTERPRETATION_SET"
    )
    if envelope.get("resolution_state") != expected_resolution:
        raise BridgeContractError(
            f"resolution_state {envelope.get('resolution_state')} does not match surviving candidate count"
        )

    consequence_classes = sorted({candidate.consequence_class for candidate in survivors})
    consequence_divergent = len(consequence_classes) > 1

    if consequence_divergent:
        disposition = RESOLUTION_REQUIRED
    else:
        disposition = READY_FOR_INTR_ADMISSION

    normalized = {
        "bridge_version": envelope["bridge_version"],
        "transport_class": envelope["transport_class"],
        "source_framework": envelope["source_framework"],
        "source_instance_id": envelope.get("source_instance_id"),
        "source_event_id": envelope["source_event_id"],
        "observed_at": envelope["observed_at"],
        "payload_sha256": envelope["payload_sha256"],
        "facts": list(envelope.get("facts", [])),
        "assertions": list(envelope.get("assertions", [])),
        "interpretation_candidates": [asdict(candidate) for candidate in candidates],
        "resolution_state": expected_resolution,
        "provenance": list(envelope.get("provenance", [])),
    }

    receipt = {
        "schema": "stegverse.elan-intr-bridge-receipt/v1",
        "input_envelope_sha256": _digest(normalized),
        "transport_class": normalized["transport_class"],
        "surviving_candidate_ids": [candidate.id for candidate in survivors],
        "eliminated_candidates": [
            {"id": candidate.id, "reasons": candidate.elimination_reasons}
            for candidate in candidates
            if candidate.status == "ELIMINATED"
        ],
        "consequence_classes": consequence_classes,
        "consequence_divergent": consequence_divergent,
        "resolution_state": expected_resolution,
        "admission_disposition": disposition,
        "intr_transition_authority_granted": False,
    }
    receipt["output_sha256"] = _digest(receipt)
    return receipt
