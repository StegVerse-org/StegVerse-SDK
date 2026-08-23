from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping

SCHEMA_ID = "stegverse.sdk.spe-steggate-bridge.v1"
CANONICAL_STEGGATE_RUNTIME = "stegverse:steggate:canonical:three-layer:v1"
SPE_RECEIPT_SCHEMA = "stegverse.spe.sdk_commitment_intake.v0.1"
SDK_ENVELOPE_SCHEMA = "stegverse.sdk.spe_commitment_intake.v0.1"
PERMISSION_CONTRACT_ID = "PA-001"
PERMISSION_CONTRACT_VERSION = "1.0.0"
HEX64 = set("0123456789abcdef")


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _required_text(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} is required")
    return text


def _hex_hash(value: Any, name: str) -> str:
    text = _required_text(value, name)
    if len(text) != 64 or any(char not in HEX64 for char in text):
        raise ValueError(f"{name} must be 64 lowercase hex characters")
    return text


def _prefixed_hash(value: Any, name: str) -> str:
    text = _required_text(value, name)
    if not text.startswith("sha256:"):
        raise ValueError(f"{name} must use sha256: prefix")
    _hex_hash(text[7:], name)
    return text


def _parse_time(value: Any, name: str) -> datetime:
    text = _required_text(value, name)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"{name} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return parsed.astimezone(timezone.utc)


