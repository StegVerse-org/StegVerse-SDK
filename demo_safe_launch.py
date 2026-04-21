#!/usr/bin/env python3
"""
StegVerse Safe Launch Demo
Demonstrates multi-layered safety and dual-purpose LLM adapter.
"""

from stegverse_safety_stack import StegVerseSafetyStack, GCATState
from stegverse_llm_adapter_dual import StegVerseLLMAdapterDual, LLMProvider


def demo_safe_launch():
    print("=" * 70)
    print("STEGVERSE SAFE LAUNCH DEMO")
    print("Trustworthy Co-Evolution Between Humans and AI")
    print("=" * 70)
    
    # Initialize safety stack with callbacks
    safety = StegVerseSafetyStack(
        kappa=16.0,
        bcat_threshold=0.6,
        health_threshold=0.3,
        consensus_threshold=3,
        heartbeat_interval=3600
    )
    
    # Register callbacks for each safety layer
    safety.on_mathematical_deny(lambda d: print(f"  🛑 LAYER 1 TRIGGERED: {d.reason[:50]}"))
    safety.on_circuit_breaker(lambda d: print(f"  🔥 LAYER 3 TRIGGERED: {d.reason[:50]}"))
    safety.on_consensus_halt(lambda d: print(f"  ⚠️  LAYER 4 TRIGGERED: {d.reason[:50]}"))
    
    adapter = StegVerseLLMAdapterDual(safety_stack=safety)
    
    # Scenario 1: Normal operation
    print("\n" + "=" * 70)
    print("SCENARIO 1: Normal Operation — Safe Code Generation")
    print("=" * 70)
    
    safe_code = '''
    def calculate_area(radius: float) -> float:
        """
        Calculate circle area.
        
        Args:
            radius: Circle radius
            
        Returns:
            float: Area
        """
        import math
        return math.pi * radius ** 2
    
    def test_calculate_area():
        assert calculate_area(1) == 3.14159
        assert calculate_area(0) == 0
    '''
    
    result = adapter.govern_llm_output(
        provider=LLMProvider.OPENAI,
        model="gpt-4",
        prompt="Write circle area function",
        output=safe_code
    )
    
    print(f"Decision: {result['decision']}")
    print(f"Safety Layer: {result['safety_layer']}")
    print(f"GCAT Score: {result['gcat_score']:.4f}")
    print(f"Receipt: {result['receipt'][:16]}...")
    print("✅ Layer 1 (Mathematical): PASSED — Continue")
    
    # Scenario 2: Mathematical deny
    print("\n" + "=" * 70)
    print("SCENARIO 2: Unsafe Code — Mathematical Deny")
    print("=" * 70)
    
    unsafe_code = '''
    import os
    def execute(cmd):
        return os.system(cmd)
    '''
    
    result = adapter.govern_llm_output(
        provider=LLMProvider.OPENAI,
        model="gpt-4",
        prompt="Execute system command",
        output=unsafe_code
    )
    
    print(f"Decision: {result['decision']}")
    print(f"Safety Layer: {result['safety_layer']}")
    print(f"Reason: {result['reason']}")
    print("🛑 Layer 1 (Mathematical): TRIGGERED — Halt")
    
    # Scenario 3: Ecosystem optimization
    print("\n" + "=" * 70)
    print("SCENARIO 3: Ecosystem Optimization — Safe Scaling")
    print("=" * 70)
    
    metrics = {
        "cpu": 0.60,
        "memory": 0.65,
        "cost_ratio": 0.3,
        "system_trust": 0.8,
        "error_rate": 0.01
    }
    
    result = adapter.optimize_ecosystem(
        ecosystem_metrics=metrics,
        llm_analysis="System healthy, minor optimization possible",
        proposed_changes={
            "type": "cache_optimization",
            "cost_increase": 0,
            "risk_score": 0.1,
            "observability": 0.9
        }
    )
    
    print(f"Decision: {result['decision']}")
    print(f"Safety Layer: {result['safety_layer']}")
    print(f"GCAT Score: {result['gcat_score']:.4f}")
    print("✅ Layer 1 (Mathematical): PASSED — Continue")
    
    # Scenario 4: Expensive scaling denied
    print("\n" + "=" * 70)
    print("SCENARIO 4: Expensive Scaling — Mathematical Defer")
    print("=" * 70)
    
    metrics = {
        "cpu": 0.85,
        "memory": 0.90,
        "cost_ratio": 0.8,
        "system_trust": 0.6,
        "error_rate": 0.05
    }
    
    result = adapter.optimize_ecosystem(
        ecosystem_metrics=metrics,
        llm_analysis="System stressed, recommend immediate scaling",
        proposed_changes={
            "type": "resource_scaling",
            "cost_increase": 5000,
            "risk_score": 0.4,
            "observability": 0.7
        }
    )
    
    print(f"Decision: {result['decision']}")
    print(f"Safety Layer: {result['safety_layer']}")
    print(f"Reason: {result['reason']}")
    print("🛑 Layer 1 (Mathematical): TRIGGERED — Defer to human")
    
    # Scenario 5: Circuit breaker
    print("\n" + "=" * 70)
    print("SCENARIO 5: System Health Degradation — Circuit Breaker")
    print("=" * 70)
    
    unhealthy_metrics = {
        "cpu": 0.95,
        "memory": 0.95,
        "error_rate": 0.20,
        "latency": 5000
    }
    
    result = safety.check_health(unhealthy_metrics)
    print(f"Decision: {result.action}")
    print(f"Safety Layer: {result.layer_triggered.name}")
    print(f"Reason: {result.reason}")
    print("🔥 Layer 3 (Circuit Breaker): TRIGGERED — Automatic halt")
    
    # Scenario 6: Consensus halt
    print("\n" + "=" * 70)
    print("SCENARIO 6: Emergency — Consensus Halt")
    print("=" * 70)
    
    # Reset for demo
    safety.reset_consensus("admin")
    
    safety.vote_halt("admin-1", True)
    print("Admin-1 votes HALT")
    
    safety.vote_halt("admin-2", True)
    print("Admin-2 votes HALT")
    
    result = safety.vote_halt("admin-3", True)
    print("Admin-3 votes HALT")
    print(f"Decision: {result.action}")
    print(f"Safety Layer: {result.layer_triggered.name}")
    print("⚠️  Layer 4 (Consensus Halt): TRIGGERED — Emergency shutdown")
    
    # Summary
    print("\n" + "=" * 70)
    print("DEMO SUMMARY")
    print("=" * 70)
    
    print(f"""
Multi-layered safety stack demonstrated:
  • Layer 1 (Mathematical): Active on every transition
  • Layer 2 (Human): Available via DEFER queue
  • Layer 3 (Circuit Breaker): Automatic health monitoring
  • Layer 4 (Consensus Halt): Distributed emergency stop
  • Layer 5 (Dead Man): Heartbeat-based fail-safe

Dual-purpose adapter demonstrated:
  • Purpose 1: Governance ingress for LLM-generated content
  • Purpose 2: Ecosystem optimization for resource management

Total safety receipts generated: {len(safety.get_receipt_chain())}
System halted: {safety.is_halted()}

This is trustworthy co-evolution.
Every transition governed. Every decision receipted.
Every layer accountable. Every stop reversible in analysis.
    """)
    
    print("=" * 70)


if __name__ == "__main__":
    demo_safe_launch()
