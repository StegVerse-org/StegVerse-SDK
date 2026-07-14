"""SDK verification for adapter system-boundary declaration round trips.

This module verifies declaration, receipt, and reference consistency. Acceptance is
non-authorizing and does not establish admissibility, custody, standing, or any
consciousness, personhood, or welfare classification.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Mapping

from .system_boundary import validate_system_boundary_declaration

IDENTITY_FIELDS = {
    "schema_version",
    "system_id",
    "surfaces",
    "continuity",
    "authority",
    "claims_boundary",
}


@dataclass(frozen=True)
class SystemBoundaryRoundTripResult:
    accepted: bool
    status: str
    errors: list[str]
    declaration_id: str | None
    receipt_hash: str | None
    non_claims: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "status": self.status,
            "errors": list(self.errors),
            "declaration_id": self.declaration_id,
            "receipt_hash": self.receipt_hash,
            "non_claims": dict(self.non_claims),
        }


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _content_view(declaration: Mapping[str, Any]) -> dict[str, Any]:
    missing = sorted(IDENTITY_FIELDS - set(declaration))
    if missing:
        raise ValueError(f"declaration missing identity fields: {', '.join(missing)}")
    return {key: declaration[key] for key in sorted(IDENTITY_FIELDS)}


def _derive_declaration_id(declaration: Mapping[str, Any]) -> str:
    digest = sha256(_canonical_json(_content_view(declaration)).encode("utf-8")).hexdigest()
    return f"sbd:sha256:{digest}"


def _expected_receipt(
    declaration: Mapping[str, Any], receipt: Mapping[str, Any]
) -> dict[str, Any]:
    content = _content_view(declaration)
    body = {
        "schema_version": "system_boundary_declaration_receipt.v1",
        "declaration_id": _derive_declaration_id(declaration),
        "declaration_hash": f"sha256:{sha256(_canonical_json(content).encode('utf-8')).hexdigest()}",
        "system_id": declaration["system_id"],
        "evidence_refs": list(declaration.get("continuity", {}).get("evidence_refs", [])),
        "source_commit": receipt.get("source_commit"),
        "previous_receipt_hash": receipt.get("previous_receipt_hash"),
        "authority_boundary": {
            "receipt_is_execution_authority": False,
            "receipt_is_admissibility": False,
            "receipt_is_custody": False,
            "declaration_proves_consciousness": False,
        },
    }
    receipt_hash = sha256(_canonical_json(body).encode("utf-8")).hexdigest()
    return {**body, "receipt_hash": f"sha256:{receipt_hash}"}


def validate_system_boundary_round_trip(
    declaration: Mapping[str, Any],
    receipt: Mapping[str, Any],
    reference: Mapping[str, Any],
) -> SystemBoundaryRoundTripResult:
    """Verify an adapter declaration/receipt/reference tuple for SDK ingestion."""

    errors: list[str] = []
    validation = validate_system_boundary_declaration(declaration)
    errors.extend(validation.errors)

    if not isinstance(receipt, Mapping):
        errors.append("system-boundary receipt must be an object")
    if not isinstance(reference, Mapping):
        errors.append("system-boundary reference must be an object")

    declaration_id: str | None = None
    receipt_hash: str | None = None
    if not errors:
        declaration_id = _derive_declaration_id(declaration)
        if declaration.get("declaration_id") != declaration_id:
            errors.append("declaration_id does not match canonical content")

        expected_receipt = _expected_receipt(declaration, receipt)
        if dict(receipt) != expected_receipt:
            errors.append("system-boundary receipt reconstruction mismatch")
        receipt_hash = expected_receipt["receipt_hash"]

        if reference.get("algorithm") != "sha256":
            errors.append("system_boundary_declaration_ref.algorithm must be sha256")
        if reference.get("digest") != expected_receipt["declaration_hash"].removeprefix("sha256:"):
            errors.append("system_boundary_declaration_ref.digest mismatch")
        if reference.get("declaration_id") != declaration_id:
            errors.append("system_boundary_declaration_ref.declaration_id mismatch")
        if reference.get("receipt_hash") != receipt_hash:
            errors.append("system_boundary_declaration_ref.receipt_hash mismatch")
        for key in (
            "authorizing",
            "custody_transferred",
            "admissibility_determined",
            "production_binding_enabled",
        ):
            if reference.get(key) is not False:
                errors.append(f"system_boundary_declaration_ref.{key} must be false")

    non_claims = {
        "sdk_round_trip_is_execution_authority": False,
        "sdk_round_trip_is_admissibility": False,
        "sdk_round_trip_is_custody": False,
        "sdk_round_trip_grants_standing": False,
        "declaration_proves_consciousness": False,
        "production_binding_enabled": False,
    }
    return SystemBoundaryRoundTripResult(
        accepted=not errors,
        status="accepted_for_non_authorizing_receipt_handoff" if not errors else "rejected_fail_closed",
        errors=errors,
        declaration_id=declaration_id,
        receipt_hash=receipt_hash,
        non_claims=non_claims,
    )
