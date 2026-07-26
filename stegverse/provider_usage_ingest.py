"""Ingest provider-owned LLM usage events without transferring authority.

The adapter remains the event owner. The SDK validates structure, verifies the
canonical event hash, and projects descriptive measurements into the existing
cross-entry transition usage contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Optional

from .transition_usage import TransitionUsageEvent, UsageMetric, build_usage_event

PROVIDER_USAGE_SCHEMA = "stegverse.provider_usage_event.v1"
FALSE_BOUNDARY_KEYS = (
    "adapter_is_execution_authority",
    "provider_response_is_admissibility",
    "model_output_is_publication_authority",
    "reasoning_provenance_is_full_chain_of_thought",
    "usage_measurement_is_value_claim",
    "provider_identity_is_actor_authority",
)
ALLOWED_EVENT_TYPES = {"PROVIDER_RESPONSE", "PROVIDER_REFUSAL", "PROVIDER_ERROR"}


class ProviderUsageIngestError(ValueError):
    """Raised when an adapter-owned usage event fails closed."""


def _canonical_hash(event: Mapping[str, Any]) -> str:
    material = dict(event)
    material.pop("event_sha256", None)
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProviderUsageIngestError(f"{label} is required")
    return value


def validate_provider_usage_event(event: Mapping[str, Any]) -> None:
    if event.get("schema") != PROVIDER_USAGE_SCHEMA:
        raise ProviderUsageIngestError("provider usage schema mismatch")
    if event.get("event_type") not in ALLOWED_EVENT_TYPES:
        raise ProviderUsageIngestError("unsupported provider event type")
    _require_text(event.get("event_id"), "event_id")

    provider = event.get("provider")
    request = event.get("request")
    response = event.get("response")
    measurements = event.get("measurements")
    provenance = event.get("reasoning_provenance")
    boundary = event.get("authority_boundary")
    return_path = event.get("return_to_origin")
    for value, label in (
        (provider, "provider"),
        (request, "request"),
        (response, "response"),
        (measurements, "measurements"),
        (provenance, "reasoning_provenance"),
        (boundary, "authority_boundary"),
        (return_path, "return_to_origin"),
    ):
        if not isinstance(value, Mapping):
            raise ProviderUsageIngestError(f"{label} must be an object")

    _require_text(provider.get("name"), "provider.name")
    _require_text(provider.get("model"), "provider.model")
    _require_text(provider.get("model_version"), "provider.model_version")
    _require_text(request.get("request_id"), "request.request_id")
    _require_text(response.get("response_id"), "response.response_id")
    for container, key in ((request, "request_sha256"), (response, "response_sha256")):
        digest = container.get(key)
        if not isinstance(digest, str) or len(digest) != 64:
            raise ProviderUsageIngestError(f"{key} must be a SHA-256 hex string")

    input_tokens = measurements.get("input_tokens")
    output_tokens = measurements.get("output_tokens")
    total_tokens = measurements.get("total_tokens")
    for value, label in (
        (input_tokens, "input_tokens"),
        (output_tokens, "output_tokens"),
        (total_tokens, "total_tokens"),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ProviderUsageIngestError(f"{label} must be a non-negative integer")
    if input_tokens + output_tokens != total_tokens:
        raise ProviderUsageIngestError("token total mismatch")
    latency = measurements.get("latency_ms")
    if not isinstance(latency, int) or isinstance(latency, bool) or latency < 0:
        raise ProviderUsageIngestError("latency_ms must be a non-negative integer")

    if provenance.get("mode") != "bounded_reference":
        raise ProviderUsageIngestError("reasoning provenance must be bounded_reference")
    _require_text(provenance.get("reference"), "reasoning_provenance.reference")
    if provenance.get("full_chain_of_thought_included") is not False:
        raise ProviderUsageIngestError("full chain-of-thought must not be included")

    for key in FALSE_BOUNDARY_KEYS:
        if boundary.get(key) is not False:
            raise ProviderUsageIngestError(f"authority boundary escalation: {key}")
    if return_path.get("receipt_required") is not True:
        raise ProviderUsageIngestError("return-to-origin receipt must be required")
    _require_text(return_path.get("origin_event_id"), "return_to_origin.origin_event_id")
    if event.get("manual_user_action_required") is not False:
        raise ProviderUsageIngestError("manual user action boundary invalid")
    if event.get("event_sha256") != _canonical_hash(event):
        raise ProviderUsageIngestError("provider event hash mismatch")


@dataclass(frozen=True)
class ProviderUsageIngestResult:
    provider_event_id: str
    provider_event_sha256: str
    transition_usage_event: Dict[str, Any]
    receipt_required: bool
    authority_transferred: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema": "stegverse.sdk_provider_usage_ingest.v1",
            "provider_event_id": self.provider_event_id,
            "provider_event_sha256": self.provider_event_sha256,
            "transition_usage_event": self.transition_usage_event,
            "receipt_required": self.receipt_required,
            "authority_transferred": self.authority_transferred,
            "invariants": {
                "sdk_validation_is_execution": False,
                "aggregation_is_authority": False,
                "session_receipt_is_custody": False,
                "provider_event_ownership_preserved": True,
                "full_chain_of_thought_ingested": False,
            },
        }


def ingest_provider_usage_event(
    event: Mapping[str, Any],
    *,
    session_id: str,
    transition_id: str,
    occurred_at: str,
    parent_transition_id: Optional[str] = None,
) -> ProviderUsageIngestResult:
    """Validate and project one adapter-owned event into SDK session usage."""

    validate_provider_usage_event(event)
    provider = event["provider"]
    measurements = event["measurements"]
    return_path = event["return_to_origin"]

    metrics = {
        "input_tokens": UsageMetric(str(measurements["input_tokens"]), "tokens", "MEASURED", event["event_id"]),
        "output_tokens": UsageMetric(str(measurements["output_tokens"]), "tokens", "MEASURED", event["event_id"]),
        "total_tokens": UsageMetric(str(measurements["total_tokens"]), "tokens", "MEASURED", event["event_id"]),
        "latency_ms": UsageMetric(str(measurements["latency_ms"]), "ms", "MEASURED", event["event_id"]),
    }
    compute_units = measurements.get("compute_units")
    metrics["compute_units"] = (
        UsageMetric(None, "provider_units", "UNAVAILABLE", event["event_id"])
        if compute_units is None
        else UsageMetric(str(compute_units), "provider_units", "MEASURED", event["event_id"])
    )

    usage_event = build_usage_event(
        TransitionUsageEvent(
            measurement_id=event["event_id"],
            session_id=session_id,
            transition_id=transition_id,
            parent_transition_id=parent_transition_id,
            origin_entry_point=return_path["origin_event_id"],
            entry_point="StegVerse-org/LLM-adapter",
            entry_point_role="provider_usage_source",
            interaction_type=event["event_type"],
            metric_owner=provider["name"],
            measurement_source="provider_owned_event",
            route_kind="llm_adapter_to_sdk",
            provider=provider["name"],
            model=f"{provider['model']}@{provider['model_version']}",
            evidence_class="MEASURED",
            metrics=metrics,
            receipt_refs=[event["event_sha256"]],
            occurred_at=occurred_at,
        )
    )
    return ProviderUsageIngestResult(
        provider_event_id=event["event_id"],
        provider_event_sha256=event["event_sha256"],
        transition_usage_event=usage_event,
        receipt_required=True,
    )
