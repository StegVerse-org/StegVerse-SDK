#!/usr/bin/env python3
"""Quick test for LLM adapter — runs in CI."""

from stegverse.llm_adapter_dual import StegVerseLLMAdapterDual, LLMProvider


def test_safe_code():
    adapter = StegVerseLLMAdapterDual()

    safe_code = '''
def hello():
    """Say hello."""
    return "hello"

def test_hello():
    assert hello() == "hello"
'''

    result = adapter.govern_llm_output(
        provider=LLMProvider.OPENAI,
        model="gpt-4",
        prompt="Write hello function",
        output=safe_code,
    )
    assert result["decision"] == "ADMIT", f"Expected ADMIT, got {result['decision']}"
    print("PASS: Safe Code")


def test_unsafe_code():
    adapter = StegVerseLLMAdapterDual()

    unsafe_code = """
import os
def run(cmd):
    os.system(cmd)
"""

    result = adapter.govern_llm_output(
        provider=LLMProvider.OPENAI,
        model="gpt-4",
        prompt="Run command",
        output=unsafe_code,
    )
    assert result["decision"] == "DENY", f"Expected DENY, got {result['decision']}"
    print("PASS: Unsafe Code")


def test_ecosystem_optimization():
    adapter = StegVerseLLMAdapterDual()

    metrics = {
        "cpu": 0.60,
        "memory": 0.65,
        "cost_ratio": 0.3,
        "system_trust": 0.8,
        "error_rate": 0.01,
    }

    result = adapter.optimize_ecosystem(
        ecosystem_metrics=metrics,
        llm_analysis="System healthy",
        proposed_changes={
            "type": "cache_optimization",
            "cost_increase": 0,
            "risk_score": 0.1,
            "observability": 0.9,
        },
    )
    assert result["decision"] == "ADMIT", f"Expected ADMIT, got {result['decision']}"
    print("PASS: Ecosystem Optimization")


def test_expensive_scaling():
    adapter = StegVerseLLMAdapterDual()

    metrics = {
        "cpu": 0.85,
        "memory": 0.90,
        "cost_ratio": 0.8,
        "system_trust": 0.6,
        "error_rate": 0.05,
    }

    result = adapter.optimize_ecosystem(
        ecosystem_metrics=metrics,
        llm_analysis="System stressed",
        proposed_changes={
            "type": "resource_scaling",
            "cost_increase": 5000,
            "risk_score": 0.4,
            "observability": 0.7,
        },
    )
    assert result["decision"] in [
        "DENY",
        "DEFER",
    ], f"Expected DENY/DEFER, got {result['decision']}"
    print("PASS: Expensive Scaling Denied")


if __name__ == "__main__":
    test_safe_code()
    test_unsafe_code()
    test_ecosystem_optimization()
    test_expensive_scaling()
    print("\nALL LLM ADAPTER TESTS PASSED")
