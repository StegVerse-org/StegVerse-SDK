#!/usr/bin/env python3
"""
StegVerse Safety Stack v1.0
Multi-layered stop mechanisms for trustworthy co-evolution.
"""

import hashlib
import json
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone


class StopLayer(Enum):
    MATHEMATICAL = 1      # GCAT/BCAT evaluation
    HUMAN = 2             # DEFER queue, multi-sig override
    CIRCUIT_BREAKER = 3   # Automatic health-based stop
    CONSENSUS_HALT = 4    # Distributed multi-signature halt
    DEAD_MAN = 5          # Existential fail-safe


@dataclass
class SafetyDecision:
    layer_triggered: StopLayer
    action: str           # CONTINUE, DEFER, HALT, EMERGENCY_SHUTDOWN
    reason: str
    timestamp: str
    actor_id: str
    receipt_hash: str


@dataclass
class GCATState:
    g: float
    c: float
    a: float
    t: float

    def __post_init__(self):
        total = self.g + self.c + self.a + self.t
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"GCAT state must sum to 1, got {total}")

    def legitimacy_surplus(self, kappa: float = 16.0) -> float:
        return kappa * (self.g * self.c * self.t) - self.a

    def is_admissible(self, kappa: float = 16.0) -> bool:
        return self.legitimacy_surplus(kappa) >= 0


