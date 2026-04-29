#!/usr/bin/env python3
"""Quick test for safety stack — runs in CI."""

from stegverse.safety_stack import StegVerseSafetyStack, GCATState


def test_layer1_mathematical():
    safety = StegVerseSafetyStack()

    # Safe state
    safe = GCATState(g=0.30, c=0.30, a=0.20, t=0.20)
    d = safety.evaluate_mathematical(safe, 0.8, "test")
    assert d.action == "CONTINUE", f"Expected CONTINUE, got {d.action}"

    # Unsafe state
    unsafe = GCATState(g=0.10, c=0.10, a=0.60, t=0.20)
    d = safety.evaluate_mathematical(unsafe, 0.5, "test")
    assert d.action == "HALT", f"Expected HALT, got {d.action}"

    print("PASS: Layer 1 Mathematical")


def test_layer3_circuit_breaker():
    safety = StegVerseSafetyStack()

    # Healthy
    d = safety.check_health({"cpu": 0.5, "memory": 0.6, "error_rate": 0.01})
    assert d.action == "CONTINUE", f"Expected CONTINUE, got {d.action}"

    # Unhealthy
    d = safety.check_health({"cpu": 0.95, "memory": 0.95, "error_rate": 0.20})
    assert d.action == "HALT", f"Expected HALT, got {d.action}"

    print("PASS: Layer 3 Circuit Breaker")


def test_layer4_consensus():
    safety = StegVerseSafetyStack()

    safety.vote_halt("a1", True)
    safety.vote_halt("a2", True)
    d = safety.vote_halt("a3", True)
    assert (
        d.action == "EMERGENCY_SHUTDOWN"
    ), f"Expected EMERGENCY_SHUTDOWN, got {d.action}"

    print("PASS: Layer 4 Consensus Halt")


def test_chain_integrity():
    safety = StegVerseSafetyStack()

    safe = GCATState(g=0.30, c=0.30, a=0.20, t=0.20)
    safety.evaluate_mathematical(safe, 0.8, "test")

    chain = safety.get_receipt_chain()
    assert len(chain) == 1, f"Expected 1 receipt, got {len(chain)}"

    print("PASS: Chain Integrity")


if __name__ == "__main__":
    test_layer1_mathematical()
    test_layer3_circuit_breaker()
    test_layer4_consensus()
    test_chain_integrity()
    print("\nALL SAFETY STACK TESTS PASSED")
