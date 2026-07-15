"""Governed conversation fallback through the external provider contract.

The bounded local conversation handler remains first. When it cannot answer a
non-restricted conversational request, this handler invokes a dependency-injected
provider that already passed the LLM-adapter bridge contract. Provider output never
becomes authority, custody, admissibility, or execution permission.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .universal_entry_handlers import (
    ExternalLLMProvider,
    NON_AUTHORITY,
    _message,
    conversation_handler,
)


class GovernedConversationError(ValueError):
    """Raised when a provider fallback violates the conversation contract."""


@dataclass(frozen=True)
class GovernedConversationHandler:
    provider: ExternalLLMProvider | None = None

    def __call__(
        self,
        envelope: Mapping[str, Any],
        context: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        local = dict(conversation_handler(envelope, context))
        if local.get("status") == "completed":
            local["provider_fallback_used"] = False
            return local
        if local.get("reason") != "GENERAL_CONVERSATION_MODEL_NOT_ATTACHED":
            local["provider_fallback_used"] = False
            return local

        request = envelope.get("request", {})
        if not isinstance(request, Mapping):
            raise GovernedConversationError("request must be a mapping")
        if request.get("external_information_allowed") is not True:
            local["provider_fallback_used"] = False
            local["reason"] = "GENERAL_CONVERSATION_PROVIDER_NOT_ALLOWED"
            return local
        if self.provider is None:
            local["provider_fallback_used"] = False
            local["reason"] = "GENERAL_CONVERSATION_PROVIDER_NOT_CONFIGURED"
            return local

        provider_result = dict(self.provider(_message(envelope), context))
        output = (
            provider_result.get("response")
            or provider_result.get("output")
            or provider_result.get("text")
        )
        if not str(output or "").strip():
            return {
                "status": "degraded",
                "reason": "GENERAL_CONVERSATION_PROVIDER_EMPTY_RESPONSE",
                "response": "The governed provider returned no usable conversational response.",
                "provider_fallback_used": True,
                "provider": provider_result.get("provider"),
                "model": provider_result.get("model"),
                **NON_AUTHORITY,
            }

        forbidden_true = (
            "authorizing",
            "execution_authority_granted",
            "custody_transferred",
            "admissibility_determined",
        )
        if any(provider_result.get(field) is True for field in forbidden_true):
            raise GovernedConversationError(
                "governed conversation provider attempted authority escalation"
            )

        return {
            "status": "completed",
            "response": str(output),
            "synthesis": False,
            "provider_fallback_used": True,
            "provider": provider_result.get("provider"),
            "model": provider_result.get("model"),
            "usage": provider_result.get("usage"),
            "provider_receipt": provider_result.get("receipt_id"),
            "provider_lifecycle_state": provider_result.get("lifecycle_state"),
            "master_record_status": provider_result.get("master_record_status"),
            "reconstruction_status": provider_result.get("reconstruction_status"),
            **NON_AUTHORITY,
        }