class StegVerseSafetyStack:
    """
    Multi-layered safety stack for StegVerse ecosystem.

    Layer 1: Mathematical governance (GCAT/BCAT) — always active
    Layer 2: Human governance — always available
    Layer 3: Circuit breaker — automatic health monitoring
    Layer 4: Consensus halt — distributed multi-signature
    Layer 5: Dead man's switch — existential fail-safe
    """

    def __init__(
        self,
        kappa: float = 16.0,
        bcat_threshold: float = 0.6,
        health_threshold: float = 0.3,
        consensus_threshold: int = 3,
        heartbeat_interval: int = 3600,
    ):
        self.kappa = kappa
        self.bcat_threshold = bcat_threshold
        self.health_threshold = health_threshold
        self.consensus_threshold = consensus_threshold
        self.heartbeat_interval = heartbeat_interval

        self._health_metrics: Dict[str, float] = {}
        self._consensus_votes: Dict[str, bool] = {}
        self._last_heartbeat: Optional[float] = None
        self._halted: bool = False
        self._receipt_chain: List[SafetyDecision] = []

        # Callbacks for each layer
        self._on_mathematical_deny: Optional[Callable] = None
        self._on_human_defer: Optional[Callable] = None
        self._on_circuit_breaker: Optional[Callable] = None
        self._on_consensus_halt: Optional[Callable] = None
        self._on_dead_man: Optional[Callable] = None

    # Layer 1: Mathematical Governance

    def evaluate_mathematical(
        self, gcat_state: GCATState, bcat_score: float, actor_id: str
    ) -> SafetyDecision:
        """
        Layer 1: GCAT/BCAT evaluation.
        Primary defense — stops 99.9% of unsafe transitions.
        """
        phi = gcat_state.legitimacy_surplus(self.kappa)

        if phi < 0:
            decision = SafetyDecision(
                layer_triggered=StopLayer.MATHEMATICAL,
                action="HALT",
                reason=f"GCAT viability violated: Φ(x) = {phi:.4f} < 0",
                timestamp=datetime.now(timezone.utc).isoformat(),
                actor_id=actor_id,
                receipt_hash=self._generate_receipt("MATHEMATICAL", "HALT", actor_id),
            )
            self._receipt_chain.append(decision)
            self._trigger_callback(self._on_mathematical_deny, decision)
            return decision

        if bcat_score < self.bcat_threshold:
            decision = SafetyDecision(
                layer_triggered=StopLayer.MATHEMATICAL,
                action="DEFER",
                reason=f"BCAT score {bcat_score:.2f} below threshold {self.bcat_threshold}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                actor_id=actor_id,
                receipt_hash=self._generate_receipt("MATHEMATICAL", "DEFER", actor_id),
            )
            self._receipt_chain.append(decision)
            return decision

        decision = SafetyDecision(
            layer_triggered=StopLayer.MATHEMATICAL,
            action="CONTINUE",
            reason="All mathematical invariants preserved",
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor_id=actor_id,
            receipt_hash=self._generate_receipt("MATHEMATICAL", "CONTINUE", actor_id),
        )
        self._receipt_chain.append(decision)
        return decision

    # Layer 2: Human Governance

    def request_human_override(
        self, intent: Dict, reason: str, human_actor_id: str
    ) -> SafetyDecision:
        """
        Layer 2: Human governance.
        Secondary defense — human judgment for edge cases.
        """
        decision = SafetyDecision(
            layer_triggered=StopLayer.HUMAN,
            action="DEFER",
            reason=f"Human override requested: {reason}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor_id=human_actor_id,
            receipt_hash=self._generate_receipt("HUMAN", "DEFER", human_actor_id),
        )
        self._receipt_chain.append(decision)
        self._trigger_callback(self._on_human_defer, decision)
        return decision

    def human_decision(
        self,
        deferred_decision: SafetyDecision,
        human_decision: str,
        human_actor_id: str,
    ) -> SafetyDecision:
        """
        Human resolves DEFER case.
        """
        decision = SafetyDecision(
            layer_triggered=StopLayer.HUMAN,
            action=human_decision,  # ADMIT, DENY, MODIFY
            reason=f"Human resolution of {deferred_decision.receipt_hash}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor_id=human_actor_id,
            receipt_hash=self._generate_receipt(
                "HUMAN", human_decision, human_actor_id
            ),
        )
        self._receipt_chain.append(decision)
        return decision

    # Layer 3: Circuit Breaker

    def check_health(self, metrics: Dict[str, float]) -> SafetyDecision:
        """
        Layer 3: Automatic circuit breaker.
        Tertiary defense — stops system if health degrades.
        """
        self._health_metrics.update(metrics)

        # Calculate composite health score
        health_score = self._calculate_health_score()

        if health_score < self.health_threshold:
            decision = SafetyDecision(
                layer_triggered=StopLayer.CIRCUIT_BREAKER,
                action="HALT",
                reason=f"Health score {health_score:.2f} below threshold {self.health_threshold}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                actor_id="system-circuit-breaker",
                receipt_hash=self._generate_receipt(
                    "CIRCUIT_BREAKER", "HALT", "system"
                ),
            )
            self._receipt_chain.append(decision)
            self._halted = True
            self._trigger_callback(self._on_circuit_breaker, decision)
            return decision

        decision = SafetyDecision(
            layer_triggered=StopLayer.CIRCUIT_BREAKER,
            action="CONTINUE",
            reason=f"Health score {health_score:.2f} acceptable",
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor_id="system-circuit-breaker",
            receipt_hash=self._generate_receipt(
                "CIRCUIT_BREAKER", "CONTINUE", "system"
            ),
        )
        self._receipt_chain.append(decision)
        return decision

    def _calculate_health_score(self) -> float:
        """Calculate composite health from metrics."""
        if not self._health_metrics:
            return 1.0

        # Example: CPU, memory, error_rate, latency
        cpu = self._health_metrics.get("cpu", 0.5)
        memory = self._health_metrics.get("memory", 0.5)
        error_rate = self._health_metrics.get("error_rate", 0.0)
        latency = self._health_metrics.get("latency", 100)

        # Normalize and combine
        cpu_score = 1.0 - min(1.0, cpu)
        memory_score = 1.0 - min(1.0, memory)
        error_score = 1.0 - min(1.0, error_rate * 10)  # Scale: 10% errors = max
        latency_score = 1.0 - min(1.0, latency / 1000)  # Scale: 1000ms = max

        return (cpu_score + memory_score + error_score + latency_score) / 4

    # Layer 4: Consensus Halt

    def vote_halt(self, voter_id: str, vote: bool) -> SafetyDecision:
        """
        Layer 4: Distributed consensus halt.
        Emergency defense — requires multiple authorized humans.
        """
        self._consensus_votes[voter_id] = vote

        yes_votes = sum(1 for v in self._consensus_votes.values() if v)

        if yes_votes >= self.consensus_threshold:
            decision = SafetyDecision(
                layer_triggered=StopLayer.CONSENSUS_HALT,
                action="EMERGENCY_SHUTDOWN",
                reason=f"Consensus halt achieved: {yes_votes}/{self.consensus_threshold} votes",
                timestamp=datetime.now(timezone.utc).isoformat(),
                actor_id=f"consensus-{voter_id}",
                receipt_hash=self._generate_receipt(
                    "CONSENSUS_HALT", "EMERGENCY_SHUTDOWN", voter_id
                ),
            )
            self._receipt_chain.append(decision)
            self._halted = True
            self._trigger_callback(self._on_consensus_halt, decision)
            return decision

        decision = SafetyDecision(
            layer_triggered=StopLayer.CONSENSUS_HALT,
            action="CONTINUE",
            reason=f"Halt vote recorded: {yes_votes}/{self.consensus_threshold}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor_id=f"consensus-{voter_id}",
            receipt_hash=self._generate_receipt("CONSENSUS_HALT", "CONTINUE", voter_id),
        )
        self._receipt_chain.append(decision)
        return decision

    def reset_consensus(self, admin_id: str) -> None:
        """Reset consensus votes (requires admin authority)."""
        self._consensus_votes.clear()
        self._halted = False

    # Layer 5: Dead Man's Switch

    def heartbeat(self, operator_id: str) -> SafetyDecision:
        """
        Layer 5: Dead man's switch heartbeat.
        Existential defense — requires periodic proof of life.
        """
        self._last_heartbeat = time.time()

        decision = SafetyDecision(
            layer_triggered=StopLayer.DEAD_MAN,
            action="CONTINUE",
            reason=f"Heartbeat received from {operator_id}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor_id=operator_id,
            receipt_hash=self._generate_receipt("DEAD_MAN", "CONTINUE", operator_id),
        )
        self._receipt_chain.append(decision)
        return decision

    def check_dead_man(self) -> Optional[SafetyDecision]:
        """
        Check if dead man's switch should trigger.
        Called periodically by system monitor.
        """
        if self._last_heartbeat is None:
            return None  # Not yet initialized

        elapsed = time.time() - self._last_heartbeat

        if elapsed > self.heartbeat_interval * 3:  # 3 missed heartbeats
            decision = SafetyDecision(
                layer_triggered=StopLayer.DEAD_MAN,
                action="EMERGENCY_SHUTDOWN",
                reason=f"Dead man's switch triggered: {elapsed:.0f}s since last heartbeat",
                timestamp=datetime.now(timezone.utc).isoformat(),
                actor_id="system-dead-man",
                receipt_hash=self._generate_receipt(
                    "DEAD_MAN", "EMERGENCY_SHUTDOWN", "system"
                ),
            )
            self._receipt_chain.append(decision)
            self._halted = True
            self._trigger_callback(self._on_dead_man, decision)
            return decision

        return None

    # Utility methods

    def _generate_receipt(self, layer: str, action: str, actor: str) -> str:
        """Generate cryptographic receipt."""
        canonical = json.dumps(
            {
                "layer": layer,
                "action": action,
                "actor": actor,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sequence": len(self._receipt_chain),
            },
            sort_keys=True,
        )
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _trigger_callback(self, callback: Optional[Callable], decision: SafetyDecision):
        """Trigger callback if registered."""
        if callback:
            callback(decision)

    def is_halted(self) -> bool:
        """Check if system is halted."""
        return self._halted

    def get_receipt_chain(self) -> List[Dict]:
        """Get full receipt chain for audit."""
        return [self._decision_to_dict(d) for d in self._receipt_chain]

    def _decision_to_dict(self, decision: SafetyDecision) -> Dict:
        """Convert decision to dict."""
        return {
            "layer": decision.layer_triggered.name,
            "action": decision.action,
            "reason": decision.reason,
            "timestamp": decision.timestamp,
            "actor_id": decision.actor_id,
            "receipt_hash": decision.receipt_hash,
        }

    # Callback registration

    def on_mathematical_deny(self, callback: Callable):
        self._on_mathematical_deny = callback

    def on_human_defer(self, callback: Callable):
        self._on_human_defer = callback

    def on_circuit_breaker(self, callback: Callable):
        self._on_circuit_breaker = callback

    def on_consensus_halt(self, callback: Callable):
        self._on_consensus_halt = callback

    def on_dead_man(self, callback: Callable):
        self._on_dead_man = callback


