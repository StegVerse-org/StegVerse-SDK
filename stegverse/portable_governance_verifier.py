from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .interlock_transition import canonical_hash as interlock_hash, validate_interlock_transition
from .interlock_return import validate_interlock_return
from .spe_steggate_bridge import stable_hash

SCHEMA_ID = "stegverse.portable-governance-verification-bundle.v1"
REPORT_SCHEMA_ID = "stegverse.portable-governance-verification-report.v1"
STAGES = {"PRE_STEGGATE", "POST_RETURN"}


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def bundle_hash(value: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _verify_spe(envelope: Mapping[str, Any], receipt: Mapping[str, Any]) -> None:
    candidate = dict(envelope.get("candidate") or {})
    candidate_core = dict(candidate)
    claimed_candidate_hash = candidate_core.pop("candidate_hash", None)
    _require(bool(claimed_candidate_hash), "candidate_hash is required")
    _require(stable_hash(candidate_core) == claimed_candidate_hash, "candidate_hash mismatch")
    _require(envelope.get("candidate_hash") == claimed_candidate_hash, "envelope candidate_hash mismatch")

    envelope_core = dict(envelope)
    claimed_envelope_hash = envelope_core.pop("envelope_hash", None)
    _require(bool(claimed_envelope_hash), "envelope_hash is required")
    _require(stable_hash(envelope_core) == claimed_envelope_hash, "envelope_hash mismatch")

    for field in ("package_id", "transition_id", "run_id", "candidate_hash", "envelope_hash"):
        _require(receipt.get(field) == envelope.get(field), f"SPE receipt {field} mismatch")
    _require(receipt.get("execution_authorized") is False, "SPE receipt cannot authorize execution")
    _require(receipt.get("execution_performed") is False, "SPE receipt cannot claim execution")
    _require(receipt.get("master_record_installed") is False, "SPE receipt cannot claim custody")
    receipt_core = dict(receipt)
    claimed_receipt_hash = receipt_core.pop("receipt_hash", None)
    _require(bool(claimed_receipt_hash), "SPE receipt_hash is required")
    _require(stable_hash(receipt_core) == claimed_receipt_hash, "SPE receipt_hash mismatch")


def verify_portable_governance_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Independently verify portable governance evidence without granting authority."""
    value = dict(bundle)
    _require(value.get("schema") == SCHEMA_ID, "unsupported portable verification bundle schema")
    stage = value.get("stage")
    _require(stage in STAGES, "verification stage is invalid")
    for field in ("package_id", "transition_id", "run_id"):
        _require(bool(str(value.get(field) or "").strip()), f"{field} is required")

    ingress = dict(value.get("ingress_interlock") or {})
    validate_interlock_transition(ingress)
    _require(ingress.get("connection", {}).get("class") == "INTERLOCK", "portable proof requires INTERLOCK ingress")
    ingress_digest = interlock_hash(ingress)

    envelope = dict(value.get("spe_envelope") or {})
    receipt = dict(value.get("spe_receipt") or {})
    _verify_spe(envelope, receipt)

    bridge = dict(value.get("steggate_bridge") or {})
    _require(bridge.get("schema") == "stegverse.sdk.spe-steggate-bridge.v1", "bridge schema mismatch")
    bridge_core = dict(bridge)
    claimed_bridge_hash = bridge_core.pop("bridge_hash", None)
    _require(bool(claimed_bridge_hash), "bridge_hash is required")
    _require(stable_hash(bridge_core) == claimed_bridge_hash, "bridge_hash mismatch")

    for field in ("package_id", "transition_id", "run_id"):
        expected = value[field]
        _require(ingress.get(field) == expected, f"ingress {field} mismatch")
        _require(envelope.get(field) == expected, f"SPE envelope {field} mismatch")
        _require(receipt.get(field) == expected, f"SPE receipt {field} mismatch")
        _require(bridge.get(field) == expected, f"StegGate bridge {field} mismatch")

    _require(bridge.get("interlock", {}).get("ingress_interlock_hash") == ingress_digest, "bridge ingress interlock hash mismatch")
    standing = bridge.get("standing_binding", {})
    _require(standing.get("receipt_hash") == receipt.get("receipt_hash"), "bridge SPE receipt binding mismatch")
    _require(standing.get("candidate_hash") == receipt.get("candidate_hash"), "bridge candidate binding mismatch")
    _require(standing.get("envelope_hash") == receipt.get("envelope_hash"), "bridge envelope binding mismatch")
    _require(standing.get("execution_authorized") is False, "standing binding cannot authorize execution")
    _require(bridge.get("admissibility_candidate", {}).get("decision") == "PENDING", "SDK bridge must not decide admissibility")
    _require(bridge.get("authority", {}).get("sdk_authority") == "NONE", "SDK authority must remain NONE")
    _require(bridge.get("authority", {}).get("execution_authorized") is False, "bridge cannot authorize execution")

    return_record = value.get("interlock_return")
    if stage == "POST_RETURN":
        _require(isinstance(return_record, Mapping), "POST_RETURN requires interlock_return")
        return_value = dict(return_record)
        validate_interlock_return(return_value)
        for field in ("package_id", "transition_id", "run_id"):
            _require(return_value.get(field) == value[field], f"return {field} mismatch")
        _require(return_value.get("binding", {}).get("ingress_interlock_hash") == ingress_digest, "return ingress interlock hash mismatch")
    else:
        _require(return_record is None, "PRE_STEGGATE cannot claim interlock return")

    checks = [
        "INGRESS_INTERLOCK_VALID",
        "SPE_ENVELOPE_HASH_VALID",
        "SPE_RECEIPT_HASH_VALID",
        "IDENTITY_CONTINUITY_VALID",
        "SPE_BINDING_VALID",
        "STEGGATE_BRIDGE_HASH_VALID",
        "AUTHORITY_NON_TRANSFER_VALID",
    ]
    if stage == "POST_RETURN":
        checks.append("INTERLOCK_RETURN_VALID")

    return {
        "schema": REPORT_SCHEMA_ID,
        "status": "PASS",
        "stage": stage,
        "package_id": value["package_id"],
        "transition_id": value["transition_id"],
        "run_id": value["run_id"],
        "bundle_hash": bundle_hash(value),
        "ingress_interlock_hash": ingress_digest,
        "bridge_hash": claimed_bridge_hash,
        "checks": checks,
        "authority": {
            "verification_authority": "NONE",
            "execution_authorized": False,
            "standing_minted": False,
            "admissibility_decided": False,
            "custody_claimed": False,
        },
    }


__all__ = ["SCHEMA_ID", "REPORT_SCHEMA_ID", "STAGES", "bundle_hash", "verify_portable_governance_bundle"]
