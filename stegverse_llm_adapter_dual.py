#!/usr/bin/env python3
"""
StegVerse LLM Adapter v2.0 — Dual Purpose
1. Governance Ingress: LLM output → canonical intent → pipeline
2. Ecosystem Optimization: Ecosystem state → LLM → optimization → pipeline
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone

from stegverse_safety_stack import StegVerseSafetyStack, GCATState, SafetyDecision


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    AZURE = "azure"
    GOOGLE = "google"


@dataclass
class CanonicalIntent:
    """Universal intent format for StegVerse pipeline."""
    schema_version: str = "2.1"
    ingress_source: str = ""  # llm|human|webhook|api|ecosystem
    provider: str = ""
    model: str = ""
    actor_id: str = ""
    session_id: str = ""
    intent_type: str = ""  # code_generation|resource_scaling|optimization|...
    payload: Dict[str, Any] = None
    gcat_state: Dict[str, float] = None
    metadata: Dict[str, Any] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if self.payload is None:
            self.payload = {}
        if self.gcat_state is None:
            self.gcat_state = {"g": 0.25, "c": 0.25, "a": 0.25, "t": 0.25}
        if self.metadata is None:
            self.metadata = {}
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "ingress": {
                "source": self.ingress_source,
                "provider": self.provider,
                "model": self.model,
                "actor_id": self.actor_id,
                "session_id": self.session_id,
                "timestamp": self.timestamp
            },
            "payload": self.payload,
            "gcat_state": self.gcat_state,
            "metadata": self.metadata
        }
    
    def hash(self) -> str:
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()


class StegVerseLLMAdapterDual:
    """
    Dual-purpose LLM adapter for StegVerse ecosystem.
    
    Purpose 1: Governance Ingress
        LLM generates content → adapter translates → pipeline evaluates
        
    Purpose 2: Ecosystem Optimization
        Ecosystem metrics → LLM analyzes → adapter translates → pipeline evaluates
    """
    
    def __init__(self, 
                 safety_stack: Optional[StegVerseSafetyStack] = None,
                 pipeline_url: str = "https://api.stegverse.org/v1"):
        self.safety = safety_stack or StegVerseSafetyStack()
        self.pipeline_url = pipeline_url
        self._session_counter = 0
    
    # Purpose 1: Governance Ingress
    
    def govern_llm_output(self,
                          provider: LLMProvider,
                          model: str,
                          prompt: str,
                          output: str,
                          user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Purpose 1: LLM output → canonical intent → safety stack → decision
        """
        self._session_counter += 1
        session_id = f"ingress-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{self._session_counter}"
        
        # Parse LLM output
        parsed = self._parse_llm_output(output)
        
        # Compute GCAT state from output characteristics
        gcat_state = self._compute_gcat_state(parsed)
        
        # Build canonical intent
        intent = CanonicalIntent(
            ingress_source="llm",
            provider=provider.value,
            model=model,
            actor_id=f"llm-{provider.value}-{model}-{hashlib.sha256(session_id.encode()).hexdigest()[:8]}",
            session_id=session_id,
            intent_type="code_generation",
            payload=parsed,
            gcat_state=gcat_state,
            metadata={"prompt": prompt, "user_context": user_context or {}}
        )
        
        # Evaluate through safety stack (Layer 1: Mathematical)
        gcat_obj = GCATState(**gcat_state)
        bcat_score = self._compute_bcat_score(parsed)
        
        safety_decision = self.safety.evaluate_mathematical(gcat_obj, bcat_score, intent.actor_id)
        
        if safety_decision.action == "HALT":
            return {
                "decision": "DENY",
                "safety_layer": safety_decision.layer_triggered.name,
                "reason": safety_decision.reason,
                "receipt": safety_decision.receipt_hash,
                "suggestions": self._generate_suggestions(gcat_obj, bcat_score, parsed)
            }
        
        if safety_decision.action == "DEFER":
            return {
                "decision": "DEFER",
                "safety_layer": safety_decision.layer_triggered.name,
                "reason": safety_decision.reason,
                "receipt": safety_decision.receipt_hash,
                "intent": intent.to_dict()
            }
        
        # ADMITTED — return with receipt
        return {
            "decision": "ADMIT",
            "safety_layer": safety_decision.layer_triggered.name,
            "receipt": safety_decision.receipt_hash,
            "intent_hash": intent.hash(),
            "gcat_score": gcat_obj.legitimacy_surplus(),
            "bcat_score": bcat_score
        }
    
    # Purpose 2: Ecosystem Optimization
    
    def optimize_ecosystem(self,
                           ecosystem_metrics: Dict[str, Any],
                           llm_analysis: str,
                           proposed_changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Purpose 2: Ecosystem state → LLM optimization → safety stack → decision
        """
        self._session_counter += 1
        session_id = f"optimization-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{self._session_counter}"
        
        # Compute ecosystem GCAT state
        gcat_state = self._compute_ecosystem_gcat_state(ecosystem_metrics)
        
        # Build canonical intent for optimization
        intent = CanonicalIntent(
            ingress_source="ecosystem",
            provider="stegverse-internal",
            model="optimizer",
            actor_id="llm-stegverse-optimizer-001",
            session_id=session_id,
            intent_type="ecosystem_modification",
            payload={
                "metrics": ecosystem_metrics,
                "analysis": llm_analysis,
                "proposed_changes": proposed_changes
            },
            gcat_state=gcat_state,
            metadata={"optimization_type": proposed_changes.get("type", "unknown")}
        )
        
        # Evaluate through safety stack
        gcat_obj = GCATState(**gcat_state)
        bcat_score = self._compute_ecosystem_bcat_score(proposed_changes)
        
        safety_decision = self.safety.evaluate_mathematical(gcat_obj, bcat_score, intent.actor_id)
        
        if safety_decision.action == "HALT":
            return {
                "decision": "DENY",
                "safety_layer": safety_decision.layer_triggered.name,
                "reason": safety_decision.reason,
                "receipt": safety_decision.receipt_hash,
                "suggestions": [
                    "Reduce cost impact of proposed changes",
                    "Increase observability before scaling",
                    "Defer to human review for high-cost changes"
                ]
            }
        
        if safety_decision.action == "DEFER":
            return {
                "decision": "DEFER",
                "safety_layer": safety_decision.layer_triggered.name,
                "reason": safety_decision.reason,
                "receipt": safety_decision.receipt_hash,
                "intent": intent.to_dict()
            }
        
        # ADMITTED — return with receipt and execution plan
        return {
            "decision": "ADMIT",
            "safety_layer": safety_decision.layer_triggered.name,
            "receipt": safety_decision.receipt_hash,
            "intent_hash": intent.hash(),
            "gcat_score": gcat_obj.legitimacy_surplus(),
            "bcat_score": bcat_score,
            "execution_plan": proposed_changes
        }
    
    # Private methods
    
    def _parse_llm_output(self, output: str) -> Dict[str, Any]:
        """Extract structured data from LLM output."""
        import re
        
        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)\n```", output, re.DOTALL)
        files = re.findall(r'["\']([\w/]+\.(py|js|ts|java|go|rs))["\']', output)
        
        return {
            "code_blocks": code_blocks,
            "files_modified": [f[0] for f in files],
            "lines_added": sum(len(block.split("\n")) for block in code_blocks),
            "has_tests": "test" in output.lower() or "assert" in output.lower(),
            "has_docs": '"""' in output or "docstring" in output.lower(),
            "complexity": self._estimate_complexity(code_blocks)
        }
    
    def _compute_gcat_state(self, parsed: Dict) -> Dict[str, float]:
        """Compute GCAT state from parsed LLM output."""
        g = 0.3 + (0.15 if parsed.get("has_docs") else 0) + (0.1 if parsed.get("has_tests") else 0)
        c = 0.2 + (0.25 if parsed.get("has_tests") else 0)
        a = 0.15 + (0.25 * min(1.0, parsed.get("lines_added", 0) / 100))
        t = 0.25
        
        total = g + c + a + t
        return {"g": g/total, "c": c/total, "a": a/total, "t": t/total}
    
    def _compute_bcat_score(self, parsed: Dict) -> float:
        """Compute BCAT score from parsed output."""
        observability = 0.3 + (0.4 if parsed.get("has_tests") else 0)
        risk = 1.0 - min(1.0, parsed.get("complexity", 0.5))
        boundary = 1.0 - min(1.0, parsed.get("lines_added", 0) / 500)
        return observability * 0.4 + risk * 0.3 + boundary * 0.3
    
    def _compute_ecosystem_gcat_state(self, metrics: Dict) -> Dict[str, float]:
        """Compute GCAT state from ecosystem metrics."""
        cpu = metrics.get("cpu", 0.5)
        memory = metrics.get("memory", 0.5)
        cost = metrics.get("cost_ratio", 0.5)
        trust = metrics.get("system_trust", 0.5)
        
        # Governance capacity: inverse of resource pressure
        g = 1.0 - max(cpu, memory)
        # Constraint integrity: based on system health
        c = 1.0 - metrics.get("error_rate", 0)
        # Artifact pressure: cost + load
        a = (cost + cpu) / 2
        # Trust continuity: system stability
        t = trust
        
        total = g + c + a + t
        return {"g": g/total, "c": c/total, "a": a/total, "t": t/total}
    
    def _compute_ecosystem_bcat_score(self, changes: Dict) -> float:
        """Compute BCAT score for ecosystem changes."""
        cost = changes.get("cost_increase", 0)
        risk = changes.get("risk_score", 0.5)
        observability = changes.get("observability", 0.5)
        
        return observability * 0.4 + (1.0 - risk) * 0.3 + (1.0 - min(1.0, cost / 10000)) * 0.3
    
    def _estimate_complexity(self, code_blocks: List[str]) -> float:
        """Estimate code complexity."""
        if not code_blocks:
            return 0.0
        total_lines = sum(len(block.split("\n")) for block in code_blocks)
        return min(1.0, total_lines / 200)
    
    def _generate_suggestions(self, gcat: GCATState, bcat: float, parsed: Dict) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        if gcat.legitimacy_surplus() < 0:
            suggestions.append("Reduce artifact pressure: smaller changes")
        if bcat < 0.6:
            suggestions.append("Improve observability: add tests, docs")
        if not parsed.get("has_tests"):
            suggestions.append("Add tests for verification")
        if not parsed.get("has_docs"):
            suggestions.append("Add documentation")
        return suggestions


