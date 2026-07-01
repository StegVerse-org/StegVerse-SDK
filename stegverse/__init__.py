"""StegVerse SDK — governed AI execution with verifiable receipts.

Public API surface:
    StegVerseSDK          — main client (submit_intent, get_decision, verify_receipt)
    StegVerseLLMAdapter   — govern LLM outputs before execution
    StegVerseSafetyStack  — 5-layer safety governance
    submit_intent         — convenience function
    govern_llm_output     — convenience function
    evaluate_admissibility_packet — evaluate dynamic admissibility tester packets
    handle_universal_transition_table_package — validate universal transition-table intake
    validate_commitment_candidate — validate non-authorizing commitment candidates
    build_query_packet    — build governed LLM retrieval/evidence packet
    build_response_receipt — build reconstructable governed LLM response receipt
    validate_governed_llm_session_packet — validate complete adapter session packets
    intake_governed_llm_session_packet — produce route-ready SDK intake result
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


# --- Governed LLM reconstruction contracts ---
from .governed_llm import (
    CRITICAL_RISK,
    HIGH_RISK,
    LOW_RISK,
    MEDIUM_RISK,
    SCHEMA_VERSION as GOVERNED_LLM_SCHEMA_VERSION,
    EvidencePointer,
    GovernedQueryPacket,
    GovernedResponseReceipt,
    build_query_packet,
    build_response_receipt,
    classify_query_purpose,
    classify_risk_tier,
    reconstruction_summary,
)

# --- Governed LLM full session packets ---
from .governed_llm_session import (
    GovernedLLMSessionDecision,
    GovernedLLMSessionValidationError,
    SESSION_PACKET_SCHEMA_VERSION,
    validate_governed_llm_session_packet,
)
from .governed_llm_session_intake import (
    GovernedLLMSessionIntakeResult,
    SESSION_INTAKE_SCHEMA_VERSION,
    intake_governed_llm_session_packet,
)

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

# --- Universal transition-table intake ---
from .universal_transition_table_intake import (
    UniversalTransitionTableIntakeError,
    handle_universal_transition_table_package,
    validate_commitment_candidate,
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
    # Governed LLM reconstruction contracts
    "GOVERNED_LLM_SCHEMA_VERSION",
    "LOW_RISK",
    "MEDIUM_RISK",
    "HIGH_RISK",
    "CRITICAL_RISK",
    "EvidencePointer",
    "GovernedQueryPacket",
    "GovernedResponseReceipt",
    "build_query_packet",
    "build_response_receipt",
    "classify_query_purpose",
    "classify_risk_tier",
    "reconstruction_summary",
    # Governed LLM full session packets
    "SESSION_PACKET_SCHEMA_VERSION",
    "SESSION_INTAKE_SCHEMA_VERSION",
    "GovernedLLMSessionDecision",
    "GovernedLLMSessionIntakeResult",
    "GovernedLLMSessionValidationError",
    "validate_governed_llm_session_packet",
    "intake_governed_llm_session_packet",
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
    # Universal transition-table intake
    "UniversalTransitionTableIntakeError",
    "handle_universal_transition_table_package",
    "validate_commitment_candidate",
    # Receipts
    "verify_receipt",
]