def _validate_envelope(envelope: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    value = dict(envelope)
    if value.get("schema_version") != SDK_ENVELOPE_SCHEMA:
        raise ValueError("unsupported SDK SPE envelope schema")
    if value.get("destination_repo") != "StegVerse-Labs/Standing-Proof-Engine":
        raise ValueError("SPE envelope destination mismatch")
    if value.get("route_purpose") != "FRESH_STANDING_DETERMINATION":
        raise ValueError("SPE envelope route purpose mismatch")
    if value.get("receipt_required") is not True:
        raise ValueError("SPE envelope must require receipt")

    candidate = value.get("candidate")
    if not isinstance(candidate, Mapping):
        raise ValueError("SPE envelope candidate must be object")
    candidate_value = dict(candidate)
    if candidate_value.get("authorizing") is not False:
        raise ValueError("SPE candidate must remain non-authorizing")
    if candidate_value.get("requires_fresh_standing_determination") is not True:
        raise ValueError("fresh standing determination must be required")

    candidate_core = dict(candidate_value)
    claimed_candidate_hash = _hex_hash(candidate_core.pop("candidate_hash", None), "candidate_hash")
    if stable_hash(candidate_core) != claimed_candidate_hash:
        raise ValueError("candidate_hash mismatch")
    if value.get("candidate_hash") != claimed_candidate_hash:
        raise ValueError("envelope candidate_hash mismatch")

    envelope_core = dict(value)
    claimed_envelope_hash = _hex_hash(envelope_core.pop("envelope_hash", None), "envelope_hash")
    if stable_hash(envelope_core) != claimed_envelope_hash:
        raise ValueError("envelope_hash mismatch")

    return value, candidate_value


def _validate_receipt(receipt: Mapping[str, Any], envelope: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(receipt)
    if value.get("schema_version") != SPE_RECEIPT_SCHEMA:
        raise ValueError("unsupported SPE standing receipt schema")
    if value.get("receipt_type") != "SPE_STANDING_DETERMINATION":
        raise ValueError("unexpected SPE receipt type")
    if value.get("source_repo") != "StegVerse-org/StegVerse-SDK":
        raise ValueError("SPE receipt source mismatch")
    if value.get("destination_repo") != "StegVerse-Labs/Standing-Proof-Engine":
        raise ValueError("SPE receipt destination mismatch")

    for field in ("package_id", "transition_id", "run_id", "candidate_hash", "envelope_hash"):
        if value.get(field) != envelope.get(field):
            raise ValueError(f"SPE receipt {field} mismatch")

    result = value.get("standing_result")
    if result not in {"ALLOW", "DENY", "FAIL_CLOSED"}:
        raise ValueError("SPE standing_result is invalid")
    if value.get("execution_authorized") is not False:
        raise ValueError("SPE receipt cannot authorize execution")
    if value.get("execution_performed") is not False:
        raise ValueError("SPE receipt cannot claim execution")
    if value.get("master_record_installed") is not False:
        raise ValueError("SPE receipt cannot claim Master Records custody")
    expected_next = "GOVERNED_EXECUTION_AUTHORITY" if result == "ALLOW" else None
    if value.get("next_boundary") != expected_next:
        raise ValueError("SPE receipt next_boundary mismatch")

    receipt_core = dict(value)
    claimed_receipt_hash = _hex_hash(receipt_core.pop("receipt_hash", None), "receipt_hash")
    if stable_hash(receipt_core) != claimed_receipt_hash:
        raise ValueError("SPE receipt_hash mismatch")
    return value


def _standing_current(candidate: Mapping[str, Any], observed_at: str) -> bool:
    observed = _parse_time(observed_at, "observed_at")
    window = candidate.get("validity_window")
    if not isinstance(window, Mapping):
        raise ValueError("candidate validity_window must be object")
    not_before = window.get("not_before")
    not_after = window.get("not_after")
    if not_before is not None and observed < _parse_time(not_before, "validity_window.not_before"):
        return False
    if not_after is not None and observed > _parse_time(not_after, "validity_window.not_after"):
        return False
    return True


def build_steggate_request_candidate(
    envelope: Mapping[str, Any],
    receipt: Mapping[str, Any],
    *,
    interlock_context: Mapping[str, Any],
    observed_at: str,
    three_layer_request: Mapping[str, Any],
    permission_predicates: Mapping[str, Any],
) -> dict[str, Any]:
    """Verify SPE return and build a non-authorizing canonical StegGate request candidate."""
    envelope_value, candidate = _validate_envelope(envelope)
    receipt_value = _validate_receipt(receipt, envelope_value)

    for field in ("package_id", "transition_id", "run_id"):
        if interlock_context.get(field) != envelope_value.get(field):
            raise ValueError(f"interlock {field} mismatch")
    ingress_interlock_hash = _prefixed_hash(
        interlock_context.get("ingress_interlock_hash"), "interlock_context.ingress_interlock_hash"
    )

    if receipt_value["standing_result"] != "ALLOW":
        raise ValueError("SPE standing does not allow progression to StegGate")
    if not _standing_current(candidate, observed_at):
        raise ValueError("SPE standing validity window is not current")

    request = dict(three_layer_request)
    required_request_fields = {
        "judgment_conditions",
        "signal_admission",
        "execution_boundary",
        "action",
        "target",
        "scope",
    }
    if not required_request_fields.issubset(request):
        raise ValueError("three_layer_request is incomplete")
    for field in ("judgment_conditions", "signal_admission", "execution_boundary"):
        if not isinstance(request.get(field), Mapping):
            raise ValueError(f"three_layer_request.{field} must be object")
    for field in ("action", "target", "scope"):
        _required_text(request.get(field), f"three_layer_request.{field}")

    predicates = dict(permission_predicates)
    required_predicates = (
        "authority_current",
        "continuity_current",
        "governing_conditions_current",
        "consequence_attributable",
        "consequence_reconstructable",
    )
    for field in required_predicates:
        if not isinstance(predicates.get(field), bool):
            raise ValueError(f"permission_predicates.{field} must be boolean")
    if predicates.get("consent_or_standing_required") is not True:
        raise ValueError("SPE bridge requires consent_or_standing_required=true")
    if "consent_or_standing_current" in predicates:
        raise ValueError("consent_or_standing_current is derived from verified SPE standing")

    observed = _parse_time(observed_at, "observed_at").isoformat()
    receipt_hash = receipt_value["receipt_hash"]
    bridge_core = {
        "schema": SCHEMA_ID,
        "package_id": envelope_value["package_id"],
        "transition_id": envelope_value["transition_id"],
        "run_id": envelope_value["run_id"],
        "interlock": {
            "ingress_interlock_hash": ingress_interlock_hash,
            "participant_id": _required_text(interlock_context.get("participant_id"), "interlock_context.participant_id"),
        },
        "standing_binding": {
            "receipt_hash": receipt_hash,
            "candidate_hash": receipt_value["candidate_hash"],
            "envelope_hash": receipt_value["envelope_hash"],
            "standing_result": "ALLOW",
            "standing_current": True,
            "observed_at": observed,
            "execution_authorized": False,
        },
        "admissibility_candidate": {
            "runtime_identity": CANONICAL_STEGGATE_RUNTIME,
            "permission_contract": {
                "contract_id": PERMISSION_CONTRACT_ID,
                "version": PERMISSION_CONTRACT_VERSION,
            },
            "permission_predicates": {
                **predicates,
                "consent_or_standing_current": True,
            },
            "three_layer_request": request,
            "three_layer_request_hash": stable_hash(request),
            "decision": "PENDING",
        },
        "authority": {
            "sdk_authority": "NONE",
            "spe_execution_authority": "NONE",
            "steggate_decision_authority": "CANONICAL_RUNTIME_ONLY",
            "execution_authorized": False,
            "master_records_custody_claimed": False,
        },
    }
    return {**bridge_core, "bridge_hash": stable_hash(bridge_core)}


__all__ = [
    "SCHEMA_ID",
    "CANONICAL_STEGGATE_RUNTIME",
    "PERMISSION_CONTRACT_ID",
    "PERMISSION_CONTRACT_VERSION",
    "stable_hash",
    "build_steggate_request_candidate",
]
