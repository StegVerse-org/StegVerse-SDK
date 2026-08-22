"""Freeze and verify bounded execution-boundary production fixtures.

This module is deliberately non-authorizing. It canonicalizes the externally
agreed examination fixture, validates the minimum n=1 constraints, and binds the
frozen declaration to a stable hash so post-freeze drift is detectable before a
controlled-production run.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from .admissibility import stable_hash

EXECUTION_BOUNDARY_FIXTURE_SCHEMA = (
    "stegverse.governed_admissibility.execution_boundary_fixture.v1"
)

_REQUIRED_EVIDENCE_INTERFACES = tuple(f"E{i}" for i in range(1, 10))


def _required_text(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field}_required")
    return text


def _validate_payload_hash(value: Any) -> str:
    payload_hash = _required_text(value, "payload_hash")
    if not payload_hash.startswith("sha256:"):
        raise ValueError("payload_hash_must_be_sha256")
    return payload_hash


def _normalize_interfaces(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("evidence_interfaces_must_be_a_sequence")
    interfaces = [str(item or "").strip() for item in value]
    if any(not item for item in interfaces):
        raise ValueError("evidence_interface_id_required")
    if len(set(interfaces)) != len(interfaces):
        raise ValueError("evidence_interfaces_must_be_unique")
    if tuple(interfaces) != _REQUIRED_EVIDENCE_INTERFACES:
        raise ValueError("evidence_interfaces_must_equal_E1_through_E9")
    return interfaces


def _canonical_fixture(fixture: Mapping[str, Any]) -> Dict[str, Any]:
    if fixture.get("schema") != EXECUTION_BOUNDARY_FIXTURE_SCHEMA:
        raise ValueError("unexpected_execution_boundary_fixture_schema")

    predicates = fixture.get("frozen_admissibility_predicates")
    if not isinstance(predicates, Mapping) or not predicates:
        raise ValueError("frozen_admissibility_predicates_required")

    if fixture.get("concurrency_prohibited") is not True:
        raise ValueError("concurrency_must_be_prohibited_for_minimum_n1_fixture")

    initial_state = _required_text(fixture.get("initial_required_state"), "initial_required_state")
    intervening_state = _required_text(fixture.get("intervening_state"), "intervening_state")
    if initial_state == intervening_state:
        raise ValueError("intervening_state_must_materially_change")

    canonical: Dict[str, Any] = {
        "schema": EXECUTION_BOUNDARY_FIXTURE_SCHEMA,
        "fixture_id": _required_text(fixture.get("fixture_id"), "fixture_id"),
        "candidate_id": _required_text(fixture.get("candidate_id"), "candidate_id"),
        "candidate_action_type": _required_text(
            fixture.get("candidate_action_type"), "candidate_action_type"
        ),
        "payload_hash": _validate_payload_hash(fixture.get("payload_hash")),
        "target_id": _required_text(fixture.get("target_id"), "target_id"),
        "authority_source_id": _required_text(
            fixture.get("authority_source_id"), "authority_source_id"
        ),
        "frozen_admissibility_predicates": dict(predicates),
        "material_state_variable": _required_text(
            fixture.get("material_state_variable"), "material_state_variable"
        ),
        "initial_required_state": initial_state,
        "intervening_state": intervening_state,
        "state_transition_method": _required_text(
            fixture.get("state_transition_method"), "state_transition_method"
        ),
        "execution_boundary_definition": _required_text(
            fixture.get("execution_boundary_definition"), "execution_boundary_definition"
        ),
        "evidence_interfaces": _normalize_interfaces(fixture.get("evidence_interfaces")),
        "independent_reconstruction_required": fixture.get(
            "independent_reconstruction_required"
        )
        is True,
        "concurrency_prohibited": True,
        "examination_authorizes_execution": False,
        "sdk_authorizes_execution": False,
    }

    if canonical["independent_reconstruction_required"] is not True:
        raise ValueError("independent_reconstruction_must_be_required")

    return canonical


def freeze_execution_boundary_fixture(fixture: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate and bind an examination fixture to an immutable local hash."""
    canonical = _canonical_fixture(fixture)
    frozen = dict(canonical)
    frozen["fixture_hash"] = stable_hash(canonical)
    frozen["frozen"] = True
    return frozen


def verify_frozen_execution_boundary_fixture(fixture: Mapping[str, Any]) -> bool:
    """Return True only when the supplied frozen fixture has not drifted."""
    if fixture.get("frozen") is not True:
        return False
    supplied_hash = str(fixture.get("fixture_hash") or "")
    if not supplied_hash.startswith("sha256:"):
        return False

    try:
        canonical = _canonical_fixture(fixture)
    except (TypeError, ValueError):
        return False
    return supplied_hash == stable_hash(canonical)
