"""Elyria public-framework translation for the existing governed external-adapter path.

This module is deliberately framework-side only. It does not create an Interlock/InTr
protocol, transport authority, transition authority, credential path, receipt system,
or Master Records custody. Callers inject the transport that reaches an Elyria public
surface; this codec validates and preserves foreign framework evidence.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Mapping


class ElyriaFrameworkAdapterError(ValueError):
    """Raised when Elyria request/response material violates the adapter contract."""


AssessmentTransport = Callable[[Mapping[str, Any]], Mapping[str, Any]]
ReplayTransport = Callable[[str], Mapping[str, Any]]

ELYRIA_VERDICTS = frozenset({"ADMIT", "HOLD", "REFUSE", "NO_PROVABLE_ADMISSION"})
ELYRIA_MOVEMENT_FIELDS = (
    "movement_id",
    "authority_present",
    "authority_scope_valid",
    "standing_active",
    "evidence_present",
    "evidence_sufficient",
    "custody_preserved",
    "refusal_condition_active",
    "revalidation_required",
    "receipt_available",
    "replay_available",
)


def _required_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ElyriaFrameworkAdapterError(f"{field} must be a non-empty string")
    return value


def validate_transition_identity(identity: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(identity, Mapping):
        raise ElyriaFrameworkAdapterError("transition_identity must be a mapping")
    transition_id = _required_nonempty_string(identity.get("transition_id"), "transition_id")
    run_id = _required_nonempty_string(identity.get("run_id"), "run_id")
    normalized = deepcopy(dict(identity))
    normalized["transition_id"] = transition_id
    normalized["run_id"] = run_id
    return normalized


def validate_elyria_movement(movement: Mapping[str, Any]) -> dict[str, Any]:
    """Validate source-native Elyria movement input without synthesizing favorable evidence."""
    if not isinstance(movement, Mapping):
        raise ElyriaFrameworkAdapterError("movement must be a mapping")
    missing = [field for field in ELYRIA_MOVEMENT_FIELDS if field not in movement]
    if missing:
        raise ElyriaFrameworkAdapterError("movement missing required Elyria fields: " + ", ".join(missing))
    _required_nonempty_string(movement.get("movement_id"), "movement_id")
    for field in ELYRIA_MOVEMENT_FIELDS[1:]:
        if not isinstance(movement.get(field), bool):
            raise ElyriaFrameworkAdapterError(f"{field} must be boolean")
    evidence_items = movement.get("evidence_items", [])
    if not isinstance(evidence_items, list):
        raise ElyriaFrameworkAdapterError("evidence_items must be a list when supplied")
    return deepcopy(dict(movement))


def build_elyria_assessment_request(
    movement: Mapping[str, Any], *, transition_identity: Mapping[str, Any]
) -> dict[str, Any]:
    """Build a local adapter envelope while preserving the exact Elyria HTTP body."""
    return {
        "adapter_profile": "stegverse.external-adapter.elyria.v1",
        "framework": "elyria-admission-runtime",
        "operation": "movement_assessment",
        "transition_identity": validate_transition_identity(transition_identity),
        "elyria_http_body": validate_elyria_movement(movement),
        "authority": {
            "adapter_grants_authority": False,
            "foreign_verdict_is_stegverse_admission": False,
            "foreign_receipt_is_master_records_custody": False,
            "route_closure_claim_is_stegverse_observation": False,
        },
    }


def normalize_elyria_assessment_response(
    response: Mapping[str, Any],
    *,
    requested_movement: Mapping[str, Any],
    transition_identity: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(response, Mapping):
        raise ElyriaFrameworkAdapterError("Elyria assessment response must be a mapping")
    request = validate_elyria_movement(requested_movement)
    identity = validate_transition_identity(transition_identity)

    movement_id = _required_nonempty_string(response.get("movement_id"), "response.movement_id")
    if movement_id != request["movement_id"]:
        raise ElyriaFrameworkAdapterError("Elyria movement_id mismatch")

    verdict = _required_nonempty_string(response.get("verdict"), "response.verdict")
    if verdict not in ELYRIA_VERDICTS:
        raise ElyriaFrameworkAdapterError(f"unsupported Elyria verdict {verdict!r}")

    original_input = response.get("original_input")
    if not isinstance(original_input, Mapping):
        raise ElyriaFrameworkAdapterError("Elyria receipt missing original_input")
    if dict(original_input) != request:
        raise ElyriaFrameworkAdapterError("Elyria receipt original_input mismatch")

    receipt_id = _required_nonempty_string(response.get("receipt_id"), "response.receipt_id")
    input_hash = _required_nonempty_string(response.get("input_hash"), "response.input_hash")
    signature = _required_nonempty_string(response.get("signature"), "response.signature")
    signature_algorithm = _required_nonempty_string(
        response.get("signature_algorithm"), "response.signature_algorithm"
    )

    return {
        "adapter_profile": "stegverse.external-adapter.elyria.v1",
        "framework": "elyria-admission-runtime",
        "operation": "movement_assessment",
        "transition_identity": identity,
        "movement_id": movement_id,
        "foreign_verdict": verdict,
        "foreign_receipt_id": receipt_id,
        "foreign_input_hash": input_hash,
        "foreign_signature_algorithm": signature_algorithm,
        "foreign_signature": signature,
        "foreign_receipt": deepcopy(dict(response)),
        "foreign_framework_observation": True,
        "stegverse_admission_determined": False,
        "authority_granted": False,
        "master_records_custody_recorded": False,
        "foreign_signature_verified_by_stegverse": False,
        "authentic_external_transport_observed": False,
    }


def normalize_elyria_replay_response(
    replay: Mapping[str, Any], *, receipt_id: str, transition_identity: Mapping[str, Any]
) -> dict[str, Any]:
    if not isinstance(replay, Mapping):
        raise ElyriaFrameworkAdapterError("Elyria replay response must be a mapping")
    expected_receipt = _required_nonempty_string(receipt_id, "receipt_id")
    actual_receipt = _required_nonempty_string(replay.get("receipt_id"), "replay.receipt_id")
    if actual_receipt != expected_receipt:
        raise ElyriaFrameworkAdapterError("Elyria replay receipt_id mismatch")

    required_checks = (
        "input_hash_matches",
        "verdict_matches",
        "signature_matches",
        "evidence_summary_matches",
    )
    for field in required_checks:
        if not isinstance(replay.get(field), bool):
            raise ElyriaFrameworkAdapterError(f"replay.{field} must be boolean")

    return {
        "adapter_profile": "stegverse.external-adapter.elyria.v1",
        "framework": "elyria-admission-runtime",
        "operation": "receipt_replay",
        "transition_identity": validate_transition_identity(transition_identity),
        "foreign_receipt_id": actual_receipt,
        "foreign_replay": deepcopy(dict(replay)),
        "foreign_replay_all_checks_pass": all(bool(replay[field]) for field in required_checks),
        "stegverse_admission_determined": False,
        "authority_granted": False,
        "master_records_custody_recorded": False,
        "authentic_external_transport_observed": False,
    }


def normalize_elyria_no_bind_proof(
    proof: Mapping[str, Any], *, transition_identity: Mapping[str, Any]
) -> dict[str, Any]:
    """Preserve Elyria no-bind/route-closure claims without upgrading them to observed fact."""
    if not isinstance(proof, Mapping):
        raise ElyriaFrameworkAdapterError("Elyria no-bind proof must be a mapping")
    if proof.get("proof_type") != "elyria_no_bind_proof":
        raise ElyriaFrameworkAdapterError("unsupported Elyria no-bind proof_type")
    if not isinstance(proof.get("movement_attempted"), Mapping):
        raise ElyriaFrameworkAdapterError("no-bind proof missing movement_attempted")
    if not isinstance(proof.get("reason_admission_failed"), list) or not proof.get("reason_admission_failed"):
        raise ElyriaFrameworkAdapterError("no-bind proof missing failure reasons")
    _required_nonempty_string(proof.get("blocked_consequence_path"), "blocked_consequence_path")
    _required_nonempty_string(proof.get("route_closure_state"), "route_closure_state")
    _required_nonempty_string(proof.get("downstream_effect_status"), "downstream_effect_status")

    return {
        "adapter_profile": "stegverse.external-adapter.elyria.v1",
        "framework": "elyria-admission-runtime",
        "operation": "no_bind_evidence",
        "transition_identity": validate_transition_identity(transition_identity),
        "foreign_no_bind_proof": deepcopy(dict(proof)),
        "foreign_route_closure_assertion": proof.get("route_closure_state"),
        "foreign_downstream_effect_assertion": proof.get("downstream_effect_status"),
        "route_closure_observed_by_stegverse": False,
        "downstream_effect_observed_by_stegverse": False,
        "stegverse_admission_determined": False,
        "authority_granted": False,
        "master_records_custody_recorded": False,
    }


@dataclass(frozen=True)
class ElyriaFrameworkAdapter:
    """Dependency-injected Elyria binding for the existing external-adapter shell."""

    assess_transport: AssessmentTransport
    replay_transport: ReplayTransport | None = None

    def assess(
        self, movement: Mapping[str, Any], *, transition_identity: Mapping[str, Any]
    ) -> dict[str, Any]:
        envelope = build_elyria_assessment_request(
            movement, transition_identity=transition_identity
        )
        response = self.assess_transport(envelope["elyria_http_body"])
        return normalize_elyria_assessment_response(
            response,
            requested_movement=envelope["elyria_http_body"],
            transition_identity=envelope["transition_identity"],
        )

    def replay(
        self, receipt_id: str, *, transition_identity: Mapping[str, Any]
    ) -> dict[str, Any]:
        if self.replay_transport is None:
            raise ElyriaFrameworkAdapterError("replay transport is not configured")
        replay = self.replay_transport(receipt_id)
        return normalize_elyria_replay_response(
            replay,
            receipt_id=receipt_id,
            transition_identity=transition_identity,
        )
