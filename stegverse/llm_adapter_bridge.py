"""Strict bridge from the LLM-adapter gateway return into universal entry.

The bridge accepts a dependency-injected transport callable. It validates identity,
provider usage, authority, custody, and receipt fields before exposing provider text
to the universal-entry external LLM handler.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping


class LLMAdapterBridgeError(ValueError):
    """Raised when an adapter request or response violates the bridge contract."""


AdapterTransport = Callable[[Mapping[str, Any]], Mapping[str, Any]]


def _identity(envelope: Mapping[str, Any]) -> dict[str, Any]:
    origin = envelope.get("origin", {})
    continuity = envelope.get("continuity", {})
    if not isinstance(origin, Mapping) or not isinstance(continuity, Mapping):
        raise LLMAdapterBridgeError("origin and continuity must be mappings")
    transition_id = continuity.get("transition_id")
    run_id = continuity.get("run_id")
    message_id = origin.get("message_id")
    session_id = origin.get("session_id")
    if not all(isinstance(value, str) and value for value in (transition_id, run_id, message_id, session_id)):
        raise LLMAdapterBridgeError("missing transition/run/message/session identity")
    return {
        "transition_id": transition_id,
        "run_id": run_id,
        "event_id": message_id,
        "origin_manifest_id": continuity.get("manifest_hash") or f"manifest:{message_id}",
        "parent_transition_id": continuity.get("parent_transition_id"),
        "previous_receipt_id": continuity.get("previous_receipt_id"),
        "session_id": session_id,
    }


def build_adapter_request(prompt: str, envelope: Mapping[str, Any]) -> dict[str, Any]:
    identity = _identity(envelope)
    return {
        "message": prompt,
        "session_id": identity.pop("session_id"),
        "requested_route": "Unknown",
        "transition_intent": "external_llm",
        "transition_destination": "governed-return",
        "goal": "universal entry governed provider response",
        "execution_model": "allowlisted_task_request_only",
        "raw_shell_allowed": False,
        "authority_required": True,
        "rate_limit_required": True,
        "receipt_required_for_execution": True,
        "interaction_profile": {},
        "interaction_bands": ["provider", "receipt"],
        "math_solver_supported": True,
        "transition_identity": identity,
    }


def normalize_adapter_response(
    response: Mapping[str, Any],
    *,
    expected_transition_id: str,
    expected_run_id: str,
) -> dict[str, Any]:
    if not isinstance(response, Mapping):
        raise LLMAdapterBridgeError("adapter response must be a mapping")
    if response.get("transition_id") != expected_transition_id:
        raise LLMAdapterBridgeError("adapter transition_id mismatch")
    if response.get("run_id") != expected_run_id:
        raise LLMAdapterBridgeError("adapter run_id mismatch")

    authority = response.get("authority", {})
    if not isinstance(authority, Mapping):
        raise LLMAdapterBridgeError("adapter authority must be a mapping")
    forbidden_true = (
        "provider_output_is_authority",
        "repository_mutation_allowed",
        "publication_allowed",
        "final_response_receipt_is_repository_execution_authority",
        "local_persistence_is_master_records_custody",
        "site_grants_admissibility",
    )
    escalated = [name for name in forbidden_true if authority.get(name) is True]
    if escalated:
        raise LLMAdapterBridgeError(f"adapter authority escalation: {', '.join(escalated)}")

    provider = response.get("provider") or {}
    if not isinstance(provider, Mapping):
        raise LLMAdapterBridgeError("provider field must be a mapping")
    provider_used = provider.get("used") is True
    output = response.get("response")
    if provider_used and not isinstance(output, str):
        raise LLMAdapterBridgeError("provider result used without response text")

    usage_submission = response.get("provider_usage_submission") or {}
    if not isinstance(usage_submission, Mapping):
        raise LLMAdapterBridgeError("provider usage submission must be a mapping")
    if usage_submission.get("authority_granted") is True or usage_submission.get("custody_recorded") is True:
        raise LLMAdapterBridgeError("provider usage submission escalated authority or custody")

    return {
        "response": str(output or ""),
        "provider": provider.get("provider"),
        "model": provider.get("model"),
        "usage": provider.get("usage") or usage_submission.get("usage"),
        "receipt_id": provider.get("provider_receipt_id") or response.get("final_receipt_id") or response.get("receipt_id"),
        "provider_used": provider_used,
        "provider_status": provider.get("status"),
        "transition_id": response.get("transition_id"),
        "run_id": response.get("run_id"),
        "lifecycle_state": response.get("lifecycle_state"),
        "master_record_status": response.get("master_record_status"),
        "reconstruction_status": response.get("reconstruction_status"),
        "local_persistence_is_custody": False,
        "authority_granted": False,
    }


@dataclass(frozen=True)
class GovernedLLMAdapterProvider:
    transport: AdapterTransport

    def __call__(self, prompt: str, context: Mapping[str, Any]) -> Mapping[str, Any]:
        envelope = context.get("universal_entry_envelope")
        if not isinstance(envelope, Mapping):
            raise LLMAdapterBridgeError("universal_entry_envelope missing from dispatch context")
        request = build_adapter_request(prompt, envelope)
        response = self.transport(request)
        identity = request["transition_identity"]
        return normalize_adapter_response(
            response,
            expected_transition_id=identity["transition_id"],
            expected_run_id=identity["run_id"],
        )
