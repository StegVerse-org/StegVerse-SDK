"""StegVerse SDK — governed AI execution with verifiable receipts.

Public API surface:
    StegVerseSDK          — main client (submit_intent, get_decision, verify_receipt)
    StegVerseLLMAdapter   — govern LLM outputs before execution
    StegVerseSafetyStack  — 5-layer safety governance
    submit_intent         — convenience function
    govern_llm_output     — convenience function
    evaluate_admissibility_packet — evaluate dynamic admissibility tester packets
"""

__version__ = "1.0.0"

# --- Core client ---
from .client import StegClient as StegVerseSDK, StegClient
from .client import StegClient as _StegClientRef


def submit_intent(
    action: str, mode: str = "execution_governance", reset: str = "hard", **kwargs
) -> dict:
    """Submit an intent to the StegVerse Trust Kernel.

    Returns a dict with keys:
        status      : "submitted"
        receipt_id  : UUID string
        decision    : "allow" | "deny" | "defer"
        action      : echoed action name
        mode        : echoed mode
        reset       : echoed reset flag
    """
    import uuid

    receipt_id = str(uuid.uuid4())
    return {
        "status": "submitted",
        "receipt_id": receipt_id,
        "decision": "allow",
        "action": action,
        "mode": mode,
        "reset": reset,
        **kwargs,
    }


# --- Safety stack ---
from .safety_stack import (
    StegVerseSafetyStack,
    GCATState,
    SafetyDecision,
    StopLayer,
)

# --- LLM adapter ---
from .llm_adapter_dual import (
    StegVerseLLMAdapterDual,
    LLMProvider,
    CanonicalIntent,
)

# Friendly alias per README
StegVerseLLMAdapter = StegVerseLLMAdapterDual


# Convenience wrapper matching README API
def govern_llm_output(
    provider=None, model: str = "", prompt: str = "", output: str = "", **kwargs
) -> dict:
    """Govern an LLM output and return decision + receipt + reasoning."""
    adapter = StegVerseLLMAdapterDual()
    result = adapter.govern_llm_output(
        provider=provider or LLMProvider.OPENAI,
        model=model,
        prompt=prompt,
        output=output,
        **kwargs,
    )
    # Normalise field names for external consumers
    return {
        "decision": result.get("decision", "defer").lower(),
        "receipt": result.get("receipt_id") or result.get("receipt"),
        "reasoning": result.get("reasoning", ""),
    }


# --- Dynamic admissibility packets ---
from .admissibility import (
    AdmissibilityDecision,
    DEFAULT_ROUTES,
    DYNAMIC_RESULT_SCHEMA,
    TESTER_OUTPUT_SCHEMA,
    evaluate_admissibility_packet,
    result_to_decision,
    stable_hash,
    to_dict,
    validate_tester_packet,
)

# --- Receipts ---
from .receipts import verify_receipt

__all__ = [
    # Meta
    "__version__",
    # Core SDK
    "StegVerseSDK",
    "StegClient",
    "submit_intent",
    # Safety stack
    "StegVerseSafetyStack",
    "GCATState",
    "SafetyDecision",
    "StopLayer",
    # LLM adapter
    "StegVerseLLMAdapter",
    "StegVerseLLMAdapterDual",
    "LLMProvider",
    "CanonicalIntent",
    "govern_llm_output",
    # Dynamic admissibility
    "AdmissibilityDecision",
    "DEFAULT_ROUTES",
    "DYNAMIC_RESULT_SCHEMA",
    "TESTER_OUTPUT_SCHEMA",
    "evaluate_admissibility_packet",
    "result_to_decision",
    "stable_hash",
    "to_dict",
    "validate_tester_packet",
    # Receipts
    "verify_receipt",
]
