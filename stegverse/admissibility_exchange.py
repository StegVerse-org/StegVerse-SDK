"""Governed Admissibility Exchange helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Dict, Mapping, Optional

from .admissibility_bundle import verify_admissibility_bundle

GAX_EXCHANGE_SCHEMA = "stegverse.admissibility.gax_exchange.v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_gax_exchange(
    bundle: Mapping[str, Any],
    *,
    exchange_type: str = "bundle_export",
    producer_component: str = "sdk",
    producer_version: str = "1.0",
    execution_receipt: Optional[Mapping[str, Any]] = None,
    notes: Optional[list[str]] = None,
    related_formalisms: Optional[list[str]] = None,
) -> Dict[str, Any]:
    """Build a portable GAX payload around a governed admissibility bundle."""
    return {
        "schema": GAX_EXCHANGE_SCHEMA,
        "exchange_type": exchange_type,
        "created_at": _utc_now(),
        "producer": {
            "component": producer_component,
            "version": producer_version,
        },
        "bundle": dict(bundle),
        "attachments": {
            "execution_receipt": dict(execution_receipt) if execution_receipt is not None else None,
            "notes": list(notes) if notes is not None else [],
            "related_formalisms": list(related_formalisms) if related_formalisms is not None else [],
        },
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_execution_proof": True,
        },
    }


def verify_gax_exchange(exchange: Mapping[str, Any]) -> bool:
    """Return True when a GAX payload has the expected shape and valid bundle."""
    required = {"schema", "exchange_type", "created_at", "producer", "bundle", "attachments", "boundary"}
    if not required.issubset(exchange.keys()):
        return False
    if exchange.get("schema") != GAX_EXCHANGE_SCHEMA:
        return False
    if not isinstance(exchange.get("producer"), Mapping):
        return False
    if not isinstance(exchange.get("attachments"), Mapping):
        return False
    bundle = exchange.get("bundle")
    if not isinstance(bundle, Mapping):
        return False
    return verify_admissibility_bundle(bundle)


def export_gax_json(exchange: Mapping[str, Any]) -> str:
    """Serialize a GAX payload as deterministic formatted JSON."""
    return json.dumps(exchange, indent=2, sort_keys=True)


def load_gax_json(payload: str) -> Dict[str, Any]:
    """Load a GAX JSON payload into a dictionary."""
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("GAX payload must decode to an object")
    return parsed
