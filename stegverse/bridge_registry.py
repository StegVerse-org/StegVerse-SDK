"""Registry for SDK dynamic admissibility bridges."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Mapping, Optional

BRIDGE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "generic_tester_packet": {
        "id": "generic_tester_packet",
        "label": "Generic tester packet",
        "module": "stegverse.admissibility",
        "builder": None,
        "evaluator": "evaluate_admissibility_packet",
        "summary": "Evaluates discipline-aware tester packets directly.",
        "input_schema": "schemas/admissibility/tester-output.schema.json",
        "result_schema": "schemas/admissibility/dynamic-demo-result.schema.json",
        "discipline_id": "any",
        "recommended_route": ["discipline_test_matrix"],
    },
    "llm_output": {
        "id": "llm_output",
        "label": "LLM output",
        "module": "stegverse.llm_admissibility",
        "builder": "build_llm_tester_packet",
        "evaluator": "evaluate_llm_output_admissibility",
        "summary": "Converts LLM text into a dynamic admissibility tester packet.",
        "input_schema": "schemas/admissibility/tester-output.schema.json",
        "result_schema": "schemas/admissibility/llm-bridge-result.schema.json",
        "discipline_id": "ai_llm_systems",
        "recommended_route": ["governance_filter", "llm_governance_comparison", "fail_closed"],
    },
    "math_artifact": {
        "id": "math_artifact",
        "label": "Math / formalism artifact",
        "module": "stegverse.math_admissibility",
        "builder": "build_math_tester_packet",
        "evaluator": "evaluate_math_artifact_admissibility",
        "summary": "Converts math-solver or formalism artifacts into dynamic admissibility tester packets.",
        "input_schema": "schemas/admissibility/tester-output.schema.json",
        "result_schema": "schemas/admissibility/math-bridge-result.schema.json",
        "discipline_id": "mathematics_formal_methods",
        "recommended_route": ["math_solver_adapter", "receipt_replay", "transition_admissibility"],
    },
}


def list_dynamic_bridges() -> List[Dict[str, Any]]:
    """Return all registered dynamic admissibility bridge descriptors."""
    return [deepcopy(item) for item in BRIDGE_REGISTRY.values()]


def get_dynamic_bridge(bridge_id: str) -> Optional[Dict[str, Any]]:
    """Return one bridge descriptor by id, or None if unknown."""
    bridge = BRIDGE_REGISTRY.get(bridge_id)
    return deepcopy(bridge) if bridge is not None else None


def require_dynamic_bridge(bridge_id: str) -> Dict[str, Any]:
    """Return one bridge descriptor or raise KeyError."""
    bridge = get_dynamic_bridge(bridge_id)
    if bridge is None:
        known = ", ".join(sorted(BRIDGE_REGISTRY))
        raise KeyError(f"unknown dynamic admissibility bridge: {bridge_id}; known: {known}")
    return bridge


def bridge_ids() -> List[str]:
    """Return registered bridge ids."""
    return sorted(BRIDGE_REGISTRY)


def bridge_registry_snapshot() -> Mapping[str, Dict[str, Any]]:
    """Return a deep-copied snapshot keyed by bridge id."""
    return deepcopy(BRIDGE_REGISTRY)