# CLI for testing
if __name__ == "__main__":
    print("StegVerse LLM Adapter v2.0 — Dual Purpose")
    print("=" * 60)
    
    adapter = StegVerseLLMAdapterDual()
    
    # Test Purpose 1: Governance Ingress
    print("\n--- Purpose 1: Governance Ingress ---")
    
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
        prompt="Write a hello function",
        output=safe_code
    )
    print(f"Safe code: {result['decision']} (Layer: {result['safety_layer']})")
    
    risky_code = '''
    import os
    def run(cmd):
        os.system(cmd)
    '''
    
    result = adapter.govern_llm_output(
        provider=LLMProvider.OPENAI,
        model="gpt-4",
        prompt="Run a command",
        output=risky_code
    )
    print(f"Risky code: {result['decision']} (Layer: {result['safety_layer']})")
    print(f"Reason: {result['reason'][:60]}")
    
    # Test Purpose 2: Ecosystem Optimization
    print("\n--- Purpose 2: Ecosystem Optimization ---")
    
    metrics = {
        "cpu": 0.85,
        "memory": 0.90,
        "cost_ratio": 0.8,
        "system_trust": 0.7,
        "error_rate": 0.02
    }
    
    analysis = "System approaching resource limits. Recommend scaling."
    changes = {
        "type": "resource_scaling",
        "cost_increase": 5000,
        "risk_score": 0.3,
        "observability": 0.8
    }
    
    result = adapter.optimize_ecosystem(metrics, analysis, changes)
    print(f"Scale proposal: {result['decision']} (Layer: {result['safety_layer']})")
    print(f"GCAT Score: {result.get('gcat_score', 'N/A')}")
    
    # Test with low-cost optimization
    changes["cost_increase"] = 0
    changes["type"] = "resource_optimization"
    
    result = adapter.optimize_ecosystem(metrics, analysis, changes)
    print(f"Optimize proposal: {result['decision']} (Layer: {result['safety_layer']})")
    print(f"GCAT Score: {result.get('gcat_score', 'N/A')}")