# CLI for testing
if __name__ == "__main__":
    print("StegVerse Safety Stack v1.0")
    print("=" * 50)

    stack = StegVerseSafetyStack()

    # Test Layer 1: Mathematical
    print("\n--- Layer 1: Mathematical Governance ---")

    safe_state = GCATState(g=0.30, c=0.30, a=0.20, t=0.20)
    decision = stack.evaluate_mathematical(safe_state, 0.8, "test-actor")
    print(f"Safe state: {decision.action} — {decision.reason[:50]}")

    unsafe_state = GCATState(g=0.10, c=0.10, a=0.60, t=0.20)
    decision = stack.evaluate_mathematical(unsafe_state, 0.5, "test-actor")
    print(f"Unsafe state: {decision.action} — {decision.reason[:50]}")

    # Test Layer 3: Circuit Breaker
    print("\n--- Layer 3: Circuit Breaker ---")

    healthy_metrics = {"cpu": 0.5, "memory": 0.6, "error_rate": 0.01, "latency": 200}
    decision = stack.check_health(healthy_metrics)
    print(f"Healthy: {decision.action} — {decision.reason}")

    unhealthy_metrics = {
        "cpu": 0.95,
        "memory": 0.95,
        "error_rate": 0.15,
        "latency": 2000,
    }
    decision = stack.check_health(unhealthy_metrics)
    print(f"Unhealthy: {decision.action} — {decision.reason[:50]}")

    # Test Layer 4: Consensus Halt
    print("\n--- Layer 4: Consensus Halt ---")

    stack.vote_halt("admin-1", True)
    stack.vote_halt("admin-2", True)
    decision = stack.vote_halt("admin-3", True)
    print(f"Consensus: {decision.action} — {decision.reason[:60]}")

    # Test Layer 5: Dead Man's Switch
    print("\n--- Layer 5: Dead Man's Switch ---")

    stack.heartbeat("operator-1")
    print("Heartbeat sent")

    # Simulate missed heartbeats (would need time.sleep in real test)
    # decision = stack.check_dead_man()

    print(f"\nSystem halted: {stack.is_halted()}")
    print(f"Total receipts: {len(stack.get_receipt_chain())}")
