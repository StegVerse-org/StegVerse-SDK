from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TERMS_RECEIPT_SCHEMA = "stegverse.sdk.demo-terms-acceptance-receipt.v1"
TERMS_OF_SERVICE_VERSION = "1.0.0"
TERMS_OF_USE_VERSION = "1.0.0"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def _terms_root() -> Path:
    return Path(__file__).resolve().parents[1] / "legal" / "demo"


def current_demo_terms_descriptor() -> dict[str, Any]:
    root = _terms_root()
    tos = root / "DEMO_TERMS_OF_SERVICE.md"
    tou = root / "DEMO_TERMS_OF_USE.md"
    if not tos.is_file() or not tou.is_file():
        raise RuntimeError("demo_terms_files_missing")
    return {
        "terms_of_service": {"version": TERMS_OF_SERVICE_VERSION, "sha256": _sha256_bytes(tos.read_bytes()), "path": "legal/demo/DEMO_TERMS_OF_SERVICE.md"},
        "terms_of_use": {"version": TERMS_OF_USE_VERSION, "sha256": _sha256_bytes(tou.read_bytes()), "path": "legal/demo/DEMO_TERMS_OF_USE.md"},
    }


def accept_demo_terms(*, participant_id: str, signer_name: str, signer_capacity: str, accepted: bool, electronic_signature: str, accepted_at: str | None = None) -> dict[str, Any]:
    participant_id = participant_id.strip()
    signer_name = signer_name.strip()
    signer_capacity = signer_capacity.strip()
    electronic_signature = electronic_signature.strip()
    if accepted is not True:
        raise ValueError("demo_terms_affirmative_acceptance_required")
    if not participant_id or not signer_name or not signer_capacity or not electronic_signature:
        raise ValueError("demo_terms_signer_identity_incomplete")
    timestamp = accepted_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    receipt: dict[str, Any] = {
        "schema": TERMS_RECEIPT_SCHEMA,
        "participant_id": participant_id,
        "signer_name": signer_name,
        "signer_capacity": signer_capacity,
        "affirmatively_accepted": True,
        "electronic_signature": electronic_signature,
        "accepted_at": timestamp,
        "terms": current_demo_terms_descriptor(),
        "service_relationship_only": True,
        "software_license_rights_replaced": False,
        "execution_authority_granted": False,
        "credential_authority_granted": False,
        "repository_access_granted": False,
    }
    receipt["receipt_hash"] = _hash_json(receipt)
    return receipt


def verify_demo_terms_acceptance(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("schema") != TERMS_RECEIPT_SCHEMA or receipt.get("affirmatively_accepted") is not True:
        return False
    for key in ("participant_id", "signer_name", "signer_capacity", "electronic_signature", "accepted_at"):
        if not isinstance(receipt.get(key), str) or not str(receipt.get(key)).strip():
            return False
    if receipt.get("service_relationship_only") is not True:
        return False
    for key in ("software_license_rights_replaced", "execution_authority_granted", "credential_authority_granted", "repository_access_granted"):
        if receipt.get(key) is not False:
            return False
    try:
        if receipt.get("terms") != current_demo_terms_descriptor():
            return False
    except RuntimeError:
        return False
    candidate = dict(receipt)
    expected = candidate.pop("receipt_hash", None)
    return isinstance(expected, str) and expected == _hash_json(candidate)
